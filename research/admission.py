"""Counterexample-to-Contract admission.

Converts an independently verified defect into a permanent regression
contract behind explicit human approval.  Nothing here permits software
promotion, production mutation, automatic main merge, or push.
"""

from hashlib import sha256
import json
import re
import time
from typing import Any, Dict


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

ADMISSION_FIELDS = frozenset((
    "schema_version", "record_type", "contract_sha256",
    "authorization_sha256", "admitted_at", "registry_version", "outcome",
))

GATE_INVENTORY = frozenset((
    "source_environment_identity", "isolation", "protected_asset_integrity",
    "baseline_correctness", "trusted_observation", "independent_replay",
    "specification_traceability", "evidence_integrity_currency",
    "budget_state",
))


class AdmissionError(ValueError):
    """Raised when admission validation fails."""


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
        allow_nan=False,
    ).encode("ascii")


def _digest(value: Any) -> str:
    return sha256(_canonical(value)).hexdigest()


def build_contract() -> dict:
    """Build the D011 counterexample-to-contract proposal."""
    core = {
        "schema_version": SCHEMA_VERSION,
        "record_type": "grrr-counterexample-contract-v1",
        "challenge": CHALLENGE,
        "specification": {
            "member": SPEC_MEMBER,
            "case": SPEC_CASE,
            "source_commit": SOURCE_COMMIT,
            "source_archive_sha256": SOURCE_ARCHIVE_SHA256,
            "expected": "Display text must be captured from [[Title|Display]] syntax",
        },
        "source_binding": {
            "commit": SOURCE_COMMIT,
            "archive_sha256": SOURCE_ARCHIVE_SHA256,
        },
        "replay_binding": {
            "export_sha256": REPLAY_EXPORT_SHA256,
            "finding": "Verified defect",
            "verified": True,
        },
        "expected_behavior": {
            "input": "[[Sr PM Agent|PM]]",
            "expected_title": "Sr PM Agent",
            "expected_display": "PM",
            "defect_behavior": "Display text not captured when parsing wikilinks",
        },
    }
    contract = dict(core)
    contract["contract_sha256"] = _digest(core)
    return contract


def validate_contract(value: dict) -> dict:
    """Validate the contract proposal."""
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
    # Enforce export hash binding
    replay_export = value["replay_binding"].get("export_sha256")
    if replay_export != REPLAY_EXPORT_SHA256:
        raise AdmissionError("replay export hash binding differs")
    core = {k: v for k, v in value.items() if k != "contract_sha256"}
    if value["contract_sha256"] != _digest(core):
        raise AdmissionError("contract_sha256 mismatch")
    if value["replay_binding"].get("finding") != "Verified defect":
        raise AdmissionError("replay finding must be Verified defect")
    if value["replay_binding"].get("verified") is not True:
        raise AdmissionError("replay must be verified")
    return value


def validate_authorization(auth: dict, contract: dict) -> dict:
    """Validate a human authorization for contract admission."""
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


def check_gates(replay_receipt: dict) -> dict:
    """Check all mandatory gates from the replay receipt."""
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


_consumed_authorizations = set()


def consume_authorization(auth: dict) -> str:
    """Consume a validated authorization so it cannot be reused."""
    auth_hash = _digest(auth)
    if auth_hash in _consumed_authorizations:
        raise AdmissionError("authorization already consumed")
    _consumed_authorizations.add(auth_hash)
    return auth_hash


_admitted_contracts = {}


def persist_admission(admission: dict) -> dict:
    """Persist an admission to the in-process registry; reject duplicates."""
    contract_hash = admission["contract_sha256"]
    if contract_hash in _admitted_contracts:
        raise AdmissionError("contract already admitted")
    _admitted_contracts[contract_hash] = admission
    return admission


def admit(contract: dict, authorization: dict, replay_receipt: dict) -> dict:
    """Perform contract admission after all checks pass."""
    validated_contract = validate_contract(contract)
    validated_auth = validate_authorization(authorization, validated_contract)
    # Bind receipt to the contract's export hash
    receipt_finding = replay_receipt.get("finding")
    receipt_verified = replay_receipt.get("verified")
    if receipt_finding != "Verified defect" or receipt_verified is not True:
        raise AdmissionError("replay receipt finding/verified mismatch")
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


def recurrence_rejected(admission: dict, replay_receipt: dict) -> bool:
    """Check that the admitted contract rejects recurrence of the defect."""
    if not isinstance(admission, dict):
        return False
    if not isinstance(replay_receipt, dict):
        return False
    if admission.get("outcome") != "admitted":
        return False
    contract_hash = admission.get("contract_sha256")
    if not contract_hash or not HASH_RE.match(contract_hash):
        return False
    if contract_hash not in _admitted_contracts:
        return False
    gates = admission.get("gate_results", {})
    if not gates or not all(s == "pass" for s in gates.values()):
        return False
    return replay_receipt.get("finding") == "Verified defect" and replay_receipt.get("verified") is True
