"""No-execution tests for the three-arm Jev preflight."""

import copy
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "research"))

import jev_three_arm_preflight as preflight  # noqa: E402


class ThreeArmPreflightTests(unittest.TestCase):
    def test_valid_inputs_produce_prepare_only_request(self):
        result = preflight.run_preflight()
        self.assertTrue(result["prepare_only"])
        self.assertFalse(result["execution_authorized"])
        self.assertFalse(result["measurement_started"])
        self.assertEqual(result["design"]["commit"], "9e107609db76022ed6d8e138cbbece2e41d634ee")
        self.assertEqual(result["confirmatory_request"]["total_calls"], 96)
        self.assertEqual(result["confirmatory_request"]["retries"], 0)
        self.assertFalse(result["excluded_pilot"]["reuse_as_confirmatory_repetition"])

    def test_default_invocation_refuses_without_output_or_execution(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "request.json"
            self.assertEqual(preflight.main([]), 2)
            self.assertFalse(output.exists())

    def test_prepare_only_writes_sanitized_exclusive_request(self):
        with tempfile.TemporaryDirectory() as directory:
            output = (Path(directory) / "prepare-only.json").resolve()
            self.assertEqual(
                preflight.main(["--prepare-only", "--output", str(output)]), 0
            )
            value = json.loads(output.read_bytes())
            self.assertTrue(value["prepare_only"])
            self.assertFalse(value["execution_authorized"])
            raw = output.read_bytes()
            for forbidden in (b"apikey_", b"Authorization", b"Bearer "):
                self.assertNotIn(forbidden, raw)
            self.assertEqual(
                preflight.main(["--prepare-only", "--output", str(output)]), 2
            )

    def test_tampered_design_and_approval_reject(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            plan = root / "plan.json"
            approval = root / "approval.md"
            plan.write_bytes(preflight.PLAN_PATH.read_bytes())
            approval.write_bytes(preflight.APPROVAL_PATH.read_bytes())
            plan.write_bytes(plan.read_bytes() + b"\n")
            with self.assertRaises(preflight.PreflightRefused):
                preflight.run_preflight(plan_path=plan, approval_path=approval)
            plan.write_bytes(preflight.PLAN_PATH.read_bytes())
            approval.write_bytes(b"tampered approval")
            with self.assertRaises(preflight.PreflightRefused):
                preflight.run_preflight(plan_path=plan, approval_path=approval)

    def test_pilot_identity_counts_and_usage_must_match(self):
        with tempfile.TemporaryDirectory() as directory:
            pilot = Path(directory)
            for name in ("events.jsonl", "report.json"):
                (pilot / name).write_bytes((preflight.PILOT_PATH / name).read_bytes())
            report = json.loads((pilot / "report.json").read_bytes())
            report["attempts"]["retry_count"] = 1
            (pilot / "report.json").write_text(json.dumps(report))
            original_read = preflight._read_bytes
            immutable_report = (preflight.PILOT_PATH / "report.json").read_bytes()

            def allow_hash_but_not_semantics(path, expected_sha, label):
                if path.name == "report.json":
                    return immutable_report
                return original_read(path, expected_sha, label)

            preflight._read_bytes = allow_hash_but_not_semantics
            try:
                with self.assertRaises(preflight.PreflightRefused):
                    preflight.run_preflight(pilot_path=pilot)
            finally:
                preflight._read_bytes = original_read

    def test_protected_truth_manifest_and_budget_arithmetic(self):
        result = preflight.run_preflight()
        truth = preflight._sha256(preflight.TRUTH_PATH.read_bytes())
        manifest = json.loads(preflight.MANIFEST_PATH.read_bytes())
        self.assertEqual(result["design"]["sha256"], preflight.evaluation_plan_v2.EXPECTED_PLAN_SHA256)
        self.assertEqual(truth, "7cf9f99f5836c4e3e147df2866d54480a706f2665a732fbf61bd1a0d0b4c52ea")
        self.assertEqual(manifest["artifacts"]["protected/truth.json"], truth)
        self.assertEqual(result["confirmatory_request"]["cumulative_call_ceiling_including_pilot"], 128)

    def test_module_has_no_secret_or_network_boundary(self):
        source = Path(preflight.__file__).read_bytes()
        for forbidden in (
            b"TYPESAFE_API_KEY", b"jev_api_key", b"urllib", b"urlopen",
            b"jev_adapter",
        ):
            self.assertNotIn(forbidden, source)

    def test_double_slash_and_protected_outputs_reject(self):
        values = (
            "//Library/GRRR/request.json",
            "/Library/GRRR/request.json",
            "/tmp/real/../request.json",
        )
        for value in values:
            with self.assertRaises(preflight.PreflightRefused):
                preflight._safe_output(Path(value))

    def test_non_immediate_symlinked_output_ancestor_rejects(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            real = root / "real"
            real.mkdir()
            linked = root / "ancestor-link"
            linked.symlink_to(real, target_is_directory=True)
            with self.assertRaises(preflight.PreflightRefused):
                preflight._safe_output(linked / "sub" / "request.json")


if __name__ == "__main__":
    unittest.main()
