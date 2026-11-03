"""Equal-budget selector comparison over the frozen vlt corpus.

Implements deterministic, random, and Jev-guided selection arms.
Jev requires an operator-provisioned external adapter; without it,
the arm is honestly reported unavailable and the three-arm comparison
is incomplete, per AC #4.
"""

import hashlib
import json
import random
from pathlib import Path
from typing import Dict, List, Optional


SCHEMA_VERSION = 1
CORPUS_FREEZE_DIGEST = (
    "dfa75ef2bf3d43fd4f750094fe643afe4f204812c0ae2426276bedb471fa8529"
)
JEV_AVAILABLE = False  # No operator-provisioned adapter exists

ARMS = ("deterministic", "random", "jev")


class SelectorError(ValueError):
    """Raised when selector validation fails."""


def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("ascii")


def _digest(value):
    return hashlib.sha256(_canonical(value)).hexdigest()


def load_catalog(corpus_path: Path) -> List[str]:
    """Load public challenge IDs from the corpus manifest."""
    manifest = json.loads((corpus_path / "manifest.json").read_bytes())
    ids = manifest.get("challenge_ids", [])
    if not isinstance(ids, list) or not all(isinstance(i, str) for i in ids):
        raise SelectorError("catalog must be a list of challenge ID strings")
    if len(ids) != len(set(ids)):
        raise SelectorError("catalog contains duplicate challenge IDs")
    return ids


def deterministic_select(catalog: List[str], budget: int, seed: int = 0) -> Dict:
    """Deterministic risk-based selection: lexical order under fixed budget."""
    ranked = sorted(catalog)
    selected = ranked[:budget]
    return {
        "arm": "deterministic",
        "selector_version": "1.0.0",
        "seed": seed,
        "catalog_size": len(catalog),
        "budget": budget,
        "selected": selected,
        "provenance": "lexical-order-under-budget",
    }


def random_select(catalog: List[str], budget: int, seed: int = 42) -> Dict:
    """Random selection with reproducible seed."""
    rng = random.Random(seed)
    ranked = list(catalog)
    rng.shuffle(ranked)
    selected = ranked[:budget]
    return {
        "arm": "random",
        "selector_version": "1.0.0",
        "seed": seed,
        "catalog_size": len(catalog),
        "budget": budget,
        "selected": selected,
        "provenance": "seeded-shuffle-under-budget",
    }


def jev_select(catalog: List[str], budget: int, seed: int = 0) -> Dict:
    """Jev-guided selection. Requires operator-provisioned adapter."""
    if not JEV_AVAILABLE:
        return {
            "arm": "jev",
            "selector_version": None,
            "seed": None,
            "catalog_size": len(catalog),
            "budget": budget,
            "selected": [],
            "available": False,
            "reason": "No operator-provisioned Jev adapter available; arm unavailable",
            "provenance": "unavailable",
        }
    raise SelectorError("Jev adapter not implemented")


def run_comparison(catalog: List[str], budget: int, seed: int = 42) -> Dict:
    """Run all three arms under equal budget."""
    results = {
        "deterministic": deterministic_select(catalog, budget, 0),
        "random": random_select(catalog, budget, seed),
        "jev": jev_select(catalog, budget, seed),
    }
    return {
        "schema_version": SCHEMA_VERSION,
        "corpus_freeze_digest": CORPUS_FREEZE_DIGEST,
        "budget_per_arm": budget,
        "seed": seed,
        "arms": results,
        "jev_available": JEV_AVAILABLE,
        "comparison_complete": JEV_AVAILABLE,
        "outcome": "incomplete-jev-unavailable" if not JEV_AVAILABLE else "complete",
    }


def validate_selections(value: Dict) -> Dict:
    """Validate that selections are well-formed and non-overlapping within arms."""
    if not isinstance(value, dict) or set(value) != set(ARMS):
        raise SelectorError("must have exactly three arms")
    for arm in ARMS:
        selection = value[arm]
        if not isinstance(selection, dict):
            raise SelectorError(f"{arm} selection must be dict")
        ids = selection.get("selected", [])
        if not isinstance(ids, list):
            raise SelectorError(f"{arm} selected must be list")
        if len(ids) != len(set(ids)):
            raise SelectorError(f"{arm} has duplicate selections")
        if arm == "jev" and not selection.get("available", False):
            if ids:
                raise SelectorError("unavailable Jev must not select anything")
    return value
