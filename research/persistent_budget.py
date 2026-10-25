"""A campaign has one pre-provisioned store, never a fresh runtime allowance."""
import os
import json
from pathlib import Path
import sqlite3
import stat
from contextlib import closing
from budget import Budget, vector, CEILINGS
from common import EVALUATOR, canonical, digest, fields, identifier, require
from trusted_install import immutable, record
import accounting_registration
import accounting_recovery

ACTIVE = Path('/Library/GRRR/accounting-poc2/active.json')
PROFILES = ('synthetic', 'offline', 'trusted-observation')
REGISTERED_PROFILES = PROFILES + ('independent-replay',)


class RecheckingCursor(sqlite3.Cursor):
    """Python 3.9 may cache statements even with cached_statements=0."""
    def execute(self, sql: str, parameters: object = ()) -> sqlite3.Cursor:
        self.connection.refresh_authorizer()
        return super().execute(sql, parameters)

    def executemany(self, sql: str, parameters: object) -> sqlite3.Cursor:
        self.connection.refresh_authorizer()
        return super().executemany(sql, parameters)

    def executescript(self, sql: str) -> sqlite3.Cursor:
        self.connection.refresh_authorizer()
        return super().executescript(sql)


class RecheckingConnection(sqlite3.Connection):
    """Invalidate prepared authorization decisions before every SQL entrypoint."""
    def set_authorizer(self, callback: object) -> None:
        self.authorization = callback
        super().set_authorizer(callback)

    def refresh_authorizer(self) -> None:
        callback = getattr(self, 'authorization', None)
        if callback is not None:
            super().set_authorizer(callback)

    def cursor(self, factory: type = RecheckingCursor) -> sqlite3.Cursor:
        require(factory is RecheckingCursor, 'Unauthorized', 'Unreviewed accounting cursor factory')
        return super().cursor(factory)

    def execute(self, sql: str, parameters: object = ()) -> sqlite3.Cursor:
        return self.cursor().execute(sql, parameters)

    def executemany(self, sql: str, parameters: object) -> sqlite3.Cursor:
        return self.cursor().executemany(sql, parameters)

    def executescript(self, sql: str) -> sqlite3.Cursor:
        return self.cursor().executescript(sql)

    def blobopen(self, table: str, column: str, row: int, *, readonly: bool = False,
                 name: str = 'main') -> object:
        """Incremental BLOB writes bypass SQL authorization: never expose them.

        No accounting API needs writable BLOB handles, even on legacy stores.
        Deny before native lookup on every Python version and for every target.
        Existing handles from older code require installer writer quiescence.
        """
        require(readonly is True, 'Unauthorized', 'Writable accounting BLOB handles are forbidden')
        native = getattr(super(), 'blobopen', None)
        if native is None:
            raise sqlite3.NotSupportedError('Read-only incremental BLOB API unavailable in this Python')
        return native(table, column, row, readonly=True, name=name)


def validate_store(binding: dict, path: Path) -> None:
    registered = type(binding.get('version')) is int and binding['version'] == 2
    recovered = type(binding.get('version')) is int and binding['version'] == 3
    fields(binding, {'version', 'campaign', 'store_id', 'directory', 'prior_history_receipt', 'profiles',
                     'device', 'inode'} | ({'registration_sha256'} if registered or recovered else set())
           | ({'recovery_sha256'} if recovered else set()))
    require(type(binding['version']) is int and binding['version'] in (1, 2, 3)
            and binding['profiles'] == list(REGISTERED_PROFILES if registered or recovered else PROFILES),
            'RecoveryRequired', 'Persistent binding schema differs')
    if registered or recovered:
        try:
            verifier = accounting_recovery.verify if recovered else accounting_registration.verify
            require(verifier()['binding'] == binding,
                    'RecoveryRequired', 'Registered binding differs')
        except (ValueError, OSError, KeyError, TypeError, sqlite3.Error) as exc:
            require(False, 'RecoveryRequired', 'Incomplete or changed replay registration: ' + str(exc))
    else:
        require(not os.path.lexists(path.parent.parent / 'registration')
                and not os.path.lexists(path.parent.parent / 'recovery'),
                'RecoveryRequired', 'Partial replay registration requires independent review')
    for key in ('campaign', 'store_id', 'prior_history_receipt'):
        identifier(binding[key], True)
    require(path == Path(binding['directory']) / 'budget.sqlite', 'RecoveryRequired', 'Store path differs')
    info = path.lstat()
    require(stat.S_ISREG(info.st_mode) and info.st_uid == EVALUATOR
            and info.st_nlink == 1 and info.st_mode & 0o077 == 0
            and type(binding['device']) is int and type(binding['inode']) is int
            and (info.st_dev, info.st_ino) == (binding['device'], binding['inode']),
            'RecoveryRequired', 'Persistent database missing or unsafe')
    with closing(sqlite3.connect(path.as_uri() + '?mode=ro', uri=True)) as db:
        require(db.execute('PRAGMA journal_mode').fetchall() == [('delete',)],
                'RecoveryRequired', 'Unreviewed persistent journal mode')
        require(db.execute('PRAGMA integrity_check').fetchall() == [('ok',)],
                'RecoveryRequired', 'Prior accounting integrity unknown')
        tables = {row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        require({'reservations', 'metering', 'overhead', 'state', 'store_identity'} <= tables,
                'RecoveryRequired', 'Prior accounting schema incomplete; no automatic repair')
        require(db.execute('SELECT id,stopped FROM state').fetchall() in ([(1, 0)], [(1, 1)]),
                'RecoveryRequired', 'Prior stop state missing or malformed')
        require(db.execute('SELECT campaign,store_id,prior_history_receipt FROM store_identity').fetchall()
                == [(binding['campaign'], binding['store_id'], binding['prior_history_receipt'])],
                'RecoveryRequired', 'Prior accounting identity differs')
        for reservation, key, run, stage, maximum, actual, receipt in db.execute(
                'SELECT id,key,run,stage,maximum,actual,receipt FROM reservations'):
            for value in (reservation, key, run):
                identifier(value)
            require(stage in CEILINGS, 'RecoveryRequired', 'Unknown prior accounting stage')
            vector(json.loads(maximum))
            if actual is not None:
                vector(json.loads(actual))
                meter = db.execute('SELECT body FROM metering WHERE id=? AND reservation=?',
                                   (receipt, reservation)).fetchall()
                require(len(meter) == 1 and digest(bytes(meter[0][0])) == receipt
                        and canonical(json.loads(meter[0][0])['usage']) == canonical(json.loads(actual)),
                        'RecoveryRequired', 'Prior settlement lacks a bound meter receipt')


class PersistentBudget(Budget):
    def __init__(self, profile: str) -> None:
        require(profile in REGISTERED_PROFILES, 'InvalidInput', 'Unregistered accounting profile')
        binding = record(ACTIVE)
        directory = Path(binding['directory'])
        require(directory.parent == ACTIVE.parent and directory.name == binding['store_id'],
                'RecoveryRequired', 'Store must be in protected accounting namespace')
        immutable(directory.parent, directory=True)
        info = directory.lstat()
        require(stat.S_ISDIR(info.st_mode) and info.st_uid == EVALUATOR and info.st_mode & 0o077 == 0,
                'RecoveryRequired', 'Prior store directory unavailable')
        path = directory / 'budget.sqlite'
        validate_store(binding, path)
        require(profile in binding['profiles'], 'InvalidInput', 'Profile absent from active accounting binding')
        self.profile = profile
        self.recovered_readonly = binding['version'] == 3
        self.store_id = binding['store_id']
        self.binding_hash = digest(canonical(binding))
        super().__init__(path, existing=True, read_only=binding['version'] in (2, 3),
                         connection_factory=RecheckingConnection)
        self.db.set_authorizer(self.authorize_sql)

    def totals(self, principal: int) -> dict:
        result = super().totals(principal)
        if self.recovered_readonly:
            result.update(historical_unknowns='unresolved', spendable=None)
        return result

    def require_mutable(self) -> None:
        """Recheck publication for every profile and stale handle, before any effect."""
        super().require_mutable()
        current = record(ACTIVE)
        require(digest(canonical(current)) == self.binding_hash
                and type(current['version']) is int and current['version'] == 1
                and not os.path.lexists(self.path.parent.parent / 'registration')
                and not os.path.lexists(self.path.parent.parent / 'recovery'),
                'RecoveryRequired', 'Accounting registration changed or partial; mutations frozen')

    def authorize_sql(self, action: int, first: str, second: str, database: str, source: str) -> int:
        """Defense for stale SQLite handles; uncached statements recheck each execution.

        Only read/SELECT/function/transaction opcodes are intrinsically read-only.
        Everything else, including PRAGMA, DDL, ATTACH, and writes, uses the same
        live mutation guard. SQLite converts callback denial into DatabaseError.
        """
        if action in (sqlite3.SQLITE_READ, sqlite3.SQLITE_SELECT, sqlite3.SQLITE_FUNCTION,
                      sqlite3.SQLITE_TRANSACTION, sqlite3.SQLITE_RECURSIVE):
            return sqlite3.SQLITE_OK
        try:
            self.require_mutable()
        except Exception:
            return sqlite3.SQLITE_DENY
        return sqlite3.SQLITE_OK

    def reserve(self, principal: int, run: str, maximum: dict, key: str,
                stage: str = 'poc', binding: str = None) -> dict:
        # The same physical POC/milestone ledger includes all profile charges.
        require(digest(canonical(record(ACTIVE))) == self.binding_hash,
                'RecoveryRequired', 'Persistent accounting identity changed')
        if self.profile == 'independent-replay':
            require(stage == 'poc', 'InvalidInput', 'Independent replay is POC-only; no fresh allowance')
            validate_store(record(ACTIVE), self.path)
        self.require_mutable()
        bound = digest(canonical({'profile': self.profile, 'request_binding': binding}))
        return super().reserve(principal, run, maximum, key, stage, bound)
