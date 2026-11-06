"""Real unprivileged fixtures only; never inspect the protected installation."""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import capstone_installation as installation
from common import Failure, digest


class InstallationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='grrr-backend-fixture-',
                                               dir='/private/tmp')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.leaf = self.root / 'source'
        self.leaf.write_bytes(b'fixture bytes')
        self.leaf.chmod(0o444)
        self.records = [dict(relative_path='source', mode=0o444,
                             sha256=digest(b'fixture bytes'))]

    def read(self):
        return installation.open_public_fixture(str(self.root), self.records)

    def test_positive_detached_bytes_are_not_provenance(self):
        result = self.read()
        self.assertEqual(result['contents']['source'], b'fixture bytes')
        self.assertEqual(result['actual_uid'], os.getuid())
        self.assertEqual(result['environment'], 'NONPRODUCTION')
        self.assertFalse(result['stable_installation'])
        self.assertFalse(result['trusted_provenance'])
        self.leaf.unlink()
        self.leaf.write_bytes(b'changed by same UID')
        self.assertEqual(result['contents']['source'], b'fixture bytes')
        with self.assertRaises(TypeError):
            result['contents']['source'] = b'forged'

    def test_nested_inventory(self):
        folder = self.root / 'nested'
        folder.mkdir(mode=0o700)
        self.leaf.rename(folder / 'source')
        self.records[0]['relative_path'] = 'nested/source'
        self.assertEqual(self.read()['contents']['nested/source'], b'fixture bytes')

    def test_all_opens_are_readonly_nofollow(self):
        actual_open = os.open
        observed = []

        def guarded_open(path, flags, *args, **kwargs):
            self.assertFalse(flags & (os.O_CREAT | os.O_TRUNC | os.O_WRONLY | os.O_RDWR))
            self.assertTrue(flags & os.O_NOFOLLOW)
            self.assertNotIn('GRRR', os.fspath(path).split('/'))
            observed.append(path)
            return actual_open(path, flags, *args, **kwargs)

        with patch.object(installation.os, 'open', side_effect=guarded_open):
            self.read()
        self.assertEqual(observed[:3], ['/', 'private', 'tmp'])

    def test_symlink_nested_ancestor_refuses(self):
        (self.root / 'nested').symlink_to(self.root, target_is_directory=True)
        self.records[0]['relative_path'] = 'nested/source'
        # Inventory includes source so the denial must reach the nested link.
        self.records.append(dict(relative_path='source', mode=0o444,
                                 sha256=digest(b'fixture bytes')))
        with self.assertRaises(Failure):
            self.read()

    def test_production_never_probes_even_with_valid_role(self):
        with patch.object(installation.os, 'open', side_effect=AssertionError), \
                patch.object(installation.os, 'stat', side_effect=AssertionError), \
                patch.object(installation.os, 'lstat', side_effect=AssertionError):
            for role in ('operator', 'evaluator', 'broker', 'reviewer', None):
                with self.assertRaises(Failure) as caught:
                    installation.open_installed(role)
                self.assertEqual(caught.exception.record['code'], 'Unavailable')

    def test_bad_roots_refuse_before_filesystem_access(self):
        paths = ('/Library/GRRR', '/Library/GRRR/capstone-v1',
                 '/private/tmp/grrr-backend-fixture-x/../../Library/GRRR',
                 '/tmp/grrr-backend-fixture-x', '/private/tmp/x',
                 '/private/tmp/grrr-backend-fixture-x/child')
        with patch.object(installation.os, 'open', side_effect=AssertionError), \
                patch.object(installation.os, 'stat', side_effect=AssertionError), \
                patch.object(installation.os, 'lstat', side_effect=AssertionError):
            for root in paths:
                with self.subTest(root=root), self.assertRaises(Failure):
                    installation.open_public_fixture(root, self.records)

    def test_no_stability_or_uid_override(self):
        for kwargs in ({'require_stable_installation': True}, {'uid': os.getuid()},
                       {'trusted': True}):
            with self.assertRaises(TypeError):
                installation.open_public_fixture(str(self.root), self.records, **kwargs)

    def test_writable_file_refuses(self):
        self.leaf.chmod(0o644)
        with self.assertRaises(Failure):
            self.read()

    def test_nonprivate_root_refuses(self):
        self.root.chmod(0o755)
        with self.assertRaises(Failure):
            self.read()

    def test_symlink_leaf_refuses(self):
        self.leaf.unlink()
        self.leaf.symlink_to('missing')
        with self.assertRaises(Failure):
            self.read()

    def test_symlink_root_refuses(self):
        alias = self.root.parent / (self.root.name + '-alias')
        alias.symlink_to(self.root)
        self.addCleanup(alias.unlink)
        with self.assertRaises(Failure):
            installation.open_public_fixture(str(alias), self.records)

    def test_hardlink_refuses(self):
        other = self.root / 'alias'
        os.link(self.leaf, other)
        self.records.append(dict(relative_path='alias', mode=0o444,
                                 sha256=digest(b'fixture bytes')))
        self.records.sort(key=lambda item: item['relative_path'])
        with self.assertRaises(Failure):
            self.read()

    def test_fifo_refuses_without_blocking(self):
        self.leaf.unlink()
        os.mkfifo(self.leaf, 0o444)
        with self.assertRaises(Failure):
            self.read()

    def test_extra_and_missing_files_refuse(self):
        extra = self.root / 'extra'
        extra.write_bytes(b'x')
        with self.assertRaises(Failure):
            self.read()
        extra.unlink()
        self.leaf.unlink()
        with self.assertRaises(Failure):
            self.read()

    def test_wrong_hash_refuses(self):
        self.records[0]['sha256'] = '0' * 64
        with self.assertRaises(Failure):
            self.read()

    def test_actual_acl_refuses_on_file_and_directory(self):
        for path in (self.leaf, self.root):
            with self.subTest(path=path):
                subprocess.run(['/bin/chmod', '+a',
                                'everyone allow read,write', str(path)], check=True)
                try:
                    with self.assertRaises(Failure):
                        self.read()
                finally:
                    subprocess.run(['/bin/chmod', '-N', str(path)], check=True)
        self.assertEqual(self.read()['contents']['source'], b'fixture bytes')

    def test_real_descriptor_owner_and_mode_checks(self):
        fd = os.open(self.root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        try:
            with self.assertRaises(Failure):
                installation._check(fd, uid=0, directory=True, mode=0o700)
            with self.assertRaises(Failure):
                installation._check(fd, uid=os.getuid(), directory=True, mode=0o755)
        finally:
            os.close(fd)

    def test_unsupported_acl_platform_fails_closed(self):
        with patch.object(installation.sys, 'platform', 'unsupported'):
            with self.assertRaises(Failure):
                self.read()

    def test_close_failure_still_attempts_entire_ancestor_stack(self):
        actual_open, actual_close, actual_check = installation._open, os.close, installation._check
        for body_failure in (False, True):
            opened, attempted = [], []

            def track_open(*args, **kwargs):
                fd = actual_open(*args, **kwargs)
                opened.append(fd)
                return fd

            def fail_first_ancestor_close(fd):
                attempted.append(fd)
                actual_close(fd)
                if len(opened) >= 4 and fd == opened[3]:
                    raise InterruptedError('injected close error after release')

            def maybe_fail_check(fd, **kwargs):
                if body_failure and len(opened) >= 4 and fd == opened[3]:
                    raise RuntimeError('injected body failure')
                return actual_check(fd, **kwargs)

            with self.subTest(body_failure=body_failure), \
                    patch.object(installation, '_open', side_effect=track_open), \
                    patch.object(installation.os, 'close', side_effect=fail_first_ancestor_close), \
                    patch.object(installation, '_check', side_effect=maybe_fail_check):
                with self.assertRaises(RuntimeError if body_failure else Failure):
                    self.read()
            self.assertEqual(attempted[-4:], list(reversed(opened[:4])))
            for fd in opened[:4]:
                with self.assertRaises(OSError):
                    os.fstat(fd)


if __name__ == '__main__':
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(InstallationTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    raise SystemExit(int(result.testsRun == 0 or bool(result.skipped)
                        or not result.wasSuccessful()))
