"""The 28 approved spendability evidence adversarial cases."""

from copy import deepcopy
from hashlib import sha256
import json
import unittest


from research.spendability_evidence import validate_evidence


def canonical(value):
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"))


def digest(value):
    return sha256(canonical(value).encode("utf-8")).hexdigest()


def text_digest(value):
    return sha256(value.encode("utf-8")).hexdigest()


def vector(execution_us=0, **changes):
    value = {"currency": "USD", "money_cents": 0, "execution_us": execution_us, "review_us": 0}
    value.update(changes)
    return value


def bound_hash(label):
    return sha256(label.encode("utf-8")).hexdigest()


def provenance(label, binding_authorized=True, authenticated=True):
    return {
        "issuer": "issuer-1",
        "issuer_authenticated": authenticated,
        "evidence_sha256": bound_hash(label + ":evidence"),
        "measurement_window": "2026-10-25T00:00:00Z/2026-10-25T01:00:00Z",
        "trusted_history": authenticated,
        "request_binding_authorized": binding_authorized,
    }


def request_blob(row):
    return canonical({"binding": row["binding"], "maximum": row["maximum"], "run": row["run"], "stage": row["stage"]})


def refresh_baseline(package):
    rows = {name: package[name] for name in ("reservations", "meters", "overhead", "state", "store_identity")}
    package["baseline"]["row_multiset_sha256"] = digest(rows)
    package["reconciliation"]["row_multiset_sha256"] = package["baseline"]["row_multiset_sha256"]
    package["reconciliation"]["baseline_sha256"] = digest(package["baseline"])


def meter_row(reservation, usage):
    body = canonical({"reservation": reservation["id"], "usage": usage})
    return {
        "id": text_digest(body),
        "reservation": reservation["id"],
        "body": body,
        "usage": deepcopy(usage),
        "provenance": provenance(reservation["id"] + ":meter"),
    }


def reservation_row(identifier, maximum, actual=None, binding=None):
    if binding is None:
        binding = bound_hash(identifier + ":binding")
    disposition = "pending" if actual is None else "settled"
    row = {
        "id": identifier,
        "key": "key-" + identifier,
        "run": "run-" + identifier,
        "stage": "poc",
        "maximum": deepcopy(maximum),
        "binding": binding,
        "actual": deepcopy(actual),
        "receipt": None,
        "request_blob": "",
        "request_sha256": "",
        "disposition": disposition,
        "provenance": provenance(identifier + ":reservation"),
        "pending_evidence": None if actual is not None else {
            "dispatch_outcome": "not-dispatched", "final_observation_sha256": bound_hash(identifier + ":final"),
            "stale_handles_accounted": True, "baseline_unchanged": True,
        },
    }
    row["request_blob"] = request_blob(row)
    row["request_sha256"] = text_digest(row["request_blob"])
    return row


def valid_package():
    active = bound_hash("active")
    schema_objects = [
        "state", "reservations", "metering", "overhead", "store_identity",
        "state_id_unique", "reservation_id_unique", "reservation_key_unique",
        "metering_id_unique", "metering_reservation_unique", "overhead_key_unique",
    ]
    settled_usage = [0, 0, 0, 0, 0, 0, 0, 208_265_788]
    reservations = []
    meters = []
    for index, usage in enumerate(settled_usage, 1):
        identifier = "settled-%03d" % index
        actual = vector(usage)
        row = reservation_row(identifier, vector(300_000_000), actual=actual)
        meter = meter_row(row, actual)
        row["receipt"] = meter["id"]
        row["pending_evidence"] = None
        reservations.append(row)
        meters.append(meter)
    for index in range(1, 4):
        identifier = "pending-%03d" % index
        reservations.append(reservation_row(identifier, vector(300_000_000)))

    total = vector(1_108_265_788)
    rows = {
        "reservations": reservations,
        "meters": meters,
        "overhead": [],
        "state": [{"id": 1, "active_binding": active, "stopped": 0}],
        "store_identity": [{
            "campaign": "campaign-1", "store_id": "store-1",
            "active_binding": active,
            "prior_history_receipt": bound_hash("prior-history"),
        }],
    }
    expected_pending = {row["id"]: deepcopy(row["maximum"]) for row in reservations if row["disposition"] == "pending"}
    metadata = {"database_device": 1, "database_inode": 2, "owner": "root", "mode": 0o600,
                "acl": "root:read-write", "link_count": 1, "sidecars": [], "symlinks_absent": True}
    metadata_sha256 = digest(metadata)
    baseline = {
        "active_binding": active,
        "prior_active_binding": bound_hash("prior-active"),
        "registration_receipt": bound_hash("registration"),
        "recovery_intent": bound_hash("recovery-intent"),
        "recovery_receipt": bound_hash("recovery-receipt"),
        "completion_record": bound_hash("completion"),
        "database_sha256": bound_hash("database"),
        "database_device": 1, "database_inode": 2, "owner": "root", "mode": 0o600,
        "acl": "root:read-write", "link_count": 1, "sidecars": [], "symlinks_absent": True,
        "schema_fingerprint": digest({"schema_objects": sorted(schema_objects)}),
        "schema_objects": schema_objects,
        "row_multiset_sha256": digest(rows),
        "metadata_sha256": metadata_sha256,
        "provenance_sha256": digest({
            "database_sha256": bound_hash("database"),
            "metadata_sha256": metadata_sha256,
        }),
        "toolchain_sha256": bound_hash("toolchain"),
        "observer": "observer-1",
        "capture_stable": True,
        "journal_mode": "delete",
        "integrity_result": "ok",
        "journal_sidecars_absent": True,
        "review_sha256": bound_hash("review"),
        "review_approved": True,
        "operator_decision_sha256": bound_hash("operator"),
        "operator_decision_bound": True,
        "historical_completeness": True,
        "recovery_lineage_complete": True,
        "overhead_completeness": {name: True for name in ("preparation", "selection", "execution", "review", "other")},
        "expected_pending_maxima": expected_pending,
    }
    zero_scope = {"poc": vector(), "milestone": vector()}
    reconciliation = {
        "id": "attempt-1",
        "baseline_sha256": digest(baseline),
        "active_binding": baseline["active_binding"],
        "database_sha256": baseline["database_sha256"],
        "schema_fingerprint": baseline["schema_fingerprint"],
        "row_multiset_sha256": baseline["row_multiset_sha256"],
        "policy_sha256": bound_hash("policy"),
        "toolchain_sha256": baseline["toolchain_sha256"],
        "review_sha256": baseline["review_sha256"],
        "authorization_sha256": baseline["operator_decision_sha256"],
        "created_at": "2026-10-25T00:00:00Z", "valid_until": "2026-10-25T01:00:00Z",
        "prior_use": False, "authorization_bound": True, "freshness_attested": True,
        "dispatch_authorization": None,
    }
    return {
        "schema_version": 1,
        "canonicalization_version": 1,
        "baseline": baseline,
        **rows,
        "known_encumbered": {"poc": deepcopy(total), "milestone": deepcopy(total)},
        "overhead_totals": deepcopy(zero_scope),
        "ceilings": {
            "poc": vector(3_300_000_000, money_cents=15_000, review_us=10_000),
            "milestone": vector(3_300_000_000, money_cents=15_000, review_us=10_000),
        },
        "unknown_upper_bounds": deepcopy(zero_scope),
        "reconciliation": reconciliation,
        "reported_spendability": None,
    }


def current_like_package():
    package = valid_package()
    package["baseline"]["historical_completeness"] = False
    package["baseline"]["recovery_lineage_complete"] = False
    package["baseline"]["overhead_completeness"]["other"] = False
    for collection in (package["reservations"], package["meters"]):
        for row in collection:
            row["provenance"]["issuer_authenticated"] = False
            row["provenance"]["trusted_history"] = False
    refresh_baseline(package)
    return package


def set_binding(package, identifier, value, proof):
    row = next(item for item in package["reservations"] if item["id"] == identifier)
    row["binding"] = value
    row["provenance"]["request_binding_authorized"] = proof
    row["request_blob"] = request_blob(row)
    row["request_sha256"] = text_digest(row["request_blob"])
    refresh_baseline(package)


def set_maximum(package, identifier, maximum):
    row = next(item for item in package["reservations"] if item["id"] == identifier)
    row["maximum"] = deepcopy(maximum)
    row["request_blob"] = request_blob(row)
    row["request_sha256"] = text_digest(row["request_blob"])
    refresh_baseline(package)


class SpendabilityEvidenceCases(unittest.TestCase):
    def assert_fail_closed(self, result, gate, expected_pending=3):
        self.assertFalse(result.valid)
        self.assertIsNone(result.spendable)
        self.assertEqual(result.first_failed_gate, gate)
        self.assertEqual(len(result.pending_maxima), expected_pending)
        self.assertEqual(result.pending_maximum_totals["execution_us"], expected_pending * 300_000_000)
        self.assertFalse(result.execution_authorized)
        self.assertEqual(result.allowed_mutations, ())

    def assert_case(self, mutation, gate, refresh=False):
        package = valid_package()
        mutation(package)
        if refresh:
            refresh_baseline(package)
        self.assert_fail_closed(validate_evidence(package), gate)

    def test_case_01_missing_active_artifact_fails_baseline(self):
        self.assert_case(lambda package: package["baseline"].pop("active_binding"), "baseline_ancestry")

    def test_case_02_changed_database_identity_fails_integrity(self):
        self.assert_case(lambda package: package["baseline"].__setitem__(
            "database_inode", package["baseline"]["database_inode"] + 1), "store_integrity", refresh=True)

    def test_case_03_unexpected_schema_object_refuses_before_rows(self):
        self.assert_case(lambda package: package["baseline"]["schema_objects"].append("rogue-object"), "schema_fingerprint")

    def test_case_04_duplicate_reservation_id_is_ambiguous(self):
        self.assert_case(lambda package: package["reservations"].append(deepcopy(package["reservations"][0])), "row_joins", True)

    def test_case_05_orphan_meter_is_not_adopted(self):
        self.assert_case(lambda package: package["meters"][0].__setitem__("reservation", "unjoined-reservation"), "row_joins", True)

    def test_case_06_null_actual_with_receipt_is_invalid(self):
        self.assert_case(lambda package: package["reservations"][0].__setitem__("actual", None), "row_joins", True)

    def test_case_07_usage_over_maximum_is_not_clipped(self):
        self.assert_case(lambda package: set_maximum(package, "settled-008", vector(100_000_000)), "arithmetic")

    def test_case_08_duplicate_meter_json_key_is_rejected(self):
        self.assert_case(lambda package: package["meters"][0].__setitem__("body", (
            '{"reservation":"settled-001","reservation":"settled-001",'
            '"usage":{"currency":"USD","execution_us":0,"money_cents":0,"review_us":0}}'
        )), "canonical_json", True)

    def test_case_09_boolean_integer_is_rejected(self):
        self.assert_case(lambda package: package["reservations"][0]["maximum"].__setitem__("execution_us", True), "row_schema", True)

    def test_case_10_unknown_stage_fails_closed(self):
        self.assert_case(lambda package: package["reservations"][0].__setitem__("stage", "production"), "row_schema", True)

    def test_case_11_all_omitted_pending_holds_remain(self):
        self.assert_case(lambda package: package.__setitem__("reservations", [
            row for row in package["reservations"] if row["disposition"] != "pending"
        ]), "pending_evidence", True)

    def test_case_12_pending_null_changed_to_zero_refused(self):
        def mutate(package):
            next(row for row in package["reservations"] if row["disposition"] == "pending")["actual"] = vector(0)
        self.assert_case(mutate, "row_joins", True)

    def test_case_13_poc_omitted_from_milestone_scope(self):
        self.assert_case(lambda package: package["known_encumbered"]["milestone"].__setitem__(
            "execution_us", package["known_encumbered"]["milestone"]["execution_us"] - 300_000_000), "scope_arithmetic")

    def test_case_14_valid_digest_unauthenticated_issuer_fails(self):
        def mutate(package):
            package["meters"][0]["provenance"]["issuer_authenticated"] = False
            package["meters"][0]["provenance"]["trusted_history"] = False
        self.assert_case(mutate, "provenance", True)

    def test_case_15_null_binding_without_authorization_proof(self):
        self.assert_case(lambda package: set_binding(package, "pending-001", None, False), "provenance")

    def test_case_16_empty_overhead_is_not_historical_zero(self):
        self.assert_case(lambda package: package["baseline"]["overhead_completeness"].__setitem__("preparation", False), "overhead_completeness")

    def test_case_17_partial_recovery_lineage_requires_recovery(self):
        self.assert_case(lambda package: package["baseline"].__setitem__("recovery_lineage_complete", False), "historical_completeness")

    def test_case_18_reused_reconciliation_attempt_is_stale(self):
        self.assert_case(lambda package: package["reconciliation"].__setitem__("prior_use", True), "reconciliation_record")

    def test_case_19_same_count_different_row_multiset_refused(self):
        self.assert_case(lambda package: package["reservations"][0].__setitem__(
            "id", package["reservations"][1]["id"]), "baseline_rows")

    def test_case_20_low_encumbrance_does_not_clear_unresolved_gate(self):
        self.assert_case(lambda package: package["baseline"].__setitem__("historical_completeness", False), "historical_completeness")

    def test_case_21_current_arithmetic_reproduction_is_not_completeness(self):
        package = current_like_package()
        result = validate_evidence(package)
        self.assertFalse(result.valid)
        self.assertIsNone(result.spendable)
        self.assertEqual(result.first_failed_gate, "historical_completeness")
        self.assertEqual(result.pending_maximum_totals["execution_us"], 900_000_000)

    def test_case_22_all_gates_pass_without_dispatch_authorization(self):
        package = valid_package()
        package["reconciliation"]["dispatch_authorization"] = None
        result = validate_evidence(package)
        self.assertTrue(result.valid)
        self.assertTrue(result.spendable)
        self.assertFalse(result.execution_authorized)
        self.assertEqual(result.allowed_mutations, ())

    def test_case_23_one_unresolved_gate_forces_null(self):
        self.assert_case(lambda package: package["baseline"].__setitem__("historical_completeness", False), "historical_completeness")

    def test_case_24_authenticated_paired_null_retains_maximum(self):
        package = valid_package()
        result = validate_evidence(package)
        self.assertTrue(result.valid)
        self.assertIsNotNone(result.pending_maxima["pending-001"])
        self.assertEqual(result.pending_maxima["pending-001"]["execution_us"], 300_000_000)
        self.assertEqual(result.pending_maximum_totals["execution_us"], 900_000_000)

    def test_case_25_provenance_backed_null_binding_is_valid(self):
        package = valid_package()
        set_binding(package, "pending-001", None, True)
        result = validate_evidence(package)
        self.assertTrue(result.valid)
        self.assertTrue(result.spendable)

    def test_case_26_unproven_null_binding_remains_unknown(self):
        self.assert_case(lambda package: set_binding(package, "pending-001", None, False), "provenance")

    def test_case_27_settled_one_sided_null_refused(self):
        self.assert_case(lambda package: package["reservations"][0].__setitem__("receipt", None), "row_joins", True)

    def test_case_28_non_null_spendability_with_unresolved_gate_invalid(self):
        package = current_like_package()
        package["reported_spendability"] = True
        result = validate_evidence(package)
        self.assertFalse(result.valid)
        self.assertIsNone(result.spendable)
        decision = next(gate for gate in result.gate_results if gate.gate == "spendability_decision")
        self.assertFalse(decision.passed)
        self.assertFalse(result.execution_authorized)


if __name__ == "__main__":
    unittest.main()
