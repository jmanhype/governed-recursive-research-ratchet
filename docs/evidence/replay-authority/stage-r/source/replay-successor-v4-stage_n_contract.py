"""Standalone Stage N authority constants for the v4 source bundle."""

import json
import re


DECISION = "candidate-fresh-replay-successor-poc"
PROFILE = "independent-replay"
MODES = ("normal", "failed-rebuild", "interruption", "two-failures")
HOLD_IDS = (
    "69523b39a51c44739114313c9325028c",
    "b34d8b9d106e42eab3a3e43daac98ddd",
    "d375ce6a2d924646bec71df64e939a5b",
)
PREDECESSOR_ACTIVE_SHA256 = (
    "9c5194dd12ff7601917fcccc293c459db09a41da8bad9fa9983cbef618d453f8"
)
PREDECESSOR_DATABASE_SHA256 = (
    "9c6ff2561a364ed982cd5477dd4b200c995da6910c9a17aa3d3c411a962d64f3"
)
PREDECESSOR_RECOVERY_SHA256 = (
    "6d3d5b092c0ee8273a657c83823d8465b215f2b1b66ec627dfde2d96b21fe587"
)
SESSION_EXECUTION_US = 480_000_000
AGGREGATE_EXECUTION_US = SESSION_EXECUTION_US * len(MODES)
MAXIMUM_GUEST_LAUNCHES = 12
HASH_RE = re.compile(r"[0-9a-f]{64}\Z")


def contract() -> dict:
    return {
        "decision": DECISION,
        "profile": PROFILE,
        "modes": list(MODES),
        "session_execution_us": SESSION_EXECUTION_US,
        "aggregate_execution_us": AGGREGATE_EXECUTION_US,
        "maximum_guest_launches": MAXIMUM_GUEST_LAUNCHES,
        "predecessor": {
            "active_sha256": PREDECESSOR_ACTIVE_SHA256,
            "database_sha256": PREDECESSOR_DATABASE_SHA256,
            "recovery_sha256": PREDECESSOR_RECOVERY_SHA256,
            "spendable": None,
            "history_status": "unresolved",
            "all_original_ceilings_encumbered": True,
        },
        "unresolved_holds": list(HOLD_IDS),
        "spendable": None,
        "authority": False,
    }


def validate(value: dict) -> dict:
    required = {
        "decision", "profile", "modes", "session_execution_us",
        "aggregate_execution_us", "maximum_guest_launches", "spendable",
        "predecessor", "unresolved_holds", "authority",
    }
    if not isinstance(value, dict) or set(value) != required:
        raise ValueError("Stage N source contract fields differ")
    if value != contract():
        raise ValueError("Stage N source contract differs")
    return value


def canonical(value: dict) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
        allow_nan=False,
    ).encode("ascii")
