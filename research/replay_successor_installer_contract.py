"""Design-only contract for a future v4 replay-successor installer.

No function here reads a file, executes a process, opens SQLite, or touches a
protected path.  The contract deliberately leaves installer, plan, review, and
authorization bytes unissued; it cannot authenticate or install anything.
"""

import re
from typing import Any, Dict

from spendability_stage_c import AUTHORITY_FIELDS, StageCError, digest


CONTRACT_VERSION = 1
HASH_RE = re.compile(r"[0-9a-f]{64}\Z")
NO_AUTHORITY = {name: False for name in sorted(AUTHORITY_FIELDS)}

BASE_COMMIT = "2051e7dd5378db6ed4c2057dd50aa3287bfe3525"
STAGE_N_PACKAGE_SHA256 = "e349cc8349f62072af94f8b82ee1aafa1648db22270a77b9dba278469d305a48"
STAGE_O_PACKAGE_SHA256 = "283918e2c1df4b9b25b79a26be90de9e5d20ea8c195b058a5b827c474872553b"
PREDECESSOR_ACTIVE_SHA256 = "9c5194dd12ff7601917fcccc293c459db09a41da8bad9fa9983cbef618d453f8"
PREDECESSOR_DATABASE_SHA256 = "9c6ff2561a364ed982cd5477dd4b200c995da6910c9a17aa3d3c411a962d64f3"
PREDECESSOR_RECOVERY_SHA256 = "6d3d5b092c0ee8273a657c83823d8465b215f2b1b66ec627dfde2d96b21fe587"
CANONICAL_PYTHON_SHA256 = "5c5950c62eee5fd227a67e4bdfcde81c9add59799bba0949635f3d5ba9661c26"
INSTALLER_ENTRYPOINT = "/Library/GRRR/bootstrap/install-replay-successor-v4"
TARGET_STORE_ID = "unissued-independent-replay-v4"
TARGET_DIRECTORY = "/Library/GRRR/accounting-poc2/unissued-independent-replay-v4"
INSTALLER_ACTION = "install-fresh-v4-replay-successor-poc"
OPERATOR_PRINCIPAL = "operator-via-exclusive-root-parent"
FAILURE_MODE = "refuse-no-retry-preserve-partial-evidence"
ROLLBACK_SCOPE = "new-successor-namespace-only"

SOURCE_ROLES = (
    "installer-entrypoint",
    "v4-store-schema",
    "stage-n-contract",
    "stage-o-runtime-adapter",
    "protected-preflight",
    "atomic-publisher",
    "postflight-verifier",
    "failure-preservation",
)
SOURCE_ARTIFACTS = {role: "/Library/GRRR/bootstrap/replay-successor-v4-"
                        + role.replace("-", "_") + ".py"
                        for role in SOURCE_ROLES if role != "installer-entrypoint"}
SOURCE_ARTIFACTS["installer-entrypoint"] = INSTALLER_ENTRYPOINT
INSTALLER_FIELDS = frozenset((
    "entrypoint", "target_store_id", "target_directory", "source_roles",
    "source_artifacts", "source_sha256", "interpreter_sha256", "plan_sha256", "review_sha256",
    "authorization_sha256", "issuance_status", "exclusive_parent",
    "install_once", "predecessor_read_only", "predecessor_mutations",
    "failure_mode", "rollback_scope", "protected_access",
))
AUTHORIZATION_FIELDS = frozenset((
    "action", "principal", "plan_sha256", "review_sha256",
    "record_sha256_policy", "budget_amendment_required",
    "budget_amendment_authorized", "reconciliation_authorized",
    "replay_authorized", "execution_authorized", "admission", "promotion",
    "automatic_merge", "push",
))
CONTRACT_FIELDS = frozenset((
    "schema_version", "record_type", "decision", "basis", "installer",
    "authorization", "gates", "outcome", "authority",
))
ISSUED_AUTHORIZATION_FIELDS = frozenset((
    "schema_version", "record_type", "action", "principal", "basis",
    "installer_sha256", "plan_sha256", "review_sha256",
    "protected_installation_requested", "exclusive_parent",
    "budget_amendment_required", "budget_amendment_authorized",
    "reconciliation_authorized", "replay_authorized",
    "execution_authorized", "admission", "promotion", "automatic_merge", "push",
))


def _require(condition: bool, detail: str) -> None:
    if not condition:
        raise StageCError("replay_successor_installer_contract", detail)


def _exact(value: Any, expected: frozenset, label: str) -> Dict[str, Any]:
    _require(isinstance(value, dict) and set(value) == set(expected),
             label + " fields differ")
    return value


def _hash(value: Any, label: str) -> str:
    _require(type(value) is str and HASH_RE.fullmatch(value) is not None,
             label + " must be a lowercase SHA-256")
    return value


def _null(value: Any, label: str) -> None:
    _require(value is None, label + " must remain unissued in the design contract")


def _basis() -> Dict[str, Any]:
    return {
        "story_head": BASE_COMMIT,
        "stage_n_package_sha256": STAGE_N_PACKAGE_SHA256,
        "stage_o_package_sha256": STAGE_O_PACKAGE_SHA256,
        "predecessor_active_sha256": PREDECESSOR_ACTIVE_SHA256,
        "predecessor_database_sha256": PREDECESSOR_DATABASE_SHA256,
        "predecessor_recovery_sha256": PREDECESSOR_RECOVERY_SHA256,
    }


def candidate_installer_contract() -> Dict[str, Any]:
    """Return the sole unissued design candidate; this is not authority."""
    return {
        "schema_version": CONTRACT_VERSION,
        "record_type": "replay-successor-v4-installer-contract-v1",
        "decision": "candidate-installer-contract-not-issued",
        "basis": _basis(),
        "installer": {
            "entrypoint": INSTALLER_ENTRYPOINT,
            "target_store_id": TARGET_STORE_ID,
            "target_directory": TARGET_DIRECTORY,
            "source_roles": list(SOURCE_ROLES),
            "source_artifacts": dict(SOURCE_ARTIFACTS),
            "source_sha256": {role: None for role in SOURCE_ROLES},
            "interpreter_sha256": CANONICAL_PYTHON_SHA256,
            "plan_sha256": None,
            "review_sha256": None,
            "authorization_sha256": None,
            "issuance_status": "unissued",
            "exclusive_parent": True,
            "install_once": True,
            "predecessor_read_only": True,
            "predecessor_mutations": [],
            "failure_mode": FAILURE_MODE,
            "rollback_scope": ROLLBACK_SCOPE,
            "protected_access": "design-only-no-access",
        },
        "authorization": {
            "action": INSTALLER_ACTION,
            "principal": OPERATOR_PRINCIPAL,
            "plan_sha256": None,
            "review_sha256": None,
            "record_sha256_policy": "external-exact-hash-required-at-install",
            "budget_amendment_required": True,
            "budget_amendment_authorized": False,
            "reconciliation_authorized": False,
            "replay_authorized": False,
            "execution_authorized": False,
            "admission": "blocked",
            "promotion": "disabled",
            "automatic_merge": False,
            "push": False,
        },
        "gates": {
            "installer_source_built": {"status": "not-run", "evidence": []},
            "independent_security_review": {"status": "not-run", "evidence": []},
            "exact_plan_issued": {"status": "not-run", "evidence": []},
            "operator_authorization_issued": {"status": "not-run", "evidence": []},
            "protected_staging": {"status": "not-run", "evidence": []},
            "installation": {"status": "not-run", "evidence": []},
            "postflight": {"status": "not-run", "evidence": []},
        },
        "outcome": {
            "contract_valid": True,
            "design_only": True,
            "installer_issued": False,
            "authorization_issued": False,
            "installation_ready": False,
            "protected_access_performed": False,
            "allowed_mutations": [],
            "spendable": None,
        },
        "authority": dict(NO_AUTHORITY),
    }


def validate_installer_contract(value: Any) -> Dict[str, Any]:
    record = _exact(value, CONTRACT_FIELDS, "installer contract")
    _require(type(record["schema_version"]) is int
             and record["schema_version"] == CONTRACT_VERSION,
             "installer contract version differs")
    _require(record["record_type"] == "replay-successor-v4-installer-contract-v1",
             "installer contract record type differs")
    _require(record["decision"] == "candidate-installer-contract-not-issued",
             "installer contract cannot claim issuance")
    _require(digest(record["basis"]) == digest(_basis()),
             "installer contract basis differs")

    installer = _exact(record["installer"], INSTALLER_FIELDS, "installer")
    _require(installer["entrypoint"] == INSTALLER_ENTRYPOINT,
             "future installer entrypoint differs")
    _require(installer["target_store_id"] == TARGET_STORE_ID,
             "future target store differs")
    _require(installer["target_directory"] == TARGET_DIRECTORY,
             "future target directory differs")
    _require(tuple(installer["source_roles"]) == SOURCE_ROLES,
             "future source-role closure differs")
    _require(digest(installer["source_artifacts"]) == digest(SOURCE_ARTIFACTS),
             "future source artifact paths differ")
    _require(set(installer["source_sha256"]) == set(SOURCE_ROLES),
             "future source digest roles differ")
    for role in SOURCE_ROLES:
        _null(installer["source_sha256"][role], "source " + role)
    _require(installer["interpreter_sha256"] == CANONICAL_PYTHON_SHA256,
             "canonical interpreter identity differs")
    for name in ("plan_sha256", "review_sha256", "authorization_sha256"):
        _null(installer[name], "installer " + name)
    _require(installer["issuance_status"] == "unissued",
             "installer issuance status differs")
    _require(installer["exclusive_parent"] is True
             and installer["install_once"] is True
             and installer["predecessor_read_only"] is True,
             "installer safety flags differ")
    _require(installer["predecessor_mutations"] == [],
             "installer cannot mutate the predecessor")
    _require(installer["failure_mode"] == FAILURE_MODE,
             "installer failure mode differs")
    _require(installer["rollback_scope"] == ROLLBACK_SCOPE,
             "installer rollback scope differs")
    _require(installer["protected_access"] == "design-only-no-access",
             "design contract cannot claim protected access")

    authorization = _exact(record["authorization"], AUTHORIZATION_FIELDS,
                           "installer authorization")
    _require(authorization["action"] == INSTALLER_ACTION,
             "future operator action differs")
    _require(authorization["principal"] == OPERATOR_PRINCIPAL,
             "future operator principal differs")
    for name in ("plan_sha256", "review_sha256"):
        _null(authorization[name], "authorization " + name)
    _require(authorization["record_sha256_policy"]
             == "external-exact-hash-required-at-install",
             "authorization hash policy differs")
    _require(authorization["budget_amendment_required"] is True,
             "fresh successor charge requires a separate amendment")
    _require(authorization["budget_amendment_authorized"] is False,
             "installer authorization cannot amend the budget")
    _require(authorization["reconciliation_authorized"] is False,
             "installer authorization cannot reconcile history")
    _require(authorization["replay_authorized"] is False,
             "installer authorization cannot dispatch replay")
    _require(authorization["execution_authorized"] is False,
             "installer authorization cannot execute work")
    _require(authorization["admission"] == "blocked"
             and authorization["promotion"] == "disabled"
             and authorization["automatic_merge"] is False
             and authorization["push"] is False,
             "installer decision guards differ")

    expected_gates = candidate_installer_contract()["gates"]
    _require(digest(record["gates"]) == digest(expected_gates),
             "installer gate inventory differs")
    expected_outcome = candidate_installer_contract()["outcome"]
    _require(digest(record["outcome"]) == digest(expected_outcome),
             "installer outcome differs")
    _require(digest(record["authority"]) == digest(NO_AUTHORITY),
             "installer contract cannot grant authority")
    _require(digest(record) == digest(candidate_installer_contract()),
             "installer contract differs from exact regeneration")
    return record


def candidate_authorization_requirement() -> Dict[str, Any]:
    """Describe the future operator record without issuing or trusting one."""
    return {
        "schema_version": CONTRACT_VERSION,
        "record_type": "replay-successor-v4-authorization-requirement-v1",
        "action": INSTALLER_ACTION,
        "principal": OPERATOR_PRINCIPAL,
        "basis": _basis(),
        "distinct_receipts_required": (
            "installer_sha256", "plan_sha256", "review_sha256",
        ),
        "external_authorization_sha256_required": True,
        "protected_installation_requested": True,
        "must_preserve_predecessor": True,
        "budget_amendment_required": True,
        "budget_amendment_authorized": False,
        "reconciliation_authorized": False,
        "replay_authorized": False,
        "execution_authorized": False,
        "authority": dict(NO_AUTHORITY),
    }


def validate_issued_authorization_shape(value: Any) -> Dict[str, Any]:
    """Validate a synthetic future record's shape; authenticate nothing."""
    record = _exact(value, ISSUED_AUTHORIZATION_FIELDS,
                    "issued installer authorization")
    _require(type(record["schema_version"]) is int
             and record["schema_version"] == CONTRACT_VERSION,
             "issued authorization version differs")
    _require(record["record_type"] == "replay-successor-v4-authorization-v1",
             "issued authorization record type differs")
    _require(record["action"] == INSTALLER_ACTION,
             "issued authorization action differs")
    _require(record["principal"] == OPERATOR_PRINCIPAL,
             "issued authorization principal differs")
    _require(digest(record["basis"]) == digest(_basis()),
             "issued authorization basis differs")
    hashes = []
    for name in ("installer_sha256", "plan_sha256", "review_sha256"):
        hashes.append(_hash(record[name], "issued authorization " + name))
    _require(len(set(hashes)) == len(hashes),
             "issued authorization receipts are not distinct")
    _require(record["protected_installation_requested"] is True,
             "issued authorization must request protected installation explicitly")
    _require(record["exclusive_parent"] is True,
             "issued authorization requires exclusive parent control")
    _require(record["budget_amendment_required"] is True,
             "fresh successor charge still requires an amendment")
    _require(record["budget_amendment_authorized"] is False,
             "install authorization cannot amend the budget")
    _require(record["reconciliation_authorized"] is False,
             "install authorization cannot reconcile history")
    _require(record["replay_authorized"] is False,
             "install authorization cannot dispatch replay")
    _require(record["execution_authorized"] is False,
             "install authorization cannot execute work")
    _require(record["admission"] == "blocked"
             and record["promotion"] == "disabled"
             and record["automatic_merge"] is False
             and record["push"] is False,
             "issued authorization decision guards differ")
    return {
        "authorization_shape_valid": True,
        "authenticated": False,
        "installation_authorized": False,
        "authority": dict(NO_AUTHORITY),
        "reason": "exact protected bytes, reviewer decision, operator identity, and live state remain unverified",
    }


def contract_summary() -> Dict[str, Any]:
    contract = candidate_installer_contract()
    return {
        "schema_version": CONTRACT_VERSION,
        "record_type": contract["record_type"],
        "decision": contract["decision"],
        "basis": _basis(),
        "source_roles": list(SOURCE_ROLES),
        "interpreter_sha256": CANONICAL_PYTHON_SHA256,
        "future_action": INSTALLER_ACTION,
        "future_principal": OPERATOR_PRINCIPAL,
        "unissued_receipts": [
            "source_sha256", "plan_sha256", "review_sha256",
            "authorization_sha256",
        ],
        "budget_amendment_required": True,
        "budget_amendment_authorized": False,
        "reconciliation_authorized": False,
        "replay_authorized": False,
        "execution_authorized": False,
        "authority": dict(NO_AUTHORITY),
        "implementation_status": "design-only",
    }
