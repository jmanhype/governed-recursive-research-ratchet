"""Operator review surfaces for the fail-closed replay status projection.

Reads archived replay evidence and produces consistent Plain Text,
Markdown, and JSON reports using the approved vocabulary.
"""

import json
import math
import textwrap
from decimal import Decimal
from pathlib import Path
from typing import Any, Dict

from status_view import (
    DECISIONS, EXECUTION_STATES, FINDINGS, project_status,
)


class ReportError(ValueError):
    """Raised when replay evidence or a report violates review safeguards."""


def _unique_fields(pairs: list) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ReportError("Duplicate archived JSON field")
        result[key] = value
    return result


def _json_float(token: str) -> float:
    value = float(token)
    if not math.isfinite(value) or Decimal(token) != Decimal(str(value)):
        raise ReportError("Archived number loses precision")
    return value


def _invalid_constant(token: str) -> None:
    raise ReportError("Non-finite archived JSON number")


def _read_json(path: Path) -> Dict[str, Any]:
    try:
        value = json.loads(path.read_bytes(), object_pairs_hook=_unique_fields,
                           parse_float=_json_float, parse_constant=_invalid_constant)
        if type(value) is not dict:
            raise ReportError("Archived record is not an object")
        return value
    except (OSError, ValueError, UnicodeError, RecursionError, ArithmeticError) as exc:
        raise ReportError("Archived evidence is unreadable or ambiguous") from exc


def load_replay_data(evidence_path: Path) -> Dict[str, Any]:
    """Load replay evidence from the export directory."""
    snapshot = _read_json(evidence_path / "snapshot.json")
    receipt_obj = evidence_path / "objects/78fde524d9562f6cb28df336512b3ca84bc8d72c72b47cd71f1a47516613ab4e"
    receipt = _read_json(receipt_obj) if receipt_obj.exists() else {}
    lifecycle_path = evidence_path.parent / "lifecycle.json"
    lifecycle = _read_json(lifecycle_path) if lifecycle_path.exists() else {}
    return {"snapshot": snapshot, "receipt": receipt, "lifecycle": lifecycle}


def build_report(data: Dict[str, Any]) -> Dict[str, Any]:
    """Build the shared version-2 report from replay data."""
    return project_status(data)


def _validated(report: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(report, dict) or report.get("schema_version") != 2:
        raise ReportError("report must be a version-2 status projection")
    return report


def _cost_line(budget: Dict[str, Any]) -> str:
    if budget["state"] == "Reported":
        value = budget["cost_usd"]
        if type(value) is int:
            amount = f"{value}.00"
        elif value == 0:
            amount = "0.00"
        elif value < 0.01 or value >= 1e15:
            amount = repr(value)
        else:
            amount = f"{value:.2f}"
        return f"${amount} reported, unverified; not spendability"
    return "Unknown; no settled or spendable amount is established"


def _elapsed_line(execution: Dict[str, Any]) -> str:
    value = execution["elapsed_seconds"]
    return "Unknown" if value is None else f"{value:.1f} seconds reported, unverified"


def _render_markdown(report: Dict[str, Any], status: bool) -> str:
    r = _validated(report)
    gates = r["verification"]["gates"]
    title = "GRRR Read-only Status" if status else "GRRR Historical Replay Review"
    lines = [
        f"# {title}", "", "## Scope", "",
        "- Historical archived input; unverified as current evidence.",
        "- Current verification is absent; no live runtime state is inferred.",
        "- Read-only projection; all projected action authorities are false.", "",
        "## Status Summary" if status else "## Decision Summary", "",
        f"- Run: `{r['run']}`",
        f"- Challenge: `{r['challenge']}`",
        f"- Execution: {r['execution']['state']}",
        f"- Elapsed: {_elapsed_line(r['execution'])}",
        f"- Finding: {r['verification']['finding']}",
        f"- Exact verification boolean: {str(r['verification']['verified']).lower()}",
        f"- Required gates: {gates['required_passed']}/{gates['required_total']} pass",
        f"- Evidence review eligibility: {str(r['verification']['evidence_review_eligible']).lower()}",
        f"- Cost: {_cost_line(r['budget'])}",
        f"- Spendability: {r['budget']['spendability']}",
        f"- Human decision: {r['human_decision']['state']}",
        f"- Recommendation: {r['recommendation']}", "",
        "## Technical Verification", "",
        "Required full replay gate profile (not just admission's subset):", "",
    ]
    lines.extend(
        f"- {name}: {record['status']}" for name, record in gates["required"].items()
    )
    lines.append(f"- Admission-only subset: {gates['admission_subset_passed']}/"
                 f"{gates['admission_subset_total']}; not full verification or approval")
    if gates["extra_names"]:
        lines.extend(("", "Extra gates are outside this profile and do not substitute:"))
        lines.extend(f"- {name}" for name in gates["extra_names"])
    lines.extend((
        "", "## Full Audit", "",
        f"- Source review: {r['source_review']['state']}",
        f"- Installation: {r['installation']['state']}",
        f"- Stop/cessation: {r['cessation']['state']}",
        f"- Admission: {r['admission']['state']}",
        f"- Promotion: {r['promotion']['state']}",
        "- Human decision, admission, installation, promotion and replay are not authorized here.",
        "- Evidence review eligibility, when true, means inspect evidence only.",
        "- Artifact identity/provenance/currency is not established by this projection.",
        "", "---", "", f"Next action: **{r['next_action']}**",
        f"Next owner: **{r['next_owner']}**",
    ))
    return "\n".join(lines)


def _render_text(report: Dict[str, Any], status: bool) -> str:
    r = _validated(report)
    gates = r["verification"]["gates"]
    title = "GRRR READ-ONLY STATUS" if status else "GRRR HISTORICAL REPLAY REVIEW"
    lines = [
        title, "=" * len(title),
        "Evidence:        Historical archive; current verification absent",
        "Projection:      Read-only; no live runtime or authority inferred",
        f"Run:             {r['run']}",
        f"Challenge:       {r['challenge']}",
        f"Execution:       {r['execution']['state']}",
        f"Elapsed:         {_elapsed_line(r['execution'])}",
        f"Finding:         {r['verification']['finding']}",
        f"Verified exact:  {str(r['verification']['verified']).lower()}",
        f"Required gates:  {gates['required_passed']}/{gates['required_total']} pass",
        f"Review eligible: {str(r['verification']['evidence_review_eligible']).lower()}",
        f"Cost:            {_cost_line(r['budget'])}",
        f"Spendability:    {r['budget']['spendability']}",
        f"Human decision:  {r['human_decision']['state']}",
        f"Source review:   {r['source_review']['state']}",
        f"Installation:    {r['installation']['state']}",
        f"Stop/cessation:  {r['cessation']['state']}",
        f"Admission:       {r['admission']['state']}",
        f"Promotion:       {r['promotion']['state']}",
        "All authorities: false",
        f"Recommendation:  {r['recommendation']}",
        f"Next action:     {r['next_action']}",
        f"Next owner:      {r['next_owner']}",
        "", "Required full replay gates:",
    ]
    lines.extend(f"- {name}: {record['status']}" for name, record in gates["required"].items())
    lines.append(f"Admission-only subset: {gates['admission_subset_passed']}/"
                 f"{gates['admission_subset_total']}; not full verification or approval")
    if gates["extra_names"]:
        lines.append("Extra gates (not substitutes): " + ", ".join(gates["extra_names"]))
    lines.append("Identity: not established; no artifact provenance or currency claim")
    return "\n".join(textwrap.fill(line, width=80, subsequent_indent="  ",
                                  break_long_words=False, break_on_hyphens=False)
                     if line else "" for line in lines)


def to_markdown(report: Dict[str, Any]) -> str:
    """Render the shared projection as decision-safe Markdown."""
    return _render_markdown(report, False)


def to_status_markdown(report: Dict[str, Any]) -> str:
    """Render the shared projection as status-oriented Markdown."""
    return _render_markdown(report, True)


def to_plain_text(report: Dict[str, Any]) -> str:
    """Render the shared projection as accessible terminal text."""
    return _render_text(report, False)


def to_status_plain_text(report: Dict[str, Any]) -> str:
    """Render the shared projection as accessible status text."""
    return _render_text(report, True)


def to_json(report: Dict[str, Any]) -> str:
    return json.dumps(_validated(report), indent=2, sort_keys=True, allow_nan=False)


def to_status_json(report: Dict[str, Any]) -> str:
    """Render the same shared projection as JSON."""
    return to_json(report)
