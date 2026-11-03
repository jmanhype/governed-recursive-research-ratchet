"""Build the fail-closed Stage L per-request evidence search record."""

from hashlib import sha256
import json
from pathlib import Path
import re
import sqlite3
from typing import Any, Dict, List, Mapping, Sequence, Tuple

from spendability_stage_c import AUTHORITY_FIELDS, StageCError


STAGE_K_COMMIT = "3cfaeb7e5b54c884ad794c5c1b7b72cc6dd63a6a"
STAGE_K_PACKAGE_SHA256 = "9bea19bfa163b47b909356f7efe274a8536851e54f1b136c1f882425bdeaf8f2"
STAGE_K_MATRIX_SHA256 = "d71139015cd3b27683503984947ba692800e407aecd6f45d1ccf6e3c18ecd4d1"
STAGE_J_PACKAGE_SHA256 = "7a2251decd3073aaa268e2dabdeb16f4d9d8f9283536760c38ad4d6b5ab1c53e"
STAGE_A_BASELINE_SHA256 = "7608cbe6fc5f671b88573eca8b642ebfbc172f0cb920f75d60ca34cfa60c730a"
TRUSTED_LEDGER_SHA256 = "11e3fba4f8ff3f1b27d65c359e76c1c99465164970e7d4f050c072cbf49feb09"
SESSION_SOURCE_SHA256 = "a595ff5c996d5d673e005a3d55e0b82a3a8187ed5693b2c232a0f16e771fa80e"
SESSION_LINE_11533_SHA256 = "9ab13249897f4508a2410ba4eabbf29becaab434e7fba8cc3ab551f25650ae60"
SESSION_LINE_11534_SHA256 = "e1b73e4b545b93cbc43164effce8e9e6f10c4c38ca11095e3b5f1b89fc4f1cd8"
RETAINED_SESSION_SEARCH_SHA256 = "e568f36d965aa425971744573b562f005c3f1279ba73fef7610bc495224faaa3"
SESSION_SOURCE_PATH = Path(
    "/Users/speed/.codex/sessions/2026/10/20/"
    "rollout-2026-10-20T06-57-58-01a156c2-7319-7bc3-a65c-b516699997ee_"
    "01a1592c-ec38-7e22-af4c-1b1997276e76.jsonl"
)
STAGE_L_CREATED_AT = "2026-10-28T18:15:00Z"

RESERVATION_IDS = (
    "1bf9d516461040c0baef70648c074d61",
    "5b7851814d764da1a3b3830abc9853ce",
    "7ecc4c7e17f742dc9ec2a8c6dada50f2",
    "b954f6890a1e43e3b13f24298fa7ca33",
    "b95be730d6a5408886071d29848bbd05",
    "d3c965a29ab547c999e66bf0b60eca9f",
    "e38c33051ff64b4eab106e65a200fe06",
    "eb045d10d73b48ef9d570a1cf870f6eb",
)
RUN_IDS = (
    "e55f8e3b44604e509fb005d76d0d7e9f",
    "283eab529e1c491583775cbe1a8f1c89",
    "93135d89fa334ec09d87b655db72c5b7",
    "d6cdf6f3f93a4fc6ab154020c8cc221d",
    "2e1a9c4468794c128d80a568e26752da",
    "20849b384ed641ca9f8e5c6f880d96dd",
    "3848e1bb84214727b5647e4085b0257a",
    "60fa3361bf5640be8b251e6a1eab93bd",
)
TARGET_FIELDS = (
    "principal", "issuer", "operation_id", "operation", "started_at",
    "ended_at", "clock", "window_sha256", "created_at",
    "artifact_creation_timestamp",
)


def _digest(raw: bytes) -> str:
    return sha256(raw).hexdigest()


def _decode(raw: bytes, label: str) -> Dict[str, Any]:
    def pairs(values: Sequence[Tuple[str, Any]]) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        for key, value in values:
            if key in result:
                raise StageCError("request_search", label + " has duplicate key " + key)
            result[key] = value
        return result

    def reject(value: str) -> None:
        raise StageCError("request_search", label + " has non-finite constant " + value)

    try:
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=pairs,
                           parse_constant=reject)
    except (UnicodeDecodeError, json.JSONDecodeError, TypeError, ValueError) as exc:
        raise StageCError("request_search", label + " is not valid UTF-8 JSON") from exc
    if not isinstance(value, dict):
        raise StageCError("request_search", label + " must be an object")
    return value


def _require(condition: bool, detail: str) -> None:
    if not condition:
        raise StageCError("request_search", detail)


def _artifact(path: Path, expected: str) -> Dict[str, Any]:
    raw = path.read_bytes()
    actual = _digest(raw)
    _require(actual == expected, "artifact bytes differ: " + str(path))
    try:
        portable = path.resolve().relative_to(Path(__file__).resolve().parents[1])
    except ValueError:
        portable = path.resolve()
    return {"path": str(portable), "bytes": len(raw), "sha256": actual}


def _target_hits(value: Any) -> List[Dict[str, str]]:
    hits: List[Dict[str, str]] = []

    def walk(item: Any, path: str = "") -> None:
        if isinstance(item, dict):
            for key, child in item.items():
                child_path = (path + "/" if path else "") + str(key)
                if str(key).lower() in TARGET_FIELDS:
                    hits.append({
                        "field": str(key),
                        "path": child_path,
                        "value_kind": (type(child).__name__
                                       if isinstance(child, (dict, list)) else
                                       "scalar"),
                    })
                walk(child, child_path)
        elif isinstance(item, list):
            for index, child in enumerate(item):
                walk(child, path + "/" + str(index))

    walk(value)
    return hits


def _validate_stage_k(root: Path) -> Dict[str, Any]:
    package = root / "docs/evidence/spendability/stage-k/PACKAGE.json"
    matrix = root / "docs/evidence/spendability/stage-k/PER-RECORD-MATRIX.json"
    _require(_digest(package.read_bytes()) == STAGE_K_PACKAGE_SHA256,
             "Stage K package bytes differ")
    matrix_raw = matrix.read_bytes()
    _require(_digest(matrix_raw) == STAGE_K_MATRIX_SHA256,
             "Stage K matrix bytes differ")
    package_value = _decode(package.read_bytes(), "Stage K package")
    matrix_value = _decode(matrix_raw, "Stage K matrix")
    _require(package_value.get("base_commit") == "9b58eae0ba62d0d384a4743ea069bf3dde6c9f6d",
             "Stage K package base differs")
    _require(package_value.get("independent_review")
             == "STAGE_K_PER_RECORD_NARROW_REWORK_REVIEW: APPROVED",
             "Stage K review differs")
    _require(matrix_value.get("summary", {}).get("candidate_record_sets") == 8,
             "Stage K candidate count differs")
    return matrix_value


def _serialized_target_hits(raw: bytes) -> List[Dict[str, Any]]:
    text = raw.decode("utf-8", "ignore")
    hits: List[Dict[str, Any]] = []
    for field in TARGET_FIELDS:
        pattern = r'\\?"' + field.replace("_", r"_") + r'\\?"\s*:\s*(\\?"[^"\\]*\\?"|[^,}\n]+)'
        for match in re.finditer(pattern, text):
            value = match.group(1).strip()
            hits.append({
                "field": field,
                "serialized_value": value,
                "byte_offset": match.start(),
            })
    return hits


def _session_records(candidate_ids: Sequence[str],
                     retained_path: Path) -> Dict[str, Any]:
    if not SESSION_SOURCE_PATH.exists():
        retained_raw = retained_path.read_bytes()
        _require(_digest(retained_raw) == RETAINED_SESSION_SEARCH_SHA256,
                 "Stage L retained original-session search bytes differ")
        result = json.loads(retained_raw)
        _require(set(result.get("exact_match_counts", {})) == set(candidate_ids)
                 and all(result["exact_match_counts"][identifier] > 0
                         for identifier in candidate_ids),
                 "Stage L retained identifier coverage differs")
        _require(result.get("matching_line_numbers") == [11533, 11534],
                 "Stage L retained matching lines differ")
        return result

    source_raw = SESSION_SOURCE_PATH.read_bytes()
    _require(_digest(source_raw) == SESSION_SOURCE_SHA256,
             "Stage L original session archive bytes differ")
    selected: Dict[int, Tuple[bytes, Dict[str, Any], set]] = {}
    exact_counts = {identifier: 0 for identifier in candidate_ids}
    with SESSION_SOURCE_PATH.open("rb") as stream:
        for line_number, line in enumerate(stream, 1):
            raw = line.rstrip(b"\n")
            identifiers = {identifier for identifier in candidate_ids
                           if identifier.encode() in raw}
            for identifier in identifiers:
                exact_counts[identifier] += raw.count(identifier.encode())
            if identifiers:
                selected[line_number] = (raw, json.loads(raw), identifiers)
    _require(set(selected) == {11533, 11534},
             "Stage L selected session lines differ")
    expected_hashes = {
        11533: SESSION_LINE_11533_SHA256,
        11534: SESSION_LINE_11534_SHA256,
    }
    records = []
    for line_number, (raw, value, identifiers) in selected.items():
        _require(_digest(raw) == expected_hashes[line_number],
                 "Stage L session line bytes differ")
        payload = value.get("payload", {})
        item = payload.get("item", {})
        matched = sorted(identifiers)
        hits = _target_hits(value)
        serialized_hits = _serialized_target_hits(raw)
        records.append({
            "line_number": line_number,
            "timestamp": value.get("timestamp"),
            "record_type": value.get("type"),
            "payload_type": payload.get("type"),
            "item_type": item.get("type"),
            "status": item.get("status"),
            "line_bytes": len(raw),
            "line_sha256": _digest(raw),
            "matched_candidate_ids": matched,
            "exact_target_field_hits": hits,
            "serialized_target_field_hits": serialized_hits,
            "raw_line_retained": False,
        })
    _require(len(records[0]["matched_candidate_ids"]) == len(candidate_ids),
             "Stage L primary session identifier coverage differs")
    _require(all(exact_counts[identifier] > 0 for identifier in candidate_ids),
             "Stage L original archive identifier coverage differs")
    operation_values = [hit["serialized_value"].strip('\\"')
                        for record in records
                        for hit in record["serialized_target_field_hits"]
                        if hit["field"] == "operation"]
    _require(operation_values == ["unknown"] * 3,
             "Stage L serialized operation boundary differs")
    return {
        "source_path": str(SESSION_SOURCE_PATH),
        "source_bytes": len(source_raw),
        "source_sha256": SESSION_SOURCE_SHA256,
        "search_method": "full-line exact-byte scan of every archive line",
        "matching_line_numbers": sorted(selected),
        "exact_match_counts": exact_counts,
        "matching_records": records,
        "tool_record_boundary": {
            "started_at_ms": 1792612839190,
            "completed_at_ms": 1792612839190 + 14916,
            "classification": "operator tool/readback boundary, not reservation timing",
        },
        "raw_private_records_retained": False,
    }


def _meter_index(root: Path) -> Dict[str, Dict[str, Any]]:
    path = root / "docs/evidence/spendability/stage-a/BASELINE.json"
    raw = path.read_bytes()
    _require(_digest(raw) == STAGE_A_BASELINE_SHA256,
             "Stage A baseline bytes differ")
    value = _decode(raw, "Stage A baseline")
    result: Dict[str, Dict[str, Any]] = {}
    for row in value.get("raw_tables", {}).get("metering", {}).get("rows", []):
        reservation = row.get("reservation", {}).get("value")
        receipt = row.get("id", {}).get("value")
        body_cell = row.get("body", {})
        body_hex = body_cell.get("blob_hex")
        _require(isinstance(reservation, str) and isinstance(receipt, str)
                 and isinstance(body_hex, str),
                 "Stage A meter row differs")
        body = bytes.fromhex(body_hex)
        _require(_digest(body) == receipt,
                 "Stage A meter receipt differs")
        result[reservation] = {
            "receipt": receipt,
            "body": body,
            "decoded": json.loads(body),
        }
    _require(set(result) == set(RESERVATION_IDS),
             "Stage A meter reservation coverage differs")
    return result


def _trusted_records(root: Path) -> Tuple[Dict[int, Dict[str, Any]], Dict[str, Dict[str, Any]], Dict[str, Dict[str, Any]]]:
    ledger_path = root / "docs/evidence/trusted-observation/v4-run-9d3df87/evaluator/ledger.sqlite"
    raw = ledger_path.read_bytes()
    _require(_digest(raw) == TRUSTED_LEDGER_SHA256,
             "trusted ledger bytes differ")
    connection = sqlite3.connect("file:" + str(ledger_path) + "?mode=ro&immutable=1",
                                 uri=True)
    try:
        rows = connection.execute(
            "SELECT seq,prior,hash,body FROM events ORDER BY seq").fetchall()
    finally:
        connection.close()
    events: Dict[int, Dict[str, Any]] = {}
    objects: Dict[str, Dict[str, Any]] = {}
    for sequence, prior, hashed, body_raw in rows:
        _require(_digest(prior.encode("ascii") + body_raw) == hashed,
                 "trusted event hash differs")
        body = _decode(body_raw, "trusted event")
        events[sequence] = {
            "seq": sequence, "prior": prior, "hash": hashed,
            "body": body, "raw": body_raw,
        }
        if body.get("kind") == "trusted-receipt":
            for object_hash in body.get("objects", []):
                object_path = (root / "docs/evidence/trusted-observation/"
                               "v4-run-9d3df87/evaluator/objects" / object_hash)
                object_raw = object_path.read_bytes()
                _require(_digest(object_raw) == object_hash,
                         "trusted object bytes differ")
                record = _decode(object_raw, "trusted object")
                reservation = record.get("reservation")
                if isinstance(reservation, str):
                    objects[reservation] = {
                        "hash": object_hash, "raw": object_raw,
                        "record": record,
                    }
    _require(set(objects) == set(RESERVATION_IDS),
             "trusted object reservation coverage differs")
    request_events: Dict[str, Dict[str, Any]] = {}
    for event in events.values():
        body = event["body"]
        if body.get("kind") == "reserved-before-dispatch":
            reservation = body.get("request", {}).get("reservation")
            _require(isinstance(reservation, str),
                     "trusted request reservation identity differs")
            request_events[reservation] = event
    _require(len(request_events) == 11,
             "trusted request event coverage differs")
    return request_events, objects, events


def _record_search(root: Path, reservation: str,
                   request_event: Mapping[str, Any],
                   observation: Mapping[str, Any],
                   meter: Mapping[str, Any]) -> Dict[str, Any]:
    sources = {
        "request_event": request_event["body"],
        "observation_object": observation["record"],
        "meter_body": meter["decoded"],
    }
    hits = {name: _target_hits(value) for name, value in sources.items()}
    _require(all(not value for value in hits.values()),
             "Stage L exact trusted target fields differ: " + reservation)
    duration = observation["record"].get("seconds")
    _require(isinstance(duration, float),
             "Stage L observation duration differs: " + reservation)
    return {
        "reservation_id": reservation,
        "run_id": request_event["body"].get("request", {}).get("run"),
        "request_key": request_event["body"].get("request", {}).get("key"),
        "request_event": {
            "sequence": request_event["seq"],
            "sha256": request_event["hash"],
            "canonical_bytes": len(request_event["raw"]),
        },
        "observation_object_sha256": observation["hash"],
        "meter_receipt_sha256": meter["receipt"],
        "duration_seconds": duration,
        "exact_target_field_hits": hits,
        "field_status": {
            "authenticated_principal": "not-present-in-retained-original-records",
            "issuer": "not-present-in-retained-original-records",
            "operation_id": "not-present-in-retained-original-records",
            "operation_boundary": "not-present-in-retained-original-records",
            "started_at": "not-present-in-retained-original-records",
            "ended_at": "not-present-in-retained-original-records",
            "clock": "not-present-in-retained-original-records",
            "window_sha256": "not-present-in-retained-original-records",
            "artifact_creation_timestamp": "not-present-in-retained-original-records",
        },
        "classification": None,
        "response_readiness": "not-ready",
    }


def build_request_search(root: Path,
                         created_at: str = STAGE_L_CREATED_AT) -> Dict[str, Any]:
    stage_k = _validate_stage_k(root)
    request_events, observations, _all_events = _trusted_records(root)
    all_request_ids = sorted(request_events,
                             key=lambda reservation: request_events[reservation]["seq"])
    all_candidate_ids = []
    for reservation in all_request_ids:
        all_candidate_ids.append(reservation)
        all_candidate_ids.append(request_events[reservation]["body"]["request"]["run"])
    retained_path = root / "docs/evidence/spendability/stage-l/RETAINED-SESSION-SEARCH.json"
    session = _session_records(all_candidate_ids, retained_path)
    meters = _meter_index(root)
    request_search_records = []
    for reservation in all_request_ids:
        event = request_events[reservation]
        request_search_records.append({
            "reservation_id": reservation,
            "run_id": event["body"].get("request", {}).get("run"),
            "event_sequence": event["seq"],
            "event_sha256": event["hash"],
            "exact_target_field_hits": _target_hits(event["body"]),
            "settled_candidate": reservation in RESERVATION_IDS,
        })
    _require(len(request_search_records) == 11, "Stage L request event inventory differs")
    _require(all(not record["exact_target_field_hits"]
                 for record in request_search_records),
             "Stage L request target fields differ")
    _require(sum(record["settled_candidate"] for record in request_search_records) == 8,
             "Stage L settled request inventory differs")
    items = []
    for reservation in RESERVATION_IDS:
        items.append(_record_search(
            root, reservation, request_events[reservation],
            observations[reservation], meters[reservation]))
    _require({item["run_id"] for item in items} == set(RUN_IDS),
             "Stage L run coverage differs")
    _require(all(item["classification"] is None for item in items),
             "Stage L classification boundary differs")
    return {
        "schema_version": 1,
        "record_type": "spendability-per-request-evidence-search-v1",
        "created_at": created_at,
        "basis": {
            "stage_k_commit": STAGE_K_COMMIT,
            "stage_k_package_sha256": STAGE_K_PACKAGE_SHA256,
            "stage_k_matrix_sha256": STAGE_K_MATRIX_SHA256,
            "stage_j_package_sha256": STAGE_J_PACKAGE_SHA256,
            "stage_a_baseline_sha256": STAGE_A_BASELINE_SHA256,
            "trusted_ledger_sha256": TRUSTED_LEDGER_SHA256,
            "original_session_archive_sha256": SESSION_SOURCE_SHA256,
        },
        "search_boundary": {
            "protected_paths_accessed": [],
            "network_searched": False,
            "full_original_session_archive_line_scan": True,
            "retained_trusted_request_event_bytes_scanned": True,
            "retained_observation_object_bytes_scanned": True,
            "retained_meter_body_bytes_scanned": True,
            "later_operator_analysis_sessions_treated_as_original_evidence": False,
            "whole_operator_archive_absence_established": False,
            "raw_private_records_retained": False,
            "candidate_ids": {
                "reservations": list(RESERVATION_IDS),
                "runs": list(RUN_IDS),
            },
            "target_fields": list(TARGET_FIELDS),
        },
        "original_session_search": session,
        "request_event_search": {
            "records": request_search_records,
            "all_events_scanned": 11,
            "settled_events_scanned": 8,
            "pending_events_scanned": 3,
            "exact_target_fields_found": 0,
        },
        "trusted_record_search": {
            "records": 8,
            "request_events_scanned": 11,
            "observation_objects_scanned": 8,
            "meter_bodies_scanned": 8,
            "exact_target_fields_found": 0,
        },
        "items": items,
        "summary": {
            "candidate_record_sets": len(items),
            "authenticated_principal_records_found": 0,
            "issuer_records_found": 0,
            "operation_id_records_found": 0,
            "operation_boundary_records_found": 0,
            "generic_operation_fields_found": 3,
            "generic_operation_values": ["unknown", "unknown", "unknown"],
            "started_at_records_found": 0,
            "ended_at_records_found": 0,
            "clock_records_found": 0,
            "window_digest_records_found": 0,
            "duration_values": len(items),
            "response_ready_record_sets": 0,
            "final_classifications_made": 0,
        },
        "outcome": {
            "search_valid_for_declared_boundary": True,
            "whole_archive_absence_established": False,
            "response_ready": False,
            "classification_complete": False,
            "spendable": None,
            "valid": False,
            "execution_authorized": False,
            "allowed_mutations": [],
        },
        "authority": {name: False for name in AUTHORITY_FIELDS},
    }


def validate_request_search(record: Mapping[str, Any],
                            root: Path) -> Dict[str, Any]:
    expected = build_request_search(root, created_at=record.get("created_at", ""))
    if record != expected:
        raise StageCError("request_search", "record differs from exact regeneration")
    return {
        "record_valid": True,
        "search_valid_for_declared_boundary": True,
        "response_ready": False,
        "classification_complete": False,
        "spendable": None,
        "allowed_mutations": [],
        "execution_authorized": False,
    }
