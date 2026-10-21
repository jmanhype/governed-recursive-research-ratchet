"""Ten mandatory scenarios; real UID/service/guest only, no substitutes/skips.

Run by the approved dedicated root launcher from its protected code snapshot.
Direct nonprivileged invocation fails without starting any guest.
"""
import base64
import json
import os
from pathlib import Path
import socket
import sys
import time
import unittest
import uuid
from concurrent.futures import ThreadPoolExecutor

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'research'))
sys.path.insert(0, str(ROOT / 'tests'))
from common import EVALUATOR, Failure, MAX_WIRE, call, canonical, digest, peer_uid, receive, require
from unit_trusted_observation import BudgetChecks
from observation import regular_artifact
from trusted_evaluation import Session
from trusted_execution import root_record, validate_config, validate_approval


class ActualIdentityBudget(BudgetChecks, unittest.TestCase):
    """Only this mixin is reused, never BudgetUnit's identity substitution."""


class Mandatory(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        require(os.getuid() == EVALUATOR and len(sys.argv) == 2, 'Unauthorized',
                'AWAITING_PARENT_IDENTITY_RUN: approved dedicated launcher and actual evaluator UID 320 required')
        cls.runtime = Path(sys.argv[1])
        require(cls.runtime.parent == Path('/private/tmp') and cls.runtime.name.startswith('grrr-trusted-')
                and cls.runtime.stat().st_uid == 0 and not cls.runtime.is_symlink(),
                'Unauthorized', 'Untrusted runtime')
        config = validate_config(root_record(cls.runtime / 'runner/config.json'))
        validate_approval(root_record(cls.runtime / 'runner/approval.json'), config,
                          root_record(cls.runtime / 'runner/license.json'))
        cls.session = Session(cls.runtime / 'evaluator')
        cls.endpoint = cls.session.endpoint

    def status(self, run='status'):
        return call(self.endpoint, {'action': 'status', 'run': run})

    def wait(self, run, predicate, seconds=305):
        deadline = time.monotonic() + seconds
        while time.monotonic() < deadline:
            status = self.status(run)
            if predicate(status):
                return status
            time.sleep(0.05)
        self.fail('Bounded real service observation deadline exceeded')

    def test_01_preflight_stop_before_candidate(self):
        request = self.session.prepare(probe='stop')
        with ThreadPoolExecutor(1) as pool:
            future = pool.submit(call, self.endpoint, request)
            self.wait(request['run'], lambda value: value['ready'], 45)
            started = time.monotonic()
            receipt = call(self.endpoint, {'action': 'stop', 'run': request['run']})
            self.assertLess(time.monotonic() - started, 2)
            self.assertTrue(receipt['fenced'])
            result = future.result(timeout=9)
        self.assertTrue(result['ceased'])
        self.assertFalse(result['transport_complete'])
        with self.assertRaises(Failure):
            self.session.accept(request, result)
        self.assertGreaterEqual(self.session.budget.totals(EVALUATOR)['pending'], 1)

    def test_02_clean_guest_supervisor_observation(self):
        result, decision = self.session.execute()
        guest = result['guest']
        self.assertTrue(guest['kernel_lock_held_by_supervisor'])
        self.assertTrue(guest['note_absent_during_hold'])
        self.assertTrue(guest['candidate_cessation'])
        self.assertEqual(decision['baseline_correctness'], 'pass')
        self.assertFalse(decision['verified'])
        self.assertEqual(decision['admission'], 'blocked')
        self.assertEqual(decision['independent_replay'], 'not-run')

    def test_03_forgery_and_malformed_candidate_data(self):
        for variant in ('forged-pass', 'altered-expectations', 'malformed', 'oversized'):
            with self.subTest(variant=variant):
                result, decision = self.session.execute(variant)
                self.assertEqual(decision['baseline_correctness'], 'fail')
                self.assertFalse(decision['verified'])
                self.assertEqual(decision['admission'], 'blocked')
                if variant == 'oversized':
                    self.assertTrue(result['guest']['output_exceeded'])
                else:
                    self.assertTrue(base64.b64decode(result['guest']['candidate_output']))

    def test_04_actual_mutation_and_control_impersonation(self):
        host = root_record(self.runtime / 'host-probes.json')
        self.assertEqual(len(host), 2)
        self.assertTrue(all(all(item['denials'].values()) for item in host))
        expected = {'read_supervisor_denied', 'write_supervisor_denied', 'read_expectation_denied',
                    'create_control_denied', 'parent_stdout_denied', 'parent_memory_denied',
                    'console_denied', 'signal_supervisor_denied', 'replace_supervisor_denied'}
        for variant in ('mutation', 'impersonation'):
            with self.subTest(variant=variant):
                result, decision = self.session.execute(variant)
                probes = json.loads(base64.b64decode(result['guest']['candidate_output']))
                self.assertEqual(set(probes), expected)
                self.assertTrue(all(value is True for value in probes.values()))
                self.assertTrue(result['guest']['supervisor_unchanged'])
                self.assertEqual(decision['baseline_correctness'], 'fail')

    def test_05_service_wire_schema_and_filesystem_controls(self):
        before = self.status()['launches']
        request = {'action': 'dispatch', 'version': 1, 'run': 'invalid', 'arm': 'trusted-control',
                   'challenge': 'vlt-lock-observation-001', 'variant': 'clean', 'key': 'invalid',
                   'reservation': 'unreserved', 'epoch': 0, 'probe': None}
        for change in ({'action': 'shell'}, {'role': 'evaluator'}, {'run': '../escape'},
                       {'variant': "__import__('os').system('id')"}, {'expected': 'PASS'},
                       {'epoch': True}, {'epoch': 1}, {'version': True}, {'reservation': None}):
            with self.subTest(change=change), self.assertRaises(Failure):
                call(self.endpoint, dict(request, **change))
        missing = dict(request)
        del missing['key']
        with self.assertRaises(Failure):
            call(self.endpoint, missing)
        for raw in (b'{"action":"dispatch"}', b'{"action":"status","action":"dispatch"}\n',
                    b'{"x":NaN}\n', b'X' * (MAX_WIRE + 1)):
            with socket.socket(socket.AF_UNIX) as conn:
                conn.settimeout(10)
                conn.connect(str(self.endpoint))
                self.assertEqual(peer_uid(conn), 321)
                try:
                    conn.sendall(raw)
                    conn.shutdown(socket.SHUT_WR)
                except BrokenPipeError:
                    pass
                response = receive(conn)
                self.assertEqual(response['error']['code'], 'InvalidInput')
        objects = self.runtime / 'evaluator/objects'
        target = objects / ('a' * 64)
        target.symlink_to(self.runtime / 'evaluator/expectation')
        with self.assertRaises(Failure):
            regular_artifact(objects, target.name)
        with self.assertRaises(Failure):
            regular_artifact(objects, '../expectation')
        target.unlink()
        text = b"__import__('os').system('id')"
        executable = objects / digest(text)
        executable.write_bytes(text)
        executable.chmod(0o700)
        with self.assertRaises(Failure):
            regular_artifact(objects, executable.name)
        executable.unlink()
        self.assertEqual(self.status()['launches'], before)

    def test_06_real_atomic_budget_ceilings_and_unknowns(self):
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(ActualIdentityBudget)
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        self.assertEqual(result.testsRun, 9)
        self.assertTrue(result.wasSuccessful())
        self.assertFalse(result.skipped)

    def test_07_reservation_not_lease_epoch_and_delayed_receipt(self):
        before = self.status()['launches']
        request = self.session.prepare()
        call(self.endpoint, {'action': 'stop', 'run': request['run']})
        with self.assertRaises(Failure) as stopped:
            call(self.endpoint, request)
        self.assertEqual(stopped.exception.record['code'], 'Stopped')
        with self.assertRaises(Failure):
            call(self.endpoint, dict(request, epoch=1))
        with self.assertRaises(Failure):
            self.session.budget.settle(EVALUATOR, request['reservation'],
                {'reservation': request['reservation'], 'receipt': '0' * 64})
        self.assertGreaterEqual(self.session.budget.totals(EVALUATOR)['pending'], 2)
        self.assertEqual(self.status()['launches'], before)

    def test_08_lost_response_no_repeated_effect(self):
        request = self.session.prepare()
        before = self.status()['launches']
        with socket.socket(socket.AF_UNIX) as conn:
            conn.settimeout(5)
            conn.connect(str(self.endpoint))
            self.assertEqual(peer_uid(conn), 321)
            conn.sendall(canonical(request) + b'\n')
            # Deliberately lose the response. Never resend to discover outcome.
        self.assertGreaterEqual(self.session.budget.totals(EVALUATOR)['pending'], 3)
        status = self.wait(request['run'], lambda value: value['result'] is not None)
        result = status['result']
        decision = self.session.accept(request, result)
        self.assertEqual(decision['baseline_correctness'], 'pass')
        # Once the trusted result exists, exact duplicate must return it, not launch.
        self.assertEqual(call(self.endpoint, request), result)
        with self.assertRaises(Failure):
            call(self.endpoint, dict(request, variant='forged-pass'))
        self.assertEqual(self.status()['launches'], before + 1)

    def test_09_watchdog_cessation_and_halt(self):
        request = self.session.prepare(probe='deadline')
        result = call(self.endpoint, request)
        self.assertTrue(result['ceased'])
        self.assertLess(result['seconds'], 10)
        with self.assertRaises(Failure):
            self.session.accept(request, result)
        self.assertTrue(self.status()['halted'])
        with self.assertRaises(Failure):
            call(self.endpoint, dict(request, run=uuid.uuid4().hex, key=uuid.uuid4().hex))

    def test_10_evaluator_store_exhaustion_before_effect(self):
        before = self.status()['launches']
        store = self.session.budget
        pages = store.db.execute('PRAGMA page_count').fetchone()[0]
        store.db.execute('PRAGMA max_page_count=' + str(pages))
        error = None
        for number in range(1000):
            try:
                store.reserve(EVALUATOR, 'full-' + str(number),
                    {'currency': 'USD', 'money_cents': 0, 'execution_us': 0, 'review_us': 0},
                    'full-' + str(number))
            except Failure as exc:
                error = exc
                break
        self.assertIsNotNone(error)
        self.assertEqual(error.record['code'], 'RecoveryRequired')
        self.assertIn('full', str(error.__cause__))
        with self.assertRaises(Failure):
            self.session.prepare()
        self.assertEqual(self.status()['launches'], before)


if __name__ == '__main__':
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(Mandatory)
    required = suite.countTestCases()
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    summary = {'required': required, 'executed': result.testsRun,
                      'skipped': len(result.skipped), 'failures': len(result.failures),
                      'errors': len(result.errors), 'mandatory_guest_gate': 'not-run' if result.testsRun == 0 else 'executed',
                      'verified': False, 'admission': 'blocked'}
    print(json.dumps(summary))
    if result.testsRun and hasattr(Mandatory, 'session'):
        session = Mandatory.session
        snapshot = session.ledger.snapshot({'kind': 'mandatory-suite', 'summary': summary}, uuid.uuid4().hex)
        (session.root / 'snapshot.json').write_bytes(canonical(snapshot))
        (session.root / 'summary.json').write_bytes(canonical(summary))
    raise SystemExit(0 if result.wasSuccessful() and result.testsRun == required and not result.skipped else 1)
