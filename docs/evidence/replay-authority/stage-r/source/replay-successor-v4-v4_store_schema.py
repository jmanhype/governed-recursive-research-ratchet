"""Stopped empty v4 store schema used only in a caller-approved sandbox."""

from contextlib import closing
import json
import os
from pathlib import Path
import sqlite3


CAMPAIGN = "GRRR-REPLAY-SUCCESSOR-POC-2"
STORE_ID = "unissued-independent-replay-v4"
PRIOR_HISTORY_RECEIPT = (
    "6d3d5b092c0ee8273a657c83823d8465b215f2b1b66ec627dfde2d96b21fe587"
)
TABLE_SQL = {
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


def create_store(path: Path) -> dict:
    """Create a fresh stopped store and return its physical identity."""
    path.parent.mkdir(mode=0o700, parents=False, exist_ok=False)
    with closing(sqlite3.connect(path, isolation_level=None)) as db:
        db.execute("PRAGMA journal_mode=DELETE")
        db.execute("PRAGMA synchronous=FULL")
        for ddl in TABLE_SQL.values():
            db.execute(ddl)
        db.execute("INSERT INTO state VALUES(1,1)")
        db.execute(
            "INSERT INTO store_identity VALUES(?,?,?)",
            (CAMPAIGN, STORE_ID, PRIOR_HISTORY_RECEIPT),
        )
    os.chmod(path, 0o600)
    info = path.lstat()
    return {"device": info.st_dev, "inode": info.st_ino}
