"""Declared source schema, NOT an installer, migration, or grant issuer."""
import sqlite3
from common import require

CORE_SQL = (
    'CREATE TABLE events(seq INTEGER PRIMARY KEY, prior TEXT NOT NULL, hash TEXT UNIQUE NOT NULL, body BLOB NOT NULL)',
    'CREATE TABLE idempotency(key TEXT PRIMARY KEY NOT NULL, seq INTEGER NOT NULL REFERENCES events(seq), prior TEXT NOT NULL, hash TEXT NOT NULL, body BLOB NOT NULL)',
    'CREATE TRIGGER immutable_update BEFORE UPDATE ON events BEGIN SELECT RAISE(ABORT,"immutable"); END',
    'CREATE TRIGGER immutable_delete BEFORE DELETE ON events BEGIN SELECT RAISE(ABORT,"immutable"); END',
)
JOURNAL_SQL = (
    '''CREATE TABLE capstone_grants(
grant_id TEXT PRIMARY KEY NOT NULL, raw BLOB NOT NULL, raw_sha256 TEXT NOT NULL,
authorization_sha256 TEXT NOT NULL, operator_uid INTEGER NOT NULL,
consumed_by TEXT UNIQUE,
CHECK(typeof(raw)='blob'), CHECK(typeof(operator_uid)='integer'))''',
    '''CREATE TABLE capstone_operations(
operation_id TEXT PRIMARY KEY NOT NULL,
grant_id TEXT UNIQUE NOT NULL REFERENCES capstone_grants(grant_id),
record BLOB NOT NULL CHECK(typeof(record)='blob'))''',
    '''CREATE TRIGGER capstone_grants_update BEFORE UPDATE ON capstone_grants
WHEN NEW.grant_id IS NOT OLD.grant_id OR NEW.raw IS NOT OLD.raw
OR NEW.raw_sha256 IS NOT OLD.raw_sha256
OR NEW.authorization_sha256 IS NOT OLD.authorization_sha256
OR NEW.operator_uid IS NOT OLD.operator_uid
OR OLD.consumed_by IS NOT NULL OR NEW.consumed_by IS NULL
BEGIN SELECT RAISE(ABORT,'immutable grant'); END''',
    '''CREATE TRIGGER capstone_grants_delete BEFORE DELETE ON capstone_grants
BEGIN SELECT RAISE(ABORT,'immutable grant'); END''',
    '''CREATE TRIGGER capstone_operations_update BEFORE UPDATE ON capstone_operations
WHEN NEW.operation_id IS NOT OLD.operation_id OR NEW.grant_id IS NOT OLD.grant_id
BEGIN SELECT RAISE(ABORT,'immutable operation'); END''',
    '''CREATE TRIGGER capstone_operations_delete BEFORE DELETE ON capstone_operations
BEGIN SELECT RAISE(ABORT,'immutable operation'); END''',
)


def validate_schema(db: sqlite3.Connection) -> None:
    """Read-only exact sqlite_master comparison, including implicit indexes.

    Unrelated ledger tables may coexist; extra objects on any owned table or
    in our namespace, temporary shadows, and attached databases are refused.
    """
    owned = {'events', 'idempotency', 'capstone_grants', 'capstone_operations'}
    expected = set(CORE_SQL + JOURNAL_SQL)
    rows = db.execute('SELECT type,name,tbl_name,sql FROM main.sqlite_master').fetchall()
    actual = set()
    indexes = set()
    for kind, name, table, sql in rows:
        if table in owned or name.startswith('capstone_'):
            if sql is None:
                indexes.add((kind, name, table))
            else:
                actual.add(sql)
    require(actual == expected, 'IntegrityFailure', 'Journal/core schema differs')
    expected_indexes = {('index', 'sqlite_autoindex_' + t + '_' + str(n), t)
                        for t, count in (('events', 1), ('idempotency', 1),
                                         ('capstone_grants', 2), ('capstone_operations', 2))
                        for n in range(1, count + 1)}
    require(indexes == expected_indexes, 'IntegrityFailure', 'Journal indexes differ')
    require(not db.execute('SELECT name FROM sqlite_temp_master').fetchall(),
            'IntegrityFailure', 'Temporary schema is not allowed')
    require(all(row[1] in ('main', 'temp') for row in db.execute('PRAGMA database_list')),
            'IntegrityFailure', 'Attached databases are not allowed')
    require(db.execute('PRAGMA foreign_keys').fetchone() == (1,)
            and db.execute('PRAGMA synchronous').fetchone() == (2,)
            and db.execute('PRAGMA journal_mode').fetchone() == ('delete',),
            'IntegrityFailure', 'Durability/foreign-key settings differ')
