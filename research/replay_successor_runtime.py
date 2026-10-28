"""Design-only runtime adapter for the v4 replay-successor contract.

This module performs no filesystem, SQLite, process, VM, or protected-path
access.  It cannot install a store, amend a budget, authenticate an operator,
or authorize replay.  Its only live-capable output is a fail-closed gate matrix.
"""

import re
from typing import Any, Dict

from replay_successor_contract import (
    AGGREGATE_SESSION_CEILING_US, BINDING_VERSION, MODES,
    PREDECESSOR_HOLD_IDS, SESSION_MAXIMUM, candidate_binding, candidate_receipt,
    validate_binding, validate_receipt,
)
from spendability_stage_c import AUTHORITY_FIELDS, StageCError, digest


ADAPTER_VERSION = 1
HASH_RE = re.compile(r"[0-9a-f]{64}\Z")
IDENTIFIER_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,127}\Z")
NO_AUTHORITY = {name: False for name in sorted(AUTHORITY_FIELDS)}

OBSERVATION_FIELDS = frozenset((
    "schema_version", "record_type", "source", "active_binding_version",
    "installed", "installer_sha256", "review_sha256",
    "authorization_sha256", "store_device", "store_inode",
    "budget_amendment_sha256", "operator_per_run_approval_sha256",
    "execution_requested",
))
FUTURE_REQUEST_FIELDS = frozenset((
    "schema_version", "record_type", "contract_receipt_sha256",
    "contract_binding_sha256", "profile", "stage", "mode", "run",
    "reservation", "session_index", "session_execution_us", "guest_launches",
    "installer_sha256", "review_sha256", "authorization_sha256",
    "budget_amendment_sha256", "operator_per_run_approval_sha256",
))
STATUS_FIELDS = frozenset((
    "schema_version", "record_type", "implementation_status",
    "basis", "gates", "outcome", "authority",
))
MODE_GUEST_LAUNCHES = {
    "normal": 2,
    "failed-rebuild": 2,
    "interruption": 2,
    "two-failures": 6,
}


def _require(condition: bool, detail: str) -> None:
    if not condition:
        raise StageCError("replay_successor_runtime", detail)


def _exact(value: Any, expected: frozenset, label: str) -> Dict[str, Any]:
    _require(isinstance(value, dict) and set(value) == set(expected),
             label + " fields differ")
    return value


def _hash(value: Any, label: str) -> str:
    _require(type(value) is str and HASH_RE.fullmatch(value) is not None,
             label + " must be a lowercase SHA-256")
    return value


def _identifier(value: Any, label: str) -> str:
    _require(type(value) is str and IDENTIFIER_RE.fullmatch(value) is not None,
             label + " differs from the approved identifier grammar")
    return value


def candidate_observation() -> Dict[str, Any]:
    """Return the sole hypothetical input accepted by this design adapter."""
    return {
        "schema_version": ADAPTER_VERSION,
        "record_type": "replay-successor-runtime-observation-v1",
        "source": "repository-hypothetical",
        "active_binding_version": 3,
        "installed": False,
        "installer_sha256": None,
        "review_sha256": None,
        "authorization_sha256": None,
        "store_device": None,
        "store_inode": None,
        "budget_amendment_sha256": None,
        "operator_per_run_approval_sha256": None,
        "execution_requested": False,
    }


def validate_observation(value: Any) -> Dict[str, Any]:
    """Reject every attempt to turn a design input into a live claim."""
    record = _exact(value, OBSERVATION_FIELDS, "runtime observation")
    expected = candidate_observation()
    _require(digest(record) == digest(expected),
             "design adapter observation must remain explicitly uninstalled")
    return record


def future_requirements() -> Dict[str, Any]:
    """Describe, but never authenticate, the separately reviewable inputs."""
    return {
        "schema_version": ADAPTER_VERSION,
        "record_type": "replay-successor-future-input-contract-v1",
        "installed_binding": {
            "version": BINDING_VERSION,
            "profiles": ["independent-replay"],
            "store_identity": "actual-device-inode-required",
            "design_only": False,
        },
        "distinct_receipts_required": [
            "installer_sha256", "review_sha256", "authorization_sha256",
            "budget_amendment_sha256", "operator_per_run_approval_sha256",
        ],
        "per_request_limits": {
            "modes": list(MODES),
            "session_maximum": dict(SESSION_MAXIMUM),
            "aggregate_execution_ceiling_us": AGGREGATE_SESSION_CEILING_US,
            "mode_guest_launches": dict(MODE_GUEST_LAUNCHES),
        },
        "protected_verification_required_before_authority": [
            "exact installer bytes",
            "independent runtime review",
            "operator budget amendment",
            "protected v4 installation and store identity",
            "fresh per-run operator approval",
            "dedicated evaluator/runner identities",
            "mandatory live replay gates",
        ],
        "authority": dict(NO_AUTHORITY),
    }


def adapter_status(receipt: Any = None, binding: Any = None,
                   observation: Any = None) -> Dict[str, Any]:
    """Return a blocked, complete design-state gate matrix."""
    receipt = candidate_receipt() if receipt is None else receipt
    binding = candidate_binding() if binding is None else binding
    observation = candidate_observation() if observation is None else observation
    validate_receipt(receipt)
    validate_binding(binding, receipt)
    validate_observation(observation)
    receipt_hash = digest(receipt)
    binding_hash = digest(binding)
    return {
        "schema_version": ADAPTER_VERSION,
        "record_type": "replay-successor-runtime-adapter-status-v1",
        "implementation_status": "design-only-pending-independent-review",
        "basis": {
            "contract_receipt_sha256": receipt_hash,
            "contract_binding_sha256": binding_hash,
            "runtime_observation": "repository-hypothetical-uninstalled",
            "predecessor_holds_preserved": len(PREDECESSOR_HOLD_IDS),
        },
        "gates": {
            "stage_n_candidate_contract": {
                "status": "pass", "evidence": [receipt_hash, binding_hash]},
            "predecessor_history_and_holds": {
                "status": "pass", "evidence": ["retained-stage-a-records"]},
            "independent_runtime_review": {
                "status": "not-run", "evidence": []},
            "operator_budget_amendment": {
                "status": "not-run", "evidence": []},
            "protected_v4_installation": {
                "status": "not-run", "evidence": []},
            "installed_store_identity": {
                "status": "not-run", "evidence": []},
            "per_run_operator_approval": {
                "status": "not-run", "evidence": []},
            "mandatory_live_replay": {
                "status": "not-run", "evidence": []},
            "replay_execution": {
                "status": "blocked",
                "evidence": ["design-only-input-cannot-authorize-effects"]},
        },
        "outcome": {
            "adapter_valid": True,
            "design_only": True,
            "replay_possible": False,
            "execution_authorized": False,
            "allowed_mutations": [],
            "spendable": None,
            "failure_mode": "refuse-before-effects",
            "protected_access": False,
        },
        "authority": dict(NO_AUTHORITY),
    }


def validate_adapter_status(value: Any, receipt: Any = None,
                            binding: Any = None,
                            observation: Any = None) -> Dict[str, Any]:
    expected = adapter_status(receipt, binding, observation)
    record = _exact(value, STATUS_FIELDS, "adapter status")
    _require(digest(record) == digest(expected),
             "adapter status differs from exact regeneration")
    return record


def validate_future_request(value: Any) -> Dict[str, Any]:
    """Validate only the shape of a future request; never grant authority."""
    record = _exact(value, FUTURE_REQUEST_FIELDS, "future replay request")
    _require(record["schema_version"] == ADAPTER_VERSION,
             "future request version differs")
    _require(record["record_type"] == "replay-successor-future-request-v1",
             "future request record type differs")
    mode = record["mode"]
    _require(type(mode) is str and mode in MODES,
             "future request mode differs")
    _require(record["contract_receipt_sha256"] == digest(candidate_receipt())
             and record["contract_binding_sha256"] == digest(candidate_binding()),
             "future request does not bind the exact Stage N candidate")
    _require(record["profile"] == "independent-replay"
             and record["stage"] == "poc",
             "future request profile/stage differs")
    for name in ("run", "reservation"):
        _identifier(record[name], "future request " + name)
    index = record["session_index"]
    _require(type(index) is int and not isinstance(index, bool)
             and index == MODES.index(mode),
             "future request session index differs")
    _require(record["session_execution_us"] == SESSION_MAXIMUM["execution_us"],
             "future request session execution limit differs")
    _require(record["guest_launches"] == MODE_GUEST_LAUNCHES[mode],
             "future request guest-launch limit differs")
    hashes = []
    for name in ("installer_sha256", "review_sha256", "authorization_sha256",
                 "budget_amendment_sha256", "operator_per_run_approval_sha256"):
        hashes.append(_hash(record[name], "future request " + name))
    _require(len(set(hashes)) == len(hashes),
             "future request receipts are not distinct")
    return {
        "request_shape_valid": True,
        "execution_authorized": False,
        "authority": dict(NO_AUTHORITY),
        "remaining_gates": future_requirements()[
            "protected_verification_required_before_authority"],
        "reason": "protected installation and live per-run verification remain required",
    }
