# Review packet — GRRR-q3hp capstone driver
HEAD: 90d3b130a8f75f4de7d738006c746b6f02a1950e

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
RECEIPT_KINDS = ('runtime', 'corpus', 'vm', 'accounting', 'review', 'approval',
                 'observation')
REQUEST_FIELDS = {'version', 'driver_commit', 'runtime_identity', 'corpus_binding',
                  'accounting_binding', 'vm_assets', 'authorization_sha256',
                  'request_sha256', 'floors', 'receipts'}
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
    return {'version': VERSION, 'driver_commit': value['driver_commit'],
            'runtime_identity': value['runtime_identity'],
            'corpus_binding': value['corpus_binding'],
            'accounting_binding': value['accounting_binding'],
            'vm_assets': value['vm_assets'],
            'authorization_sha256': value['authorization_sha256'],
            'request_sha256': value['request_sha256'],
            'floors': _floors(value['floors']),
            'receipts': _receipts(value['receipts'])}


def _gates(request: dict) -> tuple[dict, list]:
    """Each gate is decided by exactly one receipt; absent means not-run."""
    receipts = request['receipts']
    gates, refusals = {}, []

    def want(name: str, expected: tuple, refusal=None) -> dict:
        if name not in receipts:
            if refusal is not None:
                refusals.append(refusal)
            return _gate('not-run', None, refusal or 'no-receipt')
        return _gate('pass', receipts[name], None)

    gates['source_environment_identity'] = (
        _gate('pass', None, None) if 'runtime' in receipts
        else _gate('not-run', None, 'no-runtime-receipt'))
    gates['isolation'] = want('vm', (), 'isolation-unverified')
    gates['protected_asset_integrity'] = (
        _gate('pass', receipts['vm'], None)
        if {'vm', 'corpus'} <= set(receipts) else _gate('not-run', None, 'no-asset-receipt'))
    gates['baseline_correctness'] = want('corpus', (), 'baseline-unverified')
    gates['trusted_observation'] = want('observation', ())
    gates['independent_replay'] = want('observation', ())
    gates['specification_traceability'] = want('review', ())
    gates['evidence_integrity_currency'] = (
        _gate('pass', receipts['corpus'], None)
        if {'corpus', 'vm'} <= set(receipts) else _gate('not-run', None, 'no-asset-receipt'))
    if 'accounting' in receipts:
        gates['budget_state'] = _gate('pass', receipts['accounting'], None)
    else:
        gates['budget_state'] = _gate('blocked', None, 'budget-unverified')
        refusals.append('budget-unverified')
    gates['reviewer_outcome'] = want('review', (), 'review-missing')
    if 'approval' in receipts:
        gates['action_specific_human_approval'] = _gate('pass', receipts['approval'], None)
    else:
        gates['action_specific_human_approval'] = _gate('not-run', None, 'approval-missing')
        refusals.append('approval-missing')
    require(set(gates) == set(GATES), 'InvalidInput', 'Gate inventory differs')
    return gates, refusals


def prepare(request: dict) -> dict:
    """Bind revisions and emit an immutable per-gate plan. No side effects."""
    bound = _request(request)
    floors = bound['floors']
    gates, refusals = _gates(bound)
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


def run(plan: dict, request: dict, *, dispatch=None) -> dict:
    """Dispatch only a runnable plan that still matches every bound revision."""
    require(type(plan) is dict and plan.get('schema') == PREPARE_SCHEMA,
            'InvalidInput', 'Unknown prepare plan')
    body = {key: plan[key] for key in ('schema', 'version', 'bound', 'gates',
                                       'refusals', 'runnable')}
    require(plan.get('plan_id') == digest(canonical(body)),
            'StaleBinding', 'Prepare plan was changed after issue')
    bound = _request(request)
    require(bound == plan['bound'], 'StaleBinding', 'Run request differs from the prepared binding')
    blocked = [name for name in GATES if plan['gates'][name]['state'] != 'pass']
    require(not plan['refusals'] and plan['runnable'] and not blocked,
            'GateBlocked', 'Plan is not runnable: ' + ','.join(sorted(set(plan['refusals']) | set(blocked))))
    require(dispatch is not None, 'Unavailable',
            'No authenticated evaluator dispatcher; the operator cannot execute')
    result = dispatch(dict(plan))
    require(type(result) is dict, 'InvalidInput', 'Dispatcher result differs')
    return {'schema': RUN_SCHEMA, 'version': VERSION, 'plan_id': plan['plan_id'],
            'gates': plan['gates'], 'dispatch': result, 'executed': True}

## tests (names)
    def test_all_receipts_make_a_runnable_plan_with_every_gate_separate(self):
    def test_missing_accounting_blocks_budget_and_refuses(self):
    def test_missing_review_and_approval_are_truthful_not_run(self):
    def test_floor_breach_refuses_before_anything_runs(self):
    def test_historical_or_malformed_receipts_are_rejected(self):
    def test_bad_commit_and_unknown_version_are_rejected(self):
    def test_prepare_has_no_environment_side_effects(self):
    def test_run_dispatches_only_the_prepared_binding(self):
    def test_run_requires_a_dispatcher(self):
    def test_run_refuses_changed_binding(self):
    def test_run_refuses_tampered_plan(self):
    def test_run_refuses_a_non_runnable_plan(self):

## CLI
#!/usr/bin/env python3
"""Operator-facing capstone driver: prepare a plan, then request a run.

The CLI holds no evaluator authority. `run` exits non-zero with an
`Unavailable` record because no authenticated dispatcher is wired here; the
plan itself is always emitted so each gate's truth is inspectable.
"""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'research'))

from capstone_driver import prepare, run  # noqa: E402
from common import Failure  # noqa: E402


def _load(path: str) -> dict:
    return json.loads(Path(path).read_bytes())


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog='capstone-driver', add_help=True)
