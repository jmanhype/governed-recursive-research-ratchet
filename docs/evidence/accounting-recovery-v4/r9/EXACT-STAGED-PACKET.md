# Recovery v4 exact review packet, r9

Prepared for review; not independent approval or execution proof.

Action: release-v4-stop-retain-unknowns. No reconciliation or replay.

## Exact staged hashes
- `accounting_recovery_planner_v4.py`: `3a2c6fa896ba59f864af215de3b55fe88bb83544a87fe6c425c43a506e9aa61c`
- `accounting_recovery_v4.py`: `79bce91b4a5054bc2e59e05e9d3e55f924715f2ee44f34a61cc716b7a72c79d7`
- `records/authorization.json`: `5d1deb5fe0c26e378233c0a1fa1c1104fa60ce8aaee38673b2fd4efa9f6e026e`
- `records/plan.json`: `4603b443783e8bfc91f6a1c1c408f54cd8f3f073aaf35f14af9278d01d8f0953`
- `records/review.json`: `1bcb3351e435ff476c35e5df713b6facd519a9fa96d0670db9f2df13388ea2dc`

## Exact baseline
```json
{"active_hex":"7b2263616d706169676e223a2266616262346130333532643836373130663039626537643930373936303632633533623730643636613938633866626533393035633736613866396661376639222c22646576696365223a31363737373232392c226469726563746f7279223a222f4c6962726172792f475252522f6163636f756e74696e672d706f63322f61313432636162623562616464373962313062343634643031393831383463616632313830383866346333353263313632343037366237323037383133353330222c22696e6f6465223a3731303536303738332c227072696f725f686973746f72795f72656365697074223a2236643364356230393263306565383237336136353763383338323364383436356232313566326231623636656336323764666465326439366232316665353837222c2270726f66696c6573223a5b22696e646570656e64656e742d7265706c6179225d2c2273746f72655f6964223a2261313432636162623562616464373962313062343634643031393831383463616632313830383866346333353263313632343037366237323037383133353330222c2276657273696f6e223a347d0a","inventory":{"database_sha256":"5cade36d1c437635d5881448961753b2b5306c595a893caba70b5fd8e0bac1d3","header":{"application_id":0,"read_version":1,"schema_cookie":5,"user_version":0,"write_version":1},"schema":[["index","sqlite_autoindex_metering_1","metering",""],["index","sqlite_autoindex_metering_2","metering",""],["index","sqlite_autoindex_overhead_1","overhead",""],["index","sqlite_autoindex_reservations_1","reservations",""],["index","sqlite_autoindex_reservations_2","reservations",""],["table","metering","metering","CREATE TABLE metering(\n            id TEXT PRIMARY KEY, reservation TEXT UNIQUE NOT NULL,\n            body BLOB NOT NULL)"],["table","overhead","overhead","CREATE TABLE overhead(\n            key TEXT PRIMARY KEY, category TEXT NOT NULL,\n            duration_us INTEGER NOT NULL)"],["table","reservations","reservations","CREATE TABLE reservations(\n            id TEXT PRIMARY KEY, key TEXT UNIQUE NOT NULL,\n            binding BLOB NOT NULL, run TEXT NOT NULL, stage TEXT NOT NULL,\n            maximum BLOB NOT NULL, actual BLOB, receipt TEXT)"],["table","state","state","CREATE TABLE state(\n            id INTEGER PRIMARY KEY CHECK(id=1), stopped INTEGER NOT NULL)"],["table","store_identity","store_identity","CREATE TABLE store_identity(\n            campaign TEXT NOT NULL, store_id TEXT NOT NULL,\n            prior_history_receipt TEXT NOT NULL)"]],"tables":{"metering":{"rowid":true,"rows":[[["i",1],["s","fecaf6a5e0491f0de71d70eccbcf4d692f3ea1a7d17d1dd9c6ddd88c2bba6f49"],["s","44a4ce6ec75647f982c9f728880d1605"],["b","7b2265766964656e6365223a2265386336653537303738613339653936653939363062623834616631616636373735343733663364643639333665306535363563336139373763653464346465222c227265736572766174696f6e223a223434613463653665633735363437663938326339663732383838306431363035222c227573616765223a7b2263757272656e6379223a22555344222c22657865637574696f6e5f7573223a34353334303032332c226d6f6e65795f63656e7473223a302c227265766965775f7573223a307d7d"]]]},"overhead":{"rowid":true,"rows":[]},"reservations":{"rowid":true,"rows":[[["i",1],["s","44a4ce6ec75647f982c9f728880d1605"],["s","2b0e24287d524dcfba4611a9c601e398"],["b","7b2262696e64696e67223a2230333736353635343035666434643738613064326232363938366632383230306235616635303231343231353137653035613864316663623135316539303362222c226d6178696d756d223a7b2263757272656e6379223a22555344222c22657865637574696f6e5f7573223a3438303030303030302c226d6f6e65795f63656e7473223a302c227265766965775f7573223a307d2c2272756e223a226463346531353765653039343437393361353935336638383035333032353338222c227374616765223a22706f63227d"],["s","dc4e157ee0944793a5953f8805302538"],["s","poc"],["b","7b2263757272656e6379223a22555344222c22657865637574696f6e5f7573223a3438303030303030302c226d6f6e65795f63656e7473223a302c227265766965775f7573223a307d"],["b","7b2263757272656e6379223a22555344222c22657865637574696f6e5f7573223a34353334303032332c226d6f6e65795f63656e7473223a302c227265766965775f7573223a307d"],["s","fecaf6a5e0491f0de71d70eccbcf4d692f3ea1a7d17d1dd9c6ddd88c2bba6f49"]],[["i",2],["s","a549efbdca5743878052c0226c617c1f"],["s","d2454951509449de8b12e70efa487dfc"],["b","7b2262696e64696e67223a2230333736353635343035666434643738613064326232363938366632383230306235616635303231343231353137653035613864316663623135316539303362222c226d6178696d756d223a7b2263757272656e6379223a22555344222c22657865637574696f6e5f7573223a3438303030303030302c226d6f6e65795f63656e7473223a302c227265766965775f7573223a307d2c2272756e223a226463346531353765653039343437393361353935336638383035333032353338222c227374616765223a22706f63227d"],["s","dc4e157ee0944793a5953f8805302538"],["s","poc"],["b","7b2263757272656e6379223a22555344222c22657865637574696f6e5f7573223a3438303030303030302c226d6f6e65795f63656e7473223a302c227265766965775f7573223a307d"],["n"],["n"]]]},"state":{"rowid":true,"rows":[[["i",1],["i",1],["i",1]]]},"store_identity":{"rowid":true,"rows":[[["i",1],["s","fabb4a0352d86710f09be7d90796062c53b70d66a98c8fbe3905c76a8f9fa7f9"],["s","a142cabb5badd79b10b464d0198184caf218088f4c352c1624076b7207813530"],["s","6d3d5b092c0ee8273a657c83823d8465b215f2b1b66ec627dfde2d96b21fe587"]]]}}},"metadata":{"active":{"device":16777229,"gid":0,"inode":685895848,"links":1,"mode":292,"uid":0},"database":{"device":16777229,"gid":320,"inode":710560783,"links":1,"mode":384,"uid":320},"directory":{"device":16777229,"gid":320,"inode":710560782,"links":3,"mode":448,"uid":320}}}
```

## accounting_recovery_v4.py
```python
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
        os.fchmod(descriptor, mode)
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


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


def header(raw: bytes) -> dict:
    """Stable SQLite header fields; excludes counters that a commit must change."""
    check(len(raw) >= 100 and raw[:16] == b'SQLite format 3\x00', 'not a sqlite database')
    return {'write_version': raw[18], 'read_version': raw[19],
            'schema_cookie': int.from_bytes(raw[40:44], 'big'),
            'user_version': int.from_bytes(raw[60:64], 'big'),
            'application_id': int.from_bytes(raw[68:72], 'big')}


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
        raw = read(database)
        result = {'database_sha256': digest(raw), 'header': header(raw),
                  'schema': [[row[0], row[1], row[2], row[3] or '']
                             for row in db.execute(
                                 'SELECT type,name,tbl_name,sql FROM sqlite_master '
                                 'ORDER BY type,name')]}
        tables = [row[0] for row in db.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
        result['tables'] = {}
        for table in tables:
            quoted = '"' + table.replace('"', '""') + '"'
            # table_info omits generated/hidden columns, including alias masks.
            info = db.execute('PRAGMA table_xinfo(' + quoted + ')').fetchall()
            check(bool(info), 'table column metadata unavailable: ' + table)
            columns = [row[1] for row in info if row[6] != 1]
            names = {row[1].lower() for row in info}
            aliases = ('rowid', '_rowid_', 'oid')
            probe = next((alias for alias in aliases if alias not in names), None)
            check(probe is not None, 'table masks the hidden rowid: ' + table)
            # A qualified identifier cannot become a double-quoted string
            # literal. SQLite resolves it even with LIMIT 0 / an empty table.
            # Only this exact missing-column error means WITHOUT ROWID; all
            # other failures propagate rather than silently dropping identity.
            try:
                db.execute('SELECT _grrr_probe.' + probe + ' FROM ' + quoted
                           + ' AS _grrr_probe LIMIT 0')
                hidden = True
            except sqlite3.OperationalError as error:
                if str(error) != 'no such column: _grrr_probe.' + probe:
                    raise
                hidden = False
            if not hidden:
                rows = db.execute('SELECT * FROM ' + quoted).fetchall()
            else:
                masked = set(aliases + ('_grrr_rowid',)) & names
                check(not masked, 'table masks the hidden rowid: ' + table)
                rows = db.execute('SELECT rowid AS _grrr_rowid, * FROM ' + quoted
                                  + ' ORDER BY _grrr_rowid').fetchall()
                if rows:
                    check(len(rows[0]) == len(columns) + 1
                          and type(rows[0][0]) is int,
                          'hidden rowid was not captured: ' + table)
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
    check(after['schema'] == before['schema'] and after['tables'] == tables
          and after['header'] == before['header'],
          'history, schema, header, holds or unknown rows changed')


def apply_install(base: Path, plan: dict, review: dict, authorization: dict,
                  *, privileged: bool, owner: int = 320, active_uid: int = 0) -> dict:
    try:
        return _install(base, plan, review, authorization, privileged=privileged,
                        owner=owner, active_uid=active_uid)
    except BaseException as original:
        recovery = base / 'recovery-v4'
        intent = None
        try:
            intent = json.loads(read(recovery / 'intent.json'))
        except BaseException:
            pass
        if intent is None or not (
                canonical(intent.get('plan')) == canonical(plan)
                and canonical(intent.get('review')) == canonical(review)
                and canonical(intent.get('authorization')) == canonical(authorization)):
            raise original
        _recover_failure(base, recovery, None, owner)
        raise


def _install(base: Path, plan: dict, review: dict, authorization: dict,
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
        # Hold the exclusive guard from the mutation through publication and
        # verification: no writer may touch any row in between.
        db.execute('BEGIN IMMEDIATE')
        published = _publish(base, recovery, database, pre, before, owner)
        db.execute('COMMIT')
        return published
    finally:
        db.close()


def _publish(base: Path, recovery: Path, database: Path, pre: os.stat_result,
             before: dict, owner: int) -> dict:
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
    os.chmod(recovery, 0o555)
    sync(recovery)
    sync(base)
    return verify(base, owner=owner)


def _recover_failure(base: Path, recovery: Path, database: Path | None,
                     owner: int) -> None:
    """Invalidate completion first, then restore and record, in that order."""
    failure = []
    # 1. Completion must be invalidated even when the store cannot be located.
    try:
        os.chmod(recovery, 0o700)
    except Exception as error:
        failure.append('namespace: ' + str(error))
    try:
        (recovery / 'complete.json').unlink()
    except FileNotFoundError:
        pass
    except Exception as error:
        failure.append('invalidate: ' + str(error))
    try:
        sync(recovery)
    except Exception as error:
        failure.append('sync: ' + str(error))
    # 2. Restore only a target resolved from the protected binding.
    if database is None:
        try:
            database = binding(base, owner=owner)['database']
        except Exception as error:
            failure.append('target: ' + str(error))
    if database is not None:
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
    # 3. Durable failure record.
    try:
        publish(recovery / 'incomplete.json', canonical(
            {'outcome': 'recovery-incomplete',
             'reason': '; '.join(failure)[:512] or 'post-publish verification failed'}))
        sync(recovery)
        os.chmod(recovery, 0o555)
        sync(recovery)
        sync(base)
    except Exception as marker_error:
        failure.append('marker: ' + str(marker_error))
    if failure:
        raise RuntimeError('recovery failed and could not be fully recorded; '
                           'operator recovery required: ' + '; '.join(failure))


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
    for suffix in ('-wal', '-shm', '-journal'):
        sidecar = Path(str(found['database']) + suffix)
        check(not sidecar.exists(), 'store has an open journal or WAL sidecar')
    current = inventory(found['database'])
    state = current['tables']['state']['rows']
    check(len(state) == 1 and state[0][-1] == ['i', 0], 'store is not released')
    check(digest(canonical(current)) == receipt['inventory_after'],
          'store inventory differs from the released receipt')
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

```

## accounting_recovery_planner_v4.py
```python
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

```
