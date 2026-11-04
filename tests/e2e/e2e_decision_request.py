"""Offline schema and consistency validator for the exact-target E2E request.

This module never imports runtime code and never launches a VM. Validation is
intentionally strict: malformed, stale, missing, or authority-bearing requests
raise DecisionRequestError rather than producing a softer warning.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import PurePosixPath
import re
import subprocess
import sys
from typing import Any


REQUEST_FIELDS = frozenset((
    "schema_version", "record_type", "request_id", "created_at",
    "decision_state", "execution_authorized", "story_id", "revisions",
    "revision_policy", "historical_evidence", "mandatory_gates",
    "acceptance_criteria_journeys", "workflow", "budgets", "outputs",
    "review_requirement", "denied_until_separately_authorized",
    "rollback_and_stop_behavior", "self_hash_policy",
))
REVISIONS = {
    "historical_evidence_base": "845b47d221773eb4157491d35f57dce47ce8afe6",
    "admission_fail_closed_fix": "710e6fb1affa366da6ca4c855f49805d3bdb944d",
    "epic_current": "0b2365e30ab5858cb419f4f4ce9b2ce001850541",
    "immutable_runtime_base": "c928791cdaa72df91e61002c40317457b543b032",
    "main_observed_not_target": "c2970356436531565711fb3c2df24eb91c3ed510",
}
REVISION_POLICY = {
    "immutable_runtime_base_must_match": REVISIONS["immutable_runtime_base"],
    "epic_head_must_match": REVISIONS["epic_current"],
    "admission_fix_must_be_ancestor": True,
    "package_commit_must_descend_from_runtime_base": True,
    "package_commit_binding_is_external": True,
    "changed_request_hash_requires_new_review": True,
}
REQUEST_PATH = "docs/evidence/milestone-packet/E2E-DECISION-REQUEST.json"
MARKDOWN_PATH = "docs/evidence/milestone-packet/E2E-DECISION-REQUEST.md"
INDEX_PATH = "docs/evidence/milestone-packet/evidence-index.json"
GATE_IDS = ("source_environment_identity", "isolation", "protected_asset_integrity", "baseline_correctness", "trusted_observation", "independent_replay", "specification_traceability", "evidence_integrity_currency", "budget_state", "reviewer_outcome", "action_specific_human_approval")
JOURNEY_IDS = ("AC1", "AC2", "AC3", "AC4", "AC5", "AC6", "AC7")
SEED_IDS = ("GRRR-VC-D001", "GRRR-VC-D002", "GRRR-VC-D003", "GRRR-VC-D004", "GRRR-VC-D005", "GRRR-VC-D006", "GRRR-VC-D007", "GRRR-VC-D008", "GRRR-VC-D009", "GRRR-VC-D010", "GRRR-VC-D011", "GRRR-VC-D012", "GRRR-VC-D013", "GRRR-VC-D014", "GRRR-VC-D015", "GRRR-VC-D016", "GRRR-VC-D017", "GRRR-VC-D018", "GRRR-VC-D019", "GRRR-VC-D020", "GRRR-VC-D021", "GRRR-VC-D022", "GRRR-VC-D023", "GRRR-VC-D024", "GRRR-VC-C001", "GRRR-VC-C002", "GRRR-VC-C003", "GRRR-VC-C004", "GRRR-VC-C005", "GRRR-VC-C006", "GRRR-VC-C007", "GRRR-VC-C008")
NEGATIVE_IDS = ("forged_identity", "forged_evidence", "stale_approval", "missing_mandatory_gate", "unknown_budget", "exhausted_budget", "protected_write_attempt", "ambiguous_specification", "tampered_export", "truncated_export", "missing_export", "duplicate_authorization", "duplicate_contract", "unusable_admission_registry")
FIXED_OUTPUT_PATHS = ("PREFLIGHT.json", "VM-IDENTITY.json", "EVALUATOR-IDENTITY.json", "LEDGER-ANCHOR.json", "SEED-INVENTORY.json", "ADMISSION-GRANT.json", "ADMISSION-RECEIPT.json", "NEGATIVE-MATRIX.json", "STOP-RECOVERY.json", "COST-RECONCILIATION.json", "ACCESSIBILITY-WALKTHROUGH.md", "OPERATOR-TRANSCRIPT.md", "FINAL-REPORT.md", "REVIEW-APPROVAL.md", "SHA256SUMS")
DENIALS = ("/Library/GRRR access", "protected read or write", "VM or QEMU launch", "replay", "admission", "promotion", "production mutation", "external Jev or network call", "secret or credential access", "stash pop", "merge", "push", "automatic budget increase", "harness adaptation or autonomous patch generation")
WORKFLOW_FIELDS = frozenset((
    "preflight", "vm", "evaluator", "ledger", "seed_inventory", "replay",
    "admission", "negative_cases", "stop_and_recovery",
    "cost_and_review_time_reconciliation", "accessibility_walkthrough",
))
MARKDOWN_REQUIRED = (
    "# GRRR-6sso exact-target full E2E decision request",
    "`execution_authorized: false`",
    "## Exact runtime base and external package binding",
    "The package commit is intentionally absent from both request artifacts",
    "## Immutable historical evidence identities",
    "## Required preflight",
    "## VM, evaluator, and ledger",
    "## Seed inventory, replay, and admission",
    "## Negative cases, stop, and recovery",
    "## Independent cost and accessibility closure",
    "## Immutable output destinations",
    "## Review, denials, and rollback",
    "## Final request",
    "$50, 6 execution hours, 60 review minutes",
    "$150, 24 execution hours, 180 review minutes",
)
AUTHORITY_KEY_RE = re.compile(r"(?:^|_)(?:authoriz|authoris|approv|allow|enabl|execut|run|launch|replay|admit|promot|mutat|push|merge)(?:$|_)", re.I)
SHA1_RE = re.compile(r"[0-9a-f]{40}\Z")
SHA256_RE = re.compile(r"[0-9a-f]{64}\Z")


class DecisionRequestError(ValueError):
    """Raised when the request cannot safely be presented for human review."""


class GitPackageEvidence:
    """Read only immutable Git objects; never trust checkout-local claims."""

    def __init__(self, repository: Any) -> None:
        self.repository = repository

    def _git(self, *arguments: str, check: bool = True) -> subprocess.CompletedProcess[bytes]:
        result = subprocess.run(
            ("git", "-C", str(self.repository), *arguments),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if check and result.returncode != 0:
            raise DecisionRequestError("Git object evidence is missing or unreadable")
        return result

    def commit_exists(self, revision: str) -> bool:
        return self._git("cat-file", "-e", revision + "^{commit}", check=False).returncode == 0

    def is_ancestor(self, ancestor: str, descendant: str) -> bool:
        return self._git("merge-base", "--is-ancestor", ancestor, descendant, check=False).returncode == 0

    def blob(self, revision: str, path: str) -> bytes:
        return self._git("show", revision + ":" + path).stdout

    def blob_id(self, revision: str, path: str) -> str:
        value = self._git("rev-parse", revision + ":" + path).stdout.decode("ascii").strip()
        if not SHA1_RE.fullmatch(value):
            raise DecisionRequestError("Git request blob identity is malformed")
        return value


class ResolvedPackage:
    """Immutable package bytes resolved from two explicit commit arguments."""

    def __init__(self, repository: Any, runtime_base: str, package_commit: str,
                 request_bytes: bytes, markdown_bytes: bytes, index_bytes: bytes) -> None:
        self.repository = repository
        self.runtime_base = runtime_base
        self.package_commit = package_commit
        self.request_bytes = request_bytes
        self.markdown_bytes = markdown_bytes
        self.index_bytes = index_bytes


def _keys(value: dict, expected: set[str], label: str) -> None:
    if not isinstance(value, dict) or set(value) != expected:
        raise DecisionRequestError(label + " fields differ")


def _walk(value: Any, path: str = "$"):
    """Yield every scalar path and value without interpreting artifact text."""
    if isinstance(value, dict):
        for key, child in value.items():
            yield from _walk(child, path + "." + str(key))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _walk(child, f"{path}[{index}]")
    else:
        yield path, value


def _only_explicit_execution_authority(request: dict) -> None:
    if request.get("execution_authorized") is not False:
        raise DecisionRequestError("execution_authorized must be exactly false")
    for key, value in _walk(request):
        leaf = key.rsplit(".", 1)[-1]
        if AUTHORITY_KEY_RE.search(leaf) and leaf != "execution_authorized":
            raise DecisionRequestError("additional authority key " + leaf)
    text = json.dumps(request, sort_keys=True, separators=(",", ":"))
    if re.search(r'"(?:approved|allow_execution|execute|execution_started)"\s*:\s*true', text, re.I):
        raise DecisionRequestError("request contains an execution-enabling value")


def _identities(index: dict) -> dict:
    _keys(index, {"base_revision", "scope", "artifacts"}, "evidence index")
    if (index.get("base_revision") != REVISIONS["historical_evidence_base"] or
            index.get("scope") != "historical-provenance-only" or
            not isinstance(index.get("artifacts"), dict) or len(index["artifacts"]) != 19):
        raise DecisionRequestError("evidence index identity differs")
    for name, item in index["artifacts"].items():
        _keys(item, {"path", "revision", "sha256"}, "evidence item " + name)
        if (not SHA1_RE.fullmatch(str(item["revision"])) or
                not SHA256_RE.fullmatch(str(item["sha256"])) or
                not isinstance(item["path"], str) or
                item["path"].startswith(("/", "..")) or "\\" in item["path"] or
                any(part in ("", ".", "..") for part in item["path"].split("/"))):
            raise DecisionRequestError("evidence item " + name + " is malformed")
    return index["artifacts"]


def _safe_output(root: str, relative: str) -> PurePosixPath:
    if not isinstance(relative, str) or "\\" in relative or "\x00" in relative:
        raise DecisionRequestError("unsafe output destination")
    path = PurePosixPath(relative)
    if path.is_absolute() or any(part in ("", ".", "..") for part in path.parts):
        raise DecisionRequestError("unsafe output destination " + relative)
    joined = PurePosixPath(root) / path
    if not joined.is_relative_to(root) or "/Library/GRRR" in str(joined):
        raise DecisionRequestError("output escapes reserved root")
    return joined


def _validate_request_identity(request: dict, runtime_base: str) -> None:
    """Validate immutable request identity, authority surface, and revisions."""
    _keys(request, set(REQUEST_FIELDS), "request")
    if (request["schema_version"] != 1 or
            request["record_type"] != "grrr-e2e-authorization-decision-request-v1" or
            request["request_id"] != "GRRR-6sso-exact-target-e2e-v1" or
            request["story_id"] != "GRRR-6sso" or
            request["decision_state"] != "blocked-awaiting-independent-review-and-human-authorization"):
        raise DecisionRequestError("request identity differs")
    _only_explicit_execution_authority(request)
    _keys(request["revisions"], set(REVISIONS), "revisions")
    for name, expected in REVISIONS.items():
        if request["revisions"][name] != expected:
            raise DecisionRequestError("stale revision " + name)
    _keys(request["revision_policy"], set(REVISION_POLICY), "revision policy")
    for name, expected in REVISION_POLICY.items():
        if request["revision_policy"][name] != expected:
            raise DecisionRequestError("revision policy differs: " + name)
    if runtime_base != REVISIONS["immutable_runtime_base"]:
        raise DecisionRequestError("runtime base differs from immutable request binding")
    for key, _value in _walk(request):
        leaf = key.rsplit(".", 1)[-1]
        if "package" in leaf and "commit" in leaf:
            raise DecisionRequestError("package commit must be bound externally, not claimed in JSON")


def _validate_historical(request: dict, evidence_index: Any, git: GitPackageEvidence) -> None:
    """Require exact parity with the immutable 19-artifact evidence index."""
    historical = request["historical_evidence"]
    _keys(historical, {"index_path", "scope", "base_revision", "artifact_count", "limit", "artifacts"}, "historical evidence")
    artifacts = _identities(evidence_index)
    if (historical["index_path"] != INDEX_PATH or
            historical["scope"] != "historical-provenance-only" or
            historical["base_revision"] != REVISIONS["historical_evidence_base"] or
            historical["artifact_count"] != 19 or historical["artifacts"] != artifacts):
        raise DecisionRequestError("historical evidence inventory is stale or mismatched")
    base = REVISIONS["historical_evidence_base"]
    if not git.commit_exists(base):
        raise DecisionRequestError("historical evidence base is unavailable")
    for name, item in artifacts.items():
        if not git.commit_exists(item["revision"]) or not git.is_ancestor(item["revision"], base):
            raise DecisionRequestError("historical evidence revision lacks Git ancestry: " + name)
        data = git.blob(item["revision"], item["path"])
        if sha256(data).hexdigest() != item["sha256"] or data != git.blob(base, item["path"]):
            raise DecisionRequestError("historical evidence bytes differ: " + name)


def _validate_gates(request: dict) -> None:
    """Require the complete 11-gate set."""
    gates = request["mandatory_gates"]
    if (not isinstance(gates, list) or len(gates) != 11 or
            [item.get("id") for item in gates] != list(GATE_IDS) or
            any(item.get("status") != "required-not-run" or not item.get("evidence_required") for item in gates)):
        raise DecisionRequestError("mandatory gate inventory differs")


def _validate_journeys(request: dict) -> None:
    """Require the complete seven-journey set."""
    journeys = request["acceptance_criteria_journeys"]
    if (not isinstance(journeys, list) or len(journeys) != 7 or
            [item.get("id") for item in journeys] != list(JOURNEY_IDS) or
            any(item.get("status") != "blocked-not-run" or not item.get("evidence_required") for item in journeys)):
        raise DecisionRequestError("AC journey inventory differs")


def _validate_seed_inventory(request: dict) -> None:
    """Require exact seed identity, partitions, and corpus thresholds."""
    _keys(request["workflow"], set(WORKFLOW_FIELDS), "workflow")
    inventory = request["workflow"]["seed_inventory"]
    partitions = inventory.get("partitions", {})
    partition_ids = [value for values in partitions.values() for value in values]
    if (inventory.get("challenge_ids") != list(SEED_IDS) or
            sorted(partition_ids) != sorted(SEED_IDS) or len(set(partition_ids)) != 32 or
            inventory.get("minimum_representative_required") < 20 or
            inventory.get("defect_count") != 24 or inventory.get("clean_negative_count") != 8 or
            inventory.get("critical_count") != 17):
        raise DecisionRequestError("seed inventory differs")


def _validate_negative_and_denials(request: dict) -> None:
    """Require every adversarial case and denied action to remain present."""
    negative = request["workflow"]["negative_cases"]
    if (not isinstance(negative, list) or len(negative) != len(NEGATIVE_IDS) or
            [item.get("id") for item in negative] != list(NEGATIVE_IDS) or
            any(not item.get("expected") for item in negative)):
        raise DecisionRequestError("negative-case inventory differs")
    denials = request["denied_until_separately_authorized"]
    if (not isinstance(denials, list) or len(denials) != len(set(denials)) or
            denials != list(DENIALS)):
        raise DecisionRequestError("denial inventory differs")


def _validate_budgets(request: dict) -> None:
    """Require bounded incremental and cumulative accounting."""
    budgets = request["budgets"]
    _keys(budgets, {"currency", "proposed_incremental_maxima", "cumulative_ceilings", "current_cumulative_spend", "automatic_increase", "rules"}, "budgets")
    if (budgets["currency"] != "USD" or budgets["current_cumulative_spend"] != "unknown" or
            budgets["automatic_increase"] is not False or
            budgets["proposed_incremental_maxima"] != {"usd": 50, "execution_hours": 6, "review_minutes": 60} or
            budgets["cumulative_ceilings"] != {"usd_including_poc": 150, "execution_hours": 24, "review_minutes": 180}):
        raise DecisionRequestError("budget ceilings differ")


def _validate_outputs(request: dict) -> None:
    """Require exact reserved write-once destinations."""
    outputs = request["outputs"]
    _keys(outputs, {"root", "state", "mutability", "fixed_paths", "per_seed_path_template", "per_negative_path_template", "checksum_policy"}, "outputs")
    destinations = []
    root = outputs["root"]
    if outputs["state"] != "reserved-not-created" or outputs["mutability"] != "write-once-then-immutable":
        raise DecisionRequestError("output state differs")
    if outputs["fixed_paths"] != list(FIXED_OUTPUT_PATHS):
        raise DecisionRequestError("fixed output inventory differs")
    for relative in outputs["fixed_paths"]:
        destinations.append(_safe_output(root, relative))
    for template, ids in ((outputs["per_seed_path_template"], SEED_IDS),
                          (outputs["per_negative_path_template"], NEGATIVE_IDS)):
        if template.count("{") != 1 or template.count("}") != 1:
            raise DecisionRequestError("output template is not exact")
        for identifier in ids:
            destinations.append(_safe_output(root, template.format(seed_id=identifier, case_id=identifier)))
    if len(destinations) != len(set(destinations)):
        raise DecisionRequestError("output destinations collide")


def _validate_markdown(request: dict, markdown: str) -> None:
    """Require the human surface to carry the same blocked commitments."""
    if not isinstance(markdown, str) or any(term not in markdown for term in MARKDOWN_REQUIRED):
        raise DecisionRequestError("Markdown request is missing required content")
    if re.search(r"execution_authorized\s*:\s*true", markdown, re.I):
        raise DecisionRequestError("Markdown attempts to infer execution authority")
    for revision in REVISIONS.values():
        if revision not in markdown:
            raise DecisionRequestError("Markdown revision binding is stale")


def _validate_package(package: ResolvedPackage) -> dict:
    """Validate only bytes already resolved from immutable Git objects."""
    try:
        request = json.loads(package.request_bytes)
        index = json.loads(package.index_bytes)
        markdown = package.markdown_bytes.decode("utf-8")
    except (UnicodeDecodeError, ValueError, RecursionError) as exc:
        raise DecisionRequestError("malformed JSON request or index") from exc
    git = GitPackageEvidence(package.repository)
    _validate_request_identity(request, package.runtime_base)
    _validate_historical(request, index, git)
    _validate_gates(request)
    _validate_journeys(request)
    _validate_seed_inventory(request)
    _validate_negative_and_denials(request)
    _validate_budgets(request)
    _validate_outputs(request)
    _validate_markdown(request, markdown)
    request_hash = sha256(package.request_bytes).hexdigest()
    markdown_hash = sha256(package.markdown_bytes).hexdigest()
    return {
        "schema_valid": True,
        "decision": "blocked",
        "execution_authorized": False,
        "request_id": request["request_id"],
        "runtime_base": package.runtime_base,
        "package_commit": package.package_commit,
        "request_blob_git_id": git.blob_id(package.package_commit, REQUEST_PATH),
        "markdown_blob_git_id": git.blob_id(package.package_commit, MARKDOWN_PATH),
        "request_sha256": request_hash,
        "markdown_sha256": markdown_hash,
    }


def _load_package(runtime_base: str | None, package_commit: str | None,
                  repository: Any) -> ResolvedPackage:
    """Resolve and bind the package solely from explicit Git commit arguments."""
    if runtime_base is None or package_commit is None:
        raise DecisionRequestError("runtime base and package commit are both required")
    if (not SHA1_RE.fullmatch(str(runtime_base)) or
            not SHA1_RE.fullmatch(str(package_commit))):
        raise DecisionRequestError("runtime base or package commit is malformed")
    if str(runtime_base) != REVISIONS["immutable_runtime_base"]:
        raise DecisionRequestError("runtime base differs from immutable request binding")
    git = GitPackageEvidence(repository)
    if not git.commit_exists(str(runtime_base)) or not git.commit_exists(str(package_commit)):
        raise DecisionRequestError("runtime base or package commit is unavailable")
    if not git.is_ancestor(str(runtime_base), str(package_commit)):
        raise DecisionRequestError("runtime base is not an ancestor of package commit")
    return ResolvedPackage(
        repository=repository,
        runtime_base=str(runtime_base),
        package_commit=str(package_commit),
        request_bytes=git.blob(str(package_commit), REQUEST_PATH),
        markdown_bytes=git.blob(str(package_commit), MARKDOWN_PATH),
        index_bytes=git.blob(str(package_commit), INDEX_PATH),
    )


def validate_git(runtime_base: str | None, package_commit: str | None,
                 repository: Any = ".") -> dict:
    """Resolve package bytes from Git and return blocked review-only state."""
    package = _load_package(runtime_base, package_commit, repository)
    return _validate_package(package)


def main() -> int:
    """Print only schema validity and blocked state; never launch work."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runtime-base", required=True)
    parser.add_argument("--package-commit", required=True)
    parser.add_argument("--repository", default=".")
    args = parser.parse_args()
    try:
        result = validate_git(args.runtime_base, args.package_commit, args.repository)
    except (OSError, UnicodeError, DecisionRequestError) as exc:
        print("FAIL: " + str(exc), file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
