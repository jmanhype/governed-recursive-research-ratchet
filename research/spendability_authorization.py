"""Validate retained Stage J spendability authorization evidence."""

from hashlib import sha256
import json
from pathlib import Path
import re
from typing import Any, Dict, List, Mapping, Sequence, Tuple

from spendability_stage_c import AUTHORITY_FIELDS, StageCError, canonical, digest

STAGE_I_COMMIT = "9b58eae0ba62d0d384a4743ea069bf3dde6c9f6d"
STAGE_I_PACKAGE_SHA256 = "6e9493300b7a338d7c19155af169b65c96b3728852aeb1e949c15d9f5fe920ac"
STAGE_I_PROVENANCE_SHA256 = "b809e83b7da101b2a0aab4143d575d1e23f7b661608608e2a978e22aecd5b279"
CAPTURE_SHA256 = "717fc91765a4fd3c544e052ba74b00a149bb4a2f6babf2093efd118ef96a27a4"
APPROVAL_SHA256 = "fdb11c2c30b2c385f132f4607ba2a198b42b9e0840e3c0bcee3035fb4191ca7b"
REVIEW_SHA256 = "ad9570ca20676363eb4b3dff23715b058322a0ecffe10e7e3b404db5863d896d"
TRUSTED_PLAN_SHA256 = "8fb63bae1fe0795bc6e1f5a903980abd717fff3064e888ee45f8cf5b1f9d9bda"
PREPARATION_RECEIPT_SHA256 = "3d280af9e69ff05300cb0058194db14995a2d4baf927ef84d24e1199c7e70fa7"
COMPILER_SHA256 = "e670dfa79b080bad7f7d6b1d7131145c8c49068096650ebf0ac6292f098db60d"
GUEST_TOOLCHAIN_SHA256 = "3f4227ce7b206a513e794f1393adb473a07b46e94d18bd15d1c684bbb7319797"
STAGE_J_CREATED_AT = "2026-10-28T12:30:00Z"

APPROVAL_KEYS = frozenset((
    "version", "decision", "operator_uid", "profile", "image", "supervisor",
    "helper", "host_code", "license_review_sha256", "authorization_reference",
    "qemu_installation", "accounting_binding", "bootstrap_sha256",
    "python_sha256", "execution_profile",
))
REVIEW_KEYS = frozenset((
    "version", "decision", "preparation_receipt", "compiler", "guest_toolchain",
    "authorization_reference",
))
CREDENTIAL_MARKERS = (
    b"password", b"token", b"api_key", b"secret", b"credential", b"bearer",
)
CONFIG_BINDING_KEYS = (
    "operator_uid", "profile", "image", "supervisor", "helper", "host_code",
    "qemu_installation", "accounting_binding", "bootstrap_sha256",
    "python_sha256", "execution_profile",
)
HASH_RE = re.compile(r"[0-9a-f]{64}\Z")


def _bytes_digest(raw: bytes) -> str:
    return sha256(raw).hexdigest()


def _require(condition: bool, detail: str) -> None:
    if not condition:
        raise StageCError("authorization_evidence", detail)


def _decode(raw: bytes, label: str) -> Dict[str, Any]:
    def pairs(values: Sequence[Tuple[str, Any]]) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        for key, value in values:
            if key in result:
                raise StageCError("authorization_evidence", label + " has duplicate key " + key)
            result[key] = value
        return result

    def reject(value: str) -> None:
        raise StageCError("authorization_evidence", label + " has non-finite constant " + value)

    try:
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=pairs,
                           parse_constant=reject)
    except (UnicodeDecodeError, json.JSONDecodeError, TypeError, ValueError) as exc:
        raise StageCError("authorization_evidence", label + " is not valid UTF-8 JSON") from exc
    _require(isinstance(value, dict), label + " must be an object")
    return value


def _artifact(path: Path, expected: str) -> Dict[str, Any]:
    raw = path.read_bytes()
    actual = _bytes_digest(raw)
    _require(actual == expected, "artifact bytes differ: " + str(path))
    try:
        portable = path.resolve().relative_to(Path(__file__).resolve().parents[1])
    except ValueError:
        portable = path.resolve()
    return {"path": str(portable), "bytes": len(raw), "sha256": actual}


def _no_credentials(raw: bytes, label: str) -> None:
    lowered = raw.lower()
    for marker in CREDENTIAL_MARKERS:
        _require(marker not in lowered, label + " contains credential material")


def _validate_stage_i(root: Path) -> None:
    package = root / "docs/evidence/spendability/stage-i/PACKAGE.json"
    provenance = root / "docs/evidence/spendability/stage-i/PROVENANCE.json"
    _require(_bytes_digest(package.read_bytes()) == STAGE_I_PACKAGE_SHA256,
             "Stage I package bytes differ")
    _require(_bytes_digest(provenance.read_bytes()) == STAGE_I_PROVENANCE_SHA256,
             "Stage I provenance bytes differ")
    value = _decode(package.read_bytes(), "Stage I package")
    _require(value.get("base_commit") == "2c8fddf2a480a5eca8ac0dd577e3e7658c3c8e0f",
             "Stage I base commit differs")
    _require(value.get("provenance_inventory", {}).get("response_ready_record_sets") == 0,
             "Stage I readiness differs")
    _require(value.get("provenance_inventory", {}).get("final_classifications_made") == 0,
             "Stage I classification count differs")


def _validate_plan_config(root: Path) -> Mapping[str, Any]:
    path = root / "docs/evidence/trusted-observation/v4-run-9d3df87/plan.json"
    raw = path.read_bytes()
    _require(_bytes_digest(raw) == TRUSTED_PLAN_SHA256, "trusted plan bytes differ")
    plan = _decode(raw, "trusted plan")
    config = plan.get("config")
    _require(isinstance(config, dict), "trusted plan config differs")
    _require(config.get("network") is False and config.get("paid_dispatch") is False,
             "trusted plan controls differ")
    return config


def _validate_capture(raw: bytes) -> Mapping[str, Any]:
    _require(_bytes_digest(raw) == CAPTURE_SHA256, "Stage J capture bytes differ")
    value = _decode(raw, "Stage J capture")
    _require(value.get("record_type") == "spendability-protected-authorization-capture-v1",
             "Stage J capture type differs")
    _require(value.get("basis", {}).get("stage_i_commit") == STAGE_I_COMMIT,
             "Stage J capture Stage I commit differs")
    _require(value.get("basis", {}).get("stage_i_package_sha256") == STAGE_I_PACKAGE_SHA256,
             "Stage J capture Stage I package differs")
    _require(value.get("validation", {}).get("pinned_source_validator") == "PASS"
             and value.get("validation", {}).get("validate_config") == "PASS"
             and value.get("validation", {}).get("validate_approval") == "PASS",
             "Stage J pinned validation differs")
    _require(value.get("scope", {}).get("protected_paths_mutated") == [],
             "Stage J protected mutation scope differs")
    _require(value.get("scope", {}).get("final_classification_made") is False,
             "Stage J classification scope differs")
    authority = value.get("authority", {})
    _require(authority.get("protected_access") is True
             and all(not authority.get(name, True) for name in AUTHORITY_FIELDS
                     if name != "protected_access"),
             "Stage J capture authority differs")
    outcome = value.get("outcome", {})
    _require(outcome.get("authorization_common_binding_valid") is True
             and outcome.get("response_ready") is False
             and outcome.get("classification_complete") is False
             and outcome.get("spendable") is None
             and outcome.get("execution_authorized") is False,
             "Stage J capture outcome differs")
    sources = value.get("protected_sources", {})
    expected_sources = {
        "execution_approval": APPROVAL_SHA256,
        "license_review": REVIEW_SHA256,
    }
    _require(set(sources) == set(expected_sources), "Stage J protected source inventory differs")
    for name, expected_hash in expected_sources.items():
        source = sources[name]
        _require(source.get("regular") is True and source.get("symlink") is False
                 and source.get("uid") == 0 and source.get("gid") == 0
                 and source.get("mode") == "0o444" and source.get("nlink") == 1,
                 "Stage J protected metadata differs: " + name)
        _require(source.get("sha256") == expected_hash,
                 "Stage J protected hash differs: " + name)
    return value


def _validate_records(root: Path,
                      config: Mapping[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
    approval_path = root / "docs/evidence/spendability/stage-j/artifacts/execution-approval-9d3df87-fix1.json"
    review_path = root / "docs/evidence/spendability/stage-j/artifacts/license-review-9d3df87-fix1.json"
    approval_raw = approval_path.read_bytes()
    review_raw = review_path.read_bytes()
    _require(_bytes_digest(approval_raw) == APPROVAL_SHA256,
             "retained execution approval bytes differ")
    _require(_bytes_digest(review_raw) == REVIEW_SHA256,
             "retained license review bytes differ")
    _no_credentials(approval_raw, "retained execution approval")
    _no_credentials(review_raw, "retained license review")
    approval = _decode(approval_raw, "retained execution approval")
    review = _decode(review_raw, "retained license review")
    _require(set(approval) == set(APPROVAL_KEYS), "execution approval fields differ")
    _require(set(review) == set(REVIEW_KEYS), "license review fields differ")
    _require(approval.get("version") == 1 and type(approval.get("version")) is int
             and approval.get("decision") == "approved-trusted-execution",
             "execution approval decision differs")
    _require(review.get("version") == 1 and type(review.get("version")) is int
             and review.get("decision") == "approved-local-use",
             "license review decision differs")
    for name in CONFIG_BINDING_KEYS:
        _require(approval.get(name) == config.get(name),
                 "approval/config binding differs: " + name)
    _require(approval.get("license_review_sha256") == digest(review),
             "approval/license canonical binding differs")
    _require(_bytes_digest(canonical(review).encode("ascii")) == REVIEW_SHA256,
             "license review canonical bytes differ")
    _require(review.get("preparation_receipt") == PREPARATION_RECEIPT_SHA256,
             "license preparation receipt differs")
    _require(review.get("compiler") == COMPILER_SHA256,
             "license compiler identity differs")
    _require(review.get("guest_toolchain") == GUEST_TOOLCHAIN_SHA256,
             "license guest toolchain differs")
    reference = approval.get("authorization_reference")
    _require(isinstance(reference, str) and HASH_RE.fullmatch(reference) is not None
             and review.get("authorization_reference") == reference,
             "authorization reference binding differs")
    artifacts = {
        "execution_approval": _artifact(approval_path, APPROVAL_SHA256),
        "license_review": _artifact(review_path, REVIEW_SHA256),
    }
    return approval, review, artifacts


def build_authorization_validation(root: Path,
                                   created_at: str = STAGE_J_CREATED_AT) -> Dict[str, Any]:
    _validate_stage_i(root)
    config = _validate_plan_config(root)
    capture_path = root / "docs/evidence/spendability/stage-j/CAPTURE.json"
    capture = _validate_capture(capture_path.read_bytes())
    approval, _review, artifacts = _validate_records(root, config)
    provenance_path = root / "docs/evidence/spendability/stage-i/PROVENANCE.json"
    provenance = _decode(provenance_path.read_bytes(), "Stage I provenance")
    candidate_ids = [item.get("request_item_id") for item in provenance.get("items", [])]
    _require(len(candidate_ids) == 8 and len(candidate_ids) == len(set(candidate_ids)),
             "Stage I candidate inventory differs")
    items = []
    for identifier in candidate_ids:
        items.append({
            "request_item_id": identifier,
            "classification": None,
            "common_authorization_binding": "validated",
            "response_readiness": "not-ready",
            "remaining_gaps": [
                "per-request authenticated principal and issuer binding",
                "numeric process UID mapping",
                "reservation-specific dispatch operation identity and boundary",
                "reservation-specific UTC measurement start/end, clock, and window digest",
                "reservation-specific custody classification",
                "independent final classifier decision",
            ],
        })
    return {
        "schema_version": 1,
        "record_type": "spendability-authorization-evidence-validation-v1",
        "created_at": created_at,
        "basis": {
            "stage_i_commit": STAGE_I_COMMIT,
            "stage_i_package_sha256": STAGE_I_PACKAGE_SHA256,
            "stage_i_provenance_sha256": STAGE_I_PROVENANCE_SHA256,
            "stage_j_capture_sha256": CAPTURE_SHA256,
            "source_commit": "9d3df8770f82a860f128a71d76528ff922911199",
            "trusted_plan_sha256": TRUSTED_PLAN_SHA256,
            "execution_approval_sha256": APPROVAL_SHA256,
            "license_review_sha256": REVIEW_SHA256,
            "authorization_reference_sha256": approval["authorization_reference"],
        },
        "artifacts": {
            "capture": {
                "path": "docs/evidence/spendability/stage-j/CAPTURE.json",
                "sha256": CAPTURE_SHA256,
            },
            **artifacts,
        },
        "capture_scope": capture.get("scope", {}),
        "items": items,
        "summary": {
            "candidate_record_sets": len(items),
            "common_authorization_binding_valid": True,
            "response_ready_record_sets": 0,
            "final_classifications_made": 0,
        },
        "outcome": {
            "authorization_common_binding_valid": True,
            "response_ready": False,
            "classification_complete": False,
            "spendable": None,
            "valid": False,
            "execution_authorized": False,
            "allowed_mutations": [],
        },
        "authority": {name: False for name in AUTHORITY_FIELDS},
    }


def validate_authorization_record(record: Mapping[str, Any],
                                  root: Path) -> Dict[str, Any]:
    expected = build_authorization_validation(root, created_at=record.get("created_at", ""))
    if record != expected:
        raise StageCError("authorization_evidence", "record differs from exact regeneration")
    return {
        "record_valid": True,
        "authorization_common_binding_valid": True,
        "response_ready": False,
        "classification_complete": False,
        "spendable": None,
        "allowed_mutations": [],
        "execution_authorized": False,
    }

