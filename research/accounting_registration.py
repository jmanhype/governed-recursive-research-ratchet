"""Registration-only, stdlib-only bootstrap; never writes a Budget database.

Install this exact file independently as /Library/GRRR/bootstrap/register-independent-replay.
Inspection/installation there requires the pinned isolated interpreter and root.
The registration receipt freezes the stopped database: recovery is a separate change.
"""
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import sqlite3
import stat
import subprocess
import sys
from contextlib import closing, ExitStack

BASE = Path('/Library/GRRR/accounting-poc2')
BOOTSTRAP = Path('/Library/GRRR/bootstrap/register-independent-replay')
PYTHON = Path('/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/bin/python3.9')
PYTHON_SHA256 = '5c5950c62eee5fd227a67e4bdfcde81c9add59799bba0949635f3d5ba9661c26'
LEGACY = ['synthetic', 'offline', 'trusted-observation']
PROFILES = LEGACY + ['independent-replay']
CEILINGS = {'poc': [5000, 21600000000, 3600000000],
            'milestone': [15000, 86400000000, 10800000000]}
DIMENSIONS = ('money_cents', 'execution_us', 'review_us')
LOCKS = (BASE / 'launch.lock', Path('/Library/GRRR/validated-corpus/v2-launch.lock'))
ACTIVE_SHA256 = 'e5629ee930fc909b38bcdf8c6cdbd673233651b1b507d73a2230f4ce1e304c95'
DATABASE_SHA256 = '2347a548429cd8bf07048e15898de1432c960d7a08743e17dc31d39efdb5bbaf'
CAMPAIGN = '9ea9cd9b2669bc0d3fe119d722224907e1bbb06a4ca28f860c8044e2491092a9'
STORE = '901acaff42b5a42f667b1c435beba9a9ae8312539cc36eb023c45584fd2e06d6'
PRIOR = '9f64395bec815a6bb2281d3b5d96d2356899138b1929b0a9881c16483c486dde'
IDENTITY = {'device': 16777229, 'active_inode': 682589456,
            'directory_inode': 682589446, 'database_inode': 682589447}
BINDING_FIELDS = {'version', 'campaign', 'store_id', 'directory', 'prior_history_receipt',
                  'profiles', 'device', 'inode'}


def check(condition: bool, reason: str) -> None:
    if not condition:
        raise ValueError(reason)


def canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=True, allow_nan=False).encode('ascii')


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def unique(pairs: list) -> dict:
    result = {}
    for key, value in pairs:
        check(key not in result, 'duplicate field')
        result[key] = value
    return result


def decode(raw: bytes) -> dict:
    value = json.loads(raw, object_pairs_hook=unique)
    check(isinstance(value, dict) and canonical(value) == raw, 'noncanonical record')
    return value


def hashed(value: str) -> None:
    check(isinstance(value, str) and re.fullmatch('[0-9a-f]{64}', value) is not None, 'invalid digest')


def metadata(path: Path, uid: int, gid: int, mode: int, directory: bool = False) -> dict:
    info = path.lstat()
    check((stat.S_ISDIR(info.st_mode) if directory else stat.S_ISREG(info.st_mode))
          and info.st_uid == uid and info.st_gid == gid
          and stat.S_IMODE(info.st_mode) == mode
          and (directory or info.st_nlink == 1), 'unsafe metadata: ' + str(path))
    listing = subprocess.run(['/bin/ls', '-lde', str(path)], check=True, capture_output=True,
                             timeout=2, env={'PATH': '/usr/bin:/bin', 'LC_ALL': 'C'}).stdout
    check(bool(listing.split()) and b'+' not in listing.split()[0]
          and len(listing.splitlines()) == 1, 'ACL rejected')
    return {'device': info.st_dev, 'inode': info.st_ino, 'uid': info.st_uid,
            'gid': info.st_gid, 'mode': stat.S_IMODE(info.st_mode)}


def protected(path: Path, readonly: bool = True) -> None:
    check(path.is_absolute() and '..' not in path.parts, 'absolute path required')
    for ancestor in reversed(path.parents):
        info = ancestor.lstat()
        check(stat.S_ISDIR(info.st_mode) and info.st_uid == 0 and info.st_gid == 0
              and not info.st_mode & 0o022, 'mutable protected ancestor')
        metadata(ancestor, 0, 0, stat.S_IMODE(info.st_mode), True)
    metadata(path, 0, 0, 0o444 if readonly else stat.S_IMODE(path.lstat().st_mode))
    check(readonly or not path.stat().st_mode & 0o022, 'mutable interpreter')


def read(path: Path, maximum: int = 16777216) -> bytes:
    def stable(info: os.stat_result) -> tuple:
        return (info.st_dev, info.st_ino, info.st_mode, info.st_uid, info.st_gid,
                info.st_nlink, info.st_size, info.st_mtime_ns, info.st_ctime_ns)
    with os.fdopen(os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK), 'rb') as stream:
        before = os.fstat(stream.fileno())
        check(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and before.st_size <= maximum,
              'unsafe regular input')
        raw = stream.read(maximum + 1)
        after = os.fstat(stream.fileno())
        check(stable(before) == stable(after) == stable(path.lstat()) and len(raw) == before.st_size,
              'input changed during read')
        return raw


def validate_binding(binding: dict, version: int = 1) -> None:
    extra = {'registration_sha256'} if version == 2 else set()
    check(set(binding) == BINDING_FIELDS | extra and type(binding['version']) is int
          and binding['version'] == version and binding['profiles'] == (PROFILES if version == 2 else LEGACY),
          'binding schema/profiles differ')
    for key in ('campaign', 'store_id', 'prior_history_receipt'):
        hashed(binding[key])
    check(binding['directory'] == str(BASE / binding['store_id'])
          and type(binding['device']) is int and type(binding['inode']) is int,
          'binding path/identity differs')
    if version == 2:
        hashed(binding['registration_sha256'])


def resource(value: dict) -> dict:
    check(isinstance(value, dict) and set(value) == {'currency', *DIMENSIONS}
          and value['currency'] == 'USD'
          and all(type(value[k]) is int and 0 <= value[k] < 2**63 for k in DIMENSIONS),
          'unknown resource vector')
    return value


def inventory(path: Path, binding: dict, *, expected_stop: int = 1) -> dict:
    """Read-only immutable SQLite snapshot; retain exact raw cells, including unknown holds."""
    before = read(path)
    for suffix in ('-journal', '-wal', '-shm'):
        check(not os.path.lexists(str(path) + suffix), 'partial database journal')
    with closing(sqlite3.connect(path.as_uri() + '?mode=ro&immutable=1', uri=True)) as db:
        check(db.execute('PRAGMA integrity_check').fetchall() == [('ok',)]
              and db.execute('PRAGMA journal_mode').fetchall() == [('delete',)], 'database integrity/journal differs')
        schema = db.execute('SELECT type,name,tbl_name,sql FROM sqlite_master ORDER BY type,name').fetchall()
        tables = {r[1] for r in schema if r[0] == 'table'}
        check(tables == {'reservations', 'metering', 'overhead', 'state', 'store_identity'}
              and all(r[0] in ('table', 'index') for r in schema), 'unexpected schema')
        check(type(expected_stop) is int and expected_stop in (0, 1)
              and db.execute('SELECT * FROM state').fetchall() == [(1, expected_stop)],
              'registration requires stopped state or exact recovery disposition')
        check(db.execute('SELECT * FROM store_identity').fetchall()
              == [(binding['campaign'], binding['store_id'], binding['prior_history_receipt'])], 'store identity differs')
        rows = db.execute('SELECT id,key,binding,run,stage,maximum,actual,receipt FROM reservations ORDER BY id').fetchall()
        meters = db.execute('SELECT id,reservation,body FROM metering ORDER BY id').fetchall()
        overhead = db.execute('SELECT key,category,duration_us FROM overhead ORDER BY key').fetchall()
        totals = {stage: [0, 0, 0] for stage in CEILINGS}
        meter_map = {}
        ids = {r[0] for r in rows}
        for receipt, reservation, body in meters:
            check(reservation in ids and reservation not in meter_map and sha(bytes(body)) == receipt,
                  'orphan/duplicate/changed meter')
            meter = decode(bytes(body))
            check(set(meter) == {'reservation', 'usage', 'evidence'} and meter['reservation'] == reservation,
                  'meter binding differs')
            hashed(meter['evidence'])
            resource(meter['usage'])
            meter_map[reservation] = (receipt, meter['usage'])
        pending = 0
        for rid, key, request, run, stage, maximum, actual, receipt in rows:
            check(stage in CEILINGS, 'unknown accounting stage')
            for value in (rid, key, run):
                check(isinstance(value, str) and re.fullmatch('[a-zA-Z0-9][a-zA-Z0-9-]{0,63}', value) is not None,
                      'invalid reservation identity')
            maximum_value = resource(decode(bytes(maximum)))
            request_value = decode(bytes(request))
            check(set(request_value) == {'run', 'maximum', 'stage', 'binding'}
                  and request_value['run'] == run and request_value['maximum'] == maximum_value
                  and request_value['stage'] == stage, 'reservation request differs')
            if request_value['binding'] is not None:
                hashed(request_value['binding'])
            if rid in meter_map:
                check(all(meter_map[rid][1][k] <= maximum_value[k] for k in DIMENSIONS), 'meter exceeds hold')
            if actual is None:
                check(receipt is None, 'partial settlement')
                pending += 1
                used = maximum_value
            else:
                used = resource(decode(bytes(actual)))
                check(rid in meter_map and meter_map[rid] == (receipt, used), 'unbound settlement')
            for scope in CEILINGS:
                if scope == 'milestone' or stage == 'poc':
                    totals[scope] = [n + used[k] for n, k in zip(totals[scope], DIMENSIONS)]
        for key, category, duration in overhead:
            check(isinstance(key, str) and category in ('preparation', 'selector')
                  and type(duration) is int and 0 <= duration < 2**63, 'invalid overhead')
        check(all(all(n <= cap for n, cap in zip(totals[s], CEILINGS[s])) for s in CEILINGS),
              'cumulative ceiling exceeded')
        def cells(values: list) -> list:
            return [[{'blob_hex': v.hex()} if isinstance(v, bytes) else v for v in row] for row in values]
        snapshot = {'schema': schema, 'reservations': cells(rows), 'metering': cells(meters),
                    'overhead': cells(overhead), 'stopped': expected_stop, 'pending': pending,
                    'known_encumbered': totals, 'historical_unknowns': 'unresolved',
                    'spendable': None, 'database_sha256': sha(before)}
    check(read(path) == before, 'database changed during snapshot')
    return json.loads(canonical(snapshot))


def baseline() -> dict:
    """Exact pinned live baseline; no repairs, registration artifacts, or mutable outputs."""
    active = BASE / 'active.json'
    protected(active)
    raw = read(active)
    check(sha(raw) == ACTIVE_SHA256, 'active baseline hash differs')
    binding = decode(raw)
    validate_binding(binding)
    check((binding['campaign'], binding['store_id'], binding['prior_history_receipt']) == (CAMPAIGN, STORE, PRIOR),
          'pinned campaign/store/prior differs')
    directory = Path(binding['directory'])
    database = directory / 'budget.sqlite'
    check({p.name for p in BASE.iterdir()} == {'active.json', 'launch.lock', STORE}
          and {p.name for p in directory.iterdir()} == {'budget.sqlite'}, 'existing/partial/unknown state')
    meta = {'active': metadata(active, 0, 0, 0o444),
            'directory': metadata(directory, 320, 320, 0o700, True),
            'database': metadata(database, 320, 320, 0o600)}
    check(all(m['device'] == IDENTITY['device'] for m in meta.values())
          and all(meta[k]['inode'] == IDENTITY[k + '_inode'] for k in meta)
          and (binding['device'], binding['inode']) == (meta['database']['device'], meta['database']['inode']),
          'pinned device/inode differs')
    snapshot = inventory(database, binding)
    check(snapshot['database_sha256'] == DATABASE_SHA256, 'database baseline hash differs')
    return {'active_hex': raw.hex(), 'metadata': meta, 'inventory': snapshot}


def validate_receipt(binding: dict, receipt: dict, old_raw: bytes, database: Path) -> None:
    """Complete registration authorizes only opening the original stopped database."""
    validate_binding(binding, 2)
    check(set(receipt) == {'version', 'plan_sha256', 'review_sha256', 'baseline', 'ceilings',
                           'profiles', 'stage', 'stop_release', 'execution_authorized'}, 'receipt fields differ')
    check(type(receipt['version']) is int and receipt['version'] == 1
          and receipt['ceilings'] == CEILINGS and receipt['profiles'] == PROFILES
          and receipt['stage'] == 'poc' and receipt['stop_release'] is False
          and receipt['execution_authorized'] is False, 'receipt authority differs')
    hashed(receipt['plan_sha256'])
    hashed(receipt['review_sha256'])
    check(sha(canonical(receipt)) == binding['registration_sha256'], 'registration receipt changed')
    old = decode(old_raw)
    validate_binding(old)
    expected = dict(old, version=2, profiles=PROFILES, registration_sha256=sha(canonical(receipt)))
    check(binding == expected and receipt['baseline']['active_hex'] == old_raw.hex()
          and database == Path(old['directory']) / 'budget.sqlite', 'registration changed original identity')
    info = database.lstat()
    check((info.st_dev, info.st_ino) == (old['device'], old['inode']), 'original database replaced')
    check(inventory(database, old) == receipt['baseline']['inventory'], 'registered stopped baseline changed')


def idle() -> None:
    output = subprocess.run(['/bin/ps', '-axo', 'uid=,pid=,comm='], check=True, capture_output=True,
                            timeout=5, env={'PATH': '/usr/bin:/bin', 'LC_ALL': 'C'}).stdout.decode('ascii')
    check(bool(output.strip()), 'empty process inventory')
    for line in output.splitlines():
        uid, pid, command = line.split(None, 2)
        check(uid.lstrip('+-').isdigit() and pid.isdigit(), 'invalid process inventory')
        check(int(uid) not in (320, 321) and not Path(command).name.lower().startswith('qemu'),
              'active evaluator/runner/QEMU')


def bootstrap() -> None:
    check(os.getuid() == 0 and os.geteuid() == 0, 'root-only registration bootstrap')
    check(Path(__file__).absolute() == BOOTSTRAP and Path(sys.executable) == PYTHON
          and sys.version_info[:3] == (3, 9, 6) and sys.flags.isolated and sys.flags.no_site
          and sys.dont_write_bytecode, 'isolated canonical bootstrap required')
    protected(BOOTSTRAP)
    protected(PYTHON, readonly=False)
    check(sha(read(PYTHON)) == PYTHON_SHA256, 'interpreter hash differs')


def acquire(stack: ExitStack) -> None:
    """Fixed order: accounting then corpus; caller also excludes other privileged writers."""
    for path in LOCKS:
        protected(path)
        stream = stack.enter_context(os.fdopen(os.open(path, os.O_RDONLY | os.O_NOFOLLOW), 'rb'))
        check(os.fstat(stream.fileno()) == path.lstat(), 'launch lock changed')
        fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
    idle()


def inspect() -> dict:
    bootstrap()
    with ExitStack() as stack:
        acquire(stack)
        return baseline()


def exclusive(path: Path, raw: bytes) -> None:
    with os.fdopen(os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o400), 'wb') as stream:
        stream.write(raw)
        os.fchown(stream.fileno(), 0, 0)
        os.fchmod(stream.fileno(), 0o444)
        stream.flush()
        os.fsync(stream.fileno())


def sync_directory(path: Path) -> None:
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def install(plan_path: Path, expected: str, authorization: str) -> dict:
    """A receipt directory precedes the sole atomic commit point: active.json replace."""
    bootstrap()
    check(plan_path.parent == BOOTSTRAP.parent, 'protected bootstrap plan required')
    protected(plan_path)
    raw = read(plan_path)
    check(sha(raw) == expected and authorization == 'REGISTER_STOPPED_INDEPENDENT_REPLAY:' + expected,
          'exact separately approved plan authorization required')
    plan = decode(raw)
    check(set(plan) == {'version', 'baseline', 'installer_sha256', 'review_sha256', 'ceilings',
                       'profiles', 'stage', 'stop_release', 'execution_authorized', 'exclusive_parent'},
          'plan fields differ')
    check(type(plan['version']) is int and plan['version'] == 1
          and plan['installer_sha256'] == sha(read(BOOTSTRAP)) and plan['ceilings'] == CEILINGS
          and plan['profiles'] == PROFILES and plan['stage'] == 'poc'
          and plan['stop_release'] is False and plan['execution_authorized'] is False
          and plan['exclusive_parent'] is True, 'plan authority differs')
    hashed(plan['review_sha256'])
    review_path = BOOTSTRAP.parent / ('registration-review-' + plan['review_sha256'] + '.json')
    protected(review_path)
    review_raw = read(review_path)
    check(sha(review_raw) == plan['review_sha256'], 'independent review hash differs')
    review = decode(review_raw)
    check(review == {'decision': 'approved-registration-only', 'installer_sha256': plan['installer_sha256'],
                     'baseline_sha256': sha(canonical(plan['baseline'])), 'ceilings': CEILINGS,
                     'stage': 'poc', 'stop_release': False, 'execution_authorized': False},
          'independent review scope differs')
    with ExitStack() as stack:
        acquire(stack)
        before = baseline()
        check(before == plan['baseline'], 'reviewed baseline differs')
        receipt = {'version': 1, 'plan_sha256': expected, 'review_sha256': plan['review_sha256'],
                   'baseline': before, 'ceilings': CEILINGS, 'profiles': PROFILES, 'stage': 'poc',
                   'stop_release': False, 'execution_authorized': False}
        old_raw = bytes.fromhex(before['active_hex'])
        binding = dict(decode(old_raw), version=2, profiles=PROFILES,
                       registration_sha256=sha(canonical(receipt)))
        database = Path(binding['directory']) / 'budget.sqlite'
        # All checks above are read-only. Any subsequent failure leaves explicit
        # partial artifacts; legacy runtime refuses them and retries never repair.
        directory = BASE / 'registration'
        directory.mkdir(mode=0o700)
        os.chown(directory, 0, 0)
        exclusive(directory / 'prior-active.json', old_raw)
        exclusive(directory / 'receipt.json', canonical(receipt))
        exclusive(directory / 'next-active.json', canonical(binding))
        os.chmod(directory, 0o555)
        sync_directory(directory)
        sync_directory(BASE)
        idle()
        protected(BASE / 'active.json')
        check(read(BASE / 'active.json') == old_raw
              and metadata(BASE / 'active.json', 0, 0, 0o444) == before['metadata']['active']
              and metadata(database.parent, 320, 320, 0o700, True) == before['metadata']['directory']
              and metadata(database, 320, 320, 0o600) == before['metadata']['database'],
              'baseline metadata/active changed before publication')
        for name, expected_raw in [('prior-active.json', old_raw), ('receipt.json', canonical(receipt)),
                                   ('next-active.json', canonical(binding))]:
            protected(directory / name)
            check(read(directory / name) == expected_raw, 'staged registration bytes differ')
        validate_receipt(binding, receipt, old_raw, database)
        os.replace(directory / 'next-active.json', BASE / 'active.json')
        sync_directory(directory)
        sync_directory(BASE)
        verify()
        return {'registered': True, 'stopped': True, 'execution_authorized': False,
                'binding_sha256': sha(canonical(binding)), 'receipt_sha256': sha(canonical(receipt))}


def verify() -> dict:
    """Protected postflight; intentionally rejects any stop recovery or database mutation."""
    protected(BASE / 'active.json')
    directory = BASE / 'registration'
    metadata(directory, 0, 0, 0o555, True)
    check({p.name for p in BASE.iterdir()} == {'active.json', 'launch.lock', STORE, 'registration'}
          and {p.name for p in directory.iterdir()} == {'prior-active.json', 'receipt.json'},
          'partial/unknown registration state')
    for name in ('prior-active.json', 'receipt.json'):
        protected(directory / name)
    binding = decode(read(BASE / 'active.json'))
    receipt = decode(read(directory / 'receipt.json'))
    old_raw = read(directory / 'prior-active.json')
    check(sha(old_raw) == ACTIVE_SHA256, 'original binding hash differs')
    database = Path(binding['directory']) / 'budget.sqlite'
    check({p.name for p in database.parent.iterdir()} == {'budget.sqlite'}, 'partial store state')
    check(metadata(database.parent, 320, 320, 0o700, True) == receipt['baseline']['metadata']['directory']
          and metadata(database, 320, 320, 0o600) == receipt['baseline']['metadata']['database'],
          'original metadata changed')
    validate_receipt(binding, receipt, old_raw, database)
    return {'binding': binding, 'receipt': receipt}


if __name__ == '__main__':
    try:
        if sys.argv[1:] == ['inspect']:
            result = inspect()
        elif sys.argv[1:] == ['verify']:
            bootstrap()
            with ExitStack() as stack:
                acquire(stack)
                result = verify()
        elif len(sys.argv) == 5 and sys.argv[1] == 'install':
            result = install(Path(sys.argv[2]), sys.argv[3], sys.argv[4])
        else:
            raise ValueError('inspect | verify | install PROTECTED_PLAN SHA256 AUTHORIZATION')
        print(canonical(result).decode('ascii'))
    except (ValueError, OSError, sqlite3.Error, subprocess.SubprocessError) as exc:
        print(canonical({'error': str(exc), 'execution_authorized': False, 'recovery_authorized': False}).decode('ascii'))
        raise SystemExit(1)
