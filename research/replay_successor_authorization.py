"""Build the repository-only v4 operator-authorization preparation record.

This module reads only the independently approved Stage R source bundle and
existing Stage P/N constants.  It does not access or mutate
``/Library/GRRR``, stage protected records, install anything, amend a budget,
reconcile history, execute replay, admit, promote, merge, or push.
"""

from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Dict


SCHEMA_VERSION = 1
STAGE_R_SOURCE_BUNDLE_SHA256 = (
    "b6354127a7552b628506c25dc7eee27c8ecb371f56bf565a63dd247b31445084"
)
STAGE_R_SOURCE_BUNDLE_FILE_SHA256 = (
    "31cb9b8ee538ac22553927fe5f8006c47461073578f9d025f3ddb892ed3ca84c"
)
STAGE_R_PACKAGE_SHA256 = (
    "c1b70a4fc1279e48c25a6004d93bc6b6055981524c1f5acd0ff9885fe28a5a9c"
)
STAGE_R_REVIEW_SHA256 = "e84d5abc30aea4d1e7885f5ebe8df3217d7c35d206b0fa3c5d5b95b986f1cf61"
BASE_COMMIT = "b43f1fa483c8a281246f425d6c5b66606d867bff"
PREPARED_AT = "2026-11-03T15:00:00Z"

PREDECESSOR_ACTIVE_SHA256 = (
    "9c5194dd12ff7601917fcccc293c459db09a41da8bad9fa9983cbef618d453f8"
)
PREDECESSOR_DATABASE_SHA256 = (
    "9c6ff2561a364ed982cd5477dd4b200c995da6910c9a17aa3d3c411a962d64f3"
)
PREDECESSOR_RECOVERY_SHA256 = (
    "6d3d5b092c0ee8273a657c83823d8465b215f2b1b66ec627dfde2d96b21fe587"
)

STAGING_ROOT = "/Library/GRRR/bootstrap"
INSTALL_TARGET = (
    "/Library/GRRR/accounting-poc2/unissued-independent-replay-v4"
)
ACTION = "install-fresh-v4-replay-successor-poc"
PRINCIPAL = "operator-via-exclusive-root-parent"

ROLE_DESTINATIONS = {
    "installer-entrypoint": STAGING_ROOT + "/install-replay-successor-v4",
    "v4-store-schema": STAGING_ROOT + "/replay-successor-v4-v4_store_schema.py",
    "stage-n-contract": STAGING_ROOT + "/replay-successor-v4-stage_n_contract.py",
    "stage-o-runtime-adapter": STAGING_ROOT + "/replay-successor-v4-stage_o_runtime_adapter.py",
    "protected-preflight": STAGING_ROOT + "/replay-successor-v4-protected_preflight.py",
    "atomic-publisher": STAGING_ROOT + "/replay-successor-v4-atomic_publisher.py",
    "postflight-verifier": STAGING_ROOT + "/replay-successor-v4-postflight_verifier.py",
    "failure-preservation": STAGING_ROOT + "/replay-successor-v4-failure_preservation.py",
}

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

REQUIRED_FIELDS = frozenset((
    "schema_version",
    "record_type",
    "action",
    "principal",
    "status",
    "basis",
    "staging_plan",
    "installation_target",
    "predecessor_binding",
    "operator_authorization_requirement",
    "denied_authorities",
    "authority",
    "prepared_at",
))

DENIED_AUTHORITIES = frozenset((
    "budget_amendment",
    "reconciliation",
    "replay_execution",
    "admission",
    "promotion",
    "merge",
    "push",
    "production_mutation",
))

BASIS_FIELDS = frozenset((
    "base_commit",
    "stage_r_source_bundle_sha256",
    "stage_r_package_sha256",
    "stage_r_review_sha256",
))
STAGING_ITEM_FIELDS = frozenset((
    "role",
    "source_sha256",
    "protected_destination",
    "operation",
    "verification",
))
PREDECESSOR_FIELDS = frozenset((
    "active_sha256",
    "database_sha256",
    "recovery_sha256",
    "predecessor_mutation",
))
AUTH_REQ_FIELDS = frozenset((
    "authorization_type",
    "authorization_hash",
    "authorized_by",
    "authorized_at",
    "required_before",
    "record_immutable_after",
))
AUTHORITY_FIELDS = frozenset((
    "protected_staging",
    "protected_installation",
    "budget_amendment",
    "reconciliation",
    "replay_execution",
    "admission",
    "promotion",
    "merge",
    "push",
    "production_mutation",
))


class AuthorizationPreparationError(ValueError):
    """Raised when the authorization preparation record is invalid."""


def _sha256_file(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
        allow_nan=False,
    ).encode("ascii")


def _digest(value: Any) -> str:
    return sha256(_canonical(value)).hexdigest()


def build_staging_plan() -> list:
    """Return the exact eight-role staging plan."""
    plan = []
    for role in sorted(ROLE_DESTINATIONS):
        plan.append({
            "role": role,
            "source_sha256": SOURCE_ROLE_SHA256[role],
            "protected_destination": ROLE_DESTINATIONS[role],
            "operation": "copy-verify",
            "verification": "sha256",
        })
    return plan


def build_record() -> dict:
    """Build the authorization preparation record."""
    staging_plan = build_staging_plan()
    plan_digest = _digest(staging_plan)
    return {
        "schema_version": SCHEMA_VERSION,
        "record_type": "replay-successor-v4-authorization-prepared-v1",
        "action": ACTION,
        "principal": PRINCIPAL,
        "status": "prepared-not-authorized",
        "basis": {
            "base_commit": BASE_COMMIT,
            "stage_r_source_bundle_sha256": STAGE_R_SOURCE_BUNDLE_SHA256,
            "stage_r_package_sha256": STAGE_R_PACKAGE_SHA256,
            "stage_r_review_sha256": STAGE_R_REVIEW_SHA256,
        },
        "staging_plan": staging_plan,
        "staging_plan_sha256": plan_digest,
        "installation_target": INSTALL_TARGET,
        "predecessor_binding": {
            "active_sha256": PREDECESSOR_ACTIVE_SHA256,
            "database_sha256": PREDECESSOR_DATABASE_SHA256,
            "recovery_sha256": PREDECESSOR_RECOVERY_SHA256,
            "predecessor_mutation": "forbidden",
        },
        "operator_authorization_requirement": {
            "authorization_type": "explicit-human-approval",
            "authorization_hash": None,
            "authorized_by": None,
            "authorized_at": None,
            "required_before": "protected-staging",
            "record_immutable_after": True,
        },
        "denied_authorities": sorted(DENIED_AUTHORITIES),
        "authority": {
            "protected_staging": False,
            "protected_installation": False,
            "budget_amendment": False,
            "reconciliation": False,
            "replay_execution": False,
            "admission": False,
            "promotion": False,
            "merge": False,
            "push": False,
            "production_mutation": False,
        },
        "prepared_at": PREPARED_AT,
    }


def validate_record(value: dict) -> dict:
    """Validate the authorization preparation record."""
    if not isinstance(value, dict):
        raise AuthorizationPreparationError("record must be a dict")
    expected = REQUIRED_FIELDS | {"staging_plan_sha256"}
    if set(value) != expected:
        missing = expected - set(value)
        extra = set(value) - expected
        raise AuthorizationPreparationError(
            f"record fields differ: missing={sorted(missing)} extra={sorted(extra)}"
        )
    if type(value["schema_version"]) is not int or value["schema_version"] != SCHEMA_VERSION:
        raise AuthorizationPreparationError("schema_version must be integer 1")
    if value["record_type"] != "replay-successor-v4-authorization-prepared-v1":
        raise AuthorizationPreparationError("record_type differs")
    if value["action"] != ACTION:
        raise AuthorizationPreparationError("action differs")
    if value["principal"] != PRINCIPAL:
        raise AuthorizationPreparationError("principal differs")
    if value["status"] != "prepared-not-authorized":
        raise AuthorizationPreparationError("status must be prepared-not-authorized")

    basis = value["basis"]
    if not isinstance(basis, dict):
        raise AuthorizationPreparationError("basis must be dict")
    if set(basis) != BASIS_FIELDS:
        missing = BASIS_FIELDS - set(basis)
        extra = set(basis) - BASIS_FIELDS
        raise AuthorizationPreparationError(
            f"basis fields differ: missing={sorted(missing)} extra={sorted(extra)}"
        )
    if basis["base_commit"] != BASE_COMMIT:
        raise AuthorizationPreparationError("base_commit differs")
    if basis.get("stage_r_source_bundle_sha256") != STAGE_R_SOURCE_BUNDLE_SHA256:
        raise AuthorizationPreparationError("Stage R source bundle hash differs")
    if basis.get("stage_r_package_sha256") != STAGE_R_PACKAGE_SHA256:
        raise AuthorizationPreparationError("Stage R package hash differs")
    if basis.get("stage_r_review_sha256") != STAGE_R_REVIEW_SHA256:
        raise AuthorizationPreparationError("Stage R review hash differs")

    plan = value["staging_plan"]
    if not isinstance(plan, list) or len(plan) != 8:
        raise AuthorizationPreparationError("staging plan must have 8 entries")
    seen_roles = set()
    for item in plan:
        if not isinstance(item, dict):
            raise AuthorizationPreparationError("staging item must be dict")
        if set(item) != STAGING_ITEM_FIELDS:
            missing = STAGING_ITEM_FIELDS - set(item)
            extra = set(item) - STAGING_ITEM_FIELDS
            raise AuthorizationPreparationError(
                f"staging item fields differ for {item.get('role', '?')}: "
                f"missing={sorted(missing)} extra={sorted(extra)}"
            )
        role = item.get("role")
        if role in seen_roles:
            raise AuthorizationPreparationError(f"duplicate role: {role}")
        seen_roles.add(role)
        if role not in SOURCE_ROLE_SHA256:
            raise AuthorizationPreparationError(f"unknown role: {role}")
        if item.get("source_sha256") != SOURCE_ROLE_SHA256[role]:
            raise AuthorizationPreparationError(f"source hash differs for {role}")
        if item.get("protected_destination") != ROLE_DESTINATIONS[role]:
            raise AuthorizationPreparationError(f"destination differs for {role}")
        if item.get("operation") != "copy-verify":
            raise AuthorizationPreparationError(f"operation differs for {role}")
        if item.get("verification") != "sha256":
            raise AuthorizationPreparationError(f"verification differs for {role}")
    if seen_roles != set(SOURCE_ROLE_SHA256):
        raise AuthorizationPreparationError("staging plan roles incomplete")

    plan_digest = _digest(plan)
    if value["staging_plan_sha256"] != plan_digest:
        raise AuthorizationPreparationError("staging plan digest differs")

    if value["installation_target"] != INSTALL_TARGET:
        raise AuthorizationPreparationError("installation target differs")

    pred = value["predecessor_binding"]
    if not isinstance(pred, dict):
        raise AuthorizationPreparationError("predecessor binding must be dict")
    if set(pred) != PREDECESSOR_FIELDS:
        missing = PREDECESSOR_FIELDS - set(pred)
        extra = set(pred) - PREDECESSOR_FIELDS
        raise AuthorizationPreparationError(
            f"predecessor fields differ: missing={sorted(missing)} extra={sorted(extra)}"
        )
    if pred.get("active_sha256") != PREDECESSOR_ACTIVE_SHA256:
        raise AuthorizationPreparationError("predecessor active hash differs")
    if pred.get("database_sha256") != PREDECESSOR_DATABASE_SHA256:
        raise AuthorizationPreparationError("predecessor database hash differs")
    if pred.get("recovery_sha256") != PREDECESSOR_RECOVERY_SHA256:
        raise AuthorizationPreparationError("predecessor recovery hash differs")
    if pred.get("predecessor_mutation") != "forbidden":
        raise AuthorizationPreparationError("predecessor mutation must be forbidden")

    auth_req = value["operator_authorization_requirement"]
    if not isinstance(auth_req, dict):
        raise AuthorizationPreparationError("authorization requirement must be dict")
    if set(auth_req) != AUTH_REQ_FIELDS:
        missing = AUTH_REQ_FIELDS - set(auth_req)
        extra = set(auth_req) - AUTH_REQ_FIELDS
        raise AuthorizationPreparationError(
            f"authorization requirement fields differ: "
            f"missing={sorted(missing)} extra={sorted(extra)}"
        )
    if auth_req.get("authorization_type") != "explicit-human-approval":
        raise AuthorizationPreparationError("authorization type differs")
    if auth_req.get("authorization_hash") is not None:
        raise AuthorizationPreparationError("authorization hash must be null (not yet authorized)")
    if auth_req.get("authorized_by") is not None:
        raise AuthorizationPreparationError("authorized_by must be null")
    if auth_req.get("authorized_at") is not None:
        raise AuthorizationPreparationError("authorized_at must be null")
    if auth_req.get("required_before") != "protected-staging":
        raise AuthorizationPreparationError("required_before differs")
    if auth_req.get("record_immutable_after") is not True:
        raise AuthorizationPreparationError("record_immutable_after must be true")

    denied = value["denied_authorities"]
    if not isinstance(denied, list) or sorted(denied) != sorted(DENIED_AUTHORITIES):
        raise AuthorizationPreparationError("denied authorities differ")

    authority = value["authority"]
    if not isinstance(authority, dict):
        raise AuthorizationPreparationError("authority must be dict")
    if set(authority) != AUTHORITY_FIELDS:
        missing = AUTHORITY_FIELDS - set(authority)
        extra = set(authority) - AUTHORITY_FIELDS
        raise AuthorizationPreparationError(
            f"authority fields differ: missing={sorted(missing)} extra={sorted(extra)}"
        )
    for key, flag in authority.items():
        if flag is not False:
            raise AuthorizationPreparationError(f"authority {key} must be false")

    if value["prepared_at"] != PREPARED_AT:
        raise AuthorizationPreparationError("prepared_at differs")

    return value


def emit_record(repository_root: Path) -> dict:
    """Build, validate, and return the authorization preparation record."""
    source_bundle_path = (
        repository_root
        / "docs/evidence/replay-authority/stage-r/SOURCE-BUNDLE.json"
    )
    if not source_bundle_path.is_file():
        raise AuthorizationPreparationError("Stage R SOURCE-BUNDLE.json missing")
    actual = _sha256_file(source_bundle_path)
    if actual != STAGE_R_SOURCE_BUNDLE_FILE_SHA256:
        raise AuthorizationPreparationError(
            f"Stage R source bundle hash mismatch: {actual}"
        )

    package_path = (
        repository_root
        / "docs/evidence/replay-authority/stage-r/PACKAGE.json"
    )
    if not package_path.is_file():
        raise AuthorizationPreparationError("Stage R PACKAGE.json missing")
    actual_package = _sha256_file(package_path)
    if actual_package != STAGE_R_PACKAGE_SHA256:
        raise AuthorizationPreparationError(
            f"Stage R package hash mismatch: {actual_package}"
        )

    review_path = (
        repository_root
        / "docs/evidence/replay-authority/stage-r/ABSENT-LEAF-REVIEW-APPROVED.md"
    )
    if not review_path.is_file():
        raise AuthorizationPreparationError("Stage R review approval missing")
    actual_review = _sha256_file(review_path)
    if actual_review != STAGE_R_REVIEW_SHA256:
        raise AuthorizationPreparationError(
            f"Stage R review hash mismatch: {actual_review}"
        )

    record = build_record()
    return validate_record(record)
