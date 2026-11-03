"""Uncertainty-dominant failure evidence for a sandbox v4 publication."""

import json
import os
from pathlib import Path


def preserve(target: Path, authorization_sha256: str, detail: str) -> dict:
    target.mkdir(mode=0o700, parents=False, exist_ok=True)
    value = {
        "schema_version": 1,
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
    raw = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
        allow_nan=False,
    ).encode("ascii")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW
    with os.fdopen(os.open(target / "uncertain.json", flags, 0o400), "wb") as stream:
        stream.write(raw)
        os.fchmod(stream.fileno(), 0o400)
        stream.flush()
        os.fsync(stream.fileno())
    descriptor = os.open(target, os.O_RDONLY | os.O_NOFOLLOW)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
    return value
