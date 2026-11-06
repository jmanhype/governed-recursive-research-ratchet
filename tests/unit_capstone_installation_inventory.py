"""Real private-temp inventory fixtures; NOT installed authority proof."""
import hashlib
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import capstone_installation_inventory as inventory_module

from common import Failure, canonical, digest
from capstone_installation_inventory import (
    FIXTURE_DIRECTORY_MODE, FIXTURE_FILE_MODE, MAX_INVENTORY_BYTES, MAX_RECORDS,
    SCHEMA, encode_inventory, inventory_sha256, open_public_fixture,
    validate_inventory)


FILES = {
    'alpha': b'first exact bytes\n',
    'nested/one': b'A',
    'nested/two': b'BB',
    'other/deep/leaf': b'\x00binary\x7f',
}


def write_fixture(root, files=FILES, *, mode=FIXTURE_FILE_MODE):
    os.chmod(root, FIXTURE_DIRECTORY_MODE)
    for relative, data in files.items():
        path = Path(root) / relative
        path.parent.mkdir(mode=FIXTURE_DIRECTORY_MODE, parents=True, exist_ok=True)
        current = Path(root)
        for component in Path(relative).parent.parts:
            current /= component
            os.chmod(current, FIXTURE_DIRECTORY_MODE)
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL
                             | os.O_NOFOLLOW, 0o600)
        try:
            written = 0
            while written < len(data):
                written += os.write(descriptor, data[written:])
        finally:
            os.close(descriptor)
        os.chmod(path, mode)
    return expected_for(files)


def expected_for(files=FILES):
    return [dict(relative_path=path, mode=FIXTURE_FILE_MODE,
                 sha256=hashlib.sha256(data).hexdigest())
            for path, data in sorted(files.items())]


def io_mocks():
    return {name: unittest.mock.Mock(side_effect=AssertionError)
            for name in ('stat', 'lstat', 'open', 'read', 'listdir', 'fstat')}


class InventoryRecordTests(unittest.TestCase):
    def test_exact_canonical_bytes_and_stable_hash(self):
        records = expected_for()
        raw, hashed = encode_inventory(records)
        self.assertEqual(raw, canonical(records))
        self.assertEqual(hashed, hashlib.sha256(raw).hexdigest())
        self.assertEqual(hashed, inventory_sha256(records))
        self.assertEqual(hashed, inventory_sha256(expected_for()))

    def test_record_fields_modes_and_digests_are_strict(self):
        cases = []
        for field in ('relative_path', 'mode', 'sha256'):
            value = expected_for()
            del value[0][field]
            cases.append(value)
            value = expected_for()
            value[0][field] = None
            cases.append(value)
        value = expected_for(); value[0]['extra'] = 1; cases.append(value)
        for mode in (True, 0o400, 0o644, '0444', 0.0):
            value = expected_for(); value[0]['mode'] = mode; cases.append(value)
        for text in ('A' * 64, 'a' * 63, 'a' * 65, 'g' * 64, 64, None):
            value = expected_for(); value[0]['sha256'] = text; cases.append(value)
        for value in cases:
            with self.assertRaises(Failure):
                validate_inventory(value)

    def test_unsafe_paths_and_record_bounds_rejected(self):
        unsafe = ('', '.', '..', './a', 'a/.', 'a/./b', 'a/../b', '/a',
                  '/Library/GRRR/a', 'a//b', 'a/', 'a\\b', 'a\x00b', 'é',
                  'a\nb', 'z' * 4097)
        for path in unsafe:
            records = expected_for(); records[0]['relative_path'] = path
            records.sort(key=lambda record: record['relative_path'])
            with self.subTest(path=path), self.assertRaises(Failure):
                validate_inventory(records)
        self.assertRaises(Failure, validate_inventory, [])
        too_many = [dict(relative_path=f'{index:03d}', mode=FIXTURE_FILE_MODE,
                         sha256=digest(b'')) for index in range(MAX_RECORDS + 1)]
        self.assertRaises(Failure, validate_inventory, too_many)

    def test_order_and_duplicates_enforced_before_io(self):
        records = expected_for()
        duplicate = [dict(records[0]), *records]
        reversed_records = list(reversed(records))
        for value in (duplicate, reversed_records):
            with self.subTest(duplicate=value is duplicate):
                with patch.multiple('os', **io_mocks()):
                    with self.assertRaises(Failure):
                        validate_inventory(value)

    def test_lexical_fixture_rejection_before_any_syscall(self):
        records = expected_for()
        roots = ('/Library/GRRR', '/Library/GRRR/capstone-v1',
                 '/private/tmp', '/private/tmp/not-grrr-backend-fixture-x',
                 '/private/tmp/grrr-backend-fixture-x/../y',
                 '/private/tmp//grrr-backend-fixture-x',
                 '/private/tmp/grrr-backend-fixture-x/',
                 '/private/tmp/grrr-backend-fixture-x\\y', 'relative/path',
                 '/private/tmp/grrr-backend-fixture-é')
        for root in roots:
            with self.subTest(root=root):
                with patch.multiple('os', **io_mocks()):
                    with self.assertRaises(Failure):
                        open_public_fixture(root, records)


class FixtureVerificationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='grrr-backend-fixture-',
                                                 dir='/private/tmp')
        self.addCleanup(self.temp.cleanup)
        self.root = self.temp.name

    def test_real_positive_fixture_and_nonproduction_boundary(self):
        expected = write_fixture(self.root)
        result = open_public_fixture(self.root, expected)
        self.assertEqual(result['schema'], SCHEMA)
        self.assertEqual(result['environment'], 'NONPRODUCTION')
        self.assertEqual(result['actual_uid'], os.getuid())
        self.assertEqual(result['records'], expected)
        self.assertEqual(result['inventory_raw'], canonical(expected))
        self.assertEqual(result['inventory_sha256'], inventory_sha256(expected))
        self.assertEqual(dict(result['contents']), FILES)
        self.assertEqual(result['assurance'], 'DETACHED_FIXTURE_BYTES_ONLY')
        self.assertIs(result['stable_installation'], False)
        with self.assertRaises(TypeError):
            result['contents']['alpha'] = b'replacement'
        self.assertEqual(set(result), {'schema', 'environment', 'actual_uid',
                                       'inventory_raw', 'inventory_sha256', 'records',
                                       'contents', 'assurance', 'stable_installation'})
        self.assertNotIn('authority', result)
        self.assertNotIn('installed', result)

    def test_fixture_root_mode_rejected(self):
        expected = write_fixture(self.root)
        os.chmod(self.root, 0o755)
        with self.assertRaises(Failure):
            open_public_fixture(self.root, expected)

    def test_root_ancestor_and_leaf_symlinks_rejected(self):
        expected = write_fixture(self.root)
        alias = Path('/private/tmp') / ('grrr-backend-fixture-link-' + os.urandom(4).hex())
        alias.symlink_to(self.root, target_is_directory=True)
        self.addCleanup(alias.unlink)
        with self.assertRaises(Failure):
            open_public_fixture(str(alias), expected)

        ancestor = Path(self.root) / 'nested'
        real = Path(self.root) / 'real'
        os.chmod(ancestor, 0o700)
        ancestor.rename(real)
        ancestor.symlink_to(real, target_is_directory=True)
        with self.assertRaises(Failure):
            open_public_fixture(self.root, expected)
        ancestor.unlink()
        ancestor.mkdir(mode=FIXTURE_DIRECTORY_MODE)
        (ancestor / 'three').symlink_to(real / 'one', target_is_directory=False)
        changed = expected_for(dict(FILES, **{'nested/three': FILES['nested/one']}))
        with self.assertRaises(Failure):
            open_public_fixture(self.root, changed)

    def test_missing_extra_wrong_content_mode_and_directories_rejected(self):
        expected = write_fixture(self.root)
        os.unlink(Path(self.root) / 'alpha')
        with self.assertRaises(Failure):
            open_public_fixture(self.root, expected)

        alpha = Path(self.root) / 'alpha'
        descriptor = os.open(alpha, os.O_WRONLY | os.O_CREAT | os.O_EXCL
                             | os.O_NOFOLLOW, 0o600)
        os.write(descriptor, FILES['alpha']); os.close(descriptor)
        os.chmod(alpha, FIXTURE_FILE_MODE)
        original = dict(expected[0])
        expected[0] = dict(original, sha256=digest(b'wrong-content'))
        with self.assertRaises(Failure):
            open_public_fixture(self.root, expected)
        expected[0] = original

        extra_path = Path(self.root) / 'extra'
        descriptor = os.open(extra_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL
                             | os.O_NOFOLLOW, 0o600)
        os.write(descriptor, b'extra'); os.close(descriptor)
        os.chmod(extra_path, FIXTURE_FILE_MODE)
        with self.assertRaises(Failure):
            open_public_fixture(self.root, expected)
        os.unlink(extra_path)

        os.chmod(alpha, 0o400)
        with self.assertRaises(Failure):
            open_public_fixture(self.root, expected)
        os.chmod(alpha, FIXTURE_FILE_MODE)

        os.chmod(alpha, 0o600)
        with open(alpha, 'wb') as stream:
            stream.write(b'corrupted')
        os.chmod(alpha, FIXTURE_FILE_MODE)
        with self.assertRaises(Failure):
            open_public_fixture(self.root, expected)

        (Path(self.root) / 'empty').mkdir(mode=FIXTURE_DIRECTORY_MODE)
        with self.assertRaises(Failure):
            open_public_fixture(self.root, expected)

    def test_hard_link_and_content_size_bounds_rejected(self):
        files = {'one': b'linked', 'two': b'other'}
        expected = write_fixture(self.root, files)
        os.link(Path(self.root) / 'one', Path(self.root) / 'alias')
        expected.append(dict(relative_path='alias', mode=FIXTURE_FILE_MODE,
                             sha256=hashlib.sha256(files['one']).hexdigest()))
        expected.sort(key=lambda record: record['relative_path'])
        with self.assertRaises(Failure):
            open_public_fixture(self.root, expected)

        large = b'x' * (MAX_INVENTORY_BYTES + 1)
        expected = write_fixture(self.root, {'large': large})
        with self.assertRaises(Failure):
            open_public_fixture(self.root, expected)

    def test_rename_replacement_rejected_with_stable_positive_control(self):
        with tempfile.TemporaryDirectory(prefix='grrr-backend-fixture-positive-',
                                         dir='/private/tmp') as positive:
            expected = write_fixture(positive, {'target': b'target-exact-bytes'})
            result = open_public_fixture(positive, expected)
            self.assertEqual(result['environment'], 'NONPRODUCTION')
            self.assertEqual(result['inventory_sha256'], inventory_sha256(expected))

        expected = write_fixture(self.root, {'target': b'target-exact-bytes'})
        target = Path(self.root) / 'target'
        moved = Path(self.root) / 'old-name'
        replacement = Path(self.root) / 'replacement-name'
        target_inode = os.stat(target).st_ino
        real_read, triggered = os.read, False

        def replace_during_read(descriptor, count):
            nonlocal triggered
            if not triggered:
                triggered = True
                self.assertEqual(os.fstat(descriptor).st_ino, target_inode)
                os.rename(target, moved)
                created = os.open(replacement, os.O_WRONLY | os.O_CREAT | os.O_EXCL
                                  | os.O_NOFOLLOW, 0o600)
                os.write(created, b'replaced-different-bytes')
                os.close(created)
                os.chmod(replacement, FIXTURE_FILE_MODE)
            return real_read(descriptor, count)

        with patch.object(os, 'read', side_effect=replace_during_read):
            with self.assertRaisesRegex(Failure, 'Fixture namespace changed'):
                open_public_fixture(self.root, expected)
        self.assertTrue(triggered)
        self.assertEqual((moved.read_bytes(), replacement.read_bytes()),
                         (b'target-exact-bytes', b'replaced-different-bytes'))

    def test_global_lexical_order_survives_depth_first_traversal(self):
        expected = write_fixture(self.root, {'a.txt': b'sibling', 'a/leaf': b'descendant'})
        self.assertEqual([record['relative_path'] for record in expected], ['a.txt', 'a/leaf'])
        result = open_public_fixture(self.root, expected)
        self.assertEqual(result['records'], expected)

    def test_stable_authority_fails_closed_before_io_even_for_valid_fixture(self):
        expected = write_fixture(self.root)
        with patch.multiple('os', **io_mocks()):
            with self.assertRaisesRegex(Failure, 'effective trusted boundary'):
                open_public_fixture(self.root, expected, require_stable_installation=True)
            for assertion in (1, 'trusted', object()):
                with self.assertRaises(Failure):
                    open_public_fixture(self.root, expected,
                                        require_stable_installation=assertion)

    def test_same_name_replacement_after_final_check_is_not_stable_authority(self):
        expected = write_fixture(self.root, {'target': b'original'})
        real_recheck = inventory_module._recheck_namespace
        target = Path(self.root) / 'target'
        old_inode = target.stat().st_ino

        def replace_after_checks(*args):
            real_recheck(*args)
            target.rename(Path(self.root) / 'retained-old')
            write_fixture(self.root, {'target': b'hostile replacement'})

        with patch.object(inventory_module, '_recheck_namespace',
                          side_effect=replace_after_checks):
            result = open_public_fixture(self.root, expected)
        self.assertNotEqual(target.stat().st_ino, old_inode)
        self.assertEqual(target.read_bytes(), b'hostile replacement')
        self.assertEqual(result['contents']['target'], b'original')
        self.assertEqual(digest(result['contents']['target']), expected[0]['sha256'])
        self.assertIs(result['stable_installation'], False)
        self.assertEqual(result['assurance'], 'DETACHED_FIXTURE_BYTES_ONLY')

    def test_root_rebinding_after_final_check_is_not_stable_authority(self):
        expected = write_fixture(self.root, {'target': b'original'})
        real_recheck = inventory_module._recheck_namespace
        old_inode = os.stat(self.root).st_ino
        with tempfile.TemporaryDirectory(prefix='grrr-backend-fixture-rebinding-',
                                         dir='/private/tmp') as holding:
            def rebind_after_checks(*args):
                real_recheck(*args)
                os.rename(self.root, Path(holding) / 'old-root')
                os.mkdir(self.root, FIXTURE_DIRECTORY_MODE)
                write_fixture(self.root, {'target': b'hostile root'})

            with patch.object(inventory_module, '_recheck_namespace',
                              side_effect=rebind_after_checks):
                result = open_public_fixture(self.root, expected)
            self.assertNotEqual(os.stat(self.root).st_ino, old_inode)
            self.assertEqual((Path(self.root) / 'target').read_bytes(), b'hostile root')
            self.assertEqual(result['contents']['target'], b'original')
            self.assertEqual(digest(result['contents']['target']), expected[0]['sha256'])
            self.assertIs(result['stable_installation'], False)
            self.assertEqual(result['assurance'], 'DETACHED_FIXTURE_BYTES_ONLY')


if __name__ == '__main__':
    unittest.main()
