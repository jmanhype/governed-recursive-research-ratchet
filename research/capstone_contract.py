"""Source-only consistency checks. A valid record is NEVER issued authority."""
import json
import re
from typing import Any, Dict
from common import Failure, GATES, MAX_WIRE, canonical, digest, identifier, require, unique_fields

CODES = ('Unauthorized', 'InvalidInput', 'StaleBinding', 'GateBlocked', 'BudgetUnknown',
         'BudgetExceeded', 'Stopped', 'IntegrityFailure', 'Unavailable', 'RecoveryRequired')
STATES = ('claimed', 'reserved', 'dispatch-pending', 'running', 'stop-pending',
          'completed', 'stopped', 'recovery-required')
SCHEMAS: Dict[str, Any] = {
    'Vector': dict(currency=('USD',), money_cents='N', execution_us='N', review_us='N'),
    'DecisionBinding': dict(request_id='I', reviewed_package_commit='C',
        decision_json_bytes_sha256='H', decision_markdown_bytes_sha256='H', output_root='Rel'),
    'Bindings': dict(driver_commit='C', driver_inventory='H', runtime_base='C',
        runtime_inventory='H', evaluator_inventory='H', runner_inventory='H', interpreter='H',
        bootstrap='H', qemu='H', vm_assets='H', corpus='H', replay_catalog='H', replay_image='H',
        execution_profile='H', policy='H', accounting_binding='H', accounting_version='N',
        decision='DecisionBinding', invocation_bytes_sha256='H'),
    'Bounds': dict(maximum='Vector', stage=('poc',), scope='H', floors='H',
        not_before_ns='N', expires_ns='N', receipt_max_age_ns='N'),
    'Grant': dict(schema=('capstone-grant-v1',), grant_id='H', operator_uid='U',
        authorization_bytes_sha256='H', bindings='Bindings', bounds='Bounds',
        review_anchor='H', issuance_anchor='H'),
    'Request': dict(schema=('capstone-request-v1',), run='I', bindings='Bindings',
        scope='H', maximum='Vector'),
    'Anchor': dict(ledger_sequence='N', ledger_tip='H', accounting_snapshot='H',
        grant_registry_snapshot='H', installation='H'),
    'Accounting': dict(version='?N', stopped='?B', history=('verified', 'unknown'),
        spendable='?Vector', held='?Vector'),
    'Receipt': dict(schema=('capstone-observation-v1',), nonce='H', operator_uid='U',
        grant_id='H', grant_bytes_sha256='H', authorization_bytes_sha256='H', bindings='Bindings',
        observed_ns='N', service_epoch='H', anchor='?Anchor', accounting='Accounting',
        capability=('unsupported', 'observe-only', 'start-capable'),
        grant_state=('unissued', 'available', 'consumed', 'unknown'), blockers='Codes', receipt_sha256='H'),
    'Gate': dict(state=('pass', 'fail', 'not-run', 'error'), evidence='?H', reason='?Code'),
    'Plan': dict(schema=('capstone-plan-v1',), request='Request', grant='Grant',
        grant_bytes_sha256='H', authorization_bytes_sha256='H', observation='Receipt',
        gates='Gates', plan_sha256='H'),
    'Operation': dict(schema=('capstone-operation-v1',), operation_id='H', grant_id='H',
        plan_sha256='H', start_request_sha256='H', state=STATES, reservation='?H',
        dispatch=('not-run', 'pending', 'completed', 'unknown'), gates='Gates', anchor='Anchor',
        stop_requested='B', result_object='?H', blockers='Codes'),
    'Manifest': dict(schema=('capstone-manifest-v1',), plan_sha256='H', operation_id='H',
        operation='?Operation', transport=('ok', 'unknown', 'refused'), gates='Gates'),
    'Invocation': dict(run='I', scope='H', maximum='Vector'),
    'Observe': dict(action=('observe',), version=(1,), nonce='H', request='Request',
        authorization_bytes_sha256='H', grant_id='H'),
    'Start': dict(action=('start',), version=(1,), plan='Plan', operation_id='H'),
    'Status': dict(action=('status',), version=(1,), operation_id='H', nonce='H'),
    'Stop': dict(action=('stop',), version=(1,), operation_id='H'),
}


def _check(value: Any, spec: Any, depth: int = 0) -> None:
    require(depth < 40, 'InvalidInput', 'Record nesting exceeds bound')
    if isinstance(spec, tuple):
        require(any(type(value) is type(x) and value == x for x in spec),
                'InvalidInput', 'Invalid enum')
    elif isinstance(spec, dict):
        require(type(value) is dict and set(value) == set(spec), 'InvalidInput', 'Fields differ')
        for key, child in spec.items():
            _check(value[key], child, depth + 1)
    elif spec.startswith('?'):
        if value is not None:
            _check(value, spec[1:], depth + 1)
    elif spec in SCHEMAS:
        _check(value, SCHEMAS[spec], depth + 1)
        _relations(value, spec)
    elif spec == 'Gates':
        _check(value, {key: 'Gate' for key in GATES}, depth + 1)
    elif spec == 'Codes':
        require(type(value) is list and len(value) <= 64, 'InvalidInput', 'Invalid blockers')
        for item in value:
            _check(item, 'Code', depth + 1)
    elif spec == 'Code':
        _check(value, CODES, depth + 1)
    elif spec in ('N', 'U'):
        require(type(value) is int and value >= 0, 'InvalidInput', 'Invalid integer')
        if spec == 'U':
            require(0 < value < 4294967295 and value not in (320, 321), 'InvalidInput', 'Invalid operator UID')
    elif spec == 'B':
        require(type(value) is bool, 'InvalidInput', 'Invalid boolean')
    elif spec in ('H', 'C'):
        require(type(value) is str and re.fullmatch('[0-9a-f]{%d}' % (64 if spec == 'H' else 40), value)
                is not None, 'InvalidInput', 'Invalid digest or commit')
    elif spec == 'I':
        identifier(value)
    elif spec == 'Rel':
        require(type(value) is str and 0 < len(value) <= 4096 and value.isascii()
                and all(32 <= ord(c) < 127 for c in value) and '\\' not in value
                and all(x not in ('', '.', '..') for x in value.split('/')),
                'InvalidInput', 'Unsafe relative path')
    else:
        raise Failure('InvalidInput', 'Unknown record kind')


def content_digest(value: dict, field: str) -> str:
    """Hash canonical content excluding exactly the named self-digest."""
    require(type(value) is dict and field in ('receipt_sha256', 'plan_sha256') and field in value,
            'InvalidInput', 'Unknown self digest')
    return digest(canonical({k: v for k, v in value.items() if k != field}))


def operation_id(grant_id: str, plan_sha256: str) -> str:
    _check(grant_id, 'H')
    _check(plan_sha256, 'H')
    return digest(canonical(dict(grant_id=grant_id, plan_sha256=plan_sha256)))


def _relations(v: dict, kind: str) -> None:
    if kind == 'Bounds':
        require(v['expires_ns'] > v['not_before_ns'], 'InvalidInput', 'Empty grant window')
    if kind in ('Receipt', 'Plan'):
        key = 'receipt_sha256' if kind == 'Receipt' else 'plan_sha256'
        require(v[key] == content_digest(v, key), 'IntegrityFailure', 'Self digest differs')
    if kind == 'Accounting' and v['history'] == 'unknown':
        require(v['spendable'] is None, 'InvalidInput', 'Unknown history is not spendable')
    if kind == 'Plan':
        g, r, o = v['grant'], v['request'], v['observation']
        require(g['bindings'] == r['bindings'] == o['bindings']
                and g['bounds']['scope'] == r['scope'] and g['bounds']['maximum'] == r['maximum']
                and g['grant_id'] == o['grant_id'] and g['operator_uid'] == o['operator_uid']
                and g['authorization_bytes_sha256'] == v['authorization_bytes_sha256'] == o['authorization_bytes_sha256']
                and v['grant_bytes_sha256'] == o['grant_bytes_sha256'], 'StaleBinding', 'Plan bindings differ')
    if kind == 'Operation':
        require(v['operation_id'] == operation_id(v['grant_id'], v['plan_sha256']), 'StaleBinding', 'Operation identity differs')
    if kind == 'Start':
        p = v['plan']
        require(v['operation_id'] == operation_id(p['grant']['grant_id'], p['plan_sha256']),
                'StaleBinding', 'Start identity differs')
    if kind == 'Manifest' and v['operation'] is not None:
        require(all(v[k] == v['operation'][k] for k in ('plan_sha256', 'operation_id', 'gates')),
                'StaleBinding', 'Manifest differs from operation')


def validate_record(value: dict, kind: str) -> dict:
    """Validate bounded exact structure and internal consistency, NOT provenance."""
    require(type(kind) is str and kind in SCHEMAS, 'InvalidInput', 'Unknown record kind')
    try:
        _check(value, kind)
        require(len(canonical(value)) <= MAX_WIRE, 'InvalidInput', 'Record exceeds cap')
    except (ValueError, TypeError, RecursionError, OverflowError) as exc:
        raise Failure('InvalidInput', 'Malformed record') from exc
    return value


def decode_record(raw: bytes, kind: str) -> dict:
    require(type(raw) is bytes and 0 < len(raw) <= MAX_WIRE, 'InvalidInput', 'Invalid byte bound')
    try:
        value = json.loads(raw, object_pairs_hook=unique_fields,
                           parse_constant=lambda x: (_ for _ in ()).throw(ValueError(x)))
    except (ValueError, UnicodeError, RecursionError) as exc:
        raise Failure('InvalidInput', 'Malformed JSON') from exc
    return validate_record(value, kind)


def verify_bytes(raw: bytes, expected: str) -> None:
    _check(expected, 'H')
    require(type(raw) is bytes and 0 < len(raw) <= MAX_WIRE, 'InvalidInput', 'Invalid byte bound')
    require(digest(raw) == expected, 'IntegrityFailure', 'Original byte digest differs')


def bind_inputs(request: dict, invocation_raw: bytes, decision_json_raw: bytes,
                decision_markdown_raw: bytes, *, request_id: str,
                reviewed_package_commit: str, output_root: str) -> None:
    """Compare caller-provided bytes/context; no Git/protected provenance attestation."""
    validate_record(request, 'Request')
    b, d = request['bindings'], request['bindings']['decision']
    _check(request_id, 'I')
    _check(reviewed_package_commit, 'C')
    _check(output_root, 'Rel')
    verify_bytes(invocation_raw, b['invocation_bytes_sha256'])
    require(decode_record(invocation_raw, 'Invocation') == {k: request[k] for k in ('run', 'scope', 'maximum')},
            'StaleBinding', 'Invocation differs')
    verify_bytes(decision_json_raw, d['decision_json_bytes_sha256'])
    verify_bytes(decision_markdown_raw, d['decision_markdown_bytes_sha256'])
    require(d['request_id'] == request_id and d['reviewed_package_commit'] == reviewed_package_commit
            and d['output_root'] == output_root, 'StaleBinding', 'Decision context differs')


def bind_grant(plan: dict, grant_raw: bytes, authorization_raw: bytes, *, operator_uid: int) -> None:
    """Raw-byte equality only: a counterfeit consistent grant still has NO authority."""
    validate_record(plan, 'Plan')
    _check(operator_uid, 'U')
    verify_bytes(grant_raw, plan['grant_bytes_sha256'])
    require(decode_record(grant_raw, 'Grant') == plan['grant'] and plan['grant']['operator_uid'] == operator_uid,
            'StaleBinding', 'Grant context differs')
    verify_bytes(authorization_raw, plan['authorization_bytes_sha256'])


def start_request_digest(request: dict) -> str:
    validate_record(request, 'Start')
    return digest(canonical(request))


def bind_observation(plan: dict, *, nonce: str, service_epoch: str, anchor: dict,
                     now_ns: int, operator_uid: int) -> None:
    """Compare explicitly retained context; caller claims do not attest live state.

    No clock continuity, issuance, or authentication is inferred by this helper.
    A transport/authority owner must supply independently retained context.
    """
    validate_record(plan, 'Plan')
    validate_record(anchor, 'Anchor')
    _check(nonce, 'H')
    _check(service_epoch, 'H')
    _check(now_ns, 'N')
    _check(operator_uid, 'U')
    receipt, bounds = plan['observation'], plan['grant']['bounds']
    require(receipt['nonce'] == nonce and receipt['service_epoch'] == service_epoch
            and receipt['anchor'] == anchor and receipt['operator_uid'] == operator_uid,
            'StaleBinding', 'Observation context differs')
    require(bounds['not_before_ns'] <= receipt['observed_ns'] <= now_ns < bounds['expires_ns']
            and now_ns - receipt['observed_ns'] <= bounds['receipt_max_age_ns'],
            'StaleBinding', 'Observation window differs')
