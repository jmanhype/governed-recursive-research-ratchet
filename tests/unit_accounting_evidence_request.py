#!/usr/bin/python3
"""Tests for the pinned accounting evidence-request generator."""
import hashlib
import json
from pathlib import Path
import runpy
import stat
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / (
    "docs/evidence/trusted-observation/accounting-evidence-manifest/MANIFEST.json"
)
SCRIPT = ROOT / "scripts/generate-accounting-evidence-request"
MODULE = runpy.run_path(str(SCRIPT))


class AccountingEvidenceRequest(unittest.TestCase):
    maxDiff = None

    def output_location(self):
        parent = Path(tempfile.mkdtemp(prefix="grrr-request-", dir="/private/tmp"))
        parent.chmod(0o700)
        output = parent / "accounting-evidence-request"

        def cleanup():
            def remove(directory):
                if not directory.exists():
                    return
                for child in directory.iterdir():
                    if child.is_dir() and not child.is_symlink():
                        remove(child)
                    else:
                        child.unlink()
                directory.rmdir()

            remove(output)
            remove(parent)

        self.addCleanup(cleanup)
        return parent, output

    def test_generates_canonical_metadata_only_inventory(self):
        parent, output = self.output_location()
        request, request_hash = MODULE["generate"](MANIFEST, output)
        request_path = output / "REQUEST.json"
        markdown_path = output / "REQUEST.md"
        raw = request_path.read_bytes()
        parsed = json.loads(raw)
        self.assertEqual(parsed, request)
        self.assertEqual(request_hash, hashlib.sha256(raw).hexdigest())
        self.assertEqual(request["basis"]["manifest_sha256"], MODULE["MANIFEST_SHA256"])
        self.assertEqual(len(request["event_records"]), 110)
        self.assertTrue(all(
            set(record) == {
                "available_source_references", "evidence_key", "kind",
                "missing_required_fields", "profile", "reservation", "run",
            } for record in request["event_records"]
        ))
        self.assertEqual(
            sum("original_reservation_mapping" in record["missing_required_fields"]
                for record in request["event_records"]), 94
        )
        self.assertEqual(
            sum("paid_service" in record["missing_required_fields"]
                for record in request["event_records"]), 62
        )
        self.assertTrue(all(
            reference["relationship"] == "available-reference-not-receipt"
            for record in request["event_records"]
            for reference in record["available_source_references"]
        ))
        self.assertEqual(stat.S_IMODE(request_path.stat().st_mode), 0o600)
        self.assertEqual(stat.S_IMODE(markdown_path.stat().st_mode), 0o600)
        markdown = markdown_path.read_text()
        self.assertIn(MODULE["MANIFEST_SHA256"], markdown)
        self.assertIn("94 events", markdown)
        self.assertIn("62 events", markdown)
        self.assertIn("110 events", markdown)

    def test_unknown_manifest_hash_is_refused_without_output(self):
        parent, output = self.output_location()
        globals_dict = MODULE["validate_manifest"].__globals__
        with mock.patch.dict(globals_dict, {"MANIFEST_SHA256": "0" * 64}):
            with self.assertRaisesRegex(MODULE["RequestFailure"], "SHA-256 differs"):
                MODULE["generate"](MANIFEST, output)
        self.assertFalse(output.exists())

    def test_unknown_decision_is_refused_after_hash_pin(self):
        parent, output = self.output_location()
        manifest = json.loads(MANIFEST.read_text())
        manifest["decision"] = "unknown-decision"
        raw = MODULE["canonical_bytes"](manifest)
        pinned = hashlib.sha256(raw).hexdigest()
        tampered = parent / "MANIFEST.json"
        tampered.write_bytes(raw)
        globals_dict = MODULE["validate_manifest"].__globals__
        with mock.patch.dict(globals_dict, {"MANIFEST_SHA256": pinned}):
            with self.assertRaisesRegex(MODULE["RequestFailure"], "unknown manifest decision"):
                MODULE["generate"](tampered, output)
        self.assertFalse(output.exists())

    def test_unknown_top_level_schema_is_refused_after_hash_pin(self):
        parent, output = self.output_location()
        manifest = json.loads(MANIFEST.read_text())
        manifest["unknown_top_level_field"] = True
        raw = MODULE["canonical_bytes"](manifest)
        pinned = hashlib.sha256(raw).hexdigest()
        tampered = parent / "MANIFEST.json"
        tampered.write_bytes(raw)
        globals_dict = MODULE["validate_manifest"].__globals__
        with mock.patch.dict(globals_dict, {"MANIFEST_SHA256": pinned}):
            with self.assertRaisesRegex(MODULE["RequestFailure"], "top-level schema differs"):
                MODULE["generate"](tampered, output)
        self.assertFalse(output.exists())

    def test_unknown_counts_are_refused_after_hash_pin(self):
        parent, output = self.output_location()
        manifest = json.loads(MANIFEST.read_text())
        manifest["summary"]["event_count"] = 109
        raw = MODULE["canonical_bytes"](manifest)
        pinned = hashlib.sha256(raw).hexdigest()
        tampered = parent / "MANIFEST.json"
        tampered.write_bytes(raw)
        globals_dict = MODULE["validate_manifest"].__globals__
        with mock.patch.dict(globals_dict, {"MANIFEST_SHA256": pinned}):
            with self.assertRaisesRegex(MODULE["RequestFailure"], "event count differs"):
                MODULE["generate"](tampered, output)
        self.assertFalse(output.exists())

    def test_existing_request_is_never_overwritten(self):
        parent, output = self.output_location()
        _, original_hash = MODULE["generate"](MANIFEST, output)
        request_path = output / "REQUEST.json"
        markdown_path = output / "REQUEST.md"
        before = (request_path.read_bytes(), markdown_path.read_bytes())
        with self.assertRaisesRegex(MODULE["RequestFailure"], "output directory already exists"):
            MODULE["generate"](MANIFEST, output)
        self.assertEqual((request_path.read_bytes(), markdown_path.read_bytes()), before)
        self.assertEqual(
            hashlib.sha256(request_path.read_bytes()).hexdigest(), original_hash
        )
        self.assertEqual(list(parent.iterdir()), [output])


if __name__ == "__main__":
    unittest.main()
