# Review packet — GRRR-q3hp capstone driver (revision 2)



## research/capstone_driver.py

"""Explicit capstone prepare/run driver.

Pure functions over caller-supplied authenticated receipts and an injected
dispatch callable. The operator CLI never holds evaluator authority: it can
prepare a plan and it refuses `run` without a trusted dispatcher.

`prepare` performs no VM launch, no protected access and no accounting write.
Every gate is recorded separately; no aggregate code manufactures a pass.
"""
from __future__ import annotations

import re

from common import GATES, Failure, canonical, digest, fields, identifier, require

VERSION = 1
PREPARE_SCHEMA = 'capstone-prepare-plan-v1'
RUN_SCHEMA = 'capstone-run-record-v1'
RECEIPT_KINDS = ('runtime', 'corpus', 'vm', 'accounting', 'observation',
                 'replay', 'source_review', 'reviewer', 'approval')
REQUEST_FIELDS = {'version', 'driver_commit', 'runtime_identity', 'corpus_binding',
                  'accounting_binding', 'vm_assets', 'authorization_sha256',
                  'request_sha256', 'floors', 'receipts'}
GATE_RECEIPTS = {
    'source_environment_identity': ('runtime',),
    'isolation': ('vm',),
    'protected_asset_integrity': ('vm', 'corpus'),
    'baseline_correctness': ('corpus',),
    'trusted_observation': ('observation',),
    'independent_replay': ('replay',),
    'specification_traceability': ('source_review',),
    'evidence_integrity_currency': ('corpus', 'vm'),
    'budget_state': ('accounting',),
    'reviewer_outcome': ('reviewer',),
    'action_specific_human_approval': ('approval',),
}
_COMMIT = re.compile(r'[0-9a-f]{7,40}')


def _gate(state: str, evidence=None, reason=None) -> dict:
    return {'state': state, 'evidence': evidence, 'reason': reason}


def _floors(value: dict) -> dict:
    fields(value, {'free_bytes', 'required_bytes'})
    require(all(type(value[name]) is int and value[name] >= 0
                for name in ('free_bytes', 'required_bytes')),
            'InvalidInput', 'Floor values must be nonnegative integers')
    return dict(value)


def _receipts(value: dict) -> dict:
    require(type(value) is dict and set(value) <= set(RECEIPT_KINDS),
            'InvalidInput', 'Unknown receipt kind')
    for name, hashed in value.items():
        identifier(hashed, True)
    return dict(value)


def _request(value: dict) -> dict:
    fields(value, REQUEST_FIELDS)
    require(value['version'] == VERSION and type(value['version']) is int,
            'InvalidInput', 'Unknown driver request version')
    require(type(value['driver_commit']) is str
            and _COMMIT.fullmatch(value['driver_commit']) is not None,
            'InvalidInput', 'Driver commit must be a hex revision')
    for name in ('runtime_identity', 'corpus_binding', 'accounting_binding',
                 'vm_assets', 'authorization_sha256', 'request_sha256'):
        identifier(value[name], True)
    bound = {'version': VERSION, 'driver_commit': value['driver_commit'],
             'runtime_identity': value['runtime_identity'],
             'corpus_binding': value['corpus_binding'],
             'accounting_binding': value['accounting_binding'],
             'vm_assets': value['vm_assets'],
             'authorization_sha256': value['authorization_sha256'],
             'request_sha256': value['request_sha256'],
             'floors': _floors(value['floors']),
             'receipts': _receipts(value['receipts'])}
    body = dict(bound, request_sha256=None)
    require(bound['request_sha256'] == digest(canonical(body)),
            'InvalidInput', 'Request digest does not bind the request body')
    return bound


def _gates(request: dict, verify):
    """Each gate needs its OWN approved receipts; existence alone proves nothing."""
    gates, refusals = {}, []
    for name in GATES:
        needed = GATE_RECEIPTS[name]
        missing = [kind for kind in needed if kind not in request['receipts']]
        if missing:
            gates[name] = _gate('not-run', None, 'no-' + missing[0] + '-receipt')
            refusals.append(name + '-unverified')
            continue
        if verify is None:
            gates[name] = _gate('blocked', None, 'receipt-unverified')
            refusals.append(name + '-unverified')
            continue
        approved = True
        for kind in needed:
            if not verify(kind, request['receipts'][kind], request):
                approved = False
        if approved:
            gates[name] = _gate('pass', request['receipts'][needed[0]], None)
        else:
            gates[name] = _gate('blocked', None, 'receipt-rejected')
            refusals.append(name + '-unverified')
    require(set(gates) == set(GATES), 'InvalidInput', 'Gate inventory differs')
    return gates, refusals


def prepare(request: dict, *, verify=None) -> dict:
    """Bind revisions and emit an immutable per-gate plan. No side effects.

    `verify(kind, receipt_sha256, bound_request) -> bool` is trusted evaluator
    wiring. Without it every receipt-backed gate is blocked, never passed.
    """
    bound = _request(request)
    floors = bound['floors']
    gates, refusals = _gates(bound, verify)
    if floors['free_bytes'] < floors['required_bytes']:
        refusals.append('floor-breach')
        for name in GATES:
            if gates[name]['state'] == 'not-run':
                gates[name] = _gate('error', None, 'floor-breach')
    plan = {'schema': PREPARE_SCHEMA, 'version': VERSION, 'bound': bound,
            'gates': gates, 'refusals': sorted(set(refusals)),
            'runnable': not refusals and all(gates[name]['state'] == 'pass' for name in GATES)}
    plan['plan_id'] = digest(canonical(plan))
    return plan


def run(plan: dict, request: dict, *, dispatch=None, verify=None) -> dict:
    """Recompute the plan and dispatch only if it still matches exactly."""
    require(type(plan) is dict and plan.get('schema') == PREPARE_SCHEMA,
            'InvalidInput', 'Unknown prepare plan')
    expected = prepare(request, verify=verify)
    require(plan == expected, 'StaleBinding',
            'Plan differs from a fresh recomputation of the same request')
    blocked = [name for name in GATES if expected['gates'][name]['state'] != 'pass']
    require(expected['runnable'] and not blocked, 'GateBlocked',
            'Plan is not runnable: ' + ','.join(sorted(set(expected['refusals']) | set(blocked))))
    require(dispatch is not None, 'Unavailable',
            'No authenticated evaluator dispatcher; the operator cannot execute')
    result = dispatch(dict(expected))
    require(type(result) is dict, 'InvalidInput', 'Dispatcher result differs')
    return {'schema': RUN_SCHEMA, 'version': VERSION, 'plan_id': expected['plan_id'],
            'gates': expected['gates'], 'dispatch': result, 'executed': True}


## tests/unit_capstone_driver.py

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
