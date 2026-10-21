"""Supplementary parsing/accounting tests; UID substitution is NOT identity proof."""
import concurrent.futures
import copy
import fcntl
import os
from pathlib import Path
import socket
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'research'))
from budget import Budget, CEILINGS, vector
from common import EVALUATOR, Failure, canonical, digest, receive
from observation import bounded_hex, gate, regular_artifact, validate_observation


def resources(money: int = 0, execution: int = 0, review: int = 0) -> dict:
    return {'currency': 'USD', 'money_cents': money, 'execution_us': execution, 'review_us': review}


class BudgetChecks:
    """Same assertions can run against actual UID 320; unit subclass substitutes UID."""
    def setUp(self) -> None:
        self.directory = tempfile.TemporaryDirectory()
        self.path = Path(self.directory.name) / 'budget.sqlite'
        self.budget = Budget(self.path)
        self.principal = os.getuid()

    def tearDown(self) -> None:
        self.budget.db.close()
        self.directory.cleanup()

    def reserve(self, key: str, maximum: dict, stage: str = 'poc') -> dict:
        return self.budget.reserve(self.principal, key, maximum, key, stage, 'a' * 64)

    def test_unknown_maximum_and_currency(self) -> None:
        for value in (None, -1, float('inf'), float('nan'), True, 1.5, 2**63):
            with self.assertRaises(Failure):
                self.reserve('unknown', resources(execution=value))
        with self.assertRaises(Failure):
            vector(dict(resources(), currency='EUR'))
        self.assertEqual(self.budget.totals(self.principal)['pending'], 0)

    def test_restart_preserves_cross_profile_hold_and_stop(self) -> None:
        # Distinct profile bindings share one physical allowance, not one per run.
        self.budget.reserve(self.principal, 'synthetic', resources(5000), 'synthetic',
                            binding=digest(b'synthetic'))
        self.budget.db.close()
        self.budget = Budget(self.path, existing=True)
        self.assertEqual(self.budget.totals(self.principal)['pending'], 1)
        with self.assertRaises(Failure):
            self.budget.reserve(self.principal, 'offline', resources(1), 'offline',
                                binding=digest(b'offline'))
        self.budget.halt()
        self.budget.db.close()
        self.budget = Budget(self.path, existing=True)
        with self.assertRaises(Failure):
            self.budget.reserve(self.principal, 'trusted', resources(), 'trusted',
                                binding=digest(b'trusted-observation'))

    def test_missing_prior_store_never_creates_empty_allowance(self) -> None:
        missing = self.path.parent / 'missing.sqlite'
        with self.assertRaises((OSError, sqlite3.Error, Failure)):
            Budget(missing, existing=True)
        self.assertFalse(missing.exists())

    def test_second_launcher_lock_is_rejected(self) -> None:
        lock = self.path.parent / 'launch.lock'
        with lock.open('wb') as first:
            fcntl.flock(first, fcntl.LOCK_EX | fcntl.LOCK_NB)
            result = subprocess.run([sys.executable, '-I', '-S', '-B',
                str(Path(__file__).with_name('launch_lock_probe.py')), str(lock)],
                capture_output=True, timeout=3, env={'PATH': '/usr/bin:/bin', 'HOME': '/var/empty'})
            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stdout, b'blocked\n')

    def test_duplicate_binding_and_stage(self) -> None:
        first = self.reserve('same', resources(execution=100))
        self.assertEqual(first, self.reserve('same', resources(execution=100)))
        self.assertFalse(first['dispatch_lease'])
        for kwargs in ({'maximum': resources(execution=101)}, {'stage': 'milestone'}, {'binding': 'b' * 64}):
            args = dict(principal=self.principal, run='same', key='same',
                        maximum=resources(execution=100), stage='poc', binding='a' * 64)
            args.update(kwargs)
            with self.assertRaises(Failure):
                self.budget.reserve(**args)

    def test_ceiling_all_dimensions_poc_carry_forward(self) -> None:
        self.reserve('poc', resources(*CEILINGS['poc']))
        for extra in (resources(1), resources(execution=1), resources(review=1)):
            with self.assertRaises(Failure):
                self.reserve('exhausted', extra)
        remaining = tuple(a - b for a, b in zip(CEILINGS['milestone'], CEILINGS['poc']))
        self.reserve('milestone', resources(*remaining), 'milestone')
        for extra in (resources(1), resources(execution=1), resources(review=1)):
            with self.assertRaises(Failure):
                self.reserve('milestone-exhausted', extra, 'milestone')
        self.assertEqual(self.budget.totals(self.principal)['charged_and_reserved']['milestone'],
                         resources(*CEILINGS['milestone']))

    def test_concurrent_connections_cannot_overspend(self) -> None:
        def attempt(number: int) -> bool:
            store = Budget(self.path)
            try:
                store.reserve(self.principal, 'run-' + str(number), resources(1000, 4000_000000, 700_000000),
                              'key-' + str(number))
                return True
            except Failure:
                return False
            finally:
                store.db.close()
        with concurrent.futures.ThreadPoolExecutor(8) as pool:
            results = list(pool.map(attempt, range(12)))
        self.assertEqual(sum(results), 5)
        self.assertEqual(self.budget.totals(self.principal)['pending'], 5)

    def test_missing_delayed_metering_keeps_maximum(self) -> None:
        reservation = self.reserve('missing', resources(execution=100))
        with self.assertRaises(Failure):
            self.budget.settle(self.principal, reservation['id'],
                               {'reservation': reservation['id'], 'receipt': '0' * 64})
        self.assertEqual(self.budget.totals(self.principal)['charged_and_reserved']['poc']['execution_us'], 100)
        receipt = self.budget.meter(self.principal, reservation['id'], resources(execution=40), 'b' * 64)
        self.budget.settle(self.principal, reservation['id'], receipt)
        self.budget.settle(self.principal, reservation['id'], receipt)
        self.assertEqual(self.budget.totals(self.principal)['charged_and_reserved']['poc']['execution_us'], 40)
        with self.assertRaises(Failure):
            self.budget.meter(self.principal, reservation['id'], resources(execution=0), 'b' * 64)

    def test_execution_replay_review_and_overhead_are_additive(self) -> None:
        for name in ('execution', 'replay'):
            reservation = self.reserve(name, resources(execution=100))
            receipt = self.budget.meter(self.principal, reservation['id'], resources(execution=60), 'c' * 64)
            self.budget.settle(self.principal, reservation['id'], receipt)
        self.reserve('review-session', resources(review=20))
        self.budget.disclose_overhead(self.principal, 'selector', 7, 'selector')
        self.budget.disclose_overhead(self.principal, 'preparation', 11, 'prep')
        totals = self.budget.totals(self.principal)
        self.assertEqual(totals['charged_and_reserved']['poc'], resources(execution=120, review=20))
        self.assertEqual(totals['overhead_us'], {'selector': 7, 'preparation': 11})

    def test_overrun_halts_and_retains_maximum(self) -> None:
        reservation = self.reserve('overrun', resources(execution=100))
        with self.assertRaises(Failure):
            self.budget.meter(self.principal, reservation['id'], resources(execution=101), 'd' * 64)
        with self.assertRaises(Failure):
            self.reserve('new-work', resources())
        self.assertTrue(self.budget.totals(self.principal)['stopped'])
        self.assertEqual(self.budget.totals(self.principal)['pending'], 1)

    def test_receipt_cannot_settle_another_reservation(self) -> None:
        first, second = (self.reserve(name, resources(execution=100)) for name in ('one', 'two'))
        receipt = self.budget.meter(self.principal, first['id'], resources(execution=10), 'e' * 64)
        with self.assertRaises(Failure):
            self.budget.settle(self.principal, second['id'], dict(receipt, reservation=second['id']))

    def test_real_store_exhaustion_does_not_create_reservation(self) -> None:
        # SQLite's own page limit forces SQLITE_FULL, without mocks or host disk fill.
        pages = self.budget.db.execute('PRAGMA page_count').fetchone()[0]
        self.budget.db.execute('PRAGMA max_page_count=' + str(pages))
        error = None
        for number in range(1000):
            try:
                self.reserve('fill-' + str(number), resources())
            except Failure as exc:
                error = exc
                break
        self.assertIsNotNone(error)
        self.assertEqual(error.record['code'], 'RecoveryRequired')
        self.assertIn('full', str(error.__cause__))
        with self.assertRaises(Failure):
            self.reserve('after-full', resources())
        self.assertFalse(self.budget.db.in_transaction)
        self.assertIsNone(self.budget.db.execute('SELECT id FROM reservations WHERE key=?',
                                                ('fill-' + str(number),)).fetchone())


class BudgetUnit(BudgetChecks, unittest.TestCase):
    def setUp(self) -> None:
        self.identity_substitution = patch('budget.EVALUATOR', os.getuid())
        self.identity_substitution.start()
        self.addCleanup(self.identity_substitution.stop)
        super().setUp()


class ObservationUnit(unittest.TestCase):
    def observation(self) -> dict:
        return {'run': 'run', 'command': ['qemu'], 'qemu_version': '11.1.2',
                'assets': {name: 'a' * 64 for name in
                           ('alpine-virt-3.22.6-aarch64.iso', 'vmlinuz-virt', 'initramfs-virt')},
                'assets_unchanged': True, 'observation': b'CLEAN\n'.hex(),
                'exit_code': 0, 'raw': b'CLEAN\n'.hex(), 'isolation': '',
                'termination': {'run': 'run', 'ceased': True, 'seconds': 0.1, 'fenced': True},
                'seconds': 1.5, 'error': None, 'transport_complete': True, 'isolation_verified': True}

    def test_exact_observation_schema_and_forged_expectations(self) -> None:
        value = self.observation()
        self.assertEqual(validate_observation(value, 'run'), value)
        cases = ({'expected': 'PASS'}, {'role': 'evaluator'}, {'run': '../run'},
                 {'seconds': None}, {'seconds': float('nan')}, {'seconds': True},
                 {'exit_code': True}, {'exit_code': None}, {'transport_complete': 1},
                 {'assets': {}}, {'error': {'code': 'PASS'}}, {'termination': {}},
                 {'raw': '0'}, {'command': ['x' * 1025]}, {'qemu_version': []})
        for changes in cases:
            with self.subTest(changes=changes), self.assertRaises(Failure):
                validate_observation(dict(value, **changes), 'run')
        for text in (b'PASS\n', b'{"expected":"PASS","verdict":"pass"}',
                     b"__import__('os').system('touch /tmp/forged')"):
            forged = dict(value, observation=text.hex())
            self.assertEqual(validate_observation(forged, 'run')['observation'], text.hex())
            self.assertEqual(gate(forged)['state'], 'not-run')

    def test_bounded_hex_rejects_truncated_oversized_executable_text(self) -> None:
        for value in ('0', 'zz', '00 ' , '00' * 1048577, None, "__import__('os').system('id')"):
            with self.assertRaises(Failure):
                bounded_hex(value)
        self.assertEqual(bounded_hex(b'PASS\n'.hex()), b'PASS\n')
        self.assertNotEqual(bounded_hex(b'PASS\n'.hex()), b'CLEAN\n')

    def test_wire_duplicate_keys_nan_truncation_unknown_shape(self) -> None:
        for raw in (b'{"action":"start","action":"stop"}\n', b'{"x":NaN}\n',
                    b'{"x":1}', b'[]\n', b'{"x":"broken\n'):
            left, right = socket.socketpair()
            try:
                left.sendall(raw)
                left.shutdown(socket.SHUT_WR)
                with self.assertRaises(Failure):
                    receive(right)
            finally:
                left.close()
                right.close()

    def test_artifacts_no_traversal_symlinks_executable_or_wrong_hash(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            data = b'bounded data'
            name = digest(data)
            path = root / name
            path.write_bytes(data)
            self.assertEqual(regular_artifact(root, name), data)
            path.chmod(0o700)
            with self.assertRaises(Failure):
                regular_artifact(root, name)
            path.unlink()
            target = root / 'target'
            target.write_bytes(data)
            path.symlink_to(target)
            with self.assertRaises(Failure):
                regular_artifact(root, name)
            with self.assertRaises(Failure):
                regular_artifact(root, '../target')

    def test_legacy_control_receipt_never_proves_trusted_observation(self) -> None:
        self.assertEqual(gate({'transport_complete': True, 'log': 'PASS'})['state'], 'not-run')
        self.assertEqual(gate({'transport_complete': False})['state'], 'fail')
        for value in ({}, {'run': 'x'}, {'role': 'evaluator'}, {'expected': 'PASS'}):
            with self.assertRaises(Failure):
                validate_observation(value, 'run')


if __name__ == '__main__':
    unittest.main(verbosity=2)
