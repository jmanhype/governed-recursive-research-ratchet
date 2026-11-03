"""Validate Stage I issuer, authorization, boundary, and custody candidates."""

from hashlib import sha256
import json
from pathlib import Path
import subprocess
from typing import Any, Dict, List, Mapping, Sequence, Tuple

from spendability_stage_c import AUTHORITY_FIELDS, StageCError


STAGE_H_PACKAGE_SHA256 = "12c4d2ff2a042588af5b9570d1eff68dd84475a87131bef83841cdca0a37d478"
STAGE_H_READINESS_SHA256 = "d4aefba5c2f391f130b0319be3723b368cdbe4d21b13650a2d2acfbdb23341cf"
SESSION_SOURCE_SHA256 = "a595ff5c996d5d673e005a3d55e0b82a3a8187ed5693b2c232a0f16e771fa80e"
SESSION_EXTRACT_SHA256 = "b7166485d0b92636dec39dc399d6e39b1fa0fd486962051ccb88a9b7570c480b"
SESSION_SOURCE_PATH = Path(
    "/Users/speed/.codex/sessions/2026/10/20/"
    "rollout-2026-10-20T06-57-58-01a156c2-7319-7bc3-a65c-b516699997ee_"
    "01a1592c-ec38-7e22-af4c-1b1997276e76.jsonl"
)
TRUSTED_PLAN_SHA256 = "8fb63bae1fe0795bc6e1f5a903980abd717fff3064e888ee45f8cf5b1f9d9bda"
TRUSTED_READBACK_SHA256 = "2bbdb46aced148263505a775cee3e5033c20c337d1da6a73e875c87f62a821a8"
TRUSTED_LEDGER_SHA256 = "11e3fba4f8ff3f1b27d65c359e76c1c99465164970e7d4f050c072cbf49feb09"
TRUSTED_SNAPSHOT_SHA256 = "745f5d2c9086550c184cccd484023d5e490f0c082550eb55524adf25948ac513"
SOURCE_COMMIT = "9d3df8770f82a860f128a71d76528ff922911199"
EXPORT_COMMIT = "141823fe7e19e43fd3d2bfcc0fe4be8303e42642"
STAGE_I_CREATED_AT = "2026-10-28T06:00:00Z"
APPROVAL_SHA256 = "fdb11c2c30b2c385f132f4607ba2a198b42b9e0840e3c0bcee3035fb4191ca7b"
LICENSE_REVIEW_SHA256 = "ad9570ca20676363eb4b3dff23715b058322a0ecffe10e7e3b404db5863d896d"
EXECUTION_PROFILE_SHA256 = "b5400cdf040725cbe3b661d1d69f26a276123775bb63074b49fd7420befe61a7"
EXECUTION_STARTED_AT = "2026-10-21T19:55:53.853Z"
EXECUTION_COMPLETED_AT = "2026-10-21T19:59:54.106Z"
EXECUTION_DURATION_MS = 240253
PRIVATE_RUNTIME = "/private/tmp/grrr-trusted-rk5jwjmv"


def _digest(raw: bytes) -> str:
    return sha256(raw).hexdigest()


def _decode(raw: bytes, label: str) -> Dict[str, Any]:
    def pairs(values: Sequence[Tuple[str, Any]]) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        for key, value in values:
            if key in result:
                raise StageCError("provenance", label + " has duplicate key " + key)
            result[key] = value
        return result

    def reject(value: str) -> None:
        raise StageCError("provenance", label + " has non-finite constant " + value)

    try:
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=pairs,
                           parse_constant=reject)
    except (UnicodeDecodeError, json.JSONDecodeError, TypeError, ValueError) as exc:
        raise StageCError("provenance", label + " is not valid UTF-8 JSON") from exc
    if not isinstance(value, dict):
        raise StageCError("provenance", label + " must be an object")
    return value


def _require(condition: bool, detail: str) -> None:
    if not condition:
        raise StageCError("provenance", detail)


def _artifact(path: Path, expected: str) -> Dict[str, Any]:
    raw = path.read_bytes()
    actual = _digest(raw)
    _require(actual == expected, "artifact bytes differ: " + str(path))
    try:
        portable = path.resolve().relative_to(Path(__file__).resolve().parents[1])
    except ValueError:
        portable = path.resolve()
    return {"path": str(portable), "bytes": len(raw), "sha256": actual}


def _git(root: Path, *arguments: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(root), *arguments], check=True, capture_output=True,
        text=True,
    )
    return result.stdout


def _commit_identity(root: Path, commit: str, subject: str) -> Dict[str, Any]:
    fields = ("H", "P", "aI", "cI", "an", "ae", "cn", "ce", "s")
    output = _git(root, "show", "-s", "--format=" + "%n".join("%" + field for field in fields), commit)
    values = output.rstrip("\n").split("\n")
    _require(len(values) == len(fields), "git commit identity differs: " + commit)
    record = dict(zip(fields, values))
    _require(record["H"] == commit and record["s"] == subject,
             "git commit binding differs: " + commit)
    return {
        "commit": record["H"],
        "parents": record["P"].split(),
        "author_time": record["aI"],
        "commit_time": record["cI"],
        "author": record["an"] + " <" + record["ae"] + ">",
        "committer": record["cn"] + " <" + record["ce"] + ">",
        "subject": record["s"],
    }


def _validate_session_extract(raw: bytes) -> Mapping[str, Any]:
    _require(_digest(raw) == SESSION_EXTRACT_SHA256, "Stage I session extract bytes differ")
    value = _decode(raw, "Stage I session extract")
    source = value.get("source", {})
    _require(source.get("path") == str(SESSION_SOURCE_PATH),
             "Stage I source session path differs")
    _require(source.get("sha256") == SESSION_SOURCE_SHA256,
             "Stage I source session hash differs")
    _require(source.get("custodian") == "operator Codex session archive",
             "Stage I source custodian differs")
    _require(source.get("retrieval_method")
             == "read-only exact JSONL line extraction",
             "Stage I retrieval method differs")
    _require(value.get("security", {}).get("credential_values copied") is False,
             "Stage I credential boundary differs")
    text = raw.decode("utf-8")
    for forbidden in ('"chars"', "1234", "API_KEY", "OPENAI_API_KEY", "Bearer "):
        _require(forbidden.lower() not in text.lower(),
                 "Stage I extract contains prohibited credential material")
    redactions = {item.get("line_number") for item in value.get("redactions", [])}
    _require(redactions == {11465, 11489, 11647},
             "Stage I credential redactions differ")
    records = {item.get("line_number"): item for item in value.get("records", [])}
    _require(set(records) == {
        11459, 11469, 11474, 11478, 11483, 11493, 11505, 11509,
        11512, 11620, 11641, 11651,
    }, "Stage I selected session records differ")

    # Reproduce from the non-protected original archive when retained.  After
    # Codex session retention removed that mutable host file, the pinned Stage I
    # extract remains the durable evidence boundary; never invent a replacement.
    if SESSION_SOURCE_PATH.exists():
        source_raw = SESSION_SOURCE_PATH.read_bytes()
        _require(_digest(source_raw) == SESSION_SOURCE_SHA256,
                 "Stage I live source archive bytes differ")
        source_records: Dict[int, Dict[str, Any]] = {}
        with SESSION_SOURCE_PATH.open() as stream:
            for line_number, line in enumerate(stream, 1):
                if line_number in records or line_number in redactions:
                    source_value = json.loads(line)
                    if line_number in records:
                        source_records[line_number] = {
                            "line_number": line_number,
                            "timestamp": source_value.get("timestamp"),
                            "record_type": source_value.get("type"),
                            "payload": source_value.get("payload"),
                        }
                    else:
                        source_records[line_number] = source_value
        _require(set(source_records) == set(records) | redactions,
                 "Stage I source line inventory differs")
        for line_number, record in records.items():
            _require(source_records[line_number] == record,
                     "Stage I extracted record differs from source: " + str(line_number))
        for line_number in redactions:
            redacted = source_records[line_number]
            payload = redacted.get("payload", {})
            _require(redacted.get("type") == "response_item"
                     and payload.get("type") == "function_call"
                     and payload.get("name") == "write_stdin",
                     "Stage I redacted source record differs: " + str(line_number))

    approval_output = str(records[11469]["payload"].get("item", {}).get("aggregated_output", ""))
    for expected in (APPROVAL_SHA256, LICENSE_REVIEW_SHA256, EXECUTION_PROFILE_SHA256):
        _require(expected in approval_output, "Stage I approval output differs")
    validation_output = str(records[11478]["payload"].get("item", {}).get("aggregated_output", ""))
    _require("approval_validation=pass" in validation_output,
             "Stage I approval validation differs")
    launch = records[11512]["payload"].get("item", {})
    command = " ".join(launch.get("command", []))
    _require("trusted-root-bootstrap-grrr-poc2-9d3df87" in command
             and PRIVATE_RUNTIME not in command,
             "Stage I launcher command differs")
    _require(launch.get("status") == "completed",
             "Stage I launcher status differs")
    process_output = str(records[11509]["payload"].get("item", {}).get("aggregated_output", ""))
    _require("_grrr_evaluator" in process_output and "_grrr_runner" in process_output,
             "Stage I process identities differ")
    preservation_output = str(records[11651]["payload"].get("item", {}).get("aggregated_output", ""))
    _require(TRUSTED_READBACK_SHA256 in preservation_output,
             "Stage I preservation output differs")
    boundaries = {item.get("line_number"): item for item in value.get("boundaries", [])}
    execution = boundaries.get(11512, {})
    _require(execution.get("started_at") == EXECUTION_STARTED_AT,
             "Stage I execution start differs")
    _require(execution.get("completed_at") == EXECUTION_COMPLETED_AT,
             "Stage I execution completion differs")
    _require(execution.get("duration_ms") == EXECUTION_DURATION_MS,
             "Stage I execution duration differs")
    _require(not any(value.get("authority", {}).values()),
             "Stage I extract authority differs")
    _require(value.get("outcome", {}).get("final_classification") is None
             and value.get("outcome", {}).get("spendable") is None,
             "Stage I extract outcome differs")
    return value


def _validate_plan(root: Path) -> Mapping[str, Any]:
    path = root / "docs/evidence/trusted-observation/v4-run-9d3df87/plan.json"
    value = _decode(path.read_bytes(), "trusted plan")
    _require(_digest(path.read_bytes()) == TRUSTED_PLAN_SHA256,
             "trusted plan bytes differ")
    config = value.get("config", {})
    _require(config.get("execution_profile") == EXECUTION_PROFILE_SHA256,
             "trusted execution profile differs")
    _require(config.get("network") is False and config.get("paid_dispatch") is False,
             "trusted plan control flags differ")
    _require(value.get("execution_authorized") is False
             and value.get("execution_performed") is False,
             "trusted proposal execution flags differ")
    code = value.get("code")
    _require(isinstance(code, dict) and len(code) == 26,
             "trusted plan code inventory differs")
    for name, expected in code.items():
        raw = subprocess.check_output(
            ["git", "-C", str(root), "show", SOURCE_COMMIT + ":" + name])
        _require(_digest(raw) == expected,
                 "source code identity differs: " + name)
    assets = value.get("asset_hashes")
    _require(isinstance(assets, dict) and len(assets) == 4,
             "trusted asset inventory differs")
    return value


def _validate_export(root: Path) -> Dict[str, Any]:
    source = _commit_identity(
        root, SOURCE_COMMIT, "harden(GRRR-gu87): require wheel-owned trusted bootstrap")
    export = _commit_identity(
        root, EXPORT_COMMIT, "evidence(GRRR-gu87): preserve v4 trusted observation run")
    _require(export["parents"] == [SOURCE_COMMIT],
             "trusted export parent differs")
    expected = {
        "READBACK.json": TRUSTED_READBACK_SHA256,
        "evaluator/ledger.sqlite": TRUSTED_LEDGER_SHA256,
        "evaluator/snapshot.json": TRUSTED_SNAPSHOT_SHA256,
        "plan.json": TRUSTED_PLAN_SHA256,
    }
    prefix = "docs/evidence/trusted-observation/v4-run-9d3df87/"
    for name, digest in expected.items():
        raw = subprocess.check_output(
            ["git", "-C", str(root), "show", EXPORT_COMMIT + ":" + prefix + name])
        _require(_digest(raw) == digest, "trusted export member differs: " + name)
        current = (root / prefix / name).read_bytes()
        _require(_digest(current) == digest,
                 "current trusted export member differs: " + name)
    return {"source_commit": source, "export_commit": export}


def _stage_h_candidates(root: Path) -> List[Dict[str, Any]]:
    path = root / "docs/evidence/spendability/stage-h/RESPONSE-READINESS.json"
    raw = path.read_bytes()
    _require(_digest(raw) == STAGE_H_READINESS_SHA256,
             "Stage H readiness bytes differ")
    value = _decode(raw, "Stage H readiness")
    package = root / "docs/evidence/spendability/stage-h/PACKAGE.json"
    _require(_digest(package.read_bytes()) == STAGE_H_PACKAGE_SHA256,
             "Stage H package bytes differ")
    candidates = [item for item in value.get("items", [])
                  if item.get("response_readiness")
                  == "candidate-record-set-not-response-ready"]
    _require(len(candidates) == 8, "Stage H candidate inventory differs")
    return candidates


def _enrichment() -> Dict[str, Dict[str, str]]:
    return {
        "issuer_code_toolchain_profile": {
            "status": "validated-common-candidate",
            "evidence": "pinned source commit, 26 plan code hashes, runtime profile, helper, supervisor, image, Python, and QEMU identities",
        },
        "authorization": {
            "status": "candidate-reference-found",
            "evidence": "corrected execution-approval and license-review hashes plus validation output in operator session archive",
            "remaining": "exact protected approval/review artifact bytes and independent custody review",
        },
        "principal_and_issuer_identity": {
            "status": "partial-common-candidate",
            "evidence": "observed _grrr_evaluator and _grrr_runner process names in session archive",
            "remaining": "numeric process UID mapping and per-request authenticated principal/issuer binding",
        },
        "operation_boundary": {
            "status": "partial-common-candidate",
            "evidence": "exact root launcher command, private runtime path, batch start/end, and completion status",
            "remaining": "per-reservation operation IDs and request boundaries",
        },
        "measurement_boundary": {
            "status": "partial-common-candidate",
            "evidence": "batch UTC start/end and 240253 ms duration",
            "remaining": "per-reservation UTC start/end, clock, and window digest",
        },
        "custody": {
            "status": "validated-common-candidate",
            "evidence": "source commit, export commit, current bytes, redacted session archive, and preservation readback",
            "remaining": "independent response-custody classification",
        },
        "final_classification": {
            "status": "missing",
            "evidence": "no independent final classifier",
        },
    }


def build_provenance_record(root: Path,
                            created_at: str = STAGE_I_CREATED_AT) -> Dict[str, Any]:
    session_path = root / "docs/evidence/spendability/stage-i/SESSION-EXTRACT.json"
    session = _validate_session_extract(session_path.read_bytes())
    plan = _validate_plan(root)
    export = _validate_export(root)
    candidates = _stage_h_candidates(root)
    enrichment = _enrichment()
    items = []
    for candidate in candidates:
        items.append({
            "request_item_id": candidate["request_item_id"],
            "reservation_id": candidate["subject"],
            "classification": None,
            "response_readiness": "candidate-record-set-not-response-ready",
            "common_evidence": enrichment,
            "reservation_specific_missing": [
                "authenticated principal and issuer binding",
                "approved request authorization bytes",
                "dispatch operation identity and request boundary",
                "UTC measurement start/end, clock, and window digest",
                "reservation-specific custody classification",
            ],
        })
    return {
        "schema_version": 1,
        "record_type": "spendability-provenance-enrichment-v1",
        "created_at": created_at,
        "basis": {
            "stage_h_package_sha256": STAGE_H_PACKAGE_SHA256,
            "stage_h_readiness_sha256": STAGE_H_READINESS_SHA256,
            "session_source_sha256": SESSION_SOURCE_SHA256,
            "session_extract_sha256": SESSION_EXTRACT_SHA256,
            "trusted_plan_sha256": TRUSTED_PLAN_SHA256,
            "trusted_readback_sha256": TRUSTED_READBACK_SHA256,
            "trusted_ledger_sha256": TRUSTED_LEDGER_SHA256,
            "trusted_snapshot_sha256": TRUSTED_SNAPSHOT_SHA256,
            "source_commit": SOURCE_COMMIT,
            "export_commit": EXPORT_COMMIT,
            "approval_sha256": APPROVAL_SHA256,
            "license_review_sha256": LICENSE_REVIEW_SHA256,
            "execution_profile_sha256": EXECUTION_PROFILE_SHA256,
        },
        "artifacts": {
            "session_extract": _artifact(session_path, SESSION_EXTRACT_SHA256),
            "trusted_plan": _artifact(
                root / "docs/evidence/trusted-observation/v4-run-9d3df87/plan.json",
                TRUSTED_PLAN_SHA256),
        },
        "git_custody": export,
        "execution_boundary": {
            "started_at": EXECUTION_STARTED_AT,
            "completed_at": EXECUTION_COMPLETED_AT,
            "duration_ms": EXECUTION_DURATION_MS,
            "private_runtime": PRIVATE_RUNTIME,
            "source": "redacted operator session archive line 11512",
        },
        "items": items,
        "summary": {
            "candidate_record_sets": len(items),
            "response_ready_record_sets": 0,
            "common_toolchain_profile_candidates": 1,
            "authorization_reference_candidates": 1,
            "batch_execution_boundary_candidates": 1,
            "custody_chain_candidates": 1,
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


def validate_provenance_record(record: Mapping[str, Any],
                               root: Path) -> Dict[str, Any]:
    expected = build_provenance_record(root, created_at=record.get("created_at", ""))
    if record != expected:
        raise StageCError("provenance", "record differs from exact regeneration")
    return {
        "record_valid": True,
        "response_ready": False,
        "classification_complete": False,
        "spendable": None,
        "allowed_mutations": [],
        "execution_authorized": False,
    }
