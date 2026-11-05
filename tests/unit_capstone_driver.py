"""Public no-guest driver tests: parsing, binding, refusal ordering, truth.

Synthetic receipts only. These are NOT VM, evaluator or ledger proof.
"""
import copy
import unittest

from common import GATES, Failure
from capstone_driver import PREPARE_SCHEMA, prepare, run

H = 'a' * 64


def request(**changes):
    value = {
        'version': 1,
        'driver_commit': '51ebc99',
        'runtime_identity': H,
        'corpus_binding': H,
        'accounting_binding': H,
        'vm_assets': H,
        'authorization_sha256': H,
        'request_sha256': H,
        'floors': {'free_bytes': 32_000_000_000, 'required_bytes': 16_000_000_000},
        'receipts': {name: H for name in
                     ('runtime', 'corpus', 'vm', 'accounting', 'review',
                      'approval', 'observation')},
    }
    value.update(changes)
    return value


class PrepareTests(unittest.TestCase):
    def test_all_receipts_make_a_runnable_plan_with_every_gate_separate(self):
        plan = prepare(request())
        self.assertEqual(plan['schema'], PREPARE_SCHEMA)
        self.assertTrue(plan['runnable'])
        self.assertEqual(plan['refusals'], [])
        self.assertEqual(set(plan['gates']), set(GATES))
        self.assertTrue(all(plan['gates'][name]['state'] == 'pass' for name in GATES))

    def test_missing_accounting_blocks_budget_and_refuses(self):
        value = request()
        value['receipts'].pop('accounting')
        plan = prepare(value)
        self.assertFalse(plan['runnable'])
        self.assertEqual(plan['gates']['budget_state']['state'], 'blocked')
        self.assertIn('budget-unverified', plan['refusals'])
        self.assertEqual(plan['gates']['source_environment_identity']['state'], 'pass')

    def test_missing_review_and_approval_are_truthful_not_run(self):
        value = request()
        value['receipts'].pop('review')
        value['receipts'].pop('approval')
        plan = prepare(value)
        self.assertFalse(plan['runnable'])
        self.assertEqual(plan['gates']['reviewer_outcome']['state'], 'not-run')
        self.assertEqual(plan['gates']['action_specific_human_approval']['state'], 'not-run')
        self.assertIn('review-missing', plan['refusals'])
        self.assertIn('approval-missing', plan['refusals'])

    def test_floor_breach_refuses_before_anything_runs(self):
        value = request(floors={'free_bytes': 1, 'required_bytes': 2})
        value['receipts'].pop('observation')
        plan = prepare(value)
        self.assertFalse(plan['runnable'])
        self.assertIn('floor-breach', plan['refusals'])
        self.assertEqual(plan['gates']['trusted_observation']['state'], 'error')

    def test_historical_or_malformed_receipts_are_rejected(self):
        value = request()
        value['receipts']['vm'] = 'historical-provenance'
        with self.assertRaises(Failure) as blocked:
            prepare(value)
        self.assertEqual(blocked.exception.record['code'], 'InvalidInput')
        value = request()
        value['receipts']['unknown'] = H
        with self.assertRaises(Failure):
            prepare(value)

    def test_bad_commit_and_unknown_version_are_rejected(self):
        with self.assertRaises(Failure):
            prepare(request(driver_commit='not-a-commit'))
        with self.assertRaises(Failure):
            prepare(request(version=2))

    def test_prepare_has_no_environment_side_effects(self):
        plan = prepare(request())
        replayed = prepare(request())
        self.assertEqual(plan['plan_id'], replayed['plan_id'])


class RunTests(unittest.TestCase):
    def setUp(self):
        self.request = request()
        self.plan = prepare(self.request)
        self.calls = []

    def dispatch(self, plan):
        self.calls.append(plan['plan_id'])
        return {'action': 'dispatch', 'run': 'fixture'}

    def test_run_dispatches_only_the_prepared_binding(self):
        record = run(self.plan, self.request, dispatch=self.dispatch)
        self.assertTrue(record['executed'])
        self.assertEqual(record['plan_id'], self.plan['plan_id'])
        self.assertEqual(self.calls, [self.plan['plan_id']])
        self.assertEqual(set(record['gates']), set(GATES))

    def test_run_requires_a_dispatcher(self):
        with self.assertRaises(Failure) as blocked:
            run(self.plan, self.request)
        self.assertEqual(blocked.exception.record['code'], 'Unavailable')

    def test_run_refuses_changed_binding(self):
        changed = request(corpus_binding='b' * 64)
        with self.assertRaises(Failure) as blocked:
            run(self.plan, changed, dispatch=self.dispatch)
        self.assertEqual(blocked.exception.record['code'], 'StaleBinding')
        self.assertEqual(self.calls, [])

    def test_run_refuses_tampered_plan(self):
        tampered = copy.deepcopy(self.plan)
        tampered['bound']['driver_commit'] = 'deadbee'
        with self.assertRaises(Failure) as blocked:
            run(tampered, self.request, dispatch=self.dispatch)
        self.assertEqual(blocked.exception.record['code'], 'StaleBinding')

    def test_run_refuses_a_non_runnable_plan(self):
        value = request()
        value['receipts'].pop('accounting')
        plan = prepare(value)
        with self.assertRaises(Failure) as blocked:
            run(plan, value, dispatch=self.dispatch)
        self.assertEqual(blocked.exception.record['code'], 'GateBlocked')
        self.assertEqual(self.calls, [])


if __name__ == '__main__':
    unittest.main()
