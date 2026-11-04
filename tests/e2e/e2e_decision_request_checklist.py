"""Focused offline checks for malformed, stale, and missing E2E requests."""

import copy
import json
from pathlib import Path
import tempfile
import unittest

from e2e_decision_request import DecisionRequestError, REVISIONS, validate, validate_bytes


ROOT = Path(__file__).resolve().parents[2]
REQUEST = ROOT / "docs/evidence/milestone-packet/E2E-DECISION-REQUEST.json"
MARKDOWN = ROOT / "docs/evidence/milestone-packet/E2E-DECISION-REQUEST.md"
INDEX = ROOT / "docs/evidence/milestone-packet/evidence-index.json"


class DecisionRequestSchema(unittest.TestCase):
    def baseline(self):
        return json.loads(REQUEST.read_bytes()), MARKDOWN.read_text(encoding="utf-8"), json.loads(INDEX.read_bytes())

    def assert_rejected(self, request, markdown=None, index=None, current_head=None):
        base_request, base_markdown, base_index = self.baseline()
        with self.assertRaises(DecisionRequestError):
            validate(request, markdown or base_markdown, index or base_index, current_head)
        self.assertIs(base_request["execution_authorized"], False)

    def test_baseline_is_schema_valid_but_blocked(self):
        request, markdown, index = self.baseline()
        result = validate(request, markdown, index, REVISIONS["story_current"])
        self.assertTrue(result["schema_valid"])
        self.assertEqual(result["decision"], "blocked")
        self.assertIs(result["execution_authorized"], False)
        self.assertTrue(validate_bytes(REQUEST.read_bytes(), markdown, INDEX.read_bytes(), REVISIONS["story_current"]))

    def test_malformed_json_fails_closed(self):
        for malformed in (b"", b"{", b"\xff", b'{"schema_version":1,'):
            with self.subTest(malformed=malformed):
                with self.assertRaises(DecisionRequestError):
                    validate_bytes(malformed, MARKDOWN.read_text(encoding="utf-8"), INDEX.read_bytes())

    def test_stale_revisions_and_head_fail_closed(self):
        request, _, _ = self.baseline()
        for field in REVISIONS:
            changed = copy.deepcopy(request)
            changed["revisions"][field] = "0" * 40
            with self.subTest(field=field):
                self.assert_rejected(changed)
        self.assert_rejected(request, current_head="0" * 40)

    def test_missing_required_inventory_fails_closed(self):
        request, _, index = self.baseline()
        cases = {
            "gate": lambda value: value["mandatory_gates"].pop(),
            "journey": lambda value: value["acceptance_criteria_journeys"].pop(),
            "artifact": lambda value: value["historical_evidence"]["artifacts"].pop("admission"),
            "seed": lambda value: value["workflow"]["seed_inventory"]["challenge_ids"].pop(),
            "partition": lambda value: value["workflow"]["seed_inventory"]["partitions"].pop("holdout"),
            "negative": lambda value: value["workflow"]["negative_cases"].pop(),
            "output": lambda value: value["outputs"]["fixed_paths"].pop(),
            "denial": lambda value: value["denied_until_separately_authorized"].pop(),
        }
        for name, mutate in cases.items():
            changed = copy.deepcopy(request)
            mutate(changed)
            with self.subTest(missing=name):
                self.assert_rejected(changed)
        changed_index = copy.deepcopy(index)
        changed_index["artifacts"].pop("contract")
        self.assert_rejected(request, index=changed_index)

    def test_evidence_identity_mismatch_fails_closed(self):
        request, _, index = self.baseline()
        changed_index = copy.deepcopy(index)
        changed_index["artifacts"]["contract"]["sha256"] = "0" * 64
        self.assert_rejected(request, index=changed_index)
        changed_request = copy.deepcopy(request)
        changed_request["historical_evidence"]["artifacts"]["contract"]["revision"] = "1" * 40
        self.assert_rejected(changed_request)

    def test_no_execution_authority_can_be_inferred(self):
        request, markdown, _ = self.baseline()
        mutations = (
            ("flag", {**request, "execution_authorized": True}),
            ("approved", {**request, "approved": True}),
            ("allow", {**request, "allow_execution": True}),
            ("run", {**request, "run_now": True}),
            ("nested", {**request, "workflow": {**request["workflow"], "launch": True}}),
        )
        for name, changed in mutations:
            with self.subTest(mutation=name):
                self.assert_rejected(changed)
        with self.assertRaises(DecisionRequestError):
            validate(request, markdown.replace("`execution_authorized: false`", "`execution_authorized: true`"),
                     json.loads(INDEX.read_bytes()))

    def test_stale_or_missing_markdown_fails_closed(self):
        request, markdown, index = self.baseline()
        for name, changed in (
            ("empty", ""),
            ("missing-heading", markdown.replace("## Required preflight", "## Optional preflight")),
            ("stale-story", markdown.replace(REVISIONS["story_current"], "0" * 40)),
            ("missing-budget", markdown.replace("$150, 24 execution hours, 180 review minutes", "unbounded")),
        ):
            with self.subTest(markdown=name):
                with self.assertRaises(DecisionRequestError):
                    validate(request, changed, index)

    def test_output_destinations_are_reserved_and_safe(self):
        request, _, _ = self.baseline()
        outputs = request["outputs"]
        self.assertEqual(outputs["state"], "reserved-not-created")
        self.assertFalse((ROOT / outputs["root"]).exists())
        for relative in outputs["fixed_paths"]:
            path = relative.lower()
            self.assertFalse(path.startswith(("/", "..", "/library/grrr")))
            self.assertNotIn("..", path)
        self.assertIn("{seed_id}", outputs["per_seed_path_template"])
        self.assertIn("{case_id}", outputs["per_negative_path_template"])

    def test_files_never_need_runtime_or_protected_paths(self):
        source = Path(__file__).with_name("e2e_decision_request.py").read_text(encoding="utf-8")
        self.assertNotIn("import research", source)
        self.assertNotIn("os.access", source)
        self.assertNotIn("Path.read_", source)
        self.assertNotIn("Path.write_", source)
        self.assertIn("if not joined.is_relative_to(root)", source)


if __name__ == "__main__":
    unittest.main(verbosity=2)
