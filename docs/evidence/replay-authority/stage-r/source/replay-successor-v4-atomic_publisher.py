"""Exclusive, fsynced publication helpers for sandbox artifacts only."""

import os
from pathlib import Path


def write_exclusive(path: Path, raw: bytes, mode: int) -> None:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW
    with os.fdopen(os.open(path, flags, mode), "wb") as stream:
        stream.write(raw)
        os.fchmod(stream.fileno(), mode)
        stream.flush()
        os.fsync(stream.fileno())


def sync_directory(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def publish_pair(directory: Path, receipt_name: str, receipt: bytes,
                 active_name: str, active: bytes) -> None:
    write_exclusive(directory / receipt_name, receipt, 0o400)
    write_exclusive(directory / active_name, active, 0o400)
    sync_directory(directory)
