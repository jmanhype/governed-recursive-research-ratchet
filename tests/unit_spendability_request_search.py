"""Stage L per-request evidence-search tests."""

from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import json
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'research'))

from spendability_request_search import (  # noqa: E402
    RESERVATION_IDS,
    RUN_IDS,
    SESSION_LINE_11533_SHA256,
    SESSION_SOURCE_SHA256,
    STAGE_K_MATRIX_SHA256,
    STAGE_K_PACKAGE_SHA256,
    TARGET_FIELDS,
    build_request_search,
    validate_request_search,
)
from spendability_stage_c import StageCError  # noqa: E402


REQUEST_SEARCH = ROOT / 'docs/evidence/spendability/stage-l/REQUEST-SEARCH.json'


class SpendabilityRequestSearch(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = build_request_search(ROOT)

    def test_binds_exact_stage_k_and_original_archive_inputs(self):
        basis = self.record['basis']
        self.assertEqual(basis['stage_k_package_sha256'], STAGE_K_PACKAGE_SHA256)
        self.assertEqual(basis['stage_k_matrix_sha256'], STAGE_K_MATRIX_SHA256)
        self.assertEqual(basis['original_session_archive_sha256'],
                         SESSION_SOURCE_SHA256)

    def test_original_session_lines_are_hash_bound_without_raw_retention(self):
        session = self.record['original_session_search']
        records = session['matching_records']
        self.assertEqual([record['line_number'] for record in records],
                         [11533, 11534])
        self.assertEqual(records[0]['line_sha256'],
                         SESSION_LINE_11533_SHA256)
        self.assertEqual(session['search_method'],
                         'full-line exact-byte scan of every archive line')
        self.assertEqual(session['matching_line_numbers'], [11533, 11534])
        self.assertEqual(len(session['exact_match_counts']), 22)
        self.assertTrue(all(count > 0
                            for count in session['exact_match_counts'].values()))
        self.assertEqual(len(records[0]['matched_candidate_ids']), 22)
        self.assertEqual(len(records[1]['matched_candidate_ids']), 12)
        self.assertTrue(all(record['raw_line_retained'] is False
                            for record in records))
        self.assertTrue(all(record['exact_target_field_hits'] == []
                            for record in records))

    def test_full_archive_serialized_operation_hits_are_pending_unknowns(self):
        records = self.record['original_session_search']['matching_records']
        hits = [(hit['field'], hit['serialized_value'])
                for record in records
                for hit in record['serialized_target_field_hits']]
        self.assertEqual(hits, [
            ('operation', '\\"unknown\\"'),
            ('operation', '\\"unknown\\"'),
            ('operation', '\\"unknown\\"'),
        ])
        self.assertNotIn('operation_id', [field for field, _ in hits])

    def test_tool_readback_boundary_is_not_reservation_timing(self):
        boundary = self.record['original_session_search']['tool_record_boundary']
        self.assertEqual(boundary['started_at_ms'], 1792612839190)
        self.assertEqual(boundary['completed_at_ms'], 1792612854106)
        self.assertEqual(boundary['classification'],
                         'operator tool/readback boundary, not reservation timing')

    def test_exact_trusted_record_scope_is_complete(self):
        self.assertEqual(self.record['trusted_record_search'], {
            'records': 8,
            'request_events_scanned': 11,
            'observation_objects_scanned': 8,
            'meter_bodies_scanned': 8,
            'exact_target_fields_found': 0,
        })

    def test_all_eleven_request_events_are_independently_scanned(self):
        search = self.record['request_event_search']
        self.assertEqual(search['all_events_scanned'], 11)
        self.assertEqual(search['settled_events_scanned'], 8)
        self.assertEqual(search['pending_events_scanned'], 3)
        self.assertEqual(search['exact_target_fields_found'], 0)
        self.assertEqual(len(search['records']), 11)
        self.assertEqual(sum(record['settled_candidate']
                             for record in search['records']), 8)
        self.assertTrue(all(record['exact_target_field_hits'] == []
                            for record in search['records']))

    def test_all_eight_settled_candidates_are_covered_once(self):
        items = self.record['items']
        identifiers = [item['reservation_id'] for item in items]
        self.assertEqual(len(items), 8)
        self.assertEqual(set(identifiers), set(RESERVATION_IDS))
        self.assertEqual(len(identifiers), len(set(identifiers)))
        self.assertEqual({item['run_id'] for item in items}, set(RUN_IDS))

    def test_target_fields_are_absent_in_exact_retained_records(self):
        self.assertIn('created_at', TARGET_FIELDS)
        self.assertIn('artifact_creation_timestamp', TARGET_FIELDS)
        for item in self.record['items']:
            hits = item['exact_target_field_hits']
            self.assertEqual(hits, {
                'request_event': [],
                'observation_object': [],
                'meter_body': [],
            })
            for status in item['field_status'].values():
                self.assertEqual(status,
                                 'not-present-in-retained-original-records')

    def test_durations_are_retained_without_fabricating_intervals(self):
        for item in self.record['items']:
            self.assertIsInstance(item['duration_seconds'], float)
            self.assertIsNone(item['classification'])
            self.assertEqual(item['response_readiness'], 'not-ready')

    def test_search_boundary_does_not_claim_whole_archive_absence(self):
        boundary = self.record['search_boundary']
        self.assertTrue(boundary['full_original_session_archive_line_scan'])
        self.assertTrue(boundary['retained_trusted_request_event_bytes_scanned'])
        self.assertTrue(boundary['retained_observation_object_bytes_scanned'])
        self.assertTrue(boundary['retained_meter_body_bytes_scanned'])
        self.assertFalse(boundary['later_operator_analysis_sessions_treated_as_original_evidence'])
        self.assertFalse(boundary['whole_operator_archive_absence_established'])
        self.assertEqual(boundary['protected_paths_accessed'], [])

    def test_summary_reports_zero_missing_record_kinds(self):
        self.assertEqual(self.record['summary'], {
            'candidate_record_sets': 8,
            'authenticated_principal_records_found': 0,
            'issuer_records_found': 0,
            'operation_id_records_found': 0,
            'operation_boundary_records_found': 0,
            'generic_operation_fields_found': 3,
            'generic_operation_values': ['unknown', 'unknown', 'unknown'],
            'started_at_records_found': 0,
            'ended_at_records_found': 0,
            'clock_records_found': 0,
            'window_digest_records_found': 0,
            'duration_values': 8,
            'response_ready_record_sets': 0,
            'final_classifications_made': 0,
        })

    def test_record_remains_fail_closed_and_powerless(self):
        outcome = self.record['outcome']
        self.assertTrue(outcome['search_valid_for_declared_boundary'])
        self.assertFalse(outcome['whole_archive_absence_established'])
        self.assertFalse(outcome['response_ready'])
        self.assertFalse(outcome['classification_complete'])
        self.assertFalse(outcome['valid'])
        self.assertIsNone(outcome['spendable'])
        self.assertFalse(outcome['execution_authorized'])
        self.assertEqual(outcome['allowed_mutations'], [])
        self.assertFalse(any(self.record['authority'].values()))

    def test_saved_record_matches_exact_regeneration_and_hash(self):
        saved = REQUEST_SEARCH.read_bytes()
        self.assertEqual(json.loads(saved), self.record)
        self.assertEqual(sha256(saved).hexdigest(),
                         '5c13a5b140e8894894fa899e880ea83ec714d9984a030ee54eade57314fb29cf')

    def test_record_revalidates_by_exact_regeneration(self):
        result = validate_request_search(self.record, ROOT)
        self.assertTrue(result['record_valid'])
        self.assertTrue(result['search_valid_for_declared_boundary'])
        self.assertFalse(result['response_ready'])
        self.assertFalse(result['classification_complete'])
        self.assertIsNone(result['spendable'])

    def test_classification_and_authority_injection_are_rejected(self):
        classified = deepcopy(self.record)
        classified['items'][0]['classification'] = 'unavailable'
        with self.assertRaises(StageCError) as raised:
            validate_request_search(classified, ROOT)
        self.assertEqual(str(raised.exception),
                         'request_search: record differs from exact regeneration')
        authorized = deepcopy(self.record)
        authorized['authority']['reconcile'] = True
        with self.assertRaises(StageCError) as raised:
            validate_request_search(authorized, ROOT)
        self.assertEqual(str(raised.exception),
                         'request_search: record differs from exact regeneration')


if __name__ == '__main__':
    unittest.main()
