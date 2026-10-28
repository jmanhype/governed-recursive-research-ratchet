"""Build a fail-closed Stage H spendability response-readiness matrix."""

from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Dict, List, Mapping, Sequence, Tuple

from spendability_stage_c import AUTHORITY_FIELDS, StageCError
from spendability_search import (
    STAGE_A_BASELINE_SHA256,
    STAGE_F_PACKAGE_SHA256,
    STAGE_F_REQUEST_SHA256,
    STAGE_G_CREATED_AT,
    TRUSTED_EXPORT_READBACK_SHA256,
    TRUSTED_EXPORT_LEDGER_SHA256,
    TRUSTED_EXPORT_SNAPSHOT_SHA256,
    validate_external_evidence_search,
)


STAGE_G_PACKAGE_SHA256 = "d00b35c07f2b482f3441a767d179c5e163a27f0f2db4ff8544c727a7da44f4ca"
STAGE_G_CANDIDATE_INDEX_SHA256 = "31466b133af19110cd80323ff4499642307bd2c74bff055079ec13738203c7bc"
STAGE_H_CREATED_AT = "2026-10-28T01:15:00Z"
PROJECT_ROOT = Path(__file__).resolve().parents[1]

GLOBAL_RESPONSE_GAPS = (
    "artifact creation and retrieval timestamps",
    "source-system custodian and chain of custody",
    "retrieval method and independent custody review",
    "final response classification by an independent reviewer",
)

SETTLED_PRESENT_PATTERNS = (
    "exact original request bytes and canonical projection digest",
    "source artifact path, raw digest, and projection digest",
    "original meter-body bytes and digest",
    "receipt-to-meter and actual-usage join proof",
)
SETTLED_PARTIAL_PATTERNS = (
    "issuer code, toolchain, policy, and runtime-profile identities",
    "approved request authorization and idempotency key",
    "dispatch operation identity and request boundary",
)
SETTLED_MISSING_PATTERNS = (
    "authenticated principal and issuer identity",
    "UTC measurement start/end, clock, and window digest",
)


def _digest(raw: bytes) -> str:
    return sha256(raw).hexdigest()


def _decode(raw: bytes, label: str) -> Dict[str, Any]:
    def pairs(values: Sequence[Tuple[str, Any]]) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        for key, value in values:
            if key in result:
                raise StageCError("response_readiness", label + " has duplicate key " + key)
            result[key] = value
        return result

    try:
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=pairs,
                           parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)))
    except (UnicodeDecodeError, json.JSONDecodeError, TypeError, ValueError) as exc:
        raise StageCError("response_readiness", label + " is not valid UTF-8 JSON") from exc
    if not isinstance(value, dict):
        raise StageCError("response_readiness", label + " must be an object")
    return value


def _require(condition: bool, detail: str) -> None:
    if not condition:
        raise StageCError("response_readiness", detail)


def _artifact(path: Path, expected: str) -> Dict[str, Any]:
    raw = path.read_bytes()
    actual = _digest(raw)
    _require(actual == expected, "artifact bytes differ: " + str(path))
    try:
        portable = path.resolve().relative_to(PROJECT_ROOT)
    except ValueError:
        portable = path.resolve()
    return {"path": str(portable), "bytes": len(raw), "sha256": actual}


def _authority() -> Dict[str, bool]:
    return {name: False for name in AUTHORITY_FIELDS}


def _validate_stage_g_package(raw: bytes, root: Path) -> Mapping[str, Any]:
    _require(_digest(raw) == STAGE_G_PACKAGE_SHA256, "Stage G package bytes differ")
    package = _decode(raw, "Stage G package")
    _require(package.get("independent_review")
             == "STAGE_G_SEARCH_NARROW_REWORK_REVIEW: APPROVED",
             "Stage G independent review differs")
    _require(package.get("search_evidence_boundary", {}).get(
                 "generator_consumes_search_receipts") is False,
             "Stage G search-proof boundary differs")
    _require(package.get("outcome", {}).get("spendable") is None
             and package.get("outcome", {}).get("classification_complete") is False,
             "Stage G outcome differs")
    _require(not any(package.get("authority", {}).values()),
             "Stage G package authority differs")
    artifacts = package.get("artifacts")
    _require(isinstance(artifacts, dict) and len(artifacts) == 14,
             "Stage G package inventory differs")
    for name, expected in artifacts.items():
        path = root / name
        current = path.read_bytes()
        _require(len(current) == expected.get("bytes")
                 and _digest(current) == expected.get("sha256"),
                 "Stage G package member differs: " + name)
    return package


def _validate_candidate_index(raw: bytes, root: Path) -> Mapping[str, Any]:
    _require(_digest(raw) == STAGE_G_CANDIDATE_INDEX_SHA256,
             "Stage G candidate index bytes differ")
    value = _decode(raw, "Stage G candidate index")
    validate_external_evidence_search(
        value,
        (root / "docs/evidence/spendability/stage-f/REQUEST.json").read_bytes(),
        (root / "docs/evidence/spendability/stage-f/PACKAGE.json").read_bytes(),
        (root / "docs/evidence/spendability/stage-a/BASELINE.json").read_bytes(),
        root / "docs/evidence/trusted-observation/v4-run-9d3df87",
    )
    _require(value.get("record_type") == "spendability-external-evidence-search-v1",
             "Stage G record type differs")
    _require(value.get("created_at") == STAGE_G_CREATED_AT,
             "Stage G creation identity differs")
    _require(len(value.get("items", [])) == 30,
             "Stage G item inventory differs")
    return value


def _coverage(required: str, candidate: Mapping[str, Any]) -> Dict[str, str]:
    completeness = candidate.get("candidate_completeness")
    if completeness == "request-observation-and-meter-join":
        if any(pattern in required for pattern in SETTLED_PRESENT_PATTERNS):
            return "present"
        if any(pattern in required for pattern in SETTLED_PARTIAL_PATTERNS):
            return "partial"
        if any(pattern in required for pattern in SETTLED_MISSING_PATTERNS):
            return "missing"
        return "missing"
    if completeness in ("request-only", "request-and-gate-only"):
        if "request" in required and "identit" in required:
            return "partial"
        if "idempotency" in required:
            return "partial"
        return "missing"
    if candidate.get("search_status") == "partial-evaluator-export-only":
        if "inventory" in required or "joins" in required or "state" in required:
            return "partial"
        if "boundary" in required or "overlap" in required:
            return "missing"
        return "partial"
    return "missing"


def _item(request_item: Mapping[str, Any], candidate: Mapping[str, Any]) -> Dict[str, Any]:
    required_fields = request_item.get("required_evidence", [])
    coverage = [
        {"required_evidence": required, "status": _coverage(required, candidate)}
        for required in required_fields
    ]
    blocking = [
        row["required_evidence"] for row in coverage
        if row["status"] in ("partial", "missing")
    ]
    blocking.extend(GLOBAL_RESPONSE_GAPS)
    complete_candidate = (
        candidate.get("candidate_completeness")
        == "request-observation-and-meter-join"
    )
    readiness = (
        "candidate-record-set-not-response-ready"
        if complete_candidate else
        "not-ready"
    )
    return {
        "request_item_id": request_item.get("id"),
        "kind": request_item.get("kind"),
        "subject": request_item.get("subject"),
        "stage_g_search_status": candidate.get("search_status"),
        "stage_g_candidate_completeness": candidate.get("candidate_completeness"),
        "classification": None,
        "response_readiness": readiness,
        "coverage": coverage,
        "blocking_gaps": blocking,
        "independent_review_required": True,
        "artifacts": candidate.get("artifacts", []),
    }


def _request_items(raw: bytes) -> List[Dict[str, Any]]:
    _require(_digest(raw) == STAGE_F_REQUEST_SHA256, "Stage F request bytes differ")
    request = _decode(raw, "Stage F request")
    items = request.get("requested_evidence")
    _require(isinstance(items, list) and len(items) == 30,
             "Stage F request inventory differs")
    identifiers = [item.get("id") for item in items]
    _require(len(identifiers) == len(set(identifiers)) == 30,
             "Stage F request identifiers differ")
    return items


def build_response_readiness(root: Path,
                             created_at: str = STAGE_H_CREATED_AT) -> Dict[str, Any]:
    request_path = root / "docs/evidence/spendability/stage-f/REQUEST.json"
    stage_g_package_path = root / "docs/evidence/spendability/stage-g/PACKAGE.json"
    stage_g_index_path = root / "docs/evidence/spendability/stage-g/CANDIDATE-INDEX.json"
    request_raw = request_path.read_bytes()
    stage_g_package_raw = stage_g_package_path.read_bytes()
    stage_g_index_raw = stage_g_index_path.read_bytes()
    _require(_digest(request_raw) == STAGE_F_REQUEST_SHA256,
             "Stage F request bytes differ")
    _require(_digest((root / "docs/evidence/spendability/stage-f/PACKAGE.json").read_bytes())
             == STAGE_F_PACKAGE_SHA256, "Stage F package bytes differ")
    _require(_digest((root / "docs/evidence/spendability/stage-a/BASELINE.json").read_bytes())
             == STAGE_A_BASELINE_SHA256, "Stage A baseline bytes differ")
    stage_g_package = _validate_stage_g_package(stage_g_package_raw, root)
    candidate_index = _validate_candidate_index(stage_g_index_raw, root)

    candidates = {
        item.get("request_item_id"): item
        for item in candidate_index.get("items", [])
    }
    _require(len(candidates) == 30, "Stage G candidate mapping differs")
    request_items = _request_items(request_raw)
    items = []
    for request_item in request_items:
        identifier = request_item.get("id")
        _require(identifier in candidates, "Stage G request item is absent: " + str(identifier))
        items.append(_item(request_item, candidates[identifier]))

    candidate_sets = sum(
        item["response_readiness"] == "candidate-record-set-not-response-ready"
        for item in items
    )
    not_ready = sum(item["response_readiness"] == "not-ready" for item in items)
    ready = sum(not item["blocking_gaps"] for item in items)
    return {
        "schema_version": 1,
        "record_type": "spendability-candidate-response-readiness-v1",
        "created_at": created_at,
        "basis": {
            "stage_f_request_sha256": STAGE_F_REQUEST_SHA256,
            "stage_f_package_sha256": STAGE_F_PACKAGE_SHA256,
            "stage_a_baseline_sha256": STAGE_A_BASELINE_SHA256,
            "stage_g_package_sha256": STAGE_G_PACKAGE_SHA256,
            "stage_g_candidate_index_sha256": STAGE_G_CANDIDATE_INDEX_SHA256,
            "stage_g_independent_review": stage_g_package.get("independent_review"),
            "trusted_export_readback_sha256": TRUSTED_EXPORT_READBACK_SHA256,
            "trusted_export_ledger_sha256": TRUSTED_EXPORT_LEDGER_SHA256,
            "trusted_export_snapshot_sha256": TRUSTED_EXPORT_SNAPSHOT_SHA256,
        },
        "artifacts": {
            "stage_f_request": _artifact(request_path, STAGE_F_REQUEST_SHA256),
            "stage_g_package": _artifact(stage_g_package_path, STAGE_G_PACKAGE_SHA256),
            "stage_g_candidate_index": _artifact(stage_g_index_path, STAGE_G_CANDIDATE_INDEX_SHA256),
        },
        "items": items,
        "summary": {
            "total_items": len(items),
            "candidate_record_sets": candidate_sets,
            "candidate_record_sets_response_ready": ready,
            "not_ready_items": not_ready,
            "final_classifications_made": 0,
        },
        "global_blocking_gaps": list(GLOBAL_RESPONSE_GAPS),
        "outcome": {
            "response_ready": False,
            "classification_complete": False,
            "spendable": None,
            "valid": False,
            "execution_authorized": False,
            "allowed_mutations": [],
        },
        "authority": _authority(),
    }


def validate_response_readiness(record: Mapping[str, Any], root: Path) -> Dict[str, Any]:
    expected = build_response_readiness(root, created_at=record.get("created_at", ""))
    if record != expected:
        raise StageCError("response_readiness", "record differs from exact regeneration")
    return {
        "record_valid": True,
        "response_ready": False,
        "classification_complete": False,
        "spendable": None,
        "allowed_mutations": [],
        "execution_authorized": False,
    }
