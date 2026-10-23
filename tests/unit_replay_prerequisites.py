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
from trusted_install import immutable


class ReplayPrerequisites(unittest.TestCase):
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
