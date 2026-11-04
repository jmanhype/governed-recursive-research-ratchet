"""Offline public admission operations against real, isolated registry files."""

import copy
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "research"))
sys.path.insert(0, str(ROOT / "tests"))
import admission
from unit_admission import VALID_RECEIPT, _valid_auth


class AdmissionRegistryIntegration(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        original = admission.REGISTRY_PATH
        self.addCleanup(setattr, admission, "REGISTRY_PATH", original)
        self.path = Path(temporary.name) / "REGISTRY.json"
        admission.REGISTRY_PATH = self.path
        self.contract = admission.build_contract()
        self.auth = _valid_auth(self.contract)
        self.receipt = copy.deepcopy(VALID_RECEIPT)
        # Actual successful local admission supplies a valid recurrence input.
        self.record = admission.admit(self.contract, self.auth, self.receipt)
        self.valid_bytes = self.path.read_bytes()

    def assert_closed(self):
        before = self.path.lstat()
        inputs = copy.deepcopy((self.auth, self.record, self.receipt))
        operations = (
            (admission._load_registry, ()),
            (admission.consume_authorization, (self.auth,)),
            (admission.persist_admission, (self.record,)),
            (admission.recurrence_rejected, (self.record, self.receipt)),
            (admission.admit, (self.contract, self.auth, self.receipt)),
        )
        for operation, args in operations:
            with self.subTest(operation=operation.__name__):
                with self.assertRaises(admission.AdmissionError):
                    operation(*args)
                after = self.path.lstat()
                self.assertEqual((after.st_ino, after.st_size, after.st_mtime_ns),
                                 (before.st_ino, before.st_size, before.st_mtime_ns))
                self.assertFalse(self.path.with_suffix(".tmp").exists())
                self.assertEqual((self.auth, self.record, self.receipt), inputs)

    def test_success_and_durable_duplicates_after_module_reload(self):
        spec = importlib.util.spec_from_file_location("fresh_admission", admission.__file__)
        fresh = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(fresh)
        fresh.REGISTRY_PATH = self.path
        self.assertEqual(self.record["outcome"], "admitted")
        self.assertEqual(self.record["registry_version"], 1)
        registry = json.loads(self.path.read_bytes())
        self.assertEqual(registry, {
            "consumed_authorizations": [self.record["authorization_sha256"]],
            "admitted_contracts": {self.record["contract_sha256"]: self.record},
        })
        with self.assertRaisesRegex(fresh.AdmissionError, "already consumed"):
            fresh.consume_authorization(self.auth)
        with self.assertRaisesRegex(fresh.AdmissionError, "already admitted"):
            fresh.persist_admission(self.record)
        self.assertTrue(fresh.recurrence_rejected(self.record, self.receipt))
        self.assertEqual(self.path.read_bytes(), self.valid_bytes)
        self.assertFalse(self.path.with_suffix(".tmp").exists())

    def test_malformed_truncated_and_invalid_encoding(self):
        for contents in (b"not JSON", b'{"admitted_contracts":', b"\xff",
                         b"[" * 2000 + b"]" * 2000):
            with self.subTest(contents=contents):
                self.path.write_bytes(contents)
                self.assert_closed()
                self.assertEqual(self.path.read_bytes(), contents)

    def test_invalid_shapes(self):
        for value in ([], {}, {"consumed_authorizations": []},
                      {"consumed_authorizations": [], "admitted_contracts": {}, "extra": 1},
                      {"consumed_authorizations": {}, "admitted_contracts": {}},
                      {"consumed_authorizations": [], "admitted_contracts": []}):
            with self.subTest(value=value):
                contents = json.dumps(value).encode()
                self.path.write_bytes(contents)
                self.assert_closed()
                self.assertEqual(self.path.read_bytes(), contents)

    def test_unreadable_file_preserves_bytes(self):
        self.path.chmod(0)
        try:
            self.assert_closed()
        finally:
            self.path.chmod(0o600)
        self.assertEqual(self.path.read_bytes(), self.valid_bytes)

    def test_directory_read_failure_preserves_evidence(self):
        self.path.unlink()
        self.path.mkdir()
        evidence = self.path / "evidence"
        evidence.write_bytes(self.valid_bytes)
        self.assert_closed()
        self.assertTrue(self.path.is_dir())
        self.assertEqual(evidence.read_bytes(), self.valid_bytes)

    def test_dangling_registry_link_is_not_initialization(self):
        self.path.unlink()
        target = self.path.parent / "unavailable.json"
        self.path.symlink_to(target)
        self.assert_closed()
        self.assertTrue(self.path.is_symlink())
        self.assertFalse(target.exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
