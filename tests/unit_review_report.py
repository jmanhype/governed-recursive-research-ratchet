"""Tests for the review report generator."""

import json, sys, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "research"))

from review_report import (
    FINDINGS, EXECUTION_STATES, DECISIONS, ReportError,
    build_report, to_json, to_markdown, to_plain_text,
)


class TestReviewReport(unittest.TestCase):
    def test_build_report_from_real_evidence(self):
        evidence = ROOT / "docs/evidence/replay-authority/replay-result/export-ca47bda9f47645b1910cba1449bcddfe"
        if not evidence.exists():
            self.skipTest("evidence not present")
        from review_report import load_replay_data
        data = load_replay_data(evidence)
        report = build_report(data)
        self.assertEqual(report["finding"], "Verified defect")
        self.assertTrue(report["verified"])
        self.assertEqual(report["execution_state"], "Completed")

    def test_markdown_has_decision_summary_first(self):
        report = {"schema_version":1,"run":"test","challenge":"D011","execution_state":"Completed",
                  "finding":"Verified defect","verified":True,"gates_pass":9,"gates_total":9,
                  "elapsed_seconds":47.7,"cost_usd":0,"snapshot_sha256":"a"*64,
                  "decision":None,"decision_state":"Ready for review",
                  "recommendation":"Approve permanent contract admission"}
        md = to_markdown(report)
        self.assertIn("# GRRR Replay Review", md)
        self.assertIn("## Decision Summary", md)
        self.assertIn("Verified defect", md)
        self.assertIn("## Technical Verification", md)
        self.assertIn("## Full Audit", md)
        # Summary before technical
        self.assertLess(md.index("Decision Summary"), md.index("Technical Verification"))

    def test_plain_text_no_color_codes(self):
        report = {"schema_version":1,"run":"t","challenge":"c","execution_state":"Completed",
                  "finding":"Verified defect","verified":True,"gates_pass":9,"gates_total":9,
                  "elapsed_seconds":1.0,"cost_usd":0,"snapshot_sha256":"a"*64,
                  "decision":None,"decision_state":"Ready for review","recommendation":"Approve"}
        text = to_plain_text(report)
        self.assertNotIn("\x1b[", text)
        self.assertIn("Verified defect", text)

    def test_json_is_valid(self):
        report = {"schema_version":1,"run":"t","challenge":"c","execution_state":"Completed",
                  "finding":"Verified defect","verified":True,"gates_pass":9,"gates_total":9,
                  "elapsed_seconds":1.0,"cost_usd":0,"snapshot_sha256":"a"*64,
                  "decision":None,"decision_state":"Ready for review","recommendation":"Approve"}
        parsed = json.loads(to_json(report))
        self.assertEqual(parsed["finding"], "Verified defect")

    def test_unknown_finding_rejects(self):
        with self.assertRaises(ReportError):
            build_report({"receipt": {"finding": "Magic result", "verified": True}})

    def test_vocabulary_sets_defined(self):
        self.assertIn("Verified defect", FINDINGS)
        self.assertIn("Completed", EXECUTION_STATES)
        self.assertIn("Approve", DECISIONS)
        self.assertIn("Stop", DECISIONS)


if __name__ == "__main__":
    unittest.main()
