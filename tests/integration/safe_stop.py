#!/usr/bin/env python3
"""Real UID-320/321/501 host safe-stop integration; no mocks or skips."""
from __future__ import annotations
import json
import os
from pathlib import Path
import subprocess
import sys
import threading
import time
import unittest
from common import EVALUATOR, RUNNER, Failure, digest
from control import StopCoordinator, StopService
from trusted_transport import control_call


def alive(pid: int) -> bool:
    try:
        raw = subprocess.check_output(['/bin/ps', '-o', 'state=', '-p', str(pid)], timeout=1)
        state = raw.decode('ascii', 'ignore').strip()
        return bool(state) and state != 'Z'
    except (OSError, subprocess.SubprocessError):
        return False


class Mandatory(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if os.getuid() != EVALUATOR or len(sys.argv) != 2:
            raise SystemExit('AWAITING_PARENT_IDENTITY_RUN: actual evaluator UID 320 and runtime required')
        cls.runtime = Path(sys.argv[1]).absolute()
        if cls.runtime.parent != Path('/private/tmp') or not cls.runtime.name.startswith('grrr-safe-stop-'):
            raise SystemExit('Untrusted safe-stop runtime')
        cls.operator = 501
        cls.pids = json.loads((cls.runtime / 'processes.json').read_bytes())
        cls.baseline = cls.runtime / 'baseline.bin'
        cls.baseline_digest = digest(cls.baseline.read_bytes())
        cls.control_socket = cls.runtime / 'ipc' / 'control-worker.sock'

        def terminate(run: str, grace: int, wait: int) -> dict:
            return control_call(cls.control_socket, {
                'action': 'stop', 'run': run, 'pid': cls.pids[run],
                'term_grace_seconds': grace, 'kill_wait_seconds': wait,
                'baseline_digest': cls.baseline_digest},
                expected_uid=RUNNER, timeout=float(grace + wait + 1))

        cls.coordinator = StopCoordinator(cls.runtime / 'evaluator', operator_uid=cls.operator,
                                          terminator=terminate, term_grace_seconds=1,
                                          kill_wait_seconds=1)
        cls.service = StopService(cls.runtime / 'ipc', cls.coordinator)
        (cls.runtime / 'evaluator' / 'service-ready').write_bytes(b'ready\n')
        deadline = time.monotonic() + 20
        external = cls.runtime / 'external-probes.json'
        while time.monotonic() < deadline and not external.is_file():
            time.sleep(0.05)
        if not external.is_file():
            raise SystemExit('Parent identity probes did not complete')
        cls.external = json.loads(external.read_bytes())
        for name, probe in cls.external.items():
            if probe.get('code') != 0:
                raise SystemExit('Identity probe ' + name + ' failed')

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'service'):
            cls.service.close()
        if hasattr(cls, 'coordinator'):
            cls.coordinator.close()

    def test_01_operator_path_cancels_term_resistant_runner(self):
        authorized = json.loads(self.external['authorized-operator']['stdout'])
        self.assertEqual(authorized['uid'], self.operator)
        self.assertFalse(authorized['denied'])
        result = authorized['result']
        self.assertEqual(result['state'], 'stopped-safely')
        self.assertEqual(result['epoch'], 1)
        self.assertEqual(len(result['receipt']), 64)
        self.assertTrue(result['outcome']['ceased'])
        self.assertTrue(result['outcome']['forced'])
        self.assertLessEqual(result['outcome']['seconds'], 3)
        self.assertTrue(result['outcome']['baseline_ok'])
        self.assertFalse(alive(self.pids['run-operator']))
        self.assertEqual(digest(self.baseline.read_bytes()), self.baseline_digest)
        denied_runner = json.loads(self.external['denied-runner']['stdout'])
        denied_watchdog = json.loads(self.external['denied-watchdog-operator']['stdout'])
        self.assertEqual((denied_runner['uid'], denied_runner['denied'],
                          denied_runner['error']['code']), (RUNNER, True, 'Unauthorized'))
        self.assertEqual((denied_watchdog['uid'], denied_watchdog['denied'],
                          denied_watchdog['error']['code']), (self.operator, True, 'Unauthorized'))

    def test_02_watchdog_safety_authority_has_no_admission_authority(self):
        result = self.coordinator.handle(EVALUATOR, {
            'action': 'stop', 'run': 'run-watchdog', 'key': 'watchdog-stop'})
        self.assertEqual(result['state'], 'stopped-safely')
        self.assertFalse(result['retry_authorized'])
        self.assertFalse(result['promotion_authorized'])
        self.assertIsNone(result['reason'])
        self.assertFalse(alive(self.pids['run-watchdog']))
        fence = self.coordinator.admission_fence(EVALUATOR, 'run-watchdog', 'a' * 64,
                                                 'watchdog-fence-key')
        self.assertEqual(fence['admission'], 'blocked')
        self.assertFalse(fence['registry_effect'])

    def test_03_idempotency_and_distinct_key_reference(self):
        primary = self.coordinator.stop_status(self.operator, json.loads(
            self.external['authorized-operator']['stdout'])['result']['operation'])
        same = self.coordinator.stop(self.operator, 'run-operator', 'operator-stop')
        distinct = self.coordinator.stop(self.operator, 'run-operator', 'operator-stop-second')
        self.assertEqual(same, primary)
        self.assertEqual(distinct['epoch'], primary['epoch'])
        self.assertEqual(distinct['primary_operation'], primary['operation'])
        self.assertEqual(distinct['state'], primary['state'])
        cancellations = self.coordinator.db.execute(
            "SELECT count(*) FROM events WHERE body LIKE '%\"kind\":\"safe-stop-cancellation\"%' "
            "AND body LIKE '%run-operator%'").fetchone()[0]
        self.assertEqual(cancellations, 1)

    def test_04_stop_and_launch_race_has_no_post_fence_start(self):
        barrier = threading.Barrier(2)
        outcomes = []

        def launch():
            barrier.wait()
            try:
                outcomes.append(('launch', self.coordinator.register_launch(
                    EVALUATOR, 'run-race', self.pids['run-race'], 0)['epoch']))
            except Failure as exc:
                outcomes.append(('launch-denied', exc.record['code']))

        def stop():
            barrier.wait()
            outcomes.append(('stop', self.coordinator.handle(self.operator, {
                'action': 'stop', 'run': 'run-race', 'key': 'race-stop'})['state']))

        threads = [threading.Thread(target=launch), threading.Thread(target=stop)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        self.assertEqual(len(outcomes), 2)
        self.assertTrue(any(kind == 'stop' and value == 'stopped-safely'
                            for kind, value in outcomes))
        if ('launch', 0) in outcomes:
            self.assertFalse(alive(self.pids['run-race']))
        else:
            self.assertIn(('launch-denied', 'Stopped'), outcomes)
        self.assertFalse(self.coordinator.can_launch('run-race', 0))

    def test_05_unavailable_worker_is_recovery_not_safe_stop(self):
        def unavailable(run: str, grace: int, wait: int) -> dict:
            raise Failure('Unavailable', 'control worker unavailable')

        recovery = StopCoordinator(self.runtime / 'evaluator', operator_uid=self.operator,
                                   terminator=unavailable)
        self.addCleanup(recovery.close)
        pending = recovery.stop(self.operator, 'run-unavailable', 'unavailable-key')
        self.assertEqual(pending['state'], 'stopping')
        with self.assertRaises(Failure):
            recovery.terminate(EVALUATOR, pending['operation'])
        status = recovery.stop_status(self.operator, pending['operation'])
        self.assertEqual(status['state'], 'recovery-required')
        self.assertEqual(status['outcome']['code'], 'Unavailable')
        self.assertFalse(status['retry_authorized'])
        self.assertFalse(status['promotion_authorized'])
        self.assertTrue(alive(self.pids['run-unavailable']))
        self.assertFalse(self.coordinator.can_launch('run-unavailable', 0))

    def test_06_hard_trigger_preserves_baseline_and_evidence(self):
        triggers = ('budget-exhausted', 'protected-write', 'isolation-failure',
                    'missing-dependency', 'evidence-integrity-failure',
                    'repeated-unreproducibility')
        results = []
        for index, trigger in enumerate(triggers):
            results.append(self.coordinator.handle(self.operator, {
                'action': 'stop', 'run': 'run-trigger', 'key': 'trigger-key-' + str(index),
                'reason': trigger}))
        self.assertEqual({result['state'] for result in results}, {'stopped-safely'})
        self.assertEqual([result['reason'] for result in results], list(triggers))
        self.assertEqual(len({result['primary_operation'] for result in results}), 1)
        self.assertEqual(digest(self.baseline.read_bytes()), self.baseline_digest)
        recorded = self.coordinator.db.execute(
            "SELECT json_extract(body,'$.reason') FROM events WHERE "
            "json_extract(body,'$.run')='run-trigger' AND json_extract(body,'$.kind') "
            "IN ('safe-stop','safe-stop-reference')").fetchall()
        self.assertEqual([row[0] for row in recorded], list(triggers))
        cancellations = self.coordinator.db.execute(
            "SELECT count(*) FROM events WHERE body LIKE '%\"kind\":\"safe-stop-cancellation\"%' "
            "AND body LIKE '%run-trigger%'").fetchone()[0]
        self.assertEqual(cancellations, 1)

    def test_07_admission_fence_records_actual_durable_rejection(self):
        before = self.coordinator.admission_fence(EVALUATOR, 'run-admission', 'b' * 64,
                                                  'admission-before-key')
        self.assertEqual(before['admission'], 'allowed-before-registry')
        self.assertFalse(before['registry_effect'])
        stopped = self.coordinator.handle(self.operator, {
            'action': 'stop', 'run': 'run-admission', 'key': 'admission-stop-key'})
        self.assertEqual(stopped['state'], 'stopped-safely')
        after = self.coordinator.admission_fence(EVALUATOR, 'run-admission', 'c' * 64,
                                                 'admission-after-key')
        self.assertEqual(after['admission'], 'blocked')
        self.assertFalse(after['registry_effect'])
        rows = self.coordinator.db.execute(
            'SELECT proposal,blocked FROM admission_fences WHERE run=? ORDER BY proposal',
            ('run-admission',)).fetchall()
        self.assertEqual(rows, [('b' * 64, 0), ('c' * 64, 1)])

    def test_08_failed_stop_transaction_fences_until_recovery(self):
        self.coordinator.register_launch(EVALUATOR, 'run-crash', self.pids['run-crash'], 0)
        tip = self.coordinator.ledger.tip()
        events = self.coordinator.db.execute('SELECT count(*) FROM events').fetchone()[0]
        self.coordinator.db.execute(
            "CREATE TRIGGER stop_fault BEFORE INSERT ON idempotency "
            "BEGIN SELECT RAISE(ABORT,'crash'); END")
        with self.assertRaises(Failure):
            self.coordinator.stop(self.operator, 'run-crash', 'crash-key')
        self.assertEqual(self.coordinator.ledger.tip(), tip)
        self.assertEqual(self.coordinator.db.execute('SELECT count(*) FROM events').fetchone()[0], events)
        self.assertIsNone(self.coordinator.db.execute(
            'SELECT 1 FROM control_runs WHERE run=?', ('run-crash',)).fetchone())
        self.assertFalse(alive(self.pids['run-crash']))
        self.assertTrue(self.coordinator.halted)
        markers = list((self.runtime / 'evaluator' / 'recoveries').glob('recovery-*.json'))
        self.assertEqual(len(markers), 1)
        marker = json.loads(markers[0].read_bytes())
        self.assertEqual(marker['run'], 'run-crash')
        self.assertFalse(marker['retry_authorized'])
        with self.assertRaises(Failure):
            self.coordinator.admission_fence(EVALUATOR, 'run-crash', 'd' * 64, 'crash-fence-key')


if __name__ == '__main__':
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(Mandatory)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    runtime = Path(sys.argv[1]).absolute() if len(sys.argv) == 2 else None
    summary = {'required': suite.countTestCases(), 'executed': result.testsRun,
               'skipped': len(result.skipped), 'failures': len(result.failures),
               'errors': len(result.errors), 'admission': 'blocked', 'guest_executed': False}
    if runtime is not None:
        (runtime / 'evaluator' / 'integration-summary.json').write_bytes(
            json.dumps(summary, sort_keys=True).encode('ascii'))
    raise SystemExit(0 if result.wasSuccessful() and result.testsRun == suite.countTestCases()
                     and not result.skipped else 1)
