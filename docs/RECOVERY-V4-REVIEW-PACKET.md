# Recovery v4 review packet (generated, rev5)
Generated from the exact staged closure in /Library/GRRR/bootstrap/recovery-v4.
action=release-v4-stop-retain-unknowns  base=/Library/GRRR/accounting-poc2

## Staged source hashes
- accounting_recovery_planner_v4.py  3a2c6fa896ba59f864af215de3b55fe88bb83544a87fe6c425c43a506e9aa61c
- accounting_recovery_v4.py  6c1a53ff52f687d087d5565764e0c6ce414ab38dda47ec29906ad11a6c7c0336

## Record hashes
- plan.json          e3bf9163de2ceccc4f89a01b88a86328ef147c97edbc926e7786a924415907f4
- review.json        25ab92b46b38681d4e70842a9fd122817322744c8f1019291892c0b160157617
- authorization.json 9d16613a17939048890e3ab13fe2a55176e596567488058cea7bca44f4526a37

## Baseline summary (exact)
- state: {'rowid': True, 'rows': [[['i', 1], ['i', 1], ['i', 1]]]}
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


def publish(path: Path, raw: bytes, mode: int = 0o444) -> None:
    """Create a record exclusively, fsync its bytes, then set its final mode."""
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL
                         | getattr(os, 'O_NOFOLLOW', 0), 0o600)
    try:
        written = 0
        while written < len(raw):
            written += os.write(descriptor, raw[written:])
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
    os.chmod(path, mode)


def sync(path: Path) -> None:
    """Fsync a directory entry so renames and creations survive a crash."""
    descriptor = os.open(path, os.O_RDONLY | getattr(os, 'O_DIRECTORY', 0))
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


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


def encode(item: object) -> list:
    """Type-tagged cell encoding; BLOB, TEXT and numbers never collide."""
    if item is None:
        return ['n']
    if isinstance(item, bytes):
        return ['b', item.hex()]
    if isinstance(item, bool):
        return ['i', int(item)]
    if isinstance(item, int):
        return ['i', item]
    if isinstance(item, float):
        return ['f', repr(item)]
    if isinstance(item, str):
        return ['s', item]
    raise RuntimeError('unsupported sqlite value type')


def inventory(database: Path) -> dict:
    db = sqlite3.connect('file:' + str(database) + '?mode=ro', uri=True)
    try:
        result = {'database_sha256': digest(read(database)),
                  'schema': [[row[0], row[1], row[2], row[3] or '']
                             for row in db.execute(
                                 'SELECT type,name,tbl_name,sql FROM sqlite_master '
                                 'ORDER BY type,name')]}
        tables = [row[0] for row in db.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
        result['tables'] = {}
        for table in tables:
            quoted = '"' + table.replace('"', '""') + '"'
            try:
                rows = db.execute('SELECT rowid, * FROM ' + quoted
                                  + ' ORDER BY rowid').fetchall()
                hidden = True
            except sqlite3.OperationalError:
                rows = db.execute('SELECT * FROM ' + quoted).fetchall()
                hidden = False
            result['tables'][table] = {'rowid': hidden,
                                       'rows': [[encode(item) for item in row]
                                                for row in rows]}
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
    check(type(plan['version']) is int and plan['version'] == 1
          and plan['action'] == ACTION, 'plan action/version differs')
    expected_review = review_for(plan['baseline'], plan['sources'])
    check(canonical(review) == canonical(expected_review), 'independent review differs')
    check(type(review['execution_authorized']) is bool, 'review flag must be a boolean')
    check(digest(canonical(review)) == plan['review_sha256'], 'review hash differs')
    expected_authorization = authorization_for(plan, review)
    check(canonical(authorization) == canonical(expected_authorization),
          'operator authorization differs')
    check(type(authorization['execution_authorized']) is bool
          and type(authorization['exclusive_parent']) is bool,
          'authorization flags must be booleans')


def unchanged(before: dict, after: dict) -> None:
    tables = dict(before['tables'])
    state = before['tables']['state']
    expected = [list(row) for row in state['rows']]
    check(len(expected) == 1 and len(expected[0]) == (3 if state['rowid'] else 2),
          'unexpected state table shape')
    expected[0][-1] = ['i', 0]
    tables['state'] = {'rowid': state['rowid'], 'rows': expected}
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
        check(canonical(intent.get('plan')) == canonical(plan)
              and canonical(intent.get('review')) == canonical(review)
              and canonical(intent.get('authorization')) == canonical(authorization),
              'existing recovery differs from this request')
        return verify(base, owner=owner)
    check(canonical(snapshot(base, owner=owner, active_uid=active_uid))
          == canonical(plan['baseline']), 'baseline changed since the plan was made')
    recovery.mkdir(mode=0o700)
    publish(recovery / 'intent.json', canonical(
        {'version': 1, 'outcome': 'prepared-not-success', 'plan': plan,
         'review': review, 'authorization': authorization}))
    sync(recovery)
    sync(base)
    found = binding(base, owner=owner)
    database = found['database']
    db = sqlite3.connect(str(database), isolation_level=None)
    try:
        db.execute('PRAGMA foreign_keys=ON')
        db.execute('PRAGMA synchronous=FULL')
        db.execute('BEGIN IMMEDIATE')
        before = snapshot(base, owner=owner, active_uid=active_uid)
        check(canonical(before) == canonical(plan['baseline']),
              'baseline drifted after the exclusive guard was acquired')
        state = before['inventory']['tables']['state']['rows']
        check(len(state) == 1 and state[0][-1] == ['i', 1],
              'store is not stopped; recovery refuses')
        pre = database.lstat()
        check((pre.st_dev, pre.st_ino) == (before['metadata']['database']['device'],
                                           before['metadata']['database']['inode']),
              'store database moved after the baseline check')
        changed = db.execute('UPDATE state SET stopped=0 WHERE id=1 AND stopped=1').rowcount
        check(changed == 1, 'stop bit was not released exactly once')
        db.commit()
    except BaseException:
        db.rollback()
        raise
    finally:
        db.close()
    try:
        post = database.lstat()
        check((post.st_dev, post.st_ino) == (pre.st_dev, pre.st_ino),
              'store database was replaced during recovery')
        after = inventory(database)
        unchanged(before['inventory'], after)
        receipt = {'version': 1, 'outcome': 'released-stop-retained-unknowns',
                   'active_sha256': digest(read(base / 'active.json')),
                   'inventory_before': digest(canonical(before['inventory'])),
                   'inventory_after': digest(canonical(after)),
                   'database_sha256_before': before['inventory']['database_sha256'],
                   'database_sha256_after': after['database_sha256'],
                   'stopped_before': 1, 'stopped_after': 0,
                   'historical_unknowns': 'unresolved', 'spendable': 'unknown',
                   'execution_authorized': True}
        publish(recovery / 'prior-active.json', read(base / 'active.json'))
        publish(recovery / 'receipt.json', canonical(receipt))
        sync(recovery)
        sync(base)
        _verify_state(base, owner, published=False)
        publish(recovery / 'complete.json', canonical(
            {'binding_sha256': receipt['active_sha256'],
             'outcome': 'published-durable',
             'receipt_sha256': digest(canonical(receipt)),
             'execution_authorized': True}))
        sync(recovery)
        sync(base)
        os.chmod(recovery / 'intent.json', 0o444)
        os.chmod(recovery / 'prior-active.json', 0o444)
        os.chmod(recovery / 'receipt.json', 0o444)
        os.chmod(recovery / 'complete.json', 0o444)
        os.chmod(recovery, 0o555)
        sync(base)
        return verify(base, owner=owner)
    except BaseException:
        # Never leave the store released without a durable, verified completion.
        failure = []
        try:
            os.chmod(recovery, 0o700)
        except Exception as error:
            failure.append('namespace: ' + str(error))
        for name in ('intent.json', 'prior-active.json', 'receipt.json', 'complete.json'):
            try:
                os.chmod(recovery / name, 0o600)
            except FileNotFoundError:
                continue
            except Exception as error:
                failure.append(name + ': ' + str(error))
        try:
            (recovery / 'complete.json').unlink()
            sync(recovery)
        except FileNotFoundError:
            pass
        except Exception as error:
            failure.append('invalidate: ' + str(error))
        try:
            restore = sqlite3.connect(str(database), isolation_level=None)
            try:
                restore.execute('PRAGMA synchronous=FULL')
                current = restore.execute(
                    'SELECT stopped FROM state WHERE id=1').fetchone()
                if current != (1,):
                    restored = restore.execute(
                        'UPDATE state SET stopped=1 WHERE id=1 AND stopped=0').rowcount
                    restore.commit()
                    check(restored == 1, 'restore affected %d rows' % restored)
                    current = restore.execute(
                        'SELECT stopped FROM state WHERE id=1').fetchone()
                check(current == (1,), 'restored stop bit did not read back as 1')
            finally:
                restore.close()
        except Exception as restore_error:
            failure.append('restore: ' + str(restore_error))
        try:
            publish(recovery / 'incomplete.json', canonical(
                {'outcome': 'recovery-incomplete',
                 'reason': '; '.join(failure)[:512] or 'post-publish verification failed'}))
            sync(recovery)
            os.chmod(recovery, 0o555)
            sync(base)
        except Exception as marker_error:
            failure.append('marker: ' + str(marker_error))
        if failure:
            raise RuntimeError('recovery failed and could not be fully recorded; '
                               'operator recovery required: ' + '; '.join(failure))
        raise


def _verify_state(base: Path, owner: int, *, published: bool) -> dict:
    recovery = base / 'recovery-v4'
    check(recovery.is_dir() and not recovery.is_symlink(), 'recovery namespace missing')
    names = {item.name for item in recovery.iterdir()}
    check('incomplete.json' not in names, 'recovery failed before durable completion')
    required = {'intent.json', 'prior-active.json', 'receipt.json'}
    if published:
        required.add('complete.json')
    check(names == required,
          'partial or foreign recovery records')
    intent = json.loads(read(recovery / 'intent.json'))
    receipt = json.loads(read(recovery / 'receipt.json'))
    approval(intent['plan'], intent['review'], intent['authorization'])
    check(receipt['outcome'] == 'released-stop-retained-unknowns'
          and receipt['stopped_before'] == 1 and receipt['stopped_after'] == 0,
          'receipt differs')
    if published:
        complete = json.loads(read(recovery / 'complete.json'))
        check(complete['receipt_sha256'] == digest(canonical(receipt))
              and complete['outcome'] == 'published-durable', 'completion differs')
        check(complete['binding_sha256'] == receipt['active_sha256']
              == digest(read(base / 'active.json')), 'completion binding hash differs')
    else:
        check(receipt['active_sha256'] == digest(read(base / 'active.json')),
              'receipt binding hash differs')
    check(read(recovery / 'prior-active.json') == read(base / 'active.json'),
          'prior active binding differs from the current binding')
    found = binding(base, owner=owner)
    planned = intent['plan']['baseline']['metadata']
    check(metadata(base / 'active.json', planned['active']['uid'], 0o444) == planned['active']
          and metadata(found['database'], planned['database']['uid'], 0o600) == planned['database']
          and metadata(found['directory'], planned['directory']['uid'], 0o700, True)
          == planned['directory'], 'post-install metadata drift')
    current = inventory(found['database'])
    state = current['tables']['state']['rows']
    check(len(state) == 1 and state[0][-1] == ['i', 0], 'store is not released')
    check(current['database_sha256'] == receipt['database_sha256_after'],
          'current database bytes differ from the released receipt')
    return {'outcome': 'published-durable' if published else 'verified-not-published',
            'receipt': receipt}


def verify(base: Path = BASE, *, owner: int = 320) -> dict:
    recovery = base / 'recovery-v4'
    check(recovery.is_dir() and not recovery.is_symlink()
          and stat.S_IMODE(recovery.lstat().st_mode) == 0o555,
          'recovery namespace differs')
    return _verify_state(base, owner, published=True)

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
