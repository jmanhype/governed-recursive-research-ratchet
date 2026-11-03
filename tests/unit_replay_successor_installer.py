"""Stopped v4 replay-successor sandbox installer tests."""

from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from contextlib import closing
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "research"))

import replay_successor_installer as installer_module  # noqa: E402
from replay_successor_installer import (  # noqa: E402
    AUTHORIZATION_FIELDS, BASIS, BINDING_FIELDS, CANONICAL_PYTHON_SHA256,
    INSTALLER_ACTION, INSTALLER_ENTRYPOINT, PLAN_FIELDS, PROFILE,
    PROTECTED_ROOT,
    PYTHON_ENTRYPOINT, RECEIPT_FIELDS, REVIEW_FIELDS, SOURCE_ROLES,
    SUCCESSOR_STORE_ID, TARGET_DIRECTORY, candidate_authorization,
    candidate_plan, candidate_review, live_install, preflight,
    sandbox_install, source_inventory, validate_authorization, validate_plan,
    validate_review, validate_source_inventory, verify_sandbox_store,
    verify_source_files, _safe_sandbox_path,
)
from replay_successor_installer_contract import SOURCE_ARTIFACTS  # noqa: E402
from replay_successor_contract import candidate_receipt  # noqa: E402
from spendability_stage_c import StageCError, digest  # noqa: E402


IDENTITY = {
    "uid": 0,
    "euid": 0,
    "interpreter": PYTHON_ENTRYPOINT,
    "entrypoint": INSTALLER_ENTRYPOINT,
    "isolated": True,
    "no_site": True,
    "no_bytecode": True,
}


class ReplaySuccessorInstaller(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.root = Path(self.folder.name).resolve()
        self.source_root = self.root / "source"
        self.target_root = self.root / "target"
        self.source_root.mkdir(mode=0o700)
        self.target_root.mkdir(mode=0o700)
        self.predecessor = self.target_root / "predecessor-sentinel.json"
        self.predecessor.write_bytes(b"predecessor remains unchanged\n")
        self.raw_sources = {
            role: ("sandbox-source:" + role + "\n").encode("ascii")
            for role in SOURCE_ROLES
        }
        for role, raw in self.raw_sources.items():
            path = self.source_root / Path(SOURCE_ARTIFACTS[role]).name
            path.write_bytes(raw)
            path.chmod(0o400)
        self.inventory = source_inventory(self.raw_sources)
        self.plan = candidate_plan(self.inventory)
        self.review = candidate_review(self.plan)
        self.authorization = candidate_authorization(self.plan, self.review)
        self.authorization_hash = digest(self.authorization)

    def tearDown(self):
        self.folder.cleanup()

    def install(self):
        return sandbox_install(
            self.source_root, self.target_root, self.root, self.plan,
            self.review, self.authorization, self.authorization_hash, IDENTITY,
        )

    def target(self):
        return self.target_root / SUCCESSOR_STORE_ID

    def test_exact_eight_role_source_inventory(self):
        self.assertEqual(set(self.inventory), set(SOURCE_ROLES))
        self.assertEqual(len(set(self.inventory.values())), len(SOURCE_ROLES))
        for role, expected in self.inventory.items():
            self.assertEqual(expected,
                             sha256(self.raw_sources[role]).hexdigest())

    def test_source_files_validate_without_protected_access(self):
        verify_source_files(self.source_root, self.root, self.inventory)
        self.assertTrue(self.source_root.is_relative_to(self.root))

    def test_candidate_plan_binds_exact_basis_and_sandbox_only(self):
        self.assertEqual(set(self.plan), set(PLAN_FIELDS))
        self.assertEqual(self.plan["basis"], BASIS)
        self.assertEqual(self.plan["action"], INSTALLER_ACTION)
        self.assertEqual(self.plan["target_directory"], TARGET_DIRECTORY)
        self.assertEqual(self.plan["installer_sha256"],
                         self.inventory["installer-entrypoint"])
        self.assertEqual(self.plan["interpreter_sha256"],
                         CANONICAL_PYTHON_SHA256)
        self.assertIs(self.plan["sandbox_only"], True)
        self.assertIs(self.plan["budget_amendment_required"], True)
        self.assertIs(self.plan["budget_amendment_authorized"], False)
        self.assertIs(self.plan["execution_authorized"], False)

    def test_plan_revalidates_by_exact_candidate(self):
        self.assertEqual(validate_plan(self.plan), self.plan)

    def test_candidate_review_binds_plan_and_remains_powerless(self):
        self.assertEqual(set(self.review), set(REVIEW_FIELDS))
        self.assertEqual(self.review["plan_sha256"], digest(self.plan))
        self.assertEqual(self.review["source_inventory"], self.inventory)
        self.assertEqual(self.review["decision"],
                         "approved-sandbox-installer-core-only")
        self.assertIs(self.review["sandbox_only"], True)
        self.assertIs(self.review["execution_authorized"], False)
        self.assertIs(self.review["budget_amendment_authorized"], False)
        self.assertIs(self.review["reconciliation_authorized"], False)
        self.assertIs(self.review["replay_authorized"], False)

    def test_review_revalidates_by_exact_candidate(self):
        self.assertEqual(validate_review(self.review, self.plan), self.review)

    def test_candidate_authorization_binds_exact_receipts(self):
        self.assertEqual(set(self.authorization), set(AUTHORIZATION_FIELDS))
        self.assertEqual(self.authorization["installer_sha256"],
                         self.plan["installer_sha256"])
        self.assertEqual(self.authorization["plan_sha256"], digest(self.plan))
        self.assertEqual(self.authorization["review_sha256"], digest(self.review))
        self.assertIs(self.authorization["protected_installation_requested"], True)
        self.assertIs(self.authorization["exclusive_parent"], True)
        self.assertIs(self.authorization["budget_amendment_authorized"], False)
        self.assertIs(self.authorization["reconciliation_authorized"], False)
        self.assertIs(self.authorization["replay_authorized"], False)
        self.assertIs(self.authorization["execution_authorized"], False)

    def test_external_authorization_hash_is_required(self):
        result = validate_authorization(
            self.authorization, self.plan, self.review, self.authorization_hash)
        self.assertTrue(result)
        with self.assertRaises(StageCError) as raised:
            validate_authorization(
                self.authorization, self.plan, self.review, "0" * 64)
        self.assertEqual(str(raised.exception),
                         "replay_successor_installer: external authorization hash differs")

    def test_preflight_accepts_exact_synthetic_root_identity(self):
        preflight(
            self.source_root, self.target_root, self.root, self.plan, self.review,
            self.authorization, self.authorization_hash, IDENTITY,
        )
        self.assertFalse(self.target().exists())

    def test_protected_paths_reject_before_any_metadata_syscall(self):
        metadata_calls = []
        original_stat = installer_module.os.stat
        original_lstat = installer_module.os.lstat

        def guarded_stat(path, *args, **kwargs):
            value = os.fspath(path)
            metadata_calls.append(value)
            if (value.startswith("//") or value == "/Library"
                    or value.startswith("/Library/")):
                raise AssertionError("protected metadata access attempted")
            return original_stat(path, *args, **kwargs)

        def guarded_lstat(path, *args, **kwargs):
            value = os.fspath(path)
            metadata_calls.append(value)
            if (value.startswith("//") or value == "/Library"
                    or value.startswith("/Library/")):
                raise AssertionError("protected metadata access attempted")
            return original_lstat(path, *args, **kwargs)

        cases = (
            (PROTECTED_ROOT / "accounting-poc2", Path("/Library")),
            (PROTECTED_ROOT, Path("/Library")),
            (PROTECTED_ROOT / "x" / "y", PROTECTED_ROOT),
            (Path("//Library/GRRR/x"), Path("//Library")),
            (Path("/Library/unrelated/x"), Path("/Library/unrelated")),
            (Path("/Library/unrelated"), Path("/Library/unrelated")),
        )
        with mock.patch.object(installer_module.os, "stat", guarded_stat), \
                mock.patch.object(installer_module.os, "lstat", guarded_lstat):
            for candidate_path, candidate_root in cases:
                with self.subTest(path=candidate_path, root=candidate_root):
                    with self.assertRaises(StageCError) as raised:
                        _safe_sandbox_path(
                            candidate_path, candidate_root,
                            exists=False, directory=True)
                    self.assertIn("sandbox", str(raised.exception))
        self.assertEqual(metadata_calls, [])

    def test_explicit_dotdot_and_absolute_escape_reject_before_metadata(self):
        metadata_calls = []

        def refuse_metadata(path, *args, **kwargs):
            metadata_calls.append(os.fspath(path))
            raise AssertionError("lexical rejection must precede metadata")

        cases = (
            (self.root / "safe" / ".." / "outside", self.root),
            (self.root.parent / "outside", self.root),
        )
        with mock.patch.object(installer_module.os, "stat", refuse_metadata), \
                mock.patch.object(installer_module.os, "lstat", refuse_metadata):
            for candidate_path, candidate_root in cases:
                with self.subTest(path=candidate_path):
                    with self.assertRaises(StageCError) as raised:
                        _safe_sandbox_path(
                            candidate_path, candidate_root,
                            exists=False, directory=True)
                    self.assertIn("sandbox path", str(raised.exception))
        self.assertEqual(metadata_calls, [])

    def test_preflight_rejects_protected_target_without_source_access(self):
        with mock.patch.object(installer_module, "verify_source_files") as source_check:
            with self.assertRaises(StageCError) as raised:
                preflight(
                    self.source_root,
                    PROTECTED_ROOT / "accounting-poc2",
                    Path("/Library"),
                    self.plan, self.review, self.authorization,
                    self.authorization_hash, IDENTITY,
                )
        self.assertIn("protected GRRR path is outside the sandbox",
                      str(raised.exception))
        source_check.assert_not_called()

    def test_sandbox_root_beneath_symlinked_ancestor_is_rejected(self):
        outside = self.root / "real-outside-root"
        outside.mkdir()
        linked_root = self.root / "linked-root"
        linked_root.symlink_to(outside, target_is_directory=True)
        with self.assertRaises(StageCError) as raised:
            _safe_sandbox_path(
                linked_root, linked_root, exists=True, directory=True)
        self.assertIn("sandbox root ancestor is not a real directory",
                      str(raised.exception))

    def test_symlinked_sandbox_component_is_rejected(self):
        outside = self.root.parent / ("outside-" + self.root.name)
        outside.mkdir()
        self.addCleanup(outside.rmdir)
        linked_source = self.root / "linked-source"
        linked_source.symlink_to(outside, target_is_directory=True)
        with self.assertRaises(StageCError) as raised:
            preflight(
                linked_source, self.target_root, self.root, self.plan,
                self.review, self.authorization, self.authorization_hash,
                IDENTITY,
            )
        self.assertIn("sandbox directory differs", str(raised.exception))

    def test_modified_source_bytes_are_rejected_before_target_creation(self):
        path = self.source_root / Path(
            SOURCE_ARTIFACTS["atomic-publisher"]).name
        path.chmod(0o600)
        path.write_bytes(self.raw_sources["atomic-publisher"] + b"tampered\n")
        path.chmod(0o400)
        with self.assertRaises(StageCError) as raised:
            self.install()
        self.assertIn("sandbox source bytes differ", str(raised.exception))
        self.assertFalse(self.target().exists())

    def test_missing_extra_or_duplicate_source_roles_rejected(self):
        value = dict(self.inventory)
        del value["postflight-verifier"]
        with self.assertRaises(StageCError):
            validate_source_inventory(value)
        value = dict(self.inventory)
        value["unreviewed"] = "0" * 64
        with self.assertRaises(StageCError):
            validate_source_inventory(value)
        value = dict(self.inventory)
        value["protected-preflight"] = value["atomic-publisher"]
        with self.assertRaises(StageCError):
            validate_source_inventory(value)

    def test_boolean_and_float_plan_versions_rejected(self):
        for malformed in (True, 1.0):
            with self.subTest(malformed=malformed):
                value = deepcopy(self.plan)
                value["schema_version"] = malformed
                with self.assertRaises(StageCError):
                    validate_plan(value)

    def test_boolean_and_float_review_versions_rejected(self):
        for malformed in (True, 1.0):
            with self.subTest(malformed=malformed):
                value = deepcopy(self.review)
                value["schema_version"] = malformed
                with self.assertRaises(StageCError):
                    validate_review(value, self.plan)

    def test_plan_target_or_basis_tampering_rejected(self):
        changes = (
            ("target_directory", "/tmp/unapproved"),
            ("installer_sha256", "0" * 64),
            ("budget_amendment_authorized", True),
            ("execution_authorized", True),
            ("install_once", False),
            ("predecessor_mutations", ["reset"]),
        )
        for field, replacement in changes:
            with self.subTest(field=field):
                value = deepcopy(self.plan)
                value[field] = replacement
                with self.assertRaises(StageCError):
                    validate_plan(value)
        value = deepcopy(self.plan)
        value["basis"]["stage_o_package_sha256"] = "0" * 64
        with self.assertRaises(StageCError):
            validate_plan(value)

    def test_review_authority_or_receipt_tampering_rejected(self):
        changes = (
            ("execution_authorized", True),
            ("budget_amendment_authorized", True),
            ("reconciliation_authorized", True),
            ("replay_authorized", True),
            ("plan_sha256", "0" * 64),
        )
        for field, replacement in changes:
            with self.subTest(field=field):
                value = deepcopy(self.review)
                value[field] = replacement
                with self.assertRaises(StageCError):
                    validate_review(value, self.plan)

    def test_authority_tampering_rejected(self):
        changes = (
            ("budget_amendment_authorized", True),
            ("reconciliation_authorized", True),
            ("replay_authorized", True),
            ("execution_authorized", True),
            ("exclusive_parent", False),
        )
        for field, replacement in changes:
            with self.subTest(field=field):
                value = deepcopy(self.authorization)
                value[field] = replacement
                with self.assertRaises(StageCError):
                    validate_authorization(
                        value, self.plan, self.review, digest(value))

    def test_non_root_or_wrong_toolchain_identity_rejected(self):
        changes = (
            ("uid", 501), ("euid", 501),
            ("interpreter", "/usr/bin/python3"),
            ("entrypoint", "/tmp/unissued"), ("isolated", False),
            ("no_site", False), ("no_bytecode", False),
        )
        for field, replacement in changes:
            with self.subTest(field=field):
                identity = dict(IDENTITY, **{field: replacement})
                with self.assertRaises(StageCError):
                    preflight(
                        self.source_root, self.target_root, self.root, self.plan,
                        self.review, self.authorization,
                        self.authorization_hash, identity,
                    )
                self.assertFalse(self.target().exists())

    def test_successful_install_creates_stopped_empty_v4_store(self):
        receipt = self.install()
        self.assertEqual(set(receipt), set(RECEIPT_FIELDS))
        self.assertEqual(receipt["outcome"], "sandbox-installed-stopped")
        self.assertIs(receipt["stopped"], True)
        self.assertIs(receipt["sandbox_only"], True)
        self.assertIs(receipt["execution_authorized"], False)
        self.assertIs(receipt["budget_amendment_authorized"], False)
        self.assertIs(receipt["reconciliation_authorized"], False)
        self.assertIs(receipt["replay_authorized"], False)
        self.assertEqual(receipt["allowed_mutations"], [])
        verified = verify_sandbox_store(self.target(), receipt, self.root)
        self.assertEqual(verified["receipt"], receipt)

    def test_successful_binding_and_database_identity_are_exact(self):
        self.install()
        binding = json.loads((self.target() / "active.json").read_text())
        self.assertEqual(set(binding), set(BINDING_FIELDS))
        self.assertEqual(binding["version"], 4)
        self.assertEqual(binding["store_id"], SUCCESSOR_STORE_ID)
        self.assertEqual(binding["directory"], str(self.target()))
        self.assertEqual(binding["profiles"], [PROFILE])
        self.assertEqual(binding["allowed_mutation_profiles"], [PROFILE])
        self.assertEqual(binding["successor_sha256"], digest(candidate_receipt()))
        self.assertIs(binding["execution_authorized"], False)
        self.assertIs(binding["budget_amendment_required"], True)
        self.assertIs(binding["sandbox_only"], True)
        info = (self.target() / "budget.sqlite").stat()
        self.assertEqual((binding["device"], binding["inode"]),
                         (info.st_dev, info.st_ino))

    def test_store_metadata_is_private_and_files_are_read_only(self):
        self.install()
        database = self.target() / "budget.sqlite"
        active = self.target() / "active.json"
        receipt = self.target() / "receipt.json"
        self.assertEqual(stat_mode(self.target()), 0o700)
        self.assertEqual(stat_mode(database), 0o600)
        self.assertEqual(stat_mode(active), 0o400)
        self.assertEqual(stat_mode(receipt), 0o400)

    def test_predecessor_and_sources_remain_unchanged(self):
        before_predecessor = self.predecessor.read_bytes()
        before_sources = {
            path.name: path.read_bytes() for path in self.source_root.iterdir()
        }
        self.install()
        self.assertEqual(self.predecessor.read_bytes(), before_predecessor)
        self.assertEqual({
            path.name: path.read_bytes() for path in self.source_root.iterdir()
        }, before_sources)

    def test_existing_or_partial_target_refuses_without_reset(self):
        self.install()
        receipt_before = (self.target() / "receipt.json").read_bytes()
        with self.assertRaises(StageCError) as raised:
            self.install()
        self.assertIn("existing/partial successor state", str(raised.exception))
        self.assertEqual((self.target() / "receipt.json").read_bytes(),
                         receipt_before)

    def test_injected_failure_preserves_uncertain_evidence(self):
        with mock.patch("replay_successor_installer._create_database",
                        side_effect=OSError("injected database failure")):
            with self.assertRaises(OSError):
                self.install()
        uncertain = self.target() / "uncertain.json"
        self.assertTrue(uncertain.exists())
        record = json.loads(uncertain.read_text())
        self.assertEqual(record["outcome"], "uncertain-no-retry")
        self.assertEqual(record["authorization_sha256"], self.authorization_hash)
        self.assertIs(record["execution_authorized"], False)
        self.assertIs(record["budget_amendment_authorized"], False)
        self.assertIs(record["replay_authorized"], False)
        self.assertEqual(record["allowed_mutations"], [])
        self.assertFalse((self.target() / "receipt.json").exists())

    def test_failure_at_each_publication_step_makes_uncertainty_dominate(self):
        original_write = installer_module._write_exclusive
        original_sync = installer_module._sync_directory

        def fail_receipt(path, raw, mode):
            if path.name == "receipt.json":
                raise OSError("injected receipt failure")
            return original_write(path, raw, mode)

        def fail_active(path, raw, mode):
            if path.name == "active.json":
                raise OSError("injected active failure")
            return original_write(path, raw, mode)

        def fail_sync(path):
            if path.name == SUCCESSOR_STORE_ID:
                raise OSError("injected directory sync failure")
            return original_sync(path)

        failures = (
            lambda: mock.patch.object(installer_module, "_write_exclusive", fail_receipt),
            lambda: mock.patch.object(installer_module, "_write_exclusive", fail_active),
            lambda: mock.patch.object(installer_module, "_sync_directory", fail_sync),
            lambda: mock.patch.object(
                installer_module, "verify_sandbox_store",
                side_effect=OSError("injected postflight failure")),
        )
        for make_patch in failures:
            with self.subTest(make_patch=make_patch), make_patch():
                with self.assertRaises(OSError):
                    self.install()
                self.assertTrue((self.target() / "uncertain.json").exists())
                with self.assertRaises(StageCError) as raised:
                    verify_sandbox_store(
                        self.target(), {"schema_version": 1}, self.root)
                self.assertEqual(str(raised.exception),
                                 "replay_successor_installer: sandbox outcome is uncertain and cannot verify as success")
            shutil.rmtree(self.target())

    def test_unexpected_database_object_is_rejected_and_becomes_uncertain(self):
        original_create = installer_module._create_database

        def create_with_extra(path):
            identity = original_create(path)
            with closing(sqlite3.connect(path)) as db:
                db.execute("CREATE TABLE unexpected(value TEXT)")
                db.commit()
            return identity

        with mock.patch.object(installer_module, "_create_database",
                               create_with_extra):
            with self.assertRaises(StageCError) as raised:
                self.install()
        self.assertIn("sandbox database object inventory differs",
                      str(raised.exception))
        self.assertTrue((self.target() / "uncertain.json").exists())
        with self.assertRaises(StageCError) as verify_error:
            verify_sandbox_store(self.target(), {"schema_version": 1}, self.root)
        self.assertIn("sandbox outcome is uncertain", str(verify_error.exception))

    def test_tampered_active_binding_fails_postflight(self):
        receipt = self.install()
        active = self.target() / "active.json"
        active.chmod(0o600)
        value = json.loads(active.read_text())
        value["execution_authorized"] = True
        active.write_text(json.dumps(value, sort_keys=True,
                                     separators=(",", ":")) + "\n")
        active.chmod(0o400)
        with self.assertRaises(StageCError):
            verify_sandbox_store(self.target(), receipt, self.root)

    def test_tampered_database_fails_postflight(self):
        receipt = self.install()
        database = self.target() / "budget.sqlite"
        database.chmod(0o600)
        with closing(sqlite3.connect(database)) as db:
            db.execute("INSERT INTO overhead VALUES('tamper','selector',1)")
            db.commit()
        database.chmod(0o600)
        with self.assertRaises(StageCError):
            verify_sandbox_store(self.target(), receipt, self.root)

    def test_sandbox_install_remains_below_temporary_roots(self):
        self.install()
        self.assertTrue(self.target().is_relative_to(self.target_root))
        self.assertTrue(self.target_root.is_relative_to(self.root))
        self.assertNotIn("/Library/GRRR", str(self.target()))

    def test_live_install_function_refuses(self):
        with self.assertRaises(StageCError) as raised:
            live_install("anything")
        self.assertEqual(str(raised.exception),
                         "replay_successor_installer: protected v4 installer source is not issued")
        self.assertFalse(self.target().exists())

    def test_checkout_cli_refuses_wrong_grammar(self):
        script = ROOT / "scripts/install-replay-successor-v4"
        result = subprocess.run(
            [sys.executable, "-I", "-B", str(script), "unexpected"],
            text=True, capture_output=True,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("install PLAN REVIEW AUTHORIZATION SHA256", result.stderr)
        self.assertFalse(self.target().exists())

    def test_checkout_cli_refuses_even_with_exact_grammar(self):
        script = ROOT / "scripts/install-replay-successor-v4"
        result = subprocess.run(
            [sys.executable, "-I", "-B", str(script), "install",
             "PLAN", "REVIEW", "AUTHORIZATION", "SHA256"],
            text=True, capture_output=True,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("root-only isolated canonical v4 installer required",
                      result.stderr)
        self.assertFalse(self.target().exists())

    def test_database_schema_and_empty_tables_are_exact(self):
        self.install()
        database = self.target() / "budget.sqlite"
        with closing(sqlite3.connect(database.as_uri() + "?mode=ro", uri=True)) as db:
            tables = {row[0] for row in db.execute(
                "SELECT name FROM sqlite_master WHERE type='table'")}
            self.assertEqual(tables, {
                "reservations", "metering", "overhead", "state",
                "store_identity",
            })
            self.assertEqual(db.execute("SELECT id,stopped FROM state").fetchall(),
                             [(1, 1)])
            for table in ("reservations", "metering", "overhead"):
                self.assertEqual(db.execute("SELECT * FROM " + table).fetchall(), [])


def stat_mode(path: Path) -> int:
    return path.stat().st_mode & 0o777


if __name__ == "__main__":
    unittest.main()
