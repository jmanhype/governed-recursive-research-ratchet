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
TABLES = ('reservations', 'metering', 'overhead', 'state', 'store_identity')


def canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=True, allow_nan=False).encode('ascii')


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def check(condition: bool, reason: str) -> None:
    if not condition:
        raise RuntimeError(reason)


def read(path: Path, maximum: int = 1 << 24) -> bytes:
    info = path.lstat()
    check(stat.S_ISREG(info.st_mode) and not stat.S_ISLNK(info.st_mode)
          and info.st_nlink == 1 and info.st_size <= maximum, 'unsafe protected file')
    return path.read_bytes()


def metadata(path: Path, uid: int, mode: int, directory: bool = False) -> dict:
    info = path.lstat()
    kind_ok = stat.S_ISDIR(info.st_mode) if directory else stat.S_ISREG(info.st_mode)
    check(kind_ok and not stat.S_ISLNK(info.st_mode), 'protected kind differs')
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
    return {'value': value, 'directory': directory, 'database': database}


def inventory(database: Path) -> dict:
    db = sqlite3.connect('file:' + str(database) + '?mode=ro', uri=True)
    try:
        result = {'database_sha256': digest(read(database))}
        for table in TABLES:
            rows = db.execute('SELECT * FROM ' + table).fetchall()
            result[table] = [[item.hex() if isinstance(item, bytes) else item for item in row]
                             for row in rows]
        return result
    finally:
        db.close()


def snapshot(base: Path = BASE, *, owner: int = 320, active_uid: int = 0) -> dict:
    found = binding(base, owner=owner)
    active_meta = metadata(base / 'active.json', 0, 0o444)
    check(active_meta['uid'] == active_uid and active_meta['mode'] == 0o444
          and active_meta['links'] == 1, 'active binding metadata differs')
    return {'active_hex': read(base / 'active.json').hex(),
            'metadata': {'active': active_meta,
                         'database': metadata(found['database'], 320, 0o600),
                         'directory': metadata(found['directory'], 320, 0o700, True)},
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
    check(after == dict(before, state=[[1, 0]], database_sha256=after['database_sha256']),
          'history, holds or unknown rows changed')


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
    before = inventory(database)
    check(before['state'] == [[1, 1]], 'store is not stopped; recovery refuses')
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
    after = inventory(database)
    unchanged(before, after)
    receipt = {'version': 1, 'outcome': 'released-stop-retained-unknowns',
               'active_sha256': digest(read(base / 'active.json')),
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
    return verify(base, owner=owner)


def verify(base: Path = BASE, *, owner: int = 320) -> dict:
    recovery = base / 'recovery-v4'
    check(recovery.is_dir() and stat.S_IMODE(recovery.lstat().st_mode) == 0o555,
          'recovery namespace differs')
    names = {item.name for item in recovery.iterdir()}
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
    check(inventory(binding(base, owner=owner)['database'])['state'] == [[1, 0]], 'store is not released')
    return {'outcome': complete['outcome'], 'receipt': receipt}
