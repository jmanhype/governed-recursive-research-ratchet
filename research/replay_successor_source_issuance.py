"""Build the repository-only v4 protected-source issuance package.

The builder reads only the eight retained Stage R source files.  It does not
access `/Library/GRRR`, stage protected records, install anything, amend a
budget, reconcile history, or authorize replay.
"""

from hashlib import sha256
import os
from pathlib import Path
import stat
from typing import Any, Dict, Mapping

from spendability_stage_c import AUTHORITY_FIELDS, StageCError, digest


SCHEMA_VERSION = 1
BASE_COMMIT = "23fdac5fcdc9bcef5147314a8f3c8bcb6d458d3f"
STAGE_P_PACKAGE_SHA256 = "ba7e8a45486a21ff399027821d3b0bd1d21c6577730597f900f3c21fb192c0b1"
STAGE_Q_PACKAGE_SHA256 = "d953651c0bd635a1e80295376665fd2331b86ac9b5f25f726b945bcf9e41fb3e"
PREPARED_AT = "2026-11-03T14:00:00Z"
SOURCE_DIRECTORY = "docs/evidence/replay-authority/stage-r/source"
TEST_SOURCE_SHA256 = "e9aac58ccf0d0ad0f2e483cb0335d4eadaa1ffebefc929df17a1adb19f08b759"

ROLE_FILES = {
    "installer-entrypoint": "install-replay-successor-v4",
    "v4-store-schema": "replay-successor-v4-v4_store_schema.py",
    "stage-n-contract": "replay-successor-v4-stage_n_contract.py",
    "stage-o-runtime-adapter": "replay-successor-v4-stage_o_runtime_adapter.py",
    "protected-preflight": "replay-successor-v4-protected_preflight.py",
    "atomic-publisher": "replay-successor-v4-atomic_publisher.py",
    "postflight-verifier": "replay-successor-v4-postflight_verifier.py",
    "failure-preservation": "replay-successor-v4-failure_preservation.py",
}
ROLE_ORDER = tuple(ROLE_FILES)
DESTINATIONS = {
    "installer-entrypoint": "/Library/GRRR/bootstrap/install-replay-successor-v4",
    "v4-store-schema": "/Library/GRRR/bootstrap/replay-successor-v4-v4_store_schema.py",
    "stage-n-contract": "/Library/GRRR/bootstrap/replay-successor-v4-stage_n_contract.py",
    "stage-o-runtime-adapter": "/Library/GRRR/bootstrap/replay-successor-v4-stage_o_runtime_adapter.py",
    "protected-preflight": "/Library/GRRR/bootstrap/replay-successor-v4-protected_preflight.py",
    "atomic-publisher": "/Library/GRRR/bootstrap/replay-successor-v4-atomic_publisher.py",
    "postflight-verifier": "/Library/GRRR/bootstrap/replay-successor-v4-postflight_verifier.py",
    "failure-preservation": "/Library/GRRR/bootstrap/replay-successor-v4-failure_preservation.py",
}
ROLE_MARKERS = {
    "installer-entrypoint": ("v4 source issuance is not approved",),
    "v4-store-schema": ("CREATE TABLE state", "INSERT INTO state VALUES(1,1)"),
    "stage-n-contract": ("candidate-fresh-replay-successor-poc",),
    "stage-o-runtime-adapter": ("source-prepared-unissued",),
    "protected-preflight": ("protected path is outside the sandbox",),
    "atomic-publisher": ("O_EXCL", "os.fsync"),
    "postflight-verifier": ("EXPECTED_OBJECTS", "sandbox database schema differs"),
    "failure-preservation": ("uncertain-no-retry", "uncertain.json"),
}
EXPECTED_SOURCE_SHA256 = {
    "installer-entrypoint": "94b37112fc3b3146078b6edd0cf80d5e845f1cc83543344d79400d144d453dbc",
    "v4-store-schema": "629c6a70936fb94ea4b4a89b4dc3c94095aa2586194c077e4c06258b2c7ce644",
    "stage-n-contract": "d2105c6fbab6edd42ad9724e6ff2313d2531c11af14625bfb0cf8a81b9646fb5",
    "stage-o-runtime-adapter": "f54f051684dd9be4ccf635d3029cb1f099ddb227e8d763efad2c8bf24e3478c4",
    "protected-preflight": "0e09ccc6f995e24ab983489755df6a14028c154a99b84811b95d6ea95bf0946f",
    "atomic-publisher": "c448f4853e6bb9467c6994b64b3f04dfd9ee9c6d0718de69529eb24218e5a719",
    "postflight-verifier": "f276c0bd84a4fe43d5661672600734120af1332c45c372fc6881a2913491ca46",
    "failure-preservation": "8fb37a74e96c7fab7f96fed74ad1aea187fc306716ebb024a1cd0059ca9ded47",
}
RECORD_FIELDS = frozenset((
    "schema_version", "record_type", "decision", "basis", "sources",
    "source_bundle_sha256", "prepared_at", "issuance_status", "gates",
    "outcome", "authority",
))


def _require(condition: bool, detail: str) -> None:
    if not condition:
        raise StageCError("replay_successor_source_issuance", detail)


def _sha(raw: bytes) -> str:
    return sha256(raw).hexdigest()


def _source_root(root: Path) -> Path:
    _require(isinstance(root, Path) and root.is_absolute() and root.is_dir(),
             "repository root differs")
    value = root / SOURCE_DIRECTORY
    _require(value.is_dir() and not value.is_symlink(),
             "Stage R source root differs")
    return value


def _read_role(root: Path, role: str) -> Dict[str, Any]:
    source_root = _source_root(root)
    relative = Path(ROLE_FILES[role])
    _require(not relative.is_absolute() and ".." not in relative.parts,
             "Stage R source path escapes repository")
    path = source_root / relative
    info = path.lstat()
    _require(stat.S_ISREG(info.st_mode) and not path.is_symlink()
             and info.st_nlink == 1,
             "Stage R source is not a regular file: " + role)
    raw = path.read_bytes()
    _require(len(raw) <= 1_048_576, "Stage R source is too large: " + role)
    marker = ROLE_MARKERS[role][0].encode("ascii")
    _require(marker in raw, "Stage R role marker differs: " + role)
    _require(_sha(raw) == EXPECTED_SOURCE_SHA256[role],
             "Stage R source bytes differ: " + role)
    return {
        "role": role,
        "file": str(relative),
        "protected_destination": DESTINATIONS[role],
        "bytes": len(raw),
        "sha256": _sha(raw),
    }


def build_source_bundle(root: Path) -> Dict[str, Any]:
    sources = [_read_role(root, role) for role in ROLE_ORDER]
    hashes = [item["sha256"] for item in sources]
    _require(len(set(hashes)) == len(hashes), "Stage R source hashes are not distinct")
    bundle_hash = digest({item["role"]: item["sha256"] for item in sources})
    return {
        "schema_version": SCHEMA_VERSION,
        "record_type": "replay-successor-v4-source-issuance-prepared-v1",
        "decision": "prepared-not-issued",
        "basis": {
            "story_head": BASE_COMMIT,
            "stage_p_package_sha256": STAGE_P_PACKAGE_SHA256,
            "stage_q_package_sha256": STAGE_Q_PACKAGE_SHA256,
        },
        "sources": sources,
        "source_bundle_sha256": bundle_hash,
        "prepared_at": PREPARED_AT,
        "issuance_status": "prepared-not-issued",
        "gates": {
            "source_role_closure": {"status": "pass", "evidence": [bundle_hash]},
            "sandbox_functional_checks": {
                "status": "pass", "evidence": [TEST_SOURCE_SHA256],
            },
            "independent_source_review": {"status": "not-run", "evidence": []},
            "operator_issuance": {"status": "not-run", "evidence": []},
            "protected_staging": {"status": "not-run", "evidence": []},
        },
        "outcome": {
            "prepared": True,
            "issued": False,
            "installation_ready": False,
            "protected_access_performed": False,
            "allowed_mutations": [],
            "spendable": None,
        },
        "authority": {name: False for name in sorted(AUTHORITY_FIELDS)},
    }


def validate_source_bundle(value: Any, root: Path) -> Dict[str, Any]:
    record = value
    _require(isinstance(record, dict) and set(record) == set(RECORD_FIELDS),
             "Stage R source bundle fields differ")
    expected = build_source_bundle(root)
    _require(digest(record) == digest(expected),
             "Stage R source bundle differs from exact regeneration")
    return record


def verify_source_files(root: Path) -> Dict[str, Any]:
    record = build_source_bundle(root)
    validate_source_bundle(record, root)
    return {
        "members": len(record["sources"]),
        "source_bundle_sha256": record["source_bundle_sha256"],
        "distinct_hashes": len({item["sha256"] for item in record["sources"]}),
        "protected_access": False,
    }
