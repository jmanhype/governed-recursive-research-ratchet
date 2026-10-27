"""Validate the Stage B evidence-gap plan without any protected access."""

import hashlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
STAGE_A = ROOT / 'docs/evidence/spendability/stage-a'
STAGE_B = ROOT / 'docs/evidence/spendability/stage-b'


def load(path: Path) -> object:
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError('duplicate JSON key: ' + key)
            result[key] = value
        return result

    def reject(value):
        raise ValueError('non-finite JSON constant: ' + value)

    return json.loads(path.read_bytes(), object_pairs_hook=unique,
                      parse_constant=reject)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class SpendabilityGapPlan(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan = load(STAGE_B / 'GAP-PLAN.json')
        cls.baseline = load(STAGE_A / 'BASELINE.json')
        cls.validation = load(STAGE_A / 'VALIDATION.json')

    def test_plan_is_bound_to_approved_stage_a_artifacts(self):
        basis = self.plan['basis']
        self.assertEqual(basis['baseline_sha256'], sha256(STAGE_A / 'BASELINE.json'))
        self.assertEqual(basis['database_sha256'], self.baseline['database']['before']['sha256'])
        self.assertEqual(basis['active_binding_sha256'],
                         self.baseline['source_files']['active']['sha256'])
        self.assertEqual(basis['evidence_contract_sha256'],
                         self.baseline['source_files']['policy_contract']['sha256'])
        self.assertEqual(basis['stage_a_review'], 'APPROVED_BASELINE_CAPTURE')

    def test_plan_covers_every_failed_stage_a_gate_exactly(self):
        result = self.validation['interpreters']['/usr/bin/python3']
        failed = {gate['gate'] for gate in result['gate_results'] if not gate['passed']}
        planned = {gate['gate'] for gate in self.plan['required_gates']}
        self.assertEqual(planned, failed)
        self.assertEqual(len(self.plan['required_gates']), len(failed))
        self.assertEqual(self.plan['required_outcome']['first_failed_gate'],
                         result['first_failed_gate'])

    def test_observed_counts_and_known_encumbrance_are_preserved(self):
        observed = self.plan['observed_state']
        self.assertEqual(observed['reservation_count'], 11)
        self.assertEqual(observed['settled_meter_count'], 8)
        self.assertEqual(observed['pending_count'], 3)
        self.assertEqual(observed['overhead_row_count'], 0)
        self.assertEqual(observed['stopped'], 0)
        self.assertEqual(observed['settled_execution_us'], 208_265_788)
        self.assertEqual(observed['pending_maximum_execution_us'], 900_000_000)
        self.assertEqual(observed['known_encumbered_execution_us'], 1_108_265_788)
        self.assertEqual(observed['unknown_upper_bound'], 'unresolved-unbounded')

    def test_pending_ids_and_overhead_domains_are_exact(self):
        rows = self.baseline['raw_tables']['reservations']['rows']
        def actual_value(row):
            cell = row['actual']
            return cell.get('value', cell.get('decoded'))

        actual = sorted(row['id']['value'] for row in rows if actual_value(row) is None)
        self.assertEqual(sorted(self.plan['pending_reservation_ids']), actual)
        self.assertEqual(set(self.plan['overhead_categories']),
                         {'preparation', 'selection', 'execution', 'review', 'other'})

    def test_each_gap_has_fail_closed_evidence_and_acceptance(self):
        required = {'gate', 'remediation', 'required_evidence', 'acceptance', 'failure_result'}
        for gap in self.plan['required_gates']:
            with self.subTest(gap=gap['gate']):
                self.assertEqual(set(gap), required)
                self.assertIsInstance(gap['remediation'], str)
                self.assertGreaterEqual(len(gap['required_evidence']), 3)
                self.assertIsInstance(gap['acceptance'], str)
                self.assertTrue(gap['acceptance'])
                self.assertIn('unresolved', gap['failure_result'])

    def test_plan_grants_no_authority_and_requires_null_spendability(self):
        authority = self.plan['authority']
        self.assertEqual(set(authority), {'protected_access', 'write', 'reconcile', 'replay',
                                          'promotion', 'admission', 'merge', 'push'})
        self.assertFalse(any(authority.values()))
        outcome = self.plan['required_outcome']
        self.assertIs(outcome['valid'], False)
        self.assertIsNone(outcome['spendable'])
        self.assertEqual(outcome['allowed_mutations'], [])
        self.assertIs(outcome['execution_authorized'], False)


if __name__ == '__main__':
    unittest.main()
