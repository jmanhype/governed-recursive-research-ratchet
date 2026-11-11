"""Source-only tests for the fail-closed read-only status projection."""

import copy
import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "research"))

from status_view import ADMISSION_SUBSET, REQUIRED_GATES, project_status
from review_report import load_replay_data


def passing_receipt() -> dict:
    return {
        "run": "run-1", "challenge": "challenge-1", "verified": True,
        "finding": "Verified defect",
        "gates": {name: {"status": "pass"} for name in REQUIRED_GATES},
    }


def complete_data() -> dict:
    return {
        "receipt": passing_receipt(),
        "lifecycle": {"evaluator_succeeded": True, "elapsed_seconds": 4.5},
        "snapshot": {"version": 1},
    }


class TestStatusView(unittest.TestCase):
    def test_exact_positive_profile_is_review_eligible_not_approval(self):
        report = project_status(complete_data())
        self.assertTrue(report["verification"]["evidence_review_eligible"])
        self.assertTrue(report["verification"]["gates"]["exact_profile_pass"])
        self.assertEqual(report["recommendation"], "Needs more evidence")
        self.assertFalse(report["human_decision"]["approval"])
        self.assertFalse(report["admission"]["authorized"])
        self.assertFalse(report["promotion"]["authorized"])

    def test_all_eleven_gates_and_distinct_nine_gate_admission_subset(self):
        self.assertEqual(len(REQUIRED_GATES), 11)
        self.assertEqual(len(set(REQUIRED_GATES)), 11)
        self.assertEqual(len(ADMISSION_SUBSET), 9)
        report = project_status({"receipt": passing_receipt()})
        self.assertEqual(set(report["verification"]["gates"]["required"]), set(REQUIRED_GATES))
        self.assertEqual(report["verification"]["gates"]["required_total"], 11)

    def test_nine_pass_two_not_run_is_not_hidden_as_nine_of_nine(self):
        receipt = passing_receipt()
        for name in ("reviewer_outcome", "action_specific_human_approval"):
            receipt["gates"][name]["status"] = "not-run"
        report = project_status({"receipt": receipt})
        gates = report["verification"]["gates"]
        self.assertEqual((gates["required_passed"], gates["required_total"]), (9, 11))
        self.assertEqual((gates["admission_subset_passed"], gates["admission_subset_total"]), (9, 9))
        self.assertFalse(report["verification"]["evidence_review_eligible"])
        self.assertFalse(report["source_review"]["eligible"])

    def test_zero_and_missing_gates_fail_closed(self):
        for gates in ({},):
            receipt = passing_receipt()
            receipt["gates"] = gates
            report = project_status({"receipt": receipt})
            required = report["verification"]["gates"]["required"]
            self.assertEqual(report["verification"]["gates"]["required_passed"], 0)
            self.assertFalse(report["verification"]["evidence_review_eligible"])
            self.assertTrue(all(item["status"] == "not-run" for item in required.values()))
        for gates in (None, []):
            receipt = passing_receipt()
            receipt["gates"] = gates
            report = project_status({"receipt": receipt})
            required = report["verification"]["gates"]["required"]
            self.assertEqual(report["verification"]["gates"]["required_passed"], 0)
            self.assertFalse(report["verification"]["evidence_review_eligible"])
            self.assertTrue(all(item["status"] == "not-run" for item in required.values()))

    def test_every_required_gate_blocks_on_fail_error_unknown_not_run_and_malformed(self):
        blocking = ("fail", "error", "unknown", "not-run")
        for gate in REQUIRED_GATES:
            for status in blocking:
                receipt = passing_receipt()
                receipt["gates"][gate] = {"status": status}
                with self.subTest(gate=gate, status=status):
                    report = project_status({"receipt": receipt})
                    self.assertEqual(report["verification"]["gates"]["required"][gate]["status"], status)
                    self.assertEqual(report["verification"]["gates"]["required_passed"], len(REQUIRED_GATES) - 1)
                    self.assertFalse(report["verification"]["evidence_review_eligible"])
            receipt = passing_receipt()
            del receipt["gates"][gate]
            with self.subTest(gate=gate, status="missing"):
                report = project_status({"receipt": receipt})
                self.assertEqual(report["verification"]["gates"]["required"][gate]["status"], "not-run")
                self.assertFalse(report["verification"]["evidence_review_eligible"])
            receipt = passing_receipt()
            receipt["gates"][gate] = {"status": []}
            with self.subTest(gate=gate, status="malformed"):
                report = project_status({"receipt": receipt})
                self.assertEqual(report["verification"]["gates"]["required"][gate]["status"], "malformed")
                self.assertFalse(report["verification"]["evidence_review_eligible"])

    def test_extra_gates_do_not_substitute_for_missing_required_gates(self):
        receipt = passing_receipt()
        del receipt["gates"]["budget_state"]
        receipt["gates"]["reviewer_outcome"] = {"status": "pass"}
        receipt["gates"]["extra_alias"] = {"status": "pass"}
        report = project_status({"receipt": receipt})
        self.assertEqual(report["verification"]["gates"]["required"]["budget_state"]["status"], "not-run")
        self.assertEqual(report["verification"]["gates"]["required_passed"], len(REQUIRED_GATES) - 1)
        self.assertFalse(report["verification"]["evidence_review_eligible"])

    def test_verified_must_be_exact_boolean_true(self):
        for verified in (False, None, 1, "true", [True]):
            with self.subTest(verified=verified):
                receipt = passing_receipt()
                receipt["verified"] = verified
                report = project_status({"receipt": receipt})
                self.assertFalse(report["verification"]["verified"])
                self.assertFalse(report["verification"]["evidence_review_eligible"])
                self.assertIn("VERIFIED_NOT_EXACT_TRUE", report["reason_codes"])

    def test_finding_must_be_exact_verified_defect_for_eligibility(self):
        for finding in ("Not reproduced", "Inconclusive", "verified defect", "Magic", None):
            with self.subTest(finding=finding):
                receipt = passing_receipt()
                receipt["finding"] = finding
                report = project_status({"receipt": receipt})
                self.assertFalse(report["verification"]["evidence_review_eligible"])
                expected = ("FINDING_NOT_VERIFIED_DEFECT" if finding in
                            ("Not reproduced", "Inconclusive") else
                            "FINDING_UNKNOWN_OR_MALFORMED")
                self.assertIn(expected, report["reason_codes"])

    def test_malformed_containers_remain_unknown_and_blocked(self):
        for data in (
            None, [], {"receipt": []},
            {"receipt": {**passing_receipt(), "gates": {}}, "lifecycle": []},
            {"receipt": {**passing_receipt(), "gates": {"baseline_correctness": []}}},
        ):
            with self.subTest(data=data):
                report = project_status(data)
                self.assertEqual(report["execution"]["state"], "Unknown")
                self.assertFalse(report["verification"]["evidence_review_eligible"])
                self.assertFalse(any(report["action_authorization"]["authorities"].values()))

    def test_missing_lifecycle_is_unknown_not_failed(self):
        report = project_status({"receipt": passing_receipt()})
        self.assertEqual(report["execution"]["state"], "Unknown")
        self.assertIn("LIFECYCLE_MISSING", report["reason_codes"])

    def test_costs_missing_invalid_and_ambiguous_are_null_and_unknown(self):
        values = (None, True, False, -1, -0.5, float("nan"), float("inf"),
                  float("-inf"), "0", 10 ** 10000)
        for value in values:
            with self.subTest(value=value):
                receipt = passing_receipt()
                receipt["cost_usd"] = value
                report = project_status({"receipt": receipt})
                self.assertIsNone(report["budget"]["cost_usd"])
                self.assertEqual(report["budget"]["state"], "Unknown")
                self.assertEqual(report["budget"]["spendability"], "Unknown")
        receipt = passing_receipt()
        receipt["cost_usd"] = 1.25
        report = project_status({"receipt": receipt, "lifecycle": {"cost_usd": 2.00}})
        self.assertIsNone(report["budget"]["cost_usd"])
        self.assertEqual(report["budget"]["reason_code"], "COST_MALFORMED_OR_AMBIGUOUS")

    def test_explicit_zero_and_nonzero_costs_remain_unverified_observations(self):
        for value in (0, 0.0, 2, 2.5):
            with self.subTest(value=value):
                receipt = passing_receipt()
                receipt["cost_usd"] = value
                report = project_status({"receipt": receipt})
                self.assertEqual(report["budget"]["cost_usd"], value)
                self.assertIs(type(report["budget"]["cost_usd"]), type(value))
                self.assertEqual(report["budget"]["state"], "Reported")
                self.assertFalse(report["budget"]["settled_accounting"])
                self.assertEqual(report["budget"]["spendability"], "Unknown")

    def test_large_integer_cost_is_exact_and_json_safe(self):
        exact_cost = 9007199254740993
        receipt = passing_receipt()
        receipt["cost_usd"] = exact_cost
        report = project_status({"receipt": receipt})
        self.assertIs(type(report["budget"]["cost_usd"]), int)
        self.assertEqual(report["budget"]["cost_usd"], exact_cost)
        encoded = json.dumps(report, allow_nan=False)
        decoded = json.loads(encoded)
        self.assertIs(type(decoded["budget"]["cost_usd"]), int)
        self.assertEqual(decoded["budget"]["cost_usd"], exact_cost)

    def test_exact_integer_and_mixed_float_cost_conflicts_remain_unknown(self):
        pairs = ((9007199254740992, 9007199254740993), (2, 2.5))
        for input_cost, receipt_cost in pairs:
            with self.subTest(input_cost=input_cost, receipt_cost=receipt_cost):
                receipt = passing_receipt()
                receipt["cost_usd"] = receipt_cost
                report = project_status({"cost_usd": input_cost, "receipt": receipt})
                self.assertIsNone(report["budget"]["cost_usd"])
                self.assertEqual(report["budget"]["state"], "Unknown")
                self.assertEqual(report["budget"]["reason_code"],
                                 "COST_MALFORMED_OR_AMBIGUOUS")

    def test_projection_is_detached_and_input_unchanged(self):
        data = complete_data()
        data["receipt"]["nested"] = {"mutable": ["original"]}
        before = copy.deepcopy(data)
        first = project_status(data)
        first["verification"]["finding"] = "Changed"
        first["verification"]["gates"]["required"]["isolation"]["status"] = "fail"
        second = project_status(data)
        self.assertEqual(data, before)
        self.assertEqual(second["verification"]["finding"], "Verified defect")
        self.assertEqual(second["verification"]["gates"]["required"]["isolation"]["status"], "pass")

    def test_pure_projection_has_negative_io_network_and_time_guards(self):
        data = complete_data()
        denial = mock.Mock(side_effect=AssertionError("pure projection performed a guarded call"))
        with mock.patch("builtins.open", denial), mock.patch("os.open", denial), \
                mock.patch("os.stat", denial), mock.patch("os.lstat", denial), \
                mock.patch("os.read", denial), mock.patch("os.write", denial), \
                mock.patch("time.time", denial), mock.patch("time.monotonic", denial), \
                mock.patch("socket.socket", denial):
            report = project_status(data)
        self.assertEqual(report["schema_version"], 2)

    def test_unsupported_axes_and_all_action_authorities_fail_closed(self):
        report = project_status(complete_data())
        self.assertEqual(report["source_review"]["state"], "Not established")
        self.assertEqual(report["human_decision"]["state"], "Not established")
        self.assertEqual(report["action_authorization"]["state"], "Not established")
        self.assertEqual(report["installation"]["state"], "Not qualified")
        self.assertEqual(report["budget"]["spendability"], "Unknown")
        self.assertEqual(report["cessation"]["state"], "Unknown")
        self.assertEqual(report["admission"]["state"], "Not established")
        self.assertEqual(report["promotion"]["state"], "Disabled")
        self.assertFalse(any(report["action_authorization"]["authorities"].values()))
        self.assertTrue(report["read_only"])
        self.assertFalse(report["scope"]["current_verification"])

    def test_arbitrary_authority_and_ready_claims_are_not_trusted(self):
        data = complete_data()
        data["receipt"].update({
            "admission": "authorized", "promotion": "enabled",
            "ready_for_action": True, "contract_admission_authorized": True,
        })
        data["lifecycle"]["stopped"] = False
        report = project_status(data)
        self.assertFalse(report["human_decision"]["approval"])
        self.assertFalse(report["admission"]["authorized"])
        self.assertFalse(report["promotion"]["authorized"])
        self.assertFalse(any(report["action_authorization"]["authorities"].values()))
        self.assertEqual(report["cessation"]["state"], "Unknown")

    def test_no_hardcoded_snapshot_identity_is_projected(self):
        old_hash = "ab8d72f25c3a4ce2f5d5d672c4d052ea2de442f9c9384bd381d8222d7a91b689"
        report = project_status(complete_data())
        self.assertIsNone(report["evidence_identity"]["digest"])
        self.assertNotEqual(report["evidence_identity"]["basis"], old_hash)

    def test_subclass_equality_and_lookup_hooks_cannot_make_gates_pass(self):
        class Spoof(str):
            def __eq__(self, other):
                return True
        class Hooked(dict):
            def get(self, *args):
                raise AssertionError("lookup hook invoked")
        data = complete_data()
        data["receipt"]["gates"]["isolation"]["status"] = Spoof("fail")
        for value in (data, Hooked(complete_data())):
            report = project_status(value)
            self.assertFalse(report["verification"]["evidence_review_eligible"])
            self.assertIn("INPUT_MALFORMED", report["reason_codes"])

    def test_terminal_control_characters_are_not_projected(self):
        data = complete_data()
        data["receipt"]["run"] = "\x1b[2J"
        data["receipt"]["gates"]["isolation"]["status"] = "\x1b[31mpass"
        report = project_status(data)
        self.assertEqual(report["run"], "unknown")
        self.assertFalse(report["verification"]["evidence_review_eligible"])
        self.assertNotIn("\x1b", json.dumps(report, ensure_ascii=False))

    def test_real_loader_and_cli_journeys_use_same_projection(self):
        with tempfile.TemporaryDirectory(prefix="grrr-status-") as directory:
            root = Path(directory)
            app = root / "app"
            export = app / "docs/evidence/replay-authority/replay-result/export-ca47bda9f47645b1910cba1449bcddfe"
            (app / "scripts").mkdir(parents=True)
            (app / "research").mkdir()
            shutil.copyfile(ROOT / "scripts/grrr-review", app / "scripts/grrr-review")
            for name in ("status_view.py", "review_report.py", "admission.py", "common.py"):
                shutil.copyfile(ROOT / "research" / name, app / "research" / name)
            objects = export / "objects" / "78fde524d9562f6cb28df336512b3ca84bc8d72c72b47cd71f1a47516613ab4e"
            objects.parent.mkdir(parents=True)
            receipt = passing_receipt()
            del receipt["gates"]["isolation"]
            receipt["gates"]["reviewer_outcome"] = {"status": "pass"}
            receipt["identities"] = {"challenge": "challenge-1"}
            objects.write_text(json.dumps(receipt), encoding="utf-8")
            (export / "snapshot.json").write_text('{"version":1}', encoding="utf-8")
            (export.parent / "lifecycle.json").write_text(
                json.dumps({"evaluator_succeeded": False, "elapsed_seconds": 2}), encoding="utf-8"
            )
            loaded = load_replay_data(export)
            expected = project_status(loaded)
            self.assertEqual(expected["execution"]["state"], "Failed")
            self.assertFalse(expected["verification"]["evidence_review_eligible"])
            command = [sys.executable, "-B", str(app / "scripts/grrr-review")]
            json_reviews = []
            for view in ("review", "status"):
                result = subprocess.run(
                    command + ["--view", view, "--format", "json"],
                    check=True, text=True, capture_output=True,
                )
                self.assertEqual(json.loads(result.stdout), expected)
                json_reviews.append(result.stdout)
            self.assertEqual(json_reviews[0], json_reviews[1])
            for view in ("review", "status"):
                result = subprocess.run(
                    command + ["--view", view, "--format", "text"],
                    check=True, text=True, capture_output=True,
                )
                self.assertNotIn("\x1b[", result.stdout)
                self.assertIn("Historical archive; current verification absent", result.stdout)
                self.assertIn("Cost:            Unknown; no settled or spendable amount", result.stdout)
                self.assertIn("isolation: not-run", result.stdout)
                self.assertIn("All authorities: false", result.stdout)
                result = subprocess.run(
                    command + ["--view", view, "--format", "markdown"],
                    check=True, text=True, capture_output=True,
                )
                self.assertIn("Current verification is absent", result.stdout)
                self.assertIn("- isolation: not-run", result.stdout)


if __name__ == "__main__":
    unittest.main()
