"""Focused no-guest successor-accounting installation contracts."""
import hashlib
import importlib.machinery
import importlib.util
import json
import os
from pathlib import Path
import sqlite3
import stat
import subprocess
import sys
import tempfile
import unittest
from contextlib import closing
from unittest.mock import patch
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'research'))
import budget
from common import Failure, canonical, digest
import persistent_budget

OLD_RECEIPT = '9f64395bec815a6bb2281d3b5d96d2356899138b1929b0a9881c16483c486dde'
OLD_ACTIVE_SHA256 = 'cc45b70fed84bae583959379559e8fc8336a0da3b4bca1750fc20c2848619f1b'


def load_installer(root, source):
    installed = root / 'provision-successor-accounting'
    installed.write_bytes(source.read_bytes())
    installed.chmod(0o444)
    loader = importlib.machinery.SourceFileLoader('successor_accounting', str(installed))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module, installed


class SuccessorAccounting(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory(prefix='.tmp-successor-', dir=ROOT)
        self.addCleanup(self.folder.cleanup)
        self.root = Path(self.folder.name).absolute()
        self.root.chmod(0o755)
        self.install_count = 0
        self.module, installed = load_installer(self.root, ROOT / 'scripts/provision-successor-accounting')
        self.production_values = {
            'PROTECTED_UID': self.module.PROTECTED_UID,
            'PROTECTED_GID': self.module.PROTECTED_GID,
            'EVALUATOR_UID': self.module.EVALUATOR_UID,
            'EVALUATOR_GID': self.module.EVALUATOR_GID,
            'OLD_ACTIVE': self.module.OLD_ACTIVE,
            'OLD_ACTIVE_SHA256': self.module.OLD_ACTIVE_SHA256,
        }
        self.old_root = self.root / 'old'
        self.old_root.mkdir(mode=0o700)
        self.old_raw = canonical({
            'schema': 'conservative-genesis', 'campaign': 'a' * 64, 'store_id': 'b' * 64,
            'database_sha256': 'c' * 64, 'device': 16777229, 'execution_gate': 'blocked',
            'inode': 681781547, 'plan_sha256': 'd' * 64,
            'receipt_sha256': OLD_RECEIPT, 'stopped': 1, 'unresolved_history': True})
        self.old_active = self.old_root / 'active.json'
        self.old_active.write_bytes(self.old_raw)
        self.old_active.chmod(0o444)
        self.old_before = (self.old_raw, self.old_active.stat())
        self.base = self.root / 'accounting-poc2'
        values = {
            'BASE': self.base, 'OLD_ACTIVE': self.old_active, 'BOOTSTRAP': installed,
            'PYTHON': Path(sys.executable), 'PYTHON_SHA256': digest(Path(sys.executable).read_bytes()),
            'OLD_ACTIVE_SHA256': digest(self.old_raw),
            'PROTECTED_UID': os.getuid(), 'PROTECTED_GID': os.getgid(),
            'EVALUATOR_UID': os.getuid(), 'EVALUATOR_GID': os.getgid(),
            'protected': lambda path, directory=False, readonly=True: None,
            'sys': SimpleNamespace(executable=sys.executable, version_info=(3, 9, 6),
                                   dont_write_bytecode=True,
                                   flags=SimpleNamespace(isolated=True, no_site=True,
                                                         dont_write_bytecode=True)),
        }
        self.patches = [patch.object(self.module, key, value) for key, value in values.items()]
        for item in self.patches:
            self.addCleanup(item.stop)
            item.start()

    def authorization(self, raw):
        expected = hashlib.sha256(raw).hexdigest()
        return expected, ('INSTALL_GRRR_POC2_SUCCESSOR_ACCOUNTING:'
                          + expected + ':' + self.module.AUTHORIZATION_REFERENCE)

    def install(self):
        plan = self.module.plan()
        raw = canonical(plan)
        expected, authorization = self.authorization(raw)
        self.install_count += 1
        path = self.root / ('plan-%d.json' % self.install_count)
        path.write_bytes(raw)
        path.chmod(0o444)
        return self.module.install(path, expected, authorization), plan

    def test_fresh_schema_identity_modes_and_empty_tables(self):
        binding, plan = self.install()
        self.assertEqual(plan['budget'], {'currency': 'USD', 'money_cents': 5000,
                                          'execution_seconds': 21600, 'review_seconds': 3600})
        self.assertEqual((self.production_values['EVALUATOR_UID'],
                          self.production_values['EVALUATOR_GID']), (320, 320))
        self.assertEqual((binding['campaign'], binding['store_id']),
                         self.module.identities(self.module.OLD_ACTIVE_SHA256,
                                                self.module.AUTHORIZATION_REFERENCE))
        self.assertEqual(binding['directory'], str(self.base / plan['store_id']))
        self.assertEqual(binding['prior_history_receipt'], OLD_RECEIPT)
        database = Path(binding['directory']) / 'budget.sqlite'
        active = self.base / 'active.json'
        launch_lock = self.base / 'launch.lock'
        self.assertEqual((active.stat().st_uid, active.stat().st_gid, stat.S_IMODE(active.stat().st_mode)),
                         (os.getuid(), os.getgid(), 0o444))
        self.assertEqual((launch_lock.stat().st_uid, launch_lock.stat().st_gid,
                          stat.S_IMODE(launch_lock.stat().st_mode)),
                         (os.getuid(), os.getgid(), 0o444))
        self.assertEqual((database.stat().st_uid, database.stat().st_gid, stat.S_IMODE(database.stat().st_mode)),
                         (os.getuid(), os.getgid(), 0o600))
        self.assertEqual((Path(binding['directory']).stat().st_uid,
                          Path(binding['directory']).stat().st_gid,
                          stat.S_IMODE(Path(binding['directory']).stat().st_mode)),
                         (os.getuid(), os.getgid(), 0o700))
        with closing(sqlite3.connect(database.as_uri() + '?mode=ro', uri=True)) as db:
            self.assertEqual(db.execute('SELECT id,stopped FROM state').fetchall(), [(1, 0)])
            self.assertEqual(db.execute('SELECT * FROM store_identity').fetchall(),
                             [(binding['campaign'], binding['store_id'], OLD_RECEIPT)])
            for table in ('reservations', 'metering', 'overhead'):
                self.assertEqual(db.execute('SELECT * FROM ' + table).fetchall(), [])

    def test_active_binding_validates_and_runtime_uses_successor(self):
        binding, _ = self.install()
        self.assertEqual((self.production_values['PROTECTED_UID'],
                          self.production_values['PROTECTED_GID']), (0, 0))
        self.assertEqual(self.production_values['OLD_ACTIVE'],
                         Path('/Library/GRRR/accounting/active.json'))
        self.assertEqual(self.production_values['OLD_ACTIVE_SHA256'], OLD_ACTIVE_SHA256)
        with patch.object(persistent_budget, 'EVALUATOR', os.getuid()):
            persistent_budget.validate_store(binding, Path(binding['directory']) / 'budget.sqlite')
        self.assertEqual(persistent_budget.ACTIVE,
                         Path('/Library/GRRR/accounting-poc2/active.json'))
        self.assertNotEqual(persistent_budget.ACTIVE, self.old_active)
        self.assertNotEqual(persistent_budget.ACTIVE, Path('/Library/GRRR/accounting/active.json'))
        self.assertIn("Path('/Library/GRRR/accounting-poc2/active.json')",
                      (ROOT / 'scripts/trusted-root-bootstrap').read_text())

    def test_old_active_bytes_and_metadata_remain_unchanged(self):
        self.install()
        self.assertEqual(self.old_active.read_bytes(), self.old_before[0])
        after = self.old_active.stat()
        self.assertEqual((after.st_uid, after.st_gid, after.st_mode, after.st_ino, after.st_mtime_ns),
                         (self.old_before[1].st_uid, self.old_before[1].st_gid,
                          self.old_before[1].st_mode, self.old_before[1].st_ino,
                          self.old_before[1].st_mtime_ns))

    def test_existing_or_partial_output_is_refused_without_reset(self):
        binding, _ = self.install()
        active = self.base / 'active.json'
        database = Path(binding['directory']) / 'budget.sqlite'
        before = (active.read_bytes(), database.read_bytes(), active.stat(), database.stat())
        with self.assertRaisesRegex(RuntimeError, 'existing/partial'):
            self.install()
        self.assertEqual(active.read_bytes(), before[0])
        self.assertEqual(database.read_bytes(), before[1])
        self.assertEqual((active.stat().st_ino, database.stat().st_ino), (before[2].st_ino, before[3].st_ino))

        partial = self.root / 'partial-poc2'
        partial.mkdir()
        with patch.object(self.module, 'BASE', partial):
            with self.assertRaisesRegex(RuntimeError, 'existing/partial'):
                self.install()

    def test_exact_authorization_deterministic_identity_and_unsafe_metadata(self):
        plan = self.module.plan()
        raw = canonical(plan)
        expected, _ = self.authorization(raw)
        path = self.root / 'plan.json'
        path.write_bytes(raw)
        path.chmod(0o444)
        with self.assertRaisesRegex(RuntimeError, 'authorization'):
            self.module.install(path, expected, 'INSTALL_GRRR_POC2_SUCCESSOR_ACCOUNTING:' + expected)
        self.assertFalse(self.base.exists())

        changed = dict(plan, campaign='0' * 64)
        changed_raw = canonical(changed)
        changed_expected, changed_authorization = self.authorization(changed_raw)
        changed_path = self.root / 'changed-plan.json'
        changed_path.write_bytes(changed_raw)
        changed_path.chmod(0o444)
        with self.assertRaisesRegex(RuntimeError, 'deterministic'):
            self.module.install(changed_path, changed_expected, changed_authorization)
        self.assertFalse(self.base.exists())

        metadata = type('Metadata', (), {'st_uid': os.getuid(), 'st_gid': os.getuid(),
                                          'st_mode': 0o100644})()
        with self.assertRaisesRegex(RuntimeError, 'ACL'):
            self.module.safe_metadata(metadata, b'-rw-r--r--+ 1 root root ...')

    def test_runtime_reservation_and_ceiling_rejection(self):
        binding, _ = self.install()
        maximum = {'currency': 'USD', 'money_cents': 5000,
                   'execution_us': 21600_000000, 'review_us': 3600_000000}
        with patch.object(persistent_budget, 'ACTIVE', self.base / 'active.json'), \
             patch.object(persistent_budget, 'EVALUATOR', os.getuid()), \
             patch.object(budget, 'EVALUATOR', os.getuid()), \
             patch.object(persistent_budget, 'record', lambda path: binding), \
             patch.object(persistent_budget, 'immutable', lambda path, directory=False: None):
            store = persistent_budget.PersistentBudget('trusted-observation')
            try:
                reserved = store.reserve(os.getuid(), 'successor-run', maximum, 'successor-key')
                self.assertFalse(reserved['dispatch_lease'])
                with self.assertRaises(Failure):
                    store.reserve(os.getuid(), 'over-ceiling', dict(maximum, money_cents=1),
                                  'over-ceiling-key')
            finally:
                store.db.close()

    def test_checkout_installer_refuses_nonroot_before_effects(self):
        destination = Path('/Library/GRRR/accounting-poc2')
        existed = destination.exists()
        result = subprocess.run([sys.executable, '-I', '-S', '-B',
                                 str(ROOT / 'scripts/provision-successor-accounting'), 'install',
                                 '/nonexistent/plan', '0' * 64, 'wrong'], capture_output=True,
                                text=True, timeout=5)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('root-only successor installation', result.stdout)
        self.assertEqual(destination.exists(), existed)


if __name__ == '__main__':
    unittest.main()
