"""No-guest replay policy and actual filesystem/CLI controls; no identity substitution."""
import copy
import importlib.machinery
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'research'))
from common import Failure, canonical
from replay_prerequisites import (POLICY_SHA256, check_absent, check_idle,
                                  inspect_corpus, protected_preflight, validate_policy)
from trusted_install import immutable, acl_free
from trusted_execution import _acl_free
from replay_runtime import IDENTITY, PYTHON, verify_runtime


def root_preparer():
    loader = importlib.machinery.SourceFileLoader('replay_root_prepare_test', str(ROOT / 'scripts/replay-root-prepare'))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


class ReplayPrerequisites(unittest.TestCase):
    def test_parent_preexec_boundary_removes_poisoned_loader_environment(self):
        poison = {'DYLD_INSERT_LIBRARIES': '/nonexistent/grrr-poison.dylib',
                  'DYLD_LIBRARY_PATH': '/nonexistent/grrr-native',
                  'PYTHONPATH': '/nonexistent/grrr-python', 'PYTHONHOME': '/nonexistent/grrr-home',
                  'GRRR_TEST_CREDENTIAL': 'synthetic-not-a-secret', 'PATH': '/untrusted',
                  '__CF_USER_TEXT_ENCODING': 'poisoned-parent-value'}
        result = subprocess.run(['/usr/bin/env', '-i', 'PATH=/usr/bin:/bin', 'LC_ALL=C',
                                 str(PYTHON), '-I', '-S', '-B',
                                 str(ROOT / 'tests/replay_environment_probe.py')],
                                env=poison, capture_output=True, check=True, timeout=10)
        observed = json.loads(result.stdout)
        self.assertEqual(observed['python'], str(PYTHON))
        self.assertEqual(observed['uid'], os.getuid())
        self.assertTrue(observed['isolated_flags'])
        self.assertEqual(observed['names'], ['LC_ALL', 'PATH', '__CF_USER_TEXT_ENCODING'])
        self.assertNotEqual(observed['generated_cf_encoding'], 'poisoned-parent-value')
        self.assertEqual(observed['allowlist'], {'PATH': '/usr/bin:/bin', 'LC_ALL': 'C'})
        self.assertEqual(result.stderr, b'')

    def test_real_acl_checks_with_and_without_xattrs(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'asset'
            path.write_bytes(b'asset')
            for target in (Path(directory), path):
                with self.subTest(path=target):
                    self.assertTrue(acl_free(target))
                    self.assertTrue(_acl_free(target))
                    subprocess.run(['/bin/chmod', '+a', 'everyone allow read', str(target)], check=True)
                    self.assertFalse(acl_free(target))
                    self.assertFalse(_acl_free(target))
                    subprocess.run(['/usr/bin/xattr', '-w', 'com.grrr.test', 'value', str(target)], check=True)
                    self.assertFalse(acl_free(target))
                    self.assertFalse(_acl_free(target))
                    subprocess.run(['/bin/chmod', '-N', str(target)], check=True)
                    self.assertTrue(acl_free(target))
                    self.assertTrue(_acl_free(target))

    def test_live_pinned_clt_runtime_readonly(self):
        result = verify_runtime()
        self.assertEqual(result['runtime_identity'], IDENTITY)
        self.assertFalse(PYTHON.is_symlink())
        self.assertFalse(result['root_launch_authorized'])

    def test_runtime_inventory_and_root_entry_binding(self):
        module = root_preparer()
        self.assertEqual(module.PYTHON, PYTHON)
        inventory = json.loads((ROOT / 'docs/evidence/replay-prerequisites/runtime-identity.json').read_bytes())
        self.assertEqual(module.sha(canonical(inventory)), IDENTITY)
        self.assertEqual(inventory['python'], str(PYTHON))
        self.assertNotEqual(str(PYTHON), '/usr/bin/python3')

    def test_destination_real_reopen_success_and_failures(self):
        module = root_preparer()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            root.chmod(0o700)
            target = root / 'private'
            target.mkdir(mode=0o700)
            path = target / 'record'
            path.write_bytes(b'protected record')
            path.chmod(0o400)
            expected = {'.': {'kind': 'directory', 'uid': os.getuid(), 'gid': os.getgid(), 'mode': 0o700},
                        'private': {'kind': 'directory', 'uid': os.getuid(), 'gid': os.getgid(), 'mode': 0o700},
                        'private/record': {'kind': 'file', 'uid': os.getuid(), 'gid': os.getgid(),
                                           'mode': 0o400, 'raw': b'protected record'}}
            module.verify_destination(root, expected)
            for field, altered in (('uid', os.getuid() + 1), ('gid', os.getgid() + 1),
                                   ('mode', 0o600), ('raw', b'wrong bytes')):
                mutated = copy.deepcopy(expected)
                mutated['private/record'][field] = altered
                with self.subTest(field=field), self.assertRaises(RuntimeError):
                    module.verify_destination(root, mutated)
            extra = root / 'extra'
            extra.write_bytes(b'extra')
            with self.assertRaises(RuntimeError):
                module.verify_destination(root, expected)
            extra.unlink()
            path.unlink()
            path.symlink_to('/etc/passwd')
            with self.assertRaises(RuntimeError):
                module.verify_destination(root, expected)
            path.unlink()
            path.write_bytes(b'protected record')
            path.chmod(0o400)
            outside = root.parent / (root.name + '-hardlink')
            try:
                os.link(path, outside)
                with self.assertRaises(RuntimeError):
                    module.verify_destination(root, expected)
            finally:
                outside.unlink()
            # Real macOS ACL metadata must be rejected even if POSIX bits match.
            subprocess.run(['/bin/chmod', '+a', 'everyone allow read', str(path)], check=True)
            with self.assertRaises(RuntimeError):
                module.verify_destination(root, expected)
            subprocess.run(['/bin/chmod', '-N', str(path)], check=True)
            module.verify_destination(root, expected)

    def test_root_launcher_refuses_nonroot_before_effects(self):
        self.assertNotEqual(os.getuid(), 0, 'This suite must never run as root')
        target = Path('/Library/GRRR/independent-replay')
        before = target.lstat() if os.path.lexists(target) else None
        for args in (['--prepare'], ['--dispatch'], ['--prepare', '/tmp/evil']):
            result = subprocess.run([sys.executable, '-I', '-S', '-B',
                                     str(ROOT / 'scripts/replay-root-prepare'), *args],
                                    capture_output=True, timeout=10)
            self.assertEqual(result.returncode, 1)
            self.assertFalse(json.loads(result.stdout)['execution_authorized'])
        after = target.lstat() if os.path.lexists(target) else None
        self.assertEqual(before, after)

    def test_root_launcher_paths_and_code_pins(self):
        path = ROOT / 'scripts/replay-root-prepare'
        loader = importlib.machinery.SourceFileLoader('replay_root_prepare', str(path))
        spec = importlib.util.spec_from_loader(loader.name, loader)
        module = importlib.util.module_from_spec(spec)
        loader.exec_module(module)
        module.validate_location(Path('/Library/GRRR/bootstrap/replay-root-prepare'))
        for value in (path, Path('replay-root-prepare'), Path('/tmp/replay-root-prepare'),
                      Path('/Library/GRRR/bootstrap/../replay-root-prepare')):
            with self.subTest(path=value), self.assertRaises(RuntimeError):
                module.validate_location(value)
        for name, expected in module.CODE.items():
            self.assertEqual(module.sha((ROOT / 'research' / name).read_bytes()), expected)

    def test_approved_policy_canonical_bytes(self):
        raw = (ROOT / 'docs/replay-policy-v1.json').read_bytes()
        value = validate_policy(raw)
        self.assertEqual(raw, canonical(value) + b'\n')
        self.assertEqual(value['limits']['minimum_host_free_bytes'], 15 * 1024**3)
        self.assertEqual(value['limits']['paid_cost_units'], 0)
        self.assertEqual(value['stop_after_consecutive_independent_replay_failures'], 2)

    def test_every_policy_leaf_is_pinned(self):
        original = json.loads((ROOT / 'docs/replay-policy-v1.json').read_bytes())
        def leaves(value, path=()):
            if isinstance(value, dict):
                for key, child in value.items():
                    yield from leaves(child, path + (key,))
            elif isinstance(value, list):
                for index, child in enumerate(value):
                    yield from leaves(child, path + (index,))
            else:
                yield path
        for path in leaves(original):
            with self.subTest(path=path):
                altered = copy.deepcopy(original)
                cursor = altered
                for part in path[:-1]:
                    cursor = cursor[part]
                cursor[path[-1]] = 'unauthorized-change'
                with self.assertRaises(Failure):
                    validate_policy(canonical(altered) + b'\n')

    def test_duplicate_extra_noncanonical_and_boolean_policy_rejected(self):
        raw = (ROOT / 'docs/replay-policy-v1.json').read_bytes()
        value = json.loads(raw)
        for altered in (raw.rstrip(), raw.replace(b'"version":1', b'"version":true'),
                        raw.replace(b'"version":1', b'"version":1,"version":1'),
                        canonical(dict(value, extra=1)) + b'\n'):
            with self.subTest(raw=altered[:30]), self.assertRaises(Failure):
                validate_policy(altered)

    def test_real_corpus_bytes_success(self):
        result = inspect_corpus(ROOT / 'corpus')
        self.assertEqual(result['source'], '129e0b3f15a3bd6af949ee47d76f6855c582ab73')
        self.assertEqual(len(result['spec']), 64)

    def test_each_corpus_artifact_tamper_rejected(self):
        manifest = json.loads((ROOT / 'corpus/manifest.json').read_bytes())
        with tempfile.TemporaryDirectory() as directory:
            corpus = Path(directory) / 'corpus'
            shutil.copytree(ROOT / 'corpus', corpus)
            for name in ['manifest.json', *manifest['artifacts']]:
                with self.subTest(name=name):
                    path = corpus / name
                    original = path.read_bytes()
                    path.write_bytes(original + b' ')
                    with self.assertRaises(Failure):
                        inspect_corpus(corpus)
                    path.write_bytes(original)

    def test_symlink_corpus_member_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            corpus = Path(directory)
            (corpus / 'manifest.json').symlink_to(ROOT / 'corpus/manifest.json')
            with self.assertRaises(Failure):
                inspect_corpus(corpus)

    def test_namespace_fresh_partial_existing_and_dangling_link(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'runtime'
            check_absent(path)
            path.mkdir()
            with self.assertRaises(Failure):
                check_absent(path)
            path.rmdir()
            path.symlink_to(Path(directory) / 'missing')
            with self.assertRaises(Failure):
                check_absent(path)

    def test_process_inventory_parsing_fail_closed(self):
        check_idle(b'0 1 /sbin/launchd\n501 123 /usr/bin/python3\n')
        for value in (b'', b'unknown', b'320 2 /bin/false', b'321 3 /bin/false',
                      b'501 4 /Library/GRRR/qemu/bin/qemu-system-aarch64'):
            with self.subTest(value=value), self.assertRaises(Failure):
                check_idle(value)

    def test_actual_mutable_ancestor_and_symlink_denied(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'asset'
            path.write_bytes(b'untrusted')
            path.chmod(0o444)
            with self.assertRaises(Failure):
                immutable(path)
            link = Path(directory) / 'link'
            link.symlink_to(path)
            with self.assertRaises(Failure):
                immutable(link)

    def test_protected_preflight_cannot_promote_checkout(self):
        with self.assertRaises(Failure):
            protected_preflight(ROOT / 'corpus', ROOT, ROOT / 'corpus/manifest.json',
                                ROOT / 'docs/replay-policy-v1.json')

    def test_real_cli_package_success_without_dispatch(self):
        result = subprocess.run([sys.executable, '-B', str(ROOT / 'scripts/replay-prerequisites'),
                                 '--check-package'], capture_output=True, check=True, timeout=10)
        record = json.loads(result.stdout)
        self.assertEqual(record['package'], 'validated')
        self.assertFalse(record['execution_authorized'])
        self.assertEqual(record['replay_dispatch'], 'not-run')

    def test_real_cli_invalid_and_unprotected_input_fail_closed(self):
        for args in (['--provision'], ['--dispatch'],
                     ['--protected-preflight', str(ROOT / 'corpus'), str(ROOT),
                      str(ROOT / 'corpus/manifest.json'), str(ROOT / 'docs/replay-policy-v1.json')]):
            result = subprocess.run([sys.executable, '-B', str(ROOT / 'scripts/replay-prerequisites'), *args],
                                    capture_output=True, timeout=10)
            self.assertEqual(result.returncode, 1)
            record = json.loads(result.stdout)
            self.assertFalse(record['execution_authorized'])
            self.assertEqual(record['replay_dispatch'], 'not-run')


if __name__ == '__main__':
    unittest.main()
