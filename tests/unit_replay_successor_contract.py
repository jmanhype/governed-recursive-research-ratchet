"""Fail-closed v4 replay-successor authority-contract tests."""

from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import json
import subprocess
import sys
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
STAGE_A = ROOT / "docs/evidence/spendability/stage-a/BASELINE.json"
STAGE_A_SHA256 = "7608cbe6fc5f671b88573eca8b642ebfbc172f0cb920f75d60ca34cfa60c730a"
sys.path.insert(0, str(ROOT / "research"))

from replay_successor_contract import (  # noqa: E402
    AGGREGATE_SESSION_CEILING_US, BINDING_VERSION, CANDIDATE_DECISION,
    CEILING_BASIS, FAILURE_STOP_POLICY, INSTALL_FAILURE_MODE, MAXIMUM_GUEST_LAUNCHES,
    MODES, PREDECESSOR_HOLD_IDS, PROPOSED_CEILING, ROLLBACK_SCOPE,
    PREDECESSOR_HOLDS, SESSION_MAXIMUM, candidate_binding, candidate_receipt,
    contract_summary, validate_binding, validate_receipt,
)
from spendability_stage_c import StageCError  # noqa: E402


class ReplaySuccessorContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.receipt = candidate_receipt()
        cls.binding = candidate_binding()

    def test_candidate_decision_is_not_approval_or_reconciliation(self):
        self.assertEqual(self.receipt["decision"], CANDIDATE_DECISION)
        self.assertIn("candidate", self.receipt["decision"])
        self.assertFalse(self.receipt["guards"]["reconciliation_claim"])
        self.assertEqual(self.receipt["successor"]["relationship"],
                         "fresh-successor-not-reconciliation")

    def test_predecessor_binds_exact_retained_evidence(self):
        predecessor = self.receipt["predecessor"]
        self.assertEqual(predecessor["active_sha256"],
                         "9c5194dd12ff7601917fcccc293c459db09a41da8bad9fa9983cbef618d453f8")
        self.assertEqual(predecessor["database_sha256"],
                         "9c6ff2561a364ed982cd5477dd4b200c995da6910c9a17aa3d3c411a962d64f3")
        self.assertEqual(predecessor["stage_a_baseline_sha256"],
                         "7608cbe6fc5f671b88573eca8b642ebfbc172f0cb920f75d60ca34cfa60c730a")
        self.assertEqual(predecessor["stage_a_package_sha256"],
                         "bb79e0242ea914d75b3e0ab9b44248c6e4eca8435214a1d970a55bef2a99a391")
        self.assertEqual(predecessor["stage_l_package_sha256"],
                         "56bc2c82accb6530f1a479ad0b23408077a173e2ee7e2f9fcc41bc1e0099df53")
        self.assertEqual(predecessor["stage_m_package_sha256"],
                         "c65aedd7f7a2f861ef5593ba9705981ca42508bf6f3f12a4f23787381d12df0b")

    def test_unknown_history_is_not_converted_to_zero_or_absence(self):
        history = self.receipt["history"]
        self.assertEqual(history["status"], "unresolved")
        self.assertIsNone(history["spendable"])
        self.assertFalse(history["whole_archive_absence_established"])
        self.assertFalse(history["response_ready"])
        self.assertEqual(history["final_classifications_made"], 0)
        self.assertTrue(history["all_original_ceilings_encumbered"])
        self.assertEqual(history["evidence_boundary"], "retained-original-records-only")

    def test_all_three_predecessor_holds_remain_explicit_and_unreleased(self):
        holds = self.receipt["holds"]
        self.assertEqual(holds["status"], "unresolved")
        self.assertEqual(holds["count"], 3)
        self.assertEqual(tuple(holds["reservation_ids"]), PREDECESSOR_HOLD_IDS)
        self.assertEqual(holds["maximum"], {
            "currency": "USD", "money_cents": 0,
            "execution_us": 300_000_000, "review_us": 0,
        })
        self.assertIs(holds["release"], False)

    def test_hold_ids_are_derived_from_retained_stage_a_baseline(self):
        raw = STAGE_A.read_bytes()
        self.assertEqual(sha256(raw).hexdigest(), STAGE_A_SHA256)
        baseline = json.loads(raw)
        pending = []
        for row in baseline["raw_tables"]["reservations"]["rows"]:
            actual = row.get("actual")
            receipt = row.get("receipt")
            actual_value = actual.get("value") if isinstance(actual, dict) else actual
            receipt_value = receipt.get("value") if isinstance(receipt, dict) else receipt
            if (actual_value is None and receipt_value is None
                    and row["maximum"]["decoded"] == PREDECESSOR_HOLDS["maximum"]):
                pending.append(row["id"]["value"])
        pending.sort()
        pending = tuple(pending)
        self.assertEqual(tuple(sorted(PREDECESSOR_HOLD_IDS)), pending)
        self.assertEqual(pending, (
            "69523b39a51c44739114313c9325028c",
            "b34d8b9d106e42eab3a3e43daac98ddd",
            "d375ce6a2d924646bec71df64e939a5b",
        ))

    def test_fresh_allowance_requires_explicit_incremental_amendment(self):
        successor = self.receipt["successor"]
        self.assertEqual(successor["ceiling_basis"], CEILING_BASIS)
        self.assertIn("operator-approved-incremental-amendment-required",
                      successor["ceiling_basis"])
        self.assertEqual(successor["proposed_ceiling"], PROPOSED_CEILING)
        self.assertTrue(self.receipt["history"]["all_original_ceilings_encumbered"])
        self.assertTrue(self.binding["budget_amendment_required"])

    def test_successor_and_predecessor_identities_are_pinned(self):
        self.assertEqual(self.receipt["successor"]["campaign"],
                         "GRRR-REPLAY-SUCCESSOR-POC-2")
        self.assertEqual(self.receipt["successor"]["store_id"],
                         "unissued-independent-replay-v4")
        self.assertEqual(self.binding["predecessor_store_id"],
                         "901acaff42b5a42f667b1c435beba9a9ae8312539cc36eb023c45584fd2e06d6")
        self.assertEqual(self.binding["prior_history_receipt"],
                         "6d3d5b092c0ee8273a657c83823d8465b215f2b1b66ec627dfde2d96b21fe587")

    def test_replay_scope_is_bounded_and_mode_exact(self):
        scope = self.receipt["scope"]
        self.assertEqual(scope["profile"], "independent-replay")
        self.assertEqual(scope["stage"], "poc")
        self.assertEqual(tuple(scope["modes"]), MODES)
        self.assertEqual(scope["session_maximum"], SESSION_MAXIMUM)
        self.assertEqual(scope["session_count"], 4)
        self.assertEqual(scope["aggregate_session_execution_ceiling_us"],
                         AGGREGATE_SESSION_CEILING_US)
        self.assertEqual(scope["maximum_guest_launches"], MAXIMUM_GUEST_LAUNCHES)
        self.assertEqual(scope["failure_stop_policy"], FAILURE_STOP_POLICY)

    def test_no_static_contract_grants_runtime_authority(self):
        guards = self.receipt["guards"]
        self.assertEqual(guards["predecessor_mutations"], [])
        self.assertIs(guards["replay_execution_authorized"], False)
        self.assertIs(guards["per_run_operator_approval_required"], True)
        self.assertEqual(guards["admission"], "blocked")
        self.assertEqual(guards["promotion"], "disabled")
        self.assertIs(guards["automatic_merge"], False)
        self.assertIs(guards["push"], False)
        self.assertFalse(any(guards["authority"].values()))
        self.assertFalse(any(contract_summary()["authority"].values()))

    def test_installation_identities_cannot_be_fabricated(self):
        installation = self.receipt["installation"]
        self.assertIsNone(installation["installer_sha256"])
        self.assertIsNone(installation["review_sha256"])
        self.assertIsNone(installation["authorization_sha256"])
        self.assertEqual(installation["review_status"], "required")
        self.assertEqual(installation["operator_authorization_status"], "required")
        self.assertIs(installation["exclusive_parent"], True)
        self.assertIs(installation["install_once"], True)
        self.assertIs(installation["predecessor_read_only"], True)

    def test_failure_and_rollback_refuse_instead_of_resetting_predecessor(self):
        installation = self.receipt["installation"]
        self.assertEqual(installation["failure_mode"], INSTALL_FAILURE_MODE)
        self.assertEqual(installation["rollback_scope"], ROLLBACK_SCOPE)
        self.assertIs(installation["rollback_requires_verified_baseline"], True)
        self.assertIs(installation["predecessor_rollback"], False)
        self.assertIs(installation["design_only"], True)

    def test_hypothetical_v4_binding_is_replay_only_and_sibling_scoped(self):
        self.assertEqual(self.binding["version"], BINDING_VERSION)
        self.assertEqual(self.binding["profiles"], ["independent-replay"])
        self.assertEqual(self.binding["allowed_mutation_profiles"],
                         ["independent-replay"])
        self.assertEqual(self.binding["directory"],
                         "/Library/GRRR/accounting-poc2/unissued-independent-replay-v4")
        self.assertEqual(self.binding["device_identity"], "required-at-install")
        self.assertEqual(self.binding["inode_identity"], "required-at-install")
        self.assertEqual(self.binding["predecessor_binding_sha256"],
                         self.receipt["predecessor"]["active_sha256"])
        self.assertIs(self.binding["execution_authorized"], False)
        self.assertIs(self.binding["design_only"], True)

    def test_binding_binds_exact_candidate_receipt_hash(self):
        from spendability_stage_c import digest
        self.assertEqual(self.binding["successor_sha256"], digest(self.receipt))
        self.assertEqual(self.binding["campaign"],
                         self.receipt["successor"]["campaign"])
        self.assertEqual(self.binding["store_id"],
                         self.receipt["successor"]["store_id"])

    def test_candidate_revalidates_without_file_or_protected_access(self):
        def refuse(*args, **kwargs):
            raise AssertionError("design validation must not read files")
        with mock.patch("builtins.open", side_effect=refuse), \
                mock.patch.object(Path, "open", side_effect=refuse), \
                mock.patch.object(Path, "read_bytes", side_effect=refuse):
            receipt = candidate_receipt()
            binding = candidate_binding()
            validate_receipt(receipt)
            validate_binding(binding, receipt)

    def test_modified_predecessor_identity_is_rejected(self):
        value = deepcopy(self.receipt)
        value["predecessor"]["stage_m_package_sha256"] = "0" * 64
        with self.assertRaises(StageCError) as raised:
            validate_receipt(value)
        self.assertEqual(str(raised.exception),
                         "replay_successor_contract: predecessor evidence identity differs")

    def test_unknown_history_cannot_become_spendable(self):
        value = deepcopy(self.receipt)
        value["history"]["spendable"] = True
        with self.assertRaises(StageCError) as raised:
            validate_receipt(value)
        self.assertEqual(str(raised.exception),
                         "replay_successor_contract: predecessor history cannot be resolved by this design contract")

    def test_missing_or_released_hold_is_rejected(self):
        value = deepcopy(self.receipt)
        value["holds"]["reservation_ids"].pop()
        value["holds"]["count"] = 2
        with self.assertRaises(StageCError) as raised:
            validate_receipt(value)
        self.assertEqual(str(raised.exception),
                         "replay_successor_contract: predecessor holds must remain exactly unresolved")

    def test_ceiling_increase_cannot_be_relabelled_preapproved(self):
        value = deepcopy(self.receipt)
        value["successor"]["ceiling_basis"] = "preapproved-fresh-poc-allowance"
        with self.assertRaises(StageCError) as raised:
            validate_receipt(value)
        self.assertEqual(str(raised.exception),
                         "replay_successor_contract: successor ceiling basis differs")

    def test_boolean_zero_cannot_replace_integer_money_ceiling(self):
        value = deepcopy(self.receipt)
        value["successor"]["proposed_ceiling"]["money_cents"] = False
        with self.assertRaises(StageCError) as raised:
            validate_receipt(value)
        self.assertEqual(str(raised.exception),
                         "replay_successor_contract: successor proposed ceiling differs")

    def test_unknown_or_extra_mode_is_rejected(self):
        for modes in (["normal"], list(MODES) + ["clean-extra"]):
            value = deepcopy(self.receipt)
            value["scope"]["modes"] = modes
            with self.assertRaises(StageCError):
                validate_receipt(value)

    def test_injected_runtime_authority_is_rejected(self):
        value = deepcopy(self.receipt)
        value["guards"]["authority"]["replay"] = True
        with self.assertRaises(StageCError) as raised:
            validate_receipt(value)
        self.assertEqual(str(raised.exception),
                         "replay_successor_contract: design contract cannot grant authority")

    def test_fabricated_install_identity_is_rejected(self):
        value = deepcopy(self.receipt)
        value["installation"]["installer_sha256"] = "0" * 64
        with self.assertRaises(StageCError) as raised:
            validate_receipt(value)
        self.assertEqual(str(raised.exception),
                         "replay_successor_contract: installation installer_sha256 must remain unissued in the design contract")

    def test_retry_or_predecessor_rollback_is_rejected(self):
        value = deepcopy(self.receipt)
        value["installation"]["failure_mode"] = "retry-after-partial-install"
        with self.assertRaises(StageCError):
            validate_receipt(value)
        value = deepcopy(self.receipt)
        value["installation"]["predecessor_rollback"] = True
        with self.assertRaises(StageCError):
            validate_receipt(value)

    def test_v3_or_legacy_profile_cannot_pose_as_v4_binding(self):
        value = deepcopy(self.binding)
        value["version"] = 3
        with self.assertRaises(StageCError):
            validate_binding(value, self.receipt)
        value = deepcopy(self.binding)
        value["profiles"] = ["synthetic", "offline", "trusted-observation"]
        value["allowed_mutation_profiles"] = value["profiles"]
        with self.assertRaises(StageCError):
            validate_binding(value, self.receipt)

    def test_fabricated_store_device_identity_is_rejected(self):
        value = deepcopy(self.binding)
        value["device_identity"] = 16777229
        value["inode_identity"] = 682589447
        with self.assertRaises(StageCError) as raised:
            validate_binding(value, self.receipt)
        self.assertEqual(str(raised.exception),
                         "replay_successor_contract: binding device/inode identities must not be fabricated")

    def test_binding_cannot_authorize_or_drop_amendment_requirement(self):
        for field, replacement in (
            ("execution_authorized", True),
            ("budget_amendment_required", False),
            ("design_only", False),
        ):
            with self.subTest(field=field):
                value = deepcopy(self.binding)
                value[field] = replacement
                with self.assertRaises(StageCError):
                    validate_binding(value, self.receipt)

    def test_binding_hash_cannot_authenticate_modified_receipt(self):
        value = deepcopy(self.binding)
        receipt = deepcopy(self.receipt)
        receipt["history"]["spendable"] = False
        with self.assertRaises(StageCError) as raised:
            validate_binding(value, receipt)
        self.assertEqual(str(raised.exception),
                         "replay_successor_contract: predecessor history cannot be resolved by this design contract")

    def test_contract_emitter_is_deterministic_and_rejects_arguments(self):
        script = ROOT / "scripts/emit-replay-successor-contract"
        first = subprocess.run(
            [sys.executable, "-I", "-B", str(script)],
            check=True, text=True, capture_output=True,
        ).stdout
        second = subprocess.run(
            [sys.executable, "-I", "-B", str(script)],
            check=True, text=True, capture_output=True,
        ).stdout
        self.assertEqual(first, second)
        value = json.loads(first)
        validate_receipt(value["receipt"])
        validate_binding(value["binding"], value["receipt"])
        refused = subprocess.run(
            [sys.executable, "-I", "-B", str(script), "unexpected"],
            text=True, capture_output=True,
        )
        self.assertNotEqual(refused.returncode, 0)
        self.assertIn("no arguments accepted", refused.stderr)


if __name__ == "__main__":
    unittest.main()
