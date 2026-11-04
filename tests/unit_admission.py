"""Tests for the Counterexample-to-Contract admission system."""

import copy
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "research"))

from admission import (
    APPROVED_OPERATOR,
    CHALLENGE,
    REPLAY_EXPORT_SHA256,
    AdmissionError,
    admit,
    build_contract,
    check_gates,
    recurrence_rejected,
    validate_authorization,
    validate_contract,
)
import admission as _admission_mod

VALID_RECEIPT = {
    "finding": "Verified defect",
    "verified": True,
    "gates": {
        "source_environment_identity": {"status": "pass"},
        "isolation": {"status": "pass"},
        "protected_asset_integrity": {"status": "pass"},
        "baseline_correctness": {"status": "pass"},
        "trusted_observation": {"status": "pass"},
        "independent_replay": {"status": "pass"},
        "specification_traceability": {"status": "pass"},
        "evidence_integrity_currency": {"status": "pass"},
        "budget_state": {"status": "pass"},
    },
}


def _valid_auth(contract):
    return {
        "schema_version": 1,
        "record_type": "grrr-contract-admission-authorization-v1",
        "contract_sha256": contract["contract_sha256"],
        "authorized_by": "operator-speed",
        "authorized_at": "2026-11-03T17:00:00Z",
        "authorization_type": "permanent-contract-admission",
        "consumed": False,
    }


class TestAdmission(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        original = _admission_mod.REGISTRY_PATH
        self.addCleanup(setattr, _admission_mod, "REGISTRY_PATH", original)
        _admission_mod.REGISTRY_PATH = Path(temporary.name) / "REGISTRY.json"
        self.contract = build_contract()
        self.auth = _valid_auth(self.contract)
        self.receipt = copy.deepcopy(VALID_RECEIPT)

    def test_missing_registry_is_empty_without_writing(self):
        self.assertEqual(_admission_mod._load_registry(), {
            "consumed_authorizations": [], "admitted_contracts": {},
        })
        self.assertFalse(_admission_mod.REGISTRY_PATH.exists())

    def test_corrupt_registry_rejects_without_reset(self):
        for contents in (b"not JSON", b'{"consumed_authorizations": [', b"\xff"):
            with self.subTest(contents=contents):
                _admission_mod.REGISTRY_PATH.write_bytes(contents)
                with self.assertRaises(AdmissionError):
                    _admission_mod._load_registry()
                self.assertEqual(_admission_mod.REGISTRY_PATH.read_bytes(), contents)
                self.assertFalse(_admission_mod.REGISTRY_PATH.with_suffix(".tmp").exists())

    def test_invalid_registry_shapes_reject(self):
        invalid = [None, [], "registry", 1, True, {},
                   {"consumed_authorizations": []}, {"admitted_contracts": {}},
                   {"consumed_authorizations": [], "admitted_contracts": {}, "extra": 1}]
        for wrong in (None, {}, "", 1, True):
            invalid.append({"consumed_authorizations": wrong, "admitted_contracts": {}})
        for wrong in (None, [], "", 1, True):
            invalid.append({"consumed_authorizations": [], "admitted_contracts": wrong})
        for value in invalid:
            with self.subTest(value=value):
                _admission_mod.REGISTRY_PATH.write_text(json.dumps(value))
                with self.assertRaises(AdmissionError):
                    _admission_mod._load_registry()

    def test_unavailable_registry_metadata_rejects(self):
        parent = _admission_mod.REGISTRY_PATH.parent
        parent.chmod(0)
        try:
            with self.assertRaises(AdmissionError):
                _admission_mod._load_registry()
        finally:
            parent.chmod(0o700)
        self.assertEqual(list(parent.iterdir()), [])

    def test_duplicate_state_survives_reload(self):
        result = admit(self.contract, self.auth, self.receipt)
        expected = {
            "consumed_authorizations": [result["authorization_sha256"]],
            "admitted_contracts": {result["contract_sha256"]: result},
        }
        self.assertEqual(_admission_mod._load_registry(), expected)
        with self.assertRaises(AdmissionError):
            _admission_mod.consume_authorization(self.auth)
        with self.assertRaises(AdmissionError):
            _admission_mod.persist_admission(result)
        self.assertTrue(recurrence_rejected(result, self.receipt))
        self.assertEqual(_admission_mod._load_registry(), expected)

    def test_valid_contract(self):
        validated = validate_contract(copy.deepcopy(self.contract))
        self.assertEqual(validated["challenge"], CHALLENGE)

    def test_contract_hash_is_deterministic(self):
        self.assertEqual(
            build_contract()["contract_sha256"],
            build_contract()["contract_sha256"],
        )

    def test_wrong_challenge_rejects(self):
        bad = copy.deepcopy(self.contract)
        bad["challenge"] = "GRRR-VC-D999"
        with self.assertRaises(AdmissionError):
            validate_contract(bad)

    def test_modified_contract_hash_rejects(self):
        bad = copy.deepcopy(self.contract)
        bad["expected_behavior"]["expected_display"] = "WRONG"
        with self.assertRaises(AdmissionError):
            validate_contract(bad)

    def test_valid_authorization(self):
        validated = validate_authorization(copy.deepcopy(self.auth), self.contract)
        self.assertEqual(validated["authorized_by"], "operator-speed")

    def test_wrong_contract_target_rejects(self):
        bad = copy.deepcopy(self.auth)
        bad["contract_sha256"] = "0" * 64
        with self.assertRaises(AdmissionError):
            validate_authorization(bad, self.contract)

    def test_consumed_authorization_rejects(self):
        bad = copy.deepcopy(self.auth)
        bad["consumed"] = True
        with self.assertRaises(AdmissionError):
            validate_authorization(bad, self.contract)

    def test_wrong_auth_type_rejects(self):
        bad = copy.deepcopy(self.auth)
        bad["authorization_type"] = "software-promotion"
        with self.assertRaises(AdmissionError):
            validate_authorization(bad, self.contract)

    def test_wrong_operator_rejects(self):
        bad = copy.deepcopy(self.auth)
        bad["authorized_by"] = "intruder"
        with self.assertRaises(AdmissionError):
            validate_authorization(bad, self.contract)

    def test_wrong_export_hash_rejects(self):
        bad = copy.deepcopy(self.contract)
        bad["replay_binding"]["export_sha256"] = "0" * 64
        with self.assertRaises(AdmissionError):
            validate_contract(bad)

    def test_authorization_consumed_after_use(self):
        result1 = admit(self.contract, self.auth, self.receipt)
        self.assertEqual(result1["outcome"], "admitted")
        # Same authorization cannot be reused
        with self.assertRaises(AdmissionError):
            admit(self.contract, self.auth, self.receipt)

    def test_duplicate_contract_admission_rejects(self):
        result1 = admit(self.contract, self.auth, self.receipt)
        self.assertEqual(result1["outcome"], "admitted")
        # New authorization for same contract also blocked (already admitted)
        auth2 = copy.deepcopy(self.auth)
        auth2["authorized_at"] = "2026-11-03T18:00:00Z"
        with self.assertRaises(AdmissionError):
            admit(self.contract, auth2, self.receipt)

    def test_recurrence_checks_contract_registry(self):
        result = admit(self.contract, self.auth, self.receipt)
        # Valid recurrence check
        self.assertTrue(recurrence_rejected(result, self.receipt))
        # Fake admission (not in registry) rejects
        fake = {"outcome": "admitted", "contract_sha256": "f" * 64}
        self.assertFalse(recurrence_rejected(fake, self.receipt))

    def test_recurrence_checks_gate_results(self):
        result = admit(self.contract, self.auth, self.receipt)
        bad_result = copy.deepcopy(result)
        bad_result["gate_results"]["isolation"] = "not-run"
        self.assertFalse(recurrence_rejected(bad_result, self.receipt))

    def test_admission_includes_gate_results(self):
        result = admit(self.contract, self.auth, self.receipt)
        self.assertIn("gate_results", result)
        self.assertEqual(len(result["gate_results"]), 9)

    def test_all_gates_pass(self):
        results = check_gates(self.receipt)
        self.assertEqual(len(results), 9)
        for status in results.values():
            self.assertEqual(status, "pass")

    def test_not_run_gate_rejects(self):
        bad = copy.deepcopy(self.receipt)
        bad["gates"]["isolation"]["status"] = "not-run"
        with self.assertRaises(AdmissionError):
            check_gates(bad)

    def test_failed_gate_rejects(self):
        bad = copy.deepcopy(self.receipt)
        bad["gates"]["baseline_correctness"]["status"] = "fail"
        with self.assertRaises(AdmissionError):
            check_gates(bad)

    def test_unverified_finding_rejects(self):
        bad = copy.deepcopy(self.receipt)
        bad["finding"] = "Not reproduced"
        with self.assertRaises(AdmissionError):
            check_gates(bad)

    def test_successful_admission(self):
        result = admit(self.contract, self.auth, self.receipt)
        self.assertEqual(result["outcome"], "admitted")
        self.assertEqual(result["registry_version"], 1)

    def test_recurrence_rejected(self):
        result = admit(self.contract, self.auth, self.receipt)
        self.assertTrue(recurrence_rejected(result, self.receipt))

    def test_recurrence_not_rejected_if_not_admitted(self):
        self.assertFalse(recurrence_rejected({"outcome": "blocked"}, self.receipt))

    def test_admission_with_bad_receipt_rejects(self):
        bad_receipt = copy.deepcopy(self.receipt)
        bad_receipt["gates"]["isolation"]["status"] = "error"
        with self.assertRaises(AdmissionError):
            admit(self.contract, self.auth, bad_receipt)


if __name__ == "__main__":
    unittest.main()
