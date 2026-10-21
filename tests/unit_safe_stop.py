import os
import json
from pathlib import Path
import sqlite3
import tempfile
import sys
import threading
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'research'))
import control
import ledger
from common import Failure
from control import StopCoordinator


class SafeStop(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix='.tmp-safe-stop-')
        self.addCleanup(self.directory.cleanup)
        self.operator = 502
        self.patch_ledger = patch.object(ledger, 'EVALUATOR', os.getuid())
        self.patch_control = patch.object(control, 'EVALUATOR', os.getuid())
        self.patch_ledger.start(); self.patch_control.start()
        self.addCleanup(self.patch_ledger.stop); self.addCleanup(self.patch_control.stop)
        self.calls = []

    def coordinator(self, terminator=None, baseline=None):
        def default(run, grace, kill_wait):
            self.calls.append((run, grace, kill_wait))
            return {'ceased': True, 'forced': True, 'seconds': 0.1, 'baseline_ok': True}
        return StopCoordinator(Path(self.directory.name).absolute() / 'control',
                               operator_uid=self.operator, terminator=terminator or default,
                               baseline_verifier=baseline)

    def test_stop_atomic_idempotency_and_reference(self):
        coordinator = self.coordinator()
        self.addCleanup(coordinator.close)
        first = coordinator.handle(self.operator, {'action': 'stop', 'run': 'run-1', 'key': 'stop-key'})
        self.assertEqual(first['state'], 'stopped-safely')
        self.assertEqual(coordinator.stop(self.operator, 'run-1', 'stop-key'), first)
        repeated = coordinator.stop(self.operator, 'run-1', 'stop-key-2')
        self.assertEqual(repeated['epoch'], first['epoch'])
        self.assertEqual(repeated['primary_operation'], first['operation'])
        self.assertEqual(len(self.calls), 1)
        self.assertFalse(repeated['retry_authorized'])
        self.assertFalse(repeated['promotion_authorized'])

    def test_launch_fence_and_distinct_principals(self):
        coordinator = self.coordinator()
        self.addCleanup(coordinator.close)
        receipt = coordinator.register_launch(os.getuid(), 'run-race', 4242, 0)
        self.assertFalse(receipt['launch_lease'])
        self.assertTrue(coordinator.can_launch('run-race', 0))
        with self.assertRaises(Failure):
            coordinator.register_launch(321, 'run-race', 4243, 0)
        stopped = coordinator.handle(self.operator, {'action': 'stop', 'run': 'run-race', 'key': 'race-stop'})
        self.assertEqual(stopped['state'], 'stopped-safely')
        self.assertFalse(coordinator.can_launch('run-race', 0))
        self.assertFalse(coordinator.can_launch('run-race', stopped['epoch']))
        with self.assertRaises(Failure):
            coordinator.stop(321, 'run-other', 'runner-key')

    def test_status_requires_operation_digest_and_watchdog_identity(self):
        coordinator = self.coordinator()
        self.addCleanup(coordinator.close)
        stopped = coordinator.handle(self.operator, {'action': 'stop', 'run': 'run-status',
                                                     'key': 'status-key'})
        status = coordinator.handle(self.operator, {'action': 'status',
                                                    'operation': stopped['operation']})
        self.assertEqual(status, stopped)
        watchdog = coordinator.handle(os.getuid(), {'action': 'status',
                                                    'operation': stopped['operation']})
        self.assertEqual(watchdog, stopped)
        with self.assertRaises(Failure):
            coordinator.handle(self.operator, {'action': 'status', 'operation': 'run-status'})

    def test_admission_fence_is_durable_and_registry_free(self):
        coordinator = self.coordinator()
        self.addCleanup(coordinator.close)
        before = coordinator.admission_fence(os.getuid(), 'run-admission-unit', 'a' * 64,
                                             'admission-before')
        self.assertEqual(before['admission'], 'allowed-before-registry')
        self.assertFalse(before['registry_effect'])
        stopped = coordinator.handle(self.operator, {'action': 'stop', 'run': 'run-admission-unit',
                                                     'key': 'admission-stop'})
        after = coordinator.admission_fence(os.getuid(), 'run-admission-unit', 'b' * 64,
                                            'admission-after')
        self.assertEqual(after['admission'], 'blocked')
        self.assertFalse(after['registry_effect'])
        rows = coordinator.db.execute('SELECT proposal,blocked,event_digest FROM admission_fences '
                                      'WHERE run=? ORDER BY proposal',
                                      ('run-admission-unit',)).fetchall()
        self.assertEqual([row[:2] for row in rows], [('a' * 64, 0), ('b' * 64, 1)])
        self.assertTrue(all(len(row[2]) == 64 for row in rows))
        self.assertGreaterEqual(stopped['epoch'], 1)

    def test_concurrent_same_key_returns_one_original_receipt(self):
        coordinator = self.coordinator()
        self.addCleanup(coordinator.close)
        barrier = threading.Barrier(2)
        results = []

        def request():
            barrier.wait()
            results.append(coordinator.handle(self.operator, {
                'action': 'stop', 'run': 'run-concurrent', 'key': 'same-key'}))

        threads = [threading.Thread(target=request) for _ in range(2)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        self.assertEqual(results[0], results[1])
        self.assertEqual(len(self.calls), 1)

    def test_cancel_failure_and_bad_baseline_are_recovery(self):
        coordinator = self.coordinator(terminator=lambda run, grace, wait: (_ for _ in ()).throw(
            Failure('Unavailable', 'worker unavailable')))
        self.addCleanup(coordinator.close)
        pending = coordinator.stop(self.operator, 'run-fail', 'fail-key')
        with self.assertRaises(Failure):
            coordinator.terminate(os.getuid(), pending['operation'])
        stopped = coordinator.stop_status(self.operator, pending['operation'])
        self.assertEqual(stopped['state'], 'recovery-required')
        self.assertEqual(stopped['outcome']['code'], 'Unavailable')
        coordinator.close()
        baseline = self.coordinator(baseline=lambda outcome: False)
        self.addCleanup(baseline.close)
        result = baseline.handle(self.operator, {'action': 'stop', 'run': 'run-baseline', 'key': 'baseline-key'})
        self.assertEqual(result['state'], 'recovery-required')

    def test_crashed_transaction_leaves_no_stop_state_or_event(self):
        coordinator = self.coordinator()
        self.addCleanup(coordinator.close)
        coordinator.db.execute("CREATE TRIGGER stop_fault BEFORE INSERT ON idempotency BEGIN SELECT RAISE(ABORT,'crash'); END")
        with self.assertRaises(Failure):
            coordinator.stop(self.operator, 'run-crash', 'crash-key')
        self.assertEqual(coordinator.ledger.tip(), '0' * 64)
        self.assertEqual(coordinator.db.execute('SELECT count(*) FROM control_runs').fetchone()[0], 0)
        self.assertEqual(coordinator.db.execute('SELECT count(*) FROM stop_operations').fetchone()[0], 0)
        self.assertTrue(coordinator.halted)
        markers = list((Path(self.directory.name) / 'control' / 'recoveries').glob('recovery-*.json'))
        self.assertEqual(len(markers), 1)
        marker = json.loads(markers[0].read_bytes())
        self.assertEqual(marker['run'], 'run-crash')
        self.assertFalse(marker['retry_authorized'])


if __name__ == '__main__':
    unittest.main()
