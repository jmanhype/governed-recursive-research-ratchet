"""Build the fail-closed Stage K per-record evidence matrix."""

from hashlib import sha256
import json
from pathlib import Path
import subprocess
from typing import Any, Dict, List, Mapping, Sequence, Tuple

from spendability_stage_c import AUTHORITY_FIELDS, StageCError
from spendability_authorization import (
    APPROVAL_SHA256,
    REVIEW_SHA256,
    STAGE_I_COMMIT,
    STAGE_I_PACKAGE_SHA256,
    build_authorization_validation,
)


STAGE_J_PACKAGE_SHA256 = "7a2251decd3073aaa268e2dabdeb16f4d9d8f9283536760c38ad4d6b5ab1c53e"
STAGE_J_VALIDATION_SHA256 = "5f14d7647148f305125391104e092fdbc4e789bdd2ed9d6dff0ae26beed89b96"
SESSION_SEARCH_SHA256 = "84b6f0ebfb76d2adcd359274a167d2b77becd76cda6b3f265ce1845197c182cc"
SESSION_SOURCE_SHA256 = "a595ff5c996d5d673e005a3d55e0b82a3a8187ed5693b2c232a0f16e771fa80e"
SESSION_SOURCE_PATH = Path(
    "/Users/speed/.codex/sessions/2026/10/20/"
    "rollout-2026-10-20T06-57-58-01a156c2-7319-7bc3-a65c-b516699997ee_"
    "01a1592c-ec38-7e22-af4c-1b1997276e76.jsonl"
)
SESSION_READBACK_LINE = 11533
SESSION_READBACK_LINE_SHA256 = "9ab13249897f4508a2410ba4eabbf29becaab434e7fba8cc3ab551f25650ae60"
ACCOUNT_LOG_SHA256 = "eca7677d9ce4ad2a8fb27b26a8278784b5c01d3bcd4fe23fe53165ade2b894dc"
ACCOUNT_LOG_COMMIT = "e0dfaf33d3b2725a2fad63401d2b717a8365e0a6"
SOURCE_COMMIT = "9d3df8770f82a860f128a71d76528ff922911199"
SOURCE_COMMON_SHA256 = "33edaf942a89f5eb0b1481e3ca5f430d7229e2b87758894cf29f95217e479a21"
SOURCE_LEDGER_SHA256 = "380a73950fe488cbe8f95da77add2ee0cc678c95b337db7ffd578dec0ba1efc9"
STAGE_A_BASELINE_SHA256 = "7608cbe6fc5f671b88573eca8b642ebfbc172f0cb920f75d60ca34cfa60c730a"
STAGE_K_CREATED_AT = "2026-10-28T13:20:00Z"

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


def _digest(raw: bytes) -> str:
    return sha256(raw).hexdigest()


def _decode(raw: bytes, label: str) -> Dict[str, Any]:
    def pairs(values: Sequence[Tuple[str, Any]]) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        for key, value in values:
            if key in result:
                raise StageCError("per_record", label + " has duplicate key " + key)
            result[key] = value
        return result

    def reject(value: str) -> None:
        raise StageCError("per_record", label + " has non-finite constant " + value)

    try:
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=pairs,
                           parse_constant=reject)
    except (UnicodeDecodeError, json.JSONDecodeError, TypeError, ValueError) as exc:
        raise StageCError("per_record", label + " is not valid UTF-8 JSON") from exc
    if not isinstance(value, dict):
        raise StageCError("per_record", label + " must be an object")
    return value


def _require(condition: bool, detail: str) -> None:
    if not condition:
        raise StageCError("per_record", detail)


def _artifact(path: Path, expected: str) -> Dict[str, Any]:
    raw = path.read_bytes()
    actual = _digest(raw)
    _require(actual == expected, "artifact bytes differ: " + str(path))
    try:
        portable = path.resolve().relative_to(Path(__file__).resolve().parents[1])
    except ValueError:
        portable = path.resolve()
    return {"path": str(portable), "bytes": len(raw), "sha256": actual}


def _git(root: Path, *arguments: str) -> bytes:
    return subprocess.check_output(["git", "-C", str(root), *arguments])


def _validate_stage_j(root: Path) -> None:
    package = root / "docs/evidence/spendability/stage-j/PACKAGE.json"
    validation = root / "docs/evidence/spendability/stage-j/VALIDATION.json"
    _require(_digest(package.read_bytes()) == STAGE_J_PACKAGE_SHA256,
             "Stage J package bytes differ")
    _require(_digest(validation.read_bytes()) == STAGE_J_VALIDATION_SHA256,
             "Stage J validation bytes differ")
    package_value = _decode(package.read_bytes(), "Stage J package")
    _require(package_value.get("base_commit") == STAGE_I_COMMIT,
             "Stage J base commit differs")
    _require(package_value.get("independent_review")
             == "STAGE_J_AUTHORIZATION_REVIEW: APPROVED",
             "Stage J review differs")
    _require(package_value.get("evidence_scope", {}).get("protected_paths_mutated") == [],
             "Stage J protected mutation scope differs")
    build_authorization_validation(root)


def _validate_session_search(root: Path) -> Mapping[str, Any]:
    path = root / "docs/evidence/spendability/stage-k/SESSION-SEARCH.json"
    raw = path.read_bytes()
    _require(_digest(raw) == SESSION_SEARCH_SHA256, "Stage K session search bytes differ")
    value = _decode(raw, "Stage K session search")
    _require(value.get("basis", {}).get("stage_j_package_sha256")
             == STAGE_J_PACKAGE_SHA256,
             "Stage K Stage J binding differs")
    _require(value.get("source", {}).get("sha256") == SESSION_SOURCE_SHA256,
             "Stage K source archive binding differs")
    if SESSION_SOURCE_PATH.exists():
        source_raw = SESSION_SOURCE_PATH.read_bytes()
        _require(_digest(source_raw) == SESSION_SOURCE_SHA256,
                 "Stage K live source archive bytes differ")
        counts = {needle: source_raw.count(needle.encode())
                  for needle in RESERVATION_IDS + RUN_IDS}
    else:
        # The pinned Stage K publication is the retained search boundary after
        # mutable host-session retention; absent source bytes are not zero.
        counts = dict(value.get("exact_match_counts", {}))
    _require(set(counts) == set(RESERVATION_IDS + RUN_IDS),
             "Stage K identifier inventory differs")
    _require(value.get("exact_match_counts") == counts,
             "Stage K exact match counts differ")
    _require(all(counts[needle] > 0 for needle in RESERVATION_IDS + RUN_IDS),
             "Stage K candidate identifier coverage differs")
    records = {record.get("line_number"): record
               for record in value.get("matching_records", [])}
    _require(set(records) == {11533, 11534},
             "Stage K matching session records differ")
    line_raw = None
    if SESSION_SOURCE_PATH.exists():
        selected: Dict[int, Dict[str, Any]] = {}
        with SESSION_SOURCE_PATH.open("rb") as stream:
            for line_number, line in enumerate(stream, 1):
                if line_number in records:
                    selected[line_number] = json.loads(line)
                if line_number >= 11534:
                    break
        _require(set(selected) == {11533, 11534},
                 "Stage K selected source lines differ")
        with SESSION_SOURCE_PATH.open("rb") as stream:
            for line_number, line in enumerate(stream, 1):
                if line_number == SESSION_READBACK_LINE:
                    line_raw = line.rstrip(b"\n")
                    break
        _require(line_raw is not None
                 and _digest(line_raw) == SESSION_READBACK_LINE_SHA256,
                 "Stage K readback line bytes differ")
        for needle in RESERVATION_IDS + RUN_IDS:
            _require(needle.encode() in line_raw,
                     "Stage K readback line identifier differs: " + needle)
    readback = records[11533]
    _require(readback.get("line_sha256") == SESSION_READBACK_LINE_SHA256
             and len(readback.get("matched_needles", [])) == 16
             and readback.get("raw_line_retained") is False,
             "Stage K readback receipt differs")
    _require(readback.get("started_at") == "2026-10-21T20:00:39.190Z"
             and readback.get("completed_at") == "2026-10-21T20:00:54.106Z",
             "Stage K readback boundary differs")
    _require(value.get("interpretation", {}).get(
                 "line_11533_does_not_provide_per_reservation_creation_timestamps")
             is True,
             "Stage K timestamp limitation differs")
    _require(value.get("interpretation", {}).get(
                 "line_11533_does_not_provide_per_reservation_dispatch_operation_ids")
             is True,
             "Stage K operation limitation differs")
    return value


def _validate_identity_evidence(root: Path) -> Dict[str, Any]:
    account_path = root / "docs/evidence/replay-prerequisites/runtime-smoke-r3/account-groups.log"
    account_repo_path = "docs/evidence/replay-prerequisites/runtime-smoke-r3/account-groups.log"
    account_raw = account_path.read_bytes()
    _require(_digest(account_raw) == ACCOUNT_LOG_SHA256,
             "Stage K account mapping bytes differ")
    expected_lines = {
        "uid=320(_grrr_evaluator) gid=320(_grrr_evaluator) groups=320(_grrr_evaluator),12(everyone),61(localaccounts),701(com.apple.sharepoint.group.1),100(_lpoperator)",
        "uid=321(_grrr_runner) gid=321(_grrr_runner) groups=321(_grrr_runner),12(everyone),61(localaccounts),701(com.apple.sharepoint.group.1),100(_lpoperator)",
    }
    _require({line for line in account_raw.decode("ascii").splitlines() if line}
             == expected_lines,
             "Stage K account mapping content differs")
    committed_account = _git(root, "show", ACCOUNT_LOG_COMMIT + ":" + account_repo_path)
    _require(committed_account == account_raw,
             "Stage K account mapping commit bytes differ")

    common = _git(root, "show", SOURCE_COMMIT + ":research/common.py")
    ledger = _git(root, "show", SOURCE_COMMIT + ":research/ledger.py")
    _require(_digest(common) == SOURCE_COMMON_SHA256,
             "Stage K source common bytes differ")
    _require(_digest(ledger) == SOURCE_LEDGER_SHA256,
             "Stage K source ledger bytes differ")
    _require(b"EVALUATOR = 320" in common and b"RUNNER = 321" in common,
             "Stage K source identity constants differ")
    _require(b"require(principal == EVALUATOR" in ledger
             and b"Evaluator-owned ledger only" in ledger,
             "Stage K ledger principal enforcement differs")

    baseline_path = root / "docs/evidence/spendability/stage-a/BASELINE.json"
    baseline_raw = baseline_path.read_bytes()
    _require(_digest(baseline_raw) == STAGE_A_BASELINE_SHA256,
             "Stage A baseline bytes differ")
    baseline = _decode(baseline_raw, "Stage A baseline")
    database = baseline.get("database", {}).get("after", {})
    _require(database.get("uid") == 320 and database.get("gid") == 320,
             "Stage K evaluator database ownership differs")
    return {
        "account_mapping": {
            "status": "validated-common",
            "evaluator": {"name": "_grrr_evaluator", "uid": 320, "gid": 320},
            "runner": {"name": "_grrr_runner", "uid": 321, "gid": 321},
            "artifact": _artifact(account_path, ACCOUNT_LOG_SHA256),
            "commit": ACCOUNT_LOG_COMMIT,
        },
        "issuer_ledger_identity": {
            "status": "validated-common",
            "principal_uid": 320,
            "database_owner_uid": 320,
            "database_owner_gid": 320,
            "source_commit": SOURCE_COMMIT,
            "source_common_sha256": SOURCE_COMMON_SHA256,
            "source_ledger_sha256": SOURCE_LEDGER_SHA256,
            "per_request_authenticated_principal": "missing",
        },
    }


def _candidate_records(root: Path) -> List[Dict[str, Any]]:
    path = root / "docs/evidence/spendability/stage-h/RESPONSE-READINESS.json"
    value = _decode(path.read_bytes(), "Stage H readiness")
    items = [item for item in value.get("items", [])
             if item.get("response_readiness")
             == "candidate-record-set-not-response-ready"]
    _require(len(items) == 8, "Stage K candidate inventory differs")
    _require({item.get("subject") for item in items} == set(RESERVATION_IDS),
             "Stage K reservation coverage differs")
    return items


def _observation(root: Path, candidate: Mapping[str, Any]) -> Dict[str, Any]:
    artifacts = candidate.get("artifacts", [])
    observation = next((item for item in artifacts
                        if item.get("role") == "trusted-observation-object"), None)
    request = next((item for item in artifacts
                    if item.get("role") == "reservation-request-event"), None)
    meter = next((item for item in artifacts
                  if item.get("role") == "meter-body-exact-copy"), None)
    _require(observation is not None and request is not None and meter is not None,
             "Stage K candidate artifact roles differ")
    object_path = root / observation["path"]
    object_raw = object_path.read_bytes()
    _require(_digest(object_raw) == observation["sha256"],
             "Stage K observation bytes differ")
    record = _decode(object_raw, "Stage K observation")
    _require(record.get("reservation") == candidate.get("subject"),
             "Stage K observation reservation differs")
    _request_event = record
    del _request_event
    return {
        "record": record,
        "request_event": request,
        "meter": meter,
        "artifact": _artifact(object_path, observation["sha256"]),
    }


def _item(root: Path, candidate: Mapping[str, Any],
          identity: Mapping[str, Any]) -> Dict[str, Any]:
    observation = _observation(root, candidate)
    record = observation["record"]
    return {
        "request_item_id": candidate.get("request_item_id"),
        "reservation_id": candidate.get("subject"),
        "run_id": record.get("run"),
        "request_key": record.get("key"),
        "classification": None,
        "numeric_process_uid_mapping": {
            "status": "validated-common",
            "value": identity["account_mapping"],
        },
        "issuer_ledger_identity": {
            "status": "validated-common",
            "value": identity["issuer_ledger_identity"],
        },
        "per_request_authenticated_principal": {
            "status": "missing",
            "reason": "ledger event body has no authenticated principal receipt",
        },
        "operation_boundary": {
            "status": "partial",
            "request_event": observation["request_event"],
            "run_id": record.get("run"),
            "request_key": record.get("key"),
            "missing": [
                "explicit dispatch operation ID",
                "reservation-specific request start/end boundary",
            ],
        },
        "timing": {
            "status": "partial",
            "duration_seconds": record.get("seconds"),
            "common_readback_started_at": "2026-10-21T20:00:39.190Z",
            "common_readback_completed_at": "2026-10-21T20:00:54.106Z",
            "missing": [
                "reservation-specific UTC start",
                "reservation-specific UTC end",
                "measurement clock identity",
                "measurement window digest",
            ],
        },
        "custody_chain": {
            "status": "partial-validated-chain",
            "request_event": observation["request_event"],
            "observation": observation["artifact"],
            "meter_receipt_sha256": observation["meter"].get("meter_receipt_sha256"),
            "source_commit": SOURCE_COMMIT,
            "stage_i_commit": STAGE_I_COMMIT,
            "stage_j_package_sha256": STAGE_J_PACKAGE_SHA256,
            "missing": [
                "artifact creation timestamp",
                "independent reservation-specific custody classification",
            ],
        },
        "response_readiness": "not-ready",
    }


def build_per_record_matrix(root: Path,
                            created_at: str = STAGE_K_CREATED_AT) -> Dict[str, Any]:
    _validate_stage_j(root)
    session = _validate_session_search(root)
    identity = _validate_identity_evidence(root)
    candidates = _candidate_records(root)
    items = [_item(root, candidate, identity) for candidate in candidates]
    _require({item["reservation_id"] for item in items} == set(RESERVATION_IDS),
             "Stage K item reservation coverage differs")
    _require({item["run_id"] for item in items} == set(RUN_IDS),
             "Stage K item run coverage differs")
    return {
        "schema_version": 1,
        "record_type": "spendability-per-record-evidence-matrix-v1",
        "created_at": created_at,
        "basis": {
            "stage_i_commit": STAGE_I_COMMIT,
            "stage_i_package_sha256": STAGE_I_PACKAGE_SHA256,
            "stage_j_package_sha256": STAGE_J_PACKAGE_SHA256,
            "stage_j_validation_sha256": STAGE_J_VALIDATION_SHA256,
            "session_search_sha256": SESSION_SEARCH_SHA256,
            "session_source_sha256": SESSION_SOURCE_SHA256,
            "execution_approval_sha256": APPROVAL_SHA256,
            "license_review_sha256": REVIEW_SHA256,
        },
        "artifacts": {
            "session_search": _artifact(
                root / "docs/evidence/spendability/stage-k/SESSION-SEARCH.json",
                SESSION_SEARCH_SHA256),
            "account_mapping": identity["account_mapping"]["artifact"],
        },
        "common_evidence": identity,
        "session_readback": {
            "source_line": SESSION_READBACK_LINE,
            "line_sha256": SESSION_READBACK_LINE_SHA256,
            "started_at": "2026-10-21T20:00:39.190Z",
            "completed_at": "2026-10-21T20:00:54.106Z",
            "all_sixteen_candidate_ids_present": True,
        },
        "items": items,
        "summary": {
            "candidate_record_sets": len(items),
            "numeric_process_uid_mapping_validated": True,
            "issuer_ledger_identity_validated": True,
            "per_request_authenticated_principal_records": 0,
            "explicit_dispatch_operation_ids": 0,
            "reservation_specific_utc_intervals": 0,
            "duration_values": len(items),
            "common_readback_boundaries": 1,
            "custody_chains": len(items),
            "response_ready_record_sets": 0,
            "final_classifications_made": 0,
        },
        "outcome": {
            "response_ready": False,
            "classification_complete": False,
            "spendable": None,
            "valid": False,
            "execution_authorized": False,
            "allowed_mutations": [],
        },
        "authority": {name: False for name in AUTHORITY_FIELDS},
    }


def validate_per_record_matrix(record: Mapping[str, Any],
                               root: Path) -> Dict[str, Any]:
    expected = build_per_record_matrix(root, created_at=record.get("created_at", ""))
    if record != expected:
        raise StageCError("per_record", "record differs from exact regeneration")
    return {
        "record_valid": True,
        "response_ready": False,
        "classification_complete": False,
        "spendable": None,
        "allowed_mutations": [],
        "execution_authorized": False,
    }
