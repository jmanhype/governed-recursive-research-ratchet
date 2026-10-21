import copy
import json
import os
from pathlib import Path
import sqlite3
import tempfile
import unittest
import sys
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'research'))
import ledger
from common import GATES, Failure, canonical, digest
from ledger import (Ledger, DURABLE_FORMAT, experiment_event, export_snapshot,
                    recovery_state, validate_durable_event, verifySnapshot, verify_export)


class DurableEvidence(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix='.tmp-durable-')
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name).absolute() / 'ledger'
        self.identity = patch.object(ledger, 'EVALUATOR', os.getuid())
        self.identity.start()
        self.addCleanup(self.identity.stop)
        self.ledger = Ledger(self.root)
        self.addCleanup(self.ledger.close)
        self.zero = '0' * 64
        self.event = self.event_for('run-1')

    def event_for(self, run, recovery='none', objects=None):
        return experiment_event(
            run=run, experiment='experiment-1', arm='deterministic',
            started_ns=1, completed_ns=2, base_commit=self.zero, candidate_commit='a' * 64,
            evaluator='b' * 64, vm='c' * 64, toolchain='d' * 64, policy='e' * 64,
            specification='f' * 64, corpus='1' * 64, input='2' * 64,
            selector_version='selector-v1', selector_seed='seed=1',
            gates={gate: 'not-run' for gate in GATES}, gate_evidence=self.zero,
            measurements=[{'name': 'bytes-out', 'value': 3, 'unit': 'bytes'}],
            usage={'currency': 'USD', 'money_cents': 0, 'execution_us': 1, 'review_us': 0},
            reservations=[{'id': '3' * 64, 'maximum': {
                'currency': 'USD', 'money_cents': 0, 'execution_us': 2, 'review_us': 0}}],
            finding={'state': 'not-run', 'object': self.zero},
            review_target={'kind': 'review', 'id': '4' * 64},
            action_target={'kind': 'admission', 'id': '5' * 64},
            objects=objects or [], recovery_outcome=recovery)

    def test_full_event_schema_keeps_unknown_and_not_run_explicit(self):
        validate_durable_event(dict(self.event, idempotency_key='key-1', version=1))
        missing_gate = {gate: 'not-run' for gate in GATES}
        del missing_gate[GATES[0]]
        with self.assertRaises(Failure):
            validate_durable_event(dict(self.event, gates=missing_gate))
        for change in ({'actor': 'runner'}, {'started_ns': 3},
                       {'gates': {gate: {'state': 'unknown', 'evidence': self.zero} for gate in GATES}},
                       {'finding': {'state': 'not-run', 'object': 'short'}}):
            with self.assertRaises(Failure):
                validate_durable_event(dict(self.event, **change))

    def test_idempotency_compare_and_append(self):
        principal = os.getuid()
        first = self.ledger.append(principal, self.event, self.zero, 'key-1')
        duplicate = self.ledger.append(principal, self.event, self.zero, 'key-1')
        self.assertEqual(first, duplicate)
        changed = dict(self.event, completed_ns=3)
        with self.assertRaises(Failure):
            self.ledger.append(principal, changed, self.zero, 'key-1')
        changed_key = dict(self.event, run='run-2')
        with self.assertRaises(Failure):
            self.ledger.append(principal, changed_key, self.zero, 'key-1')
        self.assertEqual(self.ledger.tip(), first['digest'])

    def test_historical_updates_and_deletes_are_denied(self):
        receipt = self.ledger.append(os.getuid(), self.event, self.zero, 'key-1')
        for statement in ('UPDATE events SET body=? WHERE seq=1',
                          'DELETE FROM events WHERE seq=1'):
            with self.assertRaises(sqlite3.DatabaseError):
                self.ledger.db.execute(statement, (b'changed',))
        self.assertEqual(self.ledger.tip(), receipt['digest'])

    def test_object_precedes_reference_and_interrupted_transaction_rolls_back(self):
        content = b'forensic object'
        object_hash = self.ledger.object(content)
        referenced = list(self.event['objects']) + [object_hash]
        event = self.event_for('run-1', objects=referenced)
        self.ledger.db.execute("CREATE TRIGGER fault BEFORE INSERT ON idempotency BEGIN SELECT RAISE(ABORT,'interrupted'); END")
        with self.assertRaises(Failure):
            self.ledger.append(os.getuid(), event, self.zero, 'key-1')
        self.assertEqual(self.ledger.tip(), self.zero)
        self.assertEqual(self.ledger.db.execute('SELECT count(*) FROM idempotency').fetchone()[0], 0)
        self.assertEqual((self.root / 'objects' / object_hash).read_bytes(), content)

    def test_snapshot_detects_tampering_truncation_missing_object_and_bad_anchor(self):
        object_hash = self.ledger.object(b'object-data')
        event = self.event_for('run-1', objects=[object_hash])
        receipt = self.ledger.append(os.getuid(), event, self.zero, 'key-1')
        snapshot = self.ledger.snapshot(self.event_for('run-2', recovery='recovery-required'), 'key-2')
        anchor = snapshot['receipt']['digest']
        verifySnapshot(snapshot, anchor)
        recovered = recovery_state(snapshot)
        self.assertEqual(recovered['status'], 'RecoveryRequired')
        self.assertEqual(recovered['reservation_ids'], ['3' * 64])
        self.assertFalse(recovered['retry_authorized'])
        self.assertFalse(recovered['promotion_authorized'])
        truncated = copy.deepcopy(snapshot)
        truncated['events'] = truncated['events'][:1]
        with self.assertRaises(Failure):
            verifySnapshot(truncated, anchor)
        altered = copy.deepcopy(snapshot)
        altered['objects'][object_hash] = b'changed'.hex()
        with self.assertRaises(Failure):
            verifySnapshot(altered, anchor)
        missing = copy.deepcopy(snapshot)
        del missing['objects'][object_hash]
        with self.assertRaises(Failure):
            verifySnapshot(missing, anchor)
        with self.assertRaises(Failure):
            verifySnapshot(copy.deepcopy(snapshot), self.zero)

    def test_export_and_independent_verifier(self):
        object_hash = self.ledger.object(b'export-object')
        event = self.event_for('run-1', objects=[object_hash])
        snapshot = self.ledger.snapshot(event, 'key-2')
        anchor = snapshot['receipt']['digest']
        export = Path(self.directory.name).absolute() / 'export'
        manifest = export_snapshot(snapshot, export)
        self.assertEqual(manifest['trusted_anchor'], anchor)
        result = verify_export(export, anchor)
        self.assertTrue(result['verified'])
        with self.assertRaises(Failure):
            verify_export(export, self.zero)
        target = export / 'objects' / object_hash
        target.chmod(0o600)
        target.write_bytes(b'changed')
        with self.assertRaises(Failure):
            verify_export(export, anchor)

    def test_storage_exhaustion_returns_recovery_required(self):
        pages = self.ledger.db.execute('PRAGMA page_count').fetchone()[0]
        self.ledger.db.execute('PRAGMA max_page_count=' + str(pages))
        error = None
        for number in range(1000):
            try:
                event = self.event_for('full-' + str(number))
                self.ledger.append(os.getuid(), event, self.ledger.tip(), 'full-' + str(number))
            except Failure as exc:
                error = exc
                break
        self.assertIsNotNone(error)
        self.assertEqual(error.record['code'], 'RecoveryRequired')
        self.assertFalse(self.ledger.db.in_transaction)


if __name__ == '__main__':
    unittest.main()
