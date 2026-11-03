#!/usr/bin/python3
"""GRRR-z3w9 Stage A protected read-only baseline capture.

This program only reads the approved successor accounting store. It opens SQLite
read-only/immutable, performs no checkout imports, and writes nothing. JSON is
printed to stdout by the root parent; the calling operator shell redirects it.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import stat
import subprocess
import sys

ACCOUNTING = Path('/Library/GRRR/accounting-poc2')
ACTIVE = ACCOUNTING / 'active.json'
REGISTRATION_PRIOR = ACCOUNTING / 'registration/prior-active.json'
REGISTRATION_RECEIPT = ACCOUNTING / 'registration/receipt.json'
RECOVERY_PRIOR = ACCOUNTING / 'recovery/prior-active.json'
RECOVERY_INTENT = ACCOUNTING / 'recovery/intent.json'
RECOVERY_RECEIPT = ACCOUNTING / 'recovery/receipt.json'
RECOVERY_COMPLETE = ACCOUNTING / 'recovery/complete.json'
SELF = Path('/private/tmp/grrr_stage_a_capture.py')
POLICY = Path('/Users/speed/Documents/Codex/2026-10-19/3e4m-b-4/outputs/governed-recursive-research-ratchet/.claude/worktrees/dev-GRRR-z3w9/docs/SPENDABILITY-RECONCILIATION-EVIDENCE-CONTRACT.md')
VECTOR_NAMES = ('money_cents', 'execution_us', 'review_us')
SCHEMA_OBJECTS = [
    'state', 'reservations', 'metering', 'overhead', 'store_identity',
    'state_id_unique', 'reservation_id_unique', 'reservation_key_unique',
    'metering_id_unique', 'metering_reservation_unique', 'overhead_key_unique',
]


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True,
                      allow_nan=False).encode('ascii')


def canonical_digest(value: object) -> str:
    return digest(canonical(value))


def no_acl(path: Path) -> tuple[bool, str]:
    result = subprocess.run(['/bin/ls', '-lde', str(path)], capture_output=True,
                            timeout=5, check=True)
    text = result.stdout.decode('ascii', 'strict').strip()
    return ('+' not in text.split()[0] and len(text.splitlines()) == 1), text


def snapshot_file(path: Path) -> tuple[bytes, dict]:
    preopen = path.lstat()
    info = preopen
    if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
        raise RuntimeError('protected source is not a one-link regular file: ' + str(path))
    flags = os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0) | getattr(os, 'O_NONBLOCK', 0)
    descriptor = os.open(str(path), flags)
    try:
        opened = os.fstat(descriptor)
        chunks = []
        while True:
            chunk = os.read(descriptor, 1024 * 1024)
            if not chunk:
                break
            chunks.append(chunk)
        raw = b''.join(chunks)
        final = os.fstat(descriptor)
        identity = ('st_dev', 'st_ino', 'st_mode', 'st_uid', 'st_gid', 'st_nlink',
                    'st_size', 'st_mtime_ns', 'st_ctime_ns')
        if any(getattr(preopen, name) != getattr(opened, name) for name in identity):
            raise RuntimeError('protected path identity changed at open: ' + str(path))
        if any(getattr(opened, name) != getattr(final, name) for name in identity):
            raise RuntimeError('protected source changed during read: ' + str(path))
    finally:
        os.close(descriptor)
    safe_acl, acl_text = no_acl(path)
    if not safe_acl:
        raise RuntimeError('protected source has an ACL: ' + str(path))
    record = {
        'path': str(path), 'sha256': digest(raw), 'device': info.st_dev,
        'inode': info.st_ino, 'mode': stat.S_IMODE(info.st_mode),
        'uid': info.st_uid, 'gid': info.st_gid, 'nlink': info.st_nlink,
        'size': info.st_size, 'acl': acl_text,
    }
    return raw, record


def stable_snapshot(path: Path) -> tuple[bytes, dict, dict]:
    first, record = snapshot_file(path)
    second, after = snapshot_file(path)
    immutable_keys = ('sha256', 'device', 'inode', 'mode', 'uid', 'gid', 'nlink', 'size')
    if any(record[name] != after[name] for name in immutable_keys):
        raise RuntimeError('protected source was not stable: ' + str(path))
    return first, record, after


def decode_blob(raw: bytes) -> object:
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError('duplicate key')
            result[key] = value
        return result
    value = json.loads(raw.decode('utf-8'), object_pairs_hook=unique,
                       parse_constant=lambda item: (_ for _ in ()).throw(ValueError(item)))
    if canonical(value) != raw:
        raise ValueError('source BLOB is not canonical')
    return value


def raw_row(row: tuple, columns: list[str]) -> dict:
    result = {}
    for name, value in zip(columns, row):
        if isinstance(value, bytes):
            result[name] = {'kind': 'blob', 'blob_hex': value.hex(),
                            'byte_count': len(value), 'decoded': decode_blob(value)}
        else:
            result[name] = {'kind': type(value).__name__, 'value': value}
    return result


def zero_vector() -> dict:
    return {name: 0 for name in VECTOR_NAMES}


def vector(value: dict) -> dict:
    return {'currency': str(value['currency']),
            **{name: int(value[name]) for name in VECTOR_NAMES}}


def add(left: dict, right: dict) -> dict:
    return {name: left[name] + right[name] for name in VECTOR_NAMES}


def unauthenticated_provenance(evidence_hash: str) -> dict:
    return {
        'issuer': 'legacy-store-unauthenticated', 'issuer_authenticated': False,
        'evidence_sha256': evidence_hash, 'measurement_window': 'unknown',
        'trusted_history': False, 'request_binding_authorized': False,
    }


def main() -> int:
    if os.getuid() != 0 or os.geteuid() != 0:
        raise RuntimeError('Stage A capture requires the approved root parent')
    started = dt.datetime.now(dt.timezone.utc).isoformat()
    files = {
        'active': ACTIVE, 'registration_prior_active': REGISTRATION_PRIOR,
        'registration_receipt': REGISTRATION_RECEIPT, 'recovery_prior_active': RECOVERY_PRIOR,
        'recovery_intent': RECOVERY_INTENT, 'recovery_receipt': RECOVERY_RECEIPT,
        'recovery_complete': RECOVERY_COMPLETE, 'policy_contract': POLICY,
        'capture_program': SELF,
    }
    captured = {name: stable_snapshot(path) for name, path in files.items()}
    active = json.loads(captured['active'][0])
    database = Path(active['directory']) / 'budget.sqlite'
    observed_paths = [ACCOUNTING, ACTIVE, REGISTRATION_PRIOR, REGISTRATION_RECEIPT,
                      RECOVERY_PRIOR, RECOVERY_INTENT, RECOVERY_RECEIPT,
                      RECOVERY_COMPLETE, SELF, POLICY, database,
                      *database.parents]
    symlinks_absent = all(not path.is_symlink() for path in observed_paths)
    journal_sidecars = sorted(path.name for path in database.parent.iterdir()
                              if path.name.startswith('budget.sqlite')
                              and path.name != 'budget.sqlite')
    journal_sidecars_absent = not journal_sidecars
    db_raw_before, db_before, db_during = stable_snapshot(database)
    connection = sqlite3.connect(database.as_uri() + '?mode=ro&immutable=1', uri=True)
    connection.execute('PRAGMA query_only=ON')
    integrity = connection.execute('PRAGMA integrity_check').fetchall()
    journal_mode = connection.execute('PRAGMA journal_mode').fetchone()[0]
    schema = []
    for kind, name, table_name, sql in connection.execute(
            "SELECT type,name,tbl_name,sql FROM sqlite_master ORDER BY type,name"):
        schema.append({'type': kind, 'name': name, 'table': table_name, 'sql': sql})
    actual_tables = {item['name'] for item in schema if item['type'] == 'table'}
    required_tables = {'state', 'reservations', 'metering', 'overhead', 'store_identity'}
    # SQLite implicit primary-key/unique indexes are represented by the contract's
    # semantic names rather than unstable sqlite_autoindex names.
    expected_autoindexes = sum(1 for item in schema if item['name'].startswith('sqlite_autoindex_'))
    if actual_tables != required_tables or expected_autoindexes != 5 or len(schema) != 10:
        raise RuntimeError('schema inventory differs from approved semantic objects: '
                           + repr((sorted(actual_tables), expected_autoindexes, len(schema))))

    tables = {}
    package_rows = {}
    for table in ('state', 'store_identity', 'reservations', 'metering', 'overhead'):
        columns = [row[1] for row in connection.execute('PRAGMA table_info(' + table + ')')]
        rows = [raw_row(row, columns) for row in connection.execute('SELECT * FROM ' + table)]
        tables[table] = {'columns': columns, 'rows': rows}

    reservations_raw = connection.execute(
        'SELECT id,key,binding,run,stage,maximum,actual,receipt FROM reservations ORDER BY id'
    ).fetchall()
    metering_raw = connection.execute(
        'SELECT id,reservation,body FROM metering ORDER BY id'
    ).fetchall()
    meters_by_reservation = {row[1]: row for row in metering_raw}
    package_reservations = []
    expected_pending = {}
    known = {'poc': zero_vector(), 'milestone': zero_vector()}
    for identifier, key, binding_blob, run, stage, maximum_blob, actual_blob, receipt in reservations_raw:
        binding_source = decode_blob(binding_blob)
        maximum = vector(decode_blob(maximum_blob))
        actual = vector(decode_blob(actual_blob)) if actual_blob is not None else None
        request = {'binding': binding_source['binding'], 'maximum': maximum,
                   'run': run, 'stage': stage}
        request_blob = canonical(request).decode('ascii')
        meter = meters_by_reservation.get(identifier)
        evidence_hash = digest(binding_blob) if meter is None else digest(meter[2])
        pending = actual is None
        pending_evidence = None
        if pending:
            pending_evidence = {
                'dispatch_outcome': 'non-disposed',
                'final_observation_sha256': canonical_digest({'status': 'missing'}),
                'stale_handles_accounted': False, 'baseline_unchanged': True,
            }
            expected_pending[identifier] = maximum
        package_reservations.append({
            'id': identifier, 'key': key, 'run': run, 'stage': stage,
            'maximum': maximum, 'binding': binding_source['binding'],
            'actual': actual, 'receipt': receipt, 'request_blob': request_blob,
            'request_sha256': digest(request_blob.encode('ascii')),
            'disposition': 'pending' if pending else 'settled',
            'provenance': unauthenticated_provenance(evidence_hash),
            'pending_evidence': pending_evidence,
        })
        source = actual if actual is not None else maximum
        for scope in ('poc', 'milestone') if stage == 'poc' else ('milestone',):
            known[scope] = add(known[scope], source)
    package_meters = []
    for identifier, reservation, body in metering_raw:
        source = decode_blob(body)
        package_meters.append({
            'id': identifier, 'reservation': reservation,
            'body': canonical(source).decode('ascii'), 'usage': vector(source['usage']),
            'provenance': unauthenticated_provenance(digest(body)),
        })
    state_raw = connection.execute('SELECT id,stopped FROM state ORDER BY id').fetchall()
    store_raw = connection.execute(
        'SELECT campaign,store_id,prior_history_receipt FROM store_identity ORDER BY store_id'
    ).fetchall()
    if len(state_raw) != 1 or len(store_raw) != 1:
        raise RuntimeError('state/store identity cardinality differs')
    active_hash = captured['active'][1]['sha256']
    package_state = [{'id': state_raw[0][0], 'active_binding': active_hash,
                      'stopped': state_raw[0][1]}]
    package_store = [{'campaign': store_raw[0][0], 'store_id': store_raw[0][1],
                      'active_binding': active_hash,
                      'prior_history_receipt': store_raw[0][2]}]
    package_rows = {
        'reservations': package_reservations, 'meters': package_meters, 'overhead': [],
        'state': package_state, 'store_identity': package_store,
    }
    # Bind every raw cell and type, not the smaller validator projection.
    row_digest = canonical_digest(tables)
    metadata = {
        'database_device': db_before['device'], 'database_inode': db_before['inode'],
        'owner': str(db_before['uid']) + ':' + str(db_before['gid']),
        'mode': db_before['mode'], 'acl': db_before['acl'],
        'link_count': db_before['nlink'], 'sidecars': [],
        'symlinks_absent': True,
    }
    metadata_hash = canonical_digest(metadata)
    provenance_hash = canonical_digest({
        'database_sha256': db_before['sha256'], 'metadata_sha256': metadata_hash,
    })
    schema_fingerprint = canonical_digest(schema)
    review_pending = digest(b'GRRR-z3w9 Stage A independent review pending')
    operator_pending = digest(b'GRRR-z3w9 Stage A operator decision pending')
    overhead_incomplete = {name: False for name in (
        'preparation', 'selection', 'execution', 'review', 'other')}
    baseline = {
        'active_binding': active_hash,
        'prior_active_binding': captured['recovery_prior_active'][1]['sha256'],
        'registration_receipt': captured['registration_receipt'][1]['sha256'],
        'recovery_intent': captured['recovery_intent'][1]['sha256'],
        'recovery_receipt': captured['recovery_receipt'][1]['sha256'],
        'completion_record': captured['recovery_complete'][1]['sha256'],
        'database_sha256': db_before['sha256'],
        'database_device': db_before['device'], 'database_inode': db_before['inode'],
        'owner': metadata['owner'], 'mode': db_before['mode'],
        'acl': db_before['acl'], 'link_count': db_before['nlink'], 'sidecars': [],
        'symlinks_absent': symlinks_absent,
        'schema_fingerprint': schema_fingerprint,
        'schema_objects': list(SCHEMA_OBJECTS), 'row_multiset_sha256': row_digest,
        'metadata_sha256': metadata_hash, 'provenance_sha256': provenance_hash,
        'toolchain_sha256': captured['capture_program'][1]['sha256'],
        'observer': 'root-parent-read-only',
        # Stable bytes alone do not prove writer exclusion.
        'capture_stable': False,
        'journal_mode': journal_mode, 'integrity_result': 'ok',
        'journal_sidecars_absent': journal_sidecars_absent,
        'review_sha256': review_pending,
        'review_approved': False,
        'operator_decision_sha256': operator_pending,
        'operator_decision_bound': False,
        'historical_completeness': False, 'recovery_lineage_complete': False,
        'overhead_completeness': overhead_incomplete,
        'expected_pending_maxima': expected_pending,
    }
    now = dt.datetime.now(dt.timezone.utc)
    valid_until = now + dt.timedelta(hours=24)
    reconciliation = {
        'id': 'stage-a-' + now.strftime('%Y%m%dT%H%M%SZ'),
        'baseline_sha256': canonical_digest(baseline),
        'active_binding': active_hash,
        'database_sha256': db_before['sha256'],
        'schema_fingerprint': schema_fingerprint,
        'row_multiset_sha256': row_digest,
        'policy_sha256': captured['policy_contract'][1]['sha256'],
        'toolchain_sha256': captured['capture_program'][1]['sha256'],
        'review_sha256': review_pending,
        'authorization_sha256': operator_pending,
        'created_at': now.isoformat(), 'valid_until': valid_until.isoformat(),
        'prior_use': False, 'authorization_bound': False,
        'freshness_attested': True, 'dispatch_authorization': None,
    }
    zero_scope = {scope: dict(zero_vector(), currency='USD')
                  for scope in ('poc', 'milestone')}
    ceilings = {
        'poc': {'currency': 'USD', 'money_cents': 5000,
                'execution_us': 21600000000, 'review_us': 3600000000},
        'milestone': {'currency': 'USD', 'money_cents': 15000,
                      'execution_us': 86400000000, 'review_us': 10800000000},
    }
    known_package = {scope: dict(known[scope], currency='USD') for scope in ('poc', 'milestone')}
    validation_package = {
        'schema_version': 1, 'canonicalization_version': 1, 'baseline': baseline,
        **package_rows, 'known_encumbered': known_package,
        'overhead_totals': zero_scope, 'ceilings': ceilings,
        # The numeric validator schema cannot represent an unbounded unknown.
        # Keep this deliberately invalid rather than treating zero as proven.
        'unknown_upper_bounds': {'status': 'unresolved', 'proven_upper_bound': None},
        'reconciliation': reconciliation, 'reported_spendability': None,
    }
    process_inventory = subprocess.run(
        ['/bin/ps', '-axo', 'uid=,pid=,comm='], capture_output=True, timeout=5, check=True
    ).stdout.decode('ascii', 'strict')
    sensitive_processes = [line.strip() for line in process_inventory.splitlines()
                           if line.split() and (line.split()[0] in ('320', '321')
                                                or 'qemu' in line.lower())]
    connection.close()
    db_raw_after, db_after, db_final = stable_snapshot(database)
    captured_after = {name: stable_snapshot(path)[1] for name, path in files.items()}
    immutable_keys = ('sha256', 'device', 'inode', 'mode', 'uid', 'gid', 'nlink', 'size')
    stable = all(all(captured[name][1][key] == captured_after[name][key]
                     for key in immutable_keys) for name in files)
    stable = stable and all(db_before[key] == db_after[key] for key in immutable_keys)
    sidecars = sorted(path.name for path in database.parent.iterdir()
                      if path.name.startswith('budget.sqlite') and path.name != 'budget.sqlite')
    result = {
        'schema_version': 1,
        'capture_kind': 'GRRR-z3w9-stage-a-protected-read-only-baseline',
        'authority': {'write': False, 'reconcile': False, 'replay': False,
                      'promotion': False, 'admission': False, 'merge': False, 'push': False},
        'started_at': started, 'completed_at': dt.datetime.now(dt.timezone.utc).isoformat(),
        'active': active, 'source_files': {name: captured[name][1] for name in files},
        'database': {'path': str(database), 'before': db_before, 'during': db_during,
                     'after': db_after, 'size_bytes': len(db_raw_before),
                     'integrity_check': integrity, 'journal_mode': journal_mode,
                     'sidecars': sidecars, 'stable': stable},
        'sqlite_schema': schema, 'raw_tables': tables,
        'ancestry_contents': {
            name: json.loads(captured[name][0]) for name in (
                'active', 'registration_prior_active', 'registration_receipt',
                'recovery_prior_active', 'recovery_intent', 'recovery_receipt',
                'recovery_complete')
        },
        'counts': {'reservations': len(package_reservations), 'meters': len(package_meters),
                   'overhead': 0, 'pending': len(expected_pending)},
        'known_encumbered_calculation': known,
        'unknown_upper_bound_status': 'unresolved-unbounded',
        'sensitive_processes': sensitive_processes,
        'validation_package': validation_package,
        'mutation_performed': False,
    }
    if not stable or sidecars or integrity != [('ok',)] or journal_mode != 'delete':
        result['capture_gate'] = 'FAIL_CLOSED_UNRESOLVED_QUIESCENCE'
    else:
        result['capture_gate'] = 'PASS_READ_ONLY_SNAPSHOT_BASELINE_UNRESOLVED'
    print(json.dumps(result, sort_keys=True, indent=2, ensure_ascii=True, allow_nan=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
