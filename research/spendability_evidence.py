"""Fail-closed validation of in-memory spendability evidence packages.

This module validates a synthetic package and reports the first mandatory gate
that failed.  It never interprets a validator result as dispatch, mutation, or
protected-operation authority.
"""

from copy import deepcopy
from dataclasses import dataclass
from hashlib import sha256
import json
import re
from typing import Dict, List, Mapping, Optional, Sequence, Tuple


MAX_INT = 2**63 - 1
VECTOR_FIELDS = ("currency", "money_cents", "execution_us", "review_us")
VECTOR_NAMES = ("money_cents", "execution_us", "review_us")
SCOPES = ("poc", "milestone")
STAGES = frozenset(("poc", "milestone"))
CATEGORIES = frozenset(("preparation", "selection", "execution", "review", "other"))
STATES = frozenset(("settled", "pending"))
OUTCOMES = frozenset(("not-dispatched", "expired", "cancelled", "failed", "non-disposed"))
SCHEMA_OBJECTS = frozenset("""state reservations metering overhead store_identity
state_id_unique reservation_id_unique reservation_key_unique metering_id_unique
metering_reservation_unique overhead_key_unique""".split())
TOP_FIELDS = frozenset("""schema_version canonicalization_version baseline reservations
meters overhead state store_identity known_encumbered overhead_totals ceilings
unknown_upper_bounds reconciliation reported_spendability""".split())
BASELINE_FIELDS = frozenset("""active_binding prior_active_binding registration_receipt
recovery_intent recovery_receipt completion_record database_sha256 database_device
database_inode owner mode acl link_count sidecars symlinks_absent schema_fingerprint
schema_objects row_multiset_sha256 metadata_sha256 provenance_sha256 toolchain_sha256
observer capture_stable journal_mode integrity_result journal_sidecars_absent
review_sha256 review_approved operator_decision_sha256 operator_decision_bound
historical_completeness recovery_lineage_complete overhead_completeness
expected_pending_maxima""".split())
ANCESTRY_FIELDS = "active_binding prior_active_binding registration_receipt recovery_intent recovery_receipt completion_record".split()
RESERVATION_FIELDS = frozenset("""id key run stage maximum binding actual receipt request_blob
request_sha256 disposition provenance pending_evidence""".split())
METER_FIELDS = frozenset("id reservation body usage provenance".split())
OVERHEAD_FIELDS = frozenset("key category duration_us observer activity source_sha256".split())
STATE_FIELDS = frozenset(("id", "active_binding", "stopped"))
STORE_FIELDS = frozenset(("campaign", "store_id", "active_binding", "prior_history_receipt"))
PROVENANCE_FIELDS = frozenset("""issuer issuer_authenticated evidence_sha256
measurement_window trusted_history request_binding_authorized""".split())
PENDING_FIELDS = frozenset("""dispatch_outcome final_observation_sha256
stale_handles_accounted baseline_unchanged""".split())
RECONCILIATION_FIELDS = frozenset("""id baseline_sha256 active_binding database_sha256
schema_fingerprint row_multiset_sha256 policy_sha256 toolchain_sha256 review_sha256
authorization_sha256 created_at valid_until prior_use authorization_bound
freshness_attested dispatch_authorization""".split())
GATES = """package_schema canonical_json baseline_ancestry store_integrity schema_fingerprint
toolchain_observer quiescence independent_review operator_decision historical_completeness
baseline_rows row_schema row_joins provenance pending_evidence overhead_completeness
arithmetic scope_arithmetic reconciliation_record spendability_decision""".split()
IDENTIFIER = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,127}\Z")
HASH = re.compile(r"[0-9a-f]{64}\Z")


@dataclass(frozen=True)
class GateResult:
    """One mandatory gate outcome."""

    gate: str
    passed: bool
    details: Tuple[str, ...] = ()


@dataclass(frozen=True)
class ValidationResult:
    """Structured, fail-closed evidence-validation result."""

    valid: bool
    spendable: Optional[bool]
    first_failed_gate: Optional[str]
    gate_results: Tuple[GateResult, ...]
    pending_maxima: Mapping[str, Mapping[str, int]]
    pending_maximum_totals: Optional[Mapping[str, int]]
    observed_evidence: Mapping[str, object]
    allowed_mutations: Tuple[str, ...] = ()
    execution_authorized: bool = False


def _mapping(value):
    return isinstance(value, Mapping)

def _fail(failures, gate, detail):
    failures.setdefault(gate, []).append(detail)

def _exact(value, expected, failures, gate, label):
    if not _mapping(value):
        _fail(failures, gate, label + " must be an object")
        return False
    actual = set(value)
    if actual != set(expected):
        missing, extra = sorted(set(expected) - actual), sorted(actual - set(expected))
        _fail(failures, gate, f"{label} fields differ; missing={missing!r} extra={extra!r}")
        return False
    return True

def _integer(value):
    return type(value) is int and 0 <= value <= MAX_INT

def _hash(value):
    return type(value) is str and HASH.fullmatch(value) is not None

def _identifier(value):
    return type(value) is str and IDENTIFIER.fullmatch(value) is not None

def _safe_text(value):
    return (type(value) is str and 0 < len(value) <= 256 and value not in (".", "..")
            and ".." not in value.split("/") and all(ord(char) >= 0x20 for char in value))

def _boolean(value):
    return type(value) is bool


def canonical(value: object) -> str:
    """Return the package's versioned canonical JSON representation."""
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"), allow_nan=False)

def _digest(value):
    return sha256(canonical(value).encode("utf-8")).hexdigest()

def _text_digest(value):
    return sha256(value.encode("utf-8")).hexdigest()

def _object_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key: " + key)
        result[key] = value
    return result

def _decode_canonical(value):
    if type(value) is not str:
        return None
    try:
        decoded = json.loads(value, object_pairs_hook=_object_pairs,
                             parse_constant=lambda item: (_ for _ in ()).throw(ValueError(item)))
    except (TypeError, ValueError, json.JSONDecodeError):
        return None
    return decoded if _mapping(decoded) and canonical(decoded) == value else None

def _vector(value):
    if (not _mapping(value) or set(value) != set(VECTOR_FIELDS) or value["currency"] != "USD"
            or not all(_integer(value[name]) for name in VECTOR_NAMES)):
        return None
    return {name: value[name] for name in VECTOR_NAMES}  # type: ignore[misc]

def _zero_vector():
    return {name: 0 for name in VECTOR_NAMES}

def _add(left, right):
    result = _zero_vector()
    for name in VECTOR_NAMES:
        total = left[name] + right[name]
        if total > MAX_INT:
            return None
        result[name] = total
    return result

def _scope_map(value):
    if not _mapping(value) or set(value) != set(SCOPES):
        return None
    result = {}
    for scope in SCOPES:
        vector = _vector(value[scope])
        if vector is None:
            return None
        result[scope] = vector
    return result

def _provenance_valid(value):
    return (
        _mapping(value) and set(value) == set(PROVENANCE_FIELDS)
        and _identifier(value["issuer"])
        and _boolean(value["issuer_authenticated"]) and value["issuer_authenticated"]
        and _hash(value["evidence_sha256"])
        and _safe_text(value["measurement_window"])
        and _boolean(value["trusted_history"]) and value["trusted_history"]
        and _boolean(value["request_binding_authorized"])
    )

def _expected_pending(baseline):
    source = baseline.get("expected_pending_maxima") if _mapping(baseline) else None
    source = source if _mapping(source) else {}
    return {identifier: _vector(value) for identifier, value in source.items()
            if _identifier(identifier) and _vector(value) is not None}

def _observed_pending(reservations, expected):
    result = {key: dict(value) for key, value in expected.items()}
    if not isinstance(reservations, list):
        return result
    for row in reservations:
        if not _mapping(row) or not _identifier(row.get("id")):
            continue
        maximum = _vector(row.get("maximum"))
        if maximum is not None and row.get("disposition") == "pending":
            result[str(row["id"])] = dict(maximum)
    return result

def _pending_totals(pending):
    total = _zero_vector()
    for maximum in pending.values():
        updated = _add(total, maximum)
        if updated is None:
            return None
        total = updated
    return total

def _row_multiset_digest(package):
    try:
        return _digest({name: package[name] for name in ("reservations", "meters", "overhead", "state", "store_identity")})
    except (KeyError, TypeError, ValueError):
        return None


def _validate_baseline(baseline, failures):
    if not _mapping(baseline):
        _fail(failures, "baseline_ancestry", "baseline must be an object")
        return
    for name in ANCESTRY_FIELDS:
        if name not in baseline or not _hash(baseline[name]):
            _fail(failures, "baseline_ancestry", "missing or invalid artifact: " + name)
    if not _exact(baseline, BASELINE_FIELDS, failures, "baseline_ancestry", "baseline"):
        return

    for name in ("database_device", "database_inode", "mode", "link_count"):
        if not _integer(baseline[name]):
            _fail(failures, "store_integrity", "invalid " + name)
    if (not _hash(baseline["database_sha256"]) or not _identifier(baseline["owner"])
            or not _safe_text(baseline["acl"]) or baseline["sidecars"] != []
            or baseline["symlinks_absent"] is not True or baseline["journal_mode"] != "delete"
            or baseline["integrity_result"] != "ok" or baseline["journal_sidecars_absent"] is not True):
        _fail(failures, "store_integrity", "database identity, integrity, or provenance differs")
    names = ("database_device", "database_inode", "owner", "mode", "acl", "link_count", "sidecars", "symlinks_absent")
    metadata = {name: baseline[name] for name in names}
    provenance = {"database_sha256": baseline["database_sha256"], "metadata_sha256": _digest(metadata)}
    if (baseline["metadata_sha256"] != provenance["metadata_sha256"]
            or baseline["provenance_sha256"] != _digest(provenance)):
        _fail(failures, "store_integrity", "database metadata or provenance changed")

    objects = baseline["schema_objects"]
    expected_objects = sorted(SCHEMA_OBJECTS)
    if not isinstance(objects, list) or sorted(objects) != expected_objects:
        _fail(failures, "schema_fingerprint", "unexpected or duplicate schema object")
    elif baseline["schema_fingerprint"] != _digest({"schema_objects": sorted(objects)}):
        _fail(failures, "schema_fingerprint", "invalid schema fingerprint")

    if not _hash(baseline["toolchain_sha256"]) or not _identifier(baseline["observer"]):
        _fail(failures, "toolchain_observer", "toolchain or observer identity differs")
    if not _hash(baseline["metadata_sha256"]) or not _hash(baseline["provenance_sha256"]):
        _fail(failures, "toolchain_observer", "metadata or provenance digest differs")
    if baseline["capture_stable"] is not True:
        _fail(failures, "quiescence", "capture was not stable")
    if not _hash(baseline["review_sha256"]) or baseline["review_approved"] is not True:
        _fail(failures, "independent_review", "review is missing or not approved")
    if not _hash(baseline["operator_decision_sha256"]) or baseline["operator_decision_bound"] is not True:
        _fail(failures, "operator_decision", "operator decision is missing or unbound")
    if baseline["historical_completeness"] is not True:
        _fail(failures, "historical_completeness", "historical completeness is unresolved")
    if baseline["recovery_lineage_complete"] is not True:
        _fail(failures, "historical_completeness", "recovery or interrupted-operation lineage is incomplete")
    completeness = baseline["overhead_completeness"]
    if (not _mapping(completeness) or set(completeness) != set(CATEGORIES)
            or any(completeness[name] is not True for name in CATEGORIES)):
        _fail(failures, "overhead_completeness", "empty overhead is not proven complete")


def _validate_rows(package, failures):
    reservations, meters, overhead = package["reservations"], package["meters"], package["overhead"]
    state_rows, store_rows = package["state"], package["store_identity"]
    if not all(isinstance(value, list) for value in (reservations, meters, overhead, state_rows, store_rows)):
        _fail(failures, "row_schema", "row collections must be arrays")
        return

    for index, row in enumerate(reservations):  # type: ignore[union-attr]
        label = "reservation[" + str(index) + "]"
        if not _exact(row, RESERVATION_FIELDS, failures, "row_schema", label):
            continue
        if (not all(_identifier(row[name]) for name in ("id", "key", "run"))
                or row["stage"] not in STAGES or _vector(row["maximum"]) is None
                or (row["binding"] is not None and not _hash(row["binding"]))
                or (row["actual"] is not None and _vector(row["actual"]) is None)
                or (row["receipt"] is not None and not _hash(row["receipt"]))
                or row["disposition"] not in STATES or not _hash(row["request_sha256"])):
            _fail(failures, "row_schema", label + " fields differ")
        if not _provenance_valid(row["provenance"]):
            _fail(failures, "provenance", label + " provenance is untrusted")
        pending = row["pending_evidence"]
        if row["disposition"] == "pending":
            if not _exact(pending, PENDING_FIELDS, failures, "pending_evidence", label + " pending evidence"):
                continue
            if (pending["dispatch_outcome"] not in OUTCOMES
                    or not _hash(pending["final_observation_sha256"])
                    or pending["stale_handles_accounted"] is not True
                    or pending["baseline_unchanged"] is not True):
                _fail(failures, "pending_evidence", label + " pending evidence is incomplete")
        elif pending is not None:
            _fail(failures, "pending_evidence", label + " settled row has pending evidence")

    for index, row in enumerate(meters):  # type: ignore[union-attr]
        label = "meter[" + str(index) + "]"
        if not _exact(row, METER_FIELDS, failures, "row_schema", label):
            continue
        if not _hash(row["id"]) or not _identifier(row["reservation"]) or _vector(row["usage"]) is None:
            _fail(failures, "row_schema", label + " identity or usage differs")
        if not _provenance_valid(row["provenance"]):
            _fail(failures, "provenance", label + " provenance is untrusted")

    for index, row in enumerate(overhead):  # type: ignore[union-attr]
        label = "overhead[" + str(index) + "]"
        if not _exact(row, OVERHEAD_FIELDS, failures, "row_schema", label):
            continue
        if (not _identifier(row["key"]) or row["category"] not in CATEGORIES
                or not _integer(row["duration_us"]) or not _identifier(row["observer"])
                or not _safe_text(row["activity"]) or not _hash(row["source_sha256"])):
            _fail(failures, "row_schema", label + " fields differ")

    if len(state_rows) != 1 or not _exact(state_rows[0], STATE_FIELDS, failures, "row_schema", "state"):
        return
    state = state_rows[0]
    if state["id"] != 1 or not _hash(state["active_binding"]) or not _integer(state["stopped"]):
        _fail(failures, "row_schema", "state row differs")
    if len(store_rows) != 1 or not _exact(store_rows[0], STORE_FIELDS, failures, "row_schema", "store identity"):
        return
    store = store_rows[0]
    if (not _identifier(store["campaign"]) or not _identifier(store["store_id"])
            or not _hash(store["active_binding"]) or not _hash(store["prior_history_receipt"])):
        _fail(failures, "row_schema", "store identity row differs")


def _validate_joins(package, failures):
    reservations = package["reservations"]
    meters = package["meters"]
    if not isinstance(reservations, list) or not isinstance(meters, list):
        return
    by_id: Dict[str, Mapping[str, object]] = {}
    reservation_keys = set()
    meter_ids = set()
    meter_reservations = set()
    for row in reservations:
        if not _mapping(row) or not _identifier(row.get("id")):
            _fail(failures, "row_joins", "unidentifiable reservation")
            continue
        identifier = str(row["id"])
        if identifier in by_id:
            _fail(failures, "row_joins", "duplicate reservation id: " + identifier)
        else:
            by_id[identifier] = row
        key = row.get("key")
        if not _identifier(key):
            _fail(failures, "row_joins", "invalid reservation key")
        elif key in reservation_keys:
            _fail(failures, "row_joins", "duplicate reservation key: " + str(key))
        else:
            reservation_keys.add(str(key))

    meter_by_reservation: Dict[str, Mapping[str, object]] = {}
    for row in meters:
        if not _mapping(row) or not _hash(row.get("id")) or not _identifier(row.get("reservation")):
            _fail(failures, "row_joins", "unidentifiable meter")
            continue
        if row["id"] in meter_ids:
            _fail(failures, "row_joins", "duplicate meter id")
        meter_ids.add(str(row["id"]))
        reservation = str(row["reservation"])
        if reservation in meter_reservations:
            _fail(failures, "row_joins", "duplicate meter join: " + reservation)
        meter_reservations.add(reservation)
        meter_by_reservation[reservation] = row

    for identifier, row in by_id.items():
        actual = row.get("actual")
        receipt = row.get("receipt")
        if (actual is None) != (receipt is None):
            _fail(failures, "row_joins", "one-sided null on reservation: " + identifier)
        meter = meter_by_reservation.get(identifier)
        if row.get("disposition") == "settled":
            if meter is None:
                _fail(failures, "row_joins", "settled reservation lacks meter: " + identifier)
            elif receipt != meter.get("id"):
                _fail(failures, "row_joins", "reservation receipt differs from meter: " + identifier)
        elif meter is not None:
            _fail(failures, "row_joins", "pending reservation has meter: " + identifier)
        request = _decode_canonical(row.get("request_blob"))
        maximum = _vector(row.get("maximum"))
        if request is None or maximum is None or not _mapping(request):
            _fail(failures, "row_joins", "request projection differs: " + identifier)
        else:
            expected_request = {"binding": row.get("binding"), "maximum": row.get("maximum"),
                                "run": row.get("run"), "stage": row.get("stage")}
            if canonical(request) != canonical(expected_request):
                _fail(failures, "row_joins", "request bytes do not reproduce row: " + identifier)
            if _text_digest(str(row["request_blob"])) != row.get("request_sha256"):
                _fail(failures, "row_joins", "request digest differs: " + identifier)
        if meter is not None:
            body = _decode_canonical(meter.get("body"))
            usage = _vector(meter.get("usage"))
            if body is None or usage is None:
                _fail(failures, "row_joins", "meter body differs: " + identifier)
            else:
                expected_body = {"reservation": identifier, "usage": meter.get("usage")}
                if canonical(body) != canonical(expected_body) or _text_digest(str(meter["body"])) != meter.get("id"):
                    _fail(failures, "row_joins", "meter body or digest differs: " + identifier)
                if actual is not None and usage != _vector(actual):
                    _fail(failures, "row_joins", "meter usage differs from actual: " + identifier)

    for reservation in sorted(meter_reservations - set(by_id)):
        _fail(failures, "row_joins", "orphan meter: " + reservation)
    overhead_keys = set()
    for row in package["overhead"]:  # type: ignore[union-attr]
        if _mapping(row) and _identifier(row.get("key")):
            key = str(row["key"])
            if key in overhead_keys:
                _fail(failures, "row_joins", "duplicate overhead key: " + key)
            overhead_keys.add(key)
    baseline = package["baseline"]
    if _mapping(baseline) and isinstance(package["state"], list) and len(package["state"]) == 1:
        state = package["state"][0]
        if _mapping(state) and state.get("active_binding") != baseline.get("active_binding"):
            _fail(failures, "row_joins", "state does not match active binding")
    if isinstance(package["store_identity"], list) and len(package["store_identity"]) == 1:
        store = package["store_identity"][0]
        if _mapping(store) and _mapping(baseline) and store.get("active_binding") != baseline.get("active_binding"):
            _fail(failures, "row_joins", "store identity does not match active binding")


def _validate_arithmetic(package, failures):
    known = _scope_map(package.get("known_encumbered"))
    ceilings = _scope_map(package.get("ceilings"))
    unknown = _scope_map(package.get("unknown_upper_bounds"))
    overhead_totals = _scope_map(package.get("overhead_totals"))
    if known is None or ceilings is None or unknown is None or overhead_totals is None:
        _fail(failures, "arithmetic", "scope mapping or resource vector differs")
        return None
    calculated: Dict[str, Dict[str, int]] = {}
    reservations = package.get("reservations")
    if not isinstance(reservations, list):
        return calculated
    for row in reservations:
        if not _mapping(row):
            continue
        maximum = _vector(row.get("maximum"))
        actual = _vector(row.get("actual"))
        if maximum is None:
            continue
        if actual is not None:
            if any(actual[name] > maximum[name] for name in VECTOR_NAMES):
                _fail(failures, "arithmetic", "settled usage exceeds maximum without clipping")
            source = actual
        else:
            source = maximum
        scopes = ("poc", "milestone") if row.get("stage") == "poc" else (("milestone",) if row.get("stage") == "milestone" else ())
        for scope in scopes:
            current = calculated.setdefault(scope, _zero_vector())
            updated = _add(current, source)
            if updated is None:
                _fail(failures, "arithmetic", "resource addition overflow")
                current = {name: MAX_INT for name in VECTOR_NAMES}
            else:
                calculated[scope] = updated
    for scope in SCOPES:
        if scope not in calculated:
            calculated[scope] = _zero_vector()
        if known[scope] != calculated[scope]:
            _fail(failures, "scope_arithmetic", "known encumbrance differs for " + scope)
        if any(known[scope][name] > ceilings[scope][name] for name in VECTOR_NAMES):
            _fail(failures, "arithmetic", "known encumbrance exceeds ceiling")
        if any(unknown[scope][name] > ceilings[scope][name] for name in VECTOR_NAMES):
            _fail(failures, "arithmetic", "unknown upper bound exceeds ceiling")
    overhead = package.get("overhead")
    calculated_overhead = {}
    if isinstance(overhead, list):
        for row in overhead:
            if not _mapping(row) or not _integer(row.get("duration_us")):
                continue
            category = row.get("category")
            if category not in CATEGORIES:
                continue
            mapping = calculated_overhead.setdefault(str(category), _zero_vector())
            updated = _add(mapping, {"money_cents": 0, "execution_us": row["duration_us"], "review_us": 0})
            if updated is None:
                _fail(failures, "arithmetic", "overhead addition overflow")
            else:
                calculated_overhead[str(category)] = updated
    for scope in SCOPES:
        expected = _zero_vector()
        for values in calculated_overhead.values():
            updated = _add(expected, values)
            if updated is not None:
                expected = updated
        if overhead_totals[scope] != expected:
            _fail(failures, "arithmetic", "overhead totals are disclosed separately and differ")
    return calculated


def _validate_reconciliation(package, failures):
    record = package.get("reconciliation")
    baseline = package.get("baseline")
    if not _exact(record, RECONCILIATION_FIELDS, failures, "reconciliation_record", "reconciliation"):
        return
    if not _identifier(record["id"]) or not _safe_text(record["created_at"]) or not _safe_text(record["valid_until"]):
        _fail(failures, "reconciliation_record", "attempt identity differs")
    hash_fields = ("baseline_sha256", "active_binding", "database_sha256", "schema_fingerprint", "row_multiset_sha256",
                   "policy_sha256", "toolchain_sha256", "review_sha256", "authorization_sha256")
    if any(not _hash(record[name]) for name in hash_fields):
        _fail(failures, "reconciliation_record", "attempt digest differs")
    if (record["prior_use"] is not False or record["authorization_bound"] is not True
            or record["freshness_attested"] is not True):
        _fail(failures, "reconciliation_record", "attempt is stale, reused, unbound, or no longer fresh")
    if record["dispatch_authorization"] is not None and not _hash(record["dispatch_authorization"]):
        _fail(failures, "reconciliation_record", "dispatch authorization differs")
    if _mapping(baseline):
        expected_values = {
            "active_binding": baseline.get("active_binding"), "database_sha256": baseline.get("database_sha256"),
            "schema_fingerprint": baseline.get("schema_fingerprint"), "row_multiset_sha256": baseline.get("row_multiset_sha256"),
            "toolchain_sha256": baseline.get("toolchain_sha256"), "review_sha256": baseline.get("review_sha256"),
            "authorization_sha256": baseline.get("operator_decision_sha256"),
        }
        bindings = {"baseline_sha256": _digest(baseline), **expected_values}
        for name, expected in bindings.items():
            if record[name] != expected:
                _fail(failures, "reconciliation_record", "changed baseline after authorization: " + name)


def validate_evidence(package: Mapping[str, object]) -> ValidationResult:
    """Validate one synthetic package and return a structured fail-closed result."""

    failures: Dict[str, List[str]] = {}
    reported = package.get("reported_spendability") if _mapping(package) else None
    if not _mapping(package):
        _fail(failures, "package_schema", "package must be an object")
    else:
        fields_valid = _exact(package, TOP_FIELDS, failures, "package_schema", "package")
        if package.get("schema_version") != 1 or package.get("canonicalization_version") != 1:
            _fail(failures, "package_schema", "schema or canonicalization version differs")
        if reported is not None and not _boolean(reported):
            _fail(failures, "spendability_decision", "reported spendability differs")

        baseline = package.get("baseline")
        _validate_baseline(baseline, failures)

        canonical_fields = (("reservations", "request_blob", "reservation request"),
                            ("meters", "body", "meter body"))
        for collection, field, label in canonical_fields:
            if isinstance(package.get(collection), list):
                for row in package[collection]:
                    if _mapping(row) and _decode_canonical(row.get(field)) is None:
                        _fail(failures, "canonical_json", label + " is noncanonical or duplicate-keyed")

        row_digest = _row_multiset_digest(package)
        if _mapping(baseline):
            if not _hash(baseline.get("row_multiset_sha256")):
                _fail(failures, "baseline_rows", "row multiset digest differs")
            elif row_digest != baseline.get("row_multiset_sha256"):
                _fail(failures, "baseline_rows", "counts or checksums match but row multiset differs")

        if fields_valid:
            _validate_rows(package, failures)
            _validate_joins(package, failures)
            _validate_arithmetic(package, failures)
            _validate_reconciliation(package, failures)

        if _mapping(baseline):
            pending_expected = baseline.get("expected_pending_maxima")
            observed_ids = {str(row.get("id")) for row in package.get("reservations", [])  # type: ignore[union-attr]
                            if _mapping(row) and row.get("disposition") == "pending"}
            if not _mapping(pending_expected) or set(pending_expected) != observed_ids:
                _fail(failures, "pending_evidence", "pending row set differs from retained baseline maxima")
            for row in package.get("reservations", []):  # type: ignore[union-attr]
                if not _mapping(row) or row.get("binding") is not None:
                    continue
                provenance = row.get("provenance")
                if not _mapping(provenance) or provenance.get("request_binding_authorized") is not True:
                    _fail(failures, "provenance", "null request binding lacks boundary proof")

    pending = _observed_pending(package.get("reservations") if _mapping(package) else None, _expected_pending(package.get("baseline") if _mapping(package) else None))
    if _mapping(package) and _mapping(package.get("baseline")):
        retained = package["baseline"].get("expected_pending_maxima")
        if _mapping(retained):
            for identifier, maximum in retained.items():
                expected_maximum = _vector(maximum)
                if expected_maximum is None or pending.get(identifier) != expected_maximum:
                    _fail(failures, "pending_evidence", "retained pending maximum differs: " + str(identifier))
    totals = _pending_totals(pending)
    valid = not failures
    spendable: Optional[bool] = None
    if valid:
        ceilings = _scope_map(package.get("ceilings"))
        known = _scope_map(package.get("known_encumbered"))
        unknown = _scope_map(package.get("unknown_upper_bounds"))
        if ceilings is None or known is None or unknown is None:
            valid = False
            _fail(failures, "arithmetic", "final resource projection differs")
        else:
            spendable = all(
                ceilings[scope][name] - known[scope][name] - unknown[scope][name] > 0
                for scope in SCOPES for name in VECTOR_NAMES
            )
            for scope in SCOPES:
                bounded = _add(known[scope], unknown[scope])
                if bounded is None or any(
                    bounded[name] > ceilings[scope][name] for name in VECTOR_NAMES
                ):
                    _fail(failures, "arithmetic", "known plus unknown encumbrance exceeds ceiling")
                    valid = False
                    spendable = None
            if package.get("reported_spendability") is not None and package["reported_spendability"] != spendable:
                _fail(failures, "spendability_decision", "reported spendability does not match conservative arithmetic")
                valid = False
                spendable = None
    if failures and reported is not None:
        _fail(failures, "spendability_decision", "non-null spendability is invalid while a gate is unresolved")
    failed_gates = [gate for gate in GATES if gate in failures]
    first_failure = failed_gates[0] if failed_gates else None
    gate_results = tuple(GateResult(gate, gate not in failures, tuple(failures.get(gate, ()))) for gate in GATES)
    observed = deepcopy(package) if _mapping(package) else {}
    return ValidationResult(valid=valid, spendable=spendable, first_failed_gate=first_failure,
                            gate_results=gate_results, pending_maxima=pending, pending_maximum_totals=totals,
                            observed_evidence=observed, allowed_mutations=(), execution_authorized=False)
