"""Sandboxed core for a future stopped v4 replay-successor installer.

The functions here operate only on caller-supplied sandbox paths.  They never
open `/Library/GRRR`, authenticate an operator, issue protected receipts, or
release a budget.  The checkout CLI refuses every live installation attempt.
"""

from hashlib import sha256
import json
import os
from pathlib import Path
import sqlite3
import stat
from contextlib import closing
from typing import Any, Dict, Mapping

from replay_successor_contract import (
    PREDECESSOR_RECOVERY_RECEIPT, PREDECESSOR_STORE_ID,
    SUCCESSOR_CAMPAIGN, SUCCESSOR_STORE_ID, candidate_receipt,
)
from replay_successor_installer_contract import (
    BASE_COMMIT, CANONICAL_PYTHON_SHA256, INSTALLER_ACTION,
    INSTALLER_ENTRYPOINT, OPERATOR_PRINCIPAL, SOURCE_ARTIFACTS, SOURCE_ROLES,
    PREDECESSOR_ACTIVE_SHA256, PREDECESSOR_DATABASE_SHA256,
    PREDECESSOR_RECOVERY_SHA256, STAGE_N_PACKAGE_SHA256,
    STAGE_O_PACKAGE_SHA256, TARGET_DIRECTORY,
    validate_issued_authorization_shape,
)
from spendability_stage_c import StageCError, digest


SCHEMA_VERSION = 1
PYTHON_ENTRYPOINT = (
    "/Library/Developer/CommandLineTools/Library/Frameworks/"
    "Python3.framework/Versions/3.9/bin/python3.9"
)
PROFILE = "independent-replay"
LIBRARY_ROOT = Path("/Library")
PROTECTED_ROOT = Path("/Library/GRRR")
SOURCE_FIELDS = frozenset(SOURCE_ROLES)
PLAN_FIELDS = frozenset((
    "schema_version", "record_type", "action", "basis", "source_inventory",
    "installer_sha256", "interpreter_sha256", "target_directory",
    "budget_amendment_required", "budget_amendment_authorized",
    "execution_authorized", "exclusive_parent", "install_once",
    "predecessor_read_only", "predecessor_mutations", "failure_mode",
    "rollback_scope", "sandbox_only",
))
REVIEW_FIELDS = frozenset((
    "schema_version", "record_type", "decision", "plan_sha256",
    "source_inventory", "basis", "sandbox_only", "execution_authorized",
    "budget_amendment_authorized", "reconciliation_authorized",
    "replay_authorized",
))
AUTHORIZATION_FIELDS = frozenset((
    "schema_version", "record_type", "action", "principal", "basis",
    "installer_sha256", "plan_sha256", "review_sha256",
    "protected_installation_requested", "exclusive_parent",
    "budget_amendment_required", "budget_amendment_authorized",
    "reconciliation_authorized", "replay_authorized",
    "execution_authorized", "admission", "promotion", "automatic_merge", "push",
))
IDENTITY_FIELDS = frozenset((
    "uid", "euid", "interpreter", "entrypoint", "isolated", "no_site",
    "no_bytecode",
))
BASIS = {
    "story_head": BASE_COMMIT,
    "stage_n_package_sha256": STAGE_N_PACKAGE_SHA256,
    "stage_o_package_sha256": STAGE_O_PACKAGE_SHA256,
    "predecessor_active_sha256": PREDECESSOR_ACTIVE_SHA256,
    "predecessor_database_sha256": PREDECESSOR_DATABASE_SHA256,
    "predecessor_recovery_sha256": PREDECESSOR_RECOVERY_SHA256,
}
RECEIPT_FIELDS = frozenset((
    "schema_version", "record_type", "outcome", "plan_sha256",
    "review_sha256", "authorization_sha256", "binding_sha256",
    "database_sha256", "stopped", "sandbox_only", "execution_authorized",
    "budget_amendment_authorized", "reconciliation_authorized",
    "replay_authorized", "allowed_mutations",
))
BINDING_FIELDS = frozenset((
    "version", "campaign", "store_id", "directory",
    "prior_history_receipt", "profiles", "device", "inode",
    "successor_sha256", "predecessor_store_id",
    "predecessor_binding_sha256", "allowed_mutation_profiles",
    "execution_authorized", "budget_amendment_required", "sandbox_only",
))


def _require(condition: bool, detail: str) -> None:
    if not condition:
        raise StageCError("replay_successor_installer", detail)


def _exact(value: Any, expected: frozenset, label: str) -> Dict[str, Any]:
    _require(isinstance(value, dict) and set(value) == set(expected),
             label + " fields differ")
    return value


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("ascii")


def _sha(raw: bytes) -> str:
    return sha256(raw).hexdigest()


def _hashed(value: Any, label: str) -> str:
    _require(type(value) is str and len(value) == 64
             and all(character in "0123456789abcdef" for character in value),
             label + " must be a lowercase SHA-256")
    return value


def source_inventory(raw_files: Mapping[str, bytes]) -> Dict[str, str]:
    """Hash the exact eight-role sandbox source closure."""
    _require(set(raw_files) == set(SOURCE_ROLES), "sandbox source roles differ")
    return {role: _sha(raw_files[role]) for role in SOURCE_ROLES}


def validate_source_inventory(value: Any) -> Dict[str, str]:
    record = _exact(value, SOURCE_FIELDS, "source inventory")
    hashes = [_hashed(record[role], "source " + role) for role in SOURCE_ROLES]
    _require(len(set(hashes)) == len(hashes),
             "sandbox source hashes are not distinct")
    return record


def candidate_plan(inventory: Mapping[str, str]) -> Dict[str, Any]:
    validate_source_inventory(inventory)
    return {
        "schema_version": SCHEMA_VERSION,
        "record_type": "replay-successor-v4-installer-plan-v1",
        "action": INSTALLER_ACTION,
        "basis": dict(BASIS),
        "source_inventory": dict(inventory),
        "installer_sha256": inventory["installer-entrypoint"],
        "interpreter_sha256": CANONICAL_PYTHON_SHA256,
        "target_directory": TARGET_DIRECTORY,
        "budget_amendment_required": True,
        "budget_amendment_authorized": False,
        "execution_authorized": False,
        "exclusive_parent": True,
        "install_once": True,
        "predecessor_read_only": True,
        "predecessor_mutations": [],
        "failure_mode": "refuse-no-retry-preserve-partial-evidence",
        "rollback_scope": "new-successor-namespace-only",
        "sandbox_only": True,
    }


def validate_plan(value: Any) -> Dict[str, Any]:
    record = _exact(value, PLAN_FIELDS, "installer plan")
    _require(type(record["schema_version"]) is int
             and record["schema_version"] == SCHEMA_VERSION,
             "installer plan version differs")
    _require(record["record_type"] == "replay-successor-v4-installer-plan-v1",
             "installer plan record type differs")
    _require(record["action"] == INSTALLER_ACTION,
             "installer plan action differs")
    _require(digest(record["basis"]) == digest(BASIS),
             "installer plan basis differs")
    validate_source_inventory(record["source_inventory"])
    _require(record["installer_sha256"]
             == record["source_inventory"]["installer-entrypoint"],
             "installer plan source binding differs")
    _require(record["interpreter_sha256"] == CANONICAL_PYTHON_SHA256,
             "installer plan interpreter differs")
    _require(record["target_directory"] == TARGET_DIRECTORY,
             "installer plan target differs")
    _require(record["budget_amendment_required"] is True,
             "installer plan must require a separate budget amendment")
    _require(record["budget_amendment_authorized"] is False,
             "installer plan cannot authorize a budget amendment")
    _require(record["execution_authorized"] is False,
             "installer plan cannot authorize execution")
    _require(record["exclusive_parent"] is True
             and record["install_once"] is True
             and record["predecessor_read_only"] is True,
             "installer plan safety flags differ")
    _require(record["predecessor_mutations"] == [],
             "installer plan cannot mutate predecessor state")
    _require(record["failure_mode"] == "refuse-no-retry-preserve-partial-evidence",
             "installer plan failure mode differs")
    _require(record["rollback_scope"] == "new-successor-namespace-only",
             "installer plan rollback scope differs")
    _require(record["sandbox_only"] is True,
             "repository installer core must remain sandbox-only")
    _require(digest(record) == digest(candidate_plan(record["source_inventory"])),
             "installer plan differs from exact candidate regeneration")
    return record


def candidate_review(plan: Mapping[str, Any]) -> Dict[str, Any]:
    validate_plan(plan)
    return {
        "schema_version": SCHEMA_VERSION,
        "record_type": "replay-successor-v4-installer-review-v1",
        "decision": "approved-sandbox-installer-core-only",
        "plan_sha256": digest(plan),
        "source_inventory": dict(plan["source_inventory"]),
        "basis": dict(BASIS),
        "sandbox_only": True,
        "execution_authorized": False,
        "budget_amendment_authorized": False,
        "reconciliation_authorized": False,
        "replay_authorized": False,
    }


def validate_review(value: Any, plan: Mapping[str, Any]) -> Dict[str, Any]:
    validate_plan(plan)
    record = _exact(value, REVIEW_FIELDS, "installer review")
    _require(type(record["schema_version"]) is int
             and record["schema_version"] == SCHEMA_VERSION,
             "installer review version differs")
    _require(record["record_type"] == "replay-successor-v4-installer-review-v1",
             "installer review record type differs")
    _require(record["decision"] == "approved-sandbox-installer-core-only",
             "installer review decision differs")
    _require(record["plan_sha256"] == digest(plan),
             "installer review plan binding differs")
    _require(digest(record["source_inventory"]) == digest(plan["source_inventory"]),
             "installer review source inventory differs")
    _require(digest(record["basis"]) == digest(BASIS),
             "installer review basis differs")
    _require(record["sandbox_only"] is True,
             "installer review cannot approve protected installation")
    _require(record["execution_authorized"] is False
             and record["budget_amendment_authorized"] is False
             and record["reconciliation_authorized"] is False
             and record["replay_authorized"] is False,
             "installer review authority differs")
    _require(digest(record) == digest(candidate_review(plan)),
             "installer review differs from exact candidate regeneration")
    return record


def candidate_authorization(plan: Mapping[str, Any],
                            review: Mapping[str, Any]) -> Dict[str, Any]:
    validate_review(review, plan)
    return {
        "schema_version": SCHEMA_VERSION,
        "record_type": "replay-successor-v4-authorization-v1",
        "action": INSTALLER_ACTION,
        "principal": OPERATOR_PRINCIPAL,
        "basis": dict(BASIS),
        "installer_sha256": plan["installer_sha256"],
        "plan_sha256": digest(plan),
        "review_sha256": digest(review),
        "protected_installation_requested": True,
        "exclusive_parent": True,
        "budget_amendment_required": True,
        "budget_amendment_authorized": False,
        "reconciliation_authorized": False,
        "replay_authorized": False,
        "execution_authorized": False,
        "admission": "blocked",
        "promotion": "disabled",
        "automatic_merge": False,
        "push": False,
    }


def validate_authorization(value: Any, plan: Mapping[str, Any],
                           review: Mapping[str, Any],
                           authorization_sha256: str) -> Dict[str, Any]:
    record = _exact(value, AUTHORIZATION_FIELDS, "installer authorization")
    validate_issued_authorization_shape(record)
    _require(record["installer_sha256"] == plan["installer_sha256"],
             "authorization installer source differs")
    _require(record["plan_sha256"] == digest(plan),
             "authorization plan differs")
    _require(record["review_sha256"] == digest(review),
             "authorization review differs")
    _require(_hashed(authorization_sha256, "external authorization")
             == digest(record),
             "external authorization hash differs")
    _require(digest(record) == digest(candidate_authorization(plan, review)),
             "authorization differs from exact candidate regeneration")
    return record


def _read_stable(path: Path, maximum: int = 16 * 1024 * 1024) -> bytes:
    def stable(info: os.stat_result) -> tuple:
        return (info.st_dev, info.st_ino, info.st_mode, info.st_uid,
                info.st_gid, info.st_nlink, info.st_size,
                info.st_mtime_ns, info.st_ctime_ns)
    flags = os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK
    with os.fdopen(os.open(path, flags), "rb") as stream:
        before = os.fstat(stream.fileno())
        _require(stat.S_ISREG(before.st_mode) and before.st_nlink == 1
                 and before.st_size <= maximum, "unsafe sandbox source")
        raw = stream.read(maximum + 1)
        after = os.fstat(stream.fileno())
        _require(stable(before) == stable(after) == stable(path.lstat())
                 and len(raw) == before.st_size,
                 "sandbox source changed during read")
        return raw


def _safe_sandbox_path(path: Path, sandbox_root: Path, *,
                       exists: bool, directory: bool) -> None:
    """Validate containment lexically first; only then use filesystem metadata.

    The first phase performs no stat/lstat/open calls.  It rejects explicit
    parent traversals, normalized absolute escapes, and any path that overlaps
    the protected GRRR subtree, including an ancestor such as `/Library`.
    Filesystem checks are reached only after those fail-closed lexical checks.
    """
    _require(isinstance(path, Path) and isinstance(sandbox_root, Path)
             and path.is_absolute() and sandbox_root.is_absolute(),
             "sandbox paths must be absolute")
    current = path
    path_members: list[str] = []
    while current.parent != current:
        path_members.append(current.name)
        current = current.parent
    root_current = sandbox_root
    root_members: list[str] = []
    while root_current.parent != root_current:
        root_members.append(root_current.name)
        root_current = root_current.parent
    _require(".." not in path_members and ".." not in root_members,
             "sandbox paths cannot contain '..'")
    _require(not str(path).startswith("//")
             and not str(sandbox_root).startswith("//"),
             "sandbox paths must use a canonical single root separator")

    # Pure lexical canonicalization: no filesystem access occurs here.
    normalized_root = Path(os.path.normpath(str(sandbox_root)))
    normalized_path = Path(os.path.normpath(str(path)))
    _require(normalized_root.parent != normalized_root,
             "sandbox root must not be the filesystem root")
    _require(normalized_path.is_relative_to(normalized_root),
             "sandbox path escapes explicit sandbox root")
    for candidate in (normalized_root, normalized_path):
        protected_overlap = (
            candidate == LIBRARY_ROOT
            or LIBRARY_ROOT in candidate.parents
            or candidate == PROTECTED_ROOT
            or PROTECTED_ROOT in candidate.parents
        )
        _require(not protected_overlap,
                 "protected GRRR path is outside the sandbox")

    # Check the complete real-root-to-sandbox path.  This catches a supplied
    # sandbox root that lies beneath a symlinked ancestor; stopping at that
    # root would hide the escape.
    root_chain: list[Path] = []
    current = normalized_root
    while current.parent != current:
        root_chain.append(current)
        current = current.parent
    root_chain.append(current)
    for member in reversed(root_chain):
        info = member.lstat()
        _require(stat.S_ISDIR(info.st_mode) and not stat.S_ISLNK(info.st_mode),
                 "sandbox root ancestor is not a real directory: " + str(member))

    # Check every component below the sandbox root.  Intermediates must be real
    # directories; only the final component may be the requested file type.
    path_chain: list[Path] = []
    current = normalized_path
    while current != normalized_root:
        path_chain.append(current)
        current = current.parent
    for member in reversed(path_chain):
        if member == normalized_path and not exists:
            continue
        info = member.lstat()
        if member == normalized_path:
            if directory:
                _require(stat.S_ISDIR(info.st_mode)
                         and not stat.S_ISLNK(info.st_mode),
                         "sandbox directory differs")
            else:
                _require(stat.S_ISREG(info.st_mode)
                         and not stat.S_ISLNK(info.st_mode),
                         "sandbox regular file differs")
        else:
            _require(stat.S_ISDIR(info.st_mode)
                     and not stat.S_ISLNK(info.st_mode),
                     "sandbox ancestor is not a real directory: " + str(member))


def verify_source_files(source_root: Path, sandbox_root: Path,
                        inventory: Mapping[str, str]) -> None:
    validate_source_inventory(inventory)
    _safe_sandbox_path(source_root, sandbox_root, exists=True, directory=True)
    for role in SOURCE_ROLES:
        path = source_root / Path(SOURCE_ARTIFACTS[role]).name
        _safe_sandbox_path(path, sandbox_root, exists=True, directory=False)
        _require(_sha(_read_stable(path)) == inventory[role],
                 "sandbox source bytes differ: " + role)


def validate_identity(value: Any) -> Dict[str, Any]:
    record = _exact(value, IDENTITY_FIELDS, "installer identity")
    _require(type(record["uid"]) is int and type(record["euid"]) is int
             and record["uid"] == 0 and record["euid"] == 0,
             "sandbox preflight models root identity but does not acquire it")
    _require(record["interpreter"] == PYTHON_ENTRYPOINT,
             "canonical interpreter path differs")
    _require(record["entrypoint"] == INSTALLER_ENTRYPOINT,
             "canonical installer entrypoint differs")
    _require(record["isolated"] is True and record["no_site"] is True
             and record["no_bytecode"] is True,
             "canonical interpreter flags differ")
    return record


def preflight(source_root: Path, target_root: Path, sandbox_root: Path,
              plan: Mapping[str, Any],
              review: Mapping[str, Any], authorization: Mapping[str, Any],
              authorization_sha256: str, identity: Mapping[str, Any]) -> None:
    validate_identity(identity)
    validate_plan(plan)
    validate_review(review, plan)
    validate_authorization(authorization, plan, review, authorization_sha256)
    _safe_sandbox_path(sandbox_root, sandbox_root, exists=True, directory=True)
    _safe_sandbox_path(source_root, sandbox_root, exists=True, directory=True)
    _safe_sandbox_path(target_root, sandbox_root, exists=True, directory=True)
    verify_source_files(source_root, sandbox_root, plan["source_inventory"])
    target = target_root / SUCCESSOR_STORE_ID
    _safe_sandbox_path(target, sandbox_root, exists=False, directory=True)
    _require(not os.path.lexists(target),
             "existing/partial successor state: refuse reset")


EXPECTED_TABLE_SQL = {
    "reservations": """CREATE TABLE reservations(
            id TEXT PRIMARY KEY, key TEXT UNIQUE NOT NULL,
            binding BLOB NOT NULL, run TEXT NOT NULL, stage TEXT NOT NULL,
            maximum BLOB NOT NULL, actual BLOB, receipt TEXT)""",
    "metering": """CREATE TABLE metering(
            id TEXT PRIMARY KEY, reservation TEXT UNIQUE NOT NULL,
            body BLOB NOT NULL)""",
    "overhead": """CREATE TABLE overhead(
            key TEXT PRIMARY KEY, category TEXT NOT NULL,
            duration_us INTEGER NOT NULL)""",
    "state": """CREATE TABLE state(
            id INTEGER PRIMARY KEY CHECK(id=1), stopped INTEGER NOT NULL)""",
    "store_identity": """CREATE TABLE store_identity(
            campaign TEXT NOT NULL, store_id TEXT NOT NULL,
            prior_history_receipt TEXT NOT NULL)""",
}
EXPECTED_OBJECTS = {
    ("table", "reservations", "reservations"),
    ("table", "metering", "metering"),
    ("table", "overhead", "overhead"),
    ("table", "state", "state"),
    ("table", "store_identity", "store_identity"),
    ("index", "sqlite_autoindex_metering_1", "metering"),
    ("index", "sqlite_autoindex_metering_2", "metering"),
    ("index", "sqlite_autoindex_overhead_1", "overhead"),
    ("index", "sqlite_autoindex_reservations_1", "reservations"),
    ("index", "sqlite_autoindex_reservations_2", "reservations"),
}


def _write_exclusive(path: Path, raw: bytes, mode: int) -> None:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW
    with os.fdopen(os.open(path, flags, mode), "wb") as stream:
        stream.write(raw)
        os.fchmod(stream.fileno(), mode)
        stream.flush()
        os.fsync(stream.fileno())


def _sync_directory(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _create_database(path: Path) -> Dict[str, Any]:
    with closing(sqlite3.connect(path, isolation_level=None)) as db:
        db.execute("PRAGMA journal_mode=DELETE")
        db.execute("PRAGMA synchronous=FULL")
        db.executescript("""
          CREATE TABLE reservations(
            id TEXT PRIMARY KEY, key TEXT UNIQUE NOT NULL,
            binding BLOB NOT NULL, run TEXT NOT NULL, stage TEXT NOT NULL,
            maximum BLOB NOT NULL, actual BLOB, receipt TEXT);
          CREATE TABLE metering(
            id TEXT PRIMARY KEY, reservation TEXT UNIQUE NOT NULL,
            body BLOB NOT NULL);
          CREATE TABLE overhead(
            key TEXT PRIMARY KEY, category TEXT NOT NULL,
            duration_us INTEGER NOT NULL);
          CREATE TABLE state(
            id INTEGER PRIMARY KEY CHECK(id=1), stopped INTEGER NOT NULL);
          INSERT INTO state VALUES(1,1);
          CREATE TABLE store_identity(
            campaign TEXT NOT NULL, store_id TEXT NOT NULL,
            prior_history_receipt TEXT NOT NULL);
        """)
        db.execute(
            "INSERT INTO store_identity VALUES(?,?,?)",
            (SUCCESSOR_CAMPAIGN, SUCCESSOR_STORE_ID,
             PREDECESSOR_RECOVERY_RECEIPT),
        )
    descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
    info = path.lstat()
    return {"device": info.st_dev, "inode": info.st_ino}


def _binding(directory: Path, database_identity: Mapping[str, int]) -> Dict[str, Any]:
    return {
        "version": 4,
        "campaign": SUCCESSOR_CAMPAIGN,
        "store_id": SUCCESSOR_STORE_ID,
        "directory": str(directory),
        "prior_history_receipt": PREDECESSOR_RECOVERY_RECEIPT,
        "profiles": [PROFILE],
        "device": database_identity["device"],
        "inode": database_identity["inode"],
        "successor_sha256": digest(candidate_receipt()),
        "predecessor_store_id": PREDECESSOR_STORE_ID,
        "predecessor_binding_sha256": PREDECESSOR_ACTIVE_SHA256,
        "allowed_mutation_profiles": [PROFILE],
        "execution_authorized": False,
        "budget_amendment_required": True,
        "sandbox_only": True,
    }


def _preserve_uncertain(target: Path, authorization_sha256: str,
                        detail: str) -> None:
    if not target.exists():
        target.mkdir(mode=0o700)
    record = {
        "schema_version": SCHEMA_VERSION,
        "record_type": "replay-successor-v4-uncertain-v1",
        "outcome": "uncertain-no-retry",
        "authorization_sha256": authorization_sha256,
        "detail": detail,
        "execution_authorized": False,
        "budget_amendment_authorized": False,
        "reconciliation_authorized": False,
        "replay_authorized": False,
        "allowed_mutations": [],
    }
    _write_exclusive(target / "uncertain.json", _canonical(record), 0o400)
    _sync_directory(target)


def sandbox_install(source_root: Path, target_root: Path,
                    sandbox_root: Path,
                    plan: Mapping[str, Any], review: Mapping[str, Any],
                    authorization: Mapping[str, Any],
                    authorization_sha256: str,
                    identity: Mapping[str, Any]) -> Dict[str, Any]:
    """Create a stopped sandbox store; this function never performs live install."""
    preflight(source_root, target_root, sandbox_root, plan, review, authorization,
              authorization_sha256, identity)
    target = target_root / SUCCESSOR_STORE_ID
    target.mkdir(mode=0o700)
    try:
        database = target / "budget.sqlite"
        database_identity = _create_database(database)
        os.chmod(database, 0o600)
        binding = _binding(target, database_identity)
        binding_raw = _canonical(binding)
        database_hash = _sha(database.read_bytes())
        receipt = {
            "schema_version": SCHEMA_VERSION,
            "record_type": "replay-successor-v4-sandbox-install-v1",
            "outcome": "sandbox-installed-stopped",
            "plan_sha256": digest(plan),
            "review_sha256": digest(review),
            "authorization_sha256": authorization_sha256,
            "binding_sha256": digest(binding),
            "database_sha256": database_hash,
            "stopped": True,
            "sandbox_only": True,
            "execution_authorized": False,
            "budget_amendment_authorized": False,
            "reconciliation_authorized": False,
            "replay_authorized": False,
            "allowed_mutations": [],
        }
        _write_exclusive(target / "receipt.json", _canonical(receipt), 0o400)
        _write_exclusive(target / "active.json", binding_raw, 0o400)
        _sync_directory(target)
        verify_sandbox_store(target, receipt, sandbox_root)
        return receipt
    except BaseException as exc:
        _preserve_uncertain(target, authorization_sha256, str(exc))
        raise


def verify_sandbox_store(target: Path,
                         expected_receipt: Mapping[str, Any],
                         sandbox_root: Path) -> Dict[str, Any]:
    _safe_sandbox_path(target, sandbox_root, exists=True, directory=True)
    _require(not os.path.lexists(target / "uncertain.json"),
             "sandbox outcome is uncertain and cannot verify as success")
    raw_receipt = _read_stable(target / "receipt.json", 1 << 20)
    raw_binding = _read_stable(target / "active.json", 1 << 20)
    receipt = json.loads(raw_receipt)
    binding = json.loads(raw_binding)
    _exact(receipt, RECEIPT_FIELDS, "sandbox receipt")
    _require(digest(receipt) == digest(expected_receipt)
             and _sha(raw_receipt) == digest(expected_receipt),
             "sandbox receipt differs")
    _require(receipt["outcome"] == "sandbox-installed-stopped"
             and receipt["stopped"] is True
             and receipt["sandbox_only"] is True,
             "sandbox receipt outcome differs")
    _require(receipt["execution_authorized"] is False
             and receipt["budget_amendment_authorized"] is False
             and receipt["reconciliation_authorized"] is False
             and receipt["replay_authorized"] is False,
             "sandbox receipt authority differs")
    _exact(binding, BINDING_FIELDS, "sandbox binding")
    _require(binding["version"] == 4
             and binding["campaign"] == SUCCESSOR_CAMPAIGN
             and binding["store_id"] == SUCCESSOR_STORE_ID
             and binding["directory"] == str(target)
             and binding["profiles"] == [PROFILE]
             and binding["allowed_mutation_profiles"] == [PROFILE]
             and binding["successor_sha256"] == digest(candidate_receipt())
             and binding["predecessor_binding_sha256"] == PREDECESSOR_ACTIVE_SHA256,
             "sandbox binding identity differs")
    _require(binding["execution_authorized"] is False
             and binding["budget_amendment_required"] is True
             and binding["sandbox_only"] is True,
             "sandbox binding authority differs")
    _require(digest(binding) == receipt["binding_sha256"],
             "sandbox receipt/binding hash differs")
    database = target / "budget.sqlite"
    _require(_sha(database.read_bytes()) == receipt["database_sha256"],
             "sandbox database hash differs")
    info = database.lstat()
    _require((info.st_dev, info.st_ino)
             == (binding["device"], binding["inode"]),
             "sandbox database identity differs")
    with closing(sqlite3.connect(database.as_uri() + "?mode=ro", uri=True)) as db:
        _require(db.execute("PRAGMA integrity_check").fetchall() == [("ok",)],
                 "sandbox database integrity differs")
        _require(db.execute("PRAGMA journal_mode").fetchall() == [("delete",)],
                 "sandbox database journal differs")
        objects = {tuple(row) for row in db.execute(
            "SELECT type,name,tbl_name FROM sqlite_master")}
        _require(objects == EXPECTED_OBJECTS,
                 "sandbox database object inventory differs")
        table_sql = {row[0]: row[1] for row in db.execute(
            "SELECT name,sql FROM sqlite_master WHERE type='table'")}
        _require(table_sql == EXPECTED_TABLE_SQL,
                 "sandbox database schema differs")
        _require(db.execute("SELECT id,stopped FROM state").fetchall()
                 == [(1, 1)], "sandbox store must remain stopped")
        _require(db.execute(
            "SELECT campaign,store_id,prior_history_receipt FROM store_identity"
        ).fetchall() == [(SUCCESSOR_CAMPAIGN, SUCCESSOR_STORE_ID,
                          PREDECESSOR_RECOVERY_RECEIPT)],
                 "sandbox store identity differs")
        for table in ("reservations", "metering", "overhead"):
            _require(db.execute("SELECT * FROM " + table).fetchall() == [],
                     "sandbox " + table + " must remain empty")
    return {"binding": binding, "receipt": receipt}


def live_install(*args: Any, **kwargs: Any) -> None:
    """No live path is issued by this repository-only implementation."""
    del args, kwargs
    raise StageCError("replay_successor_installer",
                      "protected v4 installer source is not issued")
