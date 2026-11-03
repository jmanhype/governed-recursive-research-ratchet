"""Validate the exact parent-mediated v4 protected-staging action.

This module defines and validates the operator authorization record and
staging outcome.  It does not access or mutate ``/Library/GRRR``, execute
the staging script, install anything, amend a budget, reconcile history,
execute replay, admit, promote, merge, or push.
"""

from hashlib import sha256
import json
import os
from pathlib import Path
import posixpath
import re
import stat
from typing import Any, Dict


SCHEMA_VERSION = 1
STAGE_S_RECORD_SHA256 = (
    "1d27da0d718ac7713f54bc73d4b87d5bcd1ea57f3eb55de1e74b0e2c933a75c9"
)
STAGE_S_PACKAGE_SHA256 = (
    "4f81a932e0dc1ce58495d925a6c0a574653d897f6bea6c88b8ada1f3ce344ceb"
)
BASE_COMMIT = "19ec1da534174039105a9ceaa532d13c91d8f09c"
ACTION = "install-fresh-v4-replay-successor-poc"
PRINCIPAL = "operator-via-exclusive-root-parent"

SOURCE_ROLE_SHA256 = {
    "installer-entrypoint": "94b37112fc3b3146078b6edd0cf80d5e845f1cc83543344d79400d144d453dbc",
    "v4-store-schema": "629c6a70936fb94ea4b4a89b4dc3c94095aa2586194c077e4c06258b2c7ce644",
    "stage-n-contract": "d2105c6fbab6edd42ad9724e6ff2313d2531c11af14625bfb0cf8a81b9646fb5",
    "stage-o-runtime-adapter": "f54f051684dd9be4ccf635d3029cb1f099ddb227e8d763efad2c8bf24e3478c4",
    "protected-preflight": "0e09ccc6f995e24ab983489755df6a14028c154a99b84811b95d6ea95bf0946f",
    "atomic-publisher": "c448f4853e6bb9467c6994b64b3f04dfd9ee9c6d0718de69529eb24218e5a719",
    "postflight-verifier": "f276c0bd84a4fe43d5661672600734120af1332c45c372fc6881a2913491ca46",
    "failure-preservation": "8fb37a74e96c7fab7f96fed74ad1aea187fc306716ebb024a1cd0059ca9ded47",
}

HASH_RE = re.compile(r"[0-9a-f]{64}\Z")
OPERATOR_RE = re.compile(r"[A-Za-z0-9_.-]{1,64}\Z")
TIMESTAMP_RE = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z\Z")

AUTHORIZATION_FIELDS = frozenset((
    "schema_version",
    "record_type",
    "action",
    "principal",
    "stage_s_record_sha256",
    "stage_s_package_sha256",
    "base_commit",
    "authorization_hash",
    "authorized_by",
    "authorized_at",
    "authorization_scope",
    "authority",
))

AUTHORITY_FLAGS = frozenset((
    "protected_staging",
    "protected_installation",
))

STAGING_OUTCOME_FIELDS = frozenset((
    "schema_version",
    "record_type",
    "action",
    "principal",
    "authorization_sha256",
    "staged_files",
    "staging_root",
    "outcome",
))

STAGED_FILE_FIELDS = frozenset((
    "role",
    "sha256",
    "destination",
    "bytes",
))


class StagingValidationError(ValueError):
    """Raised when a staging record is invalid."""


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
        allow_nan=False,
    ).encode("ascii")


def authorization_digest(record: dict) -> str:
    """Return the exact digest of the authorization record bytes."""
    return sha256(_canonical(record)).hexdigest()


def check_no_symlink_ancestors(path: Path) -> None:
    """Reject path if any existing non-system component is a symlink.

    macOS system symlinks /var and /tmp are resolved first; only caller-
    controlled path components are checked.
    """
    if not path.is_absolute():
        raise StagingValidationError(f"path must be absolute: {path}")
    current = Path("/")
    for part in path.parts[1:]:
        current = current / part
        # Resolve known macOS system symlinks transparently
        if str(current) == "/var":
            current = Path("/private/var")
            continue
        if str(current) == "/tmp":
            current = Path("/private/tmp")
            continue
        try:
            mode = os.lstat(current).st_mode
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(mode):
            raise StagingValidationError(f"symlink ancestor: {current}")


def build_authorization_template() -> dict:
    """Return a template for the operator to fill and sign."""
    return {
        "schema_version": SCHEMA_VERSION,
        "record_type": "replay-successor-v4-protected-staging-authorization-v1",
        "action": ACTION,
        "principal": PRINCIPAL,
        "stage_s_record_sha256": STAGE_S_RECORD_SHA256,
        "stage_s_package_sha256": STAGE_S_PACKAGE_SHA256,
        "base_commit": BASE_COMMIT,
        "authorization_hash": None,
        "authorized_by": None,
        "authorized_at": None,
        "authorization_scope": {
            "staging_root": "/Library/GRRR/bootstrap",
            "roles": sorted(SOURCE_ROLE_SHA256),
            "source_sha256": dict(SOURCE_ROLE_SHA256),
        },
        "authority": {
            "protected_staging": True,
            "protected_installation": False,
        },
    }


def validate_authorization(value: dict) -> dict:
    """Validate a filled operator authorization record."""
    if not isinstance(value, dict):
        raise StagingValidationError("authorization must be a dict")
    if set(value) != AUTHORIZATION_FIELDS:
        missing = AUTHORIZATION_FIELDS - set(value)
        extra = set(value) - AUTHORIZATION_FIELDS
        raise StagingValidationError(
            f"authorization fields differ: missing={sorted(missing)} extra={sorted(extra)}"
        )
    if type(value["schema_version"]) is not int or value["schema_version"] != SCHEMA_VERSION:
        raise StagingValidationError("schema_version must be integer 1")
    if value["record_type"] != "replay-successor-v4-protected-staging-authorization-v1":
        raise StagingValidationError("record_type differs")
    if value["action"] != ACTION:
        raise StagingValidationError("action differs")
    if value["principal"] != PRINCIPAL:
        raise StagingValidationError("principal differs")
    if value["stage_s_record_sha256"] != STAGE_S_RECORD_SHA256:
        raise StagingValidationError("Stage S record hash differs")
    if value["stage_s_package_sha256"] != STAGE_S_PACKAGE_SHA256:
        raise StagingValidationError("Stage S package hash differs")
    if value["base_commit"] != BASE_COMMIT:
        raise StagingValidationError("base_commit differs")

    auth_hash = value["authorization_hash"]
    if not isinstance(auth_hash, str) or not HASH_RE.match(auth_hash):
        raise StagingValidationError("authorization_hash must be a 64-char hex string")
    if auth_hash == "0" * 64:
        raise StagingValidationError("authorization_hash must not be all zeros")

    authorized_by = value["authorized_by"]
    if not isinstance(authorized_by, str) or not OPERATOR_RE.match(authorized_by):
        raise StagingValidationError("authorized_by must be a valid operator name")

    authorized_at = value["authorized_at"]
    if not isinstance(authorized_at, str) or not TIMESTAMP_RE.match(authorized_at):
        raise StagingValidationError("authorized_at must be an ISO-8601 UTC timestamp")

    scope = value["authorization_scope"]
    if not isinstance(scope, dict) or set(scope) != {"staging_root", "roles", "source_sha256"}:
        raise StagingValidationError("authorization scope fields differ")
    if scope["staging_root"] != "/Library/GRRR/bootstrap":
        raise StagingValidationError("staging_root must be /Library/GRRR/bootstrap")
    if sorted(scope["roles"]) != sorted(SOURCE_ROLE_SHA256):
        raise StagingValidationError("authorization scope roles differ")
    if scope["source_sha256"] != SOURCE_ROLE_SHA256:
        raise StagingValidationError("authorization scope source hashes differ")

    authority = value["authority"]
    if not isinstance(authority, dict) or set(authority) != AUTHORITY_FLAGS:
        raise StagingValidationError("authority fields differ")
    if authority["protected_staging"] is not True:
        raise StagingValidationError("protected_staging must be true in authorization")
    if authority["protected_installation"] is not False:
        raise StagingValidationError(
            "protected_installation must be false (separate gate)"
        )

    return value


def build_staging_outcome(
    authorization: dict,
    staged_files: list,
    staging_root: str,
) -> dict:
    """Build a staging outcome record."""
    auth = validate_authorization(authorization)
    auth_hash = authorization_digest(auth)
    record = {
        "schema_version": SCHEMA_VERSION,
        "record_type": "replay-successor-v4-protected-staging-outcome-v1",
        "action": ACTION,
        "principal": PRINCIPAL,
        "authorization_sha256": auth_hash,
        "staged_files": staged_files,
        "staging_root": staging_root,
        "outcome": "staged-not-installed",
    }
    return validate_staging_outcome(record)


def validate_staging_outcome(value: dict) -> dict:
    """Validate a staging outcome record."""
    if not isinstance(value, dict):
        raise StagingValidationError("outcome must be a dict")
    if set(value) != STAGING_OUTCOME_FIELDS:
        missing = STAGING_OUTCOME_FIELDS - set(value)
        extra = set(value) - STAGING_OUTCOME_FIELDS
        raise StagingValidationError(
            f"outcome fields differ: missing={sorted(missing)} extra={sorted(extra)}"
        )
    if type(value["schema_version"]) is not int or value["schema_version"] != SCHEMA_VERSION:
        raise StagingValidationError("schema_version must be integer 1")
    if value["record_type"] != "replay-successor-v4-protected-staging-outcome-v1":
        raise StagingValidationError("record_type differs")
    if value["action"] != ACTION:
        raise StagingValidationError("action differs")
    if value["principal"] != PRINCIPAL:
        raise StagingValidationError("principal differs")
    auth_hash = value["authorization_sha256"]
    if not isinstance(auth_hash, str) or not HASH_RE.match(auth_hash):
        raise StagingValidationError("authorization_sha256 must be a 64-char hex string")
    if auth_hash == "0" * 64:
        raise StagingValidationError("authorization_sha256 must not be all zeros")

    staged = value["staged_files"]
    if not isinstance(staged, list) or len(staged) != 8:
        raise StagingValidationError("staged_files must have 8 entries")
    seen_roles = set()
    for item in staged:
        if not isinstance(item, dict) or set(item) != STAGED_FILE_FIELDS:
            raise StagingValidationError("staged file fields differ")
        role = item["role"]
        if role in seen_roles:
            raise StagingValidationError(f"duplicate role: {role}")
        seen_roles.add(role)
        if role not in SOURCE_ROLE_SHA256:
            raise StagingValidationError(f"unknown role: {role}")
        if item["sha256"] != SOURCE_ROLE_SHA256[role]:
            raise StagingValidationError(f"source hash differs for {role}")
        if type(item["bytes"]) is not int or item["bytes"] <= 0:
            raise StagingValidationError(f"bytes must be positive for {role}")
        if not isinstance(item["destination"], str):
            raise StagingValidationError(f"destination must be str for {role}")
        # Normalize and require exact containment without filesystem access
        normalized = posixpath.normpath(item["destination"])
        if normalized != item["destination"]:
            raise StagingValidationError(
                f"destination must be already-normalized for {role}"
            )
        expected_prefix = value["staging_root"] + "/"
        if not item["destination"].startswith(expected_prefix):
            raise StagingValidationError(
                f"destination must be under {value['staging_root']} for {role}"
            )
        # Reject traversal components
        remaining = item["destination"][len(expected_prefix):]
        if not remaining or "/" in remaining or remaining in (".", ".."):
            raise StagingValidationError(
                f"destination must be a direct file under staging root for {role}"
            )
    if seen_roles != set(SOURCE_ROLE_SHA256):
        raise StagingValidationError("staged files roles incomplete")

    if value["staging_root"] != "/Library/GRRR/bootstrap":
        raise StagingValidationError("staging_root must be /Library/GRRR/bootstrap")
    if value["outcome"] != "staged-not-installed":
        raise StagingValidationError("outcome must be staged-not-installed")

    return value
