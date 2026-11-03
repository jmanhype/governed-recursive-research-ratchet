"""Stage K per-record evidence-matrix tests."""

from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import json
import sys
import unittest
from pathlib import Path as _Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'research'))

import spendability_per_record as per_record_module  # noqa: E402
from spendability_per_record import (  # noqa: E402
    ACCOUNT_LOG_SHA256,
    RESERVATION_IDS,
    RUN_IDS,
    SESSION_READBACK_LINE_SHA256,
    SESSION_SEARCH_SHA256,
    SESSION_SOURCE_SHA256,
    STAGE_J_PACKAGE_SHA256,
    _validate_identity_evidence,
    _validate_session_search,
    build_per_record_matrix,
    validate_per_record_matrix,
)
from spendability_stage_c import StageCError  # noqa: E402


SESSION_SEARCH = ROOT / 'docs/evidence/spendability/stage-k/SESSION-SEARCH.json'
ACCOUNT_LOG = ROOT / 'docs/evidence/replay-prerequisites/runtime-smoke-r3/account-groups.log'
MATRIX = ROOT / 'docs/evidence/spendability/stage-k/PER-RECORD-MATRIX.json'


class SpendabilityPerRecordMatrix(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.session_raw = SESSION_SEARCH.read_bytes()
        cls.account_raw = ACCOUNT_LOG.read_bytes()
        cls.record = build_per_record_matrix(ROOT)

    def test_binds_exact_stage_j_and_session_inputs(self):
        basis = self.record['basis']
        self.assertEqual(basis['stage_j_package_sha256'], STAGE_J_PACKAGE_SHA256)
        self.assertEqual(sha256(self.session_raw).hexdigest(),
                         basis['session_search_sha256'])
        self.assertEqual(basis['session_search_sha256'], SESSION_SEARCH_SHA256)
        self.assertEqual(basis['session_source_sha256'], SESSION_SOURCE_SHA256)

    def test_session_search_uses_retained_publication_when_source_is_absent(self):
        with mock.patch.object(per_record_module, 'SESSION_SOURCE_PATH',
                               _Path('/nonexistent-grrr-source-archive')):
            search = _validate_session_search(ROOT)
        self.assertEqual(search['source']['sha256'], SESSION_SOURCE_SHA256)
        self.assertTrue(search['interpretation']['all_sixteen_candidate_ids_found'])
        self.assertTrue(search['interpretation']['line_11533_contains_all_sixteen_ids'])
        self.assertTrue(search['interpretation']
                        ['line_11533_does_not_provide_per_reservation_creation_timestamps'])
        self.assertTrue(search['interpretation']
                        ['line_11533_does_not_provide_per_reservation_dispatch_operation_ids'])

    def test_numeric_identity_mapping_is_validated_from_reviewed_evidence(self):
        identity = _validate_identity_evidence(ROOT)
        mapping = identity['account_mapping']
        self.assertEqual(mapping['evaluator'],
                         {'name': '_grrr_evaluator', 'uid': 320, 'gid': 320})
        self.assertEqual(mapping['runner'],
                         {'name': '_grrr_runner', 'uid': 321, 'gid': 321})
        self.assertEqual(sha256(self.account_raw).hexdigest(), ACCOUNT_LOG_SHA256)

    def test_issuer_ledger_identity_is_common_not_per_request_authentication(self):
        issuer = self.record['common_evidence']['issuer_ledger_identity']
        self.assertEqual(issuer['status'], 'validated-common')
        self.assertEqual(issuer['principal_uid'], 320)
        self.assertEqual(issuer['database_owner_uid'], 320)
        self.assertEqual(issuer['per_request_authenticated_principal'], 'missing')

    def test_all_eight_reservations_and_runs_are_covered(self):
        items = self.record['items']
        self.assertEqual(len(items), 8)
        self.assertEqual({item['reservation_id'] for item in items},
                         set(RESERVATION_IDS))
        self.assertEqual({item['run_id'] for item in items}, set(RUN_IDS))
        identifiers = [item['request_item_id'] for item in items]
        self.assertEqual(len(identifiers), len(set(identifiers)))

    def test_each_record_preserves_request_event_object_and_meter_chain(self):
        for item in self.record['items']:
            operation = item['operation_boundary']
            custody = item['custody_chain']
            self.assertEqual(operation['request_event']['event_seq'],
                             custody['request_event']['event_seq'])
            self.assertEqual(operation['request_event']['event_sha256'],
                             custody['request_event']['event_sha256'])
            self.assertIn('sha256', custody['observation'])
            self.assertTrue(custody['meter_receipt_sha256'])

    def test_durations_are_retained_without_fabricating_intervals(self):
        for item in self.record['items']:
            self.assertIsInstance(item['timing']['duration_seconds'], float)
            self.assertEqual(item['timing']['status'], 'partial')
            self.assertEqual(item['timing']['missing'], [
                'reservation-specific UTC start',
                'reservation-specific UTC end',
                'measurement clock identity',
                'measurement window digest',
            ])

    def test_common_readback_boundary_is_bound_to_hashed_source_line(self):
        readback = self.record['session_readback']
        self.assertEqual(readback['line_sha256'], SESSION_READBACK_LINE_SHA256)
        self.assertEqual(readback['started_at'], '2026-10-21T20:00:39.190Z')
        self.assertEqual(readback['completed_at'], '2026-10-21T20:00:54.106Z')
        self.assertTrue(readback['all_sixteen_candidate_ids_present'])

    def test_missing_principal_operation_and_interval_counts_are_explicit(self):
        self.assertEqual(self.record['summary'], {
            'candidate_record_sets': 8,
            'numeric_process_uid_mapping_validated': True,
            'issuer_ledger_identity_validated': True,
            'per_request_authenticated_principal_records': 0,
            'explicit_dispatch_operation_ids': 0,
            'reservation_specific_utc_intervals': 0,
            'duration_values': 8,
            'common_readback_boundaries': 1,
            'custody_chains': 8,
            'response_ready_record_sets': 0,
            'final_classifications_made': 0,
        })

    def test_record_remains_fail_closed_and_powerless(self):
        self.assertFalse(self.record['outcome']['response_ready'])
        self.assertFalse(self.record['outcome']['classification_complete'])
        self.assertFalse(self.record['outcome']['valid'])
        self.assertIsNone(self.record['outcome']['spendable'])
        self.assertFalse(self.record['outcome']['execution_authorized'])
        self.assertEqual(self.record['outcome']['allowed_mutations'], [])
        self.assertFalse(any(self.record['authority'].values()))

    def test_record_revalidates_by_exact_regeneration(self):
        result = validate_per_record_matrix(self.record, ROOT)
        self.assertTrue(result['record_valid'])
        self.assertFalse(result['response_ready'])
        self.assertFalse(result['classification_complete'])
        self.assertIsNone(result['spendable'])

    def test_saved_matrix_matches_exact_regeneration(self):
        saved = json.loads(MATRIX.read_bytes())
        self.assertEqual(saved, self.record)
        self.assertEqual(sha256(MATRIX.read_bytes()).hexdigest(),
                         'd71139015cd3b27683503984947ba692800e407aecd6f45d1ccf6e3c18ecd4d1')

    def test_session_search_and_source_hashes_are_pinned(self):
        _validate_session_search(ROOT)
        self.assertEqual(sha256(self.session_raw).hexdigest(), SESSION_SEARCH_SHA256)
        self.assertNotEqual(sha256(self.session_raw + b' ').hexdigest(),
                            SESSION_SEARCH_SHA256)

    def test_classification_and_authority_injection_are_rejected(self):
        classified = deepcopy(self.record)
        classified['items'][0]['classification'] = 'supplied'
        with self.assertRaises(StageCError) as raised:
            validate_per_record_matrix(classified, ROOT)
        self.assertEqual(str(raised.exception),
                         'per_record: record differs from exact regeneration')
        authorized = deepcopy(self.record)
        authorized['authority']['reconcile'] = True
        with self.assertRaises(StageCError) as raised:
            validate_per_record_matrix(authorized, ROOT)
        self.assertEqual(str(raised.exception),
                         'per_record: record differs from exact regeneration')


if __name__ == '__main__':
    unittest.main()
