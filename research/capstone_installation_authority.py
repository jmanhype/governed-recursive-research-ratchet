"""Source-only InstallationV2 authority joins; no installed authority exists.

The codecs below validate only the accepted InstallationV2, immutable approval
registry, ApprovalV1 and AuthorizationV1 data shapes and exact original bytes.
They never open a path, authenticate a principal, establish provenance, issue a
grant, or make a private fixture protected.  In particular, the accepted records
make a positive full-byte join circular: the installation pins the registry, the
registry embeds authorization bytes, and those bytes pin the installation hash.
No exclusion rule was accepted, so this module refuses that join rather than
omitting a field or inventing an import-review schema.
"""
import json
from collections.abc import Mapping

from capstone_backend_contract import decode_raw, encode_raw
from capstone_contract import _check
from capstone_installation_inventory import (
    encode_inventory,
    validate_inventory,
)
from capstone_installation_record import decode_installation
from common import (
    Failure,
    MAX_WIRE,
    canonical,
    digest,
    require,
    unique_fields,
)


AUTHORIZATION_SCHEMA = 'capstone-authorization-v1'
APPROVAL_SCHEMA = 'capstone-approval-v1'
REGISTRY_SCHEMA = 'capstone-approval-registry-v1'
MAX_ENTRIES = 256
AUTHORIZATION_FIELDS = frozenset((
    'schema', 'action', 'operator_uid', 'campaign_spec_sha256',
    'baseline_endorsement_sha256', 'installation_sha256', 'not_before_ns',
    'expires_ns', 'maximum', 'leaf_ids', 'review_anchor',
))
APPROVAL_FIELDS = frozenset((
    'schema', 'authorization_sha256', 'authorization_raw', 'campaign_spec_sha256',
    'campaign_id', 'issuance_id', 'receipt_max_age_ns', 'floors', 'import_review',
))
REGISTRY_FIELDS = frozenset(('schema', 'entries'))
FIXTURE_ASSURANCE = 'DETACHED_FIXTURE_BYTES_ONLY'


def _no_float(text):
    raise ValueError('Floating and non-finite JSON values are forbidden: ' + text)


def _decode_canonical(raw, validator, kind):
    require(type(raw) is bytes and 0 < len(raw) <= MAX_WIRE,
            'InvalidInput', kind + ' byte bound differs')
    try:
        value = json.loads(raw, object_pairs_hook=unique_fields,
                           parse_float=_no_float, parse_constant=_no_float)
    except (ValueError, UnicodeError, RecursionError) as exc:
        raise Failure('InvalidInput', 'Malformed ' + kind) from exc
    try:
        validator(value)
        encoded = canonical(value)
    except (ValueError, TypeError, RecursionError, OverflowError, UnicodeError) as exc:
        raise Failure('InvalidInput', 'Malformed ' + kind) from exc
    require(len(encoded) <= MAX_WIRE and encoded == raw,
            'InvalidInput', kind + ' bytes are not canonical')
    return value


def validate_authorization(value):
    """Validate exact AuthorizationV1 data; bytes alone are not approval."""
    require(type(value) is dict and set(value) == AUTHORIZATION_FIELDS,
            'InvalidInput', 'Authorization fields differ')
    _check(value['schema'], (AUTHORIZATION_SCHEMA,))
    _check(value['action'], ('capstone-execute',))
    _check(value['operator_uid'], 'U')
    for field in ('campaign_spec_sha256', 'baseline_endorsement_sha256',
                  'installation_sha256', 'review_anchor'):
        _check(value[field], 'H')
    for field in ('not_before_ns', 'expires_ns'):
        _check(value[field], 'N')
    _check(value['maximum'], 'Vector')
    leaves = value['leaf_ids']
    require(type(leaves) is list and 0 < len(leaves) <= 256,
            'InvalidInput', 'Authorization leaf set differs')
    for leaf_id in leaves:
        _check(leaf_id, 'H')
    require(leaves == sorted(set(leaves)), 'InvalidInput',
            'Authorization leaves are not sorted and unique')
    require(value['not_before_ns'] < value['expires_ns'], 'InvalidInput',
            'Authorization window is empty')
    return value


def encode_authorization(value):
    validate_authorization(value)
    raw = canonical(value)
    return raw, digest(raw)


def decode_authorization(raw):
    return _decode_canonical(raw, validate_authorization, 'authorization')


def validate_approval(value):
    """Validate an ApprovalV1 and its exact embedded AuthorizationV1 bytes."""
    require(type(value) is dict and set(value) == APPROVAL_FIELDS,
            'InvalidInput', 'Approval fields differ')
    _check(value['schema'], (APPROVAL_SCHEMA,))
    for field in ('authorization_sha256', 'campaign_spec_sha256', 'issuance_id',
                  'floors', 'import_review'):
        _check(value[field], 'H')
    _check(value['campaign_id'], 'I')
    _check(value['receipt_max_age_ns'], 'N')
    authorization_raw = decode_raw(value['authorization_raw'])
    authorization = decode_authorization(authorization_raw)
    require(digest(authorization_raw) == value['authorization_sha256'],
            'IntegrityFailure', 'Authorization original bytes differ')
    require(authorization['campaign_spec_sha256'] == value['campaign_spec_sha256'],
            'StaleBinding', 'Approval campaign specification differs')
    return value


def encode_approval(value):
    validate_approval(value)
    raw = canonical(value)
    return raw, digest(raw)


def decode_approval(raw):
    return _decode_canonical(raw, validate_approval, 'approval')


def validate_registry(value):
    """Validate exact immutable registry ordering and uniqueness invariants."""
    require(type(value) is dict and set(value) == REGISTRY_FIELDS,
            'InvalidInput', 'Registry fields differ')
    _check(value['schema'], (REGISTRY_SCHEMA,))
    entries = value['entries']
    require(type(entries) is list and 0 < len(entries) <= MAX_ENTRIES,
            'InvalidInput', 'Registry entry count differs')
    for entry in entries:
        validate_approval(entry)
    authorizations = [entry['authorization_sha256'] for entry in entries]
    require(authorizations == sorted(authorizations), 'InvalidInput',
            'Registry entries are not authorization-sorted')
    for field in ('authorization_sha256', 'campaign_id', 'issuance_id'):
        values = [entry[field] for entry in entries]
        require(len(values) == len(set(values)), 'InvalidInput',
                'Registry ' + field + ' is not unique')
    return value


def encode_registry(value):
    validate_registry(value)
    raw = canonical(value)
    return raw, digest(raw)


def decode_registry(raw):
    return _decode_canonical(raw, validate_registry, 'approval registry')


def validate_registry_pin(installation_raw, registry_raw):
    """Validate descriptor/registry bytes and the descriptor registry pin."""
    installation = decode_installation(installation_raw)
    registry = decode_registry(registry_raw)
    require(installation['authorization_registry_sha256'] == digest(registry_raw),
            'StaleBinding', 'Installation registry pin differs')
    return installation, registry


def validate_authority_binding(installation_raw, registry_raw):
    """Resolve all deterministic full-byte joins, then refuse the known cycle.

    If an embedded authorization claims the supplied installation, its exact hash
    necessarily occurred inside registry bytes already consumed by the descriptor
    pin.  That is a cryptographic construction cycle, not a runtime condition to
    repair or cache.  An authorization claiming another installation is merely a
    stale binding.  Both outcomes are failures before any authority is returned.
    """
    installation, registry = validate_registry_pin(installation_raw, registry_raw)
    installation_hash = digest(installation_raw)
    for entry in registry['entries']:
        authorization = decode_authorization(decode_raw(entry['authorization_raw']))
        require(authorization['installation_sha256'] == installation_hash,
                'StaleBinding', 'Authorization installation differs')
        require(False, 'RecoveryRequired',
                'Installation/registry/authorization full-byte cycle is unresolved')
    raise Failure('Unavailable', 'No authority entry is present')


def require_import_provenance(approval):
    """Fail closed because no accepted import-review evidence codec exists."""
    validate_approval(approval)
    raise Failure('Unavailable',
                  'Installed import-review provenance is not qualified')


def resolve_authorization(installation_raw, registry_raw, authorization_sha256,
                          now_ns):
    """Resolve no authority from source bytes; there is no provenance factory."""
    _check(authorization_sha256, 'H')
    _check(now_ns, 'N')
    installation, registry = validate_registry_pin(installation_raw, registry_raw)
    matches = [entry for entry in registry['entries']
               if entry['authorization_sha256'] == authorization_sha256]
    require(len(matches) == 1, 'Unavailable', 'Authorization is not uniquely registered')
    entry = matches[0]
    authorization = decode_authorization(decode_raw(entry['authorization_raw']))
    require(authorization['installation_sha256'] == digest(installation_raw),
            'StaleBinding', 'Authorization installation differs')
    require(False, 'RecoveryRequired',
            'Installation/registry/authorization full-byte cycle is unresolved')
    require(authorization['operator_uid'] == installation['operator_uid'],
            'StaleBinding', 'Authorization operator differs')
    require(authorization['not_before_ns'] <= now_ns < authorization['expires_ns'],
            'StaleBinding', 'Authorization is not current')
    require_import_provenance(entry)
    raise Failure('RecoveryRequired', 'Unreachable authority resolution')


def validate_detached_source_inventory(installation_raw, fixture):
    """Join a private fixture result to InstallationV2 without provenance.

    The caller must pass the mapping returned by the existing private-temp fixture
    reader, never a path.  This join proves only that those detached byte copies
    match the descriptor's source inventory.  It cannot make them an installed,
    immutable, independently reviewed closure.
    """
    installation = decode_installation(installation_raw)
    require(isinstance(fixture, Mapping), 'InvalidInput',
            'Fixture result must be a mapping')
    allowed = {
        'schema', 'environment', 'actual_uid', 'assurance',
        'stable_installation', 'trusted_provenance', 'contents',
        'inventory_raw', 'inventory_sha256', 'records',
    }
    require(set(fixture) <= allowed and {'environment', 'assurance',
            'stable_installation', 'contents', 'inventory_raw',
            'inventory_sha256'} <= set(fixture), 'InvalidInput',
            'Fixture result fields differ')
    require(fixture['environment'] == 'NONPRODUCTION'
            and fixture['assurance'] == FIXTURE_ASSURANCE
            and fixture['stable_installation'] is False
            and fixture.get('trusted_provenance', False) is False,
            'Unavailable', 'Fixture is not explicitly nonproduction detached bytes')
    contents = fixture['contents']
    require(isinstance(contents, Mapping)
            and all(type(raw) is bytes for raw in contents.values()),
            'InvalidInput', 'Fixture contents differ')
    records = fixture.get('records')
    if records is None:
        records = [dict(relative_path=path, mode=0o444, sha256=digest(raw))
                   for path, raw in sorted(contents.items())]
    normalized = validate_inventory(records)
    expected_paths = {record['relative_path'] for record in normalized}
    require(set(contents) == expected_paths, 'StaleBinding',
            'Fixture contents and inventory differ')
    for record in normalized:
        require(digest(contents[record['relative_path']]) == record['sha256'],
                'IntegrityFailure', 'Detached fixture bytes differ')
    inventory_raw, inventory_hash = encode_inventory(normalized)
    require(fixture['inventory_raw'] == inventory_raw
            and fixture['inventory_sha256'] == inventory_hash,
            'IntegrityFailure', 'Fixture inventory bytes differ')
    require(installation['source_manifest_sha256'] == inventory_hash,
            'StaleBinding', 'Installation source inventory pin differs')
    return dict(schema='capstone-detached-source-inventory-join-v1',
                environment='NONPRODUCTION', source_manifest_sha256=inventory_hash,
                trusted_provenance=False, stable_installation=False,
                inventory_sha256=inventory_hash)


def open_installed_authority(role=None):
    """Refuse before path or metadata access; no source caller can enable it."""
    require(type(role) is str or role is None, 'InvalidInput', 'Role must be text or null')
    raise Failure('Unavailable', 'Protected installation authority is not qualified')
