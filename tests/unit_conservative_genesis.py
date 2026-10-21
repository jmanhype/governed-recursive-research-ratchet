"""Real sqlite restart/concurrency/immutability tests; no identity impersonation."""
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
import json
from pathlib import Path
import runpy
import sqlite3
import sys
import tempfile
from types import SimpleNamespace
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'research'))
from common import Failure
from persistent_budget import validate_store


class ConservativeGenesis(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.api = runpy.run_path(str(ROOT / 'scripts/conservative-genesis'))
        cls.temp = tempfile.TemporaryDirectory()
        cls.output = Path(cls.temp.name) / 'prepared'
        cls.plan = cls.api['build'](ROOT, cls.output)
        cls.path = cls.output / 'budget.sqlite'
        cls.receipt = json.loads((cls.output / 'receipt.json').read_bytes())

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_hashes_raw_evidence_and_no_fabricated_reservations(self):
        result = self.api['verify'](self.path, self.receipt)
        self.assertTrue(result['verified'])
        self.assertGreater(result['artifact_count'], 100)
        self.assertTrue(self.receipt['unresolved_history'])
        self.assertFalse(self.receipt['complete_migration'])

    def test_restart_and_simultaneous_scopes_reject_even_zero(self):
        def attempt(scope):
            profile, stage = scope
            with self.assertRaisesRegex(RuntimeError, 'stopped'):
                self.api['reserve'](self.path, profile, stage, 0)
        scopes = [(p, s) for p in self.api['PROFILES'] for s in self.api['CEILINGS']]
        for restart in range(2):
            with ThreadPoolExecutor(max_workers=6) as pool:
                list(pool.map(attempt, scopes))
        self.api['verify'](self.path, self.receipt)

    def test_sql_gate_cannot_be_cleared_or_bypassed(self):
        with closing(sqlite3.connect(self.path)) as db:
            for sql in ("INSERT INTO reservations VALUES('zero')",
                        "UPDATE state SET stopped=0", "DELETE FROM state"):
                with self.assertRaises(sqlite3.IntegrityError):
                    db.execute(sql)

    def test_all_runtime_profiles_reject_conservative_active_schema(self):
        for profile in self.api['PROFILES']:
            for stage in self.api['CEILINGS']:
                with self.subTest(profile=profile, stage=stage), self.assertRaises(Failure):
                    validate_store({'schema': 'conservative-genesis', 'stopped': 1}, self.path)

    def test_existing_preparation_refused_no_reset(self):
        before = self.path.read_bytes()
        with self.assertRaises(RuntimeError):
            self.api['build'](ROOT, self.output)
        self.assertEqual(before, self.path.read_bytes())

    def test_root_installation_refused_without_identity(self):
        with self.assertRaisesRegex(RuntimeError, 'root-only'):
            self.api['install'](self.output / 'plan.json', '0' * 64, '')

    def test_real_canonical_toolchain_reviewed_owner_write_is_allowed(self):
        self.api['verify_toolchain']()
        for path in self.api['TOOLCHAIN']:
            with self.assertRaisesRegex(RuntimeError, 'writable'):
                self.api['protected'](path)

    def test_toolchain_exception_cannot_extend_to_arbitrary_files(self):
        with self.assertRaisesRegex(RuntimeError, 'unreviewed'):
            self.api['protected'](self.output / 'receipt.json', toolchain=True)
        with self.assertRaisesRegex(RuntimeError, 'mutable'):
            self.api['protected'](self.output / 'receipt.json')
        link = self.output / 'link'
        link.symlink_to(self.api['PYTHON'])
        with self.assertRaises(RuntimeError):
            self.api['protected'](link)

    def test_metadata_negative_modes_ownership_and_acl(self):
        # Pure metadata predicate cases; real filesystem/toolchain covered above.
        for uid, gid, mode, listing in (
                (501, 0, 0o100644, b'-rw-r--r--'),
                (0, 20, 0o100644, b'-rw-r--r--'),
                (0, 0, 0o100664, b'-rw-rw-r--'),
                (0, 0, 0o100646, b'-rw-r--rw-'),
                (0, 0, 0o120777, b'lrwxrwxrwx'),
                (0, 0, 0o100644, b'-rw-r--r--+')):
            with self.subTest(uid=uid, gid=gid, mode=mode, listing=listing), self.assertRaises(RuntimeError):
                self.api['safe_metadata'](SimpleNamespace(st_uid=uid, st_gid=gid, st_mode=mode), listing)
