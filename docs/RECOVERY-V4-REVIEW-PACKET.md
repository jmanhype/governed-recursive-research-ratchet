# Review packet (condensed) — v4 stop release

Constants: ACTION=release-v4-stop-retain-unknowns; BASE=/Library/GRRR/accounting-poc2; TABLES=(reservations,metering,overhead,state,store_identity).

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

## Plan summary
action=release-v4-stop-retain-unknowns version=1; stopped=[[1,1]]; counts reservations=2, metering=1, overhead=0, store_identity=1; plan_sha256=0051f3c6176b8c1c433722d67dd99d6d3175094191a374bff9a35b9e4c0fe10a; review_sha256=12947e48e15ddbc61fd326ea59fdd573500222a9cc8f680b80b577e7bfcee8b6.