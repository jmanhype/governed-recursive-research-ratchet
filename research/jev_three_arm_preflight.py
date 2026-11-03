"""Prepare, but never execute, the approved three-arm Jev evaluation."""

import argparse
import hashlib
import json
import os
import stat
import sys
from pathlib import Path
from typing import Any, Dict, Tuple

import evaluation_plan_v2


ROOT = Path(__file__).resolve().parent.parent
PLAN_PATH = ROOT / "corpus" / "evaluation-plan-v2-proposed.json"
APPROVAL_PATH = ROOT / "docs/evidence/jev-selector-measurement/THREE-ARM-DESIGN-APPROVAL.md"
PILOT_PATH = ROOT / "docs/evidence/jev-selector-measurement/run-20261103T201719Z"
TRUTH_PATH = ROOT / "corpus/protected/truth.json"
MANIFEST_PATH = ROOT / "corpus/manifest.json"

APPROVAL_SHA256 = (
    "926e1c04b49f0cb1dbfac9c5eb2775daa3182bda77939413b36297061146a8e6"
)
PILOT_EVENTS_SHA256 = (
    "44cefd57b7ac65c811e2860a2bf37dfc54c41bb0ba9bed6ef93d475dca316d98"
)
PILOT_REPORT_SHA256 = (
    "59a9a21282ae2f4b8fa213f43d0fa1d652bee07d0aad2bf6bfc45535fb436c0f"
)


class PreflightRefused(RuntimeError):
    """A design, evidence, or output boundary failed before execution."""


def _sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _read_bytes(path: Path, expected_sha: str, label: str) -> bytes:
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise PreflightRefused(f"{label} unavailable") from exc
    if _sha256(raw) != expected_sha:
        raise PreflightRefused(f"{label} hash differs")
    return raw


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_bytes())
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise PreflightRefused(f"{path.name} is unavailable or invalid") from exc


def _validate_approval(path: Path = APPROVAL_PATH) -> None:
    raw = _read_bytes(path, APPROVAL_SHA256, "design approval")
    text = raw.decode("utf-8")
    required = (
        "HASH_BOOTSTRAP_NARROW_REVIEW: APPROVED",
        "This is **design approval only**. It does not authorize execution.",
        "97ec4b8ccc34b3fc4da4fcfbef33b49bbb3f4f1c445cfecdb752715ddf034be1",
    )
    if not all(value in text for value in required):
        raise PreflightRefused("design approval markers differ")


def _validate_pilot(pilot_path: Path = PILOT_PATH) -> Dict[str, Any]:
    _read_bytes(
        pilot_path / "events.jsonl", PILOT_EVENTS_SHA256, "pilot events"
    )
    _read_bytes(
        pilot_path / "report.json", PILOT_REPORT_SHA256, "pilot report"
    )
    report = _load_json(pilot_path / "report.json")
    attempts = report.get("attempts", {})
    usage = report.get("usage", {})
    if (report.get("run_id") != "6cf35082f34a4149b67293c7b53d9740"
            or report.get("status") != "complete"
            or attempts.get("attempted_calls") != 32
            or attempts.get("returned_responses") != 32
            or attempts.get("retry_count") != 0
            or usage.get("input_tokens") != 12548
            or usage.get("output_tokens") != 736
            or usage.get("observation_complete") is not True):
        raise PreflightRefused("pilot evidence differs")
    return report


def _validate_truth_and_budget(plan: Dict[str, Any]) -> None:
    truth_hash = _sha256(TRUTH_PATH.read_bytes())
    manifest = _load_json(MANIFEST_PATH)
    pinned = plan["corpus"]["protected_truth_sha256"]
    if (pinned != truth_hash
            or manifest.get("artifacts", {}).get("protected/truth.json") != truth_hash):
        raise PreflightRefused("protected truth binding differs")

    budget = plan["budget"]
    checks = (
        budget["confirmatory_jev_scoring_calls"] == 3 * 32 == 96,
        budget["cumulative_call_ceiling_including_exploratory"]
        == budget["observed_exploratory_calls"] + 96 == 128,
        budget["projected_confirmatory_input_tokens_from_pilot"]
        == 3 * budget["observed_exploratory_input_tokens"] == 37644,
        budget["projected_confirmatory_output_tokens_from_pilot"]
        == 3 * budget["observed_exploratory_output_tokens"] == 2208,
        budget["projected_cumulative_input_tokens"]
        == budget["observed_exploratory_input_tokens"] + 37644 == 50192,
        budget["projected_cumulative_output_tokens"]
        == budget["observed_exploratory_output_tokens"] + 2208 == 2944,
        budget["hard_cumulative_input_token_ceiling"] == 60000,
        budget["hard_cumulative_output_token_ceiling"] == 4000,
    )
    if not all(checks):
        raise PreflightRefused("budget arithmetic differs")


def _safe_output(path: Path) -> Tuple[int, Path]:
    raw = os.fspath(path)
    if not isinstance(raw, str) or "\0" in raw or raw.startswith("//"):
        raise PreflightRefused("output path is unsafe")
    supplied = Path(raw)
    if not supplied.is_absolute() or ".." in supplied.parts:
        raise PreflightRefused("output path is unsafe")
    absolute = Path(os.path.abspath(raw))
    if (absolute == Path("/Library/GRRR")
            or Path("/Library/GRRR") in absolute.parents):
        raise PreflightRefused("protected output path is refused")
    if len(absolute.parts) < 2 or absolute.name in ("", ".", ".."):
        raise PreflightRefused("output filename is unsafe")

    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_CLOEXEC", 0)
    if not hasattr(os, "O_NOFOLLOW"):
        raise PreflightRefused("safe output traversal requires O_NOFOLLOW")
    flags |= os.O_NOFOLLOW
    parent_descriptor = -1
    try:
        parent_descriptor = os.open("/", flags)
        for component in absolute.parts[1:-1]:
            next_descriptor = os.open(component, flags, dir_fd=parent_descriptor)
            opened = os.fstat(next_descriptor)
            named = os.stat(
                component, dir_fd=parent_descriptor, follow_symlinks=False
            )
            if (not stat.S_ISDIR(opened.st_mode)
                    or stat.S_ISLNK(named.st_mode)
                    or (opened.st_dev, opened.st_ino) != (named.st_dev, named.st_ino)):
                os.close(next_descriptor)
                raise PreflightRefused("output ancestor is not a real directory")
            os.close(parent_descriptor)
            parent_descriptor = next_descriptor
    except PreflightRefused:
        if parent_descriptor >= 0:
            os.close(parent_descriptor)
        raise
    except OSError as exc:
        if parent_descriptor >= 0:
            os.close(parent_descriptor)
        raise PreflightRefused("output parent is unavailable") from exc
    return parent_descriptor, absolute


def run_preflight(
    plan_path: Path = PLAN_PATH,
    approval_path: Path = APPROVAL_PATH,
    pilot_path: Path = PILOT_PATH,
) -> Dict[str, Any]:
    """Validate immutable inputs and return a prepare-only request."""
    try:
        plan, raw = evaluation_plan_v2.load_plan(plan_path)
    except evaluation_plan_v2.EvaluationPlanError as exc:
        raise PreflightRefused("evaluation plan validation failed") from exc
    _validate_approval(approval_path)
    pilot = _validate_pilot(pilot_path)
    _validate_truth_and_budget(plan)
    return {
        "schema_version": 1,
        "action": "typesafe-jev-three-arm-execution-authorization-request",
        "prepare_only": True,
        "execution_authorized": False,
        "measurement_started": False,
        "design": {
            "sha256": evaluation_plan_v2.EXPECTED_PLAN_SHA256,
            "commit": "9e107609db76022ed6d8e138cbbece2e41d634ee",
            "approval_sha256": APPROVAL_SHA256,
            "review": "HASH_BOOTSTRAP_NARROW_REVIEW: APPROVED",
            "operator_design_approval": True,
        },
        "excluded_pilot": {
            "run_id": pilot["run_id"],
            "events_sha256": PILOT_EVENTS_SHA256,
            "report_sha256": PILOT_REPORT_SHA256,
            "reuse_as_confirmatory_repetition": False,
        },
        "confirmatory_request": {
            "fresh_jev_repetitions": 3,
            "calls_per_repetition": 32,
            "total_calls": 96,
            "retries": 0,
            "cumulative_call_ceiling_including_pilot": 128,
            "per_repetition_input_token_ceiling": 18000,
            "per_repetition_output_token_ceiling": 1000,
            "cumulative_input_token_ceiling": 60000,
            "cumulative_output_token_ceiling": 4000,
        },
        "stop_conditions": plan["failure"]["conditions"],
        "automatic_rerun": False,
        "next_action": "operator must separately authorize execution",
    }


def _write_exclusive(parent_descriptor: int, filename: Path, value: Dict[str, Any]) -> None:
    name = filename.name
    if name in ("", ".", "..") or "/" in name or "\0" in name:
        raise PreflightRefused("output filename is unsafe")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_CLOEXEC"):
        flags |= os.O_CLOEXEC
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        descriptor = os.open(name, flags, 0o600, dir_fd=parent_descriptor)
        with os.fdopen(descriptor, "w", encoding="ascii") as stream:
            json.dump(value, stream, sort_keys=True, ensure_ascii=True,
                      allow_nan=False, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(descriptor)
    except OSError as exc:
        raise PreflightRefused("could not write prepare-only request") from exc


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Prepare, but never execute, the approved three-arm evaluation."
    )
    parser.add_argument("--prepare-only", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    if not args.prepare_only or args.output is None:
        print("REFUSED: --prepare-only and --output are required; no execution occurred",
              file=sys.stderr)
        return 2
    try:
        request = run_preflight()
        parent_descriptor, output = _safe_output(args.output)
        try:
            _write_exclusive(parent_descriptor, output, request)
        finally:
            os.close(parent_descriptor)
    except PreflightRefused as exc:
        print(f"REFUSED: {exc}; no execution occurred", file=sys.stderr)
        return 2
    print(json.dumps({
        "prepare_only": True,
        "execution_authorized": False,
        "output": str(output.resolve()),
    }, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
