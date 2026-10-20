"""Mandatory real evaluator/runner/VM integration. Missing prerequisites fail, never skip."""
import json
import base64
import os
from pathlib import Path
import re
import sys
import threading
import time
import unittest
import uuid
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'research'))
from common import EVALUATOR, Failure, call, canonical, digest, require
from ledger import Ledger, verifySnapshot
from policy import loadPolicy

RUNTIME = Path(sys.argv[1]).resolve()


class OfflinePreflight(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        require(os.getuid() == EVALUATOR, 'Unauthorized', 'Integration must be evaluator identity')
        cls.root = RUNTIME / 'evaluator'
        cls.socket = RUNTIME / 'ipc/executor.sock'
        cls.policy_ref = digest((cls.root / 'policy.json').read_bytes())
        cls.policy = loadPolicy(EVALUATOR, cls.root / 'policy.json', cls.policy_ref)
        cls.ledger = Ledger(cls.root)
        require(cls.ledger.tip() == '0' * 64, 'RecoveryRequired', 'Never reuse preflight ledger')
        cls.reserved = 0

    def dispatch(self, probe: str | None = None) -> dict:
        run, reservation, key = (uuid.uuid4().hex for _ in range(3))
        self.__class__.reserved += 300
        self.assertLessEqual(self.reserved, 21600)
        self.ledger.snapshot({'kind': 'reserved', 'run': run, 'maximum_seconds': 300,
            'reserved_total_seconds': self.reserved, 'paid_dispatch': False, 'objects': []}, key)
        request = {'action': 'dispatch', 'request': {'run': run, 'variant': self.policy_ref, 'probe': probe},
                   'reservation': reservation, 'epoch': 0, 'key': key}
        holder = {}
        def invoke() -> None:
            try:
                holder['receipt'] = call(self.socket, request, timeout=310)
            except Exception as exc:
                holder['error'] = repr(exc)
        thread = threading.Thread(target=invoke)
        thread.start()
        if probe in ('stop', 'force'):
            deadline = time.monotonic() + 45
            while time.monotonic() < deadline and thread.is_alive():
                state = call(self.socket, {'action': 'status', 'run': run}, timeout=2)
                if state['ready']:
                    break
                time.sleep(0.05)
            self.assertTrue(state['ready'], 'Actual guest must be ready before stop')
            # A concurrent dispatch is a real IPC request, not a substituted callable.
            with self.assertRaises(Failure) as blocked:
                call(self.socket, dict(request, request=dict(request['request'], run=uuid.uuid4().hex), key=uuid.uuid4().hex))
            self.assertEqual(blocked.exception.record['code'], 'BudgetExceeded')
            started = time.monotonic()
            ack = call(self.socket, {'action': 'stop', 'run': run}, timeout=2)
            ack['roundtrip_seconds'] = time.monotonic() - started
            self.assertLessEqual(ack['roundtrip_seconds'], 2)
            self.assertTrue(ack['acknowledged'])
            (self.root / (probe + '-ack.json')).write_bytes(canonical(ack))
        thread.join(timeout=310)
        self.assertFalse(thread.is_alive(), 'Offline dispatch exceeded absolute bound')
        self.assertNotIn('error', holder)
        observed = holder['receipt']
        content = self.ledger.object(canonical(observed))
        snapshot = self.ledger.snapshot({'kind': 'offline-observation', 'run': run,
            'profile': self.policy_ref, 'objects': [content], 'probe': probe,
            'execution_seconds': observed['seconds'], 'reserved_total_seconds': self.reserved,
            'verified': False, 'admission': 'blocked'}, uuid.uuid4().hex)
        verifySnapshot(snapshot, snapshot['receipt']['digest'])
        label = probe or run
        (self.root / (label + '.json')).write_bytes(canonical(snapshot))
        self.assertTrue(observed['termination']['ceased'])
        self.assertTrue(observed['assets_unchanged'])
        self.assertLessEqual(observed['seconds'], 300)
        return observed

    def test_01_actual_permission_and_misconfiguration_controls(self) -> None:
        controls = json.loads((RUNTIME / 'controls.json').read_bytes())
        self.assertEqual(set(controls), {'network', 'share', 'identity', 'image', 'dependency', 'unauthorized-peer', 'protected-paths'})
        self.assertTrue(all(record['passed'] is True for record in controls.values()))
        for record in controls.values():
            self.assertIn('command', record)
            self.assertIn('returncode', record)

    def test_02_graceful_stop_and_acknowledgement(self) -> None:
        observed = self.dispatch('stop')
        self.assertEqual(observed['error']['code'], 'Stopped')
        self.assertFalse(observed['termination']['forced'])

    def test_03_forced_cancellation(self) -> None:
        observed = self.dispatch('force')
        self.assertEqual(observed['error']['code'], 'Stopped')
        self.assertTrue(observed['termination']['forced'])
        self.assertGreaterEqual(observed['termination']['seconds'], 5)
        self.assertLess(observed['termination']['seconds'], 7)

    def test_04_watchdog_deadline(self) -> None:
        observed = self.dispatch('watchdog')
        self.assertEqual(observed['error']['message'], 'Offline evaluator deadline exceeded')
        self.assertGreaterEqual(observed['seconds'], 240)

    def test_05_output_resource_cap(self) -> None:
        observed = self.dispatch('output')
        self.assertEqual(observed['error']['message'], 'Offline output cap exceeded')
        self.assertEqual(len(base64.b64decode(observed['raw_base64'], validate=True)), 1048576)

    def test_06_independent_builds_clean_baseline_and_isolation(self) -> None:
        builds, total = [], 0.0
        for number in range(2):
            observed = self.dispatch()
            (self.root / ('build-' + str(number + 1) + '.json')).write_bytes(canonical(observed))
            total += observed['seconds']
            self.assertIsNone(observed['error'])
            self.assertEqual(observed['exit_code'], 0)
            text = base64.b64decode(observed['observation_base64'], validate=True).decode()
            for marker in ('GRRR-ISOLATION-PASS', 'GRRR-DEPENDENCIES-END', 'GRRR-TESTS-PASS',
                           'GRRR-SYNTHETIC-IO-PASS', 'GRRR-BASELINE-PASS'):
                self.assertEqual(text.count(marker), 1)
            identities = re.findall(r'^GRRR-BUILD-SHA256 ([0-9a-f]{64})  /work/vlt$', text, re.MULTILINE)
            self.assertEqual(len(identities), 1)
            events = [json.loads(line) for line in text.splitlines() if line.startswith('{"Time":')]
            self.assertTrue(events)
            self.assertTrue(any(row.get('Action') == 'pass' and row.get('Test') for row in events))
            self.assertFalse(any(row.get('Action') in ('skip', 'fail') for row in events))
            builds.append({'sha256': identities[0], 'run': observed['run'], 'seconds': observed['seconds'],
                           'command_seconds': observed['command_seconds']})
        self.assertLessEqual(total, 600)
        self.assertNotEqual(builds[0]['run'], builds[1]['run'])
        self.assertEqual(builds[0]['sha256'], builds[1]['sha256'], 'Unexplained independent build difference')
        (self.root / 'baseline-receipt.json').write_bytes(canonical({'builds': builds, 'total_seconds': total,
            'profile_sha256': self.policy_ref, 'baseline_verified': True, 'admission': 'blocked',
            'measured_invocation_max_seconds': max(row['seconds'] for row in builds),
            'measured_command_max_seconds': max(row['command_seconds'] for row in builds),
            'command_limit_seconds': 240, 'hard_ceiling_seconds': 300}))


if __name__ == '__main__':
    result = unittest.TextTestRunner(verbosity=2, failfast=True).run(unittest.defaultTestLoader.loadTestsFromTestCase(OfflinePreflight))
    counts = {'required': 6, 'executed': result.testsRun, 'skipped': len(result.skipped),
              'failures': len(result.failures), 'errors': len(result.errors)}
    print(json.dumps(counts, sort_keys=True))
    raise SystemExit(0 if result.wasSuccessful() and counts['executed'] == 6 and not counts['skipped'] else 1)
