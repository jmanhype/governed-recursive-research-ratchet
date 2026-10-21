"""No-guest v4 source-binding and fail-closed controls."""
import base64
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'research'))
from budget import Budget
from common import Failure, canonical, digest
import trusted_execution as executor
from trusted_evaluation import EXPECTED, validate_receipt
from trusted_install import verify_qemu

V3_PROFILE = '3edebcd4b85ae7ce666d953bd3c5527606a7043c42294a0f60000875f8d2eec0'
V3_IMAGE = '799ec744f27e7329686e5acb8a3e1f663c82a321f7bc1d4bc940ea5c97068233'
V3_RECEIPT = '775a767ca74f9c18678fc998111b0c9870df1a68db68e453b6af0c50ae9d6c0c'
LEGACY_QEMU = '7299ef807db462f913be5d1b89a71ea12590416175be0be5e87c2349594c6542'


def config(**changes):
    value = {'version': 1, 'profile': executor.PROFILE, 'image': executor.IMAGE,
             'supervisor': executor.SUPERVISOR, 'helper': executor.HELPER,
             'host_code': 'a' * 64, 'operator_uid': 501, 'limits': dict(executor.LIMITS),
             'network': False, 'host_shares': False, 'paid_dispatch': False,
             'read_only_inputs': True, 'qemu_installation': executor.QEMU_MANIFEST,
             'accounting_binding': 'c' * 64, 'bootstrap_sha256': 'd' * 64,
             'python_sha256': 'e' * 64}
    value.update(changes)
    value['execution_profile'] = executor.configuration_digest(value)
    return value


def review(**changes):
    value = {'version': 1, 'decision': 'approved-local-use', 'preparation_receipt': executor.RECEIPT,
             'compiler': 'e670dfa79b080bad7f7d6b1d7131145c8c49068096650ebf0ac6292f098db60d',
             'guest_toolchain': '3f4227ce7b206a513e794f1393adb473a07b46e94d18bd15d1c684bbb7319797',
             'authorization_reference': 'b' * 64}
    value.update(changes)
    return value


def approval(value=None, review_value=None, **changes):
    value = config() if value is None else value
    review_value = review() if review_value is None else review_value
    bound = ('version', 'operator_uid', 'profile', 'image', 'supervisor', 'helper', 'host_code',
             'qemu_installation', 'accounting_binding', 'bootstrap_sha256', 'python_sha256',
             'execution_profile')
    result = {key: value[key] for key in bound}
    result.update(decision='approved-trusted-execution',
                  license_review_sha256=digest(canonical(review_value)),
                  authorization_reference='f' * 64)
    result.update(changes)
    return result


def request():
    return {'action': 'dispatch', 'version': 1, 'run': 'run', 'arm': 'trusted-control',
            'challenge': 'vlt-lock-observation-001', 'variant': 'clean', 'key': 'key',
            'reservation': 'reservation', 'epoch': 0, 'probe': None}


def receipt(**changes):
    guest = {'version': 1, 'run': 'run', 'challenge': 'vlt-lock-observation-001',
             'variant': 'clean', 'supervisor_sha256': executor.SUPERVISOR,
             'supervisor_unchanged': True,
             'candidate_credentials': {'Uid': '1000 1000 1000 1000',
                                       'Gid': '1000 1000 1000 1000', 'Groups': '',
                                       'NoNewPrivs': '1', 'CapInh': '0' * 16,
                                       'CapPrm': '0' * 16, 'CapEff': '0' * 16,
                                       'CapBnd': '0' * 16, 'CapAmb': '0' * 16},
             'candidate_exit_success': True, 'candidate_output': None,
             'output_exceeded': False, 'kernel_lock_held_by_supervisor': True,
             'note_absent_during_hold': True, 'observed_note': base64.b64encode(EXPECTED).decode(),
             'note_regular': True,
             'seconds': 0.5, 'candidate_cessation': True, 'verified': False,
             'admission': 'blocked',
             'scope': 'bounded supervisor-owned schedule observation; not exhaustive race freedom'}
    value = {'version': 1, 'run': 'run', 'key': 'key', 'reservation': 'reservation',
             'guest': guest, 'error': None, 'transport_complete': True, 'ceased': True,
             'forced': False, 'seconds': 1.5, 'raw_sha256': digest(b'raw'), 'raw_bytes': 3,
             'raw_base64': 'cmF3', 'exit_code': 0, 'profile': executor.PROFILE,
             'image': executor.IMAGE, 'supervisor': executor.SUPERVISOR,
             'helper': executor.HELPER, 'execution_profile': config()['execution_profile'],
             'qemu_installation': executor.QEMU_MANIFEST}
    value.update(changes)
    return value


class V4Bindings(unittest.TestCase):
    def test_exact_v4_shape_and_no_v3_or_homebrew_fallback(self):
        self.assertEqual(executor.PRESERVED_V4, {
            'prepared-profile.json': executor.PROFILE,
            'input.iso': executor.IMAGE,
            'preparation.json': executor.RECEIPT,
            'development-binding.json':
                '9fd432900036552fcdeb95ed1433937e01fbc45b73250aba91f6ed87a0efc209',
            'supervisor': executor.SUPERVISOR,
            'helper': executor.HELPER,
        })
        self.assertEqual(executor.QEMU_MANIFEST,
                         'e40888d8d14bc9c2b8db38d8468bc53fdbf77421b284d9eacbbce1d37818b625')
        self.assertEqual(executor.QEMU_EXECUTABLE,
                         '352108bbc46171ed74ee3ef0b74ac1f32403c7e076ebac623ce2c265724699da')
        self.assertEqual(executor.QEMU_EXECUTABLE_PATH,
                         Path('/Library/GRRR/qemu/bin/qemu-system-aarch64'))
        self.assertNotEqual(executor.QEMU_MANIFEST, LEGACY_QEMU)
        self.assertNotIn('/opt/homebrew', str(executor.QEMU_EXECUTABLE_PATH))
        with self.assertRaises(Failure):
            verify_qemu({'version': 1, 'root': '/opt/homebrew',
                         'executable': 'bin/qemu-system-aarch64', 'files': {},
                         'system_build': '26A428', 'review_reference': 'a' * 64,
                         'build_record_sha256': 'b' * 64, 'data_files': {}})

        exact = config()
        executor.validate_config(exact)
        executor.validate_approval(approval(), exact, review())
        validate_receipt(receipt(), request(), exact['execution_profile'], exact['qemu_installation'])

    def test_v3_values_are_rejected_everywhere(self):
        for change in ({'profile': V3_PROFILE}, {'image': V3_IMAGE},
                       {'helper': '0' * 64}, {'qemu_installation': LEGACY_QEMU}):
            with self.subTest(change=change), self.assertRaises(Failure):
                executor.validate_config(config(**change))
        with self.assertRaises(Failure):
            executor.validate_approval(approval(), config(),
                                       review(preparation_receipt=V3_RECEIPT))
        old = receipt()
        del old['helper']
        old['profile'] = V3_PROFILE
        old['image'] = V3_IMAGE
        with self.assertRaises(Failure):
            validate_receipt(old, request(), config()['execution_profile'], executor.QEMU_MANIFEST)

    def test_helper_and_installed_qemu_mismatches_are_rejected(self):
        with self.assertRaises(Failure):
            executor.validate_config(config(helper='0' * 64))
        changed = config(helper='0' * 64)
        with self.assertRaises(Failure):
            executor.validate_approval(approval(changed), config(), review())
        with self.assertRaises(Failure):
            executor.validate_approval(approval(qemu_installation=LEGACY_QEMU), config(), review())
        with self.assertRaises(Failure):
            validate_receipt(receipt(helper='0' * 64), request(),
                             config()['execution_profile'], executor.QEMU_MANIFEST)
        with self.assertRaises(Failure):
            validate_receipt(receipt(qemu_installation=LEGACY_QEMU), request(),
                             config()['execution_profile'], executor.QEMU_MANIFEST)

    def test_absent_approval_and_stopped_accounting_block_dispatch(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(Failure):
                executor.root_record(Path(folder) / 'absent-approval.json')
            with self.assertRaises(Failure):
                executor.validate_approval(approval(decision='development-review-only'),
                                           config(), review())
        with tempfile.TemporaryDirectory() as folder:
            with patch('budget.EVALUATOR', os.getuid()):
                budget = Budget(Path(folder) / 'budget.sqlite')
                try:
                    maximum = {'currency': 'USD', 'money_cents': 0,
                               'execution_us': 300000000, 'review_us': 0}
                    budget.reserve(os.getuid(), 'first', maximum, 'first')
                    budget.halt()
                    with self.assertRaises(Failure) as caught:
                        budget.reserve(os.getuid(), 'second', maximum, 'second')
                    self.assertEqual(caught.exception.record['code'], 'Stopped')
                finally:
                    budget.db.close()


class PreservedMetadata(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.root = Path(folder.name) / 'v4'
        self.root.mkdir()
        self.root.chmod(0o755)
        self.contents = {name: ('v4-' + name).encode() for name in
                         ('prepared-profile.json', 'input.iso', 'preparation.json',
                          'development-binding.json', 'supervisor', 'helper')}
        self.expected = {}
        for name, raw in self.contents.items():
            path = self.root / name
            path.write_bytes(raw)
            path.chmod(0o444)
            self.expected[name] = digest(raw)
        patches = [
            patch.object(executor, 'PRESERVED_ROOT', self.root),
            patch.object(executor, 'PRESERVED_V4', dict(self.expected)),
            patch.object(executor, 'PROTECTED_UID', os.getuid()),
            patch.object(executor, 'PROTECTED_GID', os.getgid()),
            patch.object(executor, '_safe_ancestors', lambda path: None),
            patch.object(executor, '_acl_free', lambda path: True),
        ]
        for item in patches:
            self.addCleanup(item.stop)
            item.start()

    def test_exact_preserved_member_bytes_and_hashes(self):
        self.assertEqual(executor.validate_preserved_v4(self.root), self.expected)

    def test_preserved_metadata_and_membership_failures(self):
        with self.assertRaises(Failure):
            executor.validate_preserved_v4(self.root.parent)
        self.root.chmod(0o700)
        with self.assertRaises(Failure):
            executor.validate_preserved_v4(self.root)
        self.root.chmod(0o755)

        (self.root / 'helper').chmod(0o400)
        with self.assertRaises(Failure):
            executor.validate_preserved_v4(self.root)
        (self.root / 'helper').chmod(0o444)

        with patch.object(executor, 'PROTECTED_UID', os.getuid() + 10000):
            with self.assertRaises(Failure):
                executor.validate_preserved_v4(self.root)
        with patch.object(executor, 'PROTECTED_GID', os.getgid() + 10000):
            with self.assertRaises(Failure):
                executor.validate_preserved_v4(self.root)
        def unsafe_ancestor(path):
            raise Failure('Unauthorized', 'Unsafe ancestor fixture')
        with patch.object(executor, '_safe_ancestors', unsafe_ancestor):
            with self.assertRaises(Failure):
                executor.validate_preserved_v4(self.root)
        with patch.object(executor, '_acl_free', lambda path: False):
            with self.assertRaises(Failure):
                executor.validate_preserved_v4(self.root)

        target = self.root / 'helper'
        target.unlink()
        target.symlink_to(self.root / 'supervisor')
        with self.assertRaises(Failure):
            executor.validate_preserved_v4(self.root)
        target.unlink()
        target.write_bytes(self.contents['helper'])
        target.chmod(0o444)

        mutated = self.root / 'preparation.json'
        mutated.chmod(0o600)
        mutated.write_bytes(b'changed-v4')
        mutated.chmod(0o444)
        with self.assertRaises(Failure):
            executor.validate_preserved_v4(self.root)
        mutated.chmod(0o600)
        mutated.write_bytes(self.contents['preparation.json'])
        mutated.chmod(0o444)

        (self.root / 'extra').write_bytes(b'extra')
        (self.root / 'extra').chmod(0o444)
        with self.assertRaises(Failure):
            executor.validate_preserved_v4(self.root)
        (self.root / 'extra').unlink()
        (self.root / 'supervisor').unlink()
        with self.assertRaises(Failure):
            executor.validate_preserved_v4(self.root)

    def test_linked_and_oversize_protected_files_reject(self):
        hard = self.root.parent / 'outside-hard-link'
        os.link(self.root / 'helper', hard)
        try:
            with self.assertRaises(Failure):
                executor.protected_bytes(hard, self.expected['helper'])
        finally:
            hard.unlink()
        with self.assertRaises(Failure):
            executor.protected_bytes(self.root / 'preparation.json',
                                     self.expected['preparation.json'], maximum=2)

    def test_bounded_root_record_accepts_installed_manifest_size(self):
        record = self.root.parent / 'installation.json'
        record.write_bytes(canonical({'version': 1, 'padding': 'x' * 16680}))
        record.chmod(0o444)
        self.assertEqual(executor.root_record(record)['version'], 1)
        oversized = self.root.parent / 'oversized.json'
        oversized.write_bytes(b'x' * (executor.ROOT_RECORD_MAX_BYTES + 1))
        oversized.chmod(0o444)
        with self.assertRaises(Failure):
            executor.root_record(oversized)


if __name__ == '__main__':
    unittest.main()
