"""Counterexample-to-Contract admission.

Converts an independently verified defect into a permanent regression
contract behind explicit human approval.  Nothing here permits software
promotion, production mutation, automatic main merge, or push.
"""

from hashlib import sha256
import json
import os
from pathlib import Path
import re
import threading
import time

SCHEMA_VERSION = 1
CHALLENGE = "GRRR-VC-D011"
APPROVED_OPERATOR = "operator-speed"
REPLAY_EXPORT_SHA256 = (
    "ab8d72f25c3a4ce2f5d5d672c4d052ea2de442f9c9384bd381d8222d7a91b689"
)
SPEC_MEMBER = "wikilinks_test.go"
SPEC_CASE = "TestParseWikilinks/link with display text"
SOURCE_COMMIT = "129e0b3f15a3bd6af949ee47d76f6855c582ab73"
SOURCE_ARCHIVE_SHA256 = (
    "e644b9848b306f158a2367293dd96c66dac2bed97c0dd42891db007667c0ae7e"
)

HASH_RE = re.compile(r"[0-9a-f]{64}\Z")
OPERATOR_RE = re.compile(r"[A-Za-z0-9_.-]{1,64}\Z")
TIMESTAMP_RE = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z\Z")

CONTRACT_FIELDS = frozenset((
    "schema_version", "record_type", "challenge", "specification",
    "source_binding", "replay_binding", "expected_behavior",
    "contract_sha256",
))

AUTHORIZATION_FIELDS = frozenset((
    "schema_version", "record_type", "contract_sha256", "authorized_by",
    "authorized_at", "authorization_type", "consumed",
))

GATE_INVENTORY = frozenset((
    "source_environment_identity", "isolation", "protected_asset_integrity",
    "baseline_correctness", "trusted_observation", "independent_replay",
    "specification_traceability", "evidence_integrity_currency",
    "budget_state",
))

REGISTRY_PATH = Path(__file__).resolve().parent.parent / "docs/evidence/contract-admission/REGISTRY.json"
_registry_lock = threading.Lock()


def _load_registry():
    if REGISTRY_PATH.exists():
        try:
            return json.loads(REGISTRY_PATH.read_bytes())
        except (json.JSONDecodeError, OSError):
            pass
    return {"consumed_authorizations": [], "admitted_contracts": {}}


def _save_registry(registry):
    REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp = REGISTRY_PATH.with_suffix(".tmp")
    tmp.write_text(json.dumps(registry, sort_keys=True, indent=2) + "\n")
    os.replace(tmp, REGISTRY_PATH)


class AdmissionError(ValueError):
    pass


def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("ascii")


def _digest(value):
    return sha256(_canonical(value)).hexdigest()


def build_contract():
    core = {
        "schema_version": SCHEMA_VERSION,
        "record_type": "grrr-counterexample-contract-v1",
        "challenge": CHALLENGE,
        "specification": {
            "member": SPEC_MEMBER, "case": SPEC_CASE,
            "source_commit": SOURCE_COMMIT,
            "source_archive_sha256": SOURCE_ARCHIVE_SHA256,
            "expected": "Display text must be captured from [[Title|Display]] syntax",
        },
        "source_binding": {"commit": SOURCE_COMMIT, "archive_sha256": SOURCE_ARCHIVE_SHA256},
        "replay_binding": {"export_sha256": REPLAY_EXPORT_SHA256, "finding": "Verified defect", "verified": True},
        "expected_behavior": {
            "input": "[[Sr PM Agent|PM]]", "expected_title": "Sr PM Agent",
            "expected_display": "PM",
            "defect_behavior": "Display text not captured when parsing wikilinks",
        },
    }
    contract = dict(core)
    contract["contract_sha256"] = _digest(core)
    return contract


def validate_contract(value):
    if not isinstance(value, dict):
        raise AdmissionError("contract must be dict")
    if set(value) != CONTRACT_FIELDS:
        raise AdmissionError("contract fields differ")
    if type(value["schema_version"]) is not int or value["schema_version"] != SCHEMA_VERSION:
        raise AdmissionError("schema_version must be integer 1")
    if value["record_type"] != "grrr-counterexample-contract-v1":
        raise AdmissionError("record_type differs")
    if value["challenge"] != CHALLENGE:
        raise AdmissionError("challenge differs")
    core = {k: v for k, v in value.items() if k != "contract_sha256"}
    if value["contract_sha256"] != _digest(core):
        raise AdmissionError("contract_sha256 mismatch")
    replay = value["replay_binding"]
    if replay.get("export_sha256") != REPLAY_EXPORT_SHA256:
        raise AdmissionError("replay export hash binding differs")
    if replay.get("finding") != "Verified defect":
        raise AdmissionError("replay finding must be Verified defect")
    if replay.get("verified") is not True:
        raise AdmissionError("replay must be verified")
    return value


def validate_authorization(auth, contract):
    if not isinstance(auth, dict):
        raise AdmissionError("authorization must be dict")
    if set(auth) != AUTHORIZATION_FIELDS:
        raise AdmissionError("authorization fields differ")
    if type(auth["schema_version"]) is not int or auth["schema_version"] != SCHEMA_VERSION:
        raise AdmissionError("schema_version must be integer 1")
    if auth["record_type"] != "grrr-contract-admission-authorization-v1":
        raise AdmissionError("record_type differs")
    if auth["contract_sha256"] != contract["contract_sha256"]:
        raise AdmissionError("authorization targets a different contract")
    if not isinstance(auth["authorized_by"], str) or not OPERATOR_RE.match(auth["authorized_by"]):
        raise AdmissionError("authorized_by must be a valid operator name")
    if auth["authorized_by"] != APPROVED_OPERATOR:
        raise AdmissionError("authorized_by is not the approved operator")
    if not isinstance(auth["authorized_at"], str) or not TIMESTAMP_RE.match(auth["authorized_at"]):
        raise AdmissionError("authorized_at must be ISO-8601 UTC")
    if auth["authorization_type"] != "permanent-contract-admission":
        raise AdmissionError("authorization_type must be permanent-contract-admission")
    if auth["consumed"] is not False:
        raise AdmissionError("authorization must not be consumed")
    return auth


def check_gates(replay_receipt):
    gates = replay_receipt.get("gates", {})
    results = {}
    for gate_name in sorted(GATE_INVENTORY):
        status = gates.get(gate_name, {}).get("status", "not-run")
        results[gate_name] = status
        if status != "pass":
            raise AdmissionError("gate %s is %s, must be pass" % (gate_name, status))
    if replay_receipt.get("finding") != "Verified defect":
        raise AdmissionError("finding must be Verified defect")
    if replay_receipt.get("verified") is not True:
        raise AdmissionError("replay must be verified")
    return results


def consume_authorization(auth):
    with _registry_lock:
        registry = _load_registry()
        auth_hash = _digest(auth)
        if auth_hash in registry["consumed_authorizations"]:
            raise AdmissionError("authorization already consumed")
        registry["consumed_authorizations"].append(auth_hash)
        _save_registry(registry)
    return auth_hash


def persist_admission(admission):
    with _registry_lock:
        registry = _load_registry()
        contract_hash = admission["contract_sha256"]
        if contract_hash in registry["admitted_contracts"]:
            raise AdmissionError("contract already admitted")
        registry["admitted_contracts"][contract_hash] = admission
        _save_registry(registry)
    return admission


def admit(contract, authorization, replay_receipt):
    validated_contract = validate_contract(contract)
    validated_auth = validate_authorization(authorization, validated_contract)
    gate_results = check_gates(replay_receipt)
    auth_hash = consume_authorization(validated_auth)
    admission = {
        "schema_version": SCHEMA_VERSION,
        "record_type": "grrr-contract-admission-v1",
        "contract_sha256": validated_contract["contract_sha256"],
        "authorization_sha256": auth_hash,
        "admitted_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "registry_version": 1,
        "outcome": "admitted",
        "gate_results": gate_results,
    }
    return persist_admission(admission)


def recurrence_rejected(admission, replay_receipt):
    if not isinstance(admission, dict) or not isinstance(replay_receipt, dict):
        return False
    if admission.get("outcome") != "admitted":
        return False
    contract_hash = admission.get("contract_sha256")
    if not isinstance(contract_hash, str) or not HASH_RE.match(contract_hash):
        return False
    registry = _load_registry()
    if contract_hash not in registry.get("admitted_contracts", {}):
        return False
    gates = admission.get("gate_results", {})
    if not isinstance(gates, dict) or set(gates) != GATE_INVENTORY:
        return False
    if not all(s == "pass" for s in gates.values()):
        return False
    receipt_gates = replay_receipt.get("gates", {})
    if not isinstance(receipt_gates, dict):
        return False
    for gate_name in GATE_INVENTORY:
        if receipt_gates.get(gate_name, {}).get("status") != "pass":
            return False
    return replay_receipt.get("finding") == "Verified defect" and replay_receipt.get("verified") is True
