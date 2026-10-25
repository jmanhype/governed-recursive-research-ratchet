"""No-guest fixtures: real SQLite/files, translated ownership; NOT live proof."""
from contextlib import closing
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import unittest
from unittest.mock import patch

import unit_replay_accounting_registration as registration_tests
from unit_replay_accounting_registration import ROOT
import accounting_registration as reg
import accounting_recovery as recovery
import persistent_budget
from common import Failure


class Recovery(unittest.TestCase):
    def setUp(self):
        self.fixture = registration_tests.Registration('test_registration_preserves_every_database_byte_and_hold')
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        if self._testMethodName == 'test_three_pending_holds_at_exact_ceiling_retained':
            store = registration_tests.budget.Budget(self.fixture.database, existing=True)
            try:
                store.db.execute('UPDATE state SET stopped=0')
                store.reserve(os.getuid(), 'old-run', registration_tests.vector(4988), 'hold-two')
                store.reserve(os.getuid(), 'old-run', registration_tests.vector(), 'hold-three')
                with self.assertRaises(Failure):
                    store.reserve(os.getuid(), 'old-run', registration_tests.vector(1), 'over-ceiling')
                store.halt()
            finally:
                store.db.close()
            reg.DATABASE_SHA256 = reg.sha(self.fixture.database.read_bytes())
            self.fixture.baseline = reg.baseline()
        self.fixture.install()
        self.base = self.fixture.base
        self.database = self.fixture.database
        self.before = recovery.snapshot()
        self.registration_bytes = [(p, p.read_bytes()) for p in (self.base / 'registration').iterdir()]
        self.fixture.stack.enter_context(patch.object(recovery, 'bootstrap', lambda: None))
        self.fixture.stack.enter_context(patch.object(recovery, 'INSTALL', self.fixture.bootstrap / 'accounting_recovery.py'))
        review = {'decision': 'approved-stop-only-read-only', 'action': recovery.ACTION,
                  'baseline_sha256': reg.sha(reg.canonical(self.before)), 'sources': recovery.sources(),
                  'ceilings': reg.CEILINGS, 'allowed_mutations': [],
                  'historical_unknowns': 'unresolved', 'spendable': None, 'execution_authorized': False}
        self.plan = {'version': 1, 'action': recovery.ACTION, 'baseline': self.before,
                     'sources': recovery.sources(), 'review_sha256': reg.sha(reg.canonical(review))}
        self.review = review
        self.authorization = {'principal': 'operator-via-exclusive-root-parent', 'action': recovery.ACTION,
                              'plan_sha256': reg.sha(reg.canonical(self.plan)),
                              'review_sha256': self.plan['review_sha256'],
                              'baseline_sha256': review['baseline_sha256'], 'sources': recovery.sources(),
                              'exclusive_parent': True, 'execution_authorized': False}

    def inputs(self):
        paths = []
        for name, value in [('recovery-plan', self.plan), ('review', self.review), ('authorization', self.authorization)]:
            path = self.fixture.bootstrap / (name + '.json')
            if path.exists():
                path.chmod(0o644)
            path.write_bytes(reg.canonical(value))
            path.chmod(0o444)
            paths.append(path)
        return paths

    def install(self):
        return recovery.install(*self.inputs(), reg.sha(reg.canonical(self.authorization)))

    def test_success_preserves_exact_history_identity_and_unknowns(self):
        result = self.install()
        self.assertEqual(result['binding']['version'], 3)
        self.assertEqual(result, recovery.verify())
        after = reg.inventory(self.database, self.fixture.binding, expected_stop=0)
        recovery.unchanged(self.before['inventory'], after)
        self.assertEqual(after['pending'], 1)
        self.assertEqual(after['known_encumbered'], {'poc': [12, 800, 80], 'milestone': [12, 800, 80]})
        self.assertEqual(after['historical_unknowns'], 'unresolved')
        self.assertIsNone(after['spendable'])
        self.assertEqual(self.database.stat().st_ino, self.fixture.before_inode)
        for path, raw in self.registration_bytes:
            self.assertEqual(path.read_bytes(), raw)
        self.assertEqual(result['receipt']['allowed_mutations'], [])
        self.assertFalse(result['receipt']['execution_authorized'])
        with self.assertRaises(ValueError):
            reg.verify()  # v2 verifier is deliberately not relaxed.

    def test_three_pending_holds_at_exact_ceiling_retained(self):
        self.install()
        after = reg.inventory(self.database, self.fixture.binding, expected_stop=0)
        recovery.unchanged(self.before['inventory'], after)
        self.assertEqual(after['pending'], 3)
        self.assertEqual(after['known_encumbered']['poc'][0], 5000)
        self.assertEqual(after['known_encumbered']['milestone'][0], 5000)
        self.assertIsNone(after['spendable'])
        with self.fixture.persistent_context():
            store = persistent_budget.PersistentBudget('independent-replay')
            try:
                self.assertIsNone(store.totals(os.getuid())['spendable'])
                self.assertEqual(store.totals(os.getuid())['historical_unknowns'], 'unresolved')
                with self.assertRaises(Failure):
                    store.reserve(os.getuid(), 'run', registration_tests.vector(), 'zero')
            finally:
                store.db.close()

    def test_runtime_all_profiles_and_sql_surfaces_remain_frozen(self):
        self.install()
        raw = self.database.read_bytes()
        with self.fixture.persistent_context():
            for profile in reg.PROFILES:
                store = persistent_budget.PersistentBudget(profile)
                try:
                    self.assertTrue(store.read_only)
                    self.fixture.assert_frozen_mutators(store)
                    self.fixture.assert_blob_access_read_only(store)
                    for sql in ('PRAGMA user_version=3', 'CREATE TABLE forbidden(x)',
                                "ATTACH DATABASE ':memory:' AS forbidden"):
                        with self.subTest(profile=profile, sql=sql), self.assertRaises(sqlite3.DatabaseError):
                            store.db.execute(sql)
                    self.assertFalse(store.totals(os.getuid())['stopped'])
                finally:
                    store.db.close()
        self.assertEqual(self.database.read_bytes(), raw)

    def test_stale_registered_handles_and_cached_cursor_remain_frozen(self):
        with self.fixture.persistent_context():
            store = persistent_budget.PersistentBudget('offline')
            try:
                store.prepublication_cursor = store.db.cursor()
                store.prepublication_cursor.execute('SELECT * FROM state').fetchall()
                self.install()
                self.fixture.assert_frozen_mutators(store)
                self.fixture.assert_blob_access_read_only(store)
            finally:
                store.db.close()

    def test_repeated_install_refuses_without_reusing_authorization(self):
        self.install()
        raw = {p: p.read_bytes() for p in (self.base / 'recovery').iterdir()}
        with self.assertRaises(ValueError):
            self.install()
        for path, value in raw.items():
            self.assertEqual(path.read_bytes(), value)

    def test_changed_authority_source_review_plan_refuse_before_effects(self):
        for document, key, value in [('plan', 'version', True), ('plan', 'action', 'register'),
                                    ('plan', 'sources', {}), ('review', 'allowed_mutations', ['reserve']),
                                    ('authorization', 'principal', 'registration'),
                                    ('authorization', 'exclusive_parent', False),
                                    ('authorization', 'exclusive_parent', 1),
                                    ('authorization', 'execution_authorized', True),
                                    ('authorization', 'plan_sha256', 'f' * 64)]:
            original = getattr(self, document)
            setattr(self, document, dict(original, **{key: value}))
            with self.subTest(document=document, key=key), self.assertRaises(ValueError):
                self.install()
            setattr(self, document, original)
            self.assertFalse((self.base / 'recovery').exists())
        self.assertEqual(self.database.read_bytes(), self.fixture.before)

    def test_missing_extra_duplicate_and_noncanonical_input_fields(self):
        paths = self.inputs()
        expected = reg.sha(reg.canonical(self.authorization))
        for raw in (b'{"x":1,"x":2}', reg.canonical(self.plan) + b'\n', b'{}',
                    reg.canonical(dict(self.plan, unexpected=1))):
            paths[0].chmod(0o644)
            paths[0].write_bytes(raw)
            paths[0].chmod(0o444)
            with self.assertRaises(ValueError):
                recovery.install(*paths, expected)
        self.assertFalse((self.base / 'recovery').exists())

    def test_baseline_tampering_and_unknown_journal_refuse(self):
        for suffix in ('-wal', '-journal', '-shm'):
            sidecar = Path(str(self.database) + suffix)
            sidecar.write_bytes(b'partial')
            with self.assertRaises(ValueError):
                self.install()
            sidecar.unlink()
        self.assertFalse((self.base / 'recovery').exists())

    def test_actual_concurrent_sqlite_writer_refuses_before_outputs(self):
        other = sqlite3.connect(self.database, isolation_level=None)
        try:
            other.execute('BEGIN IMMEDIATE')
            with self.assertRaises(sqlite3.OperationalError):
                self.install()
            self.assertFalse((self.base / 'recovery').exists())
        finally:
            other.rollback()
            other.close()

    def test_actual_competing_launch_lock_refuses(self):
        import fcntl
        with (self.base / 'launch.lock').open('rb') as stream:
            fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
            with self.assertRaises(BlockingIOError):
                self.install()
        self.assertFalse((self.base / 'recovery').exists())

    def test_failure_before_database_commit_is_explicit_partial(self):
        original = reg.exclusive
        def fail(path, raw):
            if path.name == 'prior-active.json':
                raise OSError('injected before database effect')
            original(path, raw)
        with patch.object(reg, 'exclusive', fail), self.assertRaises(OSError):
            self.install()
        self.assertEqual(self.database.read_bytes(), self.fixture.before)
        self.assert_uncertain()

    def assert_uncertain(self):
        self.assertEqual(reg.decode((self.base / 'recovery/uncertain.json').read_bytes())['outcome'],
                         'uncertain-no-retry')
        with self.assertRaises(ValueError):
            recovery.verify()
        with self.assertRaises(ValueError):
            self.install()
        with self.fixture.persistent_context(), self.assertRaises(Failure):
            persistent_budget.PersistentBudget('independent-replay')

    def test_failure_after_database_commit_never_claims_success(self):
        original = reg.exclusive
        def fail(path, raw):
            if path.name == 'receipt.json':
                raise OSError('injected after database commit')
            original(path, raw)
        with patch.object(reg, 'exclusive', fail), self.assertRaises(OSError):
            self.install()
        self.assertEqual(reg.inventory(self.database, self.fixture.binding, expected_stop=0)['stopped'], 0)
        self.assert_uncertain()

    def test_failure_after_publication_remains_unusable(self):
        original = reg.exclusive
        def fail(path, raw):
            if path.name == 'complete.json':
                raise OSError('injected completion failure')
            original(path, raw)
        with patch.object(reg, 'exclusive', fail), self.assertRaises(OSError):
            self.install()
        self.assertEqual(reg.decode(self.fixture.active.read_bytes())['version'], 3)
        self.assert_uncertain()

    def test_receipt_tamper_missing_noncanonical_and_unknown_artifacts(self):
        self.install()
        path = self.base / 'recovery/receipt.json'
        raw = path.read_bytes()
        for value in (b'{}', raw + b'\n', reg.canonical(dict(reg.decode(raw), unexpected=1))):
            path.chmod(0o644)
            path.write_bytes(value)
            path.chmod(0o444)
            with self.assertRaises(ValueError):
                recovery.verify()
        path.chmod(0o644)
        path.write_bytes(raw)
        path.chmod(0o444)
        directory = path.parent
        directory.chmod(0o755)
        (directory / 'unknown').write_bytes(b'unknown')
        directory.chmod(0o555)
        with self.assertRaises(ValueError):
            recovery.verify()

    def test_replaced_database_and_history_tamper_refuse(self):
        self.install()
        with closing(sqlite3.connect(self.database)) as db:
            db.execute('UPDATE reservations SET actual=NULL,receipt=NULL')
            db.commit()
        with self.assertRaises(ValueError):
            recovery.verify()

    def test_replaced_inode_refuses_identical_bytes(self):
        self.install()
        replacement = self.database.parent / 'replacement'
        replacement.write_bytes(self.database.read_bytes())
        replacement.chmod(0o600)
        replacement.replace(self.database)
        with self.assertRaises(ValueError):
            recovery.verify()

    def test_wrong_mode_symlink_and_hardlink_refuse(self):
        self.install()
        self.database.chmod(0o644)
        with self.assertRaises(ValueError):
            recovery.verify()
        self.database.chmod(0o600)
        target = self.database.parent / 'target'
        self.database.rename(target)
        self.database.symlink_to(target)
        with self.assertRaises((ValueError, OSError)):
            recovery.verify()
        self.database.unlink()
        target.rename(self.database)
        os.link(self.database, target)
        with self.assertRaises(ValueError):
            recovery.verify()

    def test_missing_receipt_refuses(self):
        self.install()
        directory = self.base / 'recovery'
        directory.chmod(0o755)
        (directory / 'receipt.json').unlink()
        directory.chmod(0o555)
        with self.assertRaises(ValueError):
            recovery.verify()

    def test_unknown_binding_versions_never_fallback_to_mutable(self):
        self.install()
        value = reg.decode(self.fixture.active.read_bytes())
        for version in (True, 0, 4, '3'):
            with self.subTest(version=version), self.assertRaises(Failure):
                persistent_budget.validate_store(dict(value, version=version), self.database)


class Entrypoint(unittest.TestCase):
    def test_checkout_cannot_execute_recovery(self):
        result = subprocess.run([sys.executable, '-I', '-S', '-B',
                                 str(ROOT / 'research/accounting_recovery.py'), 'verify'],
                                capture_output=True, text=True, timeout=5)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('root-only', result.stderr)


if __name__ == '__main__':
    unittest.main()
