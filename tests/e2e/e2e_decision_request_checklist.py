"""Focused offline checks for malformed, stale, and missing E2E requests."""

import copy
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
import unittest

from e2e_decision_request import (
    DecisionRequestError, REVISIONS, _load_package, _validate_package, validate_git,
)


ROOT = Path(__file__).resolve().parents[2]
REQUEST = ROOT / "docs/evidence/milestone-packet/E2E-DECISION-REQUEST.json"
MARKDOWN = ROOT / "docs/evidence/milestone-packet/E2E-DECISION-REQUEST.md"
INDEX = ROOT / "docs/evidence/milestone-packet/evidence-index.json"
RUNTIME_BASE = REVISIONS["immutable_runtime_base"]
OLD_PACKAGE = "dfb9d6daa1e8b259445c4fb1e22e28373481729a"
PRE_RUNTIME_PACKAGE = REVISIONS["historical_evidence_base"]


def git(*arguments: str) -> str:
    value = subprocess.run(("git", "-C", str(ROOT), *arguments), stdout=subprocess.PIPE, check=True).stdout
    return value.decode("ascii").strip()


def head() -> str:
    return git("rev-parse", "HEAD")


class DecisionRequestSchema(unittest.TestCase):
    def baseline_package(self):
        return _load_package(RUNTIME_BASE, head(), ROOT)

    def package_with(self, request=None, markdown=None, index=None):
        package = self.baseline_package()
        package.request_bytes = request if request is not None else package.request_bytes
        package.markdown_bytes = markdown if markdown is not None else package.markdown_bytes
        package.index_bytes = index if index is not None else package.index_bytes
        return package

    def assert_rejected(self, request=None, markdown=None, index=None):
        package = self.package_with(request=request, markdown=markdown, index=index)
        with self.assertRaises(DecisionRequestError):
            _validate_package(package)
        self.assertFalse(json.loads(package.request_bytes)["execution_authorized"])

    def test_baseline_is_schema_valid_but_blocked(self):
        package = self.baseline_package()
        result = _validate_package(package)
        self.assertTrue(result["schema_valid"])
        self.assertEqual(result["decision"], "blocked")
        self.assertIs(result["execution_authorized"], False)
        self.assertEqual(result["runtime_base"], RUNTIME_BASE)
        self.assertEqual(result["package_commit"], package.package_commit)
        self.assertEqual(result["request_id"], "GRRR-6sso-exact-target-e2e-v1")

    def test_explicit_runtime_and_package_bindings_use_git_evidence(self):
        package = self.baseline_package()
        result = validate_git(RUNTIME_BASE, package.package_commit, ROOT)
        request_hash = sha256(REQUEST.read_bytes()).hexdigest()
        markdown_hash = sha256(MARKDOWN.read_bytes()).hexdigest()
        self.assertEqual(result["request_sha256"], request_hash)
        self.assertEqual(result["markdown_sha256"], markdown_hash)
        self.assertNotEqual(result["request_blob_git_id"], result["markdown_blob_git_id"])

    def test_missing_either_explicit_binding_fails_closed(self):
        current = head()
        for runtime, package in ((None, current), (RUNTIME_BASE, None), ("", current), (RUNTIME_BASE, "")):
            with self.subTest(runtime=runtime, package=package):
                with self.assertRaises(DecisionRequestError):
                    validate_git(runtime, package, ROOT)
        script = Path(__file__).with_name("e2e_decision_request.py")
        for arguments in ([], ["--runtime-base", RUNTIME_BASE], ["--package-commit", current]):
            with self.subTest(arguments=arguments):
                completed = subprocess.run((sys.executable, str(script), *arguments), stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
                self.assertEqual(completed.returncode, 2)

    def test_mismatched_forged_or_wrong_ancestry_package_fails_closed(self):
        with self.assertRaises(DecisionRequestError):
            validate_git(OLD_PACKAGE, head(), ROOT)
        with self.assertRaises(DecisionRequestError):
            validate_git(RUNTIME_BASE, OLD_PACKAGE, ROOT)
        with self.assertRaises(DecisionRequestError):
            validate_git(RUNTIME_BASE, PRE_RUNTIME_PACKAGE, ROOT)
        with self.assertRaises(DecisionRequestError):
            validate_git(RUNTIME_BASE, "0" * 40, ROOT)

    def test_self_referential_package_claim_fails_closed(self):
        package = self.baseline_package()
        request = json.loads(package.request_bytes)
        request["package_commit"] = package.package_commit
        self.assert_rejected(json.dumps(request).encode("ascii"))

    def test_malformed_json_fails_closed(self):
        for malformed in (b"", b"{", b"\xff", b'{"schema_version":1,'):
            with self.subTest(malformed=malformed):
                with self.assertRaises(DecisionRequestError):
                    _validate_package(self.package_with(request=malformed))

    def test_stale_revisions_and_head_fail_closed(self):
        request = json.loads(self.baseline_package().request_bytes)
        for field in REVISIONS:
            changed = copy.deepcopy(request)
            changed["revisions"][field] = "0" * 40
            with self.subTest(field=field):
                self.assert_rejected(changed)
        changed_policy = copy.deepcopy(request)
        changed_policy["revision_policy"]["immutable_runtime_base_must_match"] = "0" * 40
        self.assert_rejected(changed_policy)

    def test_missing_required_inventory_fails_closed(self):
        package = self.baseline_package()
        request, index = json.loads(package.request_bytes), json.loads(package.index_bytes)
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
        package = self.baseline_package()
        request, index = json.loads(package.request_bytes), json.loads(package.index_bytes)
        changed_index = copy.deepcopy(index)
        changed_index["artifacts"]["contract"]["sha256"] = "0" * 64
        self.assert_rejected(request, index=changed_index)
        changed_request = copy.deepcopy(request)
        changed_request["historical_evidence"]["artifacts"]["contract"]["revision"] = "1" * 40
        self.assert_rejected(changed_request)

    def test_no_execution_authority_can_be_inferred(self):
        package = self.baseline_package()
        request, markdown = json.loads(package.request_bytes), package.markdown_bytes.decode("utf-8")
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
            _validate_package(self.package_with(
                markdown=markdown.replace("`execution_authorized: false`", "`execution_authorized: true`")))

    def test_stale_or_missing_markdown_fails_closed(self):
        package = self.baseline_package()
        markdown = package.markdown_bytes.decode("utf-8")
        for name, changed in (
            ("empty", ""),
            ("missing-heading", markdown.replace("## Required preflight", "## Optional preflight")),
            ("stale-runtime-base", markdown.replace(REVISIONS["immutable_runtime_base"], "0" * 40)),
            ("missing-external-binding", markdown.replace("The package commit is intentionally absent from both request artifacts", "Package binding omitted")),
            ("missing-budget", markdown.replace("$150, 24 execution hours, 180 review minutes", "unbounded")),
        ):
            with self.subTest(markdown=name):
                with self.assertRaises(DecisionRequestError):
                    _validate_package(self.package_with(markdown=changed))

    def test_output_destinations_are_reserved_and_safe(self):
        request = json.loads(self.baseline_package().request_bytes)
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
