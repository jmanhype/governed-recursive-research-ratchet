"""Strict loader for the proposed, not-yet-approved three-arm evaluation plan."""

import json
import hashlib
from pathlib import Path
from typing import Any, Dict, Tuple


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_PLAN_PATH = ROOT / "corpus" / "evaluation-plan-v2-proposed.json"
EXPECTED_PLAN_SHA256 = (
    "97ec4b8ccc34b3fc4da4fcfbef33b49bbb3f4f1c445cfecdb752715ddf034be1"
)
EXPECTED_PLAN_SIZE = 6904
EXPECTED_TOP_LEVEL = {
    "schema_version", "plan_id", "state", "approval", "corpus",
    "prior_evidence", "arms", "budget", "metrics", "uncertainty",
    "decision_rule", "privacy", "failure", "review",
}


class EvaluationPlanError(ValueError):
    """The proposed evaluation plan does not match its pre-registered schema."""


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON field")
        result[key] = value
    return result


def _exact_keys(value: Any, expected: set, label: str) -> Dict:
    if not isinstance(value, dict) or set(value) != expected:
        raise EvaluationPlanError(f"{label} fields differ")
    return value


def _exact_int(value: Any, expected: int, label: str) -> None:
    if type(value) is not int or value != expected:
        raise EvaluationPlanError(f"{label} differs")


def _exact_equal(left: Any, right: Any) -> bool:
    if type(left) is not type(right):
        return False
    if isinstance(left, dict):
        return (set(left) == set(right)
                and all(_exact_equal(left[key], right[key]) for key in left))
    if isinstance(left, list):
        return (len(left) == len(right)
                and all(_exact_equal(a, b) for a, b in zip(left, right)))
    return left == right


def validate_plan(plan: Any, raw: bytes) -> Dict:
    """Require the exact reviewed design bytes and parsed object shape.

    The byte pin is intentional: every semantic value, type, ordering, and
    spelling in the pre-registered JSON is part of the design. A semantic
    change requires a new hash and fresh independent review.
    """
    if (not isinstance(raw, bytes) or len(raw) != EXPECTED_PLAN_SIZE
            or hashlib.sha256(raw).hexdigest() != EXPECTED_PLAN_SHA256):
        raise EvaluationPlanError("proposed evaluation plan bytes differ")
    try:
        parsed_from_raw = json.loads(
            raw,
            object_pairs_hook=_unique_object,
            parse_constant=lambda item: (_ for _ in ()).throw(ValueError(item)),
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise EvaluationPlanError("proposed evaluation plan bytes are invalid") from exc
    if not _exact_equal(parsed_from_raw, plan):
        raise EvaluationPlanError("parsed plan does not match reviewed bytes")
    root = _exact_keys(plan, EXPECTED_TOP_LEVEL, "top-level")
    return root


def load_plan(path: Path = DEFAULT_PLAN_PATH) -> Tuple[Dict, bytes]:
    try:
        raw = Path(path).read_bytes()
        value = json.loads(
            raw,
            object_pairs_hook=_unique_object,
            parse_constant=lambda item: (_ for _ in ()).throw(ValueError(item)),
        )
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise EvaluationPlanError("proposed evaluation plan is invalid JSON") from exc
    return validate_plan(value, raw), raw
