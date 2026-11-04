"""Equal-budget selector comparison over the frozen vlt corpus.

Implements deterministic, random, and Jev-guided selection arms.
Jev requires an operator-provisioned external adapter; without it,
the arm is honestly reported unavailable and the three-arm comparison
is incomplete, per AC #4.
"""

import hashlib
import json
import random
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import jev_adapter


SCHEMA_VERSION = 1
CORPUS_FREEZE_DIGEST = (
    "dfa75ef2bf3d43fd4f750094fe643afe4f204812c0ae2426276bedb471fa8529"
)
DEFAULT_CORPUS_ROOT = Path(__file__).resolve().parent.parent / "corpus"

ARMS = ("deterministic", "random", "jev")


class SelectorError(ValueError):
    """Raised when selector validation fails."""


def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("ascii")


def _digest(value):
    return hashlib.sha256(_canonical(value)).hexdigest()


def _unique_fields(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON field")
        result[key] = value
    return result


def _load_json(path: Path) -> Tuple[Any, bytes]:
    try:
        raw = path.read_bytes()
        value = json.loads(
            raw,
            object_pairs_hook=_unique_fields,
            parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)),
        )
        return value, raw
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise SelectorError(f"could not load valid JSON: {path.name}") from exc


def _validated_ids(value: Any, label: str) -> List[str]:
    if (not isinstance(value, list) or not value
            or not all(isinstance(item, str) and item for item in value)
            or len(value) != len(set(value))):
        raise SelectorError(f"{label} must be a non-empty list of unique IDs")
    return value


def _verified_freeze_digest(manifest: Dict[str, Any]) -> str:
    """Verify the manifest against its canonical frozen digest."""
    freeze_digest = manifest.get("freeze_digest")
    if freeze_digest != CORPUS_FREEZE_DIGEST:
        raise SelectorError("corpus freeze digest does not match the frozen selector corpus")
    frozen = {key: value for key, value in manifest.items() if key != "freeze_digest"}
    if _digest(frozen) != freeze_digest:
        raise SelectorError("corpus manifest fails canonical freeze self-verification")
    return freeze_digest


def _load_frozen_projection(root: Path) -> Tuple[str, List[str], List[Dict]]:
    """Load an artifact-byte-bound manifest/public projection.

    A matching manifest ID list alone is declarative and insufficient. The
    public projection is hashed exactly as stored, then its membership must
    equal the manifest catalog exactly.
    """
    manifest, _ = _load_json(root / "manifest.json")
    if not isinstance(manifest, dict):
        raise SelectorError("corpus manifest must be an object")
    freeze_digest = _verified_freeze_digest(manifest)
    manifest_ids = _validated_ids(
        manifest.get("challenge_ids"), "manifest catalog"
    )

    artifacts = manifest.get("artifacts")
    artifact_name = "public/challenges.json"
    if not isinstance(artifacts, dict):
        raise SelectorError("corpus manifest artifacts must be an object")
    expected_hash = artifacts.get(artifact_name)
    if (not isinstance(expected_hash, str)
            or re.fullmatch(r"[0-9a-f]{64}", expected_hash) is None):
        raise SelectorError("public challenges artifact hash is invalid")

    public, public_raw = _load_json(root / "public" / "challenges.json")
    if not isinstance(public, list) or not public:
        raise SelectorError("public challenges projection must be a non-empty list")
    if not all(isinstance(item, dict) for item in public):
        raise SelectorError("public challenge entries must be objects")
    public_ids = [item.get("challenge") for item in public]
    if not all(isinstance(item, str) for item in public_ids):
        raise SelectorError("public challenge IDs must be strings")
    if len(public_ids) != len(set(public_ids)):
        raise SelectorError("public challenges projection contains duplicate IDs")
    if hashlib.sha256(public_raw).hexdigest() != expected_hash:
        raise SelectorError("public challenges bytes do not match manifest hash")
    if set(manifest_ids) != set(public_ids):
        raise SelectorError("manifest and public challenge memberships differ")
    return freeze_digest, manifest_ids, public


def load_catalog(corpus_path: Path) -> List[str]:
    """Load the byte-bound public catalog from the corpus manifest."""
    return _load_frozen_projection(corpus_path)[1]


def _validate_catalog_and_budget(catalog: List[str], budget: int, seed: int) -> None:
    if (not isinstance(catalog, list) or not catalog
            or not all(isinstance(item, str) and item for item in catalog)
            or len(catalog) != len(set(catalog))):
        raise SelectorError("catalog must be a non-empty list of unique IDs")
    if (not isinstance(budget, int) or isinstance(budget, bool)
            or not 0 <= budget <= len(catalog)):
        raise SelectorError("budget must be an integer between zero and catalog size")
    if not isinstance(seed, int) or isinstance(seed, bool):
        raise SelectorError("seed must be an integer")


def deterministic_select(catalog: List[str], budget: int, seed: int = 0) -> Dict:
    """Deterministic risk-based selection: lexical order under fixed budget."""
    _validate_catalog_and_budget(catalog, budget, seed)
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
    _validate_catalog_and_budget(catalog, budget, seed)
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


def jev_select(
    catalog: List[str],
    budget: int,
    seed: int = 0,
    corpus_path: Optional[Path] = None,
    transport=None,
) -> Dict:
    """Jev-guided selection via the operator-provisioned TypeSafe broker.

    Returns the probabilistically ranked head of the catalog. The result is a
    recommendation, never a verified finding; callers must not treat a high
    score as evidence that a defect exists.
    """
    _validate_catalog_and_budget(catalog, budget, seed)
    if not jev_adapter.is_available():
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

    root = Path(corpus_path) if corpus_path is not None else DEFAULT_CORPUS_ROOT
    freeze_digest, manifest_ids, public = _load_frozen_projection(root)
    if set(catalog) != set(manifest_ids):
        missing = sorted(set(manifest_ids) - set(catalog))
        invented = sorted(set(catalog) - set(manifest_ids))
        raise SelectorError(
            "catalog membership differs from the frozen corpus "
            f"(missing: {missing[:5]}, invented: {invented[:5]})"
        )

    ranked = jev_adapter.rank_challenges(
        public,
        corpus_freeze_digest=freeze_digest,
        transport=transport,
    )
    selected = [item["challenge"] for item in ranked[:budget]]

    return {
        "arm": "jev",
        "selector_version": "1.1.0",
        "seed": seed,
        "catalog_size": len(catalog),
        "budget": budget,
        "selected": selected,
        "available": True,
        "provenance": "typesafe-jev-expected-defect-weight",
        "recommendation_only": True,
        "model": sorted({item["model"] for item in ranked if item.get("model")}),
        "usage": {
            "input_tokens": sum(item["usage"].get("input_tokens", 0) for item in ranked),
            "output_tokens": sum(item["usage"].get("output_tokens", 0) for item in ranked),
        },
        "ranking": [
            {
                "challenge": item["challenge"],
                "expected_defect_weight": round(item["expected_defect_weight"], 6),
                "score": item["score"],
                "confidence": item["confidence"],
            }
            for item in ranked
        ],
    }


def run_comparison(
    catalog: List[str],
    budget: int,
    seed: int = 42,
    corpus_path: Optional[Path] = None,
    transport=None,
) -> Dict:
    """Run all three arms under equal budget."""
    _validate_catalog_and_budget(catalog, budget, seed)
    results = {
        "deterministic": deterministic_select(catalog, budget, 0),
        "random": random_select(catalog, budget, seed),
        "jev": jev_select(
            catalog,
            budget,
            seed,
            corpus_path=corpus_path,
            transport=transport,
        ),
    }
    jev_available = bool(results["jev"].get("available"))
    return {
        "schema_version": SCHEMA_VERSION,
        "corpus_freeze_digest": CORPUS_FREEZE_DIGEST,
        "budget_per_arm": budget,
        "seed": seed,
        "arms": results,
        "jev_available": jev_available,
        "comparison_complete": jev_available,
        "outcome": "incomplete-jev-unavailable" if not jev_available else "complete",
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
