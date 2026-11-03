"""Stage H candidate response-readiness tests."""

from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'research'))

from spendability_response import (  # noqa: E402
    STAGE_G_CANDIDATE_INDEX_SHA256,
    STAGE_G_PACKAGE_SHA256,
    _validate_stage_g_package,
    build_response_readiness,
    validate_response_readiness,
)
from spendability_stage_c import StageCError  # noqa: E402


REQUEST = ROOT / 'docs/evidence/spendability/stage-f/REQUEST.json'
STAGE_G_PACKAGE = ROOT / 'docs/evidence/spendability/stage-g/PACKAGE.json'
STAGE_G_INDEX = ROOT / 'docs/evidence/spendability/stage-g/CANDIDATE-INDEX.json'


class SpendabilityResponseReadiness(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.request_raw = REQUEST.read_bytes()
        cls.stage_g_package_raw = STAGE_G_PACKAGE.read_bytes()
        cls.stage_g_index_raw = STAGE_G_INDEX.read_bytes()
        cls.record = build_response_readiness(ROOT)

    def test_binds_exact_approved_stage_f_and_stage_g_inputs(self):
        basis = self.record['basis']
        self.assertEqual(sha256(self.request_raw).hexdigest(),
                         basis['stage_f_request_sha256'])
        self.assertEqual(sha256(self.stage_g_package_raw).hexdigest(),
                         basis['stage_g_package_sha256'])
        self.assertEqual(sha256(self.stage_g_index_raw).hexdigest(),
                         basis['stage_g_candidate_index_sha256'])
        self.assertEqual(basis['stage_g_package_sha256'], STAGE_G_PACKAGE_SHA256)
        self.assertEqual(basis['stage_g_candidate_index_sha256'],
                         STAGE_G_CANDIDATE_INDEX_SHA256)
        self.assertEqual(basis['stage_g_independent_review'],
                         'STAGE_G_SEARCH_NARROW_REWORK_REVIEW: APPROVED')

    def test_all_thirty_stage_f_items_are_represented_once(self):
        identifiers = [item['request_item_id'] for item in self.record['items']]
        self.assertEqual(len(identifiers), 30)
        self.assertEqual(len(identifiers), len(set(identifiers)))
        self.assertEqual(self.record['summary'], {
            'total_items': 30,
            'candidate_record_sets': 8,
            'candidate_record_sets_response_ready': 0,
            'not_ready_items': 22,
            'final_classifications_made': 0,
        })

    def test_eight_candidates_are_not_response_ready(self):
        candidates = [item for item in self.record['items']
                      if item['response_readiness']
                      == 'candidate-record-set-not-response-ready']
        self.assertEqual(len(candidates), 8)
        for item in candidates:
            self.assertIsNone(item['classification'])
            self.assertTrue(item['blocking_gaps'])
            self.assertTrue(item['independent_review_required'])

    def test_settled_candidates_disclose_mandatory_identity_and_timing_gaps(self):
        candidates = [item for item in self.record['items']
                      if item['response_readiness']
                      == 'candidate-record-set-not-response-ready']
        joined_gaps = '\n'.join(candidates[0]['blocking_gaps'])
        self.assertIn('authenticated principal and issuer identity', joined_gaps)
        self.assertIn('approved request authorization and idempotency key', joined_gaps)
        self.assertIn('UTC measurement start/end, clock, and window digest', joined_gaps)
        self.assertIn('source-system custodian and chain of custody', joined_gaps)

    def test_present_joins_do_not_hide_missing_response_contract_fields(self):
        item = next(item for item in self.record['items']
                    if item['response_readiness']
                    == 'candidate-record-set-not-response-ready')
        statuses = {row['required_evidence']: row['status'] for row in item['coverage']}
        self.assertEqual(statuses['original meter-body bytes and digest'], 'present')
        self.assertEqual(statuses['receipt-to-meter and actual-usage join proof'], 'present')
        self.assertEqual(statuses['authenticated principal and issuer identity'], 'missing')
        self.assertEqual(statuses['UTC measurement start/end, clock, and window digest'],
                         'missing')

    def test_pending_and_unestablished_items_remain_not_ready(self):
        not_ready = [item for item in self.record['items']
                     if item['response_readiness'] == 'not-ready']
        self.assertEqual(len(not_ready), 22)
        self.assertTrue(all(item['classification'] is None for item in not_ready))
        self.assertTrue(all(item['blocking_gaps'] for item in not_ready))
        self.assertEqual(sum(item['stage_g_search_status']
                             == 'search-completeness-not-established'
                             for item in not_ready), 15)

    def test_record_remains_fail_closed_and_powerless(self):
        self.assertFalse(self.record['outcome']['response_ready'])
        self.assertFalse(self.record['outcome']['classification_complete'])
        self.assertFalse(self.record['outcome']['valid'])
        self.assertIsNone(self.record['outcome']['spendable'])
        self.assertFalse(self.record['outcome']['execution_authorized'])
        self.assertEqual(self.record['outcome']['allowed_mutations'], [])
        self.assertFalse(any(self.record['authority'].values()))

    def test_record_revalidates_by_exact_regeneration(self):
        result = validate_response_readiness(self.record, ROOT)
        self.assertTrue(result['record_valid'])
        self.assertFalse(result['response_ready'])
        self.assertFalse(result['classification_complete'])
        self.assertIsNone(result['spendable'])

    def test_modified_stage_g_package_is_rejected(self):
        with self.assertRaises(StageCError) as raised:
            _validate_stage_g_package(b'changed', ROOT)
        self.assertEqual(str(raised.exception),
                         'response_readiness: Stage G package bytes differ')

    def test_classification_injection_is_rejected(self):
        value = deepcopy(self.record)
        value['items'][0]['classification'] = 'supplied'
        with self.assertRaises(StageCError) as raised:
            validate_response_readiness(value, ROOT)
        self.assertEqual(str(raised.exception),
                         'response_readiness: record differs from exact regeneration')

    def test_authority_injection_is_rejected(self):
        value = deepcopy(self.record)
        value['authority']['reconcile'] = True
        with self.assertRaises(StageCError) as raised:
            validate_response_readiness(value, ROOT)
        self.assertEqual(str(raised.exception),
                         'response_readiness: record differs from exact regeneration')


if __name__ == '__main__':
    unittest.main()
