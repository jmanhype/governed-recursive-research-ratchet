"""Stage E evidence-bundle assembler tests using retained evidence only."""

from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'research'))

from spendability_bundle import (  # noqa: E402
    assemble_evidence_bundle, validate_evidence_bundle,
)
from spendability_stage_c import StageCError  # noqa: E402


STAGE_A = ROOT / 'docs/evidence/spendability/stage-a/BASELINE.json'
STAGE_D = ROOT / 'docs/evidence/spendability/stage-d/CAPTURE.json'
POSTCAPTURE = ROOT / 'docs/evidence/spendability/stage-d/POSTCAPTURE-VERIFY.json'
STAGE_A_SHA256 = '7608cbe6fc5f671b88573eca8b642ebfbc172f0cb920f75d60ca34cfa60c730a'
STAGE_D_SHA256 = 'd22bec465786840fc85a139ebe3781f68bd1663bde51649ac96d34e03e340de8'
POSTCAPTURE_SHA256 = '78eb1f69a30d161f3c2d8c67fbbf40e579cc3de5f53b6bb0f8e8fc395888574a'


class SpendabilityBundle(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stage_a_raw = STAGE_A.read_bytes()
        cls.stage_d_raw = STAGE_D.read_bytes()
        cls.post_raw = POSTCAPTURE.read_bytes()
        cls.bundle = assemble_evidence_bundle(
            cls.stage_a_raw, cls.stage_d_raw, cls.post_raw,
            stage_d_capture_sha256=STAGE_D_SHA256,
            stage_d_postcapture_sha256=POSTCAPTURE_SHA256,
            created_at='2026-10-27T05:10:00Z',
        )

    def test_bundle_binds_exact_retained_stage_a_and_stage_d_bytes(self):
        basis = self.bundle['basis']
        self.assertEqual(basis['stage_a_baseline_sha256'], STAGE_A_SHA256)
        self.assertEqual(basis['stage_d_capture_sha256'], STAGE_D_SHA256)
        self.assertEqual(basis['stage_d_postcapture_sha256'], POSTCAPTURE_SHA256)
        self.assertEqual(basis['database_sha256'],
                         '9c6ff2561a364ed982cd5477dd4b200c995da6910c9a17aa3d3c411a962d64f3')
        self.assertEqual(basis['stage_d_independent_review'],
                         'STAGE_D_NARROW_REWORK_REVIEW: APPROVED')

    def test_raw_stage_a_row_multiset_is_preserved(self):
        stage_a = json.loads(self.stage_a_raw)
        self.assertEqual(self.bundle['raw_rows'], stage_a['raw_tables'])
        self.assertEqual(len(self.bundle['raw_rows']['reservations']['rows']), 11)
        self.assertEqual(len(self.bundle['raw_rows']['metering']['rows']), 8)
        self.assertEqual(len(self.bundle['raw_rows']['overhead']['rows']), 0)

    def test_stage_d_schema_and_quiescence_are_embedded_and_valid(self):
        self.assertEqual(self.bundle['schema_compatibility']['status'], 'mapped')
        self.assertTrue(self.bundle['quiescence']['validation']['schema_valid'])
        self.assertTrue(self.bundle['quiescence']['validation']['writer_exclusion_recorded'])
        self.assertFalse(self.bundle['quiescence']['validation']['writer_exclusion_observed'])
        self.assertIsNone(self.bundle['quiescence']['validation']['writer_exclusion_proven'])
        self.assertTrue(self.bundle['postcapture_immutable']['all_immutable'])

    def test_eleven_unresolved_provenance_sidecars_are_present(self):
        records = self.bundle['provenance']
        self.assertEqual(len(records), 11)
        self.assertEqual({record['reservation_id'] for record in records},
                         {row['id']['value'] for row in
                          self.bundle['raw_rows']['reservations']['rows']})
        self.assertTrue(all(record['status'] == 'unresolved' for record in records))
        self.assertTrue(all(record['meter']['meter_id'] is None for record in records))
        self.assertTrue(all(record['meter']['usage_sha256'] is None for record in records))

    def test_three_pending_holds_retain_full_maxima(self):
        records = self.bundle['pending_dispositions']
        self.assertEqual(len(records), 3)
        self.assertEqual({record['reservation_id'] for record in records}, {
            '69523b39a51c44739114313c9325028c',
            'b34d8b9d106e42eab3a3e43daac98ddd',
            'd375ce6a2d924646bec71df64e939a5b',
        })
        self.assertTrue(all(record['status'] == 'unresolved' for record in records))
        self.assertTrue(all(record['maximum']['execution_us'] == 300_000_000
                            for record in records))
        self.assertTrue(all(record['missing_evidence'] for record in records))

    def test_completeness_remains_unbounded_and_unresolved(self):
        value = self.bundle['historical_completeness']
        self.assertEqual(value['status'], 'unresolved')
        self.assertTrue(value['unbounded_unknown'])
        self.assertEqual(len(value['lineage']), 8)
        self.assertEqual(len(value['reservation_coverage']), 11)
        self.assertEqual(set(value['overhead']),
                         {'preparation', 'selection', 'execution', 'review', 'other'})
        self.assertTrue(all(item['upper_bound_us'] is None
                            for item in value['overhead'].values()))

    def test_gate_inventory_and_outcome_fail_closed(self):
        gates = self.bundle['gate_inventory']
        self.assertEqual(gates['schema_compatibility']['status'], 'pass')
        for name in ('quiescence', 'provenance', 'pending_evidence',
                     'overhead_completeness', 'historical_completeness',
                     'independent_review', 'operator_decision',
                     'spendability_decision'):
            self.assertEqual(gates[name]['status'], 'unresolved', name)
        outcome = self.bundle['outcome']
        self.assertTrue(self.bundle['assembly_valid'])
        self.assertFalse(self.bundle['evidence_valid'])
        self.assertFalse(outcome['valid'])
        self.assertEqual(outcome['first_failed_gate'], 'quiescence')
        self.assertIsNone(outcome['spendable'])
        self.assertEqual(outcome['allowed_mutations'], [])
        self.assertFalse(outcome['execution_authorized'])

    def test_bundle_has_no_operational_authority(self):
        self.assertFalse(any(self.bundle['authority'].values()))
        self.assertTrue(all(record['authority']['reconcile'] is False
                            for record in self.bundle['provenance']))
        self.assertTrue(all(record['authority']['replay'] is False
                            for record in self.bundle['pending_dispositions']))
        self.assertFalse(any(self.bundle['historical_completeness']['authority'].values()))

    def test_bundle_revalidates_by_exact_regeneration(self):
        result = validate_evidence_bundle(
            self.bundle, self.stage_a_raw, self.stage_d_raw, self.post_raw)
        self.assertTrue(result['assembly_valid'])
        self.assertFalse(result['evidence_valid'])
        self.assertEqual(result['first_failed_gate'], 'quiescence')
        self.assertIsNone(result['spendable'])

    def test_forged_stage_a_bytes_are_rejected(self):
        with self.assertRaises(StageCError) as raised:
            assemble_evidence_bundle(
                b'forged-stage-a', self.stage_d_raw, self.post_raw,
                stage_d_capture_sha256=STAGE_D_SHA256,
                stage_d_postcapture_sha256=POSTCAPTURE_SHA256,
                created_at='2026-10-27T05:10:00Z')
        self.assertEqual(str(raised.exception),
                         'evidence_bundle: Stage A baseline bytes differ')

    def test_unbound_stage_d_capture_is_rejected(self):
        with self.assertRaises(StageCError) as raised:
            assemble_evidence_bundle(
                self.stage_a_raw, self.stage_d_raw, self.post_raw,
                stage_d_capture_sha256='0' * 64,
                stage_d_postcapture_sha256=POSTCAPTURE_SHA256,
                created_at='2026-10-27T05:10:00Z')
        self.assertEqual(str(raised.exception),
                         'evidence_bundle: Stage D capture is not the approved byte digest')

    def test_modified_capture_cannot_be_authenticated_by_updated_bundle_basis(self):
        modified = self.stage_d_raw + b'\n'
        value = deepcopy(self.bundle)
        value['basis']['stage_d_capture_sha256'] = sha256(modified).hexdigest()
        with self.assertRaises(StageCError) as raised:
            validate_evidence_bundle(
                value, self.stage_a_raw, modified, self.post_raw)
        self.assertEqual(str(raised.exception),
                         'evidence_bundle: Stage D capture is not the approved byte digest')

    def test_unbound_postcapture_is_rejected(self):
        with self.assertRaises(StageCError) as raised:
            assemble_evidence_bundle(
                self.stage_a_raw, self.stage_d_raw, self.post_raw,
                stage_d_capture_sha256=STAGE_D_SHA256,
                stage_d_postcapture_sha256='0' * 64,
                created_at='2026-10-27T05:10:00Z')
        self.assertEqual(str(raised.exception),
                         'evidence_bundle: Stage D postcapture is not the approved byte digest')

    def test_modified_postcapture_cannot_be_authenticated_by_updated_bundle_basis(self):
        modified = self.post_raw + b'\n'
        value = deepcopy(self.bundle)
        value['basis']['stage_d_postcapture_sha256'] = sha256(modified).hexdigest()
        with self.assertRaises(StageCError) as raised:
            validate_evidence_bundle(
                value, self.stage_a_raw, self.stage_d_raw, modified)
        self.assertEqual(str(raised.exception),
                         'evidence_bundle: Stage D postcapture is not the approved byte digest')

    def test_tampered_bundle_is_rejected(self):
        value = deepcopy(self.bundle)
        value['provenance'][0]['status'] = 'authenticated'
        with self.assertRaises(StageCError) as raised:
            validate_evidence_bundle(
                value, self.stage_a_raw, self.stage_d_raw, self.post_raw)
        self.assertEqual(str(raised.exception),
                         'evidence_bundle: bundle differs from exact regeneration')

    def test_non_null_spendability_cannot_be_injected(self):
        value = deepcopy(self.bundle)
        value['outcome']['spendable'] = True
        with self.assertRaises(StageCError) as raised:
            validate_evidence_bundle(
                value, self.stage_a_raw, self.stage_d_raw, self.post_raw)
        self.assertEqual(str(raised.exception),
                         'evidence_bundle: bundle differs from exact regeneration')


if __name__ == '__main__':
    unittest.main()
