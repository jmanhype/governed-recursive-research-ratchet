"""Strict data-only codec for InstallationV2 descriptors.

Validation establishes only canonical shape and the SHA-256 of those exact
bytes. It does not inspect an installation, authenticate a caller, resolve
manifest contents, or grant any effect or authority.
"""
import json

from capstone_contract import _check
from common import Failure, MAX_WIRE, canonical, digest, require, unique_fields


SCHEMA = 'capstone-installation-v2'
REVIEWER_UID = 322
DIGEST_FIELDS = frozenset((
    'source_manifest_sha256', 'runtime_manifest_sha256', 'evaluator_manifest_sha256',
    'runner_manifest_sha256', 'interpreter_sha256', 'bootstrap_sha256',
    'qemu_manifest_sha256', 'assets_sha256', 'corpus_sha256',
    'replay_catalog_sha256', 'replay_image_sha256', 'execution_profile_sha256',
    'policy_sha256', 'accounting_binding_sha256', 'baseline_endorsement_sha256',
    'authorization_registry_sha256', 'floors_sha256', 'timing_policy_sha256',
    'reviewer_manifest_sha256',
))
FIELDS = frozenset(('schema', 'operator_uid', *DIGEST_FIELDS))
SCHEMAS = {
    'InstallationV2': dict(schema=(SCHEMA,), operator_uid='U',
                           **{name: 'H' for name in DIGEST_FIELDS}),
}


def validate_record(value):
    """Validate InstallationV2 data; provenance and installation remain absent."""
    require(type(value) is dict and set(value) == FIELDS, 'InvalidInput', 'Fields differ')
    _check(value['schema'], (SCHEMA,))
    _check(value['operator_uid'], 'U')
    require(value['operator_uid'] != REVIEWER_UID, 'InvalidInput',
            'Invalid operator UID')
    for name in DIGEST_FIELDS:
        _check(value[name], 'H')
    require(len(canonical(value)) <= MAX_WIRE, 'InvalidInput', 'Record exceeds cap')
    return value


def _no_float(text):
    raise ValueError('Floating and non-finite JSON values are forbidden: ' + text)


def decode_record(raw):
    """Decode exact canonical JSON bytes; no descriptor path is consulted."""
    require(type(raw) is bytes and 0 < len(raw) <= MAX_WIRE,
            'InvalidInput', 'Invalid byte bound')
    try:
        value = json.loads(raw, object_pairs_hook=unique_fields,
                           parse_float=_no_float, parse_constant=_no_float)
    except (ValueError, UnicodeError, RecursionError) as exc:
        raise Failure('InvalidInput', 'Malformed JSON') from exc
    validate_record(value)
    require(canonical(value) == raw, 'InvalidInput', 'Record bytes are not canonical')
    return value


def encode_record(value):
    """Return exact canonical bytes and their SHA-256, never authority."""
    validate_record(value)
    raw = canonical(value)
    return raw, digest(raw)


validate_installation = validate_record
decode_installation = decode_record
encode_installation = encode_record
