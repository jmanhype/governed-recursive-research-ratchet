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
                                    inventory, snapshot, unchanged, verify)

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
    db_info = database.stat()
    active = {'campaign': 'c' * 64, 'device': db_info.st_dev, 'directory': str(store),
              'inode': db_info.st_ino, 'prior_history_receipt': 'd' * 64,
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

    def test_verify_rejects_post_install_drift(self):
        self.install()
        db = sqlite3.connect(self.database)
        db.execute("INSERT INTO overhead VALUES('k2','preparation',9)")
        db.commit()
        db.close()
        with self.assertRaises(RuntimeError):
            verify(self.base, owner=OWNER)

    def test_binding_rejects_active_identity_mismatch(self):
        active = json.loads((self.base / 'active.json').read_text())
        active['inode'] = active['inode'] + 1
        os.chmod(self.base / 'active.json', 0o644)
        (self.base / 'active.json').write_bytes(canonical(active))
        os.chmod(self.base / 'active.json', 0o444)
        with self.assertRaises(RuntimeError):
            snapshot(self.base, owner=OWNER, active_uid=OWNER)

    def test_schema_objects_are_part_of_the_baseline(self):
        db = sqlite3.connect(self.database)
        db.execute("CREATE TRIGGER hidden AFTER UPDATE ON state BEGIN SELECT 1; END")
        db.commit()
        db.close()
        with self.assertRaises(RuntimeError):
            self.install()

    def test_verify_rejects_metadata_drift(self):
        self.install()
        os.chmod(self.database, 0o644)
        with self.assertRaises(RuntimeError):
            verify(self.base, owner=OWNER)

    def test_unlisted_table_data_is_part_of_the_baseline(self):
        db = sqlite3.connect(self.database)
        db.execute('CREATE TABLE audit(id INTEGER PRIMARY KEY, note TEXT)')
        db.execute("INSERT INTO audit(note) VALUES('before')")
        db.commit()
        db.close()
        self.records = build(self.base, RESEARCH, owner=OWNER, active_uid=OWNER)
        db = sqlite3.connect(self.database)
        db.execute("UPDATE audit SET note='after' WHERE id=1")
        db.commit()
        db.close()
        with self.assertRaises(RuntimeError):
            self.install()

    def test_trigger_side_effect_on_unlisted_table_is_refused_and_restored(self):
        db = sqlite3.connect(self.database)
        db.execute('CREATE TABLE audit(id INTEGER PRIMARY KEY, note TEXT)')
        db.execute("CREATE TRIGGER release_audit AFTER UPDATE ON state "
                   "BEGIN INSERT INTO audit(note) VALUES('released'); END")
        db.commit()
        db.close()
        self.records = build(self.base, RESEARCH, owner=OWNER, active_uid=OWNER)
        with self.assertRaises(RuntimeError):
            self.install()
        db = sqlite3.connect(self.database)
        self.assertEqual(db.execute('SELECT stopped FROM state').fetchone(), (1,))
        db.close()
        with self.assertRaises(RuntimeError):
            verify(self.base, owner=OWNER)

    def test_blob_and_text_are_not_interchangeable(self):
        db = sqlite3.connect(self.database)
        db.execute("INSERT INTO metering VALUES('m2','r1',x'31')")
        db.commit()
        db.close()
        self.records = build(self.base, RESEARCH, owner=OWNER, active_uid=OWNER)
        db = sqlite3.connect(self.database)
        db.execute("UPDATE metering SET body='31' WHERE id='m2'")
        db.commit()
        db.close()
        with self.assertRaises(RuntimeError):
            self.install()

    def test_rowid_identity_is_part_of_the_baseline(self):
        db = sqlite3.connect(self.database)
        db.execute("INSERT INTO store_identity VALUES('c','s','r')")
        db.commit()
        db.close()
        self.records = build(self.base, RESEARCH, owner=OWNER, active_uid=OWNER)
        db = sqlite3.connect(self.database)
        db.execute('DELETE FROM store_identity')
        db.execute("INSERT INTO store_identity VALUES('c','s','r')")
        db.commit()
        db.close()
        with self.assertRaises(RuntimeError):
            self.install()

    def test_post_publish_verification_failure_restores_and_records(self):
        import accounting_recovery_v4 as module
        original = module.verify

        def failing(base, *, owner=OWNER):
            raise RuntimeError('simulated post-publish verification failure')

        module.verify = failing
        try:
            with self.assertRaises(RuntimeError):
                self.install()
        finally:
            module.verify = original
        db = sqlite3.connect(self.database)
        self.assertEqual(db.execute('SELECT stopped FROM state').fetchone(), (1,))
        db.close()
        recovery = self.base / 'recovery-v4'
        self.assertIn('incomplete.json', {item.name for item in recovery.iterdir()})
        with self.assertRaises(RuntimeError):
            original(self.base, owner=OWNER)

    def test_authorization_boolean_confusion_is_refused(self):
        broken = copy.deepcopy(self.records)
        broken['authorization']['execution_authorized'] = 1
        with self.assertRaises(RuntimeError):
            self.install(broken)
        broken = copy.deepcopy(self.records)
        broken['authorization']['exclusive_parent'] = 1
        with self.assertRaises(RuntimeError):
            self.install(broken)

    def test_pre_publication_failure_publishes_no_completion(self):
        import accounting_recovery_v4 as module
        original = module._verify_state

        def failing(base, owner, *, published):
            raise RuntimeError('simulated pre-publication failure')

        module._verify_state = failing
        try:
            with self.assertRaises(RuntimeError):
                self.install()
        finally:
            module._verify_state = original
        recovery = self.base / 'recovery-v4'
        self.assertNotIn('complete.json', {item.name for item in recovery.iterdir()})
        db = sqlite3.connect(self.database)
        self.assertEqual(db.execute('SELECT stopped FROM state').fetchone(), (1,))
        db.close()

    def test_verify_rejects_open_journal_sidecar(self):
        self.install()
        sidecar = Path(str(self.database) + '-wal')
        sidecar.write_bytes(b'')
        os.chmod(sidecar, 0o600)
        try:
            with self.assertRaises(RuntimeError):
                verify(self.base, owner=OWNER)
        finally:
            sidecar.unlink()

    def test_repeat_install_verification_failure_invalidates_completion(self):
        self.install()
        import accounting_recovery_v4 as module
        original = module.verify

        def failing(base, *, owner=OWNER):
            raise RuntimeError('simulated repeat verification failure')

        module.verify = failing
        try:
            with self.assertRaises(RuntimeError):
                self.install()
        finally:
            module.verify = original
        db = sqlite3.connect(self.database)
        self.assertEqual(db.execute('SELECT stopped FROM state').fetchone(), (1,))
        db.close()
        names = {item.name for item in (self.base / 'recovery-v4').iterdir()}
        self.assertIn('incomplete.json', names)
        self.assertNotIn('complete.json', names)

    def test_header_mutation_after_plan_is_refused(self):
        db = sqlite3.connect(self.database)
        db.execute('PRAGMA user_version=7')
        db.commit()
        db.close()
        with self.assertRaises(RuntimeError):
            self.install()

    def test_inventory_refuses_shadowed_rowid(self):
        db = sqlite3.connect(self.database)
        db.execute('CREATE TABLE shadow(rowid TEXT, value TEXT)')
        db.execute("INSERT INTO shadow VALUES('a','b')")
        db.commit()
        db.close()
        with self.assertRaises(RuntimeError):
            inventory(self.database)

    def test_unresolvable_target_still_invalidates_completion(self):
        self.install()
        os.chmod(self.base / 'active.json', 0o644)
        (self.base / 'active.json').write_bytes(b'{}')
        os.chmod(self.base / 'active.json', 0o444)
        import accounting_recovery_v4 as module
        original = module.verify

        def failing(base, *, owner=OWNER):
            raise RuntimeError('simulated verification failure')

        module.verify = failing
        try:
            with self.assertRaises(RuntimeError):
                self.install()
        finally:
            module.verify = original
        names = {item.name for item in (self.base / 'recovery-v4').iterdir()}
        self.assertIn('incomplete.json', names)
        self.assertNotIn('complete.json', names)

    def test_unchanged_detects_header_drift(self):
        before = snapshot(self.base, owner=OWNER, active_uid=OWNER)['inventory']
        after = copy.deepcopy(before)
        after['tables']['state']['rows'][0][-1] = ['i', 0]
        after['database_sha256'] = 'irrelevant'
        unchanged(before, after)
        after['header']['user_version'] = 7
        with self.assertRaises(RuntimeError):
            unchanged(before, after)

    def test_without_rowid_table_is_supported(self):
        db = sqlite3.connect(self.database)
        db.execute('CREATE TABLE wr(key TEXT PRIMARY KEY, value TEXT) WITHOUT ROWID')
        db.execute("INSERT INTO wr VALUES('a','b')")
        db.commit()
        db.close()
        found = inventory(self.database)['tables']['wr']
        self.assertFalse(found['rowid'])
        self.assertEqual(found['rows'], [[['s', 'a'], ['s', 'b']]])

    def test_generated_column_shadowing_rowid_alias_is_refused(self):
        db = sqlite3.connect(self.database)
        db.execute('CREATE TABLE shadowed(id INTEGER PRIMARY KEY, '
                   '_grrr_rowid TEXT GENERATED ALWAYS AS (id) VIRTUAL)')
        db.execute('INSERT INTO shadowed(id) VALUES(1)')
        db.commit()
        db.close()
        with self.assertRaises(RuntimeError):
            inventory(self.database)

    def test_empty_generated_alias_masks_are_refused(self):
        for alias in ('rowid', '_rowid_', 'oid', '_grrr_rowid'):
            for storage in ('VIRTUAL', 'STORED'):
                with self.subTest(alias=alias, storage=storage):
                    db = sqlite3.connect(self.database)
                    db.execute('CREATE TABLE shadowed(id INTEGER PRIMARY KEY, "'
                               + alias.upper() + '" TEXT GENERATED ALWAYS AS (id) '
                               + storage + ')')
                    db.commit()
                    db.close()
                    with self.assertRaisesRegex(RuntimeError, 'masks the hidden rowid'):
                        inventory(self.database)
                    db = sqlite3.connect(self.database)
                    db.execute('DROP TABLE shadowed')
                    db.commit()
                    db.close()

    def test_comment_words_do_not_hide_rowid_changes(self):
        for comment in ('/* WITHOUT ROWID */', '-- WITHOUT and ROWID\n',
                        '/* WITHOUT */ /* ROWID */'):
            with self.subTest(comment=comment):
                db = sqlite3.connect(self.database)
                db.execute('UPDATE state SET stopped=1')
                db.execute('CREATE TABLE commented(value TEXT) ' + comment)
                db.execute("INSERT INTO commented(rowid,value) VALUES(7,'same')")
                db.commit()
                db.close()
                before = inventory(self.database)
                self.assertTrue(before['tables']['commented']['rowid'])
                db = sqlite3.connect(self.database)
                db.execute('UPDATE state SET stopped=0')
                db.commit()
                db.close()
                unchanged(before, inventory(self.database))
                db = sqlite3.connect(self.database)
                db.execute('UPDATE commented SET rowid=8')
                db.commit()
                db.close()
                with self.assertRaisesRegex(RuntimeError, 'rows changed'):
                    unchanged(before, inventory(self.database))
                db = sqlite3.connect(self.database)
                db.execute('DROP TABLE commented')
                db.commit()
                db.close()

    def test_empty_without_rowid_and_quoted_names(self):
        db = sqlite3.connect(self.database)
        db.execute('CREATE TABLE "wr""quoted"("rowid" TEXT PRIMARY KEY, '
                   '"_rowid_" TEXT) WITHOUT /* split options */ ROWID')
        db.execute('CREATE TABLE "ordinary""quoted"("WITHOUT" TEXT, "ROWID value" TEXT)')
        db.commit()
        db.close()
        found = inventory(self.database)['tables']
        self.assertEqual(found['wr"quoted'], {'rowid': False, 'rows': []})
        self.assertEqual(found['ordinary"quoted'], {'rowid': True, 'rows': []})
        db = sqlite3.connect(self.database)
        db.execute('INSERT INTO "ordinary""quoted" VALUES(\'a\',\'b\')')
        db.commit()
        db.close()
        self.assertEqual(inventory(self.database)['tables']['ordinary"quoted']['rows'],
                         [[['i', 1], ['s', 'a'], ['s', 'b']]])

    def test_nonempty_unmasked_generated_columns_capture_identity(self):
        db = sqlite3.connect(self.database)
        db.execute('CREATE TABLE generated(value INTEGER, '
                   '"virtual" INTEGER GENERATED ALWAYS AS (value+1) VIRTUAL, '
                   '"stored" INTEGER GENERATED ALWAYS AS (value+2) STORED)')
        db.execute('INSERT INTO generated(rowid,value) VALUES(9,20)')
        db.commit()
        db.close()
        self.assertEqual(inventory(self.database)['tables']['generated'],
                         {'rowid': True, 'rows': [
                             [['i', 9], ['i', 20], ['i', 21], ['i', 22]]]})

    def test_all_hidden_aliases_masked_fail_closed_when_empty(self):
        db = sqlite3.connect(self.database)
        db.execute('CREATE TABLE masked(rowid TEXT, _rowid_ TEXT, oid TEXT)')
        db.commit()
        db.close()
        with self.assertRaisesRegex(RuntimeError, 'masks the hidden rowid'):
            inventory(self.database)


if __name__ == '__main__':
    unittest.main()
