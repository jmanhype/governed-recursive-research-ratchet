"""Exact postflight verification for a stopped sandbox v4 store."""

from contextlib import closing
import hashlib
import importlib.util
import sqlite3
from pathlib import Path


def _schema_module():
    """Load the exact hyphen-named sibling without changing sys.path."""
    path = Path(__file__).with_name(
        "replay-successor-v4-v4_store_schema.py")
    spec = importlib.util.spec_from_file_location(
        "replay_successor_v4_v4_store_schema", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_SCHEMA = _schema_module()
CAMPAIGN = _SCHEMA.CAMPAIGN
EXPECTED_OBJECTS = _SCHEMA.EXPECTED_OBJECTS
PRIOR_HISTORY_RECEIPT = _SCHEMA.PRIOR_HISTORY_RECEIPT
STORE_ID = _SCHEMA.STORE_ID
TABLE_SQL = _SCHEMA.TABLE_SQL


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def verify(database: Path, expected_hash: str,
           identity: tuple[int, int]) -> dict:
    if sha256(database.read_bytes()) != expected_hash:
        raise ValueError("sandbox database hash differs")
    info = database.lstat()
    if (info.st_dev, info.st_ino) != identity:
        raise ValueError("sandbox database identity differs")
    with closing(sqlite3.connect(database.as_uri() + "?mode=ro", uri=True)) as db:
        if db.execute("PRAGMA integrity_check").fetchall() != [("ok",)]:
            raise ValueError("sandbox database integrity differs")
        if db.execute("PRAGMA journal_mode").fetchall() != [("delete",)]:
            raise ValueError("sandbox database journal differs")
        objects = {tuple(row) for row in db.execute(
            "SELECT type,name,tbl_name FROM sqlite_master")}
        if objects != EXPECTED_OBJECTS:
            raise ValueError("sandbox database objects differ")
        ddl = {row[0]: row[1] for row in db.execute(
            "SELECT name,sql FROM sqlite_master WHERE type='table'")}
        if ddl != TABLE_SQL:
            raise ValueError("sandbox database schema differs")
        if db.execute("SELECT id,stopped FROM state").fetchall() != [(1, 1)]:
            raise ValueError("sandbox store is not stopped")
        identity_row = db.execute(
            "SELECT campaign,store_id,prior_history_receipt FROM store_identity"
        ).fetchall()
        if identity_row != [(CAMPAIGN, STORE_ID, PRIOR_HISTORY_RECEIPT)]:
            raise ValueError("sandbox store identity differs")
        for table in ("reservations", "metering", "overhead"):
            if db.execute("SELECT * FROM " + table).fetchall() != []:
                raise ValueError("sandbox accounting table is not empty")
    return {"stopped": True, "empty": True, "verified": True}
