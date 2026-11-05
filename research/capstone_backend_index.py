"""Source-only backend index coherence, not an authority or scheduler.

Only existing Ledger handles are accepted. No permits, worker capabilities,
recovery, installation, allowance checks or implicit migration are supplied.
Unsupported evidence-dependent transitions refuse rather than fabricate proof.
"""
import base64
import copy
import json
import os
from pathlib import Path
import stat

from common import (CAMPAIGN_EVENT_FORMAT, EVALUATOR, GATES, Failure, canonical, digest,
                    identifier, require, unique_fields)
from ledger import Ledger
from capstone_contract import decode_record, validate_record, operation_id, content_digest
from capstone_backend_schema import (BACKEND_SQL, BLOBS, PREFIX, PRIMARY_KEYS,
                                     TABLE_COLUMNS, validate_schema)

BASE_FORMAT = 'capstone-backend-event-v1'
CAMPAIGN_FORMAT = CAMPAIGN_EVENT_FORMAT
CAMPAIGN_ACTIONS = ('campaign-start', 'campaign-select', 'campaign-leaf-bind',
                    'campaign-advance', 'campaign-finish', 'campaign-fence',
                    'campaign-stop-outcome')
_OPEN = object()
MAX_RAW = 16 * 1024 * 1024


def _failure(phase, *, code, now_ns, leaf_id=None, operation_id=None, plan_hash=None,
             effects='none', next_action='query-status'):
    return dict(schema='capstone-failure-v1', phase=phase, input_sha256=None,
                authorization_sha256=None, campaign_plan_sha256=plan_hash,
                leaf_id=leaf_id, operation_id=operation_id, code=code,
                gates={name: dict(state='not-run', evidence=None, reason=None)
                       for name in GATES},
                effects=effects, next_action=next_action, created_ns=now_ns)


def derive_manifest(state, campaign_id, progress, gates, *, claim=None, now_ns=None):
    """Pure CampaignManifestV2 derivation; no Manifest is invented for a leaf."""
    identifier(campaign_id)
    _check(type(now_ns) is int and now_ns >= 0,
           'Campaign manifest needs an explicit observation time')
    run = state['campaign_run'].get((campaign_id,))
    _check(run is not None, 'Campaign manifest has no run')
    _check(type(gates) is dict and set(gates) == set(GATES),
           'Campaign manifest gates differ')
    for gate in gates.values():
        _check(set(gate) == {'state', 'evidence', 'reason'}
               and gate['state'] in ('pass', 'fail', 'not-run', 'error'),
               'Campaign manifest gate record differs')
    leaves = sorted((row for row in state['leaf'].values()
                     if row['campaign_id'] == campaign_id),
                    key=lambda row: row['leaf_index'])
    _check(bool(leaves), 'Campaign manifest has no leaves')
    completed = set((progress or {}).get(campaign_id, ()))
    entries, failures, claimed_count = [], [], 0
    for leaf in leaves:
        index = leaf['leaf_index']
        plan_row = state['leaf_plan'].get((campaign_id, index))
        if plan_row is None:
            failure = _failure('prepare', code='Unavailable', now_ns=now_ns,
                               leaf_id=leaf['leaf_id'], plan_hash=run['plan_hash'])
            entries.append(dict(leaf_id=leaf['leaf_id'], preclaim='not-planned',
                                operation_id=None, actual_plan_raw=None,
                                actual_plan_sha256=None, actual_plan_bytes_sha256=None,
                                review_sha256=None, manifest=None, failure=failure))
            failures.append(failure)
            continue
        plan = decode_record(plan_row['plan_raw'], 'Plan')
        _check(canonical(plan) == plan_row['plan_raw']
               and plan['plan_sha256'] == plan_row['plan_hash']
               and digest(plan_row['plan_raw']) == plan_row['plan_bytes_sha256']
               and plan_row['operation_id'] == operation_id(plan['grant']['grant_id'],
                                                            plan['plan_sha256']),
               'Campaign manifest Plan links differ')
        operation = claim(plan_row['operation_id']) if claim is not None else None
        if operation is None:
            failure = _failure('prepare', code='Unavailable', now_ns=now_ns,
                               leaf_id=leaf['leaf_id'], operation_id=plan_row['operation_id'],
                               plan_hash=run['plan_hash'], effects='possible')
            entries.append(dict(leaf_id=leaf['leaf_id'], preclaim='binding-only',
                                operation_id=plan_row['operation_id'],
                                actual_plan_raw=base64.b64encode(plan_row['plan_raw']).decode('ascii'),
                                actual_plan_sha256=plan_row['plan_hash'],
                                actual_plan_bytes_sha256=plan_row['plan_bytes_sha256'],
                                review_sha256=plan_row['review_hash'], manifest=None,
                                failure=failure))
            failures.append(failure)
            continue
        claimed_count += 1
        validate_record(operation, 'Operation')
        _check(operation['operation_id'] == plan_row['operation_id']
               and operation['plan_sha256'] == plan_row['plan_hash'],
               'Campaign manifest Operation links differ')
        manifest = dict(schema='capstone-manifest-v1', plan_sha256=plan_row['plan_hash'],
                        operation_id=plan_row['operation_id'], operation=operation,
                        transport='ok' if operation['dispatch'] == 'completed' else 'unknown',
                        gates=operation['gates'])
        validate_record(manifest, 'Manifest')
        entries.append(dict(leaf_id=leaf['leaf_id'], preclaim='claimed',
                            operation_id=plan_row['operation_id'],
                            actual_plan_raw=base64.b64encode(plan_row['plan_raw']).decode('ascii'),
                            actual_plan_sha256=plan_row['plan_hash'],
                            actual_plan_bytes_sha256=plan_row['plan_bytes_sha256'],
                            review_sha256=plan_row['review_hash'], manifest=manifest,
                            failure=None))
    execution = ('not-run' if claimed_count == 0 else
                 'completed' if completed.issuperset(leaf['leaf_index'] for leaf in leaves)
                 else 'partial')
    manifest = dict(schema='capstone-campaign-manifest-v2',
                    campaign_plan_sha256=run['plan_hash'], leaves=entries, gates=gates,
                    execution=execution, verification='blocked', admission='blocked',
                    promotion='disabled', failures=failures)
    return manifest, digest(canonical(manifest))


def _campaign(state, event, receipt, grants, progress=None, joins=None, live=None,
              advance_proof=None, manifest_provider=None, fence_provider=None,
              stop_provider=None, replay=False, db=None):
    """Campaign-v2 reducer entry; unimplemented actions refuse, never accept."""
    _fields(event, ('format', 'action', 'record', 'idempotency_key', 'version'))
    record = event['record']
    _fields(record, ('campaign_id', 'previous_revision', 'run', 'binding',
                     'leaf_plan', 'evidence'))
    action = event['action']
    _check(action in CAMPAIGN_ACTIONS, 'Unknown campaign action')
    identifier(record['campaign_id'])
    evidence = record['evidence']
    _check(type(evidence) is list and evidence == sorted(set(evidence))
           and all(type(item) is str and len(item) == 64 for item in evidence),
           'Campaign evidence is unsorted, duplicated or malformed')
    previous = record['previous_revision']
    _check(previous is None or (type(previous) is int and previous >= 0),
           'Campaign previous revision differs')
    if action == 'campaign-select':
        _select(state, event, receipt, record, progress, joins, replay=replay)
        return []
    if action == 'campaign-leaf-bind':
        _leaf_bind(state, event, receipt, record, progress, joins, live, replay)
        return []
    if action == 'campaign-advance':
        _advance(state, event, receipt, record, progress, advance_proof, replay)
        return []
    if action == 'campaign-finish':
        return _finish(state, event, receipt, record, progress, manifest_provider, replay, db)
        return
    if action == 'campaign-fence':
        return _fence(state, event, receipt, record, progress, fence_provider, replay, db)
        return
    if action == 'campaign-stop-outcome':
        return _stop_outcome(state, event, receipt, record, progress, stop_provider, replay, db)
        return
    if action != 'campaign-start':
        raise Failure('Unavailable', 'Campaign action not implemented: ' + action)

    _check(previous is None and record['binding'] is None and record['leaf_plan'] is None,
           'Campaign start rows differ')
    _check(len(evidence) == 2, 'Campaign start evidence differs')
    run = _row('campaign_run', record['run'], ('last_event', 'intent_anchor'))
    _check(run['state'] == 'running' and run['active_leaf'] is None
           and run['result_object'] is None and run['revision'] == 0,
           'Campaign start run state differs')
    _check(len(run['owner_epoch']) == 64, 'Campaign owner epoch differs')
    campaign = state['campaign'].get((run['campaign_id'],))
    issuance = state['issuance'].get((run['auth_hash'],))
    _check(campaign is not None and campaign['campaign_id'] == run['campaign_id']
           and campaign['stopped'] == 0, 'Campaign start control join differs')
    _check(issuance is not None and issuance['phase'] == 'issued'
           and issuance['campaign_id'] == run['campaign_id']
           and issuance['auth_hash'] == run['auth_hash'], 'Campaign start issuance join differs')
    _check(all(row['state'] not in ('running', 'stop-pending', 'recovery-required')
               for row in state['campaign_run'].values()), 'Campaign already active')
    plan = decode_record(run['plan_raw'], 'Plan')
    _check(canonical(plan) == run['plan_raw'] and plan['plan_sha256'] == run['plan_hash'],
           'Campaign start plan bytes differ')
    grant_id = plan['grant']['grant_id']
    _check(grant_id in grants and grants[grant_id][0] == grant_id,
           'Campaign start grant join differs')
    _check(run['campaign_operation_id'] == operation_id(grant_id, plan['plan_sha256']),
           'Campaign start operation id differs')
    _check(event['idempotency_key'] == _domain('campaign-event-v2', {
        'campaign_id': run['campaign_id'], 'action': action, 'revision': 0}),
        'Campaign start key differs')
    run['last_event'] = receipt['digest']
    run['intent_anchor'] = receipt['digest']
    _put(state, 'campaign_run', run)
    return []


def _leaf_bind(state, event, receipt, record, progress, joins, live, replay=False):
    """Atomic base binding + leaf_plan insert; live owner/gate proof required."""
    if not replay:
        require(live is not None, 'Unavailable',
                'Live owner/gate/window verification is unavailable; bind refuses')
    del progress
    campaign_id = record['campaign_id']
    current = state['campaign_run'].get((campaign_id,))
    _check(current is not None and current['state'] == 'running'
           and current['active_leaf'] is not None, 'Campaign bind state differs')
    _check(record['previous_revision'] == current['revision'],
           'Campaign bind previous revision differs')
    binding = _row('binding', record['binding'], ('bind_anchor',))
    plan_row = _row('leaf_plan', record['leaf_plan'])
    _check(plan_row['campaign_id'] == campaign_id, 'Campaign bind campaign differs')
    _check(plan_row['leaf_index'] == current['active_leaf'],
           'Campaign bind leaf differs from the selected leaf')
    leaf = state['leaf'].get((campaign_id, plan_row['leaf_index']))
    _check(leaf is not None, 'Campaign bind leaf is absent')
    _check(binding['grant_id'] == leaf['grant_id'] and plan_row['operation_id']
           == binding['operation_id'], 'Campaign bind identity differs')
    plan = decode_record(plan_row['plan_raw'], 'Plan')
    _check(canonical(plan) == plan_row['plan_raw']
           and plan['plan_sha256'] == plan_row['plan_hash'] == binding['plan_hash'],
           'Campaign bind Plan bytes or selfhash differ')
    _check(digest(plan_row['plan_raw']) == plan_row['plan_bytes_sha256'],
           'Campaign bind Plan byte digest differs')
    _check(plan_row['operation_id'] == operation_id(plan['grant']['grant_id'],
                                                   plan['plan_sha256'])
           and plan['grant']['grant_id'] == leaf['grant_id'],
           'Campaign bind operation or grant differs')
    start = decode_record(binding['start_raw'], 'Start')
    _check(canonical(start) == binding['start_raw']
           and canonical(start['plan']) == plan_row['plan_raw']
           and start['operation_id'] == binding['operation_id']
           and digest(binding['start_raw']) == binding['start_hash'],
           'Campaign bind Start bytes differ')
    _check(record['evidence'] == [plan_row['review_hash']],
           'Campaign bind evidence differs')
    _check((campaign_id, plan_row['leaf_index']) not in state['leaf_plan'],
           'Campaign bind leaf already has a Plan')
    _check((binding['operation_id'],) not in state['binding'],
           'Campaign bind operation already exists')
    _check(not any(row['grant_id'] == binding['grant_id']
                   for row in state['binding'].values()),
           'Campaign bind grant already consumed')
    run = _row('campaign_run', record['run'], ('last_event',))
    for column in ('campaign_id', 'campaign_operation_id', 'plan_hash', 'plan_raw',
                   'auth_hash', 'owner_epoch', 'intent_anchor'):
        _check(run[column] == current[column], 'Campaign bind immutable field differs')
    _check(run['state'] == 'running' and run['result_object'] is None
           and run['active_leaf'] == current['active_leaf']
           and run['revision'] == current['revision'] + 1,
           'Campaign bind revision or run state differs')
    _check(event['idempotency_key'] == _domain('campaign-event-v2', {
        'campaign_id': campaign_id, 'action': event['action'],
        'revision': run['revision']}), 'Campaign bind key differs')
    if not replay:
        live(campaign_id, plan_row['leaf_index'], binding, plan_row, state)
    binding['bind_anchor'] = receipt['digest']
    _put(state, 'binding', binding)
    _put(state, 'leaf_plan', plan_row)
    run['last_event'] = receipt['digest']
    _put(state, 'campaign_run', run, True)


def _fence(state, event, receipt, record, progress, fence_provider, replay=False, db=None):
    """Controller-authenticated cut to recovery-required; never resumes work."""
    if not replay:
        require(fence_provider is not None, 'Unavailable',
                'Authenticated fence evidence is unavailable; fence refuses')
    _check(record['binding'] is None and record['leaf_plan'] is None,
           'Campaign fence rows differ')
    campaign_id = record['campaign_id']
    current = state['campaign_run'].get((campaign_id,))
    _check(current is not None and current['state'] in ('running', 'stop-pending'),
           'Campaign fence state differs')
    _check(record['previous_revision'] == current['revision'],
           'Campaign fence previous revision differs')
    run = _row('campaign_run', record['run'], ('last_event',))
    if replay:
        terminal = run['result_object']
        _check(terminal is not None and len(record['evidence']) == 3
               and terminal in record['evidence'], 'Campaign fence evidence differs')
        kinds = {}
        for hashed in record['evidence']:
            value = _json(_durable_object(db, hashed))
            _check(type(value) is dict and type(value.get('schema')) is str,
                   'Campaign fence evidence object differs')
            kinds[value['schema']] = value
        _check(set(kinds) == {'capstone-campaign-manifest-v2',
                              'capstone-failure-v1', 'capstone-campaign-fence-v2'},
               'Campaign fence evidence roles differ')
        manifest = kinds['capstone-campaign-manifest-v2']
        snapshot = kinds['capstone-campaign-fence-v2']
        _check(manifest.get('schema') == 'capstone-campaign-manifest-v2'
               and digest(canonical(manifest)) == terminal
               and snapshot.get('campaign_operation_id') == current['campaign_operation_id']
               and snapshot.get('owner_epoch') == current['owner_epoch']
               and snapshot.get('observed_owner') in ('present', 'absent')
               and snapshot.get('active_leaf') == current['active_leaf']
               and snapshot.get('cut') in ('owner-lost', 'binding-gap', 'claim-gap',
                                           'accounting-gap', 'dispatch-unknown',
                                           'evidence-failure'),
               'Campaign fence durable evidence differs')
        objects = []
    else:
        manifest, terminal, failure, snapshot = fence_provider(
            campaign_id, state, record['evidence'])
        _check(type(manifest) is dict
               and manifest.get('schema') == 'capstone-campaign-manifest-v2'
               and terminal == digest(canonical(manifest)),
               'Campaign fence manifest differs')
        _check(type(failure) is dict and failure.get('schema') == 'capstone-failure-v1',
               'Campaign fence failure record differs')
        _check(type(snapshot) is dict
               and snapshot.get('schema') == 'capstone-campaign-fence-v2'
               and snapshot.get('campaign_operation_id') == current['campaign_operation_id']
               and snapshot.get('owner_epoch') == current['owner_epoch']
               and snapshot.get('observed_owner') in ('present', 'absent')
               and snapshot.get('active_leaf') == current['active_leaf']
               and snapshot.get('cut') in ('owner-lost', 'binding-gap', 'claim-gap',
                                           'accounting-gap', 'dispatch-unknown',
                                           'evidence-failure'),
               'Campaign fence snapshot differs')
        _check(record['evidence'] == sorted({digest(canonical(failure)),
                                             digest(canonical(snapshot)), terminal}),
               'Campaign fence evidence differs')
        objects = [canonical(failure), canonical(snapshot), canonical(manifest)]
    for column in ('campaign_id', 'campaign_operation_id', 'plan_hash', 'plan_raw',
                   'auth_hash', 'owner_epoch', 'intent_anchor'):
        _check(run[column] == current[column], 'Campaign fence immutable field differs')
    _check(run['state'] == 'recovery-required'
           and run['active_leaf'] == current['active_leaf']
           and run['result_object'] == terminal
           and run['revision'] == current['revision'] + 1,
           'Campaign fence revision or run state differs')
    _check(event['idempotency_key'] == _domain('campaign-event-v2', {
        'campaign_id': campaign_id, 'action': event['action'],
        'revision': run['revision']}), 'Campaign fence key differs')
    run['last_event'] = receipt['digest']
    _put(state, 'campaign_run', run, True)
    return objects


def _stop_outcome(state, event, receipt, record, progress, stop_provider, replay=False,
                  db=None):
    """Stop-pending resolves to stopped only when the outcome verifies fully."""
    if not replay:
        require(stop_provider is not None, 'Unavailable',
                'Authenticated stop outcome is unavailable; stop-outcome refuses')
    _check(record['binding'] is None and record['leaf_plan'] is None,
           'Campaign stop-outcome rows differ')
    campaign_id = record['campaign_id']
    current = state['campaign_run'].get((campaign_id,))
    _check(current is not None and current['state'] == 'stop-pending',
           'Campaign stop-outcome state differs')
    _check(record['previous_revision'] == current['revision'],
           'Campaign stop-outcome previous revision differs')
    run = _row('campaign_run', record['run'], ('last_event',))
    if replay:
        terminal = run['result_object']
        _check(terminal is not None and len(record['evidence']) == 2
               and terminal in record['evidence'], 'Campaign stop-outcome evidence differs')
        kinds = {}
        for hashed in record['evidence']:
            value = _json(_durable_object(db, hashed))
            _check(type(value) is dict and type(value.get('schema')) is str,
                   'Campaign stop-outcome evidence object differs')
            kinds[value['schema']] = value
        _check(set(kinds) == {'capstone-campaign-manifest-v2',
                              'capstone-campaign-stop-v2'},
               'Campaign stop-outcome evidence roles differ')
        outcome = kinds['capstone-campaign-stop-v2']
        _check(digest(canonical(kinds['capstone-campaign-manifest-v2'])) == terminal,
               'Campaign stop-outcome manifest differs')
        verified = outcome.get('verified')
        _check(type(verified) is bool,
               'Campaign stop-outcome durable verification flag differs')
        _check(run['state'] in ('stopped', 'recovery-required'),
               'Campaign stop-outcome state differs')
        _check((run['state'] == 'stopped') is verified,
               'Campaign stop-outcome state contradicts durable evidence')
        objects = []
    else:
        manifest, terminal, outcome, verified = stop_provider(
            campaign_id, state, record['evidence'])
        _check(type(manifest) is dict
               and manifest.get('schema') == 'capstone-campaign-manifest-v2'
               and terminal == digest(canonical(manifest))
               and type(outcome) is dict and type(verified) is bool,
               'Campaign stop-outcome evidence differs')
        _check(outcome.get('verified') is verified,
               'Campaign stop-outcome verification flag differs')
        _check(record['evidence'] == sorted({digest(canonical(outcome)), terminal}),
               'Campaign stop-outcome evidence differs')
        objects = [canonical(outcome), canonical(manifest)]
    for column in ('campaign_id', 'campaign_operation_id', 'plan_hash', 'plan_raw',
                   'auth_hash', 'owner_epoch', 'intent_anchor'):
        _check(run[column] == current[column], 'Campaign stop-outcome immutable field differs')
    expected_state = 'stopped' if verified else 'recovery-required'
    expected_leaf = None if verified else current['active_leaf']
    _check(run['state'] == expected_state and run['active_leaf'] == expected_leaf
           and run['result_object'] == terminal
           and run['revision'] == current['revision'] + 1,
           'Campaign stop-outcome revision or run state differs')
    _check(event['idempotency_key'] == _domain('campaign-event-v2', {
        'campaign_id': campaign_id, 'action': event['action'],
        'revision': run['revision']}), 'Campaign stop-outcome key differs')
    run['last_event'] = receipt['digest']
    _put(state, 'campaign_run', run, True)
    return objects


def _finish(state, event, receipt, record, progress, manifest_provider, replay=False,
            db=None):
    """Complete only when every leaf advanced and a manifest provider exists."""
    if not replay:
        require(manifest_provider is not None, 'Unavailable',
                'Terminal manifest derivation is unavailable; finish refuses')
    _check(record['binding'] is None and record['leaf_plan'] is None,
           'Campaign finish rows differ')
    campaign_id = record['campaign_id']
    current = state['campaign_run'].get((campaign_id,))
    _check(current is not None and current['state'] == 'running'
           and current['active_leaf'] is None, 'Campaign finish state differs')
    _check(record['previous_revision'] == current['revision'],
           'Campaign finish previous revision differs')
    leaves = {row['leaf_index'] for row in state['leaf'].values()
              if row['campaign_id'] == campaign_id}
    completed = set((progress or {}).get(campaign_id, ()))
    _check(bool(leaves) and completed.issuperset(leaves),
           'Campaign finish before every leaf advanced')
    run = _row('campaign_run', record['run'], ('last_event',))
    if replay:
        terminal = run['result_object']
        _check(terminal is not None, 'Campaign finish has no terminal hash')
        manifest = _json(_durable_object(db, terminal))
        _check(type(manifest) is dict
               and manifest.get('schema') == 'capstone-campaign-manifest-v2'
               and manifest.get('campaign_plan_sha256') == current['plan_hash']
               and type(manifest.get('leaves')) is list
               and len(manifest['leaves']) == len(leaves)
               and digest(canonical(manifest)) == terminal,
               'Campaign finish durable manifest differs')
        _check(record['evidence'] == [terminal], 'Campaign finish evidence differs')
        objects = []
    else:
        manifest, terminal = manifest_provider(campaign_id, state, progress)
        _check(type(manifest) is dict
               and manifest.get('schema') == 'capstone-campaign-manifest-v2'
               and manifest.get('campaign_plan_sha256') == current['plan_hash']
               and type(manifest.get('leaves')) is list
               and len(manifest['leaves']) == len(leaves),
               'Campaign finish manifest differs')
        _check(terminal == digest(canonical(manifest)),
               'Campaign finish manifest digest differs')
        _check(record['evidence'] == [terminal], 'Campaign finish evidence differs')
        objects = [canonical(manifest)]
    for column in ('campaign_id', 'campaign_operation_id', 'plan_hash', 'plan_raw',
                   'auth_hash', 'owner_epoch', 'intent_anchor'):
        _check(run[column] == current[column], 'Campaign finish immutable field differs')
    _check(run['state'] == 'completed' and run['active_leaf'] is None
           and run['result_object'] == terminal
           and run['revision'] == current['revision'] + 1,
           'Campaign finish revision or run state differs')
    _check(event['idempotency_key'] == _domain('campaign-event-v2', {
        'campaign_id': campaign_id, 'action': event['action'],
        'revision': run['revision']}), 'Campaign finish key differs')
    run['last_event'] = receipt['digest']
    _put(state, 'campaign_run', run, True)
    return objects


def _advance(state, event, receipt, record, progress, advance_proof, replay=False):
    """Advance one leaf only with certified claim/exit/settlement proof."""
    if not replay:
        require(advance_proof is not None, 'Unavailable',
                'Claim/exit/settlement proof is unavailable; advance refuses')
    _check(record['binding'] is None and record['leaf_plan'] is None,
           'Campaign advance rows differ')
    campaign_id = record['campaign_id']
    current = state['campaign_run'].get((campaign_id,))
    _check(current is not None and current['state'] == 'running'
           and current['active_leaf'] is not None, 'Campaign advance state differs')
    _check(record['previous_revision'] == current['revision'],
           'Campaign advance previous revision differs')
    _check(len(record['evidence']) == 1, 'Campaign advance evidence differs')
    run = _row('campaign_run', record['run'], ('last_event',))
    for column in ('campaign_id', 'campaign_operation_id', 'plan_hash', 'plan_raw',
                   'auth_hash', 'owner_epoch', 'intent_anchor'):
        _check(run[column] == current[column], 'Campaign advance immutable field differs')
    _check(run['state'] == 'running' and run['active_leaf'] is None
           and run['result_object'] is None
           and run['revision'] == current['revision'] + 1,
           'Campaign advance revision or run state differs')
    _check(event['idempotency_key'] == _domain('campaign-event-v2', {
        'campaign_id': campaign_id, 'action': event['action'],
        'revision': run['revision']}), 'Campaign advance key differs')
    index = current['active_leaf']
    _check((campaign_id, index) in state['leaf_plan'],
           'Campaign advance leaf has no bound Plan')
    if not replay:
        advance_proof(campaign_id, index, record['evidence'][0], state)
    run['last_event'] = receipt['digest']
    _put(state, 'campaign_run', run, True)
    if progress is not None:
        progress.setdefault(campaign_id, {})[index] = record['evidence'][0]


def _select(state, event, receipt, record, progress, joins, live=None, replay=False):
    """First unfinished leaf; completion is certified by an injected verifier."""
    if not replay:
        require(joins is not None, 'Unavailable',
                'Campaign completion joins are unavailable; select refuses')
    _check(record['binding'] is None and record['leaf_plan'] is None,
           'Campaign select rows differ')
    campaign_id = record['campaign_id']
    current = state['campaign_run'].get((campaign_id,))
    _check(current is not None, 'Campaign select run is absent')
    _check(current['state'] == 'running' and current['active_leaf'] is None
           and current['result_object'] is None, 'Campaign select state differs')
    _check(record['previous_revision'] == current['revision'],
           'Campaign select previous revision differs')
    run = _row('campaign_run', record['run'], ('last_event',))
    for column in ('campaign_id', 'campaign_operation_id', 'plan_hash', 'plan_raw',
                   'auth_hash', 'owner_epoch', 'intent_anchor'):
        _check(run[column] == current[column], 'Campaign select immutable field differs')
    _check(run['state'] == 'running' and run['result_object'] is None
           and run['revision'] == current['revision'] + 1,
           'Campaign select revision or state differs')
    leaves = sorted(row['leaf_index'] for row in state['leaf'].values()
                    if row['campaign_id'] == campaign_id)
    _check(bool(leaves), 'Campaign select has no leaves')
    completed = dict((progress or {}).get(campaign_id, {}))
    unfinished = [index for index in leaves if index not in completed]
    _check(bool(unfinished), 'Campaign select has no unfinished leaf')
    selected = unfinished[0]
    _check(all(index in completed for index in leaves if index < selected),
           'Campaign select skipped an unfinished predecessor')
    _check(run['active_leaf'] == selected, 'Campaign select leaf differs')
    _check((campaign_id, selected) not in state['leaf_plan'],
           'Campaign select leaf already has a Plan')
    _check(receipt.get('digest') is not None, 'Campaign select receipt differs')
    _check(event['idempotency_key'] == _domain('campaign-event-v2', {
        'campaign_id': campaign_id, 'action': event['action'],
        'revision': run['revision']}), 'Campaign select key differs')
    _check(sorted(completed.values()) == record['evidence'],
           'Campaign select evidence differs from completed result refs')
    if not replay:
        joins(campaign_id, sorted(completed), state)
    run['last_event'] = receipt['digest']
    _put(state, 'campaign_run', run, True)


def _check(ok, message):
    require(ok, 'IntegrityFailure', message)


def _fields(value, names):
    _check(type(value) is dict and set(value) == set(names), 'Backend fields differ')


def _json(raw):
    _check(type(raw) is bytes and len(raw) <= MAX_RAW, 'Backend bytes bound/type')
    try:
        value = json.loads(raw, object_pairs_hook=unique_fields)
        _check(canonical(value) == raw, 'Noncanonical backend object')
        return value
    except (ValueError, TypeError, UnicodeError, RecursionError) as exc:
        raise Failure('IntegrityFailure', 'Invalid backend JSON') from exc


def _raw(value):
    _check(type(value) is str and len(value) <= MAX_RAW * 2, 'Raw encoding bound/type')
    try:
        result = base64.b64decode(value, validate=True)
    except (ValueError, TypeError) as exc:
        raise Failure('IntegrityFailure', 'Invalid base64') from exc
    _check(len(result) <= MAX_RAW and base64.b64encode(result).decode('ascii') == value,
           'Noncanonical raw encoding')
    return result


def _domain(tag, value):
    return digest(tag.encode('ascii') + b'\0' + canonical(value))


def _objects_dir(db):
    main = [row[2] for row in db.execute('PRAGMA database_list') if row[1] == 'main']
    _check(len(main) == 1 and main[0], 'Durable evidence database path is absent')
    return Path(main[0]).parent / 'objects'


def _durable_object(db, hashed):
    """Resolve a hash-addressed durable evidence object; never trust the event."""
    identifier(hashed, True)
    path = _objects_dir(db) / hashed
    _check(path.is_file() and not path.is_symlink(), 'Durable evidence object is absent')
    raw = path.read_bytes()
    _check(digest(raw) == hashed, 'Durable evidence object digest differs')
    return raw


def _store_object(db, raw):
    """Persist evidence bytes before the referencing event is appended."""
    _check(type(raw) is bytes and 0 < len(raw) <= MAX_RAW, 'Evidence object bytes differ')
    hashed = digest(raw)
    directory = _objects_dir(db)
    try:
        directory.mkdir(mode=0o700, exist_ok=True)
        path = directory / hashed
        if not path.exists():
            descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                                 0o600)
            try:
                os.write(descriptor, raw)
                os.fsync(descriptor)
            finally:
                os.close(descriptor)
            directory_fd = os.open(directory, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
            try:
                os.fsync(directory_fd)
            finally:
                os.close(directory_fd)
    except OSError as exc:
        raise Failure('RecoveryRequired', 'Evidence object could not be persisted') from exc
    return hashed


def _row(table, value, omitted=()):
    _fields(value, set(TABLE_COLUMNS[table]) - set(omitted))
    result = copy.deepcopy(value)
    nullable = {'bundle_raw', 'issued_anchor', 'stop_operation', 'stop_anchor',
                'active_leaf', 'result_object'}
    integers = {'leaf_index', 'epoch', 'stop_epoch', 'stopped', 'revision', 'active_leaf'}
    for column, item in result.items():
        if item is None:
            _check(column in nullable, 'Unexpected null backend column')
        elif column in BLOBS.get(table, ()):
            result[column] = _raw(item)
        elif column in integers:
            _check(type(item) is int and 0 <= item < 2**63, 'Invalid backend integer')
        else:
            _check(type(item) is str, 'Invalid backend text')
            identifier(item, column.endswith(('hash', 'anchor', 'epoch', 'event'))
                       or column in ('operation_id', 'grant_id', 'leaf_id', 'issuance_id',
                                     'plan_bytes_sha256', 'campaign_operation_id', 'result_object'))
    return result


def _key(table, row):
    return tuple(row[column] for column in PRIMARY_KEYS[table])


def _put(state, table, row, replace=False):
    key = _key(table, row)
    _check((key in state[table]) == replace, 'Duplicate or missing backend transition row')
    state[table][key] = row


def _spec(row):
    spec, auth = _json(row['spec_raw']), _json(row['auth_raw'])
    _fields(spec, ('schema', 'campaign_id', 'shared_bindings', 'policy', 'coverage',
                   'leaves', 'maximum', 'expires_ns'))
    _fields(auth, ('schema', 'action', 'operator_uid', 'campaign_spec_sha256',
                   'baseline_endorsement_sha256', 'installation_sha256', 'not_before_ns',
                   'expires_ns', 'maximum', 'leaf_ids', 'review_anchor'))
    _check(spec['schema'] == 'capstone-campaign-spec-v1'
           and auth['schema'] == 'capstone-authorization-v1'
           and auth['action'] == 'capstone-execute', 'Spec/authorization format differs')
    _check(digest(row['spec_raw']) == row['spec_hash'] == auth['campaign_spec_sha256']
           and digest(row['auth_raw']) == row['auth_hash']
           and row['campaign_id'] == spec['campaign_id'], 'Issuance raw hash bindings differ')
    from capstone_contract import _check as typed
    for field in ('campaign_spec_sha256', 'baseline_endorsement_sha256',
                  'installation_sha256', 'review_anchor'):
        typed(auth[field], 'H')
    for field in ('not_before_ns', 'expires_ns'):
        typed(auth[field], 'N')
    typed(auth['operator_uid'], 'U')
    typed(spec['maximum'], 'Vector')
    typed(spec['expires_ns'], 'N')
    _check(auth['maximum'] == spec['maximum'] and auth['not_before_ns'] < auth['expires_ns']
           <= spec['expires_ns'], 'Authorization bounds differ')
    leaves = spec['leaves']
    _check(type(leaves) is list and 1 <= len(leaves) <= 256, 'Finite leaf set differs')
    skeleton_leaves = []
    for index, leaf in enumerate(leaves):
        _fields(leaf, ('index', 'leaf_id', 'pair_id', 'purpose', 'challenge', 'role', 'attempt',
                       'request', 'invocation_raw', 'maximum', 'predecessor'))
        _check(type(leaf['index']) is int and leaf['index'] == index, 'Leaf order differs')
        typed(leaf['pair_id'], 'H')
        typed(leaf['challenge'], 'I')
        typed(leaf['attempt'], 'N')
        typed(leaf['maximum'], 'Vector')
        _check(leaf['purpose'] in ('corpus', 'replay') and leaf['role'] in ('baseline', 'candidate'),
               'Leaf enum differs')
        _check(leaf['predecessor'] is None or (type(leaf['predecessor']) is int
               and 0 <= leaf['predecessor'] < index), 'Leaf predecessor differs')
        validate_record(leaf['request'], 'Request')
        _check(leaf['leaf_id'] == _domain('campaign-leaf-v1',
               {k: v for k, v in leaf.items() if k != 'leaf_id'}), 'Leaf hash differs')
        skeleton_leaves.append(dict({k: leaf[k] for k in ('index', 'pair_id', 'purpose', 'challenge',
                                   'role', 'attempt', 'maximum', 'predecessor')},
                                   run=leaf['request']['run']))
    skeleton = dict({k: spec[k] for k in ('campaign_id', 'shared_bindings', 'policy',
                                         'coverage', 'maximum', 'expires_ns')},
                    schema='capstone-campaign-skeleton-v1', leaves=skeleton_leaves)
    skeleton_hash = _domain('campaign-skeleton-v1', skeleton)
    for leaf in leaves:
        request = leaf['request']
        invocation = _raw(leaf['invocation_raw'])
        scope = _domain('leaf-scope-v1', {'skeleton': skeleton_hash, 'index': leaf['index']})
        _check(request['scope'] == scope and request['maximum'] == leaf['maximum']
               and invocation == canonical(dict(run=request['run'], scope=scope, maximum=leaf['maximum']))
               and request['bindings'] == dict(spec['shared_bindings'], invocation_bytes_sha256=digest(invocation)),
               'Leaf request/invocation bindings differ')
    _check(spec['shared_bindings']['policy'] == spec['policy'], 'Policy binding differs')
    typed(spec['coverage'], 'H')
    for field in ('money_cents', 'execution_us', 'review_us'):
        _check(spec['maximum'][field] == sum(leaf['maximum'][field] for leaf in leaves),
               'Finite maximum differs')
    _check(auth['leaf_ids'] == [leaf['leaf_id'] for leaf in leaves]
           and len(set(auth['leaf_ids'])) == len(leaves)
           and len({leaf['request']['run'] for leaf in leaves}) == len(leaves), 'Finite identities differ')
    return spec, auth


def _base(state, event, receipt, grants):
    action, records = event['action'], event['record']
    _check(type(records) is list and len(records) <= 3, 'Backend row groups differ')
    groups = {}
    for group in records:
        _fields(group, ('table', 'rows'))
        name = group['table']
        _check(type(name) is str and name.startswith(PREFIX), 'Backend table namespace differs')
        name = name[len(PREFIX):]
        _check(name in TABLE_COLUMNS and name not in groups and type(group['rows']) is list,
               'Backend table inventory differs')
        groups[name] = group['rows']
    if action == 'issuance-intent':
        _check(set(groups) == {'issuance'} and len(groups['issuance']) == 1, 'Intent rows differ')
        row = _row('issuance', groups['issuance'][0], ('intent_anchor',))
        _check(row['phase'] == 'intent' and row['bundle_raw'] is None and row['issued_anchor'] is None,
               'Intent phase differs')
        _spec(row)
        _check(event['idempotency_key'] == _domain('issue-intent-v1', {'authorization': row['auth_hash']}),
               'Intent key differs')
        _check(not any(r['campaign_id'] == row['campaign_id'] or r['issuance_id'] == row['issuance_id']
                       for r in state['issuance'].values()), 'Duplicate issuance identity')
        row['intent_anchor'] = receipt['digest']
        _put(state, 'issuance', row)
    elif action == 'issuance-commit':
        _check(set(groups) == {'issuance', 'campaign', 'leaf'} and len(groups['issuance']) == 1
               and len(groups['campaign']) == 1, 'Commit rows differ')
        row = _row('issuance', groups['issuance'][0], ('issued_anchor',))
        old = state['issuance'].get((row['auth_hash'],))
        _check(old is not None and old['phase'] == 'intent', 'Commit missing original intent')
        _check(all(row[c] == old[c] for c in TABLE_COLUMNS['issuance'][:8])
               and row['phase'] == 'issued' and row['bundle_raw'] is not None, 'Commit changed original issuance')
        spec, auth = _spec(row)
        bundle = _json(row['bundle_raw'])
        _fields(bundle, ('schema', 'campaign_spec_sha256', 'grants'))
        _check(bundle['schema'] == 'capstone-grant-bundle-v1'
               and bundle['campaign_spec_sha256'] == row['spec_hash']
               and type(bundle['grants']) is list
               and len(bundle['grants']) == len(groups['leaf']) == len(spec['leaves']), 'Bundle cardinality differs')
        campaign = _row('campaign', groups['campaign'][0])
        _check(campaign == dict(campaign_id=row['campaign_id'], issuance_id=row['issuance_id'],
               control_run=_domain('campaign-control-v1', {'issuance_id': row['issuance_id'], 'campaign_id': row['campaign_id']}),
               stop_epoch=0, stopped=0, stop_operation=None, stop_anchor=None), 'Initial campaign differs')
        _check(event['idempotency_key'] == _domain('issue-commit-v1', {'authorization': row['auth_hash']}),
               'Commit key differs')
        for leaf, entry, encoded in zip(spec['leaves'], bundle['grants'], groups['leaf']):
            _fields(entry, ('leaf_id', 'grant_raw'))
            raw = _raw(entry['grant_raw'])
            grant = decode_record(raw, 'Grant')
            gid = _domain('issued-leaf-grant-v1', dict(issuance_id=row['issuance_id'],
                         authorization=row['auth_hash'], spec=row['spec_hash'], leaf_id=leaf['leaf_id']))
            _check(grant['grant_id'] == gid and entry['leaf_id'] == leaf['leaf_id']
                   and grant['authorization_bytes_sha256'] == row['auth_hash']
                   and grant['operator_uid'] == auth['operator_uid']
                   and grant['issuance_anchor'] == row['intent_anchor']
                   and grant['review_anchor'] == auth['review_anchor']
                   and grant['bindings'] == leaf['request']['bindings']
                   and grant['bounds']['scope'] == leaf['request']['scope']
                   and grant['bounds']['maximum'] == leaf['maximum']
                   and grant['bounds']['not_before_ns'] == auth['not_before_ns']
                   and grant['bounds']['expires_ns'] == auth['expires_ns'], 'Grant bindings differ')
            expected_grant = (gid, raw, digest(raw), row['auth_hash'], auth['operator_uid'])
            _check(gid not in grants, 'Duplicate issued grant')
            grants[gid] = expected_grant
            leaf_row = _row('leaf', encoded)
            _check(leaf_row == dict(campaign_id=row['campaign_id'], leaf_index=leaf['index'],
                   leaf_id=leaf['leaf_id'], grant_id=gid, request_run=leaf['request']['run'],
                   request_hash=digest(canonical(leaf['request']))), 'Leaf row differs')
            _put(state, 'leaf', leaf_row)
        row['issued_anchor'] = receipt['digest']
        _put(state, 'issuance', row, True)
        _put(state, 'campaign', campaign)
    else:
        raise Failure('Unavailable', 'Backend action not implemented: ' + str(action))


def _stop_rows(state, receipt, extension):
    _fields(extension, ('schema', 'campaign_id', 'control_run', 'epoch', 'primary_operation',
                         'affected_operations', 'run_before_revision', 'run_after'))
    _check(extension['schema'] == 'capstone-campaign-stop-v2', 'Stop schema differs')
    campaign = state['campaign'].get((extension['campaign_id'],))
    _check(campaign is not None and campaign['control_run'] == extension['control_run']
           and type(extension['epoch']) is int and extension['epoch'] == 1, 'Stop campaign differs')
    identifier(extension['primary_operation'], True)
    grants = {r['grant_id'] for r in state['leaf'].values() if r['campaign_id'] == campaign['campaign_id']}
    operations = sorted(r['operation_id'] for r in state['binding'].values() if r['grant_id'] in grants)
    _check(extension['affected_operations'] == operations, 'Stop binding coverage differs')
    first = campaign['stopped'] == 0
    if first:
        campaign.update(stopped=1, stop_epoch=1, stop_operation=extension['primary_operation'], stop_anchor=receipt['digest'])
    else:
        _check(campaign['stop_operation'] == extension['primary_operation'], 'Stop primary differs')
    run = state['campaign_run'].get((campaign['campaign_id'],))
    if run is None:
        _check(extension['run_before_revision'] is None and extension['run_after'] is None, 'Invented stopped run')
    else:
        _check(type(extension['run_before_revision']) is int and extension['run_before_revision'] == run['revision'],
               'Stop previous revision differs')
        if first and run['state'] == 'running':
            expected = dict(run, state='stop-pending', revision=run['revision'] + 1, last_event=receipt['digest'])
            after = _row('campaign_run', extension['run_after'], ('last_event',))
            after['last_event'] = receipt['digest']
            _check(after == expected, 'Stop changed run identity/progress')
            state['campaign_run'][(campaign['campaign_id'],)] = after
        else:
            _check(_row('campaign_run', extension['run_after']) == run, 'Repeat/terminal stop changed run')
    _check(not state['projection'], 'Projection stop reducer is not yet implemented')


def _snapshot(db):
    return {table: {_key(table, dict(zip(columns, row))): dict(zip(columns, row))
                    for row in db.execute('SELECT ' + ','.join(columns) + ' FROM ' + PREFIX + table)}
            for table, columns in TABLE_COLUMNS.items()}


def _validate(db, tentative=None):
    validate_schema(db)
    state = {table: {} for table in TABLE_COLUMNS}
    grants, keys, prior, progress = {}, {}, '0' * 64, {}
    events = db.execute('SELECT seq,prior,hash,body FROM events ORDER BY seq').fetchall()
    for sequence, (seq, parent, hashed, raw) in enumerate(events, 1):
        _check(type(raw) is bytes and seq == sequence and parent == prior
               and hashed == digest(prior.encode() + raw), 'Backend core chain differs')
        event = _json(raw)
        _check(type(event) is dict, 'Backend envelope differs')
        expected_version = 2 if event.get('format') == CAMPAIGN_FORMAT else 1
        _check('idempotency_key' in event and type(event.get('version')) is int
               and event['version'] == expected_version, 'Backend envelope version differs')
        key = identifier(event['idempotency_key'])
        _check(key not in keys, 'Duplicate ledger key')
        keys[key] = (seq, parent, hashed, raw)
        prior = hashed
        if tentative is not None and seq == tentative:
            _check(seq == len(events), 'Tentative event not final')
            continue
        fmt = event.get('format', '')
        receipt = dict(sequence=seq, prior=parent, digest=hashed)
        if fmt in (BASE_FORMAT, CAMPAIGN_FORMAT):
            _fields(event, ('format', 'action', 'record', 'idempotency_key', 'version'))
            if fmt == BASE_FORMAT:
                _base(state, event, receipt, grants)
            else:
                _campaign(state, event, receipt, grants, progress, replay=True, db=db)
        elif type(fmt) is str and (fmt.startswith('capstone-backend-') or fmt.startswith('capstone-campaign-')):
            raise Failure('IntegrityFailure', 'Unknown backend event format')
        elif 'backend_stop' in event:
            _check(event.get('kind') in ('safe-stop', 'safe-stop-reference'), 'Backend stop in unknown envelope')
            extension = event['backend_stop']
            _check(event.get('run') == extension.get('control_run')
                   and event.get('epoch') == extension.get('epoch')
                   and (event.get('operation') if event['kind'] == 'safe-stop'
                        else event.get('primary_operation')) == extension.get('primary_operation'),
                   'Stop core linkage differs')
            _stop_rows(state, receipt, event['backend_stop'])
    actual_keys = {r[0]: tuple(r[1:]) for r in db.execute('SELECT key,seq,prior,hash,body FROM idempotency')}
    _check(keys == actual_keys, 'Backend idempotency rows differ')
    _check(state == _snapshot(db), 'Backend full-row replay differs')
    from capstone_journal import _validate as validate_journal
    validate_journal(db, tentative)
    for oid, gid in db.execute('SELECT operation_id,grant_id FROM capstone_operations'):
        if any(leaf['grant_id'] == gid for leaf in state['leaf'].values()):
            _check((oid,) in state['binding'], 'Campaign claim has no prior backend binding')
    actual_grants = {r[0]: tuple(r[:5]) for r in db.execute('SELECT * FROM capstone_grants')}
    _check(set(actual_grants) == set(grants), 'Backend grant cardinality differs')
    for gid, expected in grants.items():
        _check(actual_grants.get(gid) == expected, 'Issued original grant row differs')
    return state, grants, prior, len(events), progress


def _write_delta(db, before, after):
    for table in TABLE_COLUMNS:
        columns = TABLE_COLUMNS[table]
        for key, row in after[table].items():
            old = before[table].get(key)
            if old is None:
                db.execute('INSERT INTO ' + PREFIX + table + '(' + ','.join(columns) + ') VALUES('
                           + ','.join('?' for _ in columns) + ')', tuple(row[c] for c in columns))
            elif old != row:
                changed = [c for c in columns if row[c] != old[c]]
                db.execute('UPDATE ' + PREFIX + table + ' SET ' + ','.join(c + '=?' for c in changed)
                           + ' WHERE ' + ' AND '.join(c + '=?' for c in PRIMARY_KEYS[table]),
                           tuple(row[c] for c in changed) + key)


def apply_backend_stop(db, receipt, backend_stop):
    """SQL-only subordinate hook. Caller owns the existing stop transaction.

    No BEGIN, append, Journal call, object IO, or cancellation occurs here.
    Full safe-stop envelope/prefix verification belongs to the caller/replay.
    """
    _check(db.in_transaction, 'Backend stop requires caller transaction')
    _fields(receipt, ('sequence', 'prior', 'digest'))
    identifier(receipt['digest'], True)
    event_row = db.execute('SELECT prior,hash,body FROM events WHERE seq=?', (receipt['sequence'],)).fetchone()
    _check(event_row is not None and event_row[:2] == (receipt['prior'], receipt['digest']),
           'Stop receipt is not the tentative ledger event')
    event = _json(event_row[2])
    _check(event.get('kind') in ('safe-stop', 'safe-stop-reference')
           and event.get('backend_stop') == backend_stop, 'Stop hook payload differs from durable event')
    _check(event.get('run') == backend_stop.get('control_run')
           and event.get('epoch') == backend_stop.get('epoch')
           and (event.get('operation') if event['kind'] == 'safe-stop'
                else event.get('primary_operation')) == backend_stop.get('primary_operation'),
           'Stop hook core linkage differs')
    before = _validate(db, receipt['sequence'])[0]
    after = copy.deepcopy(before)
    _stop_rows(after, receipt, backend_stop)
    _write_delta(db, before, after)


class BackendIndex:
    def __init__(self, ledger, token):
        require(token is _OPEN and isinstance(ledger, Ledger), 'Unauthorized', 'Use backend factory')
        self._ledger = ledger
        # Issuer-invocation continuity only. Never reconstructed from durable intent,
        # and never an execution capability. Reopening an intent cannot mint grants.
        self._owned_intents = set()
        self.validate()

    def validate(self):
        """Return detached index data only; never a permit or live owner capability."""
        with self._ledger.lock:
            db = self._ledger.db
            own_snapshot = not db.in_transaction
            if own_snapshot:
                db.execute('BEGIN')
            try:
                return copy.deepcopy(_validate(db)[0])
            finally:
                if own_snapshot:
                    db.rollback()

    def append_transition(self, action, record, key):
        """Trusted source-caller seam. Coherence is not approval or current authority."""
        event = dict(format=BASE_FORMAT, action=action, record=copy.deepcopy(record))
        ledger = self._ledger
        with ledger.lock:
            _validate(ledger.db)
            cached = ledger.db.execute('SELECT seq,prior,hash,body FROM idempotency WHERE key=?', (key,)).fetchone()
            if cached is not None:
                _check(cached[3] == canonical(dict(event, version=1, idempotency_key=key)), 'Changed cached backend event')
                return dict(sequence=cached[0], prior=cached[1], digest=cached[2])
            if action == 'issuance-commit':
                _check(type(record) is list and len(record) == 3, 'Commit row inventory differs')
                issuance_groups = [g for g in record if type(g) is dict and g.get('table') == PREFIX + 'issuance']
                _check(len(issuance_groups) == 1 and type(issuance_groups[0].get('rows')) is list
                       and len(issuance_groups[0]['rows']) == 1, 'Commit issuance row differs')
                auth_hash = issuance_groups[0]['rows'][0].get('auth_hash')
                require(auth_hash in self._owned_intents, 'RecoveryRequired',
                        'Intent belongs to a lost/different issuer invocation')
            prior = ledger.tip()
            def apply(db, receipt):
                before, old_grants, _, _, _ = _validate(db, receipt['sequence'])
                after, grants = copy.deepcopy(before), dict(old_grants)
                _base(after, dict(event, version=1, idempotency_key=key), receipt, grants)
                for gid, row in grants.items():
                    if gid not in old_grants:
                        db.execute('INSERT INTO capstone_grants VALUES(?,?,?,?,?,NULL)', row)
                _write_delta(db, before, after)
                _validate(db)
            result = ledger.append_atomic(EVALUATOR, event, prior, key, apply)
            if action == 'issuance-intent':
                self._owned_intents.add(record[0]['rows'][0]['auth_hash'])
            elif action == 'issuance-commit':
                self._owned_intents.discard(auth_hash)
            return result

    def append_campaign(self, action, record, key, *, joins=None, live=None,
                        advance_proof=None, manifest_provider=None,
                        fence_provider=None, stop_provider=None):
        """Append one campaign-v2 event; every unverified action still refuses."""
        _check(action in CAMPAIGN_ACTIONS, 'Unknown campaign action')
        event = dict(format=CAMPAIGN_FORMAT, action=action, record=copy.deepcopy(record))
        ledger = self._ledger
        with ledger.lock:
            _validate(ledger.db)
            cached = ledger.db.execute(
                'SELECT seq,prior,hash,body FROM idempotency WHERE key=?', (key,)).fetchone()
            if cached is not None:
                _check(cached[3] == canonical(dict(event, version=2, idempotency_key=key)),
                       'Changed cached campaign event')
                return dict(sequence=cached[0], prior=cached[1], digest=cached[2])
            prior = ledger.tip()

            def apply(db, receipt):
                before, old_grants, _, _, progress = _validate(db, receipt['sequence'])
                after, grants = copy.deepcopy(before), dict(old_grants)
                objects = _campaign(after, dict(event, version=2, idempotency_key=key),
                                    receipt, grants, progress, joins, live,
                                    advance_proof, manifest_provider, fence_provider,
                                    stop_provider, db=db)
                for raw in objects:
                    _store_object(db, raw)
                _write_delta(db, before, after)
                _validate(db)

            return ledger.append_atomic(EVALUATOR, event, prior, key, apply, version=2)


def open_existing(ledger):
    require(os.getuid() == EVALUATOR, 'Unauthorized', 'Actual evaluator UID required')
    return BackendIndex(ledger, _OPEN)


def open_public_fixture(ledger, directory, *, create=False):
    """Explicit NONPRODUCTION private-temp fixture; no UID spoofing."""
    uid = os.getuid()
    require(uid not in (0, 320, 321, 322), 'Unauthorized', 'Unprivileged fixture UID required')
    require(type(directory) is type(Path()) and directory.parent == Path('/private/tmp')
            and directory.is_absolute() and '..' not in directory.parts
            and directory.name.startswith(('grrr-backend-fixture-', 'capstone-journal-fixture-')),
            'InvalidInput', 'Fixture path rejected before metadata access')
    info = directory.lstat()
    require(stat.S_ISDIR(info.st_mode) and info.st_uid == uid and stat.S_IMODE(info.st_mode) == 0o700,
            'Unauthorized', 'Fixture directory is not private')
    require(isinstance(ledger, Ledger) and type(create) is bool, 'InvalidInput', 'Invalid fixture handle/flag')
    paths = ledger.db.execute('PRAGMA database_list').fetchall()
    require([r[2] for r in paths if r[1] == 'main'] == [str(directory / 'ledger.sqlite')],
            'InvalidInput', 'Fixture DB path differs')
    require(not (directory / 'ledger.sqlite').is_symlink(), 'InvalidInput', 'Fixture database symlink')
    if create:
        require(not ledger.db.in_transaction, 'InvalidInput', 'Fixture creation inside transaction')
        try:
            ledger.db.execute('BEGIN IMMEDIATE')
            for sql in BACKEND_SQL:
                ledger.db.execute(sql)
            validate_schema(ledger.db)
            ledger.db.commit()
        except BaseException:
            ledger.db.rollback()
            raise
    return BackendIndex(ledger, _OPEN)
