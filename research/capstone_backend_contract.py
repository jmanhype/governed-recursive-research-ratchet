"""Pure source-WIP codecs: ReviewV2 and unchanged v1 nested records only.

Shape/hash consistency is NOT reviewer identity, issuance, allowance, freshness,
or execution authority. Other backend schemas remain unsupported, fail closed,
and must not be represented as implemented by this module's hash helpers.
No filesystem, transport, identity, or accounting operations occur here.
"""
import base64
import binascii
import json

import capstone_contract as v1
from common import Failure, MAX_WIRE, canonical, digest, identifier, require, unique_fields

MAX_RAW = 16 * 1024 * 1024
MAX_DEPTH = 40
MAX_NODES = 65536
SCHEMAS = {
    'ReviewV2': dict(
        schema=('capstone-jit-review-v2',), phase=('actual-plan-prelaunch',),
        verdict=('pass', 'fail'), reviewer_identity='H', verifier_inventory='H',
        policy_sha256='H', source_review_sha256='H', static_review_sha256='H',
        authorization_bytes_sha256='H', campaign_spec_sha256='H',
        campaign_plan_sha256='H', leaf_id='H', grant_bytes_sha256='H', operation_id='H',
        actual_plan_sha256='H', actual_plan_bytes_sha256='H', observation_sha256='H',
        service_epoch='H', anchor='Anchor', reviewed_ns='N', expires_ns='N',
        evidence='Hashes', blockers='Codes'),
}


def _json_data(value, depth=0, budget=None):
    if budget is None:
        budget = [MAX_NODES]
    budget[0] -= 1
    require(depth < MAX_DEPTH and budget[0] >= 0, 'InvalidInput', 'JSON complexity bound exceeded')
    kind = type(value)
    if kind is dict:
        for key, child in value.items():
            require(type(key) is str, 'InvalidInput', 'JSON keys must be strings')
            _json_data(child, depth + 1, budget)
    elif kind is list:
        for child in value:
            _json_data(child, depth + 1, budget)
    else:
        require(value is None or kind in (str, int, bool), 'InvalidInput', 'Non-JSON or floating value')


def _bytes(value, maximum):
    require(type(value) is bytes and len(value) <= maximum, 'InvalidInput', 'Invalid byte bound')
    return value


def _canonical(value, maximum):
    _json_data(value)
    try:
        raw = canonical(value)
    except (ValueError, TypeError, OverflowError, RecursionError, UnicodeError) as exc:
        raise Failure('InvalidInput', 'Malformed canonical data') from exc
    require(len(raw) <= maximum, 'InvalidInput', 'Canonical data exceeds bound')
    return raw


def _hashes(value):
    require(type(value) is list and len(value) <= MAX_NODES, 'InvalidInput', 'Invalid evidence list')
    for item in value:
        v1._check(item, 'H')
    require(value == sorted(set(value)), 'InvalidInput', 'Evidence must be sorted and unique')


def validate_record(value, kind):
    """Validate data, never provenance. Unsupported backend types REFUSE."""
    require(type(kind) is str and len(kind) <= 64, 'InvalidInput', 'Invalid record kind')
    require(kind in SCHEMAS or kind in v1.SCHEMAS, 'InvalidInput', 'Backend schema not implemented')
    _canonical(value, MAX_WIRE)
    if kind in v1.SCHEMAS:
        return v1.validate_record(value, kind)
    shape = SCHEMAS[kind]
    require(type(value) is dict and set(value) == set(shape), 'InvalidInput', 'Fields differ')
    for name, spec in shape.items():
        if spec == 'Hashes':
            _hashes(value[name])
        else:
            v1._check(value[name], spec)
    require(value['expires_ns'] > value['reviewed_ns'], 'InvalidInput', 'Empty review window')
    if value['verdict'] == 'pass':
        require(value['blockers'] == [], 'InvalidInput', 'Passing review has blockers')
        require(value['source_review_sha256'] in value['evidence']
                and value['static_review_sha256'] in value['evidence'],
                'InvalidInput', 'Passing review omits prerequisite review references')
    # Expired historical reviews remain valid DATA. ReviewClient performs the
    # separate current-clock, authenticated retrieval and exact Plan checks.
    return value


def _no_float(text):
    raise ValueError('Floating and non-finite JSON values are forbidden')


def decode_record(raw, kind):
    _bytes(raw, MAX_WIRE)
    require(bool(raw), 'InvalidInput', 'Empty record')
    try:
        value = json.loads(raw, object_pairs_hook=unique_fields,
                           parse_float=_no_float, parse_constant=_no_float)
    except (ValueError, UnicodeError, RecursionError) as exc:
        raise Failure('InvalidInput', 'Malformed JSON') from exc
    validate_record(value, kind)
    require(_canonical(value, MAX_WIRE) == raw, 'InvalidInput', 'Record bytes are not canonical')
    return value


def encode_raw(raw):
    return base64.b64encode(_bytes(raw, MAX_RAW)).decode('ascii')


def decode_raw(value):
    require(type(value) is str and len(value) <= 4 * ((MAX_RAW + 2) // 3),
            'InvalidInput', 'Raw encoding exceeds bound')
    try:
        raw = base64.b64decode(value, validate=True)
    except (ValueError, UnicodeError, binascii.Error) as exc:
        raise Failure('InvalidInput', 'Malformed raw encoding') from exc
    require(len(raw) <= MAX_RAW and base64.b64encode(raw).decode('ascii') == value,
            'InvalidInput', 'Noncanonical raw encoding')
    return raw


def domain_hash(tag, value):
    """D(tag,x), a hash helper only; it does not validate x's record schema."""
    require(type(tag) is str and 0 < len(tag) <= 128
            and all(33 <= ord(c) <= 126 for c in tag), 'InvalidInput', 'Invalid domain tag')
    require(type(value) is dict, 'InvalidInput', 'Domain payload must be an object')
    return digest(tag.encode('ascii') + b'\0' + _canonical(value, MAX_RAW))


def campaign_operation_id(campaign_id, plan_sha256):
    require(type(campaign_id) is str, 'InvalidInput', 'Invalid campaign identifier')
    identifier(campaign_id)
    v1._check(plan_sha256, 'H')
    return domain_hash('campaign-operation-v2', dict(campaign_id=campaign_id,
                                                   campaign_plan_sha256=plan_sha256))


def campaign_plan_digest(plan):
    """Compute the proposed root selfhash; NOT complete CampaignPlan validation."""
    require(type(plan) is dict and plan.get('schema') == 'capstone-campaign-plan-v2'
            and 'campaign_plan_sha256' in plan, 'InvalidInput', 'Not a campaign hash input')
    v1._check(plan['campaign_plan_sha256'], 'H')
    return digest(_canonical({k: v for k, v in plan.items() if k != 'campaign_plan_sha256'}, MAX_RAW))
