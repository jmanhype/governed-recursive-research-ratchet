import copy
import json
import os
import unittest
from common import Failure, GATES, canonical, digest
from capstone_contract import (SCHEMAS, bind_grant, bind_inputs, bind_observation, content_digest, decode_record,
                               operation_id, start_request_digest, validate_record)

H = 'a' * 64
AUTH = b'human authorization bytes, not authority'
DECISION = b'{"execution_authorized":false}'
MARKDOWN = b'# not authorized\n'


def sample(spec):
    if isinstance(spec, tuple):
        return spec[0]
    if isinstance(spec, dict):
        return {k: sample(v) for k, v in spec.items()}
    if spec.startswith('?'):
        return None
    if spec in SCHEMAS:
        v = sample(SCHEMAS[spec])
        if spec == 'Bounds':
            v['expires_ns'] = 10
        if spec == 'Accounting':
            v['history'] = 'unknown'
        if spec == 'Receipt':
            v['receipt_sha256'] = content_digest(v, 'receipt_sha256')
        if spec == 'Plan':
            v['plan_sha256'] = content_digest(v, 'plan_sha256')
        if spec == 'Operation':
            v['operation_id'] = operation_id(v['grant_id'], v['plan_sha256'])
        if spec == 'Start':
            v['operation_id'] = operation_id(v['plan']['grant']['grant_id'], v['plan']['plan_sha256'])
        return v
    return {'N': 1, 'U': os.getuid(), 'I': 'request-1', 'H': H, 'C': 'a' * 40,
            'Rel': 'outputs/reviewed', 'B': False, 'Codes': [], 'Code': 'RecoveryRequired',
            'Gates': {g: dict(state='not-run', evidence=None, reason=None) for g in GATES}}[spec]


def bound_plan():
    p = sample('Plan')
    invocation = canonical({k: p['request'][k] for k in ('run', 'scope', 'maximum')})
    b = p['request']['bindings']
    b['invocation_bytes_sha256'] = digest(invocation)
    b['decision']['decision_json_bytes_sha256'] = digest(DECISION)
    b['decision']['decision_markdown_bytes_sha256'] = digest(MARKDOWN)
    p['grant']['bindings'] = copy.deepcopy(b)
    p['observation']['bindings'] = copy.deepcopy(b)
    for v in (p, p['grant'], p['observation']):
        v['authorization_bytes_sha256'] = digest(AUTH)
    raw = json.dumps(p['grant'], indent=2).encode()
    p['grant_bytes_sha256'] = p['observation']['grant_bytes_sha256'] = digest(raw)
    p['observation']['receipt_sha256'] = content_digest(p['observation'], 'receipt_sha256')
    p['plan_sha256'] = content_digest(p, 'plan_sha256')
    return p, raw, invocation


class ContractTests(unittest.TestCase):
    def test_all_records_and_nested_exact_fields(self):
        def walk(v, path=()):
            if isinstance(v, dict):
                yield path, v
                for k, child in v.items():
                    yield from walk(child, path + (k,))
        for kind in SCHEMAS:
            original = sample(kind)
            self.assertEqual(decode_record(canonical(original), kind), original)
            for path, record in walk(original):
                for mode in ('missing', 'unknown'):
                    v = copy.deepcopy(original)
                    target = v
                    for key in path:
                        target = target[key]
                    if mode == 'missing':
                        del target[next(iter(record))]
                    else:
                        target['unknown'] = None
                    with self.subTest(kind=kind, path=path, mode=mode), self.assertRaises(Failure):
                        validate_record(v, kind)

    def test_all_leaf_types(self):
        def leaves(v, path=()):
            if isinstance(v, dict):
                for k, child in v.items():
                    yield from leaves(child, path + (k,))
            else:
                yield path
        for kind in SCHEMAS:
            original = sample(kind)
            for path in leaves(original):
                v = copy.deepcopy(original)
                target = v
                for k in path[:-1]:
                    target = target[k]
                target[path[-1]] = {'wrong': 'type'}
                with self.subTest(kind=kind, path=path), self.assertRaises(Failure):
                    validate_record(v, kind)

    def test_scalar_edge_cases(self):
        for bad in (True, False, -1, 1.0, float('nan'), '1'):
            v = sample('Vector'); v['money_cents'] = bad
            with self.assertRaises(Failure): validate_record(v, 'Vector')
        for bad in (0, 320, 321, 4294967295, True, -1):
            v = sample('Grant'); v['operator_uid'] = bad
            with self.assertRaises(Failure): validate_record(v, 'Grant')
        for bad in ('', '/absolute', '../x', 'a/../b', 'a//b', 'a/./b', 'a\\b', 'a\x00b', 'é'):
            v = sample('DecisionBinding'); v['output_root'] = bad
            with self.assertRaises(Failure): validate_record(v, 'DecisionBinding')

    def test_raw_json_rejections(self):
        for raw in (b'{}', b'[]', b'{"run":1,"run":2}', b'{"x":NaN}', b'\xff', b'{} {}', b'[' * 10000):
            with self.assertRaises(Failure): decode_record(raw, 'Request')
        with self.assertRaises(Failure): decode_record(b' ' * (3145728 + 1), 'Request')

    def test_byte_bindings_and_context(self):
        p, raw, inv = bound_plan()
        bind_grant(p, raw, AUTH, operator_uid=os.getuid())
        d = p['request']['bindings']['decision']
        args = dict(request_id=d['request_id'], reviewed_package_commit=d['reviewed_package_commit'], output_root=d['output_root'])
        bind_inputs(p['request'], inv, DECISION, MARKDOWN, **args)
        for key in args:
            changed = dict(args); changed[key] = 'b' * 40 if key == 'reviewed_package_commit' else 'other'
            with self.assertRaises(Failure): bind_inputs(p['request'], inv, DECISION, MARKDOWN, **changed)
        for values in ((inv + b' ', DECISION, MARKDOWN), (inv, DECISION+b' ', MARKDOWN), (inv, DECISION, MARKDOWN+b' ')):
            with self.assertRaises(Failure): bind_inputs(p['request'], *values, **args)
        for g, a in ((canonical(p['grant']), AUTH), (raw, AUTH+b'!')):
            with self.assertRaises(Failure): bind_grant(p, g, a, operator_uid=os.getuid())

    def test_selfhash_and_full_start_digest(self):
        p, _, _ = bound_plan()
        s = dict(action='start', version=1, plan=p, operation_id=operation_id(p['grant']['grant_id'], p['plan_sha256']))
        self.assertEqual(start_request_digest(s), digest(canonical(s)))
        p['gates'][GATES[0]]['state'] = 'pass'
        with self.assertRaises(Failure): validate_record(p, 'Plan')

    def test_consistent_rehash_does_not_hide_cross_binding(self):
        p, _, _ = bound_plan()
        p['grant']['bindings']['driver_commit'] = 'b' * 40
        p['plan_sha256'] = content_digest(p, 'plan_sha256')
        with self.assertRaises(Failure): validate_record(p, 'Plan')

    def test_unknown_is_not_zero(self):
        a = sample('Accounting'); a['spendable'] = sample('Vector')
        with self.assertRaises(Failure): validate_record(a, 'Accounting')
        a['spendable'] = None
        validate_record(a, 'Accounting')

    def test_retained_observation_context_not_authority(self):
        p, _, _ = bound_plan()
        p['observation']['anchor'] = sample('Anchor')
        p['observation']['receipt_sha256'] = content_digest(p['observation'], 'receipt_sha256')
        p['plan_sha256'] = content_digest(p, 'plan_sha256')
        args = dict(nonce=H, service_epoch=H, anchor=sample('Anchor'), now_ns=1, operator_uid=os.getuid())
        bind_observation(p, **args)
        for key, value in (('nonce', 'b'*64), ('service_epoch', 'b'*64),
                           ('now_ns', 4), ('now_ns', 0), ('operator_uid', os.getuid()+1)):
            changed = dict(args); changed[key] = value
            with self.assertRaises(Failure): bind_observation(p, **changed)
        changed = copy.deepcopy(args); changed['anchor']['ledger_sequence'] += 1
        with self.assertRaises(Failure): bind_observation(p, **changed)
        p['observation']['anchor'] = None
        p['observation']['receipt_sha256'] = content_digest(p['observation'], 'receipt_sha256')
        p['plan_sha256'] = content_digest(p, 'plan_sha256')
        with self.assertRaises(Failure): bind_observation(p, **args)
