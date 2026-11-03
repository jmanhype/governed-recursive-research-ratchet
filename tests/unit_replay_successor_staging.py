"""Unit tests for the Stage T protected-staging record formats."""

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "research"))

from replay_successor_staging import (
    ACTION,
    AUTHORITY_FLAGS,
    PRINCIPAL,
    SOURCE_ROLE_SHA256,
    STAGE_S_PACKAGE_SHA256,
    STAGE_S_RECORD_SHA256,
    BASE_COMMIT,
    StagingValidationError,
    authorization_digest,
    build_authorization_template,
    build_staging_outcome,
    check_no_symlink_ancestors,
    validate_authorization,
    validate_staging_outcome,
)


def _filled_authorization():
    template = build_authorization_template()
    template["authorization_hash"] = "a" * 64
    template["authorized_by"] = "operator-speed"
    template["authorized_at"] = "2026-11-03T16:00:00Z"
    return template


def _staged_files():
    return [
        {
            "role": role,
            "sha256": SOURCE_ROLE_SHA256[role],
            "destination": f"/Library/GRRR/bootstrap/test-{role}",
            "bytes": 100 + i,
        }
        for i, role in enumerate(sorted(SOURCE_ROLE_SHA256))
    ]


class ReplaySuccessorStaging(unittest.TestCase):
    def test_valid_authorization_passes(self):
        auth = _filled_authorization()
        validated = validate_authorization(copy.deepcopy(auth))
        self.assertEqual(validated, auth)

    def test_template_has_null_authorization(self):
        template = build_authorization_template()
        self.assertIsNone(template["authorization_hash"])
        self.assertIsNone(template["authorized_by"])
        self.assertIsNone(template["authorized_at"])
        self.assertTrue(template["authority"]["protected_staging"])
        self.assertFalse(template["authority"]["protected_installation"])

    def test_authorization_binds_stage_s(self):
        auth = _filled_authorization()
        self.assertEqual(auth["stage_s_record_sha256"], STAGE_S_RECORD_SHA256)
        self.assertEqual(auth["stage_s_package_sha256"], STAGE_S_PACKAGE_SHA256)
        self.assertEqual(auth["base_commit"], BASE_COMMIT)

    def test_authorization_staging_only_not_installation(self):
        auth = _filled_authorization()
        self.assertTrue(auth["authority"]["protected_staging"])
        self.assertFalse(auth["authority"]["protected_installation"])

    def test_authorization_scope_covers_all_eight_roles(self):
        auth = _filled_authorization()
        self.assertEqual(len(auth["authorization_scope"]["roles"]), 8)
        self.assertEqual(
            auth["authorization_scope"]["source_sha256"],
            SOURCE_ROLE_SHA256,
        )

    def test_authorization_digest_is_deterministic(self):
        auth = _filled_authorization()
        self.assertEqual(authorization_digest(auth), authorization_digest(auth))
        other = _filled_authorization()
        other["authorized_at"] = "2026-11-03T17:00:00Z"
        self.assertNotEqual(authorization_digest(auth), authorization_digest(other))

    def test_staging_outcome_valid(self):
        auth = _filled_authorization()
        staged = _staged_files()
        outcome = build_staging_outcome(auth, staged, "/Library/GRRR/bootstrap")
        validated = validate_staging_outcome(copy.deepcopy(outcome))
        self.assertEqual(validated, outcome)
        self.assertEqual(outcome["outcome"], "staged-not-installed")

    def test_staging_outcome_binds_authorization(self):
        auth = _filled_authorization()
        staged = _staged_files()
        outcome = build_staging_outcome(auth, staged, "/Library/GRRR/bootstrap")
        self.assertEqual(
            outcome["authorization_sha256"],
            authorization_digest(auth),
        )

    def test_empty_authority_rejects(self):
        bad = _filled_authorization()
        bad["authority"] = {}
        with self.assertRaises(StagingValidationError):
            validate_authorization(bad)

    def test_missing_authority_flag_rejects(self):
        bad = _filled_authorization()
        del bad["authority"]["protected_installation"]
        with self.assertRaises(StagingValidationError):
            validate_authorization(bad)

    def test_installation_true_rejects(self):
        bad = _filled_authorization()
        bad["authority"]["protected_installation"] = True
        with self.assertRaises(StagingValidationError):
            validate_authorization(bad)

    def test_staging_false_rejects(self):
        bad = _filled_authorization()
        bad["authority"]["protected_staging"] = False
        with self.assertRaises(StagingValidationError):
            validate_authorization(bad)

    def test_null_authorization_hash_rejects(self):
        bad = _filled_authorization()
        bad["authorization_hash"] = None
        with self.assertRaises(StagingValidationError):
            validate_authorization(bad)

    def test_zero_authorization_hash_rejects(self):
        bad = _filled_authorization()
        bad["authorization_hash"] = "0" * 64
        with self.assertRaises(StagingValidationError):
            validate_authorization(bad)

    def test_empty_operator_name_rejects(self):
        bad = _filled_authorization()
        bad["authorized_by"] = ""
        with self.assertRaises(StagingValidationError):
            validate_authorization(bad)

    def test_invalid_timestamp_rejects(self):
        bad = _filled_authorization()
        bad["authorized_at"] = "not-a-timestamp"
        with self.assertRaises(StagingValidationError):
            validate_authorization(bad)

    def test_wrong_stage_s_hash_rejects(self):
        bad = _filled_authorization()
        bad["stage_s_record_sha256"] = "0" * 64
        with self.assertRaises(StagingValidationError):
            validate_authorization(bad)

    def test_wrong_base_commit_rejects(self):
        bad = _filled_authorization()
        bad["base_commit"] = "0" * 40
        with self.assertRaises(StagingValidationError):
            validate_authorization(bad)

    def test_extra_scope_field_rejects(self):
        bad = _filled_authorization()
        bad["authorization_scope"]["unexpected"] = True
        with self.assertRaises(StagingValidationError):
            validate_authorization(bad)

    def test_wrong_staging_root_rejects(self):
        bad = _filled_authorization()
        bad["authorization_scope"]["staging_root"] = "/tmp/evil"
        with self.assertRaises(StagingValidationError):
            validate_authorization(bad)

    def test_outcome_missing_file_rejects(self):
        auth = _filled_authorization()
        staged = _staged_files()[:7]
        with self.assertRaises(StagingValidationError):
            build_staging_outcome(auth, staged, "/Library/GRRR/bootstrap")

    def test_outcome_duplicate_role_rejects(self):
        auth = _filled_authorization()
        staged = _staged_files()
        staged[1] = copy.deepcopy(staged[0])
        with self.assertRaises(StagingValidationError):
            build_staging_outcome(auth, staged, "/Library/GRRR/bootstrap")

    def test_outcome_wrong_hash_rejects(self):
        auth = _filled_authorization()
        staged = _staged_files()
        staged[0]["sha256"] = "0" * 64
        with self.assertRaises(StagingValidationError):
            build_staging_outcome(auth, staged, "/Library/GRRR/bootstrap")

    def test_outcome_wrong_root_rejects(self):
        auth = _filled_authorization()
        staged = _staged_files()
        with self.assertRaises(StagingValidationError):
            build_staging_outcome(auth, staged, "/tmp/evil")

    def test_outcome_installed_rejects(self):
        auth = _filled_authorization()
        staged = _staged_files()
        outcome = build_staging_outcome(auth, staged, "/Library/GRRR/bootstrap")
        bad = copy.deepcopy(outcome)
        bad["outcome"] = "installed"
        with self.assertRaises(StagingValidationError):
            validate_staging_outcome(bad)

    def test_records_json_serializable(self):
        auth = _filled_authorization()
        staged = _staged_files()
        outcome = build_staging_outcome(auth, staged, "/Library/GRRR/bootstrap")
        raw_auth = json.dumps(auth, sort_keys=True)
        raw_out = json.dumps(outcome, sort_keys=True)
        self.assertIsInstance(raw_auth, str)
        self.assertIsInstance(raw_out, str)

    def test_symlink_ancestor_rejects(self):
        import tempfile
        import os
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            real = tmp_path / "real"
            real.mkdir()
            nested = real / "nested"
            nested.mkdir()
            link = tmp_path / "link"
            os.symlink(str(real), str(link))
            target = link / "nested" / "bootstrap"
            with self.assertRaises(StagingValidationError):
                check_no_symlink_ancestors(target)

    def test_no_symlink_ancestor_accepts(self):
        with tempfile.TemporaryDirectory() as tmp:
            # Use resolved /private path to avoid macOS /var symlink
            resolved = Path(tmp).resolve()
            target = resolved / "a" / "b" / "c"
            check_no_symlink_ancestors(target)

    def test_outcome_all_zero_auth_digest_rejects(self):
        auth = _filled_authorization()
        staged = _staged_files()
        outcome = build_staging_outcome(auth, staged, "/Library/GRRR/bootstrap")
        bad = copy.deepcopy(outcome)
        bad["authorization_sha256"] = "0" * 64
        with self.assertRaises(StagingValidationError):
            validate_staging_outcome(bad)

    def test_outcome_boolean_bytes_rejects(self):
        auth = _filled_authorization()
        staged = _staged_files()
        outcome = build_staging_outcome(auth, staged, "/Library/GRRR/bootstrap")
        bad = copy.deepcopy(outcome)
        bad["staged_files"][0]["bytes"] = True
        with self.assertRaises(StagingValidationError):
            validate_staging_outcome(bad)

    def test_outside_destination_rejects(self):
        auth = _filled_authorization()
        staged = _staged_files()
        outcome = build_staging_outcome(auth, staged, "/Library/GRRR/bootstrap")
        bad = copy.deepcopy(outcome)
        bad["staged_files"][0]["destination"] = "/tmp/elsewhere"
        with self.assertRaises(StagingValidationError):
            validate_staging_outcome(bad)

    def test_traversal_destination_rejects(self):
        auth = _filled_authorization()
        staged = _staged_files()
        outcome = build_staging_outcome(auth, staged, "/Library/GRRR/bootstrap")
        bad = copy.deepcopy(outcome)
        bad["staged_files"][0]["destination"] = (
            "/Library/GRRR/bootstrap/../../../tmp/elsewhere"
        )
        with self.assertRaises(StagingValidationError):
            validate_staging_outcome(bad)

    def test_unnormalized_destination_rejects(self):
        auth = _filled_authorization()
        staged = _staged_files()
        outcome = build_staging_outcome(auth, staged, "/Library/GRRR/bootstrap")
        bad = copy.deepcopy(outcome)
        bad["staged_files"][0]["destination"] = (
            "/Library/GRRR/bootstrap//file.py"
        )
        with self.assertRaises(StagingValidationError):
            validate_staging_outcome(bad)

    def test_subdirectory_destination_rejects(self):
        auth = _filled_authorization()
        staged = _staged_files()
        outcome = build_staging_outcome(auth, staged, "/Library/GRRR/bootstrap")
        bad = copy.deepcopy(outcome)
        bad["staged_files"][0]["destination"] = (
            "/Library/GRRR/bootstrap/sub/file.py"
        )
        with self.assertRaises(StagingValidationError):
            validate_staging_outcome(bad)

    def test_relative_path_symlink_check_rejects(self):
        with self.assertRaises(StagingValidationError):
            check_no_symlink_ancestors(Path("relative/path"))


if __name__ == "__main__":
    unittest.main()
