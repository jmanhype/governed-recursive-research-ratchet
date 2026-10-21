"""A campaign has one pre-provisioned store, never a fresh runtime allowance."""
import os
import json
from pathlib import Path
import sqlite3
import stat
from budget import Budget, vector, CEILINGS
from common import EVALUATOR, canonical, digest, fields, identifier, require
from trusted_install import immutable, record

ACTIVE = Path('/Library/GRRR/accounting/active.json')
PROFILES = ('synthetic', 'offline', 'trusted-observation')


def validate_store(binding, path):
    fields(binding, {'version', 'campaign', 'store_id', 'directory', 'prior_history_receipt', 'profiles',
                     'device', 'inode'})
    require(binding['version'] == 1 and type(binding['version']) is int
            and binding['profiles'] == list(PROFILES), 'RecoveryRequired', 'Persistent binding schema differs')
    for key in ('campaign', 'store_id', 'prior_history_receipt'):
        identifier(binding[key], True)
    require(path == Path(binding['directory']) / 'budget.sqlite', 'RecoveryRequired', 'Store path differs')
    info = path.lstat()
    require(stat.S_ISREG(info.st_mode) and info.st_uid == EVALUATOR
            and info.st_nlink == 1 and info.st_mode & 0o077 == 0
            and type(binding['device']) is int and type(binding['inode']) is int
            and (info.st_dev, info.st_ino) == (binding['device'], binding['inode']),
            'RecoveryRequired', 'Persistent database missing or unsafe')
    with sqlite3.connect(path.as_uri() + '?mode=ro', uri=True) as db:
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
    def __init__(self, profile):
        require(profile in PROFILES, 'InvalidInput', 'Unregistered accounting profile')
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
        super().__init__(path, existing=True)
        self.profile = profile
        self.store_id = binding['store_id']
        self.binding_hash = digest(canonical(binding))

    def reserve(self, principal, run, maximum, key, stage='poc', binding=None):
        # The same physical POC/milestone ledger includes all profile charges.
        require(digest(canonical(record(ACTIVE))) == self.binding_hash,
                'RecoveryRequired', 'Persistent accounting identity changed')
        bound = digest(canonical({'profile': self.profile, 'request_binding': binding}))
        return super().reserve(principal, run, maximum, key, stage, bound)
