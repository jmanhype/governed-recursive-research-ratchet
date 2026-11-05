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

from common import EVALUATOR, Failure, canonical, digest, identifier, require, unique_fields
from ledger import Ledger
from capstone_contract import decode_record, validate_record, operation_id, content_digest
from capstone_backend_schema import (BACKEND_SQL, BLOBS, PREFIX, PRIMARY_KEYS,
                                     TABLE_COLUMNS, validate_schema)

BASE_FORMAT = 'capstone-backend-event-v1'
CAMPAIGN_FORMAT = 'capstone-campaign-event-v2'
CAMPAIGN_ACTIONS = ('campaign-start', 'campaign-select', 'campaign-leaf-bind',
                    'campaign-advance', 'campaign-finish', 'campaign-fence',
                    'campaign-stop-outcome')
_OPEN = object()
MAX_RAW = 16 * 1024 * 1024


def _campaign(state, event, receipt, grants):
    """Campaign-v2 reducer entry; unimplemented actions refuse, never accept."""
    _fields(event, ('format', 'action', 'record', 'idempotency_key', 'version'))
    record = event['record']
    _fields(record, ('campaign_id', 'previous_revision', 'run', 'binding',
                     'leaf_plan', 'evidence'))
    action = event['action']
    _check(action in CAMPAIGN_ACTIONS, 'Unknown campaign action')
    identifier(record['campaign_id'], True)
    evidence = record['evidence']
    _check(type(evidence) is list and evidence == sorted(set(evidence))
           and all(type(item) is str and len(item) == 64 for item in evidence),
           'Campaign evidence is unsorted, duplicated or malformed')
    previous = record['previous_revision']
    _check(previous is None or (type(previous) is int and previous >= 0),
           'Campaign previous revision differs')
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
    grants, keys, prior = {}, {}, '0' * 64
    events = db.execute('SELECT seq,prior,hash,body FROM events ORDER BY seq').fetchall()
    for sequence, (seq, parent, hashed, raw) in enumerate(events, 1):
        _check(type(raw) is bytes and seq == sequence and parent == prior
               and hashed == digest(prior.encode() + raw), 'Backend core chain differs')
        event = _json(raw)
        _check(type(event) is dict and 'idempotency_key' in event and type(event.get('version')) is int
               and event['version'] == 1, 'Backend envelope version differs')
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
                _campaign(state, event, receipt, grants)
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
    return state, grants, prior, len(events)


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
                before, old_grants, _, _ = _validate(db, receipt['sequence'])
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
