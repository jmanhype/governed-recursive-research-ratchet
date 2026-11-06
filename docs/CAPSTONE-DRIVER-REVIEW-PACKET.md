# Packet (minimal) — q3hp driver rev2

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
