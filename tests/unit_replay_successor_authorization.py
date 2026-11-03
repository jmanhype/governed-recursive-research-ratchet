"""Unit tests for the Stage S authorization preparation record."""

import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "research"))

from replay_successor_authorization import (
    ACTION,
    AuthorizationPreparationError,
    DENIED_AUTHORITIES,
    INSTALL_TARGET,
    PREDECESSOR_ACTIVE_SHA256,
    PREDECESSOR_DATABASE_SHA256,
    PREDECESSOR_RECOVERY_SHA256,
    PRINCIPAL,
    ROLE_DESTINATIONS,
    SOURCE_ROLE_SHA256,
    STAGE_R_PACKAGE_SHA256,
    STAGE_R_SOURCE_BUNDLE_SHA256,
    STAGE_R_REVIEW_SHA256,
    build_record,
    build_staging_plan,
    emit_record,
    validate_record,
)


class ReplaySuccessorAuthorizationPreparation(unittest.TestCase):
    def setUp(self):
        self.record = build_record()

    def test_valid_record_passes_validation(self):
        validated = validate_record(copy.deepcopy(self.record))
        self.assertEqual(validated, self.record)

    def test_all_eight_roles_are_bound_with_exact_hashes(self):
        self.assertEqual(len(self.record["staging_plan"]), 8)
        roles = {item["role"] for item in self.record["staging_plan"]}
        self.assertEqual(roles, set(SOURCE_ROLE_SHA256))
        for item in self.record["staging_plan"]:
            role = item["role"]
            self.assertEqual(item["source_sha256"], SOURCE_ROLE_SHA256[role])
            self.assertEqual(item["protected_destination"], ROLE_DESTINATIONS[role])

    def test_all_source_hashes_are_distinct(self):
        hashes = [item["source_sha256"] for item in self.record["staging_plan"]]
        self.assertEqual(len(hashes), 8)
        self.assertEqual(len(set(hashes)), 8)

    def test_staging_plan_digest_is_correct(self):
        from replay_successor_authorization import _digest
        plan = build_staging_plan()
        self.assertEqual(self.record["staging_plan_sha256"], _digest(plan))

    def test_status_is_prepared_not_authorized(self):
        self.assertEqual(self.record["status"], "prepared-not-authorized")

    def test_operator_authorization_is_null(self):
        req = self.record["operator_authorization_requirement"]
        self.assertIsNone(req["authorization_hash"])
        self.assertIsNone(req["authorized_by"])
        self.assertIsNone(req["authorized_at"])
        self.assertEqual(req["required_before"], "protected-staging")
        self.assertTrue(req["record_immutable_after"])

    def test_all_authority_flags_are_false(self):
        authority = self.record["authority"]
        for key, flag in authority.items():
            self.assertIs(flag, False, f"authority {key} must be False")

    def test_denied_authorities_are_complete(self):
        denied = self.record["denied_authorities"]
        self.assertEqual(sorted(denied), sorted(DENIED_AUTHORITIES))

    def test_predecessor_binding_is_exact(self):
        pred = self.record["predecessor_binding"]
        self.assertEqual(pred["active_sha256"], PREDECESSOR_ACTIVE_SHA256)
        self.assertEqual(pred["database_sha256"], PREDECESSOR_DATABASE_SHA256)
        self.assertEqual(pred["recovery_sha256"], PREDECESSOR_RECOVERY_SHA256)
        self.assertEqual(pred["predecessor_mutation"], "forbidden")

    def test_action_and_principal_are_exact(self):
        self.assertEqual(self.record["action"], ACTION)
        self.assertEqual(self.record["principal"], PRINCIPAL)

    def test_installation_target_is_sibling_not_replacement(self):
        self.assertEqual(self.record["installation_target"], INSTALL_TARGET)
        self.assertNotIn("conservative", INSTALL_TARGET)
        self.assertIn("unissued-independent-replay-v4", INSTALL_TARGET)

    def test_schema_version_must_be_integer_one(self):
        bad = copy.deepcopy(self.record)
        bad["schema_version"] = True
        with self.assertRaises(AuthorizationPreparationError):
            validate_record(bad)
        bad["schema_version"] = 1.0
        with self.assertRaises(AuthorizationPreparationError):
            validate_record(bad)

    def test_missing_field_rejects(self):
        bad = copy.deepcopy(self.record)
        del bad["authority"]
        with self.assertRaises(AuthorizationPreparationError):
            validate_record(bad)

    def test_extra_field_rejects(self):
        bad = copy.deepcopy(self.record)
        bad["unexpected"] = True
        with self.assertRaises(AuthorizationPreparationError):
            validate_record(bad)

    def test_wrong_stage_r_bundle_hash_rejects(self):
        bad = copy.deepcopy(self.record)
        bad["basis"]["stage_r_source_bundle_sha256"] = "0" * 64
        with self.assertRaises(AuthorizationPreparationError):
            validate_record(bad)

    def test_wrong_stage_r_package_hash_rejects(self):
        bad = copy.deepcopy(self.record)
        bad["basis"]["stage_r_package_sha256"] = "0" * 64
        with self.assertRaises(AuthorizationPreparationError):
            validate_record(bad)

    def test_wrong_stage_r_review_hash_rejects(self):
        bad = copy.deepcopy(self.record)
        bad["basis"]["stage_r_review_sha256"] = "0" * 64
        with self.assertRaises(AuthorizationPreparationError):
            validate_record(bad)

    def test_modified_source_hash_in_plan_rejects(self):
        bad = copy.deepcopy(self.record)
        bad["staging_plan"][0]["source_sha256"] = "0" * 64
        with self.assertRaises(AuthorizationPreparationError):
            validate_record(bad)

    def test_modified_destination_in_plan_rejects(self):
        bad = copy.deepcopy(self.record)
        bad["staging_plan"][0]["protected_destination"] = "/tmp/evil"
        with self.assertRaises(AuthorizationPreparationError):
            validate_record(bad)

    def test_missing_role_in_plan_rejects(self):
        bad = copy.deepcopy(self.record)
        bad["staging_plan"] = bad["staging_plan"][:7]
        with self.assertRaises(AuthorizationPreparationError):
            validate_record(bad)

    def test_duplicate_role_rejects(self):
        bad = copy.deepcopy(self.record)
        bad["staging_plan"][1] = copy.deepcopy(bad["staging_plan"][0])
        with self.assertRaises(AuthorizationPreparationError):
            validate_record(bad)

    def test_non_null_authorization_hash_rejects(self):
        bad = copy.deepcopy(self.record)
        bad["operator_authorization_requirement"]["authorization_hash"] = "a" * 64
        with self.assertRaises(AuthorizationPreparationError):
            validate_record(bad)

    def test_any_true_authority_flag_rejects(self):
        for key in self.record["authority"]:
            bad = copy.deepcopy(self.record)
            bad["authority"][key] = True
            with self.assertRaises(AuthorizationPreparationError):
                validate_record(bad)

    def test_removed_denied_authority_rejects(self):
        bad = copy.deepcopy(self.record)
        bad["denied_authorities"] = bad["denied_authorities"][:-1]
        with self.assertRaises(AuthorizationPreparationError):
            validate_record(bad)

    def test_predecessor_mutation_allowed_rejects(self):
        bad = copy.deepcopy(self.record)
        bad["predecessor_binding"]["predecessor_mutation"] = "allowed"
        with self.assertRaises(AuthorizationPreparationError):
            validate_record(bad)

    def test_empty_authority_dict_rejects(self):
        bad = copy.deepcopy(self.record)
        bad["authority"] = {}
        with self.assertRaises(AuthorizationPreparationError):
            validate_record(bad)

    def test_missing_authority_key_rejects(self):
        for key in self.record["authority"]:
            bad = copy.deepcopy(self.record)
            del bad["authority"][key]
            with self.assertRaises(AuthorizationPreparationError):
                validate_record(bad)

    def test_extra_authority_key_rejects(self):
        bad = copy.deepcopy(self.record)
        bad["authority"]["unexpected"] = False
        with self.assertRaises(AuthorizationPreparationError):
            validate_record(bad)

    def test_missing_authorization_hash_field_rejects(self):
        bad = copy.deepcopy(self.record)
        del bad["operator_authorization_requirement"]["authorization_hash"]
        with self.assertRaises(AuthorizationPreparationError):
            validate_record(bad)

    def test_missing_authorized_by_field_rejects(self):
        bad = copy.deepcopy(self.record)
        del bad["operator_authorization_requirement"]["authorized_by"]
        with self.assertRaises(AuthorizationPreparationError):
            validate_record(bad)

    def test_extra_predecessor_field_rejects(self):
        bad = copy.deepcopy(self.record)
        bad["predecessor_binding"]["unexpected"] = True
        with self.assertRaises(AuthorizationPreparationError):
            validate_record(bad)

    def test_missing_predecessor_field_rejects(self):
        bad = copy.deepcopy(self.record)
        del bad["predecessor_binding"]["predecessor_mutation"]
        with self.assertRaises(AuthorizationPreparationError):
            validate_record(bad)

    def test_wrong_base_commit_rejects(self):
        bad = copy.deepcopy(self.record)
        bad["basis"]["base_commit"] = "0" * 40
        with self.assertRaises(AuthorizationPreparationError):
            validate_record(bad)

    def test_missing_base_commit_rejects(self):
        bad = copy.deepcopy(self.record)
        del bad["basis"]["base_commit"]
        with self.assertRaises(AuthorizationPreparationError):
            validate_record(bad)

    def test_extra_basis_field_rejects(self):
        bad = copy.deepcopy(self.record)
        bad["basis"]["unexpected"] = "x"
        with self.assertRaises(AuthorizationPreparationError):
            validate_record(bad)

    def test_extra_staging_item_field_with_recomputed_digest_rejects(self):
        from replay_successor_authorization import _digest
        bad = copy.deepcopy(self.record)
        bad["staging_plan"][0]["injected"] = "extra"
        bad["staging_plan_sha256"] = _digest(bad["staging_plan"])
        with self.assertRaises(AuthorizationPreparationError):
            validate_record(bad)

    def test_none_prepared_at_rejects(self):
        bad = copy.deepcopy(self.record)
        bad["prepared_at"] = None
        with self.assertRaises(AuthorizationPreparationError):
            validate_record(bad)

    def test_wrong_prepared_at_rejects(self):
        bad = copy.deepcopy(self.record)
        bad["prepared_at"] = "1999-01-01T00:00:00Z"
        with self.assertRaises(AuthorizationPreparationError):
            validate_record(bad)

    def test_wrong_installation_target_rejects(self):
        bad = copy.deepcopy(self.record)
        bad["installation_target"] = "/Library/GRRR/conservative"
        with self.assertRaises(AuthorizationPreparationError):
            validate_record(bad)

    def test_emit_record_verifies_stage_r_inputs(self):
        record = emit_record(ROOT)
        self.assertEqual(record["status"], "prepared-not-authorized")
        self.assertEqual(
            record["basis"]["stage_r_source_bundle_sha256"],
            STAGE_R_SOURCE_BUNDLE_SHA256,
        )
        self.assertEqual(
            record["basis"]["stage_r_package_sha256"],
            STAGE_R_PACKAGE_SHA256,
        )
        self.assertEqual(
            record["basis"]["stage_r_review_sha256"],
            STAGE_R_REVIEW_SHA256,
        )

    def test_deterministic_build(self):
        first = build_record()
        second = build_record()
        self.assertEqual(first, second)

    def test_record_is_json_serializable_and_reversible(self):
        raw = json.dumps(self.record, sort_keys=True, separators=(",", ":"))
        restored = json.loads(raw)
        self.assertEqual(validate_record(restored), self.record)


if __name__ == "__main__":
    unittest.main()
