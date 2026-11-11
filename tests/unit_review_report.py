"""Tests for the review report generator."""

import json, sys, unittest
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "research"))

from review_report import (
    FINDINGS, EXECUTION_STATES, DECISIONS, ReportError,
    build_report, to_json, to_markdown, to_plain_text,
    to_status_json, to_status_markdown, to_status_plain_text,
    load_replay_data,
)


def receipt() -> dict:
    from status_view import REQUIRED_GATES
    return {
        "run": "run-review", "challenge": "challenge-review",
        "finding": "Verified defect", "verified": True,
        "gates": {name: {"status": "pass"} for name in REQUIRED_GATES},
    }


class TestReviewReport(unittest.TestCase):
    def make_export(self, root: Path) -> Path:
        export = root / "export"
        (export / "objects").mkdir(parents=True)
        (export / "snapshot.json").write_text('{"version":1}')
        (export / "objects/78fde524d9562f6cb28df336512b3ca84bc8d72c72b47cd71f1a47516613ab4e").write_text(json.dumps(receipt()))
        (root / "lifecycle.json").write_text('{"elapsed_seconds":47.7242865}')
        return export

    def test_build_report_uses_shared_fail_closed_projection(self):
        from status_view import project_status
        data = {"receipt": receipt(), "lifecycle": {"evaluator_succeeded": True}}
        report = build_report(data)
        self.assertEqual(report, project_status(data))
        self.assertEqual(report["schema_version"], 2)
        self.assertTrue(report["verification"]["evidence_review_eligible"])
        self.assertEqual(report["recommendation"], "Needs more evidence")
        self.assertEqual(report["decision_state"], "Not established")

    def test_zero_gates_never_recommend_approval_or_readiness(self):
        empty = receipt()
        empty["gates"] = {}
        report = build_report({"receipt": empty})
        self.assertEqual(report["verification"]["gates"]["required_passed"], 0)
        self.assertEqual(report["verification"]["gates"]["required_total"], 11)
        self.assertFalse(report["verification"]["evidence_review_eligible"])
        self.assertEqual(report["recommendation"], "Needs more evidence")
        self.assertNotIn("Ready for review", json.dumps(report))

    def test_missing_lifecycle_is_unknown(self):
        report = build_report({"receipt": receipt()})
        self.assertEqual(report["execution"]["state"], "Unknown")

    def test_unknown_or_ambiguous_finding_requests_evidence(self):
        malformed = receipt()
        malformed["finding"] = "Magic result"
        report = build_report({"receipt": malformed})
        self.assertEqual(report["verification"]["finding"], "Unknown")
        self.assertEqual(report["recommendation"], "Needs more evidence")
        self.assertFalse(report["verification"]["evidence_review_eligible"])

    def test_all_three_formats_expose_the_same_historical_limits(self):
        report = build_report({"receipt": receipt()})
        md = to_markdown(report)
        text = to_plain_text(report)
        parsed = json.loads(to_json(report))
        self.assertIn("# GRRR Historical Replay Review", md)
        self.assertIn("Verified defect", md)
        self.assertIn("Current verification is absent", md)
        self.assertIn("Historical archive; current verification absent", text)
        self.assertIn("All authorities: false", text)
        self.assertFalse(parsed["scope"]["current_verification"])
        self.assertTrue(parsed["read_only"])

    def test_status_view_variants_use_same_projected_json(self):
        report = build_report({"receipt": receipt()})
        self.assertEqual(to_status_json(report), to_json(report))
        status_text = to_status_plain_text(report)
        status_md = to_status_markdown(report)
        self.assertIn("GRRR READ-ONLY STATUS", status_text)
        self.assertIn("# GRRR Read-only Status", status_md)
        self.assertIn("All authorities: false", status_text)
        self.assertIn("all projected action authorities are false", status_md)

    def test_plain_text_no_color_codes(self):
        report = build_report({"receipt": receipt()})
        text = to_plain_text(report)
        self.assertNotIn("\x1b[", text)
        self.assertIn("Verified defect", text)
        self.assertIn("Cost:            Unknown; no settled or spendable amount", text)

    def test_json_is_valid(self):
        report = build_report({"receipt": receipt()})
        parsed = json.loads(to_json(report))
        self.assertEqual(parsed["verification"]["finding"], "Verified defect")
        self.assertFalse(parsed["scope"]["live"])

    def test_unknown_cost_is_null_and_never_rendered_as_zero(self):
        empty = receipt()
        empty["cost_usd"] = float("nan")
        report = build_report({"receipt": empty})
        self.assertIsNone(report["budget"]["cost_usd"])
        self.assertEqual(report["budget"]["state"], "Unknown")
        text = to_plain_text(report)
        self.assertNotIn("$0.00", text)
        self.assertIn("Cost:            Unknown; no settled or spendable amount", text)

    def test_reported_zero_and_nonzero_do_not_become_spendability(self):
        for value, rendered in ((0, "$0.00"), (4.25, "$4.25")):
            with self.subTest(value=value):
                observed = receipt()
                observed["cost_usd"] = value
                report = build_report({"receipt": observed})
                self.assertEqual(report["budget"]["cost_usd"], float(value))
                self.assertEqual(report["budget"]["state"], "Reported")
                self.assertEqual(report["budget"]["spendability"], "Unknown")
                self.assertIn(rendered + " reported, unverified; not spendability", to_plain_text(report))

    def test_version_one_forged_reports_are_rejected_by_renderers(self):
        forged = {"schema_version": 1, "recommendation": "Approve"}
        for renderer in (to_json, to_markdown, to_plain_text):
            with self.subTest(renderer=renderer.__name__):
                with self.assertRaises(ReportError):
                    renderer(forged)

    def test_historical_hash_constants_are_not_authority(self):
        report = build_report({"receipt": receipt()})
        self.assertIsNone(report["evidence_identity"]["digest"])
        self.assertIn("provenance/currency not established", report["evidence_identity"]["basis"])

    def test_unknown_finding_is_projected_not_raised(self):
        malformed = receipt()
        malformed["finding"] = "Magic result"
        report = build_report({"receipt": malformed})
        self.assertEqual(report["verification"]["finding"], "Unknown")

    def test_vocabulary_sets_defined(self):
        self.assertIn("Verified defect", FINDINGS)
        self.assertIn("Completed", EXECUTION_STATES)
        self.assertIn("Needs more evidence", DECISIONS)
        self.assertIn("Stop", DECISIONS)

    def test_loader_rejects_duplicate_json_at_each_artifact_and_depth(self):
        object_name = "objects/78fde524d9562f6cb28df336512b3ca84bc8d72c72b47cd71f1a47516613ab4e"
        cases = (("snapshot.json", '{"version":1,"version":1}'),
                 (object_name, '{"cost_usd":null,"cost_usd":0}'),
                 (object_name, '{"cost_usd":null,"cost\\u005fusd":0}'),
                 (object_name, '{"verified":false,"verified":true}'),
                 (object_name, '{"gates":{"isolation":{"status":"fail","status":"pass"}}}'),
                 ("../lifecycle.json", '{"elapsed_seconds":null,"elapsed_seconds":0}'))
        for member, raw in cases:
            with self.subTest(member=member, raw=raw), tempfile.TemporaryDirectory(dir="/private/tmp") as directory:
                export = self.make_export(Path(directory))
                (export / member).write_text(raw)
                with self.assertRaises(ReportError):
                    load_replay_data(export)

    def test_loader_rejects_precision_loss_underflow_and_nonfinite_numbers(self):
        for token in ("1e-1000", "0.10000000000000001", "1e400", "0e9999999999999999999",
                      "NaN", "Infinity", "-Infinity"):
            with self.subTest(token=token), tempfile.TemporaryDirectory(dir="/private/tmp") as directory:
                export = self.make_export(Path(directory))
                obj = export / "objects/78fde524d9562f6cb28df336512b3ca84bc8d72c72b47cd71f1a47516613ab4e"
                obj.write_text('{"cost_usd":' + token + '}')
                with self.assertRaises(ReportError):
                    load_replay_data(export)

    def test_small_positive_cost_is_not_formatted_as_zero(self):
        report = build_report({"receipt": {"cost_usd": 0.001}})
        for renderer in (to_plain_text, to_markdown):
            self.assertIn("$0.001 reported", renderer(report))
            self.assertNotIn("$0.00 reported", renderer(report))

    def test_large_integer_cost_remains_exact_in_json_and_human_output(self):
        value = 9007199254740993
        report = build_report({"receipt": {"cost_usd": value}})
        self.assertEqual(json.loads(to_json(report))["budget"]["cost_usd"], value)
        self.assertIn("$9007199254740993.00 reported", to_plain_text(report))

    def test_cli_refuses_duplicate_cost_without_zero_or_traceback(self):
        with tempfile.TemporaryDirectory(dir="/private/tmp") as directory:
            app = Path(directory) / "app"
            for member in ("scripts", "research"):
                (app / member).mkdir(parents=True)
            shutil.copyfile(ROOT / "scripts/grrr-review", app / "scripts/grrr-review")
            for name in ("status_view.py", "review_report.py", "admission.py", "common.py"):
                shutil.copyfile(ROOT / "research" / name, app / "research" / name)
            export = app / "docs/evidence/replay-authority/replay-result/export-ca47bda9f47645b1910cba1449bcddfe"
            (export / "objects").mkdir(parents=True)
            (export / "snapshot.json").write_text('{}')
            (export / "objects/78fde524d9562f6cb28df336512b3ca84bc8d72c72b47cd71f1a47516613ab4e").write_text('{"cost_usd":null,"cost_usd":0}')
            for format in ("text", "json"):
                run = subprocess.run([sys.executable, "-B", str(app / "scripts/grrr-review"),
                                      "--view", "status", "--format", format],
                                     capture_output=True, text=True)
                self.assertEqual(run.returncode, 2)
                self.assertNotIn("$0", run.stdout + run.stderr)
                self.assertNotIn("Traceback", run.stderr)
                if format == "json":
                    self.assertFalse(json.loads(run.stdout)["actions_authorized"])
                else:
                    self.assertIn("GRRR_REPORT_REFUSED", run.stderr)


if __name__ == "__main__":
    unittest.main()
