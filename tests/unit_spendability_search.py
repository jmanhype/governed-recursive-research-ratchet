"""Stage G local spendability evidence-search tests."""

from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import shutil
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'research'))

from spendability_search import (  # noqa: E402
    STAGE_A_BASELINE_SHA256,
    STAGE_F_PACKAGE_SHA256,
    STAGE_F_REQUEST_SHA256,
    build_external_evidence_search,
    validate_external_evidence_search,
)
from spendability_stage_c import StageCError  # noqa: E402


REQUEST = ROOT / 'docs/evidence/spendability/stage-f/REQUEST.json'
PACKAGE = ROOT / 'docs/evidence/spendability/stage-f/PACKAGE.json'
BASELINE = ROOT / 'docs/evidence/spendability/stage-a/BASELINE.json'
EXPORT = ROOT / 'docs/evidence/trusted-observation/v4-run-9d3df87'


class SpendabilityEvidenceSearch(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.request_raw = REQUEST.read_bytes()
        cls.package_raw = PACKAGE.read_bytes()
        cls.baseline_raw = BASELINE.read_bytes()
        cls.record = build_external_evidence_search(
            cls.request_raw, cls.package_raw, cls.baseline_raw, EXPORT)

    def inputs(self):
        return self.request_raw, self.package_raw, self.baseline_raw, EXPORT

    def test_binds_exact_approved_inputs(self):
        basis = self.record['basis']
        self.assertEqual(sha256(self.request_raw).hexdigest(), basis['stage_f_request_sha256'])
        self.assertEqual(sha256(self.package_raw).hexdigest(), basis['stage_f_package_sha256'])
        self.assertEqual(sha256(self.baseline_raw).hexdigest(), basis['stage_a_baseline_sha256'])
        self.assertEqual(basis['stage_f_package_sha256'], STAGE_F_PACKAGE_SHA256)
        self.assertEqual(basis['stage_f_request_sha256'], STAGE_F_REQUEST_SHA256)
        self.assertEqual(basis['stage_a_baseline_sha256'], STAGE_A_BASELINE_SHA256)

    def test_search_inventory_covers_all_thirty_items_once(self):
        items = self.record['items']
        identifiers = [item['request_item_id'] for item in items]
        self.assertEqual(len(items), 30)
        self.assertEqual(len(identifiers), len(set(identifiers)))
        self.assertEqual(self.record['summary'], {
            'total_items': 30,
            'validated_complete_candidate_items': 8,
            'partial_candidate_items': 7,
            'negative_search_not_established': 15,
            'final_classifications_made': 0,
        })

    def test_eight_settled_reservations_have_complete_candidate_joins(self):
        complete = [item for item in self.record['items']
                    if item.get('candidate_completeness')
                    == 'request-observation-and-meter-join']
        self.assertEqual(len(complete), 8)
        for item in complete:
            roles = {artifact['role'] for artifact in item['artifacts']}
            self.assertEqual(roles, {
                'reservation-request-event',
                'trusted-observation-object',
                'meter-body-exact-copy',
            })
            self.assertIsNone(item['classification'])

    def test_three_pending_reservations_remain_partial(self):
        pending = [item for item in self.record['items']
                   if item['kind'] == 'pending-disposition']
        self.assertEqual({item['subject'] for item in pending}, {
            '69523b39a51c44739114313c9325028c',
            'b34d8b9d106e42eab3a3e43daac98ddd',
            'd375ce6a2d924646bec71df64e939a5b',
        })
        for item in pending:
            self.assertEqual(item['search_status'], 'partial-pending-record-candidate')
            self.assertIn('cessation proof', item['unresolved'])

    def test_lineage_absence_is_not_converted_into_unavailable(self):
        lineage = [item for item in self.record['items']
                   if item['kind'] == 'historical-lineage']
        self.assertEqual(len(lineage), 8)
        for item in lineage:
            self.assertEqual(item['search_status'], 'search-completeness-not-established')
            self.assertIsNone(item['classification'])
            self.assertEqual(item['unresolved'], ['exact artifact bytes and custody'])

    def test_coverage_domains_do_not_become_complete_history(self):
        by_kind = {item['kind']: item for item in self.record['items']}
        self.assertEqual(by_kind['operation-history']['search_status'],
                         'partial-evaluator-export-only')
        self.assertEqual(by_kind['side-store-history']['search_status'],
                         'search-completeness-not-established')
        self.assertEqual(by_kind['global-historical-completeness']['search_status'],
                         'search-completeness-not-established')
        for category in ('preparation', 'selection', 'execution', 'review', 'other'):
            item = next(item for item in self.record['items']
                        if item['kind'] == 'overhead-domain'
                        and item['subject'] == category)
            self.assertEqual(item['search_status'],
                             'search-completeness-not-established')

    def test_record_remains_fail_closed_and_powerless(self):
        self.assertFalse(self.record['outcome']['classification_complete'])
        self.assertFalse(self.record['outcome']['valid'])
        self.assertIsNone(self.record['outcome']['spendable'])
        self.assertFalse(self.record['outcome']['execution_authorized'])
        self.assertEqual(self.record['outcome']['allowed_mutations'], [])
        self.assertFalse(any(self.record['authority'].values()))
        observations = self.record['discovery_observations']
        self.assertEqual(observations['protected_paths_accessed_by_generator'], [])
        self.assertFalse(observations['generator_consumes_search_receipts'])
        self.assertIn('negative results are not established by this generator',
                      observations['exclusions'])

    def test_record_revalidates_by_exact_regeneration(self):
        result = validate_external_evidence_search(self.record, *self.inputs())
        self.assertTrue(result['record_valid'])
        self.assertFalse(result['classification_complete'])
        self.assertIsNone(result['spendable'])
        self.assertFalse(result['execution_authorized'])

    def test_modified_request_is_rejected(self):
        with self.assertRaises(StageCError) as raised:
            build_external_evidence_search(
                self.request_raw + b' ', self.package_raw,
                self.baseline_raw, EXPORT)
        self.assertEqual(str(raised.exception), 'evidence_search: Stage F request bytes differ')

    def test_modified_package_is_rejected(self):
        with self.assertRaises(StageCError) as raised:
            build_external_evidence_search(
                self.request_raw, self.package_raw + b' ',
                self.baseline_raw, EXPORT)
        self.assertEqual(str(raised.exception), 'evidence_search: Stage F package bytes differ')

    def test_modified_baseline_is_rejected(self):
        with self.assertRaises(StageCError) as raised:
            build_external_evidence_search(
                self.request_raw, self.package_raw,
                self.baseline_raw + b' ', EXPORT)
        self.assertEqual(str(raised.exception), 'evidence_search: Stage A baseline bytes differ')

    def test_modified_trusted_ledger_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            copied = Path(temporary) / 'v4-run'
            shutil.copytree(EXPORT, copied)
            ledger = copied / 'evaluator/ledger.sqlite'
            raw = bytearray(ledger.read_bytes())
            raw[-1] ^= 1
            ledger.write_bytes(raw)
            with self.assertRaises(StageCError) as raised:
                build_external_evidence_search(
                    self.request_raw, self.package_raw, self.baseline_raw, copied)
            self.assertEqual(str(raised.exception),
                             'evidence_search: trusted export ledger bytes differ')

    def test_authority_injection_is_rejected_by_regeneration(self):
        value = deepcopy(self.record)
        value['authority']['reconcile'] = True
        with self.assertRaises(StageCError) as raised:
            validate_external_evidence_search(value, *self.inputs())
        self.assertEqual(str(raised.exception),
                         'evidence_search: record differs from exact regeneration')


if __name__ == '__main__':
    unittest.main()
