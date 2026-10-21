"""Pure parser/configuration tests; no service identity or guest proof."""
import base64
import copy
import importlib.machinery
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'research'))
from common import Failure, canonical, digest
from trusted_execution import (IMAGE, LIMITS, PROFILE, RECEIPT, SUPERVISOR, TrustedExecutor,
                               decode_guest, root_record, validate_approval, validate_config, validate_request)
from trusted_evaluation import EXPECTED, validate_receipt, verdict


def config():
    return {'version': 1, 'profile': PROFILE, 'image': IMAGE, 'supervisor': SUPERVISOR,
            'host_code': 'a' * 64, 'operator_uid': 501, 'limits': dict(LIMITS),
            'network': False, 'host_shares': False, 'paid_dispatch': False, 'read_only_inputs': True}


def request():
    return {'action': 'dispatch', 'version': 1, 'run': 'run', 'arm': 'trusted-control',
            'challenge': 'vlt-lock-observation-001', 'variant': 'clean', 'key': 'key',
            'reservation': 'reservation', 'epoch': 0, 'probe': None}


def guest():
    return {'version': 1, 'run': 'run', 'challenge': 'vlt-lock-observation-001', 'variant': 'clean',
            'supervisor_sha256': SUPERVISOR, 'supervisor_unchanged': True,
            'candidate_credentials': dict(Uid='1000 1000 1000 1000', Gid='1000 1000 1000 1000',
                Groups='', NoNewPrivs='1', **{k: '0000000000000000' for k in
                ('CapInh', 'CapPrm', 'CapEff', 'CapBnd', 'CapAmb')}),
            'candidate_exit_success': True, 'candidate_output': None, 'output_exceeded': False,
            'kernel_lock_held_by_supervisor': True, 'note_absent_during_hold': True,
            'observed_note': base64.b64encode(EXPECTED).decode(), 'note_regular': True,
            'seconds': 0.5, 'candidate_cessation': True, 'verified': False, 'admission': 'blocked',
            'scope': 'bounded supervisor-owned schedule observation; not exhaustive race freedom'}


def receipt():
    return {'version': 1, 'run': 'run', 'key': 'key', 'reservation': 'reservation',
            'guest': guest(), 'error': None, 'transport_complete': True, 'ceased': True,
            'forced': False, 'seconds': 1.5, 'raw_sha256': digest(b'raw'), 'raw_bytes': 3,
            'raw_base64': base64.b64encode(b'raw').decode(), 'exit_code': 0, 'profile': PROFILE,
            'image': IMAGE, 'supervisor': SUPERVISOR}


class HostContracts(unittest.TestCase):
    def test_fixed_profile_capabilities(self):
        validate_config(config())
        for key, value in (('network', True), ('host_shares', True), ('paid_dispatch', True),
                           ('read_only_inputs', False), ('operator_uid', 321), ('version', True),
                           ('profile', '0' * 64), ('image', '0' * 64)):
            with self.subTest(key=key), self.assertRaises(Failure):
                validate_config(dict(config(), **{key: value}))
        for key in LIMITS:
            changed = config()
            changed['limits'][key] += 1
            with self.subTest(key=key), self.assertRaises(Failure):
                validate_config(changed)

    def test_development_record_cannot_authorize_execution(self):
        review = {'version': 1, 'decision': 'approved-local-use', 'preparation_receipt': RECEIPT,
            'compiler': 'e670dfa79b080bad7f7d6b1d7131145c8c49068096650ebf0ac6292f098db60d',
            'guest_toolchain': '3f4227ce7b206a513e794f1393adb473a07b46e94d18bd15d1c684bbb7319797',
            'authorization_reference': 'b' * 64}
        approved = {k: v for k, v in config().items() if k in
                    ('version', 'operator_uid', 'profile', 'image', 'supervisor', 'host_code')}
        approved.update(decision='approved-trusted-execution', license_review_sha256=digest(canonical(review)),
                        authorization_reference='c' * 64)
        validate_approval(approved, config(), review)
        for change in ({'decision': 'development-review-only'}, {'host_code': '0' * 64},
                       {'profile': '0' * 64}, {'license_review_sha256': '0' * 64}):
            with self.assertRaises(Failure):
                validate_approval(dict(approved, **change), config(), review)
        with self.assertRaises(Failure):
            validate_approval(approved, config(), dict(review, decision='proposal'))

    def test_metadata_only_no_commands_roles_or_expectations(self):
        validate_request(request())
        for change in ({'action': 'exec'}, {'role': 'evaluator'}, {'expected': 'PASS'},
                       {'run': '../x'}, {'key': ''}, {'reservation': None}, {'epoch': True},
                       {'epoch': 1}, {'variant': '$(id)'}, {'probe': 'shell'}, {'version': True}):
            with self.subTest(change=change), self.assertRaises(Failure):
                validate_request(dict(request(), **change))
        for key in request():
            changed = request()
            del changed[key]
            with self.assertRaises(Failure):
                validate_request(changed)

    def test_guest_null_empty_capture_and_exact_note(self):
        value = decode_guest(canonical(guest()), 'run', 'clean')
        self.assertEqual(verdict(value, EXPECTED)['baseline_correctness'], 'pass')
        self.assertFalse(verdict(value, EXPECTED)['verified'])
        self.assertEqual(verdict(value, b'PASS')['baseline_correctness'], 'fail')

    def test_forged_or_incomplete_supervisor_record(self):
        for raw in (b'PASS', b'{"version":1', b'{"version":1,"version":1}',
                    b'X' * 1048577, b'{"seconds":NaN}'):
            with self.assertRaises(Failure):
                decode_guest(raw, 'run', 'clean')
        for change in ({'verified': True}, {'supervisor_sha256': '0' * 64},
                       {'candidate_credentials': {}}, {'seconds': -1}, {'seconds': None},
                       {'seconds': True}, {'candidate_output': '!!'}, {'expected': 'PASS'},
                       {'observed_note': None}, {'candidate_exit_success': 1}):
            with self.subTest(change=change), self.assertRaises(Failure):
                decode_guest(canonical(dict(guest(), **change)), 'run', 'clean')
        changed = guest()
        changed['candidate_credentials']['CapEff'] = '0000000000000001'
        with self.assertRaises(Failure):
            decode_guest(canonical(changed), 'run', 'clean')

    def test_candidate_raw_text_remains_data(self):
        for text in (b'PASS', b'{"expected":"PASS","verdict":"pass"}',
                     b"__import__('os').system('id')"):
            changed = dict(guest(), variant='forged-pass',
                           candidate_output=base64.b64encode(text).decode(),
                           observed_note=None, note_regular=False)
            value = decode_guest(canonical(changed), 'run', 'forged-pass')
            self.assertEqual(verdict(value, EXPECTED)['baseline_correctness'], 'fail')

    def test_metering_rejects_unknown_missing_and_wrong_binding(self):
        validate_receipt(receipt(), request())
        for change in ({'run': 'other'}, {'reservation': 'other'}, {'seconds': None},
                       {'seconds': float('inf')}, {'seconds': float('nan')}, {'seconds': 301},
                       {'ceased': False}, {'transport_complete': False}, {'error': {}},
                       {'raw_bytes': True}, {'raw_sha256': '0' * 64}, {'raw_base64': '!!'},
                       {'exit_code': True}, {'guest': {'trusted_observation': 'pass'}}):
            with self.subTest(change=change), self.assertRaises(Failure):
                validate_receipt(dict(receipt(), **change), request())

    def test_no_nonroot_record_or_executor_identity(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            path = root / 'approval'
            with self.assertRaises(Failure):
                root_record(path)
            path.write_text('{}')
            path.chmod(0o444)
            if os.getuid() != 0:
                with self.assertRaises(Failure):
                    root_record(path)
            (root / 'link').symlink_to(path)
            with self.assertRaises(Failure):
                root_record(root / 'link')
            if os.getuid() != 321:
                with self.assertRaises(Failure):
                    TrustedExecutor(root)

    def test_launcher_inventory_binds_each_host_source(self):
        loader = importlib.machinery.SourceFileLoader('trusted_launcher', str(ROOT / 'scripts/trusted-identity-integration'))
        spec = importlib.util.spec_from_loader(loader.name, loader)
        module = importlib.util.module_from_spec(spec)
        loader.exec_module(module)
        inventory = module.inventory()
        self.assertEqual(len(inventory), len(module.CODE))
        self.assertIn('research/trusted_execution.py', inventory)
        self.assertIn('tests/integration/trusted_observation.py', inventory)
        self.assertIn('scripts/trusted-identity-integration', inventory)
        self.assertNotIn('scripts/identity-integration', inventory)


if __name__ == '__main__':
    unittest.main()
