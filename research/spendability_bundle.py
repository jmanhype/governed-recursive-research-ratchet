"""Fail-closed Stage E assembler for the spendability evidence bundle.

This module combines repository-retained Stage A rows and the independently
reviewed Stage D locked capture. It creates unresolved sidecars for evidence
that is not yet available and never grants spendability or dispatch authority.
"""

from copy import deepcopy
from hashlib import sha256
import json
from typing import Any, Dict, List, Mapping, Tuple

from spendability_stage_c import (
    AUTHORITY_FIELDS, DATABASE_SHA256, LINEAGE_ARTIFACTS, OVERHEAD_CATEGORIES,
    PENDING_IDS, RESERVATION_IDS, STAGE_A_BASELINE_SHA256, StageCError,
    digest, validate_completeness_record, validate_pending_disposition,
    validate_provenance_record, validate_quiescence_record,
    validate_schema_compatibility,
)


BUNDLE_FIELDS = frozenset((
    "schema_version", "record_type", "basis", "raw_rows",
    "schema_compatibility", "quiescence", "postcapture_immutable",
    "provenance", "pending_dispositions", "historical_completeness",
    "gate_inventory", "assembly_valid", "evidence_valid", "outcome", "authority",
))
APPROVED_STAGE_D_CAPTURE_SHA256 = "d22bec465786840fc85a139ebe3781f68bd1663bde51649ac96d34e03e340de8"
APPROVED_STAGE_D_POSTCAPTURE_SHA256 = "78eb1f69a30d161f3c2d8c67fbbf40e579cc3de5f53b6bb0f8e8fc395888574a"
BASIS_FIELDS = frozenset((
    "stage_a_baseline_sha256", "stage_d_capture_sha256",
    "stage_d_postcapture_sha256", "database_sha256",
    "stage_d_independent_review",
))
GATES = (
    "schema_compatibility", "quiescence", "provenance", "pending_evidence",
    "overhead_completeness", "historical_completeness", "independent_review",
    "operator_decision", "spendability_decision",
)


def _object_pairs(pairs: List[Tuple[str, Any]]) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise StageCError("evidence_bundle", "duplicate JSON key: " + key)
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise StageCError("evidence_bundle", "non-finite JSON constant: " + value)


def _decode_json(raw: bytes, label: str) -> Dict[str, Any]:
    try:
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=_object_pairs,
                           parse_constant=_reject_constant)
    except (UnicodeDecodeError, json.JSONDecodeError, TypeError) as exc:
        raise StageCError("evidence_bundle", label + " is not valid UTF-8 JSON") from exc
    if not isinstance(value, dict):
        raise StageCError("evidence_bundle", label + " must be an object")
    return value


def _file_digest(raw: bytes) -> str:
    return sha256(raw).hexdigest()


def _all_false(value: Any, label: str) -> bool:
    return (isinstance(value, dict) and set(value) == set(AUTHORITY_FIELDS)
            and all(value[name] is False for name in AUTHORITY_FIELDS))


def _authority() -> Dict[str, bool]:
    return {name: False for name in AUTHORITY_FIELDS}


def _unresolved_review() -> Dict[str, Any]:
    return {"status": "unresolved", "review_sha256": None}


def _cell(row: Mapping[str, Any], name: str) -> Any:
    value = row.get(name)
    if not isinstance(value, dict) or "kind" not in value:
        raise StageCError("evidence_bundle", "retained Stage A cell differs")
    if value.get("kind") == "blob":
        return value.get("decoded")
    return value.get("value")


def _validate_stage_a(raw: bytes) -> Dict[str, Any]:
    if not isinstance(raw, (bytes, bytearray)) or _file_digest(bytes(raw)) != STAGE_A_BASELINE_SHA256:
        raise StageCError("evidence_bundle", "Stage A baseline bytes differ")
    value = _decode_json(bytes(raw), "Stage A baseline")
    database = value.get("database")
    before = database.get("before") if isinstance(database, dict) else None
    if not isinstance(before, dict) or before.get("sha256") != DATABASE_SHA256:
        raise StageCError("evidence_bundle", "Stage A database binding differs")
    tables = value.get("raw_tables")
    if not isinstance(tables, dict) or set(tables) != {
            "state", "reservations", "metering", "overhead", "store_identity"}:
        raise StageCError("evidence_bundle", "Stage A table inventory differs")
    reservations = tables.get("reservations", {}).get("rows")
    meters = tables.get("metering", {}).get("rows")
    if not isinstance(reservations, list) or len(reservations) != len(RESERVATION_IDS):
        raise StageCError("evidence_bundle", "Stage A reservation inventory differs")
    if not isinstance(meters, list) or len(meters) != 8:
        raise StageCError("evidence_bundle", "Stage A meter inventory differs")
    identifiers = {_cell(row, "id") for row in reservations if isinstance(row, dict)}
    if identifiers != set(RESERVATION_IDS):
        raise StageCError("evidence_bundle", "Stage A reservation identities differ")
    return value


def _validate_stage_d(capture_raw: bytes, expected_sha256: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    if not isinstance(capture_raw, (bytes, bytearray)):
        raise StageCError("evidence_bundle", "Stage D capture must be exact bytes")
    if _file_digest(bytes(capture_raw)) != expected_sha256:
        raise StageCError("evidence_bundle", "Stage D immutable byte digest differs")
    capture = _decode_json(bytes(capture_raw), "Stage D capture")
    if capture.get("capture_gate") != "PASS_LOCKED_READ_ONLY_EXTENDED_SCHEMA":
        raise StageCError("evidence_bundle", "Stage D capture gate differs")
    if capture.get("mutation_performed") is not False or not _all_false(capture.get("authority"), "capture authority"):
        raise StageCError("evidence_bundle", "Stage D capture asserts authority or mutation")
    schema = validate_schema_compatibility(capture.get("raw_schema"))
    quiescence = validate_quiescence_record(capture.get("quiescence"))
    return schema, quiescence


def _validate_postcapture(postcapture_raw: bytes, capture_sha256: str,
                          expected_sha256: str) -> Dict[str, Any]:
    if not isinstance(postcapture_raw, (bytes, bytearray)):
        raise StageCError("evidence_bundle", "postcapture record must be exact bytes")
    if _file_digest(bytes(postcapture_raw)) != expected_sha256:
        raise StageCError("evidence_bundle", "postcapture immutable byte digest differs")
    postcapture = _decode_json(bytes(postcapture_raw), "Stage D postcapture")
    checks = postcapture.get("checks")
    if (postcapture.get("all_immutable") is not True
            or postcapture.get("chronology_after_capture") is not True
            or postcapture.get("capture_sha256") != capture_sha256
            or not isinstance(checks, dict) or not checks or not all(item is True for item in checks.values())
            or not _all_false(postcapture.get("authority"), "postcapture authority")):
        raise StageCError("evidence_bundle", "postcapture immutability record differs")
    return postcapture


def _unresolved_provenance(row: Mapping[str, Any]) -> Dict[str, Any]:
    identifier = _cell(row, "id")
    return {
        "schema_version": 1,
        "record_type": "reservation-provenance-v1",
        "status": "unresolved",
        "reservation_id": identifier,
        "run": _cell(row, "run"),
        "stage": _cell(row, "stage"),
        "request": {
            "status": "missing", "raw_sha256": None,
            "canonical_sha256": None, "binding_authorized": False,
        },
        "issuer": {
            "status": "missing", "principal_id": None, "authenticated": False,
            "code_sha256": None, "toolchain_sha256": None,
            "policy_sha256": None, "runtime_profile_sha256": None,
        },
        "measurement": {
            "status": "missing", "started_at": None, "ended_at": None,
            "clock": None, "window_sha256": None,
        },
        "source": {
            "status": "missing", "path": None, "raw_sha256": None,
            "projection_sha256": None,
        },
        "meter": {"status": "missing", "meter_id": None, "usage_sha256": None},
        "review": _unresolved_review(),
        "authority": _authority(),
    }


def _unresolved_pending(row: Mapping[str, Any]) -> Dict[str, Any]:
    identifier = _cell(row, "id")
    maximum = _cell(row, "maximum")
    if identifier not in PENDING_IDS:
        raise StageCError("evidence_bundle", "non-pending row selected for pending sidecar")
    return {
        "schema_version": 1,
        "record_type": "pending-disposition-v1",
        "status": "unresolved",
        "reservation_id": identifier,
        "maximum": deepcopy(maximum),
        "request_id": None,
        "idempotency_key": None,
        "operation_id": None,
        "final_observation_sha256": None,
        "cessation": {
            "required": False,
            "observed": False,
            "method": "not-required",
            "evidence_sha256": digest({"descriptor": identifier + ":non-dispatch-unknown"}),
        },
        "dispatch": {"status": "unknown", "evidence_sha256": None},
        "evaluator_state": {"state": "active_or_unknown", "evidence_sha256": None},
        "baseline_before_sha256": DATABASE_SHA256,
        "baseline_after_sha256": DATABASE_SHA256,
        "stale_handles_accounted": False,
        "missing_evidence": [
            "dispatch-outcome", "final-observation", "cessation",
            "evaluator-stop-state", "stale-handle-accounting",
        ],
        "review": _unresolved_review(),
        "authority": _authority(),
    }


def _unresolved_completeness(rows: List[Mapping[str, Any]]) -> Dict[str, Any]:
    return {
        "schema_version": 1,
        "record_type": "historical-completeness-v1",
        "status": "unresolved",
        "lineage": [
            {
                "artifact": artifact,
                "status": "unresolved",
                "record_sha256": None,
                "unexplained": [artifact + "-record-unavailable"],
            } for artifact in sorted(LINEAGE_ARTIFACTS)
        ],
        "reservation_coverage": [
            {
                "reservation_id": _cell(row, "id"),
                "status": "unresolved",
                "record_sha256": None,
                "unexplained": [_cell(row, "id") + "-request-and-disposition-unavailable"],
            } for row in sorted(rows, key=lambda item: _cell(item, "id"))
        ],
        "operation_coverage": [
            {
                "status": "unresolved",
                "record_sha256": None,
                "unexplained": ["dispatch-cancel-failure-stop-replay-history"],
            }
        ],
        "side_store_coverage": [
            {
                "status": "unresolved",
                "record_sha256": None,
                "unexplained": ["side-ledger-export-adjustment-refund-replay-inventory"],
            }
        ],
        "overhead": {
            category: {
                "status": "unresolved",
                "actor": "unresolved",
                "boundary": "registration-through-current-database-snapshot",
                "source_sha256": digest({
                    "descriptor": category + "-overhead-domain",
                    "boundary": "registration-through-current-database-snapshot",
                }),
                "upper_bound_us": None,
            } for category in sorted(OVERHEAD_CATEGORIES)
        },
        "missing_history": [
            "issuer-authentication", "request-boundaries", "measurement-windows",
            "overlap-intervals", "paid-service", "manual-adjustments",
            "stop-and-recovery-lineage", "lost-or-never-created-records",
        ],
        "unbounded_unknown": True,
        "review": _unresolved_review(),
        "authority": _authority(),
    }


def assemble_evidence_bundle(stage_a_raw: bytes, stage_d_capture_raw: bytes,
                             stage_d_postcapture_raw: bytes, *,
                             stage_d_capture_sha256: str,
                             stage_d_postcapture_sha256: str,
                             created_at: str,
                             stage_d_review: str = "STAGE_D_NARROW_REWORK_REVIEW: APPROVED") -> Dict[str, Any]:
    """Assemble a structurally valid but deliberately unresolved v2 bundle."""
    if stage_d_capture_sha256 != APPROVED_STAGE_D_CAPTURE_SHA256:
        raise StageCError("evidence_bundle", "Stage D capture is not the approved byte digest")
    if stage_d_postcapture_sha256 != APPROVED_STAGE_D_POSTCAPTURE_SHA256:
        raise StageCError("evidence_bundle", "Stage D postcapture is not the approved byte digest")
    if stage_d_review != "STAGE_D_NARROW_REWORK_REVIEW: APPROVED":
        raise StageCError("evidence_bundle", "Stage D independent review is not approved")
    if not isinstance(created_at, str) or not created_at:
        raise StageCError("evidence_bundle", "bundle creation timestamp differs")
    stage_a = _validate_stage_a(stage_a_raw)
    schema, quiescence_validation = _validate_stage_d(
        stage_d_capture_raw, stage_d_capture_sha256)
    stage_d_capture = _decode_json(stage_d_capture_raw, "Stage D capture")
    stage_d_postcapture = _validate_postcapture(
        stage_d_postcapture_raw, stage_d_capture_sha256, stage_d_postcapture_sha256)
    rows = stage_a["raw_tables"]["reservations"]["rows"]
    provenance = [_unresolved_provenance(row) for row in
                  sorted(rows, key=lambda item: _cell(item, "id"))]
    pending = [_unresolved_pending(row) for row in
               sorted(rows, key=lambda item: _cell(item, "id"))
               if _cell(row, "id") in PENDING_IDS]
    completeness = _unresolved_completeness(rows)

    for record in provenance:
        validate_provenance_record(record, stage_a_raw)
    for record in pending:
        validate_pending_disposition(record)
    validate_completeness_record(completeness)

    gate_inventory = {
        "schema_compatibility": {
            "status": "pass",
            "evidence": [schema["raw_schema_sha256"], schema["mapped_contract_schema_sha256"]],
        },
        "quiescence": {
            "status": "unresolved",
            "evidence": [stage_d_capture_sha256],
            "reason": "locked capture validated; independently proven writer exclusion remains unresolved",
        },
        "provenance": {
            "status": "unresolved",
            "evidence": [record["reservation_id"] for record in provenance],
        },
        "pending_evidence": {
            "status": "unresolved",
            "evidence": [record["reservation_id"] for record in pending],
        },
        "overhead_completeness": {
            "status": "unresolved",
            "evidence": sorted(OVERHEAD_CATEGORIES),
        },
        "historical_completeness": {
            "status": "unresolved",
            "evidence": sorted(LINEAGE_ARTIFACTS),
        },
        "independent_review": {"status": "unresolved", "evidence": []},
        "operator_decision": {"status": "unresolved", "evidence": []},
        "spendability_decision": {"status": "unresolved", "evidence": []},
    }
    return {
        "schema_version": 2,
        "record_type": "spendability-evidence-bundle-v2",
        "basis": {
            "stage_a_baseline_sha256": STAGE_A_BASELINE_SHA256,
            "stage_d_capture_sha256": stage_d_capture_sha256,
            "stage_d_postcapture_sha256": stage_d_postcapture_sha256,
            "database_sha256": DATABASE_SHA256,
            "stage_d_independent_review": stage_d_review,
            "created_at": created_at,
        },
        "raw_rows": deepcopy(stage_a["raw_tables"]),
        "schema_compatibility": schema,
        "quiescence": {
            "record": deepcopy(stage_d_capture["quiescence"]),
            "validation": quiescence_validation,
        },
        "postcapture_immutable": deepcopy(stage_d_postcapture),
        "provenance": provenance,
        "pending_dispositions": pending,
        "historical_completeness": completeness,
        "gate_inventory": gate_inventory,
        "assembly_valid": True,
        "evidence_valid": False,
        "outcome": {
            "valid": False,
            "first_failed_gate": "quiescence",
            "spendable": None,
            "allowed_mutations": [],
            "execution_authorized": False,
        },
        "authority": _authority(),
    }


def validate_evidence_bundle(bundle: Mapping[str, Any], stage_a_raw: bytes,
                             stage_d_capture_raw: bytes,
                             stage_d_postcapture_raw: bytes) -> Dict[str, Any]:
    """Validate an existing bundle by exact regeneration from retained inputs."""
    if not isinstance(bundle, dict) or set(bundle) != set(BUNDLE_FIELDS):
        raise StageCError("evidence_bundle", "bundle top-level schema differs")
    basis = bundle.get("basis")
    if not isinstance(basis, dict) or set(basis) != BASIS_FIELDS | {"created_at"}:
        raise StageCError("evidence_bundle", "bundle basis schema differs")
    expected = assemble_evidence_bundle(
        stage_a_raw, stage_d_capture_raw, stage_d_postcapture_raw,
        stage_d_capture_sha256=basis.get("stage_d_capture_sha256"),
        stage_d_postcapture_sha256=basis.get("stage_d_postcapture_sha256"),
        created_at=basis.get("created_at"),
        stage_d_review=basis.get("stage_d_independent_review"),
    )
    if digest(bundle) != digest(expected):
        raise StageCError("evidence_bundle", "bundle differs from exact regeneration")
    return {
        "assembly_valid": True,
        "evidence_valid": False,
        "first_failed_gate": "quiescence",
        "spendable": None,
        "allowed_mutations": [],
        "execution_authorized": False,
    }
