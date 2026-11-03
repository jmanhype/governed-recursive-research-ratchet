"""Validate local Stage G spendability evidence candidates without authority."""

from hashlib import sha256
import base64
import json
from pathlib import Path
import sqlite3
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

from spendability_stage_c import (
    AUTHORITY_FIELDS,
    LINEAGE_ARTIFACTS,
    PENDING_IDS,
    RESERVATION_IDS,
    StageCError,
)


STAGE_A_BASELINE_SHA256 = "7608cbe6fc5f671b88573eca8b642ebfbc172f0cb920f75d60ca34cfa60c730a"
STAGE_F_REQUEST_SHA256 = "6c59851d15fa44afccc3907e0aa0bedd7eb629095898d50b51a53079183cf919"
STAGE_F_PACKAGE_SHA256 = "388b0022adfba2a2e60ca436239178fa07589b4ffbe724bae6b5f847a2e4be23"
TRUSTED_EXPORT_READBACK_SHA256 = "2bbdb46aced148263505a775cee3e5033c20c337d1da6a73e875c87f62a821a8"
TRUSTED_EXPORT_LEDGER_SHA256 = "11e3fba4f8ff3f1b27d65c359e76c1c99465164970e7d4f050c072cbf49feb09"
TRUSTED_EXPORT_SNAPSHOT_SHA256 = "745f5d2c9086550c184cccd484023d5e490f0c082550eb55524adf25948ac513"
TRUSTED_EXPORT_SNAPSHOT_ID = "a070c21845becd209d3ed84591d4d8c95db8604783cc76a997b829cc901760f6"
STAGE_F_REVIEW = "STAGE_F_REQUEST_REVIEW: APPROVED"
STAGE_G_CREATED_AT = "2026-10-28T00:45:00Z"
PROJECT_ROOT = Path(__file__).resolve().parents[1]

DISCOVERY_OBSERVATIONS = {
    "schema_version": 1,
    "record_kind": "manual-discovery-observations-not-exhaustive-search-proof",
    "generator_consumes_search_receipts": False,
    "protected_paths_accessed_by_generator": [],
    "roots": [
        {"kind": "repository-working-tree", "path": "docs/research/scripts/tests",
         "method": "exact reservation-id and exact SHA-256 byte scan",
         "evidence_status": "manual-observation-not-consumed-by-generator"},
        {"kind": "git-object-database", "path": ".git/objects",
         "method": "hash each blob no larger than 2 MiB",
         "evidence_status": "manual-observation-not-consumed-by-generator"},
        {"kind": "operator-session-archive", "path": "/Users/speed/.codex/sessions/2026/10",
         "method": "exact reservation-id and target-lineage-hash scan",
         "evidence_status": "manual-observation-not-consumed-by-generator"},
        {"kind": "operator-memory-and-attachments",
         "path": "/Users/speed/.codex/memories and /Users/speed/.codex/attachments",
         "method": "exact reservation-id and target-lineage-hash scan",
         "evidence_status": "manual-observation-not-consumed-by-generator"},
        {"kind": "project-output-archive",
         "path": "/Users/speed/Documents/Codex/2026-10-19/3e4m-b-4",
         "method": "exact-id, exact-hash, and named GRRR artifact inventory",
         "evidence_status": "manual-observation-not-consumed-by-generator"},
        {"kind": "top-level-temporary-grrr-artifacts", "path": "/private/tmp",
         "method": "top-level exact GRRR filename and target-hash scan only",
         "evidence_status": "manual-observation-not-consumed-by-generator"},
    ],
    "exclusions": [
        "credentials and API tokens were not searched or copied",
        "unrelated private log content was not printed or retained",
        "/Library/GRRR was not accessed in this Stage G slice",
        "no remote or network archive was queried",
        "agent/session records are discovery leads only and are not evaluator receipts",
        "negative results are not established by this generator",
        "manual observations are not treated as exhaustive search boundaries",
    ],
}


def _bytes_digest(raw: bytes) -> str:
    return sha256(raw).hexdigest()


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("ascii")


def _require(condition: bool, detail: str) -> None:
    if not condition:
        raise StageCError("evidence_search", detail)


def _decode(raw: bytes, label: str) -> Dict[str, Any]:
    def pairs(values: Sequence[Tuple[str, Any]]) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        for key, value in values:
            if key in result:
                raise StageCError("evidence_search", label + " has duplicate key " + key)
            result[key] = value
        return result

    def constant(value: str) -> None:
        raise StageCError("evidence_search", label + " has non-finite constant " + value)

    try:
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=pairs,
                           parse_constant=constant)
    except (UnicodeDecodeError, json.JSONDecodeError, TypeError) as exc:
        raise StageCError("evidence_search", label + " is not valid UTF-8 JSON") from exc
    _require(isinstance(value, dict), label + " must be an object")
    return value


def _cell(row: Mapping[str, Any], name: str) -> Any:
    value = row.get(name)
    _require(isinstance(value, dict) and "kind" in value,
             "Stage A raw row cell differs: " + name)
    return value.get("decoded") if value.get("kind") == "blob" else value.get("value")


def _raw_cell(row: Mapping[str, Any], name: str) -> bytes:
    value = row.get(name)
    _require(isinstance(value, dict) and value.get("kind") == "blob",
             "Stage A raw BLOB differs: " + name)
    encoded = value.get("blob_hex")
    _require(isinstance(encoded, str) and len(encoded) % 2 == 0,
             "Stage A raw BLOB encoding differs: " + name)
    try:
        return bytes.fromhex(encoded)
    except ValueError as exc:
        raise StageCError("evidence_search", "Stage A raw BLOB hex differs: " + name) from exc


def _artifact(path: Path, expected: Optional[str] = None) -> Dict[str, Any]:
    raw = path.read_bytes()
    resolved = path.resolve()
    try:
        portable = resolved.relative_to(PROJECT_ROOT)
    except ValueError:
        portable = resolved
    result = {"path": str(portable), "bytes": len(raw), "sha256": _bytes_digest(raw)}
    if expected is not None:
        _require(result["sha256"] == expected, "artifact bytes differ: " + str(path))
    return result


def _authority() -> Dict[str, bool]:
    return {name: False for name in AUTHORITY_FIELDS}


def _validate_request(raw: bytes) -> Dict[str, Any]:
    _require(_bytes_digest(raw) == STAGE_F_REQUEST_SHA256, "Stage F request bytes differ")
    value = _decode(raw, "Stage F request")
    _require(value.get("request_kind") == "spendability-evidence-request-v1",
             "Stage F request kind differs")
    _require(value.get("status") == "open", "Stage F request status differs")
    _require(not any(value.get("authority", {}).values()), "Stage F request authority differs")
    _require(value.get("outcome", {}).get("spendable") is None,
             "Stage F request spendability differs")
    items = value.get("requested_evidence")
    _require(isinstance(items, list) and len(items) == 30, "Stage F request inventory differs")
    identifiers = [item.get("id") for item in items]
    _require(len(identifiers) == len(set(identifiers)) == 30,
             "Stage F request identifiers differ")
    return value


def _validate_stage_f_package(raw: bytes) -> Dict[str, Any]:
    _require(_bytes_digest(raw) == STAGE_F_PACKAGE_SHA256, "Stage F package bytes differ")
    package = _decode(raw, "Stage F package")
    _require(package.get("independent_review") == STAGE_F_REVIEW,
             "Stage F independent review differs")
    artifacts = package.get("artifacts")
    _require(isinstance(artifacts, dict) and len(artifacts) == 10,
             "Stage F package inventory differs")
    request_entry = artifacts.get("docs/evidence/spendability/stage-f/REQUEST.json")
    _require(isinstance(request_entry, dict)
             and request_entry.get("sha256") == STAGE_F_REQUEST_SHA256,
             "Stage F package request binding differs")
    _require(not any(package.get("authority", {}).values()),
             "Stage F package authority differs")
    return package


def _validate_stage_a(raw: bytes) -> Dict[str, Any]:
    _require(_bytes_digest(raw) == STAGE_A_BASELINE_SHA256, "Stage A baseline bytes differ")
    value = _decode(raw, "Stage A baseline")
    reservations = value.get("raw_tables", {}).get("reservations", {}).get("rows")
    metering = value.get("raw_tables", {}).get("metering", {}).get("rows")
    _require(isinstance(reservations, list) and len(reservations) == 11,
             "Stage A reservation inventory differs")
    _require(isinstance(metering, list) and len(metering) == 8,
             "Stage A meter inventory differs")
    identifiers = {_cell(row, "id") for row in reservations}
    _require(identifiers == set(RESERVATION_IDS), "Stage A reservation IDs differ")
    return value


def _validate_trusted_export(root: Path) -> Dict[str, Any]:
    readback_path = root / "READBACK.json"
    ledger_path = root / "evaluator/ledger.sqlite"
    snapshot_path = root / "evaluator/snapshot.json"
    readback_raw = readback_path.read_bytes()
    ledger_raw = ledger_path.read_bytes()
    snapshot_raw = snapshot_path.read_bytes()
    _require(_bytes_digest(readback_raw) == TRUSTED_EXPORT_READBACK_SHA256,
             "trusted export readback bytes differ")
    _require(_bytes_digest(ledger_raw) == TRUSTED_EXPORT_LEDGER_SHA256,
             "trusted export ledger bytes differ")
    _require(_bytes_digest(snapshot_raw) == TRUSTED_EXPORT_SNAPSHOT_SHA256,
             "trusted export snapshot bytes differ")

    readback = _decode(readback_raw, "trusted export readback")
    snapshot = _decode(snapshot_raw, "trusted export snapshot")
    _require(readback.get("snapshot_id") == TRUSTED_EXPORT_SNAPSHOT_ID,
             "trusted readback snapshot identity differs")
    _require(snapshot.get("snapshot_id") == TRUSTED_EXPORT_SNAPSHOT_ID,
             "trusted snapshot identity differs")
    _require(readback.get("ledger_events") == 30 and readback.get("ledger_objects") == 8,
             "trusted readback counts differ")
    _require(readback.get("successor_reservations") == 11
             and readback.get("successor_settled") == 8
             and readback.get("successor_pending") == 3
             and readback.get("successor_stopped") is True,
             "trusted readback accounting counts differ")

    connection = sqlite3.connect("file:" + str(ledger_path) + "?mode=ro&immutable=1", uri=True)
    try:
        rows = connection.execute(
            "SELECT seq,prior,hash,body FROM events ORDER BY seq").fetchall()
    finally:
        connection.close()
    _require(len(rows) == 30, "trusted ledger event count differs")
    expected_prior = "0" * 64
    events: List[Dict[str, Any]] = []
    idempotency_keys = set()
    for expected_sequence, (sequence, prior, hashed, body_raw) in enumerate(rows, 1):
        _require(sequence == expected_sequence, "trusted ledger sequence differs")
        _require(prior == expected_prior, "trusted ledger prior differs")
        _require(_bytes_digest(expected_prior.encode("ascii") + body_raw) == hashed,
                 "trusted ledger event hash differs")
        body = _decode(body_raw, "trusted ledger event")
        key = body.get("idempotency_key")
        _require(isinstance(key, str) and key not in idempotency_keys,
                 "trusted ledger idempotency key differs")
        idempotency_keys.add(key)
        events.append({"seq": sequence, "prior": prior, "hash": hashed, "body": body})
        expected_prior = hashed

    projected_events = [
        {"sequence": row["seq"], "prior": row["prior"], "digest": row["hash"],
         "event": row["body"]}
        for row in events
    ]
    _require(snapshot.get("events") == projected_events,
             "trusted snapshot event projection differs")
    _require(snapshot.get("receipt", {}).get("digest") == events[-1]["hash"],
             "trusted snapshot receipt differs")
    snapshot_identity = dict(snapshot)
    declared_identity = snapshot_identity.pop("snapshot_id")
    _require(sha256(_canonical(snapshot_identity)).hexdigest() == declared_identity,
             "trusted snapshot identity calculation differs")

    expected_objects = set(snapshot.get("objects", {}))
    _require(len(expected_objects) == 8, "trusted snapshot object inventory differs")
    object_directory = root / "evaluator/objects"
    actual_objects = {path.name for path in object_directory.iterdir() if path.is_file()}
    _require(actual_objects == expected_objects | {TRUSTED_EXPORT_SNAPSHOT_SHA256},
             "trusted object directory differs")
    for name, encoded in snapshot["objects"].items():
        expected_bytes = bytes.fromhex(encoded)
        object_path = object_directory / name
        raw = object_path.read_bytes()
        _require(_bytes_digest(raw) == name and raw == expected_bytes,
                 "trusted snapshot object bytes differ: " + name)
    snapshot_copy = object_directory / TRUSTED_EXPORT_SNAPSHOT_SHA256
    _require(snapshot_copy.read_bytes() == snapshot_raw, "trusted snapshot object copy differs")

    reservation_events: Dict[str, Dict[str, Any]] = {}
    observation_objects: Dict[str, Dict[str, Any]] = {}
    gate_events: Dict[str, List[Dict[str, Any]]] = {}
    run_to_reservation: Dict[str, str] = {}
    for row in events:
        body = row["body"]
        if body.get("kind") == "reserved-before-dispatch":
            request = body.get("request")
            _require(isinstance(request, dict), "trusted reservation request differs")
            reservation = request.get("reservation")
            _require(reservation in RESERVATION_IDS, "trusted reservation identifier differs")
            _require(reservation not in reservation_events,
                     "trusted reservation event is duplicated")
            reservation_events[reservation] = row
            run_to_reservation[request.get("run")] = reservation
        elif body.get("kind") == "trusted-receipt":
            for name in body.get("objects", []):
                object_path = object_directory / name
                observation = _decode(object_path.read_bytes(), "trusted observation object")
                reservation = observation.get("reservation")
                _require(reservation in RESERVATION_IDS,
                         "trusted observation reservation differs")
                _require(reservation not in observation_objects,
                         "trusted observation object is duplicated")
                _require(observation.get("run") == body.get("run"),
                         "trusted observation run differs")
                raw = base64.b64decode(observation.get("raw_base64", ""), validate=True)
                _require(len(raw) == observation.get("raw_bytes")
                         and _bytes_digest(raw) == observation.get("raw_sha256"),
                         "trusted observation raw digest differs")
                observation_objects[reservation] = {
                    "object": name, "event": row, "record": observation,
                }
        elif body.get("kind") == "gate":
            reservation = run_to_reservation.get(body.get("run"))
            if reservation is not None:
                gate_events.setdefault(reservation, []).append(row)

    _require(set(reservation_events) == set(RESERVATION_IDS),
             "trusted reservation event coverage differs")
    _require(set(observation_objects) == set(RESERVATION_IDS) - set(PENDING_IDS),
             "trusted observation coverage differs")
    _require(set(PENDING_IDS).isdisjoint(observation_objects),
             "pending reservation has an observation receipt")
    return {
        "readback": _artifact(readback_path, TRUSTED_EXPORT_READBACK_SHA256),
        "ledger": _artifact(ledger_path, TRUSTED_EXPORT_LEDGER_SHA256),
        "snapshot": _artifact(snapshot_path, TRUSTED_EXPORT_SNAPSHOT_SHA256),
        "events": events,
        "reservation_events": reservation_events,
        "observation_objects": observation_objects,
        "gate_events": gate_events,
    }


def _stage_a_meter_index(stage_a: Mapping[str, Any]) -> Dict[str, Dict[str, Any]]:
    result: Dict[str, Dict[str, Any]] = {}
    for row in stage_a["raw_tables"]["metering"]["rows"]:
        reservation = _cell(row, "reservation")
        receipt = _cell(row, "id")
        body = _raw_cell(row, "body")
        decoded = json.loads(body.decode("utf-8"))
        _require(reservation not in result, "Stage A meter row is duplicated")
        _require(_bytes_digest(body) == receipt, "Stage A meter receipt digest differs")
        _require(decoded.get("reservation") == reservation,
                 "Stage A meter reservation join differs")
        result[reservation] = {
            "receipt": receipt,
            "decoded": decoded,
            "artifact": "docs/evidence/spendability/stage-a/BASELINE.json",
        }
    _require(set(result) == set(RESERVATION_IDS) - set(PENDING_IDS),
             "Stage A settled meter coverage differs")
    return result


def _validate_reservation_joins(stage_a: Mapping[str, Any],
                                trusted: Mapping[str, Any]) -> Dict[str, Dict[str, Any]]:
    meters = _stage_a_meter_index(stage_a)
    reservations = {
        _cell(row, "id"): row for row in stage_a["raw_tables"]["reservations"]["rows"]
    }
    validated: Dict[str, Dict[str, Any]] = {}
    for reservation in sorted(RESERVATION_IDS):
        row = reservations[reservation]
        event = trusted["reservation_events"][reservation]
        request_record = event["body"]["request"]
        actual = _cell(row, "actual")
        receipt = _cell(row, "receipt")
        _require(request_record.get("run") == _cell(row, "run"),
                 "trusted request/Stage A run join differs")
        _require(event["body"].get("maximum") == json.loads(_raw_cell(row, "maximum")),
                 "trusted request/Stage A maximum join differs")
        if reservation in PENDING_IDS:
            _require(actual is None and receipt is None, "pending Stage A settlement differs")
            _require(reservation not in meters, "pending Stage A meter differs")
            validated[reservation] = {
                "state": "pending",
                "request_event": event,
                "observation": None,
                "meter": None,
                "gates": trusted["gate_events"].get(reservation, []),
            }
            continue
        observation = trusted["observation_objects"][reservation]
        meter = meters[reservation]
        _require(actual == meter["decoded"]["usage"], "Stage A actual/meter usage join differs")
        _require(receipt == meter["receipt"], "Stage A receipt/meter join differs")
        _require(meter["decoded"].get("evidence") == observation["object"],
                 "Stage A meter/observation join differs")
        validated[reservation] = {
            "state": "settled",
            "request_event": event,
            "observation": observation,
            "meter": meter,
            "gates": trusted["gate_events"].get(reservation, []),
        }
    return validated


def _lineage_targets(stage_a: Mapping[str, Any]) -> Dict[str, Dict[str, Any]]:
    source_files = stage_a.get("source_files", {})
    database = stage_a.get("database", {})
    targets: Dict[str, Dict[str, Any]] = {}
    for artifact in LINEAGE_ARTIFACTS:
        if artifact == "database_snapshot":
            record = database.get("after", {})
            targets[artifact] = {
                "expected_sha256": record.get("sha256"),
                "expected_bytes": record.get("size"),
                "declared_path": database.get("path"),
            }
        else:
            record = source_files.get(artifact)
            _require(isinstance(record, dict), "Stage A lineage source differs")
            targets[artifact] = {
                "expected_sha256": record.get("sha256"),
                "expected_bytes": record.get("size"),
                "declared_path": record.get("path"),
            }
    _require(len(targets) == 8, "lineage target inventory differs")
    return targets


def _item_record(item: Mapping[str, Any], joins: Mapping[str, Any],
                 lineage: Mapping[str, Any]) -> Dict[str, Any]:
    kind = item.get("kind")
    subject = item.get("subject")
    record: Dict[str, Any] = {
        "request_item_id": item.get("id"),
        "kind": kind,
        "subject": subject,
        "classification": None,
        "independent_review_required": True,
    }
    if kind == "reservation-provenance" and subject in joins:
        join = joins[subject]
        record["search_status"] = (
            "validated-original-record-candidate" if join["state"] == "settled"
            else "partial-pending-record-candidate"
        )
        artifacts = [{
            "role": "reservation-request-event",
            "path": "docs/evidence/trusted-observation/v4-run-9d3df87/evaluator/ledger.sqlite",
            "event_seq": join["request_event"]["seq"],
            "event_sha256": join["request_event"]["hash"],
        }]
        if join["state"] == "settled":
            artifacts.extend([
                {
                    "role": "trusted-observation-object",
                    "path": "docs/evidence/trusted-observation/v4-run-9d3df87/evaluator/objects/"
                            + join["observation"]["object"],
                    "sha256": join["observation"]["object"],
                },
                {
                    "role": "meter-body-exact-copy",
                    "path": join["meter"]["artifact"],
                    "meter_receipt_sha256": join["meter"]["receipt"],
                },
            ])
            record["candidate_completeness"] = "request-observation-and-meter-join"
        else:
            record["candidate_completeness"] = "request-only"
            record["unresolved"] = [
                "definitive dispatch or non-dispatch disposition",
                "cessation and stale-handle proof",
                "pre/post database identity for this operation",
            ]
        record["artifacts"] = artifacts
        return record
    if kind == "pending-disposition" and subject in joins:
        join = joins[subject]
        record["search_status"] = "partial-pending-record-candidate"
        record["candidate_completeness"] = "request-and-gate-only"
        record["artifacts"] = [{
            "role": "reservation-request-event",
            "path": "docs/evidence/trusted-observation/v4-run-9d3df87/evaluator/ledger.sqlite",
            "event_seq": join["request_event"]["seq"],
            "event_sha256": join["request_event"]["hash"],
        }]
        record["unresolved"] = [
            "final observation or explicit non-observation",
            "cessation proof",
            "stale-handle accounting",
            "pre/post database identity",
        ]
        return record
    if kind == "historical-lineage":
        target = lineage[subject]
        record["search_status"] = "search-completeness-not-established"
        record["expected_sha256"] = target["expected_sha256"]
        record["expected_bytes"] = target["expected_bytes"]
        record["declared_path"] = target["declared_path"]
        record["unresolved"] = ["exact artifact bytes and custody"]
        return record
    if kind == "operation-history":
        record["search_status"] = "partial-evaluator-export-only"
        record["candidate_completeness"] = "11-reservations-8-observations-30-events"
        record["unresolved"] = ["complete campaign operation and overlap history"]
        return record
    if kind in ("side-store-history", "overhead-domain", "global-historical-completeness"):
        record["search_status"] = "search-completeness-not-established"
        record["unresolved"] = ["original-domain record and complete absence boundary"]
        return record
    raise StageCError("evidence_search", "unsupported Stage F request item")


def build_external_evidence_search(request_raw: bytes, package_raw: bytes,
                                   stage_a_raw: bytes, export_root: Path,
                                   created_at: str = STAGE_G_CREATED_AT) -> Dict[str, Any]:
    request = _validate_request(request_raw)
    _validate_stage_f_package(package_raw)
    stage_a = _validate_stage_a(stage_a_raw)
    trusted = _validate_trusted_export(export_root)
    joins = _validate_reservation_joins(stage_a, trusted)
    lineage = _lineage_targets(stage_a)
    items = [_item_record(item, joins, lineage) for item in request["requested_evidence"]]
    complete_candidates = sum(
        item.get("candidate_completeness") == "request-observation-and-meter-join"
        for item in items
    )
    partial_candidates = sum(
        str(item.get("search_status", "")).startswith("partial") for item in items
    )
    return {
        "schema_version": 1,
        "record_type": "spendability-external-evidence-search-v1",
        "created_at": created_at,
        "basis": {
            "stage_a_baseline_sha256": STAGE_A_BASELINE_SHA256,
            "stage_f_request_sha256": STAGE_F_REQUEST_SHA256,
            "stage_f_package_sha256": STAGE_F_PACKAGE_SHA256,
            "stage_f_independent_review": STAGE_F_REVIEW,
            "trusted_export_snapshot_id": TRUSTED_EXPORT_SNAPSHOT_ID,
            "trusted_export_readback_sha256": TRUSTED_EXPORT_READBACK_SHA256,
            "trusted_export_ledger_sha256": TRUSTED_EXPORT_LEDGER_SHA256,
            "trusted_export_snapshot_sha256": TRUSTED_EXPORT_SNAPSHOT_SHA256,
        },
        "discovery_observations": DISCOVERY_OBSERVATIONS,
        "validated_sources": {
            "stage_a_baseline": _artifact(
                Path("docs/evidence/spendability/stage-a/BASELINE.json"),
                STAGE_A_BASELINE_SHA256),
            "trusted_observation_export": {
                "readback": trusted["readback"],
                "ledger": trusted["ledger"],
                "snapshot": trusted["snapshot"],
                "event_count": 30,
                "observation_object_count": 8,
                "reservation_count": 11,
            },
        },
        "items": items,
        "summary": {
            "total_items": len(items),
            "validated_complete_candidate_items": complete_candidates,
            "partial_candidate_items": partial_candidates,
            "negative_search_not_established": sum(
                item.get("search_status") == "search-completeness-not-established"
                for item in items
            ),
            "final_classifications_made": 0,
        },
        "outcome": {
            "classification_complete": False,
            "spendable": None,
            "valid": False,
            "execution_authorized": False,
            "allowed_mutations": [],
        },
        "authority": _authority(),
    }


def validate_external_evidence_search(record: Mapping[str, Any], request_raw: bytes,
                                      package_raw: bytes, stage_a_raw: bytes,
                                      export_root: Path) -> Dict[str, Any]:
    expected = build_external_evidence_search(
        request_raw, package_raw, stage_a_raw, export_root,
        created_at=record.get("created_at", "")
    )
    if record != expected:
        raise StageCError("evidence_search", "record differs from exact regeneration")
    return {
        "record_valid": True,
        "classification_complete": False,
        "spendable": None,
        "allowed_mutations": [],
        "execution_authorized": False,
    }
