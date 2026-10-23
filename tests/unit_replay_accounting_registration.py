"""No-guest unit tests; privileged ownership/entrypoint are mocked, never integration proof."""
import copy
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from contextlib import ExitStack, closing
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'research'))
import accounting_registration as registration
import budget
import persistent_budget
from common import Failure


def vector(cents=0, execution=0, review=0):
    return dict(currency='USD', money_cents=cents, execution_us=execution, review_us=review)


class Registration(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.root = Path(self.folder.name).resolve()
        self.base = self.root / 'accounting'
        self.base.mkdir()
        self.directory = self.base / registration.STORE
        self.directory.mkdir(mode=0o700)
        self.database = self.directory / 'budget.sqlite'
        self.stack = ExitStack()
        self.addCleanup(self.stack.close)
        self.stack.enter_context(patch.object(budget, 'EVALUATOR', os.getuid()))
        self.stack.enter_context(patch.object(persistent_budget, 'EVALUATOR', os.getuid()))
        store = budget.Budget(self.database)
        settled = store.reserve(os.getuid(), 'old-run', vector(20, 200, 30), 'settled')
        meter = store.meter(os.getuid(), settled['id'], vector(5, 100, 10), 'a' * 64)
        store.settle(os.getuid(), settled['id'], meter)
        self.hold = store.reserve(os.getuid(), 'old-run', vector(7, 700, 70), 'uncertain')
        # A trusted meter without settlement still retains its entire maximum.
        store.meter(os.getuid(), self.hold['id'], vector(1, 1, 1), 'b' * 64)
        store.halt()
        store.db.execute('CREATE TABLE store_identity(campaign TEXT,store_id TEXT,prior_history_receipt TEXT)')
        store.db.execute('INSERT INTO store_identity VALUES(?,?,?)',
                         (registration.CAMPAIGN, registration.STORE, registration.PRIOR))
        store.db.close()
        info = self.database.stat()
        self.binding = {'version': 1, 'campaign': registration.CAMPAIGN, 'store_id': registration.STORE,
                        'prior_history_receipt': registration.PRIOR, 'profiles': registration.LEGACY,
                        'directory': str(self.directory), 'device': info.st_dev, 'inode': info.st_ino}
        self.active = self.base / 'active.json'
        self.active.write_bytes(registration.canonical(self.binding))
        self.active.chmod(0o444)
        lock = self.base / 'launch.lock'
        lock.write_bytes(b'')
        lock.chmod(0o444)
        self.bootstrap = self.root / 'bootstrap'
        self.bootstrap.mkdir()
        self.installer = self.bootstrap / 'register-independent-replay'
        self.installer.write_bytes((ROOT / 'research/accounting_registration.py').read_bytes())
        self.installer.chmod(0o444)
        original_metadata = registration.metadata
        # Unit-only ownership translation; actual modes/inodes/ACL checks still run.
        def metadata(path, uid, gid, mode, directory=False):
            return original_metadata(path, os.getuid(), os.getgid(), mode, directory)
        for name, value in {
            'BASE': self.base, 'BOOTSTRAP': self.installer, 'LOCKS': (lock,),
            'ACTIVE_SHA256': registration.sha(self.active.read_bytes()),
            'DATABASE_SHA256': registration.sha(self.database.read_bytes()),
            'IDENTITY': {'device': info.st_dev, 'active_inode': self.active.stat().st_ino,
                         'directory_inode': self.directory.stat().st_ino, 'database_inode': info.st_ino},
            'metadata': metadata, 'bootstrap': lambda: None, 'protected': lambda *a, **k: None,
            'idle': lambda: None,
        }.items():
            self.stack.enter_context(patch.object(registration, name, value))
        self.stack.enter_context(patch.object(registration.os, 'chown', lambda *a: None))
        self.stack.enter_context(patch.object(registration.os, 'fchown', lambda *a: None))
        original_replace = os.replace
        def root_replace(source, target):
            # Simulate root's permission to unlink within its read-only directory.
            mode = source.parent.stat().st_mode & 0o777
            source.parent.chmod(0o755)
            try:
                original_replace(source, target)
            finally:
                source.parent.chmod(mode)
        self.stack.enter_context(patch.object(registration.os, 'replace', root_replace))
        self.before = self.database.read_bytes()
        self.before_inode = self.database.stat().st_ino
        self.old_raw = self.active.read_bytes()
        self.baseline = registration.baseline()

    def plan(self):
        installer_hash = registration.sha(self.installer.read_bytes())
        review = {'decision': 'approved-registration-only', 'installer_sha256': installer_hash,
                  'baseline_sha256': registration.sha(registration.canonical(self.baseline)),
                  'ceilings': registration.CEILINGS, 'stage': 'poc',
                  'stop_release': False, 'execution_authorized': False}
        review_raw = registration.canonical(review)
        review_hash = registration.sha(review_raw)
        review_path = self.bootstrap / ('registration-review-' + review_hash + '.json')
        if not review_path.exists():
            review_path.write_bytes(review_raw)
            review_path.chmod(0o444)
        return {'version': 1, 'baseline': self.baseline, 'installer_sha256': installer_hash,
                'review_sha256': review_hash, 'ceilings': copy.deepcopy(registration.CEILINGS),
                'profiles': registration.PROFILES, 'stage': 'poc', 'stop_release': False,
                'execution_authorized': False, 'exclusive_parent': True}

    def install(self, plan=None):
        raw = registration.canonical(plan if plan is not None else self.plan())
        path = self.bootstrap / 'plan.json'
        if path.exists():
            path.chmod(0o644)
        path.write_bytes(raw)
        path.chmod(0o444)
        digest = registration.sha(raw)
        return registration.install(path, digest, 'REGISTER_STOPPED_INDEPENDENT_REPLAY:' + digest)

    def test_registration_preserves_every_database_byte_and_hold(self):
        result = self.install()
        self.assertTrue(result['registered'])
        self.assertTrue(result['stopped'])
        self.assertFalse(result['execution_authorized'])
        after = registration.verify()
        self.assertEqual(after['binding']['profiles'], registration.PROFILES)
        self.assertEqual(self.database.read_bytes(), self.before)
        self.assertEqual(self.database.stat().st_ino, self.before_inode)
        self.assertEqual((self.base / 'registration/prior-active.json').read_bytes(), self.old_raw)
        self.assertEqual(after['receipt']['baseline'], self.baseline)
        self.assertEqual(self.baseline['inventory']['pending'], 1)
        self.assertEqual(self.baseline['inventory']['known_encumbered'],
                         {'poc': [12, 800, 80], 'milestone': [12, 800, 80]})
        self.assertIsNone(self.baseline['inventory']['spendable'])

    def test_legacy_denies_replay_new_binding_opens_same_stopped_store(self):
        with patch.object(persistent_budget, 'ACTIVE', self.active), \
             patch.object(persistent_budget, 'immutable', lambda *a, **k: None), \
             patch.object(persistent_budget, 'record', lambda p: registration.decode(p.read_bytes())):
            with self.assertRaises(Failure):
                persistent_budget.PersistentBudget('independent-replay')
            legacy = persistent_budget.PersistentBudget('offline')
            legacy.db.close()
            self.install()
            replay = persistent_budget.PersistentBudget('independent-replay')
            try:
                self.assertEqual(replay.path, self.database)
                self.assertTrue(replay.totals(os.getuid())['stopped'])
                with self.assertRaises(Failure):
                    replay.reserve(os.getuid(), 'replay', vector(), 'new-replay')
                with self.assertRaisesRegex(Failure, 'POC-only'):
                    replay.reserve(os.getuid(), 'replay', vector(), 'new-replay', 'milestone')
            finally:
                replay.db.close()
        self.assertEqual(self.database.read_bytes(), self.before)

    def persistent_context(self):
        context = ExitStack()
        context.enter_context(patch.object(persistent_budget, 'ACTIVE', self.active))
        context.enter_context(patch.object(persistent_budget, 'immutable', lambda *a, **k: None))
        context.enter_context(patch.object(persistent_budget, 'record', lambda p: registration.decode(p.read_bytes())))
        return context

    def assert_frozen_mutators(self, store):
        with closing(sqlite3.connect(self.database)) as db:
            receipt = db.execute('SELECT id FROM metering WHERE reservation=?', (self.hold['id'],)).fetchone()[0]
        before = self.database.read_bytes()
        inode = self.database.stat().st_ino
        totals = store.totals(os.getuid())
        operations = (
            lambda: store.settle(os.getuid(), self.hold['id'], dict(reservation=self.hold['id'], receipt=receipt)),
            lambda: store.meter(os.getuid(), self.hold['id'], vector(1, 1, 1), 'b' * 64),
            lambda: store.disclose_overhead(os.getuid(), 'preparation', 5, 'overhead'),
            lambda: store.halt(),
            lambda: store.reserve(os.getuid(), 'old-run', vector(), 'uncertain'),
            lambda: budget.Budget.settle(store, os.getuid(), self.hold['id'],
                                        dict(reservation=self.hold['id'], receipt=receipt)),
            lambda: budget.Budget.meter(store, os.getuid(), self.hold['id'], vector(1, 1, 1), 'b' * 64),
            lambda: budget.Budget.disclose_overhead(store, os.getuid(), 'preparation', 5, 'overhead'),
            lambda: budget.Budget.reserve(store, os.getuid(), 'old-run', vector(), 'uncertain'),
            lambda: budget.Budget.halt(store),
        )
        for index, operation in enumerate(operations):
            with self.subTest(operation=index), self.assertRaises(Failure):
                operation()
            self.assertEqual(self.database.read_bytes(), before)
            self.assertEqual(self.database.stat().st_ino, inode)
            self.assertEqual(store.totals(os.getuid()), totals)
            self.assertEqual(totals['pending'], 1)
        with self.assertRaises(sqlite3.DatabaseError):
            store.db.execute('UPDATE state SET stopped=1 WHERE id=1')
        sql = 'UPDATE reservations SET actual=maximum WHERE actual IS NULL'
        cursor = getattr(store, 'prepublication_cursor', store.db.cursor())
        for entry in (lambda: store.db.execute(sql), lambda: store.db.executemany(sql, [()]),
                      lambda: store.db.executescript(sql), lambda: cursor.execute(sql),
                      lambda: cursor.executemany(sql, [()]), lambda: cursor.executescript(sql)):
            with self.assertRaises(sqlite3.DatabaseError):
                entry()
            self.assertEqual(store.totals(os.getuid()), totals)
        self.assertEqual(self.database.read_bytes(), before)

    def test_all_registered_profiles_freeze_every_mutator_and_base_entrypoint(self):
        self.install()
        with self.persistent_context():
            for profile in registration.PROFILES:
                with self.subTest(profile=profile):
                    store = persistent_budget.PersistentBudget(profile)
                    try:
                        self.assert_frozen_mutators(store)
                        with self.assertRaises(sqlite3.DatabaseError):
                            store.db.execute('PRAGMA user_version=7')
                    finally:
                        store.db.close()
        self.assertEqual(self.database.read_bytes(), self.before)
        self.assertEqual(self.database.stat().st_ino, self.before_inode)

    def test_stale_legacy_handles_and_reused_sql_refuse_after_registration(self):
        with self.persistent_context():
            handles = [persistent_budget.PersistentBudget(profile) for profile in registration.LEGACY]
            try:
                # Prepare/execute the identical SQL before publication. Cached
                # statements must not bypass the authorizer after publication.
                for store in handles:
                    store.prepublication_cursor = store.db.cursor()
                    store.db.execute('UPDATE state SET stopped=1 WHERE id=1')
                self.assertEqual(self.database.read_bytes(), self.before)
                self.install()
                for store in handles:
                    self.assert_frozen_mutators(store)
            finally:
                for store in handles:
                    store.db.close()

    def test_partial_registration_freezes_stale_legacy_mutators(self):
        with self.persistent_context():
            store = persistent_budget.PersistentBudget('offline')
            try:
                (self.base / 'registration').mkdir()
                self.assert_frozen_mutators(store)
            finally:
                store.db.close()

    def test_legacy_stopped_settlement_meter_and_overhead_still_work(self):
        with self.persistent_context():
            store = persistent_budget.PersistentBudget('offline')
            try:
                receipt = store.meter(os.getuid(), self.hold['id'], vector(1, 1, 1), 'b' * 64)
                store.settle(os.getuid(), self.hold['id'], receipt)
                store.disclose_overhead(os.getuid(), 'preparation', 5, 'overhead')
                store.disclose_overhead(os.getuid(), 'preparation', 5, 'overhead')
                store.halt()
                totals = store.totals(os.getuid())
                self.assertEqual(totals['pending'], 0)
                self.assertEqual(totals['overhead_us'], {'preparation': 5})
                self.assertTrue(totals['stopped'])
            finally:
                store.db.close()

    def test_partial_publication_blocks_legacy_and_retry_without_database_writes(self):
        with patch.object(registration.os, 'replace', side_effect=OSError('injected before commit')):
            with self.assertRaisesRegex(OSError, 'injected'):
                self.install()
        self.assertEqual(self.active.read_bytes(), self.old_raw)
        self.assertEqual(self.database.read_bytes(), self.before)
        with self.assertRaises(Failure):
            persistent_budget.validate_store(self.binding, self.database)
        with self.assertRaisesRegex(ValueError, 'partial'):
            self.install()

    def test_failure_during_receipt_write_is_partial_and_preserves_database(self):
        original = registration.exclusive
        def fail_receipt(path, raw):
            if path.name == 'receipt.json':
                raise OSError('injected receipt write failure')
            original(path, raw)
        with patch.object(registration, 'exclusive', fail_receipt):
            with self.assertRaisesRegex(OSError, 'injected'):
                self.install()
        self.assertEqual(self.active.read_bytes(), self.old_raw)
        self.assertEqual(self.database.read_bytes(), self.before)
        with self.assertRaises(ValueError):
            registration.baseline()

    def test_failure_after_atomic_publication_retains_stopped_verified_state(self):
        original = registration.sync_directory
        def fail_final_sync(path):
            if self.active.read_bytes() != self.old_raw:
                raise OSError('injected postcommit fsync failure')
            original(path)
        with patch.object(registration, 'sync_directory', fail_final_sync):
            with self.assertRaisesRegex(OSError, 'injected'):
                self.install()
        self.assertEqual(registration.verify()['receipt']['baseline'], self.baseline)
        self.assertEqual(self.database.read_bytes(), self.before)
        with self.assertRaises(ValueError):
            self.install()

    def test_busy_lock_prevents_any_output(self):
        with patch.object(registration.fcntl, 'flock', side_effect=BlockingIOError('busy')):
            with self.assertRaises(BlockingIOError):
                self.install()
        self.assertFalse((self.base / 'registration').exists())
        self.assertEqual(self.database.read_bytes(), self.before)

    def test_reinstall_refused_preserving_all_bytes(self):
        self.install()
        raw = self.active.read_bytes()
        with self.assertRaises(ValueError):
            self.install()
        self.assertEqual(self.active.read_bytes(), raw)
        self.assertEqual(self.database.read_bytes(), self.before)

    def test_bad_authority_and_ceiling_change_refused_before_writes(self):
        for field, value in [('stop_release', True), ('execution_authorized', True),
                             ('exclusive_parent', False), ('stage', 'milestone'), ('version', True),
                             ('profiles', registration.LEGACY), ('installer_sha256', 'a' * 64)]:
            plan = self.plan()
            plan[field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                self.install(plan)
            self.assertFalse((self.base / 'registration').exists())
        plan = self.plan()
        plan['ceilings']['poc'][0] += 1
        with self.assertRaises(ValueError):
            self.install(plan)
        self.assertEqual(self.database.read_bytes(), self.before)

    def test_changed_baseline_or_missing_review_refused(self):
        plan = self.plan()
        plan['baseline'] = copy.deepcopy(self.baseline)
        plan['baseline']['inventory']['pending'] = 0
        with self.assertRaises(ValueError):
            self.install(plan)
        plan = self.plan()
        plan['review_sha256'] = 'a' * 64
        with self.assertRaises(OSError):
            self.install(plan)
        self.assertFalse((self.base / 'registration').exists())

    def test_tamper_missing_receipt_and_stop_recovery_refused(self):
        self.install()
        receipt_path = self.base / 'registration/receipt.json'
        raw = receipt_path.read_bytes()
        receipt_path.chmod(0o644)
        receipt_path.write_bytes(raw + b'\n')
        receipt_path.chmod(0o444)
        with self.assertRaises(ValueError):
            registration.verify()
        receipt_path.chmod(0o644)
        receipt_path.write_bytes(raw)
        receipt_path.chmod(0o444)
        with closing(sqlite3.connect(self.database)) as db:
            db.execute('UPDATE state SET stopped=0')
            db.commit()
        with self.assertRaisesRegex(ValueError, 'stopped'):
            registration.verify()

    def test_missing_receipt_and_extra_output_refused(self):
        self.install()
        directory = self.base / 'registration'
        directory.chmod(0o755)
        (directory / 'receipt.json').rename(directory / 'unrecognized')
        directory.chmod(0o555)
        with self.assertRaisesRegex(ValueError, 'partial'):
            registration.verify()

    def test_vector_and_orphan_meter_refused_without_repair(self):
        for value in [dict(vector(), money_cents=True), dict(vector(), currency='EUR'),
                      dict(vector(), execution_us=-1), dict(vector(), extra=0)]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                registration.resource(value)
        with closing(sqlite3.connect(self.database)) as db:
            db.execute('UPDATE metering SET reservation=? WHERE reservation=?', ('unknown', self.hold['id']))
            db.commit()
        raw = self.database.read_bytes()
        with self.assertRaisesRegex(ValueError, 'orphan'):
            registration.inventory(self.database, self.binding)
        self.assertEqual(self.database.read_bytes(), raw)

    def test_inventory_cumulative_ceiling_refusal(self):
        with closing(sqlite3.connect(self.database)) as db:
            maximum = vector(5000)
            request = dict(run='old-run', maximum=maximum, stage='poc', binding=None)
            db.execute('UPDATE reservations SET maximum=?,binding=? WHERE id=?',
                       (registration.canonical(maximum), registration.canonical(request), self.hold['id']))
            db.execute('DELETE FROM metering WHERE reservation=?', (self.hold['id'],))
            db.commit()
        with self.assertRaisesRegex(ValueError, 'ceiling'):
            registration.inventory(self.database, self.binding)

    def test_unknown_sidecar_and_inode_replacement_refused(self):
        sidecar = Path(str(self.database) + '-wal')
        sidecar.write_bytes(b'partial')
        with self.assertRaises(ValueError):
            registration.baseline()
        sidecar.unlink()
        replacement = self.directory / 'replacement'
        replacement.write_bytes(self.before)
        replacement.chmod(0o600)
        replacement.replace(self.database)
        with self.assertRaisesRegex(ValueError, 'inode'):
            registration.baseline()

    def test_unknown_history_orphan_and_over_ceiling_refused(self):
        with closing(sqlite3.connect(self.database)) as db:
            db.execute('UPDATE reservations SET actual=? WHERE id=?',
                       (registration.canonical(vector()), self.hold['id']))
            db.commit()
        with self.assertRaisesRegex(ValueError, 'unbound settlement'):
            registration.inventory(self.database, self.binding)

    def test_profile_validation_and_duplicate_json(self):
        for replacement in [True, 2, 0]:
            value = dict(self.binding, version=replacement)
            with self.assertRaises(ValueError):
                registration.validate_binding(value)
        for profiles in [registration.PROFILES, [], registration.LEGACY[::-1], registration.LEGACY * 2]:
            with self.assertRaises(ValueError):
                registration.validate_binding(dict(self.binding, profiles=profiles))
        with self.assertRaisesRegex(ValueError, 'duplicate'):
            registration.decode(b'{"x":1,"x":2}')


class ReserveGuards(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.directory = Path(self.folder.name).resolve()
        self.directory.chmod(0o700)
        self.patch = patch.object(budget, 'EVALUATOR', os.getuid())
        self.patch.start()
        self.addCleanup(self.patch.stop)
        self.store = budget.Budget(self.directory / 'budget.sqlite')
        self.addCleanup(lambda: self.store.db.close())

    def test_stopped_duplicate_zero_changed_duplicate_and_reopen_refuse(self):
        self.store.reserve(os.getuid(), 'run', vector(), 'key')
        self.store.halt()
        for key, maximum in [('key', vector()), ('key', vector(1)), ('new', vector())]:
            with self.assertRaisesRegex(Failure, 'stopped'):
                self.store.reserve(os.getuid(), 'run', maximum, key)
        reopened = budget.Budget(self.store.path, existing=True)
        try:
            with self.assertRaisesRegex(Failure, 'stopped'):
                reopened.reserve(os.getuid(), 'run', vector(), 'key')
        finally:
            reopened.db.close()

    def test_each_dimension_exact_ceiling_and_one_over(self):
        for dimension, maximum in enumerate(registration.CEILINGS['poc']):
            with self.subTest(dimension=dimension):
                self.store.db.execute('DELETE FROM reservations')
                values = [0, 0, 0]
                values[dimension] = maximum
                self.store.reserve(os.getuid(), 'run', vector(*values), 'full')
                values[dimension] = 1
                with self.assertRaisesRegex(Failure, 'ceiling'):
                    self.store.reserve(os.getuid(), 'run', vector(*values), 'over')

    def test_milestone_includes_poc(self):
        self.store.reserve(os.getuid(), 'run', vector(5000), 'poc')
        self.store.reserve(os.getuid(), 'run', vector(10000), 'milestone', 'milestone')
        with self.assertRaisesRegex(Failure, 'ceiling'):
            self.store.reserve(os.getuid(), 'run', vector(1), 'over', 'milestone')

    def test_nonroot_checkout_bootstrap_has_no_effects(self):
        result = subprocess.run([sys.executable, '-I', '-S', '-B',
                                 str(ROOT / 'research/accounting_registration.py'), 'install',
                                 '/does-not-exist', 'a' * 64, 'unapproved'],
                                capture_output=True, text=True, timeout=5)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('root-only', result.stdout)


class BootstrapBoundaries(unittest.TestCase):
    def test_wrong_bootstrap_refuses_even_with_simulated_root_identity(self):
        with patch.object(registration.os, 'getuid', return_value=0), \
             patch.object(registration.os, 'geteuid', return_value=0):
            with self.assertRaisesRegex(ValueError, 'isolated canonical'):
                registration.bootstrap()

    def test_real_file_acl_mode_link_and_size_refusals(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder).resolve()
            path = root / 'record'
            path.write_bytes(b'{}')
            path.chmod(0o444)
            self.assertEqual(registration.read(path), b'{}')
            registration.metadata(path, os.getuid(), os.getgid(), 0o444)
            with self.assertRaises(ValueError):
                registration.metadata(path, os.getuid() + 1, os.getgid(), 0o444)
            with self.assertRaises(ValueError):
                registration.metadata(path, os.getuid(), os.getgid(), 0o600)
            with self.assertRaises(ValueError):
                registration.read(path, 1)
            link = root / 'link'
            link.symlink_to(path)
            with self.assertRaises(OSError):
                registration.read(link)
            os.link(path, root / 'hardlink')
            with self.assertRaises(ValueError):
                registration.read(path)
            (root / 'hardlink').unlink()
            subprocess.run(['/bin/chmod', '+a', 'everyone allow read', str(path)], check=True)
            try:
                with self.assertRaisesRegex(ValueError, 'ACL'):
                    registration.metadata(path, os.getuid(), os.getgid(), 0o444)
            finally:
                subprocess.run(['/bin/chmod', '-N', str(path)], check=True)

    def test_idle_refuses_service_processes_qemu_and_malformed_snapshot(self):
        for output in (b'', b'320 1 /usr/bin/python3\n', b'321 2 /usr/bin/python3\n',
                       b'501 3 /path/qemu-system-aarch64\n', b'bad snapshot\n'):
            completed = subprocess.CompletedProcess([], 0, stdout=output)
            with patch.object(registration.subprocess, 'run', return_value=completed):
                with self.subTest(output=output), self.assertRaises(ValueError):
                    registration.idle()
        completed = subprocess.CompletedProcess([], 0, stdout=b'501 1 /usr/bin/python3\n')
        with patch.object(registration.subprocess, 'run', return_value=completed):
            registration.idle()


if __name__ == '__main__':
    unittest.main()
