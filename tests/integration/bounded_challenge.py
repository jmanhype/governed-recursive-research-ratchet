"""Mandatory real-service/VM tests. Missing infrastructure is failure, never skip."""
import concurrent.futures
import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'research'))
from common import DENIED, GATES, PACKETS, Failure, call, canonical, digest, runtime_binding
from ledger import verifySnapshot
from runner import projection


class BoundedChallenge(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        binding = runtime_binding(ROOT)
        cls.runtime = Path(binding['runtime'])
        cls.evidence = Path(binding['evidence'])
        cls.endpoint = cls.runtime / 'ipc/evaluator.sock'
        state = call(cls.endpoint, {'action': 'list'}, timeout=2)
        cls.policy = state['policy']
        cls.clean = digest(canonical(PACKETS['clean']))
        cls.faulty = digest(canonical(PACKETS['faulty']))
        cls.counter = 0

    def request(self, **overrides: object) -> dict:
        type(self).counter += 1
        return dict({'action': 'start', 'policy': self.policy, 'challenge': 'grrr-walk-001',
                     'variant': self.clean, 'key': 'test-' + str(self.counter), 'epoch': 0}, **overrides)

    def denied(self, request: dict, code: str) -> None:
        with self.assertRaises(Failure) as result:
            call(self.endpoint, request)
        self.assertEqual(result.exception.record['code'], code)

    def infrastructure_control(self, name: str, expected_exit: int) -> None:
        receipt = self.runtime / 'negative-controls.json'
        self.assertEqual(receipt.stat().st_uid, 0)
        self.assertEqual(receipt.stat().st_mode & 0o222, 0)
        controls = json.loads(receipt.read_bytes())
        self.assertEqual(set(controls), {'missing-policy', 'absent-vm'})
        self.assertEqual(controls[name]['observed_code'], 'Unavailable')
        self.assertEqual(controls[name]['returncode'], expected_exit)
        self.assertEqual(digest((self.evidence / (name + '.log')).read_bytes()), controls[name]['log_sha256'])
        self.assertTrue(controls[name]['absence_confirmed'])
        implementation = 'evaluator.py' if name == 'missing-policy' else 'execution.py'
        self.assertEqual(digest((ROOT / 'research' / implementation).read_bytes()), controls[name]['implementation_sha256'])

    def test_00a_missing_policy_real_control(self) -> None:
        self.infrastructure_control('missing-policy', 3)

    def test_00b_absent_vm_real_control(self) -> None:
        self.infrastructure_control('absent-vm', 0)

    def test_01_direct_stop_before_synthetic(self) -> None:
        denied = self.request()
        self.denied(denied, 'GateBlocked')
        self.denied(dict(denied, variant=self.faulty), 'StaleBinding')
        request = self.request(action='preflight')
        with concurrent.futures.ThreadPoolExecutor(1) as pool:
            future = pool.submit(call, self.endpoint, request)
            deadline = time.monotonic() + 50  # Approved boot + bounded bootstrap, not a longer VM boot bound.
            run = None
            while time.monotonic() < deadline:
                runs = call(self.endpoint, {'action': 'list'})['runs']
                if runs:
                    run = runs[-1]
                    status = call(self.endpoint, {'action': 'status', 'run': run})
                    if status['execution'] != 'running':
                        self.fail('Preflight ended before verified readiness: ' + json.dumps(status))
                    if status.get('executor', {}).get('ready') and status['executor']['active']:
                        break
                time.sleep(0.05)
            else:
                self.fail('Preflight did not reach verified readiness before test deadline')
            self.assertIsNotNone(run)
            started = time.monotonic()
            stopped = call(self.endpoint, {'action': 'stop', 'run': run, 'key': 'stop-preflight'})
            self.assertTrue(stopped['ceased'])
            self.assertLess(time.monotonic() - started, 2)
            report = future.result(timeout=10)
        self.assertEqual(report['execution'], 'stopped')
        self.assertTrue(report['isolation_verified'])
        self.assertEqual(report['observation_error']['code'], 'Stopped')
        self.assertTrue(report['cessation_verified'])
        self.assertTrue(call(self.endpoint, {'action': 'list'})['preflight'])
        for key in ('stop-preflight', 'stop-again'):
            self.assertTrue(call(self.endpoint, {'action': 'stop', 'run': run, 'key': key})['ceased'])

    def safety_probe(self, name: str, expected_message: str) -> dict:
        report = call(self.endpoint, self.request(action='probe-' + name))
        self.assertEqual(report['execution'], 'error')
        self.assertEqual(report['finding'], 'not-evaluated')
        self.assertEqual(report['observation_error']['code'], 'GateBlocked')
        self.assertEqual(report['observation_error']['message'], expected_message)
        self.assertTrue(report['cessation_verified'])
        self.assertTrue(report['isolation_verified'])
        snapshot = call(self.endpoint, {'action': 'evidence', 'run': report['run']})
        verifySnapshot(snapshot, report['anchor'])
        (self.evidence / (name + '-control.json')).write_bytes(canonical(snapshot))
        (self.evidence / (name + '-control.anchor')).write_text(report['anchor'] + '\n')
        observed = json.loads(bytes.fromhex(snapshot['objects'][snapshot['events'][-1]['event']['objects'][0]]))
        self.assertTrue(observed['assets_unchanged'])
        self.assertEqual(len(bytes.fromhex(snapshot['objects'][observed['raw_digest']])), observed['raw_bytes'])
        self.assertLessEqual(observed['raw_bytes'], 1048576)
        self.assertTrue(call(self.endpoint, {'action': 'list'})['preflight'], 'Services must remain responsive')
        return observed

    def test_01a_active_output_cap(self) -> None:
        observed = self.safety_probe('output', 'Guest output exceeded cap')
        self.assertEqual(observed['raw_bytes'], 1048576)

    def test_01b_active_command_deadline(self) -> None:
        observed = self.safety_probe('deadline', 'Evaluator-approved deadline exceeded')
        self.assertGreaterEqual(observed['seconds'], 5)
        self.assertLess(observed['seconds'], 30)

    def test_02_clean_and_faulty_real_vm(self) -> None:
        for name, variant, expected in [('clean', self.clean, 'pass'), ('faulty', self.faulty, 'fail')]:
            command = [str(ROOT / 'bin/grrr'), 'start', '--policy', self.policy,
                       '--challenge', 'grrr-walk-001', '--variant', variant]
            result = subprocess.run(command, capture_output=True, text=True, timeout=310, cwd=ROOT)
            self.assertEqual(result.returncode, 0 if name == 'clean' else 3, result.stdout + result.stderr)
            report = json.loads(result.stdout)
            self.assertEqual(report['assertion'], expected)
            self.assertEqual(report['execution'], 'completed')
            self.assertFalse(report['verified'])
            self.assertEqual(report['admission'], 'blocked')
            snapshot = call(self.endpoint, {'action': 'evidence', 'run': report['run']})
            self.assertEqual(verifySnapshot(snapshot, report['anchor']), snapshot)
            evidence = self.evidence
            evidence.mkdir(exist_ok=True, parents=True)
            (evidence / (name + '.json')).write_bytes(canonical(snapshot))
            (evidence / (name + '.anchor')).write_text(report['anchor'] + '\n')
            (evidence / (name + '.md')).write_text(projection(snapshot, 'markdown', 'technical') + '\n')
            for format in ('text', 'markdown', 'json'):
                result = subprocess.run([str(ROOT / 'bin/grrr'), 'evidence', report['run'],
                    '--level', 'technical', '--format', format], capture_output=True, text=True, timeout=5, cwd=ROOT)
                self.assertEqual(result.returncode, 0)
                self.assertIn(report['snapshot_id'], result.stdout)
            self.assertEqual(set(report['gates']), set(GATES))
            for gate in ('independent_replay', 'reviewer_outcome', 'action_specific_human_approval'):
                self.assertEqual(report['gates'][gate]['state'], 'not-run')
            corrupt = copy.deepcopy(snapshot)
            corrupt['events'].pop()
            with self.assertRaises(Failure):
                verifySnapshot(corrupt, report['anchor'])
            type(self).saved_run_id = report['run']

    def test_03_all_denied_capabilities(self) -> None:
        for action in DENIED:
            with self.subTest(action=action):
                self.denied({'action': action}, 'GateBlocked')

    def test_04_invalid_metadata_and_bindings(self) -> None:
        self.denied(self.request(policy='0' * 64), 'StaleBinding')
        self.denied(self.request(epoch=1), 'StaleBinding')
        self.denied(self.request(challenge='../private'), 'InvalidInput')
        self.denied(self.request(role='operator'), 'InvalidInput')
        self.denied(self.request(variant='PASS'), 'InvalidInput')
        request = self.request()
        del request['policy']
        self.denied(request, 'InvalidInput')

    def test_05_idempotency_mismatch_and_concurrency(self) -> None:
        request = self.request()
        with concurrent.futures.ThreadPoolExecutor(1) as pool:
            future = pool.submit(call, self.endpoint, request)
            time.sleep(0.5)
            self.denied(dict(request, variant=self.faulty), 'StaleBinding')
            self.denied(self.request(), 'BudgetExceeded')
            first = future.result(timeout=310)
        self.assertEqual(call(self.endpoint, request)['run'], first['run'])

    def test_06_unavailable_and_unauthorized_executor(self) -> None:
        with self.assertRaises(Failure) as result:
            call(self.runtime / 'ipc/absent.sock', {}, timeout=1)
        self.assertEqual(result.exception.record['code'], 'Unavailable')
        with self.assertRaises(Failure) as result:
            call(self.runtime / 'ipc/executor.sock', {'action': 'stop', 'run': 'forged'}, timeout=2)
        self.assertEqual(result.exception.record['code'], 'Unauthorized')

    def test_07_downstream_is_unavailable(self) -> None:
        # A missing prerequisite is an explicit failure, not a TestCase.run method.
        self.assertTrue(hasattr(self, 'saved_run_id'), 'Clean/faulty execution did not produce a saved run ID')
        for action in ('review', 'recover', 'decide'):
            self.denied({'action': action, 'run': self.saved_run_id}, 'GateBlocked')

    def test_08_protected_files_are_not_operator_writable(self) -> None:
        for path in ('policy.json', 'ledger.sqlite'):
            with self.assertRaises(PermissionError):
                (self.runtime / 'evaluator' / path).read_bytes()


if __name__ == '__main__':
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(BoundedChallenge)
    required = suite.countTestCases()
    print('Required integration tests:', required, flush=True)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print(json.dumps({'required': required, 'executed': result.testsRun, 'skipped': len(result.skipped),
                      'failures': len(result.failures), 'errors': len(result.errors)}))
    raise SystemExit(0 if result.wasSuccessful() and result.testsRun == required and not result.skipped else 1)
