"""Fail-closed v4 replay-successor runtime-adapter tests."""

from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import json
import subprocess
import sys
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "research"))

from replay_successor_contract import (  # noqa: E402
    MODES, SESSION_MAXIMUM, candidate_binding, candidate_receipt,
)
from replay_successor_runtime import (  # noqa: E402
    MODE_GUEST_LAUNCHES, adapter_status, candidate_observation,
    future_requirements, validate_adapter_status, validate_future_request,
    validate_observation,
)
from spendability_stage_c import StageCError, digest  # noqa: E402


def future_request(**overrides):
    distinct = [character * 64 for character in "01234"]
    value = {
        "schema_version": 1,
        "record_type": "replay-successor-future-request-v1",
        "contract_receipt_sha256": digest(candidate_receipt()),
        "contract_binding_sha256": digest(candidate_binding()),
        "profile": "independent-replay",
        "stage": "poc",
        "mode": "normal",
        "run": "run-1",
        "reservation": "reservation-1",
        "session_index": 0,
        "session_execution_us": SESSION_MAXIMUM["execution_us"],
        "guest_launches": MODE_GUEST_LAUNCHES["normal"],
        "installer_sha256": distinct[0],
        "review_sha256": distinct[1],
        "authorization_sha256": distinct[2],
        "budget_amendment_sha256": distinct[3],
        "operator_per_run_approval_sha256": distinct[4],
    }
    value.update(overrides)
    return value


class ReplaySuccessorRuntime(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.receipt = candidate_receipt()
        cls.binding = candidate_binding()
        cls.observation = candidate_observation()
        cls.status = adapter_status(
            cls.receipt, cls.binding, cls.observation)

    def test_observation_is_explicitly_uninstalled_and_unauthorized(self):
        self.assertEqual(self.observation["source"], "repository-hypothetical")
        self.assertEqual(self.observation["active_binding_version"], 3)
        self.assertIs(self.observation["installed"], False)
        self.assertIsNone(self.observation["installer_sha256"])
        self.assertIsNone(self.observation["review_sha256"])
        self.assertIsNone(self.observation["authorization_sha256"])
        self.assertIsNone(self.observation["store_device"])
        self.assertIsNone(self.observation["store_inode"])
        self.assertIsNone(self.observation["budget_amendment_sha256"])
        self.assertIsNone(self.observation["operator_per_run_approval_sha256"])
        self.assertIs(self.observation["execution_requested"], False)

    def test_adapter_binds_exact_stage_n_candidate(self):
        self.assertEqual(self.status["basis"]["contract_receipt_sha256"],
                         digest(self.receipt))
        self.assertEqual(self.status["basis"]["contract_binding_sha256"],
                         digest(self.binding))
        self.assertEqual(self.status["basis"]["predecessor_holds_preserved"], 3)

    def test_gate_matrix_has_pass_not_run_and_blocked_states(self):
        gates = self.status["gates"]
        self.assertEqual(gates["stage_n_candidate_contract"]["status"], "pass")
        self.assertEqual(gates["predecessor_history_and_holds"]["status"], "pass")
        for name in ("independent_runtime_review", "operator_budget_amendment",
                     "protected_v4_installation", "installed_store_identity",
                     "per_run_operator_approval", "mandatory_live_replay"):
            self.assertEqual(gates[name]["status"], "not-run", name)
        self.assertEqual(gates["replay_execution"]["status"], "blocked")

    def test_adapter_outcome_never_becomes_authority(self):
        outcome = self.status["outcome"]
        self.assertTrue(outcome["adapter_valid"])
        self.assertTrue(outcome["design_only"])
        self.assertIs(outcome["replay_possible"], False)
        self.assertIs(outcome["execution_authorized"], False)
        self.assertEqual(outcome["allowed_mutations"], [])
        self.assertIsNone(outcome["spendable"])
        self.assertEqual(outcome["failure_mode"], "refuse-before-effects")
        self.assertIs(outcome["protected_access"], False)
        self.assertFalse(any(self.status["authority"].values()))

    def test_status_revalidates_by_exact_regeneration(self):
        result = validate_adapter_status(
            self.status, self.receipt, self.binding, self.observation)
        self.assertTrue(result["outcome"]["adapter_valid"])
        self.assertFalse(result["outcome"]["execution_authorized"])

    def test_adapter_does_not_read_files_or_protected_paths(self):
        def refuse(*args, **kwargs):
            raise AssertionError("design adapter must not read files")
        with mock.patch("builtins.open", side_effect=refuse), \
                mock.patch.object(Path, "open", side_effect=refuse), \
                mock.patch.object(Path, "read_bytes", side_effect=refuse):
            receipt = candidate_receipt()
            binding = candidate_binding()
            observation = candidate_observation()
            status = adapter_status(receipt, binding, observation)
            validate_adapter_status(status, receipt, binding, observation)
            validate_future_request(future_request())

    def test_claimed_installation_is_rejected(self):
        value = deepcopy(self.observation)
        value["installed"] = True
        with self.assertRaises(StageCError) as raised:
            validate_observation(value)
        self.assertEqual(str(raised.exception),
                         "replay_successor_runtime: design adapter observation must remain explicitly uninstalled")

    def test_fabricated_install_identity_is_rejected(self):
        for field in ("installer_sha256", "review_sha256",
                      "authorization_sha256", "budget_amendment_sha256",
                      "operator_per_run_approval_sha256"):
            with self.subTest(field=field):
                value = deepcopy(self.observation)
                value[field] = "0" * 64
                with self.assertRaises(StageCError):
                    validate_observation(value)

    def test_fabricated_store_identity_or_execution_is_rejected(self):
        for field, replacement in (
            ("store_device", 16777229), ("store_inode", 682589447),
            ("execution_requested", True),
            ("active_binding_version", 4), ("source", "live-protected-observation"),
        ):
            with self.subTest(field=field):
                value = deepcopy(self.observation)
                value[field] = replacement
                with self.assertRaises(StageCError):
                    validate_observation(value)

    def test_modified_stage_n_receipt_is_rejected_before_status(self):
        value = deepcopy(self.receipt)
        value["history"]["spendable"] = True
        with self.assertRaises(StageCError):
            adapter_status(value, self.binding, self.observation)

    def test_modified_stage_n_binding_is_rejected_before_status(self):
        value = deepcopy(self.binding)
        value["execution_authorized"] = True
        with self.assertRaises(StageCError):
            adapter_status(self.receipt, value, self.observation)

    def test_modified_status_cannot_self_certify(self):
        value = deepcopy(self.status)
        value["gates"]["replay_execution"]["status"] = "pass"
        with self.assertRaises(StageCError):
            validate_adapter_status(
                value, self.receipt, self.binding, self.observation)

    def test_future_requirements_list_every_protected_gate(self):
        requirements = future_requirements()
        self.assertEqual(requirements["installed_binding"]["version"], 4)
        self.assertEqual(requirements["installed_binding"]["profiles"],
                         ["independent-replay"])
        self.assertEqual(requirements["distinct_receipts_required"], [
            "installer_sha256", "review_sha256", "authorization_sha256",
            "budget_amendment_sha256", "operator_per_run_approval_sha256",
        ])
        self.assertFalse(any(requirements["authority"].values()))
        self.assertIn("exact installer bytes",
                      requirements["protected_verification_required_before_authority"])
        self.assertIn("fresh per-run operator approval",
                      requirements["protected_verification_required_before_authority"])

    def test_valid_future_request_shape_still_has_no_authority(self):
        result = validate_future_request(future_request())
        self.assertIs(result["request_shape_valid"], True)
        self.assertIs(result["execution_authorized"], False)
        self.assertFalse(any(result["authority"].values()))
        self.assertIn("protected installation", result["reason"])

    def test_future_request_binds_exact_stage_n_contract(self):
        self.assertEqual(future_request()["contract_receipt_sha256"],
                         digest(self.receipt))
        self.assertEqual(future_request()["contract_binding_sha256"],
                         digest(self.binding))

    def test_future_request_contract_profile_or_stage_tampering_rejected(self):
        for field, replacement in (
            ("contract_receipt_sha256", "0" * 64),
            ("contract_binding_sha256", "0" * 64),
            ("profile", "offline"), ("stage", "milestone"),
        ):
            with self.subTest(field=field):
                with self.assertRaises(StageCError):
                    validate_future_request(future_request(**{field: replacement}))

    def test_each_mode_has_exact_guest_launch_budget(self):
        for index, mode in enumerate(MODES):
            result = validate_future_request(future_request(
                mode=mode, session_index=index,
                guest_launches=MODE_GUEST_LAUNCHES[mode]))
            self.assertTrue(result["request_shape_valid"])

    def test_unknown_mode_or_wrong_session_budget_is_rejected(self):
        for changes in (
            {"mode": "clean-extra"}, {"session_index": 4},
            {"session_index": True}, {"session_index": 1},
            {"session_execution_us": 1},
            {"session_execution_us": True},
            {"guest_launches": MODE_GUEST_LAUNCHES["normal"] + 1},
        ):
            with self.subTest(changes=changes):
                with self.assertRaises(StageCError):
                    validate_future_request(future_request(**changes))

    def test_missing_invalid_or_reused_future_receipt_is_rejected(self):
        value = future_request()
        value["installer_sha256"] = None
        with self.assertRaises(StageCError):
            validate_future_request(value)
        value = future_request()
        value["review_sha256"] = value["installer_sha256"]
        with self.assertRaises(StageCError):
            validate_future_request(value)
        value = future_request()
        value["authorization_sha256"] = "uppercase"
        with self.assertRaises(StageCError):
            validate_future_request(value)

    def test_future_request_unknown_or_missing_fields_are_rejected(self):
        value = future_request()
        value["extra"] = False
        with self.assertRaises(StageCError):
            validate_future_request(value)
        value = future_request()
        del value["reservation"]
        with self.assertRaises(StageCError):
            validate_future_request(value)

    def test_emitter_is_deterministic_and_rejects_arguments(self):
        script = ROOT / "scripts/show-replay-successor-runtime"
        first = subprocess.run(
            [sys.executable, "-I", "-B", str(script)],
            check=True, text=True, capture_output=True).stdout
        second = subprocess.run(
            [sys.executable, "-I", "-B", str(script)],
            check=True, text=True, capture_output=True).stdout
        self.assertEqual(first, second)
        value = json.loads(first)
        validate_adapter_status(value["status"])
        validate_observation(value["observation"])
        refused = subprocess.run(
            [sys.executable, "-I", "-B", str(script), "unexpected"],
            text=True, capture_output=True)
        self.assertNotEqual(refused.returncode, 0)
        self.assertIn("no arguments accepted", refused.stderr)

    def test_module_contains_no_protected_path_access_api(self):
        source = (ROOT / "research/replay_successor_runtime.py").read_text()
        self.assertNotIn("import os", source)
        self.assertNotIn("import sqlite3", source)
        self.assertNotIn("import subprocess", source)
        self.assertNotIn("/Library/GRRR", source)
        self.assertIn("no filesystem", source)


if __name__ == "__main__":
    unittest.main()
