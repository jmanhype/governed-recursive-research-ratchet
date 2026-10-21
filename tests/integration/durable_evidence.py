"""Real UID-320 durable evidence controls; no identity substitution or skips."""
import copy
import json
import os
from pathlib import Path
import sqlite3
import sys
import unittest
import uuid

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import EVALUATOR, GATES, Failure, digest
from ledger import (Ledger, experiment_event, export_snapshot, recovery_state,
                    verifySnapshot, verify_export)


class Mandatory(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        require_identity = os.getuid() == EVALUATOR and len(sys.argv) == 3
        if not require_identity:
            raise SystemExit('AWAITING_PARENT_IDENTITY_RUN: actual evaluator UID 320 and runtime/export arguments required')
        cls.runtime = Path(sys.argv[1]).absolute()
        cls.export = Path(sys.argv[2]).absolute()
        if not (cls.runtime.parent == Path('/private/tmp') and cls.runtime.name.startswith('grrr-durable-')):
            raise SystemExit('Untrusted durable runtime')
        if not (cls.export.parent.parent == Path('/Users/Shared/GRRR/durable-evidence')
                and cls.export.parent.name.startswith('durable-') and cls.export.name == 'export'):
            raise SystemExit('Export must be outside disposable runtime')
        cls.root = cls.runtime / 'evaluator'
        cls.ledger = Ledger(cls.root)
        cls.zero = '0' * 64
        cls.anchor = None

    @classmethod
    def event_for(cls, run, recovery='none', objects=None, reservations=None):
        return experiment_event(
            run=run, experiment='GRRR-my5n', arm='deterministic', started_ns=1, completed_ns=2,
            base_commit=cls.zero, candidate_commit='a' * 64, evaluator='b' * 64,
            vm='c' * 64, toolchain='d' * 64, policy='e' * 64, specification='f' * 64,
            corpus='1' * 64, input='2' * 64, selector_version='selector-v1', selector_seed='fixed-seed',
            gates={gate: 'not-run' for gate in GATES}, gate_evidence=cls.zero,
            measurements=[{'name': 'event-bytes', 'value': 1, 'unit': 'bytes'}],
            usage={'currency': 'USD', 'money_cents': 0, 'execution_us': 1, 'review_us': 0},
            reservations=reservations or [{'id': '3' * 64, 'maximum': {
                'currency': 'USD', 'money_cents': 0, 'execution_us': 2, 'review_us': 0}}],
            finding={'state': 'not-run', 'object': cls.zero},
            review_target={'kind': 'review', 'id': '4' * 64},
            action_target={'kind': 'admission', 'id': '5' * 64},
            objects=objects or [], recovery_outcome=recovery)

    def test_01_evaluator_history_compare_append_and_immutability(self):
        event = self.event_for('run-1')
        first = self.ledger.append(EVALUATOR, event, self.zero, 'key-1')
        self.assertEqual(self.ledger.append(EVALUATOR, event, self.zero, 'key-1'), first)
        with self.assertRaises(Failure):
            self.ledger.append(EVALUATOR, self.event_for('run-2'), self.zero, 'key-1')
        with self.assertRaises(Failure):
            self.ledger.append(321, event, self.zero, 'key-api')
        for statement in ('UPDATE events SET body=? WHERE seq=1', 'DELETE FROM events WHERE seq=1'):
            with self.assertRaises(sqlite3.DatabaseError):
                self.ledger.db.execute(statement, (b'changed',))
        self.assertEqual(self.ledger.tip(), first['digest'])

    def test_02_interrupted_object_recovery_and_no_retry(self):
        content = b'interrupted forensic object'
        object_hash = self.ledger.object(content)
        original = self.event_for('run-interrupted', recovery='interrupted', objects=[object_hash])
        self.ledger.db.execute("CREATE TRIGGER interrupt BEFORE INSERT ON idempotency BEGIN SELECT RAISE(ABORT,'interrupted'); END")
        with self.assertRaises(Failure):
            self.ledger.append(EVALUATOR, original, self.ledger.tip(), 'interrupted-key')
        self.assertEqual((self.root / 'objects' / object_hash).read_bytes(), content)
        referenced_events = self.ledger.db.execute('SELECT count(*) FROM events WHERE body LIKE ?',
                                                   ('%' + object_hash + '%',)).fetchone()[0]
        self.assertEqual(referenced_events, 0)
        self.ledger.db.execute('DROP TRIGGER interrupt')
        self.ledger.append(EVALUATOR, original, self.ledger.tip(), 'interrupted-key')
        recovery = self.event_for('run-recovery', recovery='recovery-required', objects=[object_hash])
        self.ledger.append(EVALUATOR, recovery, self.ledger.tip(), 'recovery-key')
        snapshot = self.ledger.snapshot(self.event_for('run-recovery-snapshot'), 'recovery-snapshot-key')
        state = recovery_state(snapshot)
        self.assertEqual(state['status'], 'RecoveryRequired')
        self.assertEqual(state['reservation_ids'], ['3' * 64, '3' * 64])
        self.assertFalse(state['retry_authorized'])
        self.assertFalse(state['promotion_authorized'])

    def test_03_export_and_independent_trusted_anchor_verification(self):
        snapshot = self.ledger.snapshot(self.event_for('run-export'), 'export-key')
        self.anchor = snapshot['receipt']['digest']
        verifySnapshot(snapshot, self.anchor)
        manifest = export_snapshot(snapshot, self.export)
        self.assertEqual(manifest['trusted_anchor'], self.anchor)
        result = verify_export(self.export, self.anchor)
        self.assertTrue(result['verified'])
        with self.assertRaises(Failure):
            verify_export(self.export, self.zero)
        altered = copy.deepcopy(snapshot)
        altered['events'][0]['event']['actor'] = 'runner'
        with self.assertRaises(Failure):
            verifySnapshot(altered, self.anchor)
        truncated = copy.deepcopy(snapshot)
        truncated['events'] = truncated['events'][:1]
        with self.assertRaises(Failure):
            verifySnapshot(truncated, self.anchor)
        missing = copy.deepcopy(snapshot)
        missing['objects'].pop(next(iter(missing['objects'])))
        with self.assertRaises(Failure):
            verifySnapshot(missing, self.anchor)
        (self.root / 'summary.json').write_bytes(json.dumps({
            'required': 4, 'executed': 4, 'skipped': 0, 'failures': 0, 'errors': 0,
            'snapshot_id': snapshot['snapshot_id'], 'anchor': self.anchor,
            'verified': True, 'admission': 'blocked'}, sort_keys=True).encode('ascii'))

    def test_04_actual_store_exhaustion_retains_failure(self):
        fixture = self.root / 'exhaustion'
        store = Ledger(fixture)
        try:
            pages = store.db.execute('PRAGMA page_count').fetchone()[0]
            store.db.execute('PRAGMA max_page_count=' + str(pages))
            failure = None
            for number in range(1000):
                try:
                    store.append(EVALUATOR, self.event_for('full-' + str(number)),
                                 store.tip(), 'full-' + str(number))
                except Failure as exc:
                    failure = exc
                    break
            self.assertIsNotNone(failure)
            self.assertEqual(failure.record['code'], 'RecoveryRequired')
            self.assertFalse(store.db.in_transaction)
        finally:
            store.close()


if __name__ == '__main__':
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(Mandatory)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    summary = {'required': suite.countTestCases(), 'executed': result.testsRun,
               'skipped': len(result.skipped), 'failures': len(result.failures),
               'errors': len(result.errors), 'admission': 'blocked'}
    if Mandatory.root.exists():
        (Mandatory.root / 'integration-summary.json').write_bytes(json.dumps(summary).encode('ascii'))
    raise SystemExit(0 if result.wasSuccessful() and result.testsRun == suite.countTestCases()
                     and not result.skipped else 1)
