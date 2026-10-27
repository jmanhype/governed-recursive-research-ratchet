"""Fail-closed Stage C spendability evidence adapters and sidecar schemas.

This module works only with in-memory or repository-retained evidence.  It does
not open protected paths, grant authority, or turn an unresolved record into a
spendability decision.
"""

from dataclasses import dataclass
from hashlib import sha256
import json
import re
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple


STAGE_A_BASELINE_SHA256 = "7608cbe6fc5f671b88573eca8b642ebfbc172f0cb920f75d60ca34cfa60c730a"
DATABASE_SHA256 = "9c6ff2561a364ed982cd5477dd4b200c995da6910c9a17aa3d3c411a962d64f3"
PENDING_IDS = frozenset((
    "69523b39a51c44739114313c9325028c",
    "b34d8b9d106e42eab3a3e43daac98ddd",
    "d375ce6a2d924646bec71df64e939a5b",
))
RESERVATION_IDS = frozenset((
    "1bf9d516461040c0baef70648c074d61",
    "5b7851814d764da1a3b3830abc9853ce",
    "69523b39a51c44739114313c9325028c",
    "7ecc4c7e17f742dc9ec2a8c6dada50f2",
    "b34d8b9d106e42eab3a3e43daac98ddd",
    "b954f6890a1e43e3b13f24298fa7ca33",
    "b95be730d6a5408886071d29848bbd05",
    "d375ce6a2d924646bec71df64e939a5b",
    "d3c965a29ab547c999e66bf0b60eca9f",
    "e38c33051ff64b4eab106e65a200fe06",
    "eb045d10d73b48ef9d570a1cf870f6eb",
))
TABLES = frozenset(("state", "reservations", "metering", "overhead", "store_identity"))
SEMANTIC_OBJECTS = frozenset((
    "state", "reservations", "metering", "overhead", "store_identity",
    "state_id_unique", "reservation_id_unique", "reservation_key_unique",
    "metering_id_unique", "metering_reservation_unique", "overhead_key_unique",
))
OVERHEAD_CATEGORIES = frozenset(("preparation", "selection", "execution", "review", "other"))
LINEAGE_ARTIFACTS = frozenset((
    "registration_prior_active", "registration_receipt", "recovery_prior_active",
    "recovery_intent", "recovery_receipt", "recovery_complete", "active",
    "database_snapshot",
))
HASH_RE = re.compile(r"[0-9a-f]{64}\Z")
IDENTIFIER_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,127}\Z")
TIMESTAMP_RE = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(\.[0-9]+)?Z\Z")
MAX_INT = 2**63 - 1

RAW_SCHEMA_FIELDS = frozenset((
    "schema_version", "database", "sqlite_master", "table_info", "index_list",
    "index_xinfo", "foreign_keys", "application_metadata",
))
DATABASE_FIELDS = frozenset((
    "sha256", "device", "inode", "mode", "uid", "gid", "nlink", "size", "acl",
))
SQLITE_MASTER_FIELDS = frozenset(("type", "name", "table", "sql"))
TABLE_INFO_FIELDS = frozenset(("cid", "name", "type", "notnull", "dflt_value", "pk"))
INDEX_LIST_FIELDS = frozenset(("seq", "name", "unique", "origin", "partial"))
INDEX_XINFO_FIELDS = frozenset(("seqno", "cid", "name", "desc", "coll", "key"))
APP_METADATA_FIELDS = frozenset(("user_version", "application_id", "journal_mode", "encoding"))

QUIESCENCE_FIELDS = frozenset((
    "schema_version", "record_type", "baseline_sha256", "database_sha256", "lock",
    "observations", "sidecars", "process_inventory", "toolchain", "review", "authority",
))
LOCK_FIELDS = frozenset((
    "path", "protocol_version", "exclusive", "all_approved_mutators_covered",
    "identity_before", "identity_opened", "identity_released", "acquired_at", "released_at",
    "acl", "approved_protocol_sha256", "mutator_coverage_sha256",
))
LOCK_IDENTITY_FIELDS = frozenset(("device", "inode", "mode", "uid", "gid", "nlink", "acl"))
DB_OBSERVATION_FIELDS = frozenset((*DATABASE_FIELDS, "observed_at"))
PROCESS_FIELDS = frozenset(("uid_320_count", "uid_321_count", "qemu_count", "inventory_sha256"))
TOOLCHAIN_FIELDS = frozenset(("parent_code", "interpreter", "policy"))
TOOLCHAIN_IDENTITY_FIELDS = frozenset(("observed_sha256", "expected_sha256"))
REVIEW_FIELDS = frozenset(("status", "review_sha256"))

PROVENANCE_FIELDS = frozenset((
    "schema_version", "record_type", "status", "reservation_id", "run", "stage",
    "request", "issuer", "measurement", "source", "meter", "review", "authority",
))
REQUEST_FIELDS = frozenset(("status", "raw_sha256", "canonical_sha256", "binding_authorized"))
ISSUER_FIELDS = frozenset((
    "status", "principal_id", "authenticated", "code_sha256", "toolchain_sha256",
    "policy_sha256", "runtime_profile_sha256",
))
MEASUREMENT_FIELDS = frozenset(("status", "started_at", "ended_at", "clock", "window_sha256"))
SOURCE_FIELDS = frozenset(("status", "path", "raw_sha256", "projection_sha256"))
METER_LINK_FIELDS = frozenset(("status", "meter_id", "usage_sha256"))
DISPATCH_FIELDS = frozenset(("status", "evidence_sha256"))
EVALUATOR_STATE_FIELDS = frozenset(("state", "evidence_sha256"))

PENDING_FIELDS = frozenset((
    "schema_version", "record_type", "status", "reservation_id", "maximum",
    "request_id", "idempotency_key", "operation_id", "final_observation_sha256",
    "cessation", "dispatch", "evaluator_state", "baseline_before_sha256", "baseline_after_sha256",
    "stale_handles_accounted", "missing_evidence", "review", "authority",
))
CESSATION_FIELDS = frozenset(("required", "observed", "method", "evidence_sha256"))
MAXIMUM_FIELDS = frozenset(("currency", "money_cents", "execution_us", "review_us"))
PENDING_STATUSES = frozenset(("live", "expired", "cancelled", "failed_not_dispatched", "unresolved"))

COMPLETENESS_FIELDS = frozenset((
    "schema_version", "record_type", "status", "lineage", "reservation_coverage",
    "operation_coverage", "side_store_coverage", "overhead", "missing_history",
    "unbounded_unknown", "review", "authority",
))
LINEAGE_FIELDS = frozenset(("artifact", "status", "record_sha256", "unexplained"))
COVERAGE_FIELDS = frozenset(("status", "record_sha256", "unexplained"))
RESERVATION_COVERAGE_FIELDS = frozenset(("reservation_id", "status", "record_sha256", "unexplained"))
OVERHEAD_FIELDS = frozenset(("status", "actor", "boundary", "source_sha256", "upper_bound_us"))

AUTHORITY_FIELDS = frozenset((
    "protected_access", "write", "reconcile", "replay", "promotion",
    "admission", "merge", "push",
))

EXPECTED_DDL = {
    "metering": ("CREATE TABLE metering(\n            id TEXT PRIMARY KEY, reservation TEXT UNIQUE NOT NULL, body BLOB NOT NULL)"),
    "overhead": ("CREATE TABLE overhead(\n            key TEXT PRIMARY KEY, category TEXT NOT NULL, duration_us INTEGER NOT NULL)"),
    "reservations": ("CREATE TABLE reservations(\n            id TEXT PRIMARY KEY, key TEXT UNIQUE NOT NULL, binding BLOB NOT NULL,\n            run TEXT NOT NULL, stage TEXT NOT NULL, maximum BLOB NOT NULL,\n            actual BLOB, receipt TEXT)"),
    "state": "CREATE TABLE state(id INTEGER PRIMARY KEY CHECK(id=1), stopped INTEGER NOT NULL)",
    "store_identity": ("CREATE TABLE store_identity(\n            campaign TEXT NOT NULL, store_id TEXT NOT NULL, prior_history_receipt TEXT NOT NULL)"),
}
EXPECTED_COLUMNS = {
    "metering": ("id", "reservation", "body"),
    "overhead": ("key", "category", "duration_us"),
    "reservations": ("id", "key", "binding", "run", "stage", "maximum", "actual", "receipt"),
    "state": ("id", "stopped"),
    "store_identity": ("campaign", "store_id", "prior_history_receipt"),
}
EXPECTED_INDEXES = {
    "metering": (("sqlite_autoindex_metering_2", "u"), ("sqlite_autoindex_metering_1", "pk")),
    "overhead": (("sqlite_autoindex_overhead_1", "pk"),),
    "reservations": (("sqlite_autoindex_reservations_2", "u"), ("sqlite_autoindex_reservations_1", "pk")),
    "state": (),
    "store_identity": (),
}
EXPECTED_TABLE_INFO = {
    "metering": (
        (0, "id", "TEXT", 0, None, 1),
        (1, "reservation", "TEXT", 1, None, 0),
        (2, "body", "BLOB", 1, None, 0),
    ),
    "overhead": (
        (0, "key", "TEXT", 0, None, 1),
        (1, "category", "TEXT", 1, None, 0),
        (2, "duration_us", "INTEGER", 1, None, 0),
    ),
    "reservations": (
        (0, "id", "TEXT", 0, None, 1),
        (1, "key", "TEXT", 1, None, 0),
        (2, "binding", "BLOB", 1, None, 0),
        (3, "run", "TEXT", 1, None, 0),
        (4, "stage", "TEXT", 1, None, 0),
        (5, "maximum", "BLOB", 1, None, 0),
        (6, "actual", "BLOB", 0, None, 0),
        (7, "receipt", "TEXT", 0, None, 0),
    ),
    "state": (
        (0, "id", "INTEGER", 0, None, 1),
        (1, "stopped", "INTEGER", 1, None, 0),
    ),
    "store_identity": (
        (0, "campaign", "TEXT", 1, None, 0),
        (1, "store_id", "TEXT", 1, None, 0),
        (2, "prior_history_receipt", "TEXT", 1, None, 0),
    ),
}
EXPECTED_INDEX_COLUMNS = {
    "sqlite_autoindex_metering_1": "id",
    "sqlite_autoindex_metering_2": "reservation",
    "sqlite_autoindex_overhead_1": "key",
    "sqlite_autoindex_reservations_1": "id",
    "sqlite_autoindex_reservations_2": "key",
}
APPROVED_LOCK_PROTOCOL = "accounting-poc2-exclusive-v1"
APPROVED_LOCK_PROTOCOL_SHA256 = "e4a06e7e2a39e7dd6c55592e83f83b78ee4f892ac53d988fb6f18b5a0923db6e"
APPROVED_MUTATOR_COVERAGE_SHA256 = "61c077f8c4e19b06f99d7d4c35a585c4bcb0f5d1e26aeb3816bbcc4b04cf9dc1"
APPROVED_LOCK_PATH = "/Library/GRRR/accounting-poc2/launch.lock"
APPROVED_LOCK_ACL = "no-acl"


@dataclass(frozen=True)
class StageCError(ValueError):
    """A fail-closed sidecar-schema rejection."""

    gate: str
    detail: str

    def __str__(self) -> str:
        return self.gate + ": " + self.detail


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(value: Any) -> str:
    return sha256(canonical(value).encode("ascii")).hexdigest()


def _mapping(value: Any) -> bool:
    return isinstance(value, Mapping)


def _exact(value: Any, expected: frozenset, label: str, gate: str) -> Dict[str, Any]:
    if not _mapping(value):
        raise StageCError(gate, label + " must be an object")
    actual = set(value)
    if actual != set(expected):
        missing = sorted(set(expected) - actual)
        extra = sorted(actual - set(expected))
        raise StageCError(gate, f"{label} fields differ missing={missing!r} extra={extra!r}")
    return dict(value)


def _hash(value: Any, label: str, gate: str) -> str:
    if type(value) is not str or HASH_RE.fullmatch(value) is None:
        raise StageCError(gate, label + " must be a lowercase SHA-256")
    return value


def _identifier(value: Any, label: str, gate: str) -> str:
    if type(value) is not str or IDENTIFIER_RE.fullmatch(value) is None:
        raise StageCError(gate, label + " differs from the approved identifier grammar")
    return value


def _timestamp(value: Any, label: str, gate: str) -> str:
    if type(value) is not str or TIMESTAMP_RE.fullmatch(value) is None:
        raise StageCError(gate, label + " must be an ASCII UTC timestamp ending in Z")
    return value


def _chronological(start: Any, end: Any, label: str, gate: str) -> None:
    import datetime
    first = datetime.datetime.fromisoformat(_timestamp(start, label + " start", gate).replace("Z", "+00:00"))
    second = datetime.datetime.fromisoformat(_timestamp(end, label + " end", gate).replace("Z", "+00:00"))
    if first >= second:
        raise StageCError(gate, label + " window is not chronological")


def _boolean(value: Any, label: str, gate: str, expected: Optional[bool] = None) -> bool:
    if type(value) is not bool or (expected is not None and value is not expected):
        suffix = "" if expected is None else " must be " + str(expected)
        raise StageCError(gate, label + " differs" + suffix)
    return value


def _integer(value: Any, label: str, gate: str) -> int:
    if type(value) is not int or not 0 <= value <= MAX_INT:
        raise StageCError(gate, label + " must be a bounded nonnegative integer")
    return value


def _text(value: Any, label: str, gate: str) -> str:
    if (type(value) is not str or not 1 <= len(value) <= 256
            or value in (".", "..") or ".." in value.split("/")
            or any(ord(char) < 0x20 for char in value)):
        raise StageCError(gate, label + " contains unsafe or empty text")
    return value


def _enum(value: Any, allowed: frozenset, label: str, gate: str) -> str:
    if type(value) is not str or value not in allowed:
        raise StageCError(gate, label + " contains an unknown enum value")
    return value


def _unknown_list(value: Any, label: str, gate: str, allow_empty: bool = False) -> List[str]:
    if not isinstance(value, list) or (not allow_empty and not value):
        raise StageCError(gate, label + " must be a nonempty list of unknowns")
    for item in value:
        _text(item, label + " entry", gate)
    return [str(item) for item in value]


def _authority(value: Any, gate: str) -> Dict[str, bool]:
    result = _exact(value, AUTHORITY_FIELDS, "authority", gate)
    if any(result[name] is not False for name in AUTHORITY_FIELDS):
        raise StageCError(gate, "sidecar authority must remain entirely false")
    return result


def _review(value: Any, gate: str) -> Dict[str, Any]:
    result = _exact(value, REVIEW_FIELDS, "review", gate)
    status = _enum(result["status"], frozenset(("unresolved", "approved", "rejected")), "review status", gate)
    if status == "unresolved":
        if result["review_sha256"] is not None:
            raise StageCError(gate, "unresolved review cannot carry a review hash")
    else:
        _hash(result["review_sha256"], "review hash", gate)
    return result


def _database_identity(value: Any, label: str, gate: str, observation: bool = False) -> Dict[str, Any]:
    expected = DB_OBSERVATION_FIELDS if observation else DATABASE_FIELDS
    result = _exact(value, expected, label, gate)
    _hash(result["sha256"], label + " hash", gate)
    for name in ("device", "inode", "mode", "uid", "gid", "nlink", "size"):
        _integer(result[name], label + " " + name, gate)
    _text(result["acl"], label + " ACL", gate)
    if observation:
        _timestamp(result["observed_at"], label + " timestamp", gate)
    return result


def _maximum(value: Any, gate: str) -> Dict[str, Any]:
    result = _exact(value, MAXIMUM_FIELDS, "maximum", gate)
    if result["currency"] != "USD":
        raise StageCError(gate, "resource-vector currency differs")
    for name in ("money_cents", "execution_us", "review_us"):
        _integer(result[name], "maximum " + name, gate)
    return result


def _stage_a_schema_shape(baseline: Mapping[str, Any]) -> Mapping[str, Any]:
    if not _mapping(baseline):
        raise StageCError("schema_fingerprint", "Stage A baseline must be an object")
    schema = baseline.get("sqlite_schema")
    if not isinstance(schema, list) or len(schema) != 10:
        raise StageCError("schema_fingerprint", "Stage A sqlite_master inventory differs")
    tables = {}
    indexes = []
    for item in schema:
        if not _mapping(item) or set(item) != set(SQLITE_MASTER_FIELDS):
            raise StageCError("schema_fingerprint", "sqlite_master object schema differs")
        if item["type"] == "table":
            tables[str(item["name"])] = item["sql"]
        elif item["type"] == "index":
            indexes.append((str(item["table"]), str(item["name"])))
        else:
            raise StageCError("schema_fingerprint", "unknown sqlite_master object type")
    if set(tables) != set(TABLES):
        raise StageCError("schema_fingerprint", "raw table inventory differs")
    for name, ddl in EXPECTED_DDL.items():
        if tables[name] != ddl:
            raise StageCError("schema_fingerprint", name + " DDL differs")
    if sorted(indexes) != sorted((table, name)
                                 for table, values in EXPECTED_INDEXES.items()
                                 for name, _ in values):
        raise StageCError("schema_fingerprint", "implicit index inventory differs")
    return {"tables": tables, "indexes": indexes}


def validate_schema_compatibility(raw_schema: Mapping[str, Any]) -> Dict[str, Any]:
    """Validate a complete, read-only raw-schema sidecar and map its semantics."""
    value = _exact(raw_schema, RAW_SCHEMA_FIELDS, "raw schema", "schema_fingerprint")
    if value["schema_version"] != 1:
        raise StageCError("schema_fingerprint", "raw schema version differs")
    database = _database_identity(value["database"], "database", "schema_fingerprint")
    if database["sha256"] != DATABASE_SHA256:
        raise StageCError("schema_fingerprint", "raw schema is not bound to the Stage A database")

    master = value["sqlite_master"]
    if not isinstance(master, list) or len(master) != 10:
        raise StageCError("schema_fingerprint", "complete sqlite_master inventory differs")
    normalized_master = []
    for item in master:
        record = _exact(item, SQLITE_MASTER_FIELDS, "sqlite_master object", "schema_fingerprint")
        _enum(record["type"], frozenset(("table", "index")), "sqlite_master type", "schema_fingerprint")
        _identifier(record["name"], "sqlite_master name", "schema_fingerprint")
        _identifier(record["table"], "sqlite_master table", "schema_fingerprint")
        if record["type"] == "index":
            if record["sql"] is not None:
                raise StageCError("schema_fingerprint", "implicit index carries unexpected SQL")
        elif not isinstance(record["sql"], str):
            raise StageCError("schema_fingerprint", "table SQL is absent")
        normalized_master.append(record)
    _stage_a_schema_shape({"sqlite_schema": normalized_master})

    table_info = _exact(value["table_info"], frozenset(TABLES), "table_info", "schema_fingerprint")
    for table in sorted(TABLES):
        rows = table_info[table]
        if not isinstance(rows, list):
            raise StageCError("schema_fingerprint", table + " column inventory differs")
        observed_rows = []
        for row in rows:
            exact = _exact(row, TABLE_INFO_FIELDS, table + " table_info", "schema_fingerprint")
            _integer(exact["cid"], table + " cid", "schema_fingerprint")
            _identifier(exact["name"], table + " column", "schema_fingerprint")
            if not isinstance(exact["type"], str) or exact["dflt_value"] is not None:
                raise StageCError("schema_fingerprint", table + " column declaration differs")
            _integer(exact["notnull"], table + " notnull", "schema_fingerprint")
            _integer(exact["pk"], table + " pk", "schema_fingerprint")
            observed_rows.append((exact["cid"], exact["name"], exact["type"],
                                  exact["notnull"], exact["dflt_value"], exact["pk"]))
        if tuple(observed_rows) != EXPECTED_TABLE_INFO[table]:
            raise StageCError("schema_fingerprint", table + " column declaration differs")

    index_list = _exact(value["index_list"], frozenset(TABLES), "index_list", "schema_fingerprint")
    index_xinfo = _exact(value["index_xinfo"], frozenset(TABLES), "index_xinfo", "schema_fingerprint")
    for table in sorted(TABLES):
        rows = index_list[table]
        if not isinstance(rows, list):
            raise StageCError("schema_fingerprint", table + " index list differs")
        observed = []
        for row in rows:
            exact = _exact(row, INDEX_LIST_FIELDS, table + " index_list", "schema_fingerprint")
            _integer(exact["seq"], table + " index sequence", "schema_fingerprint")
            _identifier(exact["name"], table + " index", "schema_fingerprint")
            if type(exact["unique"]) is not int or exact["unique"] != 1:
                raise StageCError("schema_fingerprint", table + " index unique differs")
            _enum(exact["origin"], frozenset(("pk", "u")), table + " index origin", "schema_fingerprint")
            _integer(exact["partial"], table + " index partial", "schema_fingerprint")
            if exact["partial"] != 0:
                raise StageCError("schema_fingerprint", table + " partial index is unapproved")
            observed.append((exact["name"], exact["origin"]))
        if tuple(observed) != EXPECTED_INDEXES[table]:
            raise StageCError("schema_fingerprint", table + " semantic index mapping differs")
        xinfo_by_index = index_xinfo[table]
        if not _mapping(xinfo_by_index):
            raise StageCError("schema_fingerprint", table + " index_xinfo differs")
        expected_indexes = {name for name, _ in EXPECTED_INDEXES[table]}
        if set(xinfo_by_index) != expected_indexes:
            raise StageCError("schema_fingerprint", table + " per-index xinfo inventory differs")
        for index_name in sorted(xinfo_by_index):
            rows = xinfo_by_index[index_name]
            if not isinstance(rows, list) or len(rows) != 2:
                raise StageCError("schema_fingerprint", index_name + " xinfo rows differ")
            key = _exact(rows[0], INDEX_XINFO_FIELDS, index_name + " key xinfo", "schema_fingerprint")
            expected_column = EXPECTED_INDEX_COLUMNS[index_name]
            if (key["seqno"] != 0 or key["name"] != expected_column or key["desc"] != 0
                    or key["coll"] != "BINARY" or key["key"] != 1):
                raise StageCError("schema_fingerprint", index_name + " key xinfo differs")
            expected_cid = next(item[0] for item in EXPECTED_TABLE_INFO[table] if item[1] == expected_column)
            _integer(key["cid"], index_name + " key cid", "schema_fingerprint")
            if key["cid"] != expected_cid:
                raise StageCError("schema_fingerprint", index_name + " key xinfo differs")
            auxiliary = _exact(rows[1], INDEX_XINFO_FIELDS, index_name + " auxiliary xinfo", "schema_fingerprint")
            if (auxiliary["seqno"] != 1 or auxiliary["cid"] != -1 or auxiliary["name"] is not None
                    or auxiliary["desc"] != 0 or auxiliary["coll"] != "BINARY" or auxiliary["key"] != 0):
                raise StageCError("schema_fingerprint", index_name + " auxiliary xinfo differs")

    foreign_keys = _exact(value["foreign_keys"], frozenset(TABLES), "foreign_keys", "schema_fingerprint")
    if any(foreign_keys[table] != [] for table in TABLES):
        raise StageCError("schema_fingerprint", "unapproved foreign-key constraint exists")
    metadata = _exact(value["application_metadata"], APP_METADATA_FIELDS, "application_metadata", "schema_fingerprint")
    if (metadata["user_version"] != 0 or metadata["application_id"] != 0
            or metadata["journal_mode"] != "delete" or metadata["encoding"] != "UTF-8"):
        raise StageCError("schema_fingerprint", "database application metadata differs")

    canonical_raw_inventory = {
        "ordering": "sqlite_master,type,name; tables,lexical; indexes,PRAGMA seq; xinfo,key-then-auxiliary",
        "database": database,
        "sqlite_master": sorted(normalized_master, key=lambda item: (item["type"], item["name"])),
        "table_info": {table: table_info[table] for table in sorted(TABLES)},
        "index_list": {table: index_list[table] for table in sorted(TABLES)},
        "index_xinfo": {table: {name: xinfo_by_index[name] for name in sorted(xinfo_by_index)}
                        for table, xinfo_by_index in ((table, index_xinfo[table]) for table in sorted(TABLES))},
        "foreign_keys": {table: foreign_keys[table] for table in sorted(TABLES)},
        "application_metadata": metadata,
    }
    raw_schema_sha256 = digest(canonical_raw_inventory)

    mapping = {
        "state": {"kind": "table", "table": "state", "ddl_sha256": digest(EXPECTED_DDL["state"])},
        "reservations": {"kind": "table", "table": "reservations", "ddl_sha256": digest(EXPECTED_DDL["reservations"])},
        "metering": {"kind": "table", "table": "metering", "ddl_sha256": digest(EXPECTED_DDL["metering"])},
        "overhead": {"kind": "table", "table": "overhead", "ddl_sha256": digest(EXPECTED_DDL["overhead"])},
        "store_identity": {"kind": "table", "table": "store_identity", "ddl_sha256": digest(EXPECTED_DDL["store_identity"])},
        "state_id_unique": {"kind": "table_constraint", "table": "state", "origin": "ddl-check"},
        "reservation_id_unique": {"kind": "index_constraint", "table": "reservations", "index": "sqlite_autoindex_reservations_1", "origin": "pk"},
        "reservation_key_unique": {"kind": "index_constraint", "table": "reservations", "index": "sqlite_autoindex_reservations_2", "origin": "u"},
        "metering_id_unique": {"kind": "index_constraint", "table": "metering", "index": "sqlite_autoindex_metering_1", "origin": "pk"},
        "metering_reservation_unique": {"kind": "index_constraint", "table": "metering", "index": "sqlite_autoindex_metering_2", "origin": "u"},
        "overhead_key_unique": {"kind": "index_constraint", "table": "overhead", "index": "sqlite_autoindex_overhead_1", "origin": "pk"},
    }
    return {
        "schema_version": 1,
        "record_type": "schema-compatibility-v2",
        "status": "mapped",
        "raw_schema_sha256": raw_schema_sha256,
        "raw_inventory_ordering": canonical_raw_inventory["ordering"],
        "mapped_contract_schema_sha256": digest(mapping),
        "semantic_objects": sorted(SEMANTIC_OBJECTS),
        "mapping": mapping,
        "independent_review": "unresolved",
        "authority": {name: False for name in sorted(AUTHORITY_FIELDS)},
    }


def stage_a_schema_gap(baseline: Any) -> Dict[str, Any]:
    """Return the honest missing extended-schema evidence for a Stage A record."""
    _stage_a_schema_shape(_decode_stage_a_baseline(baseline))
    return {
        "schema_version": 1,
        "record_type": "schema-compatibility-v2",
        "status": "unresolved",
        "baseline_sha256": STAGE_A_BASELINE_SHA256,
        "database_sha256": DATABASE_SHA256,
        "missing_evidence": [
            "table_info", "index_list", "index_xinfo", "foreign_keys",
            "application_metadata", "independent compatibility review",
        ],
        "independent_review": "unresolved",
        "authority": {name: False for name in sorted(AUTHORITY_FIELDS)},
    }


def validate_quiescence_record(record: Mapping[str, Any]) -> Dict[str, Any]:
    """Validate writer-exclusion evidence without granting capture authority."""
    value = _exact(record, QUIESCENCE_FIELDS, "quiescence sidecar", "quiescence")
    if value["schema_version"] != 1 or value["record_type"] != "writer-exclusion-v1":
        raise StageCError("quiescence", "quiescence sidecar identity differs")
    _hash(value["baseline_sha256"], "baseline hash", "quiescence")
    _hash(value["database_sha256"], "database hash", "quiescence")
    if value["baseline_sha256"] != STAGE_A_BASELINE_SHA256 or value["database_sha256"] != DATABASE_SHA256:
        raise StageCError("quiescence", "quiescence sidecar is not bound to Stage A")

    lock = _exact(value["lock"], LOCK_FIELDS, "lock", "quiescence")
    if lock["path"] != APPROVED_LOCK_PATH:
        raise StageCError("quiescence", "lock path differs from the accounting-poc2 launch lock")
    if lock["protocol_version"] != APPROVED_LOCK_PROTOCOL:
        raise StageCError("quiescence", "lock protocol is not the approved accounting-poc2 protocol")
    _hash(lock["approved_protocol_sha256"], "approved lock protocol hash", "quiescence")
    if lock["approved_protocol_sha256"] != APPROVED_LOCK_PROTOCOL_SHA256:
        raise StageCError("quiescence", "approved lock protocol binding differs")
    _hash(lock["mutator_coverage_sha256"], "mutator coverage hash", "quiescence")
    if lock["mutator_coverage_sha256"] != APPROVED_MUTATOR_COVERAGE_SHA256:
        raise StageCError("quiescence", "approved mutator coverage binding differs")
    _boolean(lock["exclusive"], "exclusive lock", "quiescence", True)
    _boolean(lock["all_approved_mutators_covered"], "mutator coverage", "quiescence", True)
    _timestamp(lock["acquired_at"], "lock acquired_at", "quiescence")
    _timestamp(lock["released_at"], "lock released_at", "quiescence")
    _chronological(lock["acquired_at"], lock["released_at"], "lock", "quiescence")
    if lock["acl"] != APPROVED_LOCK_ACL:
        raise StageCError("quiescence", "lock ACL differs from the approved no-ACL representation")
    identities = []
    for name in ("identity_before", "identity_opened", "identity_released"):
        item = _exact(lock[name], LOCK_IDENTITY_FIELDS, "lock " + name, "quiescence")
        if item["acl"] != APPROVED_LOCK_ACL:
            raise StageCError("quiescence", "lock identity ACL differs or carries extended entries")
        for field in ("device", "inode", "mode", "uid", "gid", "nlink"):
            _integer(item[field], "lock " + name + " " + field, "quiescence")
        identities.append(item)
    if identities[0] != identities[1] or identities[1] != identities[2]:
        raise StageCError("quiescence", "lock identity changed across open, hold, or release")

    observations = _exact(value["observations"], frozenset(("before", "locked", "after")), "observations", "quiescence")
    observed = [_database_identity(observations[name], name + " database", "quiescence", observation=True)
                for name in ("before", "locked", "after")]
    stable_identity = [{name: item[name] for name in DATABASE_FIELDS} for item in observed]
    if stable_identity[0] != stable_identity[1] or stable_identity[1] != stable_identity[2]:
        raise StageCError("quiescence", "database identity changed during the locked window")
    if any(item["sha256"] != value["database_sha256"] for item in observed):
        raise StageCError("quiescence", "observed database is not the pinned Stage A database")
    _chronological(lock["acquired_at"], observed[0]["observed_at"], "lock-to-before", "quiescence")
    _chronological(observed[0]["observed_at"], observed[1]["observed_at"], "before-to-locked", "quiescence")
    _chronological(observed[1]["observed_at"], observed[2]["observed_at"], "locked-to-after", "quiescence")
    _chronological(observed[2]["observed_at"], lock["released_at"], "after-to-release", "quiescence")
    if value["sidecars"] != []:
        raise StageCError("quiescence", "database sidecar inventory is not empty")

    processes = _exact(value["process_inventory"], PROCESS_FIELDS, "process inventory", "quiescence")
    for name in ("uid_320_count", "uid_321_count", "qemu_count"):
        if processes[name] != 0:
            raise StageCError("quiescence", "sensitive process inventory is nonempty")
    _hash(processes["inventory_sha256"], "process inventory hash", "quiescence")
    toolchain = _exact(value["toolchain"], TOOLCHAIN_FIELDS, "toolchain", "quiescence")
    for name in TOOLCHAIN_FIELDS:
        component = _exact(toolchain[name], TOOLCHAIN_IDENTITY_FIELDS,
                           "toolchain " + name, "quiescence")
        observed_hash = _hash(component["observed_sha256"], "toolchain " + name + " observed", "quiescence")
        expected_hash = _hash(component["expected_sha256"], "toolchain " + name + " expected", "quiescence")
        if observed_hash != expected_hash:
            raise StageCError("quiescence", "toolchain " + name + " identity differs")
    if value["review"]["status"] != "unresolved" or value["review"]["review_sha256"] is not None:
        raise StageCError("quiescence", "Stage C cannot claim reviewed quiescence proof")
    _review(value["review"], "quiescence")
    _authority(value["authority"], "quiescence")
    return {
        "schema_valid": True,
        "writer_exclusion_recorded": True,
        "writer_exclusion_observed": False,
        "writer_exclusion_proven": None,
        "proof_status": "unresolved-requires-independent-protected-capture-review",
        "review_status": value["review"]["status"],
        "valid": False,
        "spendable": None,
        "allowed_mutations": [],
        "execution_authorized": False,
        "authority": value["authority"],
    }


def _provenance_group(value: Any, fields: frozenset, label: str, allowed: frozenset) -> Dict[str, Any]:
    result = _exact(value, fields, label, "provenance")
    status = _enum(result["status"], allowed, label + " status", "provenance")
    return result


def _decode_stage_a_baseline(raw: Any) -> Dict[str, Any]:
    if not isinstance(raw, (bytes, bytearray)):
        raise StageCError("provenance", "retained Stage A baseline must be exact immutable bytes")
    if sha256(raw).hexdigest() != STAGE_A_BASELINE_SHA256:
        raise StageCError("provenance", "retained Stage A baseline SHA-256 differs")

    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise StageCError("provenance", "retained Stage A baseline duplicates JSON key " + key)
            result[key] = value
        return result

    def reject(value):
        raise StageCError("provenance", "retained Stage A baseline contains a non-finite constant")

    try:
        baseline = json.loads(bytes(raw).decode("utf-8"), object_pairs_hook=unique,
                               parse_constant=reject)
    except (UnicodeDecodeError, json.JSONDecodeError, TypeError) as exc:
        raise StageCError("provenance", "retained Stage A baseline is not valid UTF-8 JSON") from exc
    if not _mapping(baseline):
        raise StageCError("provenance", "retained Stage A baseline must be an object")
    database = baseline.get("database")
    before = database.get("before") if _mapping(database) else None
    if not _mapping(before) or before.get("sha256") != DATABASE_SHA256:
        raise StageCError("provenance", "retained Stage A baseline database binding differs")
    raw_tables = baseline.get("raw_tables")
    if not _mapping(raw_tables):
        raise StageCError("provenance", "retained Stage A table inventory differs")
    reservation_table = raw_tables.get("reservations")
    meter_table = raw_tables.get("metering")
    reservation_rows = reservation_table.get("rows") if _mapping(reservation_table) else None
    meter_rows = meter_table.get("rows") if _mapping(meter_table) else None
    if not isinstance(reservation_rows, list) or len(reservation_rows) != len(RESERVATION_IDS):
        raise StageCError("provenance", "retained Stage A reservation inventory differs")
    if not isinstance(meter_rows, list):
        raise StageCError("provenance", "retained Stage A meter inventory differs")

    reservation_columns = set(EXPECTED_COLUMNS["reservations"])
    meter_columns = set(EXPECTED_COLUMNS["metering"])
    by_id = {}
    meter_by_reservation = {}
    for row in reservation_rows:
        if not _mapping(row) or set(row) != reservation_columns:
            raise StageCError("provenance", "retained Stage A reservation columns differ")
        identifier_value = row.get("id")
        if not _mapping(identifier_value) or set(identifier_value) != {"kind", "value"}:
            raise StageCError("provenance", "retained Stage A reservation ID differs")
        reservation_id = _identifier(identifier_value.get("value"), "retained reservation", "provenance")
        if reservation_id in by_id:
            raise StageCError("provenance", "retained Stage A reservation ID is duplicated")
        for name in ("binding", "maximum"):
            cell = row.get(name)
            if (not _mapping(cell) or set(cell) != {"kind", "blob_hex", "byte_count", "decoded"}
                    or cell.get("kind") != "blob"):
                raise StageCError("provenance", "retained Stage A BLOB differs")
            blob = bytes.fromhex(cell["blob_hex"])
            if (len(blob) != cell.get("byte_count")
                    or canonical(cell.get("decoded")).encode("ascii") != blob):
                raise StageCError("provenance", "retained Stage A BLOB projection differs")
        actual = row.get("actual")
        receipt = row.get("receipt")
        if _mapping(actual) and actual.get("kind") == "blob":
            if (set(actual) != {"kind", "blob_hex", "byte_count", "decoded"}
                    or canonical(actual.get("decoded")).encode("ascii")
                    != bytes.fromhex(actual["blob_hex"])
                    or len(bytes.fromhex(actual["blob_hex"])) != actual.get("byte_count")):
                raise StageCError("provenance", "retained Stage A actual BLOB differs")
            actual_present = True
        elif _mapping(actual) and actual == {"kind": "NoneType", "value": None}:
            actual_present = False
        else:
            raise StageCError("provenance", "retained Stage A actual cell differs")
        if _mapping(receipt) and receipt == {"kind": "str", "value": receipt.get("value")}:
            receipt_present = receipt.get("value") is not None
        elif _mapping(receipt) and receipt == {"kind": "NoneType", "value": None}:
            receipt_present = False
        else:
            raise StageCError("provenance", "retained Stage A receipt cell differs")
        if actual_present != receipt_present:
            raise StageCError("provenance", "retained Stage A actual/receipt pairing differs")
        by_id[reservation_id] = row

    for row in meter_rows:
        if not _mapping(row) or set(row) != meter_columns:
            raise StageCError("provenance", "retained Stage A meter columns differ")
        body = row.get("body")
        if (not _mapping(body) or set(body) != {"kind", "blob_hex", "byte_count", "decoded"}
                or body.get("kind") != "blob"):
            raise StageCError("provenance", "retained Stage A meter body differs")
        blob = bytes.fromhex(body["blob_hex"])
        decoded = body.get("decoded")
        if (len(blob) != body.get("byte_count")
                or canonical(decoded).encode("ascii") != blob
                or not _mapping(decoded) or set(decoded) != {"evidence", "reservation", "usage"}):
            raise StageCError("provenance", "retained Stage A meter body projection differs")
        id_cell = row.get("id")
        reservation_cell = row.get("reservation")
        if (not _mapping(id_cell) or id_cell.get("kind") != "str"
                or sha256(blob).hexdigest() != id_cell.get("value")
                or not _mapping(reservation_cell) or reservation_cell.get("kind") != "str"):
            raise StageCError("provenance", "retained Stage A meter identity differs")
        reservation_id = _identifier(reservation_cell.get("value"), "meter join", "provenance")
        if reservation_id not in by_id or reservation_id in meter_by_reservation:
            raise StageCError("provenance", "retained Stage A meter join is ambiguous")
        reservation = by_id[reservation_id]
        receipt_cell = reservation.get("receipt")
        actual_cell = reservation.get("actual")
        if (receipt_cell.get("value") != id_cell.get("value")
                or actual_cell.get("decoded") != decoded.get("usage")):
            raise StageCError("provenance", "retained Stage A meter/receipt usage join differs")
        meter_by_reservation[reservation_id] = row
    if set(by_id) != set(RESERVATION_IDS):
        raise StageCError("provenance", "retained Stage A reservation inventory differs")
    return baseline


def _stage_a_row(baseline: Dict[str, Any], reservation_id: str) -> Tuple[Dict[str, Any], Optional[Dict[str, Any]]]:
    rows = baseline["raw_tables"]["reservations"]["rows"]
    meters = baseline["raw_tables"]["metering"]["rows"]
    reservation = next(row for row in rows if row["id"]["value"] == reservation_id)
    meter = next((row for row in meters if row["reservation"]["value"] == reservation_id), None)
    return reservation, meter


def validate_provenance_record(record: Mapping[str, Any], baseline_raw: Any) -> Dict[str, Any]:
    """Validate one reservation provenance sidecar."""
    value = _exact(record, PROVENANCE_FIELDS, "provenance sidecar", "provenance")
    if value["schema_version"] != 1 or value["record_type"] != "reservation-provenance-v1":
        raise StageCError("provenance", "provenance sidecar identity differs")
    reservation_id = _identifier(value["reservation_id"], "reservation", "provenance")
    if reservation_id not in RESERVATION_IDS:
        raise StageCError("provenance", "reservation is absent from the Stage A inventory")
    baseline = _decode_stage_a_baseline(baseline_raw)
    retained_row, retained_meter = _stage_a_row(baseline, reservation_id)
    retained_run = retained_row["run"].get("value")
    retained_stage = retained_row["stage"].get("value")
    if value["run"] != retained_run or value["stage"] != retained_stage:
        raise StageCError("provenance", "provenance run or stage differs from retained evidence")
    _identifier(value["run"], "run", "provenance")
    _enum(value["stage"], frozenset(("poc",)), "stage", "provenance")
    status = _enum(value["status"], frozenset(("authenticated", "unresolved")), "provenance status", "provenance")
    request_cell = retained_row["binding"]
    request_blob = bytes.fromhex(request_cell["blob_hex"])
    expected_request_raw = sha256(request_blob).hexdigest()
    expected_request_projection = digest(request_cell["decoded"])
    settled = _mapping(retained_row.get("actual")) and retained_row["actual"].get("decoded") is not None
    expected_meter_id = retained_row["receipt"].get("value") if settled else None
    expected_usage_hash = None
    if settled and retained_meter is not None:
        actual_cell = retained_row["actual"]
        expected_usage_hash = digest(actual_cell["decoded"])

    request = _provenance_group(value["request"], REQUEST_FIELDS, "request", frozenset(("present", "missing")))
    issuer = _provenance_group(value["issuer"], ISSUER_FIELDS, "issuer", frozenset(("authenticated", "missing")))
    measurement = _provenance_group(value["measurement"], MEASUREMENT_FIELDS, "measurement", frozenset(("bounded", "missing")))
    source = _provenance_group(value["source"], SOURCE_FIELDS, "source", frozenset(("retained", "missing")))
    meter = _provenance_group(value["meter"], METER_LINK_FIELDS, "meter link", frozenset(("bound", "missing")))
    if status == "authenticated":
        if request["status"] != "present" or issuer["status"] != "authenticated" or measurement["status"] != "bounded" or source["status"] != "retained":
            raise StageCError("provenance", "authenticated row lacks mandatory provenance evidence")
        _hash(request["raw_sha256"], "request raw hash", "provenance")
        _hash(request["canonical_sha256"], "request canonical hash", "provenance")
        _boolean(request["binding_authorized"], "request binding authorization", "provenance", True)
        _identifier(issuer["principal_id"], "issuer principal", "provenance")
        _boolean(issuer["authenticated"], "issuer authentication", "provenance", True)
        for name in ("code_sha256", "toolchain_sha256", "policy_sha256", "runtime_profile_sha256"):
            _hash(issuer[name], "issuer " + name, "provenance")
        _timestamp(measurement["started_at"], "measurement start", "provenance")
        _timestamp(measurement["ended_at"], "measurement end", "provenance")
        _chronological(measurement["started_at"], measurement["ended_at"], "measurement", "provenance")
        _text(measurement["clock"], "measurement clock", "provenance")
        _hash(measurement["window_sha256"], "measurement window", "provenance")
        _text(source["path"], "source path", "provenance")
        _hash(source["raw_sha256"], "source raw hash", "provenance")
        _hash(source["projection_sha256"], "source projection hash", "provenance")
        if request["raw_sha256"] != expected_request_raw or request["canonical_sha256"] != expected_request_projection:
            raise StageCError("provenance", "request provenance does not reproduce retained bytes")
        if source["raw_sha256"] != expected_request_raw or source["projection_sha256"] != expected_request_projection:
            raise StageCError("provenance", "source provenance does not reproduce retained bytes")
        if settled and meter["status"] != "bound":
            raise StageCError("provenance", "settled reservation lacks meter provenance")
        if not settled and meter["status"] != "missing":
            raise StageCError("provenance", "pending reservation cannot assert settled meter provenance")
        if not settled and (meter["meter_id"] is not None or meter["usage_sha256"] is not None):
            raise StageCError("provenance", "missing meter link cannot assert meter evidence")
        if settled:
            _hash(meter["meter_id"], "meter id", "provenance")
            _hash(meter["usage_sha256"], "meter usage hash", "provenance")
            if meter["meter_id"] != expected_meter_id or meter["usage_sha256"] != expected_usage_hash:
                raise StageCError("provenance", "meter provenance does not match retained evidence")
    else:
        if (request["status"] != "missing" or issuer["status"] != "missing"
                or measurement["status"] != "missing" or source["status"] != "missing"
                or meter["status"] != "missing"):
            raise StageCError("provenance", "unresolved provenance groups must all be missing")
        for group, allowed_null in ((request, ("raw_sha256", "canonical_sha256")),
                                    (issuer, ("principal_id", "code_sha256", "toolchain_sha256", "policy_sha256", "runtime_profile_sha256")),
                                    (measurement, ("started_at", "ended_at", "clock", "window_sha256")),
                                    (source, ("path", "raw_sha256", "projection_sha256")),
                                    (meter, ("meter_id", "usage_sha256"))):
            if any(group[name] is not None for name in allowed_null):
                raise StageCError("provenance", "unresolved provenance cannot assert incomplete evidence")
        _boolean(request["binding_authorized"], "request binding authorization", "provenance", False)
        _boolean(issuer["authenticated"], "issuer authentication", "provenance", False)
    _review(value["review"], "provenance")
    _authority(value["authority"], "provenance")
    return {
        "schema_valid": True,
        "reservation_id": reservation_id,
        "status": status,
        "valid": False,
        "spendable": None,
        "allowed_mutations": [],
        "execution_authorized": False,
    }


def validate_pending_disposition(record: Mapping[str, Any]) -> Dict[str, Any]:
    """Validate one explicit pending-hold disposition sidecar."""
    value = _exact(record, PENDING_FIELDS, "pending disposition", "pending_evidence")
    if value["schema_version"] != 1 or value["record_type"] != "pending-disposition-v1":
        raise StageCError("pending_evidence", "pending sidecar identity differs")
    reservation_id = _identifier(value["reservation_id"], "pending reservation", "pending_evidence")
    if reservation_id not in PENDING_IDS:
        raise StageCError("pending_evidence", "reservation is not one of the three Stage A pending holds")
    maximum = _maximum(value["maximum"], "pending_evidence")
    if maximum != {"currency": "USD", "money_cents": 0, "execution_us": 300000000, "review_us": 0}:
        raise StageCError("pending_evidence", "pending maximum differs from the retained full hold")
    status = _enum(value["status"], PENDING_STATUSES, "pending disposition", "pending_evidence")
    for name in ("request_id", "idempotency_key", "operation_id"):
        if status == "unresolved":
            if value[name] is not None:
                raise StageCError("pending_evidence", "unresolved pending sidecar asserts " + name)
        else:
            _identifier(value[name], "pending " + name, "pending_evidence")
    _hash(value["baseline_before_sha256"], "pending baseline before", "pending_evidence")
    _hash(value["baseline_after_sha256"], "pending baseline after", "pending_evidence")
    if (value["baseline_before_sha256"] != DATABASE_SHA256
            or value["baseline_after_sha256"] != DATABASE_SHA256):
        raise StageCError("pending_evidence", "pending disposition changed the protected baseline")
    dispatch = _exact(value["dispatch"], DISPATCH_FIELDS, "dispatch", "pending_evidence")
    dispatch_status = _enum(dispatch["status"], frozenset(("dispatched", "not-dispatched", "unknown")),
                            "dispatch status", "pending_evidence")
    evaluator = _exact(value["evaluator_state"], EVALUATOR_STATE_FIELDS, "evaluator state", "pending_evidence")
    evaluator_state = _enum(evaluator["state"], frozenset(("stopped_or_halted", "active_or_unknown")),
                            "evaluator state", "pending_evidence")
    expected_dispatch = {
        "unresolved": frozenset(("unknown",)),
        "live": frozenset(("not-dispatched",)),
        "expired": frozenset(("not-dispatched",)),
        "cancelled": frozenset(("dispatched", "not-dispatched")),
        "failed_not_dispatched": frozenset(("not-dispatched",)),
    }[status]
    if dispatch_status not in expected_dispatch:
        raise StageCError("pending_evidence", status + " contradicts dispatch evidence")
    expected_evaluator = ("active_or_unknown",) if status == "unresolved" else ("stopped_or_halted",)
    if evaluator_state not in expected_evaluator:
        raise StageCError("pending_evidence", status + " contradicts evaluator state")
    if status == "unresolved":
        if dispatch_status != "unknown" or dispatch["evidence_sha256"] is not None:
            raise StageCError("pending_evidence", "unresolved pending sidecar asserts dispatch evidence")
        if evaluator_state != "active_or_unknown" or evaluator["evidence_sha256"] is not None:
            raise StageCError("pending_evidence", "unresolved pending sidecar asserts evaluator cessation")
    else:
        if dispatch_status == "unknown" or dispatch["evidence_sha256"] is None:
            raise StageCError("pending_evidence", "resolved pending sidecar lacks dispatch evidence")
        _hash(dispatch["evidence_sha256"], "dispatch evidence", "pending_evidence")
        if evaluator_state != "stopped_or_halted" or evaluator["evidence_sha256"] is None:
            raise StageCError("pending_evidence", "resolved pending sidecar lacks evaluator stop evidence")
        _hash(evaluator["evidence_sha256"], "evaluator stop evidence", "pending_evidence")
    cessation = _exact(value["cessation"], CESSATION_FIELDS, "cessation", "pending_evidence")
    _boolean(cessation["required"], "cessation required", "pending_evidence")
    _boolean(cessation["observed"], "cessation observed", "pending_evidence")
    if cessation["required"] and not cessation["observed"]:
        raise StageCError("pending_evidence", "required cessation is unobserved")
    if status != "unresolved":
        if dispatch_status == "dispatched" and cessation["required"] is not True:
            raise StageCError("pending_evidence", "dispatched hold lacks required cessation proof")
        if dispatch_status == "not-dispatched" and cessation["required"] is not False:
            raise StageCError("pending_evidence", "non-dispatched hold cannot require dispatched-process cessation")
    _text(cessation["method"], "cessation method", "pending_evidence")
    _hash(cessation["evidence_sha256"], "cessation evidence", "pending_evidence")
    if status == "unresolved":
        if value["final_observation_sha256"] is not None:
            raise StageCError("pending_evidence", "unresolved pending sidecar asserts a final observation")
        if value["stale_handles_accounted"] is not False:
            raise StageCError("pending_evidence", "unresolved hold must retain full maxima and name missing evidence")
        _unknown_list(value["missing_evidence"], "missing pending evidence", "pending_evidence")
    else:
        _hash(value["final_observation_sha256"], "final observation", "pending_evidence")
        _boolean(value["stale_handles_accounted"], "stale handles", "pending_evidence", True)
        if value["missing_evidence"] != []:
            raise StageCError("pending_evidence", "resolved pending sidecar retains missing evidence")
    _review(value["review"], "pending evidence")
    _authority(value["authority"], "pending evidence")
    return {
        "schema_valid": True,
        "reservation_id": reservation_id,
        "status": status,
        "full_maximum_retained": status == "unresolved" or status == "live",
        "valid": False,
        "spendable": None,
        "allowed_mutations": [],
        "execution_authorized": False,
    }


def _coverage_record(value: Any, label: str, gate: str) -> Dict[str, Any]:
    result = _exact(value, COVERAGE_FIELDS, label, gate)
    status = _enum(result["status"], frozenset(("covered", "unresolved")), label + " status", gate)
    if status == "covered":
        _hash(result["record_sha256"], label + " record", gate)
        if result["unexplained"] != []:
            raise StageCError(gate, label + " is covered but retains unexplained records")
    else:
        if result["record_sha256"] is not None or result["unexplained"] == []:
            raise StageCError(gate, label + " remains unresolved without explicit unknowns")
    _unknown_list(result["unexplained"], label + " unknowns", gate, allow_empty=status == "covered")
    return result


def validate_completeness_record(record: Mapping[str, Any]) -> Dict[str, Any]:
    """Validate the historical-completeness sidecar schema."""
    value = _exact(record, COMPLETENESS_FIELDS, "completeness sidecar", "historical_completeness")
    if value["schema_version"] != 1 or value["record_type"] != "historical-completeness-v1":
        raise StageCError("historical_completeness", "completeness sidecar identity differs")
    status = _enum(value["status"], frozenset(("complete", "unresolved")), "completeness status", "historical_completeness")
    lineage = value["lineage"]
    if not isinstance(lineage, list) or len(lineage) != len(LINEAGE_ARTIFACTS):
        raise StageCError("historical_completeness", "lineage inventory differs")
    artifacts = set()
    for item in lineage:
        exact = _exact(item, LINEAGE_FIELDS, "lineage artifact", "historical_completeness")
        artifact = _enum(exact["artifact"], LINEAGE_ARTIFACTS, "lineage artifact name", "historical_completeness")
        if artifact in artifacts:
            raise StageCError("historical_completeness", "lineage artifact is duplicated")
        artifacts.add(artifact)
        item_status = _enum(exact["status"], frozenset(("bound", "unresolved")), "lineage status", "historical_completeness")
        if item_status == "bound":
            _hash(exact["record_sha256"], "lineage record", "historical_completeness")
            if exact["unexplained"] != []:
                raise StageCError("historical_completeness", "bound lineage artifact is unexplained")
        elif exact["record_sha256"] is not None or exact["unexplained"] == []:
            raise StageCError("historical_completeness", "unresolved lineage artifact lacks explicit unknowns")
        _unknown_list(exact["unexplained"], "lineage unknowns", "historical_completeness",
                      allow_empty=item_status == "bound")
    if artifacts != set(LINEAGE_ARTIFACTS):
        raise StageCError("historical_completeness", "lineage inventory differs")

    reservation_coverage = value["reservation_coverage"]
    if not isinstance(reservation_coverage, list) or len(reservation_coverage) != len(RESERVATION_IDS):
        raise StageCError("historical_completeness", "reservation coverage count differs")
    covered = set()
    for item in reservation_coverage:
        result = _exact(item, RESERVATION_COVERAGE_FIELDS, "reservation coverage", "historical_completeness")
        identifier_value = result.get("reservation_id")
        reservation_id = _identifier(identifier_value, "coverage reservation", "historical_completeness")
        coverage_status = _enum(result["status"], frozenset(("covered", "unresolved")),
                                "reservation coverage status", "historical_completeness")
        if coverage_status == "covered":
            _hash(result["record_sha256"], "reservation coverage record", "historical_completeness")
            if result["unexplained"] != []:
                raise StageCError("historical_completeness", "covered reservation retains unexplained records")
        elif result["record_sha256"] is not None or result["unexplained"] == []:
            raise StageCError("historical_completeness", "unresolved reservation lacks explicit unknowns")
        _unknown_list(result["unexplained"], "reservation unknowns", "historical_completeness",
                      allow_empty=coverage_status == "covered")
        if reservation_id in covered or reservation_id not in RESERVATION_IDS:
            raise StageCError("historical_completeness", "reservation coverage identity differs")
        covered.add(reservation_id)
    if covered != set(RESERVATION_IDS):
        raise StageCError("historical_completeness", "reservation coverage inventory differs")

    for name in ("operation_coverage", "side_store_coverage"):
        rows = value[name]
        if not isinstance(rows, list) or not rows:
            raise StageCError("historical_completeness", name + " differs")
        for item in rows:
            _coverage_record(item, name, "historical_completeness")
        if status == "complete" and any(item["status"] != "covered" for item in rows):
            raise StageCError("historical_completeness", name + " is unresolved in a complete record")

    overhead = _exact(value["overhead"], OVERHEAD_CATEGORIES, "overhead coverage", "historical_completeness")
    for category in OVERHEAD_CATEGORIES:
        item = _exact(overhead[category], OVERHEAD_FIELDS, category + " overhead", "historical_completeness")
        item_status = _enum(item["status"], frozenset(("covered", "unresolved")), category + " status", "historical_completeness")
        _text(item["actor"], category + " actor", "historical_completeness")
        _text(item["boundary"], category + " boundary", "historical_completeness")
        _hash(item["source_sha256"], category + " source", "historical_completeness")
        if item_status == "covered":
            _integer(item["upper_bound_us"], category + " upper bound", "historical_completeness")
        elif item["upper_bound_us"] is not None:
            raise StageCError("historical_completeness", category + " unresolved upper bound must be null")
        if status == "complete" and item_status != "covered":
            raise StageCError("historical_completeness", category + " overhead is unresolved in a complete record")

    missing_history = _unknown_list(value["missing_history"], "missing history", "historical_completeness", allow_empty=True)
    if missing_history and status == "complete":
        raise StageCError("historical_completeness", "complete record retains missing history")
    if status == "unresolved" and value["missing_history"] == []:
        raise StageCError("historical_completeness", "unresolved record does not name missing history")
    _boolean(value["unbounded_unknown"], "unbounded unknown", "historical_completeness", status == "unresolved")
    if status == "complete" and any(item["status"] != "bound" for item in lineage):
        raise StageCError("historical_completeness", "complete record retains unresolved lineage")
    if status == "complete" and any(item["status"] != "covered" for item in reservation_coverage):
        raise StageCError("historical_completeness", "complete record retains unresolved reservations")
    _review(value["review"], "historical completeness")
    _authority(value["authority"], "historical completeness")
    return {
        "schema_valid": True,
        "status": status,
        "valid": False,
        "spendable": None,
        "allowed_mutations": [],
        "execution_authorized": False,
    }


def unresolved_stage_c_outcome(first_failed_gate: str) -> Dict[str, Any]:
    """Return the only Stage C result permitted while evidence is incomplete."""
    if first_failed_gate not in {"schema_fingerprint", "quiescence", "provenance", "pending_evidence", "historical_completeness"}:
        raise StageCError("spendability_decision", "unknown Stage C gate")
    return {
        "valid": False,
        "first_failed_gate": first_failed_gate,
        "spendable": None,
        "allowed_mutations": [],
        "execution_authorized": False,
        "authority": {name: False for name in sorted(AUTHORITY_FIELDS)},
    }
