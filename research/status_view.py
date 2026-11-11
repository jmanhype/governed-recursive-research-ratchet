"""Pure, fail-closed status projection for archived GRRR replay evidence."""

import math
from typing import Any, Dict, List, Optional, Tuple, Union

from admission import GATE_INVENTORY
from common import GATES

SCHEMA_VERSION = 2
GATE_PROFILE = "replay-evidence-v1"
REQUIRED_GATES: Tuple[str, ...] = tuple(GATES)
ADMISSION_SUBSET: Tuple[str, ...] = tuple(sorted(GATE_INVENTORY))
ACTION_AUTHORITIES: Tuple[str, ...] = (
    "contract_admission", "human_decision", "installation", "production_mutation",
    "promotion", "replay", "source_review",
)
EXECUTION_STATES = (
    "Queued", "Running", "Awaiting verification", "Ready for review",
    "Stopped", "Failed", "Completed",
)
FINDINGS = (
    "Verified defect", "Not reproduced", "Specification ambiguity",
    "Inconclusive", "Invalid claim",
)
DECISIONS = ("Approve", "Reject", "Needs more evidence", "Request change", "Stop")


def _label(value: Any) -> str:
    return value if type(value) is str and value and value.isprintable() else "unknown"


def _plain(value: Any, depth: int = 0) -> bool:
    """Reject in-process equality/lookup hooks before reading consumed JSON."""
    if depth > 50:
        return False
    if type(value) is dict:
        return all(type(key) is str and _plain(item, depth + 1)
                   for key, item in value.items())
    if type(value) is list:
        return all(_plain(item, depth + 1) for item in value)
    return type(value) in (str, int, float, bool, type(None))


def _number(value: Any) -> Optional[Union[int, float]]:
    if type(value) not in (int, float):
        return None
    try:
        finite = math.isfinite(value)
    except (OverflowError, TypeError, ValueError):
        return None
    return value if finite else None


def _observed_number(value: Any) -> Dict[str, Any]:
    number = _number(value)
    if number is None or number < 0:
        return {"value": None, "state": "Unknown"}
    return {"value": number, "state": "Observed", "verified": False}


def _cost(data: Dict[str, Any], receipt: Any, lifecycle: Any) -> Dict[str, Any]:
    sources = (("input", data), ("receipt", receipt), ("lifecycle", lifecycle))
    values: List[Tuple[str, Union[int, float]]] = []
    malformed = False
    reported = False
    for origin, container in sources:
        if type(container) is not dict or "cost_usd" not in container:
            continue
        reported = True
        candidate = container.get("cost_usd")
        number = _number(candidate)
        if number is None or number < 0:
            malformed = True
        else:
            values.append((origin, number))
    distinct = {value for _, value in values}
    if not reported:
        status, reason = "Unknown", "COST_NOT_REPORTED"
    elif malformed or len(distinct) != 1:
        status, reason = "Unknown", "COST_MALFORMED_OR_AMBIGUOUS"
    else:
        status, reason = "Reported", "COST_REPORTED_UNVERIFIED"
    return {
        "state": status,
        "cost_usd": values[0][1] if status == "Reported" else None,
        "currency": "USD" if status == "Reported" else None,
        "settled_accounting": False,
        "spendability": "Unknown",
        "sources": [origin for origin, _ in values] if status == "Reported" else [],
        "reason_code": reason,
    }


def _gates(receipt: Any, reasons: set) -> Dict[str, Any]:
    gates = receipt.get("gates") if type(receipt) is dict else None
    records: Dict[str, Dict[str, Any]] = {}
    for name in REQUIRED_GATES:
        record = gates.get(name) if type(gates) is dict else None
        status = record.get("status") if type(record) is dict else None
        if type(gates) is not dict or name not in gates:
            state = "not-run"
        elif status == "pass":
            state = "pass"
        elif type(record) is not dict or type(status) is not str or not status:
            state = "malformed"
        else:
            state = status if status in ("fail", "error", "unknown", "not-run", "blocked") else "unknown"
        records[name] = {"status": state}
        if state != "pass":
            reasons.add("GATE_NOT_PASS_" + name.upper())
            if state == "not-run":
                reasons.add("GATE_NOT_RUN_" + name.upper())
            elif state == "malformed":
                reasons.add("GATE_MALFORMED_" + name.upper())
    if type(gates) is not dict:
        reasons.add("GATE_CONTAINER_MALFORMED")
    extras = sorted(
        _label(name) for name in gates
        if type(name) is str and name not in REQUIRED_GATES
    ) if type(gates) is dict else []
    passed = sum(item["status"] == "pass" for item in records.values())
    return {
        "profile": GATE_PROFILE,
        "required_total": len(REQUIRED_GATES),
        "required_passed": passed,
        "required": records,
        "extra_names": extras,
        "admission_subset_total": len(ADMISSION_SUBSET),
        "admission_subset_passed": sum(records[name]["status"] == "pass"
                                       for name in ADMISSION_SUBSET),
        "exact_profile_pass": passed == len(REQUIRED_GATES),
    }


def project_status(data: Dict[str, Any]) -> Dict[str, Any]:
    """Return a detached, read-only version-2 status projection."""
    reasons = set()
    if not _plain(data):
        data = None
    receipt = data.get("receipt") if isinstance(data, dict) else None
    lifecycle = data.get("lifecycle") if isinstance(data, dict) else None
    if not isinstance(data, dict):
        reasons.add("INPUT_MALFORMED")
    if not isinstance(receipt, dict):
        reasons.add("RECEIPT_MALFORMED")
    if not isinstance(lifecycle, dict):
        reasons.add("LIFECYCLE_MISSING")

    finding = receipt.get("finding") if isinstance(receipt, dict) else None
    verified = receipt.get("verified") if isinstance(receipt, dict) else None
    finding_known = type(finding) is str and finding in FINDINGS
    if finding != "Verified defect":
        reasons.add(
            "FINDING_UNKNOWN_OR_MALFORMED" if not finding_known
            else "FINDING_NOT_VERIFIED_DEFECT"
        )
    if verified is not True:
        reasons.add("VERIFIED_NOT_EXACT_TRUE")
    gate_view = _gates(receipt, reasons)
    if not gate_view["exact_profile_pass"]:
        reasons.add("REQUIRED_GATES_INCOMPLETE")

    execution = "Unknown"
    succeeded = lifecycle.get("evaluator_succeeded") if isinstance(lifecycle, dict) else None
    if type(succeeded) is bool:
        execution = "Completed" if succeeded else "Failed"
    else:
        reasons.add("EXECUTION_STATE_UNKNOWN")

    eligible = bool(
        verified is True and finding_known and finding == "Verified defect"
        and gate_view["exact_profile_pass"]
    )
    if not eligible:
        reasons.add("EVIDENCE_REVIEW_NOT_ELIGIBLE")
    reasons.add(
        "HISTORICAL_EVIDENCE_INSPECTION_ELIGIBLE" if eligible
        else "HISTORICAL_EVIDENCE_INCOMPLETE"
    )
    reasons.update((
        "EVIDENCE_HISTORICAL_UNVERIFIED",
        "SOURCE_REVIEW_NOT_ESTABLISHED",
        "CURRENT_VERIFICATION_ABSENT",
        "HUMAN_DECISION_NOT_ESTABLISHED",
        "ACTION_AUTHORIZATION_NOT_ESTABLISHED",
        "INSTALLATION_NOT_QUALIFIED",
        "SPENDABILITY_UNKNOWN",
        "STOP_STATE_UNKNOWN",
        "ADMISSION_NOT_ESTABLISHED",
        "PROMOTION_DISABLED",
    ))
    budget = _cost(data, receipt, lifecycle)
    reasons.add(budget["reason_code"])
    elapsed = _observed_number(
        lifecycle.get("elapsed_seconds") if isinstance(lifecycle, dict) else None
    )
    if elapsed["state"] == "Unknown":
        reasons.add("ELAPSED_UNKNOWN")

    authorities = {name: False for name in ACTION_AUTHORITIES}
    identities = receipt.get("identities") if isinstance(receipt, dict) else None
    nested_challenge = identities.get("challenge") if isinstance(identities, dict) else None
    direct_challenge = receipt.get("challenge") if isinstance(receipt, dict) else None
    challenge = direct_challenge if isinstance(direct_challenge, str) and direct_challenge else nested_challenge
    return {
        "schema_version": SCHEMA_VERSION,
        "scope": {
            "input": "archived replay export",
            "projection": "pure in-memory read-only status",
            "gate_profile": GATE_PROFILE,
            "live": False,
            "current_verification": False,
            "read_only": True,
        },
        "read_only": True,
        "run": _label(receipt.get("run") if isinstance(receipt, dict) else None),
        "challenge": _label(challenge),
        "execution": {"state": execution, "elapsed_seconds": elapsed["value"]},
        "verification": {
            "finding": finding if finding_known else "Unknown",
            "verified": verified is True,
            "gates": gate_view,
            "evidence_review_eligible": eligible,
        },
        "source_review": {
            "state": "Not established", "eligible": False,
        },
        "human_decision": {
            "state": "Not established", "decision": None, "approval": False,
        },
        "action_authorization": {
            "state": "Not established", "authorities": authorities,
        },
        "installation": {"state": "Not qualified", "qualified": False},
        "budget": budget,
        "cessation": {"state": "Unknown", "stopped": None},
        "admission": {"state": "Not established", "authorized": False},
        "promotion": {"state": "Disabled", "authorized": False},
        "evidence_identity": {
            "digest": None,
            "basis": "not computed; artifact identity/provenance/currency not established",
        },
        "decision": None,
        "decision_state": "Not established",
        "recommendation": "Needs more evidence",
        "next_action": (
            "Inspect the named historical evidence, then request an explicit human decision"
            if eligible else "Provide complete verified historical evidence"
        ),
        "next_owner": "Human reviewer" if eligible else "Evidence owner",
        "reason_codes": sorted(reasons),
    }
