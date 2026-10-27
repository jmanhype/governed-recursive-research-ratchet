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


def file_hash(path):
    descriptor = os.open(str(path), os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0)
                         | getattr(os, 'O_NONBLOCK', 0))
    try:
        info = os.fstat(descriptor)
        require(stat.S_ISREG(info.st_mode), 'not a regular file: ' + str(path))
        digest = hashlib.sha256()
        while True:
            chunk = os.read(descriptor, 1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
        return digest.hexdigest(), os.fstat(descriptor)
    finally:
        os.close(descriptor)


def database_observation(path, label):
    raw_hash, info = file_hash(path)
    require(raw_hash == DATABASE_SHA256, 'database hash changed at ' + label)
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


def stat_record(path):
    info = path.lstat()
    return {
        'path': str(path), 'sha256': sha256_bytes(path.read_bytes()),
        'device': info.st_dev, 'inode': info.st_ino,
        'mode': stat.S_IMODE(info.st_mode), 'uid': info.st_uid,
        'gid': info.st_gid, 'nlink': info.st_nlink, 'size': info.st_size,
        'acl': acl_text(path),
    }


def dict_rows(cursor):
    names = [description[0] for description in cursor.description]
    return [dict(zip(names, row)) for row in cursor.fetchall()]


def capture_schema(database):
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
    info = database.lstat()
    database_identity = {
        'sha256': DATABASE_SHA256,
        'device': info.st_dev,
        'inode': info.st_ino,
        'mode': stat.S_IMODE(info.st_mode),
        'uid': info.st_uid,
        'gid': info.st_gid,
        'nlink': info.st_nlink,
        'size': info.st_size,
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
    require(Path(sys.executable).read_bytes() and sha256_bytes(Path(sys.executable).read_bytes()) == PYTHON_SHA256,
            'reviewed interpreter identity differs')
    started = now()
    active_raw, active_info = file_hash(ACTIVE)
    active = json.loads(ACTIVE.read_bytes())
    require(active_raw == '9c5194dd12ff7601917fcccc293c459db09a41da8bad9fa9983cbef618d453f8',
            'active binding hash differs')
    database = Path(active['directory']) / 'budget.sqlite'
    require((active['device'], active['inode']) == (database.lstat().st_dev, database.lstat().st_ino),
            'active database binding differs')

    lock_pre = LOCK.lstat()
    lock_hash = sha256_bytes(LOCK.read_bytes())
    require(lock_hash == 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
            'launch lock bytes differ')
    lock_descriptor = os.open(str(LOCK), os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0)
                              | getattr(os, 'O_NONBLOCK', 0))
    try:
        lock_open = os.fstat(lock_descriptor)
        identity_fields = ('st_dev', 'st_ino', 'st_mode', 'st_uid', 'st_gid', 'st_nlink')
        require(all(getattr(lock_pre, name) == getattr(lock_open, name) for name in identity_fields),
                'lock identity changed at open')
        fcntl.flock(lock_descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
        acquired_at = now()
        before = database_observation(database, 'before')
        raw_schema = capture_schema(database)
        locked = database_observation(database, 'locked')
        processes = process_inventory()
        after = database_observation(database, 'after')
        fcntl.flock(lock_descriptor, fcntl.LOCK_UN)
        released_at = now()
        lock_released = os.fstat(lock_descriptor)
        require(all(getattr(lock_open, name) == getattr(lock_released, name) for name in identity_fields),
                'lock identity changed during capture')
    finally:
        os.close(lock_descriptor)

    require(before['sha256'] == locked['sha256'] == after['sha256'] == DATABASE_SHA256,
            'database changed during locked capture')
    stable_fields = ('device', 'inode', 'mode', 'uid', 'gid', 'nlink', 'size', 'acl')
    require(all(before[name] == locked[name] == after[name] for name in stable_fields),
            'database metadata changed during locked capture')
    require(processes['uid_320_count'] == processes['uid_321_count'] == processes['qemu_count'] == 0,
            'sensitive process inventory is nonempty')
    sidecars = sorted(path.name for path in database.parent.iterdir()
                      if path.name.startswith('budget.sqlite') and path.name != 'budget.sqlite')
    require(sidecars == [], 'database sidecars exist')
    parent_hash = sha256_bytes(Path(__file__).read_bytes())
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
            'parent_code': {'observed_sha256': parent_hash, 'expected_sha256': parent_hash},
            'interpreter': {'observed_sha256': PYTHON_SHA256, 'expected_sha256': PYTHON_SHA256},
            'policy': {'observed_sha256': POLICY_SHA256, 'expected_sha256': POLICY_SHA256},
        },
        'review': {'status': 'unresolved', 'review_sha256': None},
        'authority': {name: False for name in AUTHORITY_NAMES},
    }
    completed = now()
    result = {
        'schema_version': 1,
        'capture_kind': 'GRRR-z3w9-stage-d-locked-extended-schema-and-quiescence',
        'authority': {name: False for name in AUTHORITY_NAMES},
        'started_at': started,
        'completed_at': completed,
        'active': dict(active, sha256=active_raw, stat=stat_record(ACTIVE)),
        'lock_file': dict(stat_record(LOCK), sha256=lock_hash),
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
