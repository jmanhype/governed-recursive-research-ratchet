"""Fixture-only tests for the v4 stop release; no live store is touched."""
import copy
import json
import os
from pathlib import Path
import sqlite3
import tempfile
import unittest

from accounting_recovery_planner_v4 import build
from accounting_recovery_v4 import (approval, apply_install, canonical, digest,
                                    snapshot, verify)

OWNER = os.getuid()
RESEARCH = Path(__file__).resolve().parents[1] / 'research'
STORE = 'a' * 64


def create_store(base: Path) -> Path:
    store = base / STORE
    store.mkdir(mode=0o700)
    database = store / 'budget.sqlite'
    db = sqlite3.connect(database)
    db.executescript("""
      CREATE TABLE reservations(id TEXT PRIMARY KEY, key TEXT, binding BLOB,
                                run TEXT, stage TEXT, maximum BLOB, actual BLOB, receipt TEXT);
      CREATE TABLE metering(id TEXT PRIMARY KEY, reservation TEXT, body BLOB);
      CREATE TABLE overhead(key TEXT PRIMARY KEY, category TEXT, duration_us INTEGER);
      CREATE TABLE state(id INTEGER PRIMARY KEY, stopped INTEGER NOT NULL);
      CREATE TABLE store_identity(campaign TEXT, store_id TEXT, prior_history_receipt TEXT);
      INSERT INTO state VALUES(1,1);
      INSERT INTO reservations VALUES('r1','k1',x'00','run1','poc',x'00',NULL,NULL);
    """)
    db.commit()
    db.close()
    os.chmod(database, 0o600)
    active = {'campaign': 'c' * 64, 'device': 1, 'directory': str(store),
              'inode': store.stat().st_ino, 'prior_history_receipt': 'd' * 64,
              'profiles': ['independent-replay'], 'store_id': STORE, 'version': 4}
    (base / 'active.json').write_bytes(canonical(active))
    os.chmod(base / 'active.json', 0o444)
    return database


class RecoveryV4Tests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='grrr-recovery-v4-')
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.database = create_store(self.base)
        self.records = build(self.base, RESEARCH, owner=OWNER, active_uid=OWNER)

    def install(self, records=None, **changes):
        records = records or self.records
        return apply_install(self.base, records['plan'], records['review'],
                             records['authorization'], privileged=False,
                             owner=OWNER, active_uid=OWNER)

    def test_plan_and_authorization_are_exact(self):
        approval(self.records['plan'], self.records['review'],
                 self.records['authorization'])
        self.assertIn('release-stop', self.records['review']['allowed_mutations'])
        self.assertEqual(self.records['review']['historical_unknowns'], 'unresolved')
        self.assertIsNone(self.records['plan'].get('unexpected'))

    def test_install_releases_only_the_stop_bit(self):
        result = self.install()
        self.assertEqual(result['outcome'], 'published-durable')
        self.assertEqual(result['receipt']['stopped_before'], 1)
        self.assertEqual(result['receipt']['stopped_after'], 0)
        db = sqlite3.connect(self.database)
        self.assertEqual(db.execute('SELECT stopped FROM state').fetchone(), (0,))
        self.assertEqual(db.execute('SELECT count(*) FROM reservations').fetchone(), (1,))
        db.close()
        self.assertEqual(verify(self.base, owner=OWNER)['outcome'], 'published-durable')

    def test_repeat_install_is_idempotent_only_for_the_exact_records(self):
        first = self.install()
        second = self.install()
        self.assertEqual(first['outcome'], second['outcome'])
        broken = copy.deepcopy(self.records)
        broken['review']['decision'] = 'approved-something-else'
        with self.assertRaises(RuntimeError):
            self.install(broken)

    def test_install_refuses_changed_inventory(self):
        db = sqlite3.connect(self.database)
        db.execute("UPDATE reservations SET key='changed' WHERE id='r1'")
        db.commit()
        db.close()
        with self.assertRaises(RuntimeError):
            self.install()

    def test_install_refuses_mismatched_authorization(self):
        broken = copy.deepcopy(self.records)
        broken['authorization']['execution_authorized'] = False
        with self.assertRaises(RuntimeError):
            self.install(broken)

    def test_install_refuses_partial_recovery_namespace(self):
        (self.base / 'recovery-v4').mkdir()
        (self.base / 'recovery-v4' / 'intent.json').write_bytes(b'{}')
        with self.assertRaises(RuntimeError):
            self.install()

    def test_privileged_path_refuses_outside_the_canonical_closure(self):
        with self.assertRaises(RuntimeError):
            apply_install(self.base, self.records['plan'], self.records['review'],
                          self.records['authorization'], privileged=True,
                          owner=OWNER, active_uid=OWNER)

    def test_baseline_change_after_plan_refuses(self):
        db = sqlite3.connect(self.database)
        db.execute("INSERT INTO overhead VALUES('k','preparation',7)")
        db.commit()
        db.close()
        with self.assertRaises(RuntimeError):
            self.install()


if __name__ == '__main__':
    unittest.main()
