"""Operational v5 accounting source tests using private temporary SQLite stores."""
import multiprocessing as mp
import os
from pathlib import Path
import sqlite3
import tempfile
import unittest

from accounting_v5 import OperationalAccountingV5
from common import Failure, canonical, digest


CAMPAIGN = 'a' * 64
STORE = 'b' * 64
PRIOR = 'c' * 64
UID = os.getuid()


def create_store(path: Path) -> None:
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    path.unlink(missing_ok=True)
    db = sqlite3.connect(path, isolation_level=None)
    db.executescript("""
      CREATE TABLE reservations(
        id TEXT PRIMARY KEY, key TEXT UNIQUE NOT NULL, binding BLOB NOT NULL,
        run TEXT NOT NULL, stage TEXT NOT NULL, maximum BLOB NOT NULL,
        actual BLOB, receipt TEXT);
      CREATE TABLE metering(
        id TEXT PRIMARY KEY, reservation TEXT UNIQUE NOT NULL, body BLOB NOT NULL);
      CREATE TABLE overhead(
        key TEXT PRIMARY KEY, category TEXT NOT NULL, duration_us INTEGER NOT NULL);
      CREATE TABLE state(id INTEGER PRIMARY KEY CHECK(id=1), stopped INTEGER NOT NULL);
      CREATE TABLE store_identity(
        campaign TEXT NOT NULL, store_id TEXT NOT NULL UNIQUE,
        prior_history_receipt TEXT NOT NULL);
      INSERT INTO state VALUES(1,0);
    """)
    db.execute('INSERT INTO store_identity VALUES(?,?,?)', (CAMPAIGN, STORE, PRIOR))
    maximum = {'currency': 'USD', 'money_cents': 10, 'execution_us': 100, 'review_us': 20}
    request = canonical({'binding': None, 'maximum': maximum, 'run': 'carry', 'stage': 'poc'})
    db.execute('INSERT INTO reservations VALUES(?,?,?,?,?,?,NULL,NULL)',
               ('carry', 'carry', request, 'carry', 'poc', canonical(maximum)))
    actual = {'currency': 'USD', 'money_cents': 3, 'execution_us': 30, 'review_us': 6}
    meter = canonical({'evidence': 'd' * 64, 'reservation': 'carry', 'usage': actual})
    receipt = digest(meter)
    db.execute('INSERT INTO metering VALUES(?,?,?)', (receipt, 'carry', meter))
    db.execute('UPDATE reservations SET actual=?,receipt=? WHERE id=?',
               (canonical(actual), receipt, 'carry'))
    pending = {'currency': 'USD', 'money_cents': 5, 'execution_us': 50, 'review_us': 10}
    pending_request = canonical({'binding': None, 'maximum': pending, 'run': 'hold', 'stage': 'poc'})
    db.execute('INSERT INTO reservations VALUES(?,?,?,?,?,?,NULL,NULL)',
               ('hold', 'hold', pending_request, 'hold', 'poc', canonical(pending)))
    db.execute('INSERT INTO overhead VALUES(?,?,?)', ('prepare', 'preparation', 7))
    db.execute('PRAGMA wal_checkpoint(TRUNCATE)')
    db.close()
    path.chmod(0o600)
    path.parent.chmod(0o700)


def open_store(path: Path):
    return OperationalAccountingV5(path, allowed_uid=UID)


class OnceFailingCommit:
    def __init__(self, delegate: sqlite3.Connection) -> None:
        self.delegate = delegate
        self.failed = False

    def execute(self, sql: str, parameters=()):
        return self.delegate.execute(sql, parameters)

    def commit(self) -> None:
        if not self.failed:
            self.failed = True
            raise sqlite3.OperationalError('injected unknown COMMIT outcome')
        self.delegate.commit()

    def rollback(self) -> None:
        self.delegate.rollback()

    def close(self) -> None:
        self.delegate.close()


def reserve_worker(root: str, output: mp.Queue, key: str) -> None:
    try:
        store = open_store(Path(root) / 'accounting-v5.sqlite')
        value = {'currency': 'USD', 'money_cents': 2, 'execution_us': 2, 'review_us': 2}
        output.put(store.reserve(UID, key, value, key))
    except BaseException as exc:
        output.put(exc)
    finally:
        if 'store' in locals():
            store.close()


class AccountingV5Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.directory = tempfile.TemporaryDirectory()
        self.root = Path(self.directory.name)
        self.path = self.root / 'accounting-v5.sqlite'
        create_store(self.path)

    def tearDown(self) -> None:
        self.directory.cleanup()

    def test_positive_reserve_meter_settle_halt_preserves_lineage_and_pending_hold(self):
        maximum = {'currency': 'USD', 'money_cents': 2, 'execution_us': 20, 'review_us': 4}
        with open_store(self.path) as store:
            reserved = store.reserve(UID, 'fresh', maximum, 'fresh')
            metered = store.meter(UID, reserved['id'], {**maximum, 'money_cents': 1},
                                  'e' * 64)
            settled = store.settle(UID, reserved['id'], metered['receipt'])
            store.halt(UID)
            snapshot = store.snapshot(UID)
        self.assertFalse(reserved['existing'])
        self.assertEqual(settled['usage']['money_cents'], 1)
        self.assertTrue(snapshot['stopped'])
        self.assertEqual(snapshot['pending'], 1)
        self.assertIn(('carry', 'carry', 'poc', False), snapshot['reservations'])
        self.assertIn(('hold', 'hold', 'poc', True), snapshot['reservations'])
        with sqlite3.connect(self.path) as db:
            self.assertEqual(db.execute('SELECT * FROM store_identity').fetchall(),
                             [(CAMPAIGN, STORE, PRIOR)])
            self.assertEqual(db.execute('SELECT stopped FROM state').fetchone(), (1,))

    def test_missing_file_never_creates_store(self):
        missing = self.root / 'missing.sqlite'
        with self.assertRaises(Failure), open_store(missing):
            pass
        self.assertFalse(missing.exists())

    def test_tampered_schema_is_rejected_without_mutation(self):
        with sqlite3.connect(self.path) as db:
            db.execute('CREATE TABLE unauthorized(value TEXT)')
        before = self.path.read_bytes()
        with self.assertRaises(Failure) as blocked, open_store(self.path):
            pass
        self.assertEqual(blocked.exception.record['code'], 'IntegrityFailure')
        self.assertEqual(self.path.read_bytes()[:len(before)], before)

    def test_negative_and_huge_carried_values_are_rejected(self):
        for money in (-1, 2**63):
            create_store(self.path)
            value = {'currency': 'USD', 'money_cents': money, 'execution_us': 1, 'review_us': 1}
            request = canonical({'binding': None, 'maximum': value, 'run': 'bad', 'stage': 'poc'})
            with sqlite3.connect(self.path) as db:
                db.execute('INSERT INTO reservations VALUES(?,?,?,?,?,?,NULL,NULL)',
                           ('bad', 'bad', request, 'bad', 'poc', canonical(value)))
            with self.assertRaises(Failure) as blocked, open_store(self.path):
                pass
            self.assertEqual(blocked.exception.record['code'], 'InvalidInput')

    def test_duplicate_settle_is_idempotent_and_settle_without_reserve_fails(self):
        with open_store(self.path) as store:
            with self.assertRaises(Failure) as missing:
                store.settle(UID, 'absent', 'f' * 64)
            self.assertEqual(missing.exception.record['code'], 'BudgetUnknown')
            maximum = {'currency': 'USD', 'money_cents': 1, 'execution_us': 1, 'review_us': 1}
            reservation = store.reserve(UID, 'fresh', maximum, 'fresh')
            receipt = store.meter(UID, reservation['id'], maximum, 'f' * 64)['receipt']
            first = store.settle(UID, reservation['id'], receipt)
            second = store.settle(UID, reservation['id'], receipt)
        self.assertEqual(first, second)
        with sqlite3.connect(self.path) as db:
            self.assertEqual(db.execute(
                'SELECT count(*) FROM reservations WHERE id=? AND actual IS NOT NULL',
                (reservation['id'],)).fetchone(), (1,))

    def test_halt_then_reserve_is_denied_and_stop_is_not_reset(self):
        with open_store(self.path) as store:
            store.halt(UID)
            with self.assertRaises(Failure) as blocked:
                store.reserve(UID, 'after-halt', {
                    'currency': 'USD', 'money_cents': 1, 'execution_us': 1, 'review_us': 1,
                }, 'after-halt')
        self.assertEqual(blocked.exception.record['code'], 'Stopped')
        with sqlite3.connect(self.path) as db:
            self.assertEqual(db.execute('SELECT stopped FROM state').fetchone(), (1,))

    def test_concurrent_reserves_from_two_connections_serialize(self):
        queue = mp.Queue()
        processes = [mp.Process(target=reserve_worker, args=(str(self.root), queue, key))
                     for key in ('concurrent-a', 'concurrent-b')]
        for process in processes:
            process.start()
        results = [queue.get(timeout=60) for _ in processes]
        for process in processes:
            process.join(10)
            self.assertFalse(process.exitcode)
        self.assertTrue(all(not isinstance(result, BaseException) for result in results))
        with sqlite3.connect(self.path) as db:
            self.assertEqual(db.execute(
                "SELECT count(*) FROM reservations WHERE key LIKE 'concurrent-%'").fetchone(), (2,))

    def test_unknown_commit_outcome_halts_and_retains_unsettled_reservation(self):
        def factory(*args, **kwargs):
            return OnceFailingCommit(sqlite3.connect(*args, **kwargs))
        maximum = {'currency': 'USD', 'money_cents': 1, 'execution_us': 1, 'review_us': 1}
        store = OperationalAccountingV5(self.path, allowed_uid=UID, connection_factory=factory)
        with self.assertRaises(Failure) as blocked:
            store.reserve(UID, 'unknown', maximum, 'unknown')
        store.close()
        self.assertEqual(blocked.exception.record['code'], 'RecoveryRequired')
        with sqlite3.connect(self.path) as db:
            self.assertEqual(db.execute('SELECT stopped FROM state').fetchone(), (1,))
            row = db.execute(
                "SELECT actual,receipt FROM reservations WHERE key='unknown'").fetchone()
            if row is not None:
                self.assertEqual(row, (None, None))
        with self.assertRaises(Failure) as denied:
            reopened = OperationalAccountingV5(self.path, allowed_uid=UID)
            reopened.reserve(UID, 'after-unknown', {
                'currency': 'USD', 'money_cents': 1, 'execution_us': 1, 'review_us': 1,
            }, 'after-unknown')
        self.assertEqual(denied.exception.record['code'], 'Stopped')


if __name__ == '__main__':
    unittest.main()
