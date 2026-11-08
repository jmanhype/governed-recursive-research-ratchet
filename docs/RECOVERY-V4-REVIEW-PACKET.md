# Recovery v4 review packet (generated, rev4)
Generated from the exact staged closure in /Library/GRRR/bootstrap/recovery-v4.
action=release-v4-stop-retain-unknowns  base=/Library/GRRR/accounting-poc2

## Staged source hashes
- accounting_recovery_planner_v4.py  3a2c6fa896ba59f864af215de3b55fe88bb83544a87fe6c425c43a506e9aa61c
- accounting_recovery_v4.py  90ffa6cfe7ec012e6a1e7df325c4ba5d25da9da04dcc1a5d603d6ce26e3cead7

## Record hashes
- plan.json          625fda3e9e1eff53cc706ab28efa29466fef080783612ff33308e822456cf86f
- review.json        d0a4296a577139ead3557ce428654163907d6caa87868a90c484ae81f17953ec
- authorization.json baee97186fd636dbfc8fb865a518fd7714410d22efd8d9c6fbd00ce7e4c2f842

## Baseline summary (exact)
- stopped: [[1, 1]]
- tables: {'metering': 1, 'overhead': 0, 'reservations': 2, 'state': 1, 'store_identity': 1}
- schema objects: 10
- database_sha256: 5cade36d1c437635d5881448961753b2b5306c595a893caba70b5fd8e0bac1d3

## Staged source (verbatim)

### accounting_recovery_v4.py

~~~python
"""Reviewed v4 stop release: unhalt the live store, retain every unknown.

This is not reconciliation and grants no spendability claim. It performs one
transition — `state.stopped 1 -> 0` — and refuses if any other row changed.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import sqlite3
import stat

BASE = Path('/Library/GRRR/accounting-poc2')
ACTIVE = BASE / 'active.json'
ACTION = 'release-v4-stop-retain-unknowns'
CEILINGS = {'poc': [5000, 21600000000, 3600000000],
            'milestone': [15000, 86400000000, 10800000000]}


def canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=True, allow_nan=False).encode('ascii')


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def check(condition: bool, reason: str) -> None:
    if not condition:
        raise RuntimeError(reason)


def read(path: Path, maximum: int = 1 << 24) -> bytes:
    descriptor = os.open(path, os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0))
    try:
        info = os.fstat(descriptor)
        check(stat.S_ISREG(info.st_mode) and not stat.S_ISLNK(info.st_mode)
              and info.st_nlink == 1 and info.st_size <= maximum,
              'unsafe protected file')
        chunks = []
        while True:
            chunk = os.read(descriptor, 65536)
            if not chunk:
                break
            chunks.append(chunk)
            check(sum(len(item) for item in chunks) <= maximum, 'protected file too large')
        return b''.join(chunks)
    finally:
        os.close(descriptor)


def metadata(path: Path, uid: int, mode: int, directory: bool = False) -> dict:
    info = path.lstat()
    kind_ok = stat.S_ISDIR(info.st_mode) if directory else stat.S_ISREG(info.st_mode)
    check(kind_ok and not stat.S_ISLNK(info.st_mode), 'protected kind differs')
    check(info.st_uid == uid and stat.S_IMODE(info.st_mode) == mode,
          'protected owner/mode differs')
    if not directory:
        check(info.st_nlink == 1, 'protected file links differ')
    return {'uid': info.st_uid, 'gid': info.st_gid,
            'mode': stat.S_IMODE(info.st_mode), 'inode': info.st_ino,
            'device': info.st_dev, 'links': info.st_nlink}


def binding(base: Path = BASE, *, owner: int = 320) -> dict:
    value = json.loads(read(base / 'active.json'))
    check(set(value) == {'campaign', 'device', 'directory', 'inode', 'prior_history_receipt',
                         'profiles', 'store_id', 'version'}, 'active binding fields differ')
    check(type(value['version']) is int and value['version'] == 4, 'not the v4 store')
    check('independent-replay' in value['profiles'], 'replay profile absent')
    directory = Path(value['directory'])
    check(directory.parent == base and directory.name == value['store_id'],
          'store outside the protected namespace')
    info = directory.lstat()
    check(stat.S_ISDIR(info.st_mode) and info.st_uid == owner and info.st_mode & 0o077 == 0,
          'store directory ownership/mode differs')
    database = directory / 'budget.sqlite'
    db_info = database.lstat()
    check(stat.S_ISREG(db_info.st_mode) and db_info.st_uid == owner
          and stat.S_IMODE(db_info.st_mode) == 0o600, 'store database ownership/mode differs')
    check(db_info.st_dev == value['device'] and db_info.st_ino == value['inode'],
          'active binding device/inode differs from the store database')
    return {'value': value, 'directory': directory, 'database': database}


def inventory(database: Path) -> dict:
    db = sqlite3.connect('file:' + str(database) + '?mode=ro', uri=True)
    try:
        result = {'database_sha256': digest(read(database)),
                  'schema': [[row[0], row[1], row[2], row[3] or '']
                             for row in db.execute(
                                 'SELECT type,name,tbl_name,sql FROM sqlite_master '
                                 'ORDER BY type,name')]}
        tables = [row[0] for row in db.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' "
            'ORDER BY name')]
        result['tables'] = {}
        for table in tables:
            rows = db.execute('SELECT * FROM "' + table + '"').fetchall()
            result['tables'][table] = [
                [item.hex() if isinstance(item, bytes) else item for item in row]
                for row in rows]
        return result
    finally:
        db.close()


def snapshot(base: Path = BASE, *, owner: int = 320, active_uid: int = 0) -> dict:
    found = binding(base, owner=owner)
    active_meta = metadata(base / 'active.json', active_uid, 0o444)
    return {'active_hex': read(base / 'active.json').hex(),
            'metadata': {'active': active_meta,
                         'database': metadata(found['database'], owner, 0o600),
                         'directory': metadata(found['directory'], owner, 0o700, True)},
            'inventory': inventory(found['database'])}


def sources(directory: Path) -> dict:
    return {name: digest(read(directory / name))
            for name in ('accounting_recovery_v4.py', 'accounting_recovery_planner_v4.py')}


def review_for(baseline: dict, source_hashes: dict) -> dict:
    return {'decision': 'approved-v4-release', 'action': ACTION,
            'baseline_sha256': digest(canonical(baseline)), 'sources': source_hashes,
            'ceilings': CEILINGS, 'allowed_mutations': ['release-stop'],
            'historical_unknowns': 'unresolved', 'spendable': 'unknown',
            'execution_authorized': True}


def plan_for(baseline: dict, source_hashes: dict) -> dict:
    review = review_for(baseline, source_hashes)
    return {'version': 1, 'action': ACTION, 'baseline': baseline,
            'sources': source_hashes, 'review_sha256': digest(canonical(review))}


def authorization_for(plan: dict, review: dict) -> dict:
    return {'principal': 'operator', 'action': ACTION,
            'plan_sha256': digest(canonical(plan)),
            'review_sha256': digest(canonical(review)),
            'baseline_sha256': review['baseline_sha256'],
            'sources': plan['sources'], 'exclusive_parent': True,
            'execution_authorized': True}


def approval(plan: dict, review: dict, authorization: dict) -> None:
    check(set(plan) == {'version', 'action', 'baseline', 'sources', 'review_sha256'},
          'plan fields differ')
    check(plan['version'] == 1 and plan['action'] == ACTION, 'plan action/version differs')
    check(review == review_for(plan['baseline'], plan['sources']),
          'independent review differs')
    check(digest(canonical(review)) == plan['review_sha256'], 'review hash differs')
    check(authorization == authorization_for(plan, review), 'operator authorization differs')


def unchanged(before: dict, after: dict) -> None:
    tables = {name: rows for name, rows in before['tables'].items()}
    tables['state'] = [[1, 0]]
    check(after['schema'] == before['schema'] and after['tables'] == tables,
          'history, schema, holds or unknown rows changed')


def apply_install(base: Path, plan: dict, review: dict, authorization: dict,
                  *, privileged: bool, owner: int = 320, active_uid: int = 0) -> dict:
    if privileged:
        check(os.getuid() == 0 and os.geteuid() == 0, 'root-only recovery required')
        check(str(Path(__file__).resolve()).startswith('/Library/GRRR/bootstrap/recovery-v4/'),
              'noncanonical recovery closure')
    approval(plan, review, authorization)
    recovery = base / 'recovery-v4'
    if recovery.exists():
        intent = json.loads(read(recovery / 'intent.json'))
        check(intent.get('plan') == plan and intent.get('review') == review
              and intent.get('authorization') == authorization,
              'existing recovery differs from this request')
        return verify(base, owner=owner)
    check(plan['baseline'] == snapshot(base, owner=owner, active_uid=active_uid),
          'baseline changed since the plan was made')
    recovery.mkdir(mode=0o700)
    (recovery / 'intent.json').write_bytes(canonical(
        {'version': 1, 'outcome': 'prepared-not-success', 'plan': plan,
         'review': review, 'authorization': authorization}))
    found = binding(base, owner=owner)
    database = found['database']
    pre = database.lstat()
    before = inventory(database)
    check(before['tables']['state'] == [[1, 1]], 'store is not stopped; recovery refuses')
    db = sqlite3.connect(str(database), isolation_level=None)
    try:
        db.execute('PRAGMA foreign_keys=ON')
        db.execute('BEGIN IMMEDIATE')
        changed = db.execute('UPDATE state SET stopped=0 WHERE id=1 AND stopped=1').rowcount
        check(changed == 1, 'stop bit was not released exactly once')
        db.commit()
    except BaseException:
        db.rollback()
        raise
    finally:
        db.close()
    post = database.lstat()
    check((post.st_dev, post.st_ino) == (pre.st_dev, pre.st_ino),
          'store database was replaced during recovery')
    try:
        after = inventory(database)
        unchanged(before, after)
        receipt = {'version': 1, 'outcome': 'released-stop-retained-unknowns',
                   'active_sha256': digest(read(base / 'active.json')),
                   'inventory_before': digest(canonical(before)),
                   'inventory_after': digest(canonical(after)),
                   'database_sha256_before': before['database_sha256'],
                   'database_sha256_after': after['database_sha256'],
                   'stopped_before': 1, 'stopped_after': 0,
                   'historical_unknowns': 'unresolved', 'spendable': 'unknown',
                   'execution_authorized': True}
        (recovery / 'prior-active.json').write_bytes(read(base / 'active.json'))
        (recovery / 'receipt.json').write_bytes(canonical(receipt))
        (recovery / 'complete.json').write_bytes(canonical(
            {'binding_sha256': receipt['active_sha256'],
             'outcome': 'published-durable',
             'receipt_sha256': digest(canonical(receipt)),
             'execution_authorized': True}))
        for name in ('intent.json', 'prior-active.json', 'receipt.json', 'complete.json'):
            os.chmod(recovery / name, 0o444)
        os.chmod(recovery, 0o555)
    except BaseException:
        # Never leave the store released without a durable, verified completion.
        try:
            restore = sqlite3.connect(str(database), isolation_level=None)
            restore.execute('UPDATE state SET stopped=1 WHERE id=1 AND stopped=0')
            restore.commit()
            restore.close()
        except Exception as restore_error:
            try:
                (recovery / 'incomplete.json').write_bytes(canonical(
                    {'outcome': 'recovery-incomplete',
                     'reason': str(restore_error)[:512]}))
            except Exception as marker_error:
                raise RuntimeError(
                    'restore and incomplete-record both failed: '
                    + str(restore_error) + ' / ' + str(marker_error)) from restore_error
            raise RuntimeError(
                'store restoration failed; incomplete marker written: '
                + str(restore_error)) from restore_error
        raise
    return verify(base, owner=owner)


def verify(base: Path = BASE, *, owner: int = 320) -> dict:
    recovery = base / 'recovery-v4'
    check(recovery.is_dir() and stat.S_IMODE(recovery.lstat().st_mode) == 0o555,
          'recovery namespace differs')
    names = {item.name for item in recovery.iterdir()}
    check('incomplete.json' not in names, 'recovery failed before durable completion')
    check(names == {'intent.json', 'prior-active.json', 'receipt.json', 'complete.json'},
          'partial or foreign recovery records')
    intent = json.loads(read(recovery / 'intent.json'))
    receipt = json.loads(read(recovery / 'receipt.json'))
    complete = json.loads(read(recovery / 'complete.json'))
    approval(intent['plan'], intent['review'], intent['authorization'])
    check(receipt['outcome'] == 'released-stop-retained-unknowns'
          and receipt['stopped_before'] == 1 and receipt['stopped_after'] == 0,
          'receipt differs')
    check(complete['receipt_sha256'] == digest(canonical(receipt))
          and complete['outcome'] == 'published-durable', 'completion differs')
    check(complete['binding_sha256'] == receipt['active_sha256'] == digest(read(base / 'active.json')),
          'completion binding hash differs')
    check(read(recovery / 'prior-active.json') == read(base / 'active.json'),
          'prior active binding differs from the current binding')
    found = binding(base, owner=owner)
    planned = intent['plan']['baseline']['metadata']
    check(metadata(base / 'active.json', planned['active']['uid'], 0o444) == planned['active']
          and metadata(found['database'], planned['database']['uid'], 0o600) == planned['database']
          and metadata(found['directory'], planned['directory']['uid'], 0o700, True)
          == planned['directory'], 'post-install metadata drift')
    current = inventory(found['database'])
    check(current['tables']['state'] == [[1, 0]], 'store is not released')
    check(current['database_sha256'] == receipt['database_sha256_after'],
          'current database bytes differ from the released receipt')
    return {'outcome': complete['outcome'], 'receipt': receipt}

~~~

### accounting_recovery_planner_v4.py

~~~python
"""Plan builder for the reviewed v4 stop release. Read-only."""
from pathlib import Path

from accounting_recovery_v4 import (BASE, authorization_for, plan_for, review_for,
                                    snapshot, sources)


def build(base: Path = BASE, directory: Path = None, *, owner: int = 320,
          active_uid: int = 0) -> dict:
    directory = Path(directory) if directory is not None else Path(__file__).parent
    baseline = snapshot(base, owner=owner, active_uid=active_uid)
    source_hashes = sources(directory)
    review = review_for(baseline, source_hashes)
    plan = plan_for(baseline, source_hashes)
    return {'plan': plan, 'review': review,
            'authorization': authorization_for(plan, review)}

~~~
