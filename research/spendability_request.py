"""Build the GRRR-z3w9 Stage F external spendability evidence request.

The request is derived only from the independently approved Stage E bundle.  It
asks for missing evidence and never converts an external response into spendability,
reconciliation, replay, admission, promotion, or operational authority.
"""

from hashlib import sha256
import json
from typing import Any, Dict, List, Mapping, Tuple

from spendability_stage_c import AUTHORITY_FIELDS, StageCError, digest
from spendability_bundle import validate_evidence_bundle


APPROVED_STAGE_E_BUNDLE_SHA256 = "52f08fc740feee1e48de7fb79b83ccb684324339dab386c383805ec136956467"
APPROVED_STAGE_E_PACKAGE_SHA256 = "36b9bfb4ae2f3d2245c4d60624e0c06548caf528578ab2ce888dfef4b2d0cc09"
REQUEST_FIELDS = frozenset((
    "schema_version", "request_kind", "status", "basis", "request_summary",
    "requested_evidence", "response_contract", "submission_guidance",
    "authority", "outcome",
))
BASIS_FIELDS = frozenset((
    "stage_e_bundle_sha256", "stage_e_package_sha256",
    "database_sha256", "stage_e_independent_review", "created_at",
))
REQUEST_KIND = "spendability-evidence-request-v1"
STAGE_E_REVIEW = "STAGE_E_NARROW_REWORK_REVIEW: APPROVED"


def _object_pairs(pairs: List[Tuple[str, Any]]) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise StageCError("evidence_request", "duplicate JSON key: " + key)
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise StageCError("evidence_request", "non-finite JSON constant: " + value)


def _decode(raw: bytes, label: str) -> Dict[str, Any]:
    try:
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=_object_pairs,
                            parse_constant=_reject_constant)
    except (UnicodeDecodeError, json.JSONDecodeError, TypeError) as exc:
        raise StageCError("evidence_request", label + " is not valid UTF-8 JSON") from exc
    if not isinstance(value, dict):
        raise StageCError("evidence_request", label + " must be an object")
    return value


def _raw_digest(raw: bytes) -> str:
    return sha256(raw).hexdigest()


def _authority() -> Dict[str, bool]:
    return {name: False for name in AUTHORITY_FIELDS}


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise StageCError("evidence_request", message)


def _cell(row: Mapping[str, Any], name: str) -> Any:
    value = row.get(name)
    if not isinstance(value, dict) or "kind" not in value:
        raise StageCError("evidence_request", "Stage E raw row cell differs")
    return value.get("decoded") if value.get("kind") == "blob" else value.get("value")


def _validate_package(raw: bytes, bundle_raw: bytes) -> Mapping[str, Any]:
    if _raw_digest(raw) != APPROVED_STAGE_E_PACKAGE_SHA256:
        raise StageCError("evidence_request", "Stage E package bytes differ")
    package = _decode(raw, "Stage E package")
    _require(package.get("independent_review") == STAGE_E_REVIEW,
             "Stage E independent review differs")
    artifacts = package.get("artifacts")
    bundle_entry = artifacts.get("docs/evidence/spendability/stage-e/BUNDLE.json") if isinstance(artifacts, dict) else None
    _require(isinstance(bundle_entry, dict)
             and bundle_entry.get("sha256") == APPROVED_STAGE_E_BUNDLE_SHA256
             and bundle_entry.get("bytes") == len(bundle_raw),
             "Stage E package bundle binding differs")
    return package


def _item(identifier: str, kind: str, subject: str, required: List[str],
          sources: List[str], rejection: List[str]) -> Dict[str, Any]:
    _require(identifier and subject and required and sources and rejection,
             "evidence request item is empty")
    return {
        "id": identifier,
        "kind": kind,
        "subject": subject,
        "required_evidence": required,
        "acceptable_sources": sources,
        "rejection_conditions": rejection,
    }


def _provenance_items(bundle: Mapping[str, Any]) -> List[Dict[str, Any]]:
    rows = bundle["raw_rows"]["reservations"]["rows"]
    items: List[Dict[str, Any]] = []
    common_sources = [
        "original evaluator request records",
        "authenticated scheduler or dispatcher records",
        "original issuer or service receipts",
        "read-only copies retained by the evaluator",
        "independently reviewed backup or archive",
    ]
    common_rejection = [
        "claimant-authored replacement log",
        "digest-shaped value without original bytes",
        "redaction that removes identity, boundary, or authorization",
        "duplicate candidate with conflicting semantics",
        "source cannot explain how and when it was created",
    ]
    for row in sorted(rows, key=lambda item: _cell(item, "id")):
        identifier = _cell(row, "id")
        actual = _cell(row, "actual")
        state = "settled" if actual is not None else "pending"
        required = [
            "exact original request bytes and canonical projection digest",
            "authenticated principal and issuer identity",
            "issuer code, toolchain, policy, and runtime-profile identities",
            "approved request authorization and idempotency key",
            "dispatch operation identity and request boundary",
            "UTC measurement start/end, clock, and window digest",
            "source artifact path, raw digest, and projection digest",
        ]
        if state == "settled":
            required.extend([
                "original meter-body bytes and digest",
                "receipt-to-meter and actual-usage join proof",
            ])
        else:
            required.extend([
                "definitive non-dispatch or operation-completion proof",
                "pending disposition and stale-handle evidence",
            ])
        items.append(_item(
            "PROV-" + identifier,
            "reservation-provenance",
            identifier,
            required,
            common_sources,
            common_rejection,
        ))
    return items


def _pending_items(bundle: Mapping[str, Any]) -> List[Dict[str, Any]]:
    return [
        _item(
            "PEND-" + record["reservation_id"],
            "pending-disposition",
            record["reservation_id"],
            [
                "request and idempotency identities",
                "operation ID and dispatch outcome",
                "final observation or explicit non-observation proof",
                "cessation proof if dispatch occurred",
                "evaluator stop/halt state and evidence",
                "pre/post database hashes",
                "stale-handle accounting",
            ],
            [
                "original dispatcher operation log",
                "evaluator stop or halt record",
                "original process-group cessation record",
                "reviewed durable run archive",
            ],
            [
                "elapsed time treated as disposition",
                "missing final observation treated as non-dispatch",
                "stop bit or exit code without cessation proof",
                "recreated log without original provenance",
            ],
        )
        for record in bundle["pending_dispositions"]
    ]


def _lineage_items(bundle: Mapping[str, Any]) -> List[Dict[str, Any]]:
    return [
        _item(
            "LINEAGE-" + record["artifact"],
            "historical-lineage",
            record["artifact"],
            [
                "exact artifact bytes and digest",
                "authorization and implementation-review identity",
                "pre/post database identity and hashes",
                "writer exclusion or lock record",
                "unchanged-or-authorized postcondition",
            ],
            [
                "protected ancestry artifact",
                "independently reviewed installation record",
                "reviewed recovery archive",
                "reviewed registration archive",
            ],
            [
                "root ownership treated as authentication",
                "partial artifact without transition lineage",
                "postcondition hash absent",
                "artifact replacement without recovery record",
            ],
        )
        for record in bundle["historical_completeness"]["lineage"]
    ]


def _coverage_items(bundle: Mapping[str, Any]) -> List[Dict[str, Any]]:
    return [
        _item(
            "OPERATIONS-1",
            "operation-history",
            "dispatch-cancel-failure-stop-replay-history",
            [
                "complete operation inventory and unique identifiers",
                "reservation/run/request joins",
                "start/end boundaries and overlap map",
                "outcome, cancellation, failure, stop, and replay state",
                "trusted receipts for each effect",
            ],
            [
                "original dispatcher log",
                "evaluator event ledger",
                "reviewed run archive",
                "reviewed backup inventory",
            ],
            [
                "empty list without affirmative search boundary",
                "duplicate snapshot counted as duplicate operation",
                "run ID treated as reservation ID",
                "effect inferred solely from exit code",
            ],
        ),
        _item(
            "SIDE-STORES-1",
            "side-store-history",
            "side-ledger-export-adjustment-refund-replay-inventory",
            [
                "complete side-store and export inventory",
                "manual adjustment and refund approvals",
                "replay or duplicate-effect records",
                "campaign/store lineage and joins",
                "cost or disposition receipt for each effect",
            ],
            [
                "reviewed accounting exports",
                "operator-owned archive",
                "independently retained evaluator receipts",
                "reviewed backup catalog",
            ],
            [
                "absence inferred only from current database",
                "unexplained sidecar or duplicate ledger",
                "manual adjustment without authorization",
                "out-of-band effect without receipt",
            ],
        ),
    ]


def _overhead_items(bundle: Mapping[str, Any]) -> List[Dict[str, Any]]:
    overhead = bundle["historical_completeness"]["overhead"]
    return [
        _item(
            "OVERHEAD-" + category.upper(),
            "overhead-domain",
            category,
            [
                "responsible actor or process",
                "campaign boundary and source-record inventory",
                "UTC intervals, clock, units, and overlap map",
                "measured cost or affirmative nonexistence proof",
                "tool/code identity used to inspect the domain",
            ],
            [
                "reviewed preparation or selection records",
                "reviewed execution and replay logs",
                "review-session records",
                "reviewed system telemetry",
            ],
            [
                "empty overhead table treated as zero",
                "unknown cost treated as zero upper bound",
                "overlapping intervals summed twice",
                "review cost substituted for execution cost",
            ],
        )
        for category in sorted(overhead)
    ]


def _global_history_item(bundle: Mapping[str, Any]) -> Dict[str, Any]:
    return _item(
        "GLOBAL-HISTORY-1",
        "global-historical-completeness",
        "registration-through-current-database-snapshot",
        [
            "complete campaign, store, profile, stage, and ceiling lineage",
            "historical stop cause and observation record",
            "paid-service decisions, proofs, and receipts",
            "lost, truncated, never-created, and unauthenticated record inventory",
            "complete recovery and interrupted-operation lineage",
            "explicit boundary proving absence where no record exists",
        ],
        [
            "operator-owned historical archive",
            "reviewed registration and recovery records",
            "reviewed evaluator export",
            "reviewed accounting custodian record",
        ],
        [
            "known encumbrance treated as complete history",
            "null or missing value converted to zero",
            "current schema validity treated as historical completeness",
            "review approval treated as authentication",
            "absence inferred without a search boundary",
        ],
    )


def build_evidence_request(stage_a_raw: bytes, stage_d_capture_raw: bytes,
                           stage_d_postcapture_raw: bytes, bundle_raw: bytes,
                           package_raw: bytes, *, created_at: str) -> Dict[str, Any]:
    """Build a deterministic evidence request from the approved Stage E state."""
    if _raw_digest(bundle_raw) != APPROVED_STAGE_E_BUNDLE_SHA256:
        raise StageCError("evidence_request", "Stage E bundle bytes differ")
    bundle = _decode(bundle_raw, "Stage E bundle")
    _validate_package(package_raw, bundle_raw)
    validation = validate_evidence_bundle(
        bundle, stage_a_raw, stage_d_capture_raw, stage_d_postcapture_raw)
    _require(validation["assembly_valid"] is True and validation["evidence_valid"] is False,
             "Stage E bundle validation differs")
    _require(bundle["outcome"] == {
        "valid": False, "first_failed_gate": "quiescence", "spendable": None,
        "allowed_mutations": [], "execution_authorized": False,
    }, "Stage E outcome is not fail-closed")
    _require(isinstance(created_at, str) and created_at,
             "request creation timestamp differs")
    items = (
        _provenance_items(bundle)
        + _pending_items(bundle)
        + _lineage_items(bundle)
        + _coverage_items(bundle)
        + _overhead_items(bundle)
        + [_global_history_item(bundle)]
    )
    identifiers = [item["id"] for item in items]
    _require(len(identifiers) == len(set(identifiers)), "evidence request IDs differ")
    return {
        "schema_version": 1,
        "request_kind": REQUEST_KIND,
        "status": "open",
        "basis": {
            "stage_e_bundle_sha256": APPROVED_STAGE_E_BUNDLE_SHA256,
            "stage_e_package_sha256": APPROVED_STAGE_E_PACKAGE_SHA256,
            "database_sha256": bundle["basis"]["database_sha256"],
            "stage_e_independent_review": STAGE_E_REVIEW,
            "created_at": created_at,
        },
        "request_summary": {
            "provenance_items": len(_provenance_items(bundle)),
            "pending_items": len(_pending_items(bundle)),
            "lineage_items": len(_lineage_items(bundle)),
            "coverage_items": len(_coverage_items(bundle)),
            "overhead_items": len(_overhead_items(bundle)),
            "global_history_items": 1,
            "total_items": len(items),
            "spendability_after_response": None,
        },
        "requested_evidence": items,
        "response_contract": {
            "required": [
                "one response record per request item ID",
                "classification: supplied, unavailable, lost, or never-created",
                "raw artifact bytes or durable exact copy",
                "SHA-256 and byte count for every artifact",
                "source system, custodian, created_at, retrieved_at, and method",
                "chain of custody and redaction justification",
                "explicit search boundary for every unavailable claim",
            ],
            "prohibited": [
                "credentials or API tokens",
                "unrelated private logs",
                "proprietary source not needed to prove the item",
                "raw private holdout fixtures",
                "claimant-authored replacements",
                "fabricated or inferred receipts",
                "authority language granting reconciliation or replay",
            ],
            "validation_rule": "External records are evidence only; only the trusted evaluator and separately authorized review can classify spendability.",
        },
        "submission_guidance": {
            "format": "canonical JSON index plus immutable artifact files",
            "index_fields": ["request_item_id", "classification", "artifact_sha256", "byte_count", "source", "custodian", "created_at", "retrieved_at", "method", "chain_of_custody", "redaction"],
            "partial_response_allowed": True,
            "unavailable_item_requirement": "document exact repositories, time ranges, systems, custodians, and searches checked",
            "operator_review_required": True,
        },
        "authority": _authority(),
        "outcome": {
            "valid": False,
            "spendable": None,
            "allowed_mutations": [],
            "execution_authorized": False,
        },
    }


def validate_evidence_request(request: Mapping[str, Any], stage_a_raw: bytes,
                              stage_d_capture_raw: bytes,
                              stage_d_postcapture_raw: bytes, bundle_raw: bytes,
                              package_raw: bytes) -> Dict[str, Any]:
    """Validate a request by exact regeneration from retained Stage E inputs."""
    if not isinstance(request, dict) or set(request) != set(REQUEST_FIELDS):
        raise StageCError("evidence_request", "request top-level schema differs")
    basis = request.get("basis")
    if not isinstance(basis, dict) or set(basis) != set(BASIS_FIELDS):
        raise StageCError("evidence_request", "request basis schema differs")
    expected = build_evidence_request(
        stage_a_raw, stage_d_capture_raw, stage_d_postcapture_raw,
        bundle_raw, package_raw, created_at=basis.get("created_at"))
    if digest(request) != digest(expected):
        raise StageCError("evidence_request", "request differs from exact regeneration")
    return {
        "request_valid": True,
        "evidence_valid": False,
        "spendable": None,
        "allowed_mutations": [],
        "execution_authorized": False,
    }
