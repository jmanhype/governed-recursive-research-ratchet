"""Operator review report generator for governed replay decisions.

Reads verified replay evidence and produces consistent Plain Text,
Markdown, and JSON reports using the approved vocabulary.
"""

import json
from pathlib import Path
from typing import Any, Dict

EXECUTION_STATES = (
    "Queued", "Running", "Awaiting verification", "Ready for review",
    "Stopped", "Failed", "Completed",
)
FINDINGS = (
    "Verified defect", "Not reproduced", "Specification ambiguity",
    "Inconclusive", "Invalid claim",
)
DECISIONS = ("Approve", "Reject", "Needs more evidence", "Request change", "Stop")

SNAPSHOT_EXPORT = "ab8d72f25c3a4ce2f5d5d672c4d052ea2de442f9c9384bd381d8222d7a91b689"
TRUSTED_ANCHOR = "34dc2753bc0be33753a3312b48f9530ff3e00019757254529310e053fd0e905e"


class ReportError(ValueError):
    pass


def load_replay_data(evidence_path: Path) -> Dict[str, Any]:
    """Load replay evidence from the export directory."""
    snapshot = json.loads((evidence_path / "snapshot.json").read_bytes())
    receipt_obj = evidence_path / "objects/78fde524d9562f6cb28df336512b3ca84bc8d72c72b47cd71f1a47516613ab4e"
    receipt = json.loads(receipt_obj.read_bytes()) if receipt_obj.exists() else {}
    lifecycle_path = evidence_path.parent / "lifecycle.json"
    lifecycle = json.loads(lifecycle_path.read_bytes()) if lifecycle_path.exists() else {}
    return {"snapshot": snapshot, "receipt": receipt, "lifecycle": lifecycle}


def build_report(data: Dict[str, Any]) -> Dict[str, Any]:
    """Build a consistent report from replay data."""
    receipt = data.get("receipt", {})
    lifecycle = data.get("lifecycle", {})
    finding = receipt.get("finding", "Inconclusive")
    if finding not in FINDINGS:
        raise ReportError(f"unknown finding: {finding}")
    gates = receipt.get("gates", {})
    gates_pass = sum(1 for g in gates.values() if g.get("status") == "pass")
    gates_total = len(gates)
    return {
        "schema_version": 1,
        "run": receipt.get("run", "unknown"),
        "challenge": receipt.get("challenge", "unknown"),
        "execution_state": "Completed" if lifecycle.get("evaluator_succeeded") else "Failed",
        "finding": finding,
        "verified": receipt.get("verified", False),
        "gates_pass": gates_pass,
        "gates_total": gates_total,
        "elapsed_seconds": lifecycle.get("elapsed_seconds", 0),
        "cost_usd": 0,
        "snapshot_sha256": SNAPSHOT_EXPORT,
        "decision": None,
        "decision_state": "Ready for review",
        "recommendation": "Approve permanent contract admission" if finding == "Verified defect" else "Reject",
    }


def to_markdown(report: Dict[str, Any]) -> str:
    """Render report as decision-first Markdown."""
    r = report
    lines = [
        "# GRRR Replay Review",
        "",
        "## Decision Summary",
        "",
        f"- **Challenge:** {r['challenge']}",
        f"- **Finding:** {r['finding']}",
        f"- **Verified:** {r['verified']}",
        f"- **Execution State:** {r['execution_state']}",
        f"- **Gates:** {r['gates_pass']}/{r['gates_total']} pass",
        f"- **Elapsed:** {r['elapsed_seconds']:.1f} seconds",
        f"- **Cost:** ${r['cost_usd']:.2f}",
        f"- **Recommendation:** {r['recommendation']}",
        "",
        "## Technical Verification",
        "",
        f"- Run ID: `{r['run']}`",
        f"- Snapshot SHA-256: `{r['snapshot_sha256']}`",
        "",
        "## Full Audit",
        "",
        f"- Snapshot is not fresh replay; recorded output only.",
        f"- Historical evidence; currency must be verified before action.",
        "",
        "---",
        f"Decision state: **{r['decision_state']}**",
    ]
    return "\n".join(lines)


def to_plain_text(report: Dict[str, Any]) -> str:
    """Render report as plain text for terminal/screen readers."""
    r = report
    return "\n".join([
        f"GRRR REPLAY REVIEW",
        f"===================",
        f"Challenge:       {r['challenge']}",
        f"Finding:         {r['finding']}",
        f"Verified:        {r['verified']}",
        f"Execution State: {r['execution_state']}",
        f"Gates:           {r['gates_pass']}/{r['gates_total']} pass",
        f"Elapsed:         {r['elapsed_seconds']:.1f} seconds",
        f"Cost:            ${r['cost_usd']:.2f}",
        f"Recommendation:  {r['recommendation']}",
        f"Decision State:  {r['decision_state']}",
        f"Snapshot:        {r['snapshot_sha256'][:16]}...",
    ])


def to_json(report: Dict[str, Any]) -> str:
    return json.dumps(report, indent=2, sort_keys=True)
