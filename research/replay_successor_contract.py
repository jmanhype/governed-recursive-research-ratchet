"""Validate the proposed GRRR replay-successor authority contract.

This module is a design artifact only.  It does not open, install, reconcile, or
mutate any accounting store and does not authorize replay execution.
"""

import re
from typing import Any, Dict

from spendability_stage_c import AUTHORITY_FIELDS, StageCError, digest


CONTRACT_VERSION = 1
BINDING_VERSION = 4
HASH_RE = re.compile(r"[0-9a-f]{64}\Z")
IDENTIFIER_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,127}\Z")
BASE = "/Library/GRRR/accounting-poc2"
PROFILE = "independent-replay"
MODES = ("normal", "failed-rebuild", "interruption", "two-failures")
SESSION_MAXIMUM = {
    "currency": "USD",
    "money_cents": 0,
    "execution_us": 480000000,
    "review_us": 0,
}
AGGREGATE_SESSION_CEILING_US = SESSION_MAXIMUM["execution_us"] * len(MODES)
MAXIMUM_GUEST_LAUNCHES = 12
CANDIDATE_DECISION = "candidate-fresh-replay-successor-poc"
CEILING_BASIS = "operator-approved-incremental-amendment-required-before-any-charge"
FAILURE_STOP_POLICY = "two-consecutive-independent-replay-failures-requires-operator-approval"
INSTALL_FAILURE_MODE = "refuse-no-retry-preserve-partial-evidence"
ROLLBACK_SCOPE = "new-successor-namespace-only"
SUCCESSOR_CAMPAIGN = "GRRR-REPLAY-SUCCESSOR-POC-2"
SUCCESSOR_STORE_ID = "unissued-independent-replay-v4"
PREDECESSOR_STORE_ID = "901acaff42b5a42f667b1c435beba9a9ae8312539cc36eb023c45584fd2e06d6"
PREDECESSOR_RECOVERY_RECEIPT = "6d3d5b092c0ee8273a657c83823d8465b215f2b1b66ec627dfde2d96b21fe587"

PREDECESSOR_FIELDS = frozenset((
    "active_sha256", "database_sha256", "stage_a_baseline_sha256",
    "stage_a_package_sha256", "stage_l_package_sha256",
    "stage_m_package_sha256",
))
SUCCESSOR_FIELDS = frozenset((
    "campaign", "store_id", "ceiling_basis", "proposed_ceiling", "relationship",
))
HISTORY_FIELDS = frozenset((
    "status", "spendable", "whole_archive_absence_established",
    "response_ready", "final_classifications_made",
    "all_original_ceilings_encumbered", "evidence_boundary",
))
HOLDS_FIELDS = frozenset((
    "status", "count", "reservation_ids", "maximum", "release",
))
SCOPE_FIELDS = frozenset((
    "profile", "stage", "modes", "session_maximum",
    "session_count", "aggregate_session_execution_ceiling_us",
    "maximum_guest_launches", "failure_stop_policy",
))
GUARD_FIELDS = frozenset((
    "predecessor_mutations", "reconciliation_claim",
    "replay_execution_authorized", "per_run_operator_approval_required",
    "admission", "promotion", "automatic_merge", "push",
    "authority",
))
INSTALLATION_FIELDS = frozenset((
    "installer_sha256", "review_sha256", "authorization_sha256",
    "review_status", "operator_authorization_status", "exclusive_parent",
    "install_once", "predecessor_read_only", "failure_mode",
    "rollback_scope", "rollback_requires_verified_baseline",
    "predecessor_rollback", "design_only",
))
RECEIPT_FIELDS = frozenset((
    "version", "kind", "decision", "predecessor", "history", "holds",
    "successor", "scope", "guards", "installation",
))
BINDING_FIELDS = frozenset((
    "version", "campaign", "store_id", "directory",
    "prior_history_receipt", "profiles", "device_identity", "inode_identity",
    "successor_sha256", "predecessor_store_id",
    "predecessor_binding_sha256", "allowed_mutation_profiles",
    "execution_authorized", "budget_amendment_required", "design_only",
))

PREDECESSOR_VALUES = {
    "active_sha256": "9c5194dd12ff7601917fcccc293c459db09a41da8bad9fa9983cbef618d453f8",
    "database_sha256": "9c6ff2561a364ed982cd5477dd4b200c995da6910c9a17aa3d3c411a962d64f3",
    "stage_a_baseline_sha256": "7608cbe6fc5f671b88573eca8b642ebfbc172f0cb920f75d60ca34cfa60c730a",
    "stage_a_package_sha256": "bb79e0242ea914d75b3e0ab9b44248c6e4eca8435214a1d970a55bef2a99a391",
    "stage_l_package_sha256": "56bc2c82accb6530f1a479ad0b23408077a173e2ee7e2f9fcc41bc1e0099df53",
    "stage_m_package_sha256": "c65aedd7f7a2f861ef5593ba9705981ca42508bf6f3f12a4f23787381d12df0b",
}
PREDECESSOR_HISTORY = {
    "status": "unresolved",
    "spendable": None,
    "whole_archive_absence_established": False,
    "response_ready": False,
    "final_classifications_made": 0,
    "all_original_ceilings_encumbered": True,
    "evidence_boundary": "retained-original-records-only",
}
PREDECESSOR_HOLD_IDS = (
    "69523b39a51c44739114313c9325028c",
    "b34d8b9d106e42eab3a3e43daac98ddd",
    "d375ce6a2d924646bec71df64e939a5b",
)
PREDECESSOR_HOLDS = {
    "status": "unresolved",
    "count": len(PREDECESSOR_HOLD_IDS),
    "reservation_ids": list(PREDECESSOR_HOLD_IDS),
    "maximum": {
        "currency": "USD",
        "money_cents": 0,
        "execution_us": 300_000_000,
        "review_us": 0,
    },
    "release": False,
}
PROPOSED_CEILING = dict(SESSION_MAXIMUM, execution_us=AGGREGATE_SESSION_CEILING_US)
NO_AUTHORITY = {name: False for name in sorted(AUTHORITY_FIELDS)}


def _require(condition: bool, detail: str) -> None:
    if not condition:
        raise StageCError("replay_successor_contract", detail)


def _exact(value: Any, fields: frozenset, label: str) -> Dict[str, Any]:
    _require(isinstance(value, dict) and set(value) == set(fields),
             label + " fields differ")
    return value


def _hashed(value: Any, label: str) -> str:
    _require(isinstance(value, str) and HASH_RE.fullmatch(value) is not None,
             label + " hash differs")
    return value


def _identifier(value: Any, label: str) -> str:
    _require(isinstance(value, str) and IDENTIFIER_RE.fullmatch(value) is not None,
             label + " identifier differs")
    return value


def _null(value: Any, label: str) -> None:
    _require(value is None, label + " must remain unissued in the design contract")


def validate_predecessor(value: Any) -> Dict[str, Any]:
    record = _exact(value, PREDECESSOR_FIELDS, "predecessor")
    for name in sorted(PREDECESSOR_FIELDS):
        _hashed(record[name], "predecessor " + name)
    _require(record == PREDECESSOR_VALUES, "predecessor evidence identity differs")
    return record


def validate_successor(value: Any) -> Dict[str, Any]:
    record = _exact(value, SUCCESSOR_FIELDS, "successor")
    _identifier(record["campaign"], "successor campaign")
    _identifier(record["store_id"], "successor store")
    _require(record["campaign"] == SUCCESSOR_CAMPAIGN,
             "successor campaign identity differs")
    _require(record["store_id"] == SUCCESSOR_STORE_ID,
             "successor store identity differs")
    _require(record["ceiling_basis"] == CEILING_BASIS,
             "successor ceiling basis differs")
    _require(digest(record["proposed_ceiling"]) == digest(PROPOSED_CEILING),
             "successor proposed ceiling differs")
    _require(record["relationship"] == "fresh-successor-not-reconciliation",
             "successor relationship differs")
    return record


def validate_history(value: Any) -> Dict[str, Any]:
    record = _exact(value, HISTORY_FIELDS, "predecessor history")
    _require(digest(record) == digest(PREDECESSOR_HISTORY),
             "predecessor history cannot be resolved by this design contract")
    return record


def validate_holds(value: Any) -> Dict[str, Any]:
    record = _exact(value, HOLDS_FIELDS, "predecessor holds")
    _require(digest(record) == digest(PREDECESSOR_HOLDS),
             "predecessor holds must remain exactly unresolved")
    return record


def validate_scope(value: Any) -> Dict[str, Any]:
    record = _exact(value, SCOPE_FIELDS, "scope")
    _require(record["profile"] == PROFILE, "only independent replay is authorized")
    _require(record["stage"] == "poc", "successor scope must be POC")
    _require(tuple(record["modes"]) == MODES, "mode inventory differs")
    _require(digest(record["session_maximum"]) == digest(SESSION_MAXIMUM),
             "session maximum differs")
    _require(record["session_count"] == len(MODES), "session count differs")
    _require(record["aggregate_session_execution_ceiling_us"]
             == AGGREGATE_SESSION_CEILING_US,
             "aggregate execution ceiling differs")
    _require(record["maximum_guest_launches"] == MAXIMUM_GUEST_LAUNCHES,
             "guest-launch ceiling differs")
    _require(record["failure_stop_policy"] == FAILURE_STOP_POLICY,
             "failure-stop policy differs")
    return record


def validate_guards(value: Any) -> Dict[str, Any]:
    record = _exact(value, GUARD_FIELDS, "guards")
    _require(record["predecessor_mutations"] == [],
             "predecessor mutations are forbidden")
    _require(record["reconciliation_claim"] is False,
             "successor cannot claim reconciliation")
    _require(record["replay_execution_authorized"] is False,
             "receipt cannot authorize all replay runs")
    _require(record["per_run_operator_approval_required"] is True,
             "per-run operator approval is mandatory")
    _require(record["admission"] == "blocked" and record["promotion"] == "disabled",
             "admission/promotion guards differ")
    _require(record["automatic_merge"] is False and record["push"] is False,
             "merge/push guards differ")
    _require(digest(record["authority"]) == digest(NO_AUTHORITY),
             "design contract cannot grant authority")
    return record


def validate_installation(value: Any) -> Dict[str, Any]:
    record = _exact(value, INSTALLATION_FIELDS, "installation")
    for name in ("installer_sha256", "review_sha256", "authorization_sha256"):
        _null(record[name], "installation " + name)
    _require(record["review_status"] == "required",
             "independent review remains required")
    _require(record["operator_authorization_status"] == "required",
             "operator authorization remains required")
    _require(record["exclusive_parent"] is True,
             "exclusive parent control is mandatory")
    _require(record["install_once"] is True,
             "installation must refuse retry/resume")
    _require(record["predecessor_read_only"] is True,
             "predecessor must remain read-only")
    _require(record["failure_mode"] == INSTALL_FAILURE_MODE,
             "failure mode differs")
    _require(record["rollback_scope"] == ROLLBACK_SCOPE,
             "rollback scope differs")
    _require(record["rollback_requires_verified_baseline"] is True,
             "rollback must require a verified baseline")
    _require(record["predecessor_rollback"] is False,
             "this contract cannot roll back the predecessor")
    _require(record["design_only"] is True,
             "contract must remain design-only")
    return record


def validate_receipt(value: Any) -> Dict[str, Any]:
    record = _exact(value, RECEIPT_FIELDS, "receipt")
    _require(record["version"] == CONTRACT_VERSION, "receipt version differs")
    _require(record["kind"] == "replay-successor-authority",
             "receipt kind differs")
    _require(record["decision"] == CANDIDATE_DECISION,
             "receipt decision differs")
    validate_predecessor(record["predecessor"])
    validate_history(record["history"])
    validate_holds(record["holds"])
    validate_successor(record["successor"])
    validate_scope(record["scope"])
    validate_guards(record["guards"])
    validate_installation(record["installation"])
    _require(digest(record) == digest(candidate_receipt()),
             "receipt differs from the sole design candidate")
    return record


def validate_binding(value: Any, receipt: Any = None) -> Dict[str, Any]:
    record = _exact(value, BINDING_FIELDS, "binding")
    _require(record["version"] == BINDING_VERSION, "binding version must be 4")
    _identifier(record["campaign"], "binding campaign")
    _identifier(record["store_id"], "binding store")
    _require(record["directory"] == BASE + "/" + record["store_id"],
             "binding must address a sibling successor store")
    _hashed(record["prior_history_receipt"], "binding prior history")
    _require(record["prior_history_receipt"] == PREDECESSOR_RECOVERY_RECEIPT,
             "binding prior-history receipt differs")
    _require(record["profiles"] == [PROFILE],
             "v4 binding must permit only independent replay")
    _require(record["device_identity"] == "required-at-install"
             and record["inode_identity"] == "required-at-install",
             "binding device/inode identities must not be fabricated")
    _hashed(record["successor_sha256"], "binding successor receipt")
    _identifier(record["predecessor_store_id"], "predecessor store")
    _hashed(record["predecessor_binding_sha256"], "predecessor binding")
    _require(record["predecessor_store_id"] == PREDECESSOR_STORE_ID,
             "predecessor store identity differs")
    _require(record["predecessor_binding_sha256"] == PREDECESSOR_VALUES["active_sha256"],
             "predecessor binding identity differs")
    _require(record["allowed_mutation_profiles"] == [PROFILE],
             "only independent-replay mutations may be allowed")
    _require(record["execution_authorized"] is False,
             "binding cannot authorize replay without per-run approval")
    _require(record["budget_amendment_required"] is True,
             "fresh successor allowance requires an explicit amendment")
    _require(record["design_only"] is True,
             "binding contract must remain design-only")
    if receipt is not None:
        validate_receipt(receipt)
        _require(receipt["successor"]["campaign"] == record["campaign"]
                 and receipt["successor"]["store_id"] == record["store_id"],
                 "binding/successor identity differs")
        _require(digest(receipt) == record["successor_sha256"],
                 "binding receipt hash differs")
    _require(digest(record) == digest(candidate_binding()),
             "binding differs from the sole design candidate")
    return record


def candidate_receipt() -> Dict[str, Any]:
    """Return the sole fail-closed design candidate; this is not authority."""
    return {
        "version": CONTRACT_VERSION,
        "kind": "replay-successor-authority",
        "decision": CANDIDATE_DECISION,
        "predecessor": dict(PREDECESSOR_VALUES),
        "history": dict(PREDECESSOR_HISTORY),
        "holds": {
            "status": PREDECESSOR_HOLDS["status"],
            "count": PREDECESSOR_HOLDS["count"],
            "reservation_ids": list(PREDECESSOR_HOLDS["reservation_ids"]),
            "maximum": dict(PREDECESSOR_HOLDS["maximum"]),
            "release": PREDECESSOR_HOLDS["release"],
        },
        "successor": {
            "campaign": SUCCESSOR_CAMPAIGN,
            "store_id": SUCCESSOR_STORE_ID,
            "ceiling_basis": CEILING_BASIS,
            "proposed_ceiling": dict(PROPOSED_CEILING),
            "relationship": "fresh-successor-not-reconciliation",
        },
        "scope": {
            "profile": PROFILE,
            "stage": "poc",
            "modes": list(MODES),
            "session_maximum": dict(SESSION_MAXIMUM),
            "session_count": len(MODES),
            "aggregate_session_execution_ceiling_us": AGGREGATE_SESSION_CEILING_US,
            "maximum_guest_launches": MAXIMUM_GUEST_LAUNCHES,
            "failure_stop_policy": FAILURE_STOP_POLICY,
        },
        "guards": {
            "predecessor_mutations": [],
            "reconciliation_claim": False,
            "replay_execution_authorized": False,
            "per_run_operator_approval_required": True,
            "admission": "blocked",
            "promotion": "disabled",
            "automatic_merge": False,
            "push": False,
            "authority": dict(NO_AUTHORITY),
        },
        "installation": {
            "installer_sha256": None,
            "review_sha256": None,
            "authorization_sha256": None,
            "review_status": "required",
            "operator_authorization_status": "required",
            "exclusive_parent": True,
            "install_once": True,
            "predecessor_read_only": True,
            "failure_mode": INSTALL_FAILURE_MODE,
            "rollback_scope": ROLLBACK_SCOPE,
            "rollback_requires_verified_baseline": True,
            "predecessor_rollback": False,
            "design_only": True,
        },
    }


def candidate_binding() -> Dict[str, Any]:
    """Return the hypothetical v4 binding shape without a store identity."""
    receipt = candidate_receipt()
    successor = receipt["successor"]
    return {
        "version": BINDING_VERSION,
        "campaign": successor["campaign"],
        "store_id": successor["store_id"],
        "directory": BASE + "/" + successor["store_id"],
        "prior_history_receipt": PREDECESSOR_RECOVERY_RECEIPT,
        "profiles": [PROFILE],
        "device_identity": "required-at-install",
        "inode_identity": "required-at-install",
        "successor_sha256": digest(receipt),
        "predecessor_store_id": PREDECESSOR_STORE_ID,
        "predecessor_binding_sha256": PREDECESSOR_VALUES["active_sha256"],
        "allowed_mutation_profiles": [PROFILE],
        "execution_authorized": False,
        "budget_amendment_required": True,
        "design_only": True,
    }


def contract_summary() -> Dict[str, Any]:
    return {
        "schema_version": CONTRACT_VERSION,
        "binding_version": BINDING_VERSION,
        "decision": CANDIDATE_DECISION,
        "profile": PROFILE,
        "modes": list(MODES),
        "ceiling_basis": CEILING_BASIS,
        "proposed_ceiling": dict(PROPOSED_CEILING),
        "session_maximum": SESSION_MAXIMUM,
        "aggregate_session_execution_ceiling_us": AGGREGATE_SESSION_CEILING_US,
        "maximum_guest_launches": MAXIMUM_GUEST_LAUNCHES,
        "relationship": "fresh-successor-not-reconciliation",
        "predecessor_history": dict(PREDECESSOR_HISTORY),
        "predecessor_unresolved_holds": len(PREDECESSOR_HOLD_IDS),
        "receipt_sha256": digest(candidate_receipt()),
        "authority": dict(NO_AUTHORITY),
        "implementation_status": "design-only",
    }
