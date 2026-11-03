"""Exact v4 source issuance package and sandbox role tests."""

from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import importlib.util
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = ROOT / "docs/evidence/replay-authority/stage-r/source"
sys.path.insert(0, str(ROOT / "research"))
sys.path.insert(0, str(SOURCE_ROOT))

from replay_successor_installer_contract import SOURCE_ARTIFACTS, SOURCE_ROLES
from replay_successor_source_issuance import (  # noqa: E402
    BASE_COMMIT, DESTINATIONS, PREPARED_AT, ROLE_FILES, ROLE_ORDER,
    STAGE_P_PACKAGE_SHA256, STAGE_Q_PACKAGE_SHA256,
    build_source_bundle, validate_source_bundle, verify_source_files,
)
from spendability_stage_c import StageCError, digest  # noqa: E402


SCRIPT = ROOT / "scripts/prepare-replay-successor-v4-source-issuance"


def load_source(name: str):
    path = SOURCE_ROOT / name
    spec = importlib.util.spec_from_file_location(name.removesuffix(".py"), path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ReplaySuccessorSourceIssuance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bundle = build_source_bundle(ROOT)

    def role_record(self, role):
        return next(item for item in self.bundle["sources"] if item["role"] == role)

    def test_exact_eight_role_closure_and_destinations(self):
        self.assertEqual(tuple(ROLE_FILES) == ROLE_ORDER, True)
        self.assertEqual(ROLE_ORDER, SOURCE_ROLES)
        self.assertEqual(DESTINATIONS, dict(SOURCE_ARTIFACTS))
        self.assertEqual([item["role"] for item in self.bundle["sources"]],
                         list(SOURCE_ROLES))
        for item in self.bundle["sources"]:
            self.assertEqual(item["protected_destination"],
                             DESTINATIONS[item["role"]])

    def test_exact_committed_basis_and_preparation_status(self):
        self.assertEqual(self.bundle["basis"], {
            "story_head": BASE_COMMIT,
            "stage_p_package_sha256": STAGE_P_PACKAGE_SHA256,
            "stage_q_package_sha256": STAGE_Q_PACKAGE_SHA256,
        })
        self.assertEqual(self.bundle["decision"], "prepared-not-issued")
        self.assertEqual(self.bundle["issuance_status"], "prepared-not-issued")
        self.assertEqual(self.bundle["prepared_at"], PREPARED_AT)
        self.assertFalse(self.bundle["outcome"]["issued"])
        self.assertFalse(self.bundle["outcome"]["installation_ready"])
        self.assertEqual(self.bundle["outcome"]["allowed_mutations"], [])
        self.assertFalse(any(self.bundle["authority"].values()))

    def test_all_source_hashes_are_exact_and_distinct(self):
        records = self.bundle["sources"]
        self.assertEqual(len(records), 8)
        hashes = [item["sha256"] for item in records]
        self.assertEqual(len(set(hashes)), 8)
        for item in records:
            raw = (SOURCE_ROOT / item["file"]).read_bytes()
            self.assertEqual(len(raw), item["bytes"])
            self.assertEqual(sha256(raw).hexdigest(), item["sha256"])

    def test_bundle_hashes_exact_role_identity_map(self):
        expected = digest({
            item["role"]: item["sha256"] for item in self.bundle["sources"]
        })
        self.assertEqual(self.bundle["source_bundle_sha256"], expected)
        result = verify_source_files(ROOT)
        self.assertEqual(result, {
            "members": 8,
            "source_bundle_sha256": expected,
            "distinct_hashes": 8,
            "protected_access": False,
        })

    def test_bundle_revalidates_by_exact_regeneration(self):
        validate_source_bundle(self.bundle, ROOT)
        value = deepcopy(self.bundle)
        value["outcome"]["issued"] = True
        with self.assertRaises(StageCError):
            validate_source_bundle(value, ROOT)

    def test_builder_uses_no_protected_metadata_or_read(self):
        original_stat = os.stat
        original_lstat = os.lstat

        def guarded_stat(path, *args, **kwargs):
            value = os.fspath(path)
            if value.startswith("/Library"):
                raise AssertionError("protected metadata access")
            return original_stat(path, *args, **kwargs)

        def guarded_lstat(path, *args, **kwargs):
            value = os.fspath(path)
            if value.startswith("/Library"):
                raise AssertionError("protected metadata access")
            return original_lstat(path, *args, **kwargs)

        with mock.patch.object(os, "stat", guarded_stat), \
                mock.patch.object(os, "lstat", guarded_lstat):
            value = build_source_bundle(ROOT)
            validate_source_bundle(value, ROOT)
        self.assertFalse(any(value["authority"].values()))

    def test_modified_missing_or_extra_source_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            stage_r = root / "docs/evidence/replay-authority/stage-r"
            shutil.copytree(SOURCE_ROOT, stage_r / "source")
            build_source_bundle(root)

            target = stage_r / "source" / ROLE_FILES["stage-n-contract"]
            target.write_bytes(target.read_bytes() + b"\n# tampered\n")
            with self.assertRaises(StageCError) as raised:
                build_source_bundle(root)
            self.assertIn("Stage R source bytes differ", str(raised.exception))

            (stage_r / "source" / ROLE_FILES["failure-preservation"]).unlink()
            with self.assertRaises(StageCError):
                build_source_bundle(root)

    def test_role_marker_tampering_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            stage_r = root / "docs/evidence/replay-authority/stage-r"
            shutil.copytree(SOURCE_ROOT, stage_r / "source")
            path = stage_r / "source" / ROLE_FILES["protected-preflight"]
            raw = path.read_bytes().replace(
                b"protected path is outside the sandbox",
                b"protected path might be inside the sandbox",
            )
            path.write_bytes(raw)
            with self.assertRaises(StageCError) as raised:
                build_source_bundle(root)
            self.assertIn("Stage R role marker differs", str(raised.exception))

    def test_emitter_is_deterministic_and_refuses_arguments(self):
        first = subprocess.run(
            [sys.executable, "-I", "-B", str(SCRIPT)],
            check=True, text=True, capture_output=True).stdout
        second = subprocess.run(
            [sys.executable, "-I", "-B", str(SCRIPT)],
            check=True, text=True, capture_output=True).stdout
        self.assertEqual(first, second)
        value = json.loads(first)
        validate_source_bundle(value, ROOT)
        refused = subprocess.run(
            [sys.executable, "-I", "-B", str(SCRIPT), "unexpected"],
            text=True, capture_output=True)
        self.assertNotEqual(refused.returncode, 0)
        self.assertIn("no arguments accepted", refused.stderr)

    def test_installer_entrypoint_script_refuses_exact_grammar(self):
        script = SOURCE_ROOT / "install-replay-successor-v4"
        result = subprocess.run(
            [sys.executable, "-I", "-B", str(script), "install",
             "PLAN", "REVIEW", "AUTHORIZATION", "SHA256"],
            text=True, capture_output=True,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("root-only isolated canonical v4 installer required",
                      result.stderr)

    def test_stage_n_contract_role_is_exact(self):
        module = load_source(ROLE_FILES["stage-n-contract"])
        value = module.contract()
        module.validate(value)
        self.assertIsNone(value["predecessor"]["spendable"])
        self.assertEqual(value["predecessor"]["history_status"], "unresolved")
        self.assertTrue(value["predecessor"]["all_original_ceilings_encumbered"])
        self.assertEqual(value["unresolved_holds"], list(module.HOLD_IDS))
        self.assertEqual(len(value["unresolved_holds"]), 3)
        self.assertEqual(module.canonical(value).decode("ascii"), json.dumps(
            value, sort_keys=True, separators=(",", ":")
        ))
        value["authority"] = True
        with self.assertRaises(ValueError):
            module.validate(value)

    def test_stage_o_adapter_role_remains_unissued(self):
        module = load_source(ROLE_FILES["stage-o-runtime-adapter"])
        status = module.adapter_status()
        self.assertEqual(status["implementation_status"],
                         "source-prepared-unissued")
        self.assertEqual(status["gates"]["replay_execution"], "blocked")
        self.assertIs(status["execution_authorized"], False)
        observation = module.candidate_observation()
        observation["installed"] = True
        with self.assertRaises(ValueError):
            module.adapter_status(observation)

    def test_preflight_role_rejects_protected_paths_before_metadata(self):
        module = load_source(ROLE_FILES["protected-preflight"])
        calls = []
        original_stat = os.stat
        original_lstat = os.lstat

        def guarded_stat(path, *args, **kwargs):
            calls.append(os.fspath(path))
            if os.fspath(path).startswith("/Library"):
                raise AssertionError("protected metadata access")
            return original_stat(path, *args, **kwargs)

        def guarded_lstat(path, *args, **kwargs):
            calls.append(os.fspath(path))
            if os.fspath(path).startswith("/Library"):
                raise AssertionError("protected metadata access")
            return original_lstat(path, *args, **kwargs)

        cases = (
            (Path("/Library/GRRR/x"), Path("/Library")),
            (Path("//Library/x"), Path("//Library")),
            (Path("/Library/unrelated/x"), Path("/Library/unrelated")),
            (Path("/safe/../outside"), Path("/safe")),
            (Path("/outside"), Path("/safe")),
        )
        with mock.patch.object(os, "stat", guarded_stat), \
                mock.patch.object(os, "lstat", guarded_lstat):
            for path, sandbox in cases:
                with self.subTest(path=path):
                    with self.assertRaises(ValueError):
                        module.safe_sandbox_path(
                            path, sandbox, exists=False, directory=True)
        self.assertEqual(calls, [])

    def test_preflight_rejects_absent_target_symlink_and_wrong_root_type(self):
        module = load_source(ROLE_FILES["protected-preflight"])
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder).resolve()
            missing = root / "genuinely-absent-target"
            self.assertFalse(missing.exists())
            module.safe_sandbox_path(
                missing, root, exists=False, directory=True)
            module.safe_sandbox_path(
                missing, root, exists=False, directory=False)

            outside = root.parent / (root.name + "-outside")
            outside.mkdir()
            self.addCleanup(outside.rmdir)
            linked_target = root / "target"
            linked_target.symlink_to(outside, target_is_directory=True)
            with self.assertRaises(ValueError) as raised:
                module.safe_sandbox_path(
                    linked_target, root, exists=False, directory=True)
            self.assertIn("sandbox symlink is forbidden", str(raised.exception))
            with self.assertRaises(ValueError) as root_error:
                module.safe_sandbox_path(
                    root, root, exists=True, directory=False)
            self.assertIn("sandbox root cannot be a file target",
                          str(root_error.exception))
            with self.assertRaises(ValueError) as absent_root_error:
                module.safe_sandbox_path(
                    root, root, exists=False, directory=True)
            self.assertIn("sandbox root cannot be an absent target",
                          str(absent_root_error.exception))

    def test_preflight_rejects_dangling_final_symlink_when_target_absent(self):
        module = load_source(ROLE_FILES["protected-preflight"])
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder).resolve()
            dangling = root / "dangling-target"
            dangling.symlink_to(root / "does-not-exist")
            with self.assertRaises(ValueError) as raised:
                module.safe_sandbox_path(
                    dangling, root, exists=False, directory=True)
            self.assertIn("sandbox symlink is forbidden", str(raised.exception))

    def test_schema_publisher_postflight_and_failure_roles_function(self):
        schema = load_source(ROLE_FILES["v4-store-schema"])
        postflight = load_source(ROLE_FILES["postflight-verifier"])
        publisher = load_source(ROLE_FILES["atomic-publisher"])
        failure = load_source(ROLE_FILES["failure-preservation"])
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            store = root / "store"
            identity = schema.create_store(store / "budget.sqlite")
            database_hash = sha256((store / "budget.sqlite").read_bytes()).hexdigest()
            result = postflight.verify(
                store / "budget.sqlite", database_hash,
                (identity["device"], identity["inode"]))
            self.assertEqual(result, {"stopped": True, "empty": True,
                                      "verified": True})

            publication = root / "publication"
            publication.mkdir(mode=0o700)
            publisher.publish_pair(
                publication, "receipt", b'{"receipt":true}', "active",
                b'{"active":true}')
            self.assertEqual((publication / "receipt").read_bytes(),
                             b'{"receipt":true}')
            self.assertEqual((publication / "active").read_bytes(),
                             b'{"active":true}')

            uncertain = root / "uncertain"
            record = failure.preserve(uncertain, "0" * 64, "unit failure")
            self.assertEqual(record["outcome"], "uncertain-no-retry")
            self.assertFalse(record["execution_authorized"])

            db = sqlite3.connect(store / "budget.sqlite")
            try:
                db.execute("CREATE TABLE unexpected(value TEXT)")
                db.commit()
            finally:
                db.close()
            with self.assertRaises(ValueError):
                postflight.verify(store / "budget.sqlite", database_hash, identity)


if __name__ == "__main__":
    unittest.main()
