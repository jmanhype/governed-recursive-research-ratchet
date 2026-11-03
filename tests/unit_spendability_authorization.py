"""Stage J retained-authorization evidence tests."""

from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'research'))

from spendability_authorization import (  # noqa: E402
    APPROVAL_SHA256,
    CAPTURE_SHA256,
    REVIEW_SHA256,
    STAGE_I_PACKAGE_SHA256,
    STAGE_I_PROVENANCE_SHA256,
    _no_credentials,
    _validate_capture,
    build_authorization_validation,
    validate_authorization_record,
)
from spendability_stage_c import StageCError  # noqa: E402


CAPTURE = ROOT / 'docs/evidence/spendability/stage-j/CAPTURE.json'
APPROVAL = ROOT / 'docs/evidence/spendability/stage-j/artifacts/execution-approval-9d3df87-fix1.json'
REVIEW = ROOT / 'docs/evidence/spendability/stage-j/artifacts/license-review-9d3df87-fix1.json'
VALIDATION = ROOT / 'docs/evidence/spendability/stage-j/VALIDATION.json'


class SpendabilityAuthorizationEvidence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.capture_raw = CAPTURE.read_bytes()
        cls.approval_raw = APPROVAL.read_bytes()
        cls.review_raw = REVIEW.read_bytes()
        cls.record = build_authorization_validation(ROOT)

    def test_binds_exact_stage_i_and_stage_j_inputs(self):
        basis = self.record['basis']
        self.assertEqual(sha256(self.capture_raw).hexdigest(), basis['stage_j_capture_sha256'])
        self.assertEqual(basis['stage_j_capture_sha256'], CAPTURE_SHA256)
        self.assertEqual(sha256(self.approval_raw).hexdigest(), basis['execution_approval_sha256'])
        self.assertEqual(basis['execution_approval_sha256'], APPROVAL_SHA256)
        self.assertEqual(sha256(self.review_raw).hexdigest(), basis['license_review_sha256'])
        self.assertEqual(basis['license_review_sha256'], REVIEW_SHA256)
        self.assertEqual(basis['stage_i_package_sha256'], STAGE_I_PACKAGE_SHA256)
        self.assertEqual(basis['stage_i_provenance_sha256'], STAGE_I_PROVENANCE_SHA256)

    def test_capture_records_exact_read_only_protected_sources(self):
        capture = _validate_capture(self.capture_raw)
        sources = capture['protected_sources']
        self.assertEqual(set(sources), {'execution_approval', 'license_review'})
        for source in sources.values():
            self.assertTrue(source['regular'])
            self.assertFalse(source['symlink'])
            self.assertEqual((source['uid'], source['gid'], source['mode'], source['nlink']),
                             (0, 0, '0o444', 1))
        self.assertEqual(capture['scope']['protected_paths_mutated'], [])
        self.assertEqual(len(capture['scope']['protected_paths_read']), 2)
        self.assertTrue(capture['validation']['pinned_source_validator'] == 'PASS')
        self.assertTrue(capture['validation']['validate_config'] == 'PASS')
        self.assertTrue(capture['validation']['validate_approval'] == 'PASS')

    def test_retained_authorization_records_contain_no_credentials(self):
        _no_credentials(self.approval_raw, 'approval')
        _no_credentials(self.review_raw, 'review')
        lowered = (self.approval_raw + self.review_raw).lower()
        for marker in (b'password', b'token', b'api_key', b'secret', b'credential', b'bearer'):
            self.assertNotIn(marker, lowered)

    def test_common_approval_binding_is_valid_against_plan(self):
        self.assertTrue(self.record['outcome']['authorization_common_binding_valid'])
        self.assertTrue(self.record['summary']['common_authorization_binding_valid'])
        self.assertIn('execution_approval', self.record['artifacts'])
        self.assertIn('license_review', self.record['artifacts'])

    def test_all_eight_candidates_receive_common_binding_only(self):
        items = self.record['items']
        identifiers = [item['request_item_id'] for item in items]
        self.assertEqual(len(items), 8)
        self.assertEqual(len(identifiers), len(set(identifiers)))
        for item in items:
            self.assertEqual(item['common_authorization_binding'], 'validated')
            self.assertEqual(item['response_readiness'], 'not-ready')
            self.assertIsNone(item['classification'])

    def test_per_request_gaps_remain_explicit(self):
        expected = {
            'per-request authenticated principal and issuer binding',
            'numeric process UID mapping',
            'reservation-specific dispatch operation identity and boundary',
            'reservation-specific UTC measurement start/end, clock, and window digest',
            'reservation-specific custody classification',
            'independent final classifier decision',
        }
        for item in self.record['items']:
            self.assertEqual(set(item['remaining_gaps']), expected)

    def test_record_remains_fail_closed_and_powerless(self):
        self.assertFalse(self.record['outcome']['response_ready'])
        self.assertFalse(self.record['outcome']['classification_complete'])
        self.assertFalse(self.record['outcome']['valid'])
        self.assertIsNone(self.record['outcome']['spendable'])
        self.assertFalse(self.record['outcome']['execution_authorized'])
        self.assertEqual(self.record['outcome']['allowed_mutations'], [])
        self.assertFalse(any(self.record['authority'].values()))

    def test_record_revalidates_by_exact_regeneration(self):
        result = validate_authorization_record(self.record, ROOT)
        self.assertTrue(result['record_valid'])
        self.assertTrue(result['authorization_common_binding_valid'])
        self.assertFalse(result['response_ready'])
        self.assertFalse(result['classification_complete'])
        self.assertIsNone(result['spendable'])

    def test_modified_capture_is_rejected(self):
        with self.assertRaises(StageCError) as raised:
            _validate_capture(b'changed')
        self.assertEqual(str(raised.exception),
                         'authorization_evidence: Stage J capture bytes differ')

    def test_classification_injection_is_rejected(self):
        value = deepcopy(self.record)
        value['items'][0]['classification'] = 'supplied'
        with self.assertRaises(StageCError) as raised:
            validate_authorization_record(value, ROOT)
        self.assertEqual(str(raised.exception),
                         'authorization_evidence: record differs from exact regeneration')

    def test_authority_injection_is_rejected(self):
        value = deepcopy(self.record)
        value['authority']['reconcile'] = True
        with self.assertRaises(StageCError) as raised:
            validate_authorization_record(value, ROOT)
        self.assertEqual(str(raised.exception),
                         'authorization_evidence: record differs from exact regeneration')

    def test_response_ready_injection_is_rejected(self):
        value = deepcopy(self.record)
        value['outcome']['response_ready'] = True
        with self.assertRaises(StageCError) as raised:
            validate_authorization_record(value, ROOT)
        self.assertEqual(str(raised.exception),
                         'authorization_evidence: record differs from exact regeneration')


if __name__ == '__main__':
    unittest.main()
