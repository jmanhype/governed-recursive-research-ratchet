"""Fail-closed future v4 installer/authorization contract tests."""

from copy import deepcopy
from pathlib import Path
import json
import subprocess
import sys
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "research"))

from replay_successor_installer_contract import (  # noqa: E402
    BASE_COMMIT, CANONICAL_PYTHON_SHA256, INSTALLER_ACTION, OPERATOR_PRINCIPAL,
    PREDECESSOR_ACTIVE_SHA256, PREDECESSOR_DATABASE_SHA256,
    PREDECESSOR_RECOVERY_SHA256, SOURCE_ARTIFACTS, SOURCE_ROLES, STAGE_N_PACKAGE_SHA256,
    STAGE_O_PACKAGE_SHA256, candidate_authorization_requirement,
    candidate_installer_contract, contract_summary,
    validate_issued_authorization_shape, validate_installer_contract,
)
from spendability_stage_c import StageCError, digest  # noqa: E402


def issued_authorization(**overrides):
    distinct = [character * 64 for character in "012"]
    value = {
        "schema_version": 1,
        "record_type": "replay-successor-v4-authorization-v1",
        "action": INSTALLER_ACTION,
        "principal": OPERATOR_PRINCIPAL,
        "basis": {
            "story_head": BASE_COMMIT,
            "stage_n_package_sha256": STAGE_N_PACKAGE_SHA256,
            "stage_o_package_sha256": STAGE_O_PACKAGE_SHA256,
            "predecessor_active_sha256": PREDECESSOR_ACTIVE_SHA256,
            "predecessor_database_sha256": PREDECESSOR_DATABASE_SHA256,
            "predecessor_recovery_sha256": PREDECESSOR_RECOVERY_SHA256,
        },
        "installer_sha256": distinct[0],
        "plan_sha256": distinct[1],
        "review_sha256": distinct[2],
        "protected_installation_requested": True,
        "exclusive_parent": True,
        "budget_amendment_required": True,
        "budget_amendment_authorized": False,
        "reconciliation_authorized": False,
        "replay_authorized": False,
        "execution_authorized": False,
        "admission": "blocked",
        "promotion": "disabled",
        "automatic_merge": False,
        "push": False,
    }
    value.update(overrides)
    return value


class ReplaySuccessorInstallerContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = candidate_installer_contract()

    def test_contract_binds_exact_committed_basis(self):
        basis = self.contract["basis"]
        self.assertEqual(basis["story_head"], BASE_COMMIT)
        self.assertEqual(basis["stage_n_package_sha256"], STAGE_N_PACKAGE_SHA256)
        self.assertEqual(basis["stage_o_package_sha256"], STAGE_O_PACKAGE_SHA256)
        self.assertEqual(basis["predecessor_active_sha256"], PREDECESSOR_ACTIVE_SHA256)
        self.assertEqual(basis["predecessor_database_sha256"], PREDECESSOR_DATABASE_SHA256)
        self.assertEqual(basis["predecessor_recovery_sha256"], PREDECESSOR_RECOVERY_SHA256)

    def test_decision_and_record_type_are_unissued_design_only(self):
        self.assertEqual(self.contract["decision"],
                         "candidate-installer-contract-not-issued")
        self.assertEqual(self.contract["record_type"],
                         "replay-successor-v4-installer-contract-v1")
        self.assertTrue(self.contract["outcome"]["design_only"])
        self.assertEqual(self.contract["installer"]["protected_access"],
                         "design-only-no-access")

    def test_future_installer_closure_is_exact_and_unhashed(self):
        installer = self.contract["installer"]
        self.assertEqual(tuple(installer["source_roles"]), SOURCE_ROLES)
        self.assertEqual(installer["source_artifacts"], SOURCE_ARTIFACTS)
        self.assertEqual(installer["source_artifacts"]["installer-entrypoint"],
                         "/Library/GRRR/bootstrap/install-replay-successor-v4")
        self.assertEqual(installer["source_artifacts"]["stage-o-runtime-adapter"],
                         "/Library/GRRR/bootstrap/replay-successor-v4-stage_o_runtime_adapter.py")
        self.assertEqual(set(installer["source_sha256"]), set(SOURCE_ROLES))
        self.assertTrue(all(value is None
                            for value in installer["source_sha256"].values()))
        self.assertEqual(installer["interpreter_sha256"], CANONICAL_PYTHON_SHA256)
        self.assertIsNone(installer["plan_sha256"])
        self.assertIsNone(installer["review_sha256"])
        self.assertIsNone(installer["authorization_sha256"])
        self.assertEqual(installer["issuance_status"], "unissued")

    def test_installer_target_is_fresh_sibling_not_predecessor_replacement(self):
        installer = self.contract["installer"]
        self.assertEqual(installer["target_store_id"],
                         "unissued-independent-replay-v4")
        self.assertEqual(installer["target_directory"],
                         "/Library/GRRR/accounting-poc2/unissued-independent-replay-v4")
        self.assertNotEqual(installer["target_directory"],
                            "/Library/GRRR/accounting-poc2/901acaff42b5a42f667b1c435beba9a9ae8312539cc36eb023c45584fd2e06d6")

    def test_install_safety_requires_exclusion_one_shot_and_read_only_predecessor(self):
        installer = self.contract["installer"]
        self.assertIs(installer["exclusive_parent"], True)
        self.assertIs(installer["install_once"], True)
        self.assertIs(installer["predecessor_read_only"], True)
        self.assertEqual(installer["predecessor_mutations"], [])
        self.assertEqual(installer["failure_mode"],
                         "refuse-no-retry-preserve-partial-evidence")
        self.assertEqual(installer["rollback_scope"],
                         "new-successor-namespace-only")

    def test_authorization_cannot_amend_reconcile_or_execute(self):
        authorization = self.contract["authorization"]
        self.assertEqual(authorization["action"], INSTALLER_ACTION)
        self.assertEqual(authorization["principal"], OPERATOR_PRINCIPAL)
        self.assertIsNone(authorization["plan_sha256"])
        self.assertIsNone(authorization["review_sha256"])
        self.assertEqual(authorization["record_sha256_policy"],
                         "external-exact-hash-required-at-install")
        self.assertIs(authorization["budget_amendment_required"], True)
        self.assertIs(authorization["budget_amendment_authorized"], False)
        self.assertIs(authorization["reconciliation_authorized"], False)
        self.assertIs(authorization["replay_authorized"], False)
        self.assertIs(authorization["execution_authorized"], False)

    def test_gate_inventory_and_outcome_fail_closed(self):
        gates = self.contract["gates"]
        self.assertEqual(set(gates), {
            "installer_source_built", "independent_security_review",
            "exact_plan_issued", "operator_authorization_issued",
            "protected_staging", "installation", "postflight",
        })
        self.assertTrue(all(gate["status"] == "not-run" for gate in gates.values()))
        outcome = self.contract["outcome"]
        self.assertTrue(outcome["contract_valid"])
        self.assertFalse(outcome["installer_issued"])
        self.assertFalse(outcome["authorization_issued"])
        self.assertFalse(outcome["installation_ready"])
        self.assertFalse(outcome["protected_access_performed"])
        self.assertEqual(outcome["allowed_mutations"], [])
        self.assertIsNone(outcome["spendable"])
        self.assertFalse(any(self.contract["authority"].values()))

    def test_contract_revalidates_by_exact_regeneration(self):
        result = validate_installer_contract(self.contract)
        self.assertTrue(result["outcome"]["contract_valid"])
        self.assertFalse(result["outcome"]["installation_ready"])

    def test_boolean_and_float_contract_versions_are_rejected(self):
        for malformed in (True, 1.0):
            with self.subTest(malformed=malformed):
                value = deepcopy(self.contract)
                value["schema_version"] = malformed
                with self.assertRaises(StageCError) as raised:
                    validate_installer_contract(value)
                self.assertEqual(str(raised.exception),
                                 "replay_successor_installer_contract: installer contract version differs")

    def test_contract_generation_does_not_read_files_or_protected_paths(self):
        def refuse(*args, **kwargs):
            raise AssertionError("design contract must not read files")
        with mock.patch("builtins.open", side_effect=refuse), \
                mock.patch.object(Path, "open", side_effect=refuse), \
                mock.patch.object(Path, "read_bytes", side_effect=refuse):
            value = candidate_installer_contract()
            validate_installer_contract(value)
            validate_issued_authorization_shape(issued_authorization())

    def test_changed_basis_is_rejected(self):
        for field, replacement in (
            ("story_head", "0" * 40), ("stage_n_package_sha256", "0" * 64),
            ("stage_o_package_sha256", "0" * 64),
            ("predecessor_active_sha256", "0" * 64),
            ("predecessor_database_sha256", "0" * 64),
            ("predecessor_recovery_sha256", "0" * 64),
        ):
            with self.subTest(field=field):
                value = deepcopy(self.contract)
                value["basis"][field] = replacement
                with self.assertRaises(StageCError):
                    validate_installer_contract(value)

    def test_fabricated_installer_plan_review_or_authorization_hash_rejected(self):
        value = deepcopy(self.contract)
        value["installer"]["source_sha256"]["installer-entrypoint"] = "0" * 64
        with self.assertRaises(StageCError):
            validate_installer_contract(value)
        for field in ("plan_sha256", "review_sha256", "authorization_sha256"):
            with self.subTest(field=field):
                value = deepcopy(self.contract)
                value["installer"][field] = "1" * 64
                with self.assertRaises(StageCError):
                    validate_installer_contract(value)

    def test_missing_or_extra_source_role_rejected(self):
        value = deepcopy(self.contract)
        value["installer"]["source_roles"].pop()
        del value["installer"]["source_sha256"]["postflight-verifier"]
        del value["installer"]["source_artifacts"]["postflight-verifier"]
        with self.assertRaises(StageCError):
            validate_installer_contract(value)
        value = deepcopy(self.contract)
        value["installer"]["source_roles"].append("unreviewed-extra")
        value["installer"]["source_sha256"]["unreviewed-extra"] = None
        value["installer"]["source_artifacts"]["unreviewed-extra"] = "/unreviewed"
        with self.assertRaises(StageCError):
            validate_installer_contract(value)

    def test_changed_future_source_artifact_path_is_rejected(self):
        value = deepcopy(self.contract)
        value["installer"]["source_artifacts"]["atomic-publisher"] = (
            "/Library/GRRR/bootstrap/unspecified-publisher.py")
        with self.assertRaises(StageCError) as raised:
            validate_installer_contract(value)
        self.assertEqual(str(raised.exception),
                         "replay_successor_installer_contract: future source artifact paths differ")

    def test_unsafe_install_flags_and_failure_modes_rejected(self):
        changes = (
            ("exclusive_parent", False), ("install_once", False),
            ("predecessor_read_only", False),
            ("predecessor_mutations", ["reset"]),
            ("failure_mode", "retry-after-partial-install"),
            ("rollback_scope", "predecessor-reset"),
            ("protected_access", "authorized-live-access"),
        )
        for field, replacement in changes:
            with self.subTest(field=field):
                value = deepcopy(self.contract)
                value["installer"][field] = replacement
                with self.assertRaises(StageCError):
                    validate_installer_contract(value)

    def test_authority_injection_is_rejected(self):
        for section, field, replacement in (
            ("authorization", "budget_amendment_authorized", True),
            ("authorization", "reconciliation_authorized", True),
            ("authorization", "replay_authorized", True),
            ("authorization", "execution_authorized", True),
            ("authorization", "automatic_merge", True),
            ("authorization", "push", True),
        ):
            with self.subTest(section=section, field=field):
                value = deepcopy(self.contract)
                value[section][field] = replacement
                with self.assertRaises(StageCError):
                    validate_installer_contract(value)

    def test_gate_or_outcome_self_certification_is_rejected(self):
        value = deepcopy(self.contract)
        value["gates"]["installation"]["status"] = "pass"
        with self.assertRaises(StageCError):
            validate_installer_contract(value)
        value = deepcopy(self.contract)
        value["outcome"]["installation_ready"] = True
        with self.assertRaises(StageCError):
            validate_installer_contract(value)

    def test_authorization_requirement_remains_external_and_unissued(self):
        requirement = candidate_authorization_requirement()
        self.assertEqual(requirement["action"], INSTALLER_ACTION)
        self.assertEqual(requirement["principal"], OPERATOR_PRINCIPAL)
        self.assertEqual(requirement["distinct_receipts_required"],
                         ("installer_sha256", "plan_sha256", "review_sha256"))
        self.assertTrue(requirement["external_authorization_sha256_required"])
        self.assertTrue(requirement["must_preserve_predecessor"])
        self.assertTrue(requirement["budget_amendment_required"])
        self.assertFalse(requirement["budget_amendment_authorized"])
        self.assertFalse(any(requirement["authority"].values()))

    def test_valid_future_authorization_shape_still_does_not_authenticate(self):
        result = validate_issued_authorization_shape(issued_authorization())
        self.assertIs(result["authorization_shape_valid"], True)
        self.assertIs(result["authenticated"], False)
        self.assertIs(result["installation_authorized"], False)
        self.assertFalse(any(result["authority"].values()))
        self.assertIn("live state remain unverified", result["reason"])

    def test_boolean_and_float_authorization_versions_are_rejected(self):
        for malformed in (True, 1.0):
            with self.subTest(malformed=malformed):
                value = issued_authorization(schema_version=malformed)
                with self.assertRaises(StageCError) as raised:
                    validate_issued_authorization_shape(value)
                self.assertEqual(str(raised.exception),
                                 "replay_successor_installer_contract: issued authorization version differs")

    def test_future_authorization_basis_and_action_are_pinned(self):
        for section, field, replacement in (
            ("basis", "stage_o_package_sha256", "0" * 64),
            ("basis", "predecessor_active_sha256", "0" * 64),
            ("record", "action", "install-unspecified-store"),
            ("record", "principal", "payload-role"),
        ):
            with self.subTest(section=section, field=field):
                value = issued_authorization()
                target = value if section == "record" else value[section]
                target[field] = replacement
                with self.assertRaises(StageCError):
                    validate_issued_authorization_shape(value)

    def test_future_authorization_receipts_must_be_distinct_and_hashed(self):
        value = issued_authorization()
        value["plan_sha256"] = value["installer_sha256"]
        with self.assertRaises(StageCError):
            validate_issued_authorization_shape(value)
        value = issued_authorization()
        value["review_sha256"] = None
        with self.assertRaises(StageCError):
            validate_issued_authorization_shape(value)
        value = issued_authorization()
        value["installer_sha256"] = True
        with self.assertRaises(StageCError):
            validate_issued_authorization_shape(value)

    def test_future_authorization_cannot_smuggle_operational_authority(self):
        changes = (
            ("protected_installation_requested", False),
            ("exclusive_parent", False),
            ("budget_amendment_authorized", True),
            ("reconciliation_authorized", True),
            ("replay_authorized", True),
            ("execution_authorized", True),
            ("automatic_merge", True), ("push", True),
        )
        for field, replacement in changes:
            with self.subTest(field=field):
                value = issued_authorization(**{field: replacement})
                with self.assertRaises(StageCError):
                    validate_issued_authorization_shape(value)

    def test_future_authorization_unknown_or_missing_fields_rejected(self):
        value = issued_authorization()
        value["extra"] = False
        with self.assertRaises(StageCError):
            validate_issued_authorization_shape(value)
        value = issued_authorization()
        del value["exclusive_parent"]
        with self.assertRaises(StageCError):
                    validate_issued_authorization_shape(value)

    def test_summary_remains_design_only_and_powerless(self):
        summary = contract_summary()
        self.assertEqual(summary["implementation_status"], "design-only")
        self.assertEqual(summary["future_action"], INSTALLER_ACTION)
        self.assertEqual(summary["unissued_receipts"], [
            "source_sha256", "plan_sha256", "review_sha256",
            "authorization_sha256",
        ])
        self.assertFalse(summary["budget_amendment_authorized"])
        self.assertFalse(summary["reconciliation_authorized"])
        self.assertFalse(summary["replay_authorized"])
        self.assertFalse(summary["execution_authorized"])
        self.assertFalse(any(summary["authority"].values()))

    def test_emitter_is_deterministic_and_rejects_arguments(self):
        script = ROOT / "scripts/show-replay-successor-installer-contract"
        first = subprocess.run(
            [sys.executable, "-I", "-B", str(script)],
            check=True, text=True, capture_output=True).stdout
        second = subprocess.run(
            [sys.executable, "-I", "-B", str(script)],
            check=True, text=True, capture_output=True).stdout
        self.assertEqual(first, second)
        value = json.loads(first)
        validate_installer_contract(value["contract"])
        refused = subprocess.run(
            [sys.executable, "-I", "-B", str(script), "unexpected"],
            text=True, capture_output=True)
        self.assertNotEqual(refused.returncode, 0)
        self.assertIn("no arguments accepted", refused.stderr)

    def test_module_has_no_file_database_or_process_access_api(self):
        source = (ROOT / "research/replay_successor_installer_contract.py").read_text()
        self.assertNotIn("import os", source)
        self.assertNotIn("import sqlite3", source)
        self.assertNotIn("import subprocess", source)
        self.assertNotIn("Path(", source)
        self.assertIn("cannot authenticate or install anything", source)


if __name__ == "__main__":
    unittest.main()
