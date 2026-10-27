#!/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/bin/python3.9
"""GRRR-z3w9 Stage D locked protected-read capture.

Reads only the approved accounting-poc2 launch lock, active binding, and SQLite
schema. The program creates no files, opens SQLite read-only/immutable, and
prints one canonical JSON document to stdout.
"""

import datetime as dt
import fcntl
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import stat
import subprocess
import sys


ACTIVE = Path('/Library/GRRR/accounting-poc2/active.json')
LOCK = Path('/Library/GRRR/accounting-poc2/launch.lock')
POLICY = Path('/Users/speed/Documents/Codex/2026-10-19/3e4m-b-4/outputs/governed-recursive-research-ratchet/.claude/worktrees/dev-GRRR-z3w9/docs/SPENDABILITY-RECONCILIATION-EVIDENCE-CONTRACT.md')
REVIEWED_SOURCE = Path('/private/tmp/grrr_stage_d_capture.py')
BASELINE_SHA256 = '7608cbe6fc5f671b88573eca8b642ebfbc172f0cb920f75d60ca34cfa60c730a'
DATABASE_SHA256 = '9c6ff2561a364ed982cd5477dd4b200c995da6910c9a17aa3d3c411a962d64f3'
LOCK_PROTOCOL = 'accounting-poc2-exclusive-v1'
LOCK_PROTOCOL_SHA256 = 'e4a06e7e2a39e7dd6c55592e83f83b78ee4f892ac53d988fb6f18b5a0923db6e'
MUTATOR_COVERAGE_SHA256 = '61c077f8c4e19b06f99d7d4c35a585c4bcb0f5d1e26aeb3816bbcc4b04cf9dc1'
PYTHON_SHA256 = '5c5950c62eee5fd227a67e4bdfcde81c9add59799bba0949635f3d5ba9661c26'
POLICY_SHA256 = 'c179b6c9640a5d848f70bb9b7e6ac3833223a6c55ddf9bfa0b2dbe68a6c82b37'
TABLES = ('metering', 'overhead', 'reservations', 'state', 'store_identity')
AUTHORITY_NAMES = ('protected_access', 'write', 'reconcile', 'replay', 'promotion',
                   'admission', 'merge', 'push')


def sha256_bytes(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True,
                      allow_nan=False)


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec='microseconds').replace('+00:00', 'Z')


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def acl_text(path):
    result = subprocess.run(['/bin/ls', '-lde', str(path)], capture_output=True,
                            timeout=5, check=True)
    text = result.stdout.decode('ascii', 'strict').strip()
    require(text and '+' not in text.split()[0], 'unsafe ACL: ' + str(path))
    return text


def stable_open(path):
    """Read one descriptor and bind it to pre/post no-follow path identities."""
    before = path.lstat()
    descriptor = os.open(str(path), os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0)
                         | getattr(os, 'O_NONBLOCK', 0))
    try:
        opened = os.fstat(descriptor)
        require(stat.S_ISREG(opened.st_mode), 'not a regular file: ' + str(path))
        identity = ('st_dev', 'st_ino', 'st_mode', 'st_uid', 'st_gid', 'st_nlink')
        require(all(getattr(before, name) == getattr(opened, name) for name in identity),
                'path identity changed at open: ' + str(path))
        chunks = []
        digest = hashlib.sha256()
        while True:
            chunk = os.read(descriptor, 1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
            chunks.append(chunk)
        final = os.fstat(descriptor)
        require(all(getattr(opened, name) == getattr(final, name) for name in identity),
                'file identity changed during read: ' + str(path))
        after = path.lstat()
        require(all(getattr(before, name) == getattr(after, name) for name in identity),
                'path identity changed during read: ' + str(path))
        return b''.join(chunks), before, opened, after
    finally:
        os.close(descriptor)


def database_observation(path, label):
    raw, path_before, info, path_after = stable_open(path)
    raw_hash = sha256_bytes(raw)
    require(raw_hash == DATABASE_SHA256, 'database hash changed at ' + label)
    identity = ('st_dev', 'st_ino', 'st_mode', 'st_uid', 'st_gid', 'st_nlink')
    require(all(getattr(path_before, name) == getattr(info, name) == getattr(path_after, name)
                for name in identity), 'database path binding differs at ' + label)
    return {
        'sha256': raw_hash,
        'device': info.st_dev,
        'inode': info.st_ino,
        'mode': stat.S_IMODE(info.st_mode),
        'uid': info.st_uid,
        'gid': info.st_gid,
        'nlink': info.st_nlink,
        'size': info.st_size,
        'acl': 'no-acl' if '+' not in acl_text(path).split()[0] else 'unsafe-acl',
        'observed_at': now(),
    }


def lock_identity(info):
    return {
        'device': info.st_dev,
        'inode': info.st_ino,
        'mode': stat.S_IMODE(info.st_mode),
        'uid': info.st_uid,
        'gid': info.st_gid,
        'nlink': info.st_nlink,
        'acl': 'no-acl',
    }


def identity_record(info):
    return {
        'device': info.st_dev, 'inode': info.st_ino,
        'mode': stat.S_IMODE(info.st_mode), 'uid': info.st_uid,
        'gid': info.st_gid, 'nlink': info.st_nlink,
    }


def dict_rows(cursor):
    names = [description[0] for description in cursor.description]
    return [dict(zip(names, row)) for row in cursor.fetchall()]


def capture_schema(database, observed_identity):
    connection = sqlite3.connect('file:' + str(database) + '?mode=ro&immutable=1', uri=True)
    try:
        connection.execute('PRAGMA query_only=ON')
        integrity = connection.execute('PRAGMA integrity_check').fetchall()
        require(integrity == [('ok',)], 'database integrity check failed')
        master = [{'type': row['type'], 'name': row['name'],
                   'table': row['tbl_name'], 'sql': row['sql']}
                  for row in dict_rows(connection.execute(
                      'SELECT type,name,tbl_name,sql FROM sqlite_master ORDER BY type,name'))]
        table_info = {table: dict_rows(connection.execute('PRAGMA table_info(' + table + ')'))
                      for table in TABLES}
        index_list = {table: dict_rows(connection.execute('PRAGMA index_list(' + table + ')'))
                      for table in TABLES}
        index_xinfo = {}
        for table in TABLES:
            index_xinfo[table] = {}
            for item in index_list[table]:
                name = item['name']
                index_xinfo[table][name] = dict_rows(
                    connection.execute('PRAGMA index_xinfo("' + name + '")'))
        foreign_keys = {table: dict_rows(connection.execute('PRAGMA foreign_key_list(' + table + ')'))
                        for table in TABLES}
        user_version = connection.execute('PRAGMA user_version').fetchone()[0]
        application_id = connection.execute('PRAGMA application_id').fetchone()[0]
        journal_mode = connection.execute('PRAGMA journal_mode').fetchone()[0]
        encoding = connection.execute('PRAGMA encoding').fetchone()[0]
    finally:
        connection.close()
    require(journal_mode == 'delete' and encoding == 'UTF-8', 'database metadata differs')
    database_identity = {
        'sha256': DATABASE_SHA256,
        'device': observed_identity['device'],
        'inode': observed_identity['inode'],
        'mode': observed_identity['mode'],
        'uid': observed_identity['uid'],
        'gid': observed_identity['gid'],
        'nlink': observed_identity['nlink'],
        'size': observed_identity['size'],
        'acl': 'no-acl' if '+' not in acl_text(database).split()[0] else 'unsafe-acl',
    }
    return {
        'schema_version': 1,
        'database': database_identity,
        'sqlite_master': master,
        'table_info': table_info,
        'index_list': index_list,
        'index_xinfo': index_xinfo,
        'foreign_keys': foreign_keys,
        'application_metadata': {
            'user_version': user_version,
            'application_id': application_id,
            'journal_mode': journal_mode,
            'encoding': encoding,
        },
    }


def process_inventory():
    result = subprocess.run(['/bin/ps', '-axo', 'uid=,pid=,comm='], capture_output=True,
                            timeout=5, check=True)
    raw = result.stdout
    text = raw.decode('ascii', 'strict')
    uid_320 = uid_321 = qemu = 0
    for line in text.splitlines():
        columns = line.split(None, 2)
        require(len(columns) == 3, 'malformed process inventory')
        if columns[0] == '320':
            uid_320 += 1
        if columns[0] == '321':
            uid_321 += 1
        if 'qemu' in columns[2].lower():
            qemu += 1
    return {
        'uid_320_count': uid_320,
        'uid_321_count': uid_321,
        'qemu_count': qemu,
        'inventory_sha256': sha256_bytes(raw),
    }


def main():
    require(os.getuid() == 0 and os.geteuid() == 0, 'exclusive root parent required')
    require(not sys.argv[1:], 'no arguments accepted')
    interpreter_raw, _, _, _ = stable_open(Path(sys.executable))
    interpreter_observed = sha256_bytes(interpreter_raw)
    require(interpreter_observed == PYTHON_SHA256, 'reviewed interpreter identity differs')
    source_raw, _, _, _ = stable_open(REVIEWED_SOURCE)
    executed_raw, _, _, _ = stable_open(Path(__file__))
    parent_expected = sha256_bytes(source_raw)
    parent_observed = sha256_bytes(executed_raw)
    require(parent_expected == parent_observed, 'reviewed parent source differs')
    policy_raw, _, _, _ = stable_open(POLICY)
    policy_observed = sha256_bytes(policy_raw)
    require(policy_observed == POLICY_SHA256, 'reviewed policy bytes differ')
    started = now()
    lock_pre = LOCK.lstat()
    lock_descriptor = os.open(str(LOCK), os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0)
                              | getattr(os, 'O_NONBLOCK', 0))
    try:
        lock_open = os.fstat(lock_descriptor)
        identity_fields = ('st_dev', 'st_ino', 'st_mode', 'st_uid', 'st_gid', 'st_nlink')
        require(all(getattr(lock_pre, name) == getattr(lock_open, name) for name in identity_fields),
                'lock identity changed at open')
        lock_chunks = []
        lock_digest = hashlib.sha256()
        while True:
            chunk = os.read(lock_descriptor, 1024 * 1024)
            if not chunk:
                break
            lock_digest.update(chunk)
            lock_chunks.append(chunk)
        lock_raw = b''.join(lock_chunks)
        lock_hash = lock_digest.hexdigest()
        require(lock_hash == 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
                'launch lock bytes differ')
        require(all(getattr(lock_open, name) == getattr(os.fstat(lock_descriptor), name)
                    for name in identity_fields), 'lock identity changed during byte read')
        fcntl.flock(lock_descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
        acquired_at = now()

        active_raw, active_path_before, active_open, active_path_after = stable_open(ACTIVE)
        active_hash = sha256_bytes(active_raw)
        active = json.loads(active_raw)
        require(active_hash == '9c5194dd12ff7601917fcccc293c459db09a41da8bad9fa9983cbef618d453f8',
                'active binding hash differs')
        active_identity = ('st_dev', 'st_ino', 'st_mode', 'st_uid', 'st_gid', 'st_nlink')
        require(all(getattr(active_path_before, name) == getattr(active_open, name)
                    == getattr(active_path_after, name) for name in active_identity),
                'active descriptor/path identity differs')
        database = Path(active['directory']) / 'budget.sqlite'
        database_path_before = database.lstat()
        require((active['device'], active['inode'])
                == (database_path_before.st_dev, database_path_before.st_ino),
                'active database binding differs')

        before = database_observation(database, 'before')
        raw_schema = capture_schema(database, before)
        locked = database_observation(database, 'locked')
        processes = process_inventory()
        after = database_observation(database, 'after')
        final_active_raw, final_active_before, final_active_open, final_active_after = stable_open(ACTIVE)
        require(sha256_bytes(final_active_raw) == active_hash, 'active binding changed during capture')
        require(all(getattr(final_active_before, name) == getattr(final_active_open, name)
                    == getattr(final_active_after, name) for name in active_identity),
                'final active descriptor/path identity differs')
        sidecars = sorted(name for name in os.listdir(database.parent)
                          if name.startswith('budget.sqlite') and name != 'budget.sqlite')
        require(sidecars == [], 'database sidecars exist')
        lock_final_path = LOCK.lstat()
        require(all(getattr(lock_pre, name) == getattr(lock_final_path, name)
                    for name in identity_fields), 'lock path identity changed during capture')
        fcntl.flock(lock_descriptor, fcntl.LOCK_UN)
        released_at = now()
        lock_released = os.fstat(lock_descriptor)
        lock_post_path = LOCK.lstat()
        require(all(getattr(lock_open, name) == getattr(lock_released, name) for name in identity_fields),
                'lock identity changed during capture')
        require(all(getattr(lock_pre, name) == getattr(lock_post_path, name)
                    for name in identity_fields), 'released lock path identity differs')
    finally:
        os.close(lock_descriptor)
    completed_at = now()

    require(before['sha256'] == locked['sha256'] == after['sha256'] == DATABASE_SHA256,
            'database changed during locked capture')
    stable_fields = ('device', 'inode', 'mode', 'uid', 'gid', 'nlink', 'size', 'acl')
    require(all(before[name] == locked[name] == after[name] for name in stable_fields),
            'database metadata changed during locked capture')
    require(processes['uid_320_count'] == processes['uid_321_count'] == processes['qemu_count'] == 0,
            'sensitive process inventory is nonempty')
    lock_identities = lock_identity(lock_open)
    quiescence = {
        'schema_version': 1,
        'record_type': 'writer-exclusion-v1',
        'baseline_sha256': BASELINE_SHA256,
        'database_sha256': DATABASE_SHA256,
        'lock': {
            'path': str(LOCK),
            'protocol_version': LOCK_PROTOCOL,
            'exclusive': True,
            'all_approved_mutators_covered': True,
            'identity_before': lock_identity(lock_pre),
            'identity_opened': dict(lock_identities),
            'identity_released': lock_identity(lock_released),
            'acquired_at': acquired_at,
            'released_at': released_at,
            'acl': 'no-acl',
            'approved_protocol_sha256': LOCK_PROTOCOL_SHA256,
            'mutator_coverage_sha256': MUTATOR_COVERAGE_SHA256,
        },
        'observations': {'before': before, 'locked': locked, 'after': after},
        'sidecars': sidecars,
        'process_inventory': processes,
        'toolchain': {
            'parent_code': {'observed_sha256': parent_observed, 'expected_sha256': parent_expected},
            'interpreter': {'observed_sha256': interpreter_observed, 'expected_sha256': PYTHON_SHA256},
            'policy': {'observed_sha256': policy_observed, 'expected_sha256': POLICY_SHA256},
        },
        'review': {'status': 'unresolved', 'review_sha256': None},
        'authority': {name: False for name in AUTHORITY_NAMES},
    }
    result = {
        'schema_version': 1,
        'capture_kind': 'GRRR-z3w9-stage-d-locked-extended-schema-and-quiescence',
        'authority': {name: False for name in AUTHORITY_NAMES},
        'started_at': started,
        'completed_at': completed_at,
        'active': dict(
            active,
            sha256=active_hash,
            descriptor_identity=identity_record(active_open),
            final_descriptor_identity=identity_record(final_active_open),
            observed_while_locked=True,
        ),
        'lock_file': {
            'path': str(LOCK), 'sha256': lock_hash,
            'path_before': identity_record(lock_pre),
            'descriptor_opened': identity_record(lock_open),
            'path_locked': identity_record(lock_final_path),
            'descriptor_released': identity_record(lock_released),
            'path_released': identity_record(lock_post_path),
            'bytes_read_from_descriptor': True,
        },
        'database_path': str(database),
        'raw_schema': raw_schema,
        'quiescence': quiescence,
        'sidecars': sidecars,
        'capture_gate': 'PASS_LOCKED_READ_ONLY_EXTENDED_SCHEMA',
        'mutation_performed': False,
    }
    print(json.dumps(result, sort_keys=True, indent=2, ensure_ascii=True, allow_nan=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
