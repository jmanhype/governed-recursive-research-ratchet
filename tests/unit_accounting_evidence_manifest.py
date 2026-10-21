#!/usr/bin/python3
"""Fixture tests for the read-only accounting evidence manifest."""
import hashlib
import json
from pathlib import Path
import runpy
import sqlite3
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/collect-accounting-evidence-manifest"
MODULE = runpy.run_path(str(SCRIPT))


class AccountingEvidenceManifest(unittest.TestCase):
    maxDiff = None
    def make_fixture(self, duplicate=False, malformed=False):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        artifact_a = b'{"artifact":"a"}'
        artifact_b = b'{"artifact":"b"}'
        source_a = {
            "path": "docs/evidence/example/a.json",
            "sha256": hashlib.sha256(artifact_a).hexdigest(),
        }
        source_b = {
            "path": "docs/evidence/example/b.json",
            "sha256": hashlib.sha256(artifact_b).hexdigest(),
        }
        event_one = {
            "event_sha256": "1" * 64, "kind": "reserved", "run": "run-one",
            "reservation": None, "profile": "offline", "execution_seconds": None,
            "maximum_seconds": 300, "money_cents": None,
            "paid_dispatch": False, "settled": False, "stop_scope": "unresolved",
            "sources": [source_a],
        }
        event_two = {
            "event_sha256": "2" * 64, "kind": "observation", "run": "run-two",
            "reservation": "reservation-two", "profile": "offline",
            "execution_seconds": 1.25, "maximum_seconds": None,
            "money_cents": None, "paid_dispatch": None, "settled": False,
            "stop_scope": "run", "sources": [source_a, source_b],
        }
        database = root / "budget.sqlite"
        connection = sqlite3.connect(database)
        with connection:
            connection.executescript("""
                CREATE TABLE artifacts(path TEXT PRIMARY KEY, sha256 TEXT NOT NULL, body BLOB NOT NULL);
                CREATE TABLE legacy_events(evidence_key TEXT PRIMARY KEY, body BLOB NOT NULL);
                CREATE TABLE metadata(name TEXT PRIMARY KEY, body BLOB NOT NULL);
                CREATE TABLE reservations(id TEXT PRIMARY KEY);
                CREATE TABLE state(id INTEGER PRIMARY KEY CHECK(id=1), stopped INTEGER NOT NULL CHECK(stopped=1));
                INSERT INTO state VALUES(1,1);
            """)
            connection.execute(
                "INSERT INTO artifacts VALUES(?,?,?)",
                (source_a["path"], source_a["sha256"], sqlite3.Binary(artifact_a)),
            )
            connection.execute(
                "INSERT INTO artifacts VALUES(?,?,?)",
                (source_b["path"], source_b["sha256"], sqlite3.Binary(artifact_b)),
            )
            first = json.dumps(event_one, sort_keys=True, separators=(",", ":")).encode()
            if malformed:
                first = json.dumps({"event_sha256": event_one["event_sha256"]}).encode()
            connection.execute(
                "INSERT INTO legacy_events VALUES(?,?)",
                (event_one["event_sha256"], sqlite3.Binary(first)),
            )
            connection.execute(
                "INSERT INTO legacy_events VALUES(?,?)",
                (event_two["event_sha256"], sqlite3.Binary(
                    json.dumps(event_two, sort_keys=True, separators=(",", ":")).encode()
                )),
            )
        receipt = {
            "campaign": "campaign", "store_id": "store", "schema": "test",
            "proposal_sha256": hashlib.sha256(b"proposal").hexdigest(),
            "migration_safety_stopped": 1, "execution_gate": "blocked",
            "release_authorized": False, "reset_allowance": False,
            "unresolved_history": True,
        }
        receipt_bytes = json.dumps(receipt, sort_keys=True).encode()
        with connection:
            connection.execute(
                "INSERT INTO metadata VALUES('proposal',?)", (sqlite3.Binary(b"proposal"),)
            )
            connection.execute(
                "INSERT INTO metadata VALUES('receipt',?)", (sqlite3.Binary(receipt_bytes),)
            )
        connection.close()
        info = database.stat()
        (root / "receipt.json").write_bytes(receipt_bytes)
        active = {
            "campaign": "campaign", "store_id": "store", "schema": "test",
            "database_sha256": hashlib.sha256(database.read_bytes()).hexdigest(),
            "receipt_sha256": hashlib.sha256(receipt_bytes).hexdigest(),
            "device": info.st_dev, "inode": info.st_ino, "stopped": 1,
            "execution_gate": "blocked", "unresolved_history": True,
        }
        (root / "active.json").write_bytes(json.dumps(active, sort_keys=True).encode())
        active_info = (root / "active.json").stat()
        receipt_info = (root / "receipt.json").stat()
        report_events = [event_one, event_two]
        if duplicate:
            report_events.append(event_two)
        report = {
            "decision": "blocked-ambiguous-history", "all_events": report_events,
            "artifact_sources": {
                source_a["path"]: source_a["sha256"],
                source_b["path"]: source_b["sha256"],
            },
            "installed": {
                "artifact_count": 2,
                "pins_before": {
                    "budget.sqlite": active["database_sha256"],
                    "active.json": hashlib.sha256((root / "active.json").read_bytes()).hexdigest(),
                    "receipt.json": active["receipt_sha256"],
                },
                "pins_after": {}, "campaign": "campaign", "store_id": "store",
            },
        }
        report["installed"]["pins_after"] = dict(report["installed"]["pins_before"])
        report_path = root / "report.json"
        report_path.write_bytes(json.dumps(report, sort_keys=True).encode())
        expected = {
            "active_sha256": active["receipt_sha256"],
            "receipt_sha256": active["receipt_sha256"],
            "prior_report_sha256": hashlib.sha256(report_path.read_bytes()).hexdigest(),
            "database_sha256": active["database_sha256"],
            "database_device": info.st_dev, "database_inode": info.st_ino,
            "database_uid": info.st_uid, "database_gid": info.st_gid,
            "database_mode": info.st_mode, "database_nlink": info.st_nlink,
            "active_device": active_info.st_dev, "active_inode": active_info.st_ino,
            "active_uid": active_info.st_uid, "active_gid": active_info.st_gid,
            "active_mode": active_info.st_mode, "active_nlink": active_info.st_nlink,
            "receipt_device": receipt_info.st_dev, "receipt_inode": receipt_info.st_ino,
            "receipt_uid": receipt_info.st_uid, "receipt_gid": receipt_info.st_gid,
            "receipt_mode": receipt_info.st_mode, "receipt_nlink": receipt_info.st_nlink,
            "artifact_count": 2, "event_count": 2,
        }
        expected["active_sha256"] = hashlib.sha256((root / "active.json").read_bytes()).hexdigest()
        return root, database, report_path, expected

    def collect(self, root, database, report, expected, name="MANIFEST.json"):
        output = root / name
        manifest = MODULE["manifest_for"](database, report, output, expected)
        return manifest, output

    def test_exact_inventory_and_correspondence(self):
        root, database, report, expected = self.make_fixture()
        manifest, output = self.collect(root, database, report, expected)
        self.assertEqual(manifest["schema_version"], 1)
        self.assertEqual(manifest["decision"], "blocked-ambiguous-history")
        self.assertEqual(manifest["summary"]["artifact_count"], 2)
        self.assertEqual(manifest["summary"]["event_count"], 2)
        self.assertEqual(manifest["summary"]["event_kind_counts"],
                         {"reserved": 1, "observation": 1})
        self.assertEqual(manifest["summary"]["event_source_reference_count"], 3)
        self.assertTrue(all(row["hash_matches"] for row in manifest["artifacts"]))
        self.assertEqual([row["evidence_key"] for row in manifest["events"]], ["1" * 64, "2" * 64])
        parsed = json.loads(output.read_text())
        self.assertEqual(parsed, manifest)

    def test_source_hash_mismatch_is_rejected_before_readback(self):
        root, database, report, expected = self.make_fixture()
        expected["database_sha256"] = "0" * 64
        with self.assertRaises(MODULE["EvidenceFailure"]):
            self.collect(root, database, report, expected)
        self.assertFalse((root / "MANIFEST.json").exists())

    def test_missing_required_evidence_is_explicit_null(self):
        root, database, report, expected = self.make_fixture()
        manifest, _ = self.collect(root, database, report, expected)
        reserved = manifest["events"][0]["required_evidence"]
        for field in ("principal", "request_key", "stage", "currency",
                      "start_interval", "end_interval", "overlap_interval",
                      "trusted_meter_receipt", "trusted_settlement_receipt"):
            self.assertEqual(reserved[field], {
                "status": "missing", "value": None,
                "basis": "not present in preserved event; not inferred",
            })
        self.assertIsNone(manifest["events"][0]["scalar_fields"]["money_cents"])
        self.assertEqual(manifest["summary"]["missing_required_evidence_event_counts"]["principal"], 2)

    def test_collection_does_not_mutate_protected_fixture(self):
        root, database, report, expected = self.make_fixture()
        before = {path.name: (path.read_bytes(), path.stat().st_mtime_ns)
                  for path in root.iterdir() if path.is_file()}
        self.collect(root, database, report, expected)
        after = {path.name: (path.read_bytes(), path.stat().st_mtime_ns)
                 for path in root.iterdir() if path.is_file() and path.name != "MANIFEST.json"}
        self.assertEqual(before, after)
        self.assertEqual(set(after), {"active.json", "budget.sqlite", "receipt.json", "report.json"})

    def test_duplicate_prior_event_is_rejected(self):
        root, database, report, expected = self.make_fixture(duplicate=True)
        with self.assertRaises(MODULE["EvidenceFailure"]):
            self.collect(root, database, report, expected)

    def test_malformed_event_is_rejected(self):
        root, database, report, expected = self.make_fixture(malformed=True)
        expected["database_sha256"] = hashlib.sha256(database.read_bytes()).hexdigest()
        with self.assertRaises(MODULE["EvidenceFailure"]):
            self.collect(root, database, report, expected)


if __name__ == "__main__":
    unittest.main()
