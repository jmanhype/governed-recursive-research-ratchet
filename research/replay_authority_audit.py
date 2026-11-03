"""Build a fail-closed replay-accounting authority-state audit."""

from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Dict, List, Mapping, Sequence

from spendability_stage_c import AUTHORITY_FIELDS, StageCError


STAGE_A_BASELINE_SHA256 = "7608cbe6fc5f671b88573eca8b642ebfbc172f0cb920f75d60ca34cfa60c730a"
STAGE_M_CREATED_AT = "2026-10-28T20:00:00Z"
LEGACY_PROFILE = "offline"
REPLAY_PROFILE = "independent-replay"


def _digest(raw: bytes) -> str:
    return sha256(raw).hexdigest()


def _decode(raw: bytes, label: str) -> Dict[str, Any]:
    value = json.loads(raw)
    if not isinstance(value, dict):
        raise StageCError("replay_authority_audit", label + " must be an object")
    return value


def _require(condition: bool, detail: str) -> None:
    if not condition:
        raise StageCError("replay_authority_audit", detail)


def preflight_classification(binding: Mapping[str, Any],
                             registered_profiles: Sequence[str]) -> Dict[str, Any]:
    """Mirror replay.preflight's exact version/profile authority gates."""
    profiles = binding.get("profiles", [])
    version = binding.get("version")
    if REPLAY_PROFILE not in registered_profiles or REPLAY_PROFILE not in profiles:
        return {
            "result": "fail",
            "code": "GateBlocked",
            "reason": "independent-replay profile absent",
        }
    if type(version) is int and version == 3:
        return {
            "result": "fail",
            "code": "GateBlocked",
            "reason": "v3 stop-only read-only binding",
        }
    if type(version) is not int or version != 1:
        return {
            "result": "fail",
            "code": "GateBlocked",
            "reason": "registration/frozen binding is not writable v1",
        }
    return {"result": "pass"}


def store_classification(binding: Mapping[str, Any],
                         legacy_profiles: Sequence[str],
                         registered_profiles: Sequence[str]) -> Dict[str, Any]:
    """Mirror persistent binding schema, profile, and mutation gates."""
    version = binding.get("version")
    registered = type(version) is int and version == 2
    recovered = type(version) is int and version == 3
    expected_profiles = list(registered_profiles if registered or recovered else legacy_profiles)
    if type(version) is not int or version not in (1, 2, 3):
        return {
            "result": "fail",
            "code": "RecoveryRequired",
            "reason": "unknown binding version",
            "expected_profiles": expected_profiles,
            "read_only": None,
            "mutations": "denied",
        }
    if binding.get("profiles") != expected_profiles:
        return {
            "result": "fail",
            "code": "RecoveryRequired",
            "reason": "binding profiles differ from version contract",
            "expected_profiles": expected_profiles,
            "read_only": None,
            "mutations": "denied",
        }
    required_fields = {
        "version", "campaign", "store_id", "directory",
        "prior_history_receipt", "profiles", "device", "inode",
    }
    if registered:
        required_fields.add("registration_sha256")
    if recovered:
        required_fields.update(("registration_sha256", "recovery_sha256"))
    if set(binding) != required_fields:
        return {
            "result": "fail",
            "code": "RecoveryRequired",
            "reason": "binding fields differ from version contract",
            "expected_profiles": expected_profiles,
            "read_only": None,
            "mutations": "denied",
        }
    read_only = version in (2, 3)
    return {
        "result": "pass",
        "expected_profiles": expected_profiles,
        "read_only": read_only,
        "mutations": "allowed-after-all-other-budget_checks" if version == 1 else "denied",
    }


def _variant(name: str, binding: Mapping[str, Any],
             legacy_profiles: Sequence[str],
             registered_profiles: Sequence[str]) -> Dict[str, Any]:
    preflight = preflight_classification(binding, registered_profiles)
    store = store_classification(binding, legacy_profiles, registered_profiles)
    replay_possible = (
        preflight["result"] == "pass"
        and store["result"] == "pass"
        and store["read_only"] is False
        and store["mutations"].startswith("allowed")
        and REPLAY_PROFILE in binding.get("profiles", [])
    )
    return {
        "name": name,
        "binding": dict(binding),
        "preflight": preflight,
        "persistent_store_schema": store,
        "independent_replay_possible": replay_possible,
    }


def build_authority_audit(root: Path,
                          created_at: str = STAGE_M_CREATED_AT) -> Dict[str, Any]:
    replay_path = root / "research/replay.py"
    persistent_path = root / "research/persistent_budget.py"
    stage_a_path = root / "docs/evidence/spendability/stage-a/BASELINE.json"
    replay_raw = replay_path.read_bytes()
    persistent_raw = persistent_path.read_bytes()
    stage_a_raw = stage_a_path.read_bytes()
    _require(_digest(stage_a_raw) == STAGE_A_BASELINE_SHA256,
             "Stage A baseline bytes differ")
    stage_a = _decode(stage_a_raw, "Stage A baseline")
    active = stage_a.get("active", {})
    _require(active.get("version") == 3, "audited active binding is not v3")
    _require(REPLAY_PROFILE in active.get("profiles", []),
             "audited active binding lacks independent replay")

    legacy_profiles = ("synthetic", "offline", "trusted-observation")
    registered_profiles = legacy_profiles + (REPLAY_PROFILE,)
    legacy_binding = {
        "version": 1,
        "profiles": list(legacy_profiles),
        "campaign": active["campaign"],
        "store_id": active["store_id"],
        "directory": active["directory"],
        "prior_history_receipt": active["prior_history_receipt"],
        "device": active["device"],
        "inode": active["inode"],
    }
    hypothetical_v1_replay = dict(legacy_binding, profiles=list(registered_profiles))
    v2_replay = dict(
        hypothetical_v1_replay,
        version=2,
        registration_sha256="0" * 64,
    )
    v3_replay = dict(
        v2_replay,
        version=3,
        recovery_sha256="0" * 64,
    )
    variants = [
        _variant("audited-active-v3", active, legacy_profiles, registered_profiles),
        _variant("legal-legacy-v1-three-profiles", legacy_binding,
                 legacy_profiles, registered_profiles),
        _variant("preflight-valid-hypothetical-v1-four-profiles", hypothetical_v1_replay,
                 legacy_profiles, registered_profiles),
        _variant("registered-frozen-v2-four-profiles", v2_replay,
                 legacy_profiles, registered_profiles),
        _variant("recovered-readonly-v3-four-profiles", v3_replay,
                 legacy_profiles, registered_profiles),
    ]
    possible = [variant["name"] for variant in variants
                if variant["independent_replay_possible"]]
    _require(not possible,
             "audit unexpectedly found a replay-capable binding variant")
    return {
        "schema_version": 1,
        "record_type": "replay-authority-state-audit-v1",
        "created_at": created_at,
        "basis": {
            "story_head": "c6fcc8bb611eab2c2f02b14999cdfe45cf44b02d",
            "stage_a_baseline_sha256": STAGE_A_BASELINE_SHA256,
            "replay_py_sha256": _digest(replay_raw),
            "persistent_budget_py_sha256": _digest(persistent_raw),
            "audited_active_binding_sha256": _digest(json.dumps(
                active, sort_keys=True, separators=(",", ":"),
                ensure_ascii=True, allow_nan=False).encode("ascii")),
        },
        "source_contracts": {
            "legacy_profiles": list(legacy_profiles),
            "registered_profiles": list(registered_profiles),
            "preflight_required_version": 1,
            "preflight_required_profile": REPLAY_PROFILE,
            "preflight_rejected_versions": [2, 3],
            "store_writable_version": 1,
            "store_writable_profile_contract": list(legacy_profiles),
            "store_read_only_versions": [2, 3],
        },
        "variants": variants,
        "summary": {
            "variants_audited": len(variants),
            "preflight_pass_variants": sum(
                variant["preflight"]["result"] == "pass" for variant in variants),
            "store_schema_pass_variants": sum(
                variant["persistent_store_schema"]["result"] == "pass"
                for variant in variants),
            "writable_store_variants": sum(
                variant["persistent_store_schema"].get("read_only") is False
                for variant in variants),
            "replay_capable_variants": 0,
        },
        "finding": {
            "classification": "inconsistent-authority-state-machine",
            "detail": (
                "Replay preflight requires v1 plus independent-replay, but the "
                "persistent-store v1 contract permits only the legacy three profiles; "
                "v2/v3 include independent-replay but are frozen/read-only."
            ),
            "required_next_step": (
                "Design and independently review a new binding authority contract; "
                "do not relax preflight or mutate the existing v3 store."
            ),
        },
        "outcome": {
            "replay_possible": False,
            "spendable": None,
            "execution_authorized": False,
            "allowed_mutations": [],
            "protected_access": False,
        },
        "authority": {name: False for name in AUTHORITY_FIELDS},
    }


def validate_authority_audit(record: Mapping[str, Any], root: Path) -> Dict[str, Any]:
    expected = build_authority_audit(root, created_at=record.get("created_at", ""))
    if record != expected:
        raise StageCError("replay_authority_audit", "record differs from exact regeneration")
    return {
        "record_valid": True,
        "replay_possible": False,
        "spendable": None,
        "execution_authorized": False,
        "allowed_mutations": [],
    }
