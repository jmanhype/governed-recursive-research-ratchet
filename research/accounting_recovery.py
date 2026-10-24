"""One-shot stop-only successor. Unknown history still forbids ALL runtime writes.

Not an approval: installation, exact-byte independent review, operator authorization
and parent writer exclusion are required separately. See ACCOUNTING-RECOVERY.md.
"""
import os
from pathlib import Path
import sqlite3
import sys
from contextlib import ExitStack, closing

INSTALL = Path('/Library/GRRR/bootstrap/recovery/accounting_recovery.py')
if __name__ == '__main__':
    # Isolated Python omits the script directory; admit only the fixed root-owned
    # closure, never a checkout or an operator-controlled import directory.
    import stat
    import subprocess
    if (os.getuid() != 0 or os.geteuid() != 0 or Path(__file__) != INSTALL
            or not sys.flags.isolated or not sys.flags.no_site or not sys.dont_write_bytecode):
        raise SystemExit('root-only isolated canonical recovery entrypoint required')
    for member in (INSTALL.parent / 'accounting_registration.py', INSTALL, *INSTALL.parents):
        info = member.lstat()
        if stat.S_ISLNK(info.st_mode) or info.st_uid != 0 or info.st_mode & 0o022:
            raise SystemExit('unsafe recovery import closure')
        listing = subprocess.run(['/bin/ls', '-lde', str(member)], check=True, capture_output=True,
                                 timeout=2, env={'PATH': '/usr/bin:/bin', 'LC_ALL': 'C'}).stdout
        if (not listing.split() or b'+' in listing.split()[0] or len(listing.splitlines()) != 1
                or (member in (INSTALL, INSTALL.parent / 'accounting_registration.py')
                    and (not stat.S_ISREG(info.st_mode) or info.st_nlink != 1
                         or stat.S_IMODE(info.st_mode) != 0o444))):
            raise SystemExit('unsafe recovery import metadata/ACL')
    import importlib.util
    spec = importlib.util.spec_from_file_location('recovery_registration', INSTALL.parent / 'accounting_registration.py')
    reg = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(reg)
else:
    import accounting_registration as reg

ACTION = 'release-stop-retain-unknowns-read-only'
SOURCE_FILES = ('accounting_recovery.py', 'accounting_registration.py')


def sources() -> dict:
    """Hash the exact two-file installer closure; protected bootstrap checks it."""
    return {name: reg.sha(reg.read(Path(__file__).parent / name)) for name in SOURCE_FILES}


def bootstrap() -> None:
    """No privilege escalation and no developer checkout execution."""
    reg.check(os.getuid() == 0 and os.geteuid() == 0 and Path(__file__) == INSTALL,
              'root-only canonical recovery required')
    reg.check(Path(sys.executable) == reg.PYTHON and sys.version_info[:3] == (3, 9, 6)
              and sys.flags.isolated and sys.flags.no_site and sys.dont_write_bytecode,
              'isolated pinned interpreter required')
    reg.protected(reg.PYTHON, readonly=False)
    reg.check(reg.sha(reg.read(reg.PYTHON)) == reg.PYTHON_SHA256, 'interpreter changed')
    for name in SOURCE_FILES:
        reg.protected(INSTALL.parent / name)


def snapshot() -> dict:
    """Original v2 validation remains unchanged and mandatory before transition."""
    verified = reg.verify()
    binding = verified['binding']
    database = Path(binding['directory']) / 'budget.sqlite'
    return {'active_hex': reg.read(reg.BASE / 'active.json').hex(),
            'registration_hex': reg.read(reg.BASE / 'registration/receipt.json').hex(),
            'prior_hex': reg.read(reg.BASE / 'registration/prior-active.json').hex(),
            'metadata': {'active': reg.metadata(reg.BASE / 'active.json', 0, 0, 0o444),
                         'database': reg.metadata(database, 320, 320, 0o600),
                         'directory': reg.metadata(database.parent, 320, 320, 0o700, True)},
            'inventory': reg.inventory(database, binding)}


def approval(plan: dict, review: dict, authorization: dict) -> None:
    """Exact schemas; root-protected records are parent-attested, not signatures."""
    reg.check(set(plan) == {'version', 'action', 'baseline', 'sources', 'review_sha256'},
              'plan fields differ')
    reg.check(type(plan['version']) is int and plan['version'] == 1 and plan['action'] == ACTION
              and plan['sources'] == sources(), 'stale source/action/version')
    reg.hashed(plan['review_sha256'])
    expected_review = {'decision': 'approved-stop-only-read-only', 'action': ACTION,
                       'baseline_sha256': reg.sha(reg.canonical(plan['baseline'])),
                       'sources': plan['sources'], 'ceilings': reg.CEILINGS,
                       'allowed_mutations': [], 'historical_unknowns': 'unresolved',
                       'spendable': None, 'execution_authorized': False}
    reg.check(reg.canonical(review) == reg.canonical(expected_review)
              and reg.sha(reg.canonical(review)) == plan['review_sha256'],
              'independent review differs')
    reg.check(reg.canonical(authorization) == reg.canonical({'principal': 'operator-via-exclusive-root-parent',
              'action': ACTION, 'plan_sha256': reg.sha(reg.canonical(plan)),
              'review_sha256': plan['review_sha256'],
              'baseline_sha256': review['baseline_sha256'], 'sources': plan['sources'],
              'exclusive_parent': True, 'execution_authorized': False}),
              'separate exact operator authorization required')


def unchanged(before: dict, after: dict) -> None:
    """Only the stop bit and SQLite physical bytes may differ, never history."""
    reg.check(after == dict(before, stopped=0, database_sha256=after['database_sha256']),
              'historical accounting/holds/unknowns changed')


def record(path: Path) -> dict:
    reg.protected(path)
    return reg.decode(reg.read(path))


def verify() -> dict:
    """Read-only complete ancestry validation; any incomplete attempt is frozen."""
    directory = reg.BASE / 'recovery'
    reg.metadata(directory, 0, 0, 0o555, True)
    reg.check({p.name for p in directory.iterdir()} ==
              {'intent.json', 'receipt.json', 'complete.json', 'prior-active.json'},
              'partial/uncertain recovery')
    intent = record(directory / 'intent.json')
    reg.check(set(intent) == {'version', 'outcome', 'plan', 'review', 'authorization'},
              'intent fields differ')
    reg.check(type(intent['version']) is int and intent['version'] == 1
              and intent['outcome'] == 'prepared-not-success', 'intent outcome differs')
    plan = intent['plan']
    approval(plan, intent['review'], intent['authorization'])
    before = plan['baseline']
    reg.check(set(before) == {'active_hex', 'registration_hex', 'prior_hex', 'metadata', 'inventory'},
              'baseline fields differ')
    prior = bytes.fromhex(before['active_hex'])
    old = reg.decode(prior)
    reg.validate_binding(old, 2)
    reg.check(reg.read(directory / 'prior-active.json') == prior, 'prior active differs')
    reg.protected(directory / 'prior-active.json')
    registration = reg.decode(bytes.fromhex(before['registration_hex']))
    original = reg.decode(bytes.fromhex(before['prior_hex']))
    reg.validate_binding(original)
    reg.check(old == dict(original, version=2, profiles=reg.PROFILES,
                         registration_sha256=reg.sha(reg.canonical(registration)))
              and reg.sha(bytes.fromhex(before['prior_hex'])) == reg.ACTIVE_SHA256,
              'registration ancestry differs')
    reg.check(set(registration) == {'version', 'plan_sha256', 'review_sha256', 'baseline',
              'ceilings', 'profiles', 'stage', 'stop_release', 'execution_authorized'}
              and type(registration['version']) is int and registration['version'] == 1
              and registration['ceilings'] == reg.CEILINGS and registration['profiles'] == reg.PROFILES
              and registration['stage'] == 'poc' and registration['stop_release'] is False
              and registration['execution_authorized'] is False, 'registration authority differs')
    reg.hashed(registration['plan_sha256'])
    reg.hashed(registration['review_sha256'])
    reg.check(registration['baseline']['active_hex'] == before['prior_hex']
              and registration['baseline']['inventory'] == before['inventory'], 'baseline ancestry differs')
    reg.metadata(reg.BASE / 'registration', 0, 0, 0o555, True)
    reg.check({p.name for p in (reg.BASE / 'registration').iterdir()} ==
              {'receipt.json', 'prior-active.json'}, 'unknown registration artifacts')
    for name, value in [('receipt.json', before['registration_hex']), ('prior-active.json', before['prior_hex'])]:
        reg.protected(reg.BASE / 'registration' / name)
        reg.check(reg.read(reg.BASE / 'registration' / name).hex() == value, 'registration bytes changed')
    receipt = record(directory / 'receipt.json')
    reg.check(set(receipt) == {'version', 'outcome', 'intent_sha256', 'prior_active_sha256',
              'registration_sha256', 'result', 'allowed_mutations', 'execution_authorized'}, 'receipt fields differ')
    reg.check(type(receipt['version']) is int and receipt['version'] == 1
              and receipt['outcome'] == 'database-committed-publication-pending'
              and receipt['intent_sha256'] == reg.sha(reg.canonical(intent))
              and receipt['prior_active_sha256'] == reg.sha(prior)
              and receipt['registration_sha256'] == old['registration_sha256']
              and receipt['allowed_mutations'] == [] and receipt['execution_authorized'] is False,
              'receipt authority/ancestry differs')
    binding = record(reg.BASE / 'active.json')
    reg.check(binding == dict(old, version=3, recovery_sha256=reg.sha(reg.canonical(receipt))),
              'successor binding differs')
    reg.check(reg.canonical(record(directory / 'complete.json')) == reg.canonical({'outcome': 'published-durable',
              'receipt_sha256': binding['recovery_sha256'], 'binding_sha256': reg.sha(reg.canonical(binding)),
              'execution_authorized': False}), 'completion differs')
    database = Path(binding['directory']) / 'budget.sqlite'
    reg.check({p.name for p in reg.BASE.iterdir()} ==
              {'active.json', 'launch.lock', old['store_id'], 'registration', 'recovery'}
              and {p.name for p in database.parent.iterdir()} == {'budget.sqlite'}, 'unknown/partial artifacts')
    reg.check(reg.metadata(database, 320, 320, 0o600) == before['metadata']['database']
              == registration['baseline']['metadata']['database']
              and reg.metadata(database.parent, 320, 320, 0o700, True) == before['metadata']['directory']
              == registration['baseline']['metadata']['directory'], 'original identity/metadata changed')
    after = reg.inventory(database, old, expected_stop=0)
    unchanged(before['inventory'], after)
    reg.check(after == receipt['result'], 'recovered database bytes changed')
    return {'binding': binding, 'receipt': receipt}


def install(plan_path: Path, review_path: Path, authorization_path: Path, expected: str) -> dict:
    """One authorized attempt. Any uncertain outcome requires a new reviewed plan."""
    bootstrap()
    for path in (plan_path, review_path, authorization_path):
        reg.check(path.parent == INSTALL.parent, 'protected recovery record required')
    plan, review, authorization = [record(p) for p in (plan_path, review_path, authorization_path)]
    reg.check(reg.sha(reg.canonical(authorization)) == expected, 'authorization hash differs')
    approval(plan, review, authorization)
    with ExitStack() as stack:
        reg.acquire(stack)
        before = snapshot()
        reg.check(before == plan['baseline'], 'stale baseline')
        binding = reg.decode(bytes.fromhex(before['active_hex']))
        database = Path(binding['directory']) / 'budget.sqlite'
        db = stack.enter_context(closing(sqlite3.connect(database.as_uri() + '?mode=rw', uri=True,
                                                        timeout=0, isolation_level=None)))
        db.execute('PRAGMA synchronous=FULL')
        db.execute('BEGIN EXCLUSIVE')
        stack.callback(db.rollback)
        reg.check(snapshot() == before, 'baseline changed under database lock')
        directory = reg.BASE / 'recovery'
        directory.mkdir(mode=0o700)
        os.chown(directory, 0, 0)
        try:
            intent = {'version': 1, 'outcome': 'prepared-not-success', 'plan': plan,
                      'review': review, 'authorization': authorization}
            reg.exclusive(directory / 'intent.json', reg.canonical(intent))
            reg.exclusive(directory / 'prior-active.json', bytes.fromhex(before['active_hex']))
            reg.sync_directory(directory)
            reg.sync_directory(reg.BASE)
            reg.idle()
            reg.check(snapshot_with_attempt(before) == before, 'baseline changed before database commit')
            reg.check(db.execute('UPDATE state SET stopped=0 WHERE id=1 AND stopped=1').rowcount == 1,
                      'stop transition differs')
            db.commit()
            after = reg.inventory(database, binding, expected_stop=0)
            unchanged(before['inventory'], after)
            receipt = {'version': 1, 'outcome': 'database-committed-publication-pending',
                       'intent_sha256': reg.sha(reg.canonical(intent)),
                       'prior_active_sha256': reg.sha(bytes.fromhex(before['active_hex'])),
                       'registration_sha256': binding['registration_sha256'], 'result': after,
                       'allowed_mutations': [], 'execution_authorized': False}
            successor = dict(binding, version=3, recovery_sha256=reg.sha(reg.canonical(receipt)))
            reg.exclusive(directory / 'receipt.json', reg.canonical(receipt))
            reg.exclusive(directory / 'next-active.json', reg.canonical(successor))
            reg.sync_directory(directory)
            reg.check(reg.read(reg.BASE / 'active.json').hex() == before['active_hex']
                      and reg.metadata(reg.BASE / 'active.json', 0, 0, 0o444) == before['metadata']['active'],
                      'active changed before publication')
            reg.idle()
            os.replace(directory / 'next-active.json', reg.BASE / 'active.json')
            reg.sync_directory(directory)
            reg.sync_directory(reg.BASE)
            reg.exclusive(directory / 'complete.json', reg.canonical({'outcome': 'published-durable',
                          'receipt_sha256': successor['recovery_sha256'],
                          'binding_sha256': reg.sha(reg.canonical(successor)), 'execution_authorized': False}))
            os.chmod(directory, 0o555)
            reg.sync_directory(directory)
            reg.sync_directory(reg.BASE)
            return verify()
        except BaseException:
            # Never retry the SQL or report success. A missing uncertain record is
            # also partial: verify requires the exact complete artifact set.
            try:
                os.chmod(directory, 0o700)
                reg.exclusive(directory / 'uncertain.json', reg.canonical({
                    'outcome': 'uncertain-no-retry', 'authorization_sha256': expected,
                    'execution_authorized': False}))
                reg.sync_directory(directory)
            finally:
                os.chmod(directory, 0o555)
            raise


def snapshot_with_attempt(before: dict) -> dict:
    """Recheck source without weakening registration.verify's artifact allowlist."""
    binding = reg.decode(bytes.fromhex(before['active_hex']))
    database = Path(binding['directory']) / 'budget.sqlite'
    reg.check(reg.read(reg.BASE / 'active.json').hex() == before['active_hex']
              and reg.metadata(reg.BASE / 'active.json', 0, 0, 0o444) == before['metadata']['active']
              and reg.metadata(database, 320, 320, 0o600) == before['metadata']['database']
              and reg.metadata(database.parent, 320, 320, 0o700, True) == before['metadata']['directory'],
              'attempt source identity changed')
    reg.check(reg.inventory(database, binding) == before['inventory'], 'attempt source inventory changed')
    for name, value in [('receipt.json', before['registration_hex']), ('prior-active.json', before['prior_hex'])]:
        reg.protected(reg.BASE / 'registration' / name)
        reg.check(reg.read(reg.BASE / 'registration' / name).hex() == value, 'attempt ancestry changed')
    return before


if __name__ == '__main__':
    try:
        if sys.argv[1:] == ['verify']:
            bootstrap()
            with ExitStack() as stack:
                reg.acquire(stack)
                result = verify()
        elif len(sys.argv) == 6 and sys.argv[1] == 'install':
            result = install(Path(sys.argv[2]), Path(sys.argv[3]), Path(sys.argv[4]), sys.argv[5])
        else:
            raise ValueError('verify | install PLAN REVIEW AUTHORIZATION AUTHORIZATION_SHA256')
        print(reg.canonical(result).decode('ascii'))
    except (ValueError, OSError, sqlite3.Error, KeyError, TypeError) as exc:
        print(reg.canonical({'error': str(exc), 'execution_authorized': False}).decode('ascii'))
        raise SystemExit(1)
