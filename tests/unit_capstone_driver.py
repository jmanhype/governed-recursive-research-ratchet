"""Public no-guest driver tests: parsing, binding, refusal ordering, truth.

Synthetic receipts only, and only an injected verifier can approve them. These
are NOT VM, evaluator or ledger proof.
"""
import copy
import unittest

from common import GATES, Failure, canonical, digest
from capstone_driver import PREPARE_SCHEMA, prepare, run

H = 'a' * 64
KINDS = ('runtime', 'corpus', 'vm', 'accounting', 'observation', 'replay',
         'source_review', 'reviewer', 'approval')


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
        'receipts': {name: H for name in KINDS},
    }
    value.update(changes)
    body = dict(value, request_sha256=None)
    value['request_sha256'] = digest(canonical(body))
    return value


def approve_all(kind, hashed, bound):
    return True


class PrepareTests(unittest.TestCase):
    def test_verified_receipts_make_a_runnable_plan_with_every_gate_separate(self):
        plan = prepare(request(), verify=approve_all)
        self.assertEqual(plan['schema'], PREPARE_SCHEMA)
        self.assertTrue(plan['runnable'])
        self.assertEqual(plan['refusals'], [])
        self.assertEqual(set(plan['gates']), set(GATES))
        self.assertTrue(all(plan['gates'][name]['state'] == 'pass' for name in GATES))

    def test_without_a_verifier_every_receipt_gate_is_blocked(self):
        plan = prepare(request())
        self.assertFalse(plan['runnable'])
        self.assertTrue(all(plan['gates'][name]['state'] == 'blocked' for name in GATES))
        self.assertIn('budget_state-unverified', plan['refusals'])

    def test_rejected_receipt_blocks_only_its_gate(self):
        def reject_budget(kind, hashed, bound):
            return kind != 'accounting'

        plan = prepare(request(), verify=reject_budget)
        self.assertFalse(plan['runnable'])
        self.assertEqual(plan['gates']['budget_state']['state'], 'blocked')
        self.assertEqual(plan['gates']['isolation']['state'], 'pass')

    def test_missing_accounting_is_truthful_not_run(self):
        value = request()
        value['receipts'].pop('accounting')
        body = dict(value, request_sha256=None)
        value['request_sha256'] = digest(canonical(body))
        plan = prepare(value, verify=approve_all)
        self.assertFalse(plan['runnable'])
        self.assertEqual(plan['gates']['budget_state']['state'], 'not-run')
        self.assertIn('budget_state-unverified', plan['refusals'])

    def test_floor_breach_refuses_before_anything_runs(self):
        value = request(floors={'free_bytes': 1, 'required_bytes': 2})
        value['receipts'].pop('observation')
        body = dict(value, request_sha256=None)
        value['request_sha256'] = digest(canonical(body))
        plan = prepare(value, verify=approve_all)
        self.assertFalse(plan['runnable'])
        self.assertIn('floor-breach', plan['refusals'])
        self.assertEqual(plan['gates']['trusted_observation']['state'], 'error')

    def test_historical_or_malformed_receipts_are_rejected(self):
        value = request()
        value['receipts']['vm'] = 'historical-provenance'
        with self.assertRaises(Failure) as blocked:
            prepare(value, verify=approve_all)
        self.assertEqual(blocked.exception.record['code'], 'InvalidInput')
        value = request()
        value['receipts']['unknown'] = H
        with self.assertRaises(Failure):
            prepare(value, verify=approve_all)

    def test_request_digest_must_bind_the_body(self):
        value = request()
        value['corpus_binding'] = 'b' * 64
        with self.assertRaises(Failure):
            prepare(value, verify=approve_all)

    def test_bad_commit_and_unknown_version_are_rejected(self):
        with self.assertRaises(Failure):
            prepare(request(driver_commit='not-a-commit'), verify=approve_all)
        with self.assertRaises(Failure):
            prepare(request(version=2), verify=approve_all)

    def test_prepare_is_deterministic(self):
        self.assertEqual(prepare(request(), verify=approve_all),
                         prepare(request(), verify=approve_all))


class RunTests(unittest.TestCase):
    def setUp(self):
        self.request = request()
        self.plan = prepare(self.request, verify=approve_all)
        self.calls = []

    def dispatch(self, plan):
        self.calls.append(plan['plan_id'])
        return {'action': 'dispatch', 'run': 'fixture'}

    def test_run_dispatches_only_a_recomputed_matching_plan(self):
        record = run(self.plan, self.request, dispatch=self.dispatch, verify=approve_all)
        self.assertTrue(record['executed'])
        self.assertEqual(record['plan_id'], self.plan['plan_id'])
        self.assertEqual(self.calls, [self.plan['plan_id']])

    def test_run_requires_a_dispatcher(self):
        with self.assertRaises(Failure) as blocked:
            run(self.plan, self.request, verify=approve_all)
        self.assertEqual(blocked.exception.record['code'], 'Unavailable')

    def test_run_refuses_a_forged_plan_even_with_a_matching_self_digest(self):
        # Start from a truthful non-runnable plan, then forge it to look runnable.
        forged = copy.deepcopy(prepare(self.request))
        forged['gates']['budget_state'] = {'state': 'pass', 'evidence': H, 'reason': None}
        forged['refusals'] = []
        forged['runnable'] = True
        forged['plan_id'] = digest(canonical({key: forged[key] for key in
                                              ('schema', 'version', 'bound', 'gates',
                                               'refusals', 'runnable')}))
        with self.assertRaises(Failure) as blocked:
            run(forged, self.request, dispatch=self.dispatch, verify=approve_all)
        self.assertEqual(blocked.exception.record['code'], 'StaleBinding')
        self.assertEqual(self.calls, [])

    def test_run_refuses_changed_binding(self):
        changed = request()
        changed['corpus_binding'] = 'b' * 64
        body = dict(changed, request_sha256=None)
        changed['request_sha256'] = digest(canonical(body))
        with self.assertRaises(Failure) as blocked:
            run(self.plan, changed, dispatch=self.dispatch, verify=approve_all)
        self.assertEqual(blocked.exception.record['code'], 'StaleBinding')

    def test_run_refuses_a_non_runnable_plan(self):
        plan = prepare(self.request)
        with self.assertRaises(Failure) as blocked:
            run(plan, self.request, dispatch=self.dispatch)
        self.assertEqual(blocked.exception.record['code'], 'GateBlocked')
        self.assertEqual(self.calls, [])


if __name__ == '__main__':
    unittest.main()
