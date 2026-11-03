"""Stage F external spendability evidence-request tests."""

from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'research'))

from spendability_request import (  # noqa: E402
    APPROVED_STAGE_E_BUNDLE_SHA256, APPROVED_STAGE_E_PACKAGE_SHA256,
    build_evidence_request, validate_evidence_request,
)
from spendability_stage_c import StageCError  # noqa: E402


STAGE_A = ROOT / 'docs/evidence/spendability/stage-a/BASELINE.json'
STAGE_D = ROOT / 'docs/evidence/spendability/stage-d/CAPTURE.json'
POSTCAPTURE = ROOT / 'docs/evidence/spendability/stage-d/POSTCAPTURE-VERIFY.json'
BUNDLE = ROOT / 'docs/evidence/spendability/stage-e/BUNDLE.json'
PACKAGE = ROOT / 'docs/evidence/spendability/stage-e/PACKAGE.json'
CREATED_AT = '2026-10-28T00:15:00Z'


class SpendabilityEvidenceRequest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stage_a_raw = STAGE_A.read_bytes()
        cls.stage_d_raw = STAGE_D.read_bytes()
        cls.post_raw = POSTCAPTURE.read_bytes()
        cls.bundle_raw = BUNDLE.read_bytes()
        cls.package_raw = PACKAGE.read_bytes()
        cls.request = build_evidence_request(
            cls.stage_a_raw, cls.stage_d_raw, cls.post_raw,
            cls.bundle_raw, cls.package_raw, created_at=CREATED_AT)

    def input_bytes(self):
        return (
            self.stage_a_raw, self.stage_d_raw, self.post_raw,
            self.bundle_raw, self.package_raw,
        )

    def test_request_binds_exact_approved_stage_e_artifacts(self):
        basis = self.request['basis']
        self.assertEqual(sha256(self.bundle_raw).hexdigest(), basis['stage_e_bundle_sha256'])
        self.assertEqual(sha256(self.package_raw).hexdigest(), basis['stage_e_package_sha256'])
        self.assertEqual(basis['stage_e_bundle_sha256'], APPROVED_STAGE_E_BUNDLE_SHA256)
        self.assertEqual(basis['stage_e_package_sha256'], APPROVED_STAGE_E_PACKAGE_SHA256)
        self.assertEqual(basis['stage_e_independent_review'],
                         'STAGE_E_NARROW_REWORK_REVIEW: APPROVED')

    def test_request_contains_exact_item_inventory(self):
        summary = self.request['request_summary']
        self.assertEqual(summary['provenance_items'], 11)
        self.assertEqual(summary['pending_items'], 3)
        self.assertEqual(summary['lineage_items'], 8)
        self.assertEqual(summary['coverage_items'], 2)
        self.assertEqual(summary['overhead_items'], 5)
        self.assertEqual(summary['global_history_items'], 1)
        self.assertEqual(summary['total_items'], 30)
        self.assertEqual(len(self.request['requested_evidence']), 30)
        identifiers = [item['id'] for item in self.request['requested_evidence']]
        self.assertEqual(len(identifiers), len(set(identifiers)))

    def test_provenance_requests_cover_all_eleven_reservations(self):
        items = [item for item in self.request['requested_evidence']
                 if item['kind'] == 'reservation-provenance']
        expected = {
            '1bf9d516461040c0baef70648c074d61',
            '5b7851814d764da1a3b3830abc9853ce',
            '69523b39a51c44739114313c9325028c',
            '7ecc4c7e17f742dc9ec2a8c6dada50f2',
            'b34d8b9d106e42eab3a3e43daac98ddd',
            'b954f6890a1e43e3b13f24298fa7ca33',
            'b95be730d6a5408886071d29848bbd05',
            'd375ce6a2d924646bec71df64e939a5b',
            'd3c965a29ab547c999e66bf0b60eca9f',
            'e38c33051ff64b4eab106e65a200fe06',
            'eb045d10d73b48ef9d570a1cf870f6eb',
        }
        self.assertEqual({item['subject'] for item in items}, expected)
        self.assertTrue(all(item['required_evidence'] for item in items))

    def test_pending_requests_cover_three_full_holds(self):
        items = [item for item in self.request['requested_evidence']
                 if item['kind'] == 'pending-disposition']
        self.assertEqual({item['subject'] for item in items}, {
            '69523b39a51c44739114313c9325028c',
            'b34d8b9d106e42eab3a3e43daac98ddd',
            'd375ce6a2d924646bec71df64e939a5b',
        })
        for item in items:
            joined = '\n'.join(item['required_evidence'])
            self.assertIn('dispatch outcome', joined)
            self.assertIn('stale-handle accounting', joined)

    def test_lineage_and_overhead_domains_are_complete(self):
        items = self.request['requested_evidence']
        lineage = {item['subject'] for item in items if item['kind'] == 'historical-lineage'}
        self.assertEqual(lineage, {
            'registration_prior_active', 'registration_receipt',
            'recovery_prior_active', 'recovery_intent',
            'recovery_receipt', 'recovery_complete',
            'active', 'database_snapshot',
        })
        overhead = {item['subject'] for item in items if item['kind'] == 'overhead-domain'}
        self.assertEqual(overhead, {
            'preparation', 'selection', 'execution', 'review', 'other',
        })

    def test_operation_side_store_and_global_history_are_explicit(self):
        kinds = {item['kind'] for item in self.request['requested_evidence']}
        self.assertIn('operation-history', kinds)
        self.assertIn('side-store-history', kinds)
        self.assertIn('global-historical-completeness', kinds)
        global_item = next(item for item in self.request['requested_evidence']
                           if item['kind'] == 'global-historical-completeness')
        self.assertIn('paid-service decisions, proofs, and receipts',
                      global_item['required_evidence'])

    def test_response_contract_requires_provenance_and_forbids_secrets(self):
        contract = self.request['response_contract']
        self.assertIn('chain of custody and redaction justification', contract['required'])
        self.assertIn('explicit search boundary for every unavailable claim', contract['required'])
        self.assertIn('credentials or API tokens', contract['prohibited'])
        self.assertIn('claimant-authored replacements', contract['prohibited'])
        self.assertIn('authority language granting reconciliation or replay', contract['prohibited'])

    def test_request_remains_fail_closed_and_powerless(self):
        self.assertEqual(self.request['status'], 'open')
        self.assertIsNone(self.request['request_summary']['spendability_after_response'])
        self.assertFalse(self.request['outcome']['valid'])
        self.assertIsNone(self.request['outcome']['spendable'])
        self.assertEqual(self.request['outcome']['allowed_mutations'], [])
        self.assertFalse(self.request['outcome']['execution_authorized'])
        self.assertFalse(any(self.request['authority'].values()))

    def test_request_revalidates_by_exact_regeneration(self):
        result = validate_evidence_request(self.request, *self.input_bytes())
        self.assertTrue(result['request_valid'])
        self.assertFalse(result['evidence_valid'])
        self.assertIsNone(result['spendable'])
        self.assertEqual(result['allowed_mutations'], [])
        self.assertFalse(result['execution_authorized'])

    def test_modified_stage_e_bundle_is_rejected(self):
        modified = self.bundle_raw + b'\n'
        with self.assertRaises(StageCError) as raised:
            build_evidence_request(
                self.stage_a_raw, self.stage_d_raw, self.post_raw,
                modified, self.package_raw, created_at=CREATED_AT)
        self.assertEqual(str(raised.exception),
                         'evidence_request: Stage E bundle bytes differ')

    def test_modified_stage_e_package_is_rejected(self):
        modified = self.package_raw + b'\n'
        with self.assertRaises(StageCError) as raised:
            build_evidence_request(
                self.stage_a_raw, self.stage_d_raw, self.post_raw,
                self.bundle_raw, modified, created_at=CREATED_AT)
        self.assertEqual(str(raised.exception),
                         'evidence_request: Stage E package bytes differ')

    def test_tampered_request_is_rejected(self):
        value = deepcopy(self.request)
        value['requested_evidence'][0]['required_evidence'].append('optional evidence')
        with self.assertRaises(StageCError) as raised:
            validate_evidence_request(value, *self.input_bytes())
        self.assertEqual(str(raised.exception),
                         'evidence_request: request differs from exact regeneration')

    def test_authority_cannot_be_injected(self):
        value = deepcopy(self.request)
        value['authority']['reconcile'] = True
        with self.assertRaises(StageCError) as raised:
            validate_evidence_request(value, *self.input_bytes())
        self.assertEqual(str(raised.exception),
                         'evidence_request: request differs from exact regeneration')

    def test_non_null_spendability_cannot_be_injected(self):
        value = deepcopy(self.request)
        value['outcome']['spendable'] = True
        with self.assertRaises(StageCError) as raised:
            validate_evidence_request(value, *self.input_bytes())
        self.assertEqual(str(raised.exception),
                         'evidence_request: request differs from exact regeneration')

    def test_missing_item_is_rejected(self):
        value = deepcopy(self.request)
        value['requested_evidence'].pop()
        value['request_summary']['total_items'] -= 1
        with self.assertRaises(StageCError) as raised:
            validate_evidence_request(value, *self.input_bytes())
        self.assertEqual(str(raised.exception),
                         'evidence_request: request differs from exact regeneration')


if __name__ == '__main__':
    unittest.main()
