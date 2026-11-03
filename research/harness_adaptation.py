"""One deterministic, repository-only Harness adaptation cycle.

The cycle is deliberately bounded: bind immutable inputs, evaluate only two
pre-registered proposals, and compose nothing unless a non-leaking candidate
beats the measured random benchmark. It never executes a selected challenge.
"""

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

import evaluation_plan_v2
import selector_comparison


EXPECTED_RESULT_SHA256 = "b7bb2ec8717e8921e16f9a3e312f6ad46839a125634dc6e3d144499cc841fefb"
EXPECTED_TRUTH_SHA256 = "7cf9f99f5836c4e3e147df2866d54480a706f2665a732fbf61bd1a0d0b4c52ea"
EXPECTED_MANIFEST_SHA256 = "32fb59c74ea96653c50e3deea0d66474bafdd78caf96c3e9c4c589aba703e354"
EXPECTED_PUBLIC_PROJECTION_SHA256 = "c6aa57a2eb595fd2fe35ae817295df2220738b8538755826c5af11af648fd361"
EXPECTED_CORPUS_VERSION = "GRRR-validated-corpus-v2.2-isolated"
EXPECTED_CORPUS_FREEZE_DIGEST = selector_comparison.CORPUS_FREEZE_DIGEST
EXPECTED_RANDOM_MEAN = 6.0
FIXED_RANDOM_SEEDS = (45, 46, 47)
BUDGET = 8
RESULT_FIELDS = {
    "schema_version", "status", "evaluation_scope", "design_sha256",
    "protected_truth_sha256", "arms", "decision", "usage", "jev_run_ids",
    "not_claims",
}
DECISION_FIELDS = {
    "pre_registered_default", "jev_wins", "outcome", "measured_leading_arm",
    "permitted_claim",
}
TRUTH_ROW_FIELDS = {"challenge", "truth", "critical", "expected_behavior"}
FORBIDDEN_OUTPUT_MARKERS = (
    "expected_behavior", "raw provider response", "/library/grrr"
)


class AdaptationCycleError(RuntimeError):
    """Raised instead of weakening a bound or safety gate."""


def _unique_object(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError("Duplicate JSON field")
        value[key] = item
    return value


def _load_json(path: Path) -> Tuple[Any, bytes]:
    try:
        raw = path.read_bytes()
        value = json.loads(
            raw,
            object_pairs_hook=_unique_object,
            parse_constant=lambda item: (_ for _ in ()).throw(ValueError(item)),
        )
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise AdaptationCycleError(f"invalid JSON input: {path.name}") from exc
    return value, raw


def _sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AdaptationCycleError(message)


def _validate_result_identity(value: Dict[str, Any]) -> None:
    _require(
        value["schema_version"] == 1 and value["status"] == "complete"
        and value["evaluation_scope"] == "selector-quality-only"
        and value["design_sha256"] == evaluation_plan_v2.EXPECTED_PLAN_SHA256
        and value["protected_truth_sha256"] == EXPECTED_TRUTH_SHA256,
        "completed result identity differs",
    )


def _validate_result_decision(value: Dict[str, Any]) -> None:
    decision = value["decision"]
    _require(
        isinstance(decision, dict) and set(decision) == DECISION_FIELDS
        and decision["jev_wins"] is False
        and decision["outcome"] == "inconclusive-jev-did-not-win"
        and decision["pre_registered_default"] == "retain-deterministic-lexical-baseline",
        "completed decision differs",
    )


def _validate_random_benchmark(value: Dict[str, Any]) -> None:
    arm = value["arms"].get("random") if isinstance(value["arms"], dict) else None
    values = arm.get("primary_repetition_values") if isinstance(arm, dict) else None
    mean = arm.get("primary_mean") if isinstance(arm, dict) else None
    _require(
        isinstance(values, list) and len(values) == 3
        and all(type(item) in (int, float) for item in values)
        and sum(values) == 18 and type(mean) in (int, float)
        and mean == EXPECTED_RANDOM_MEAN,
        "random benchmark mean differs",
    )


def _validate_completed_result(value: Any, raw: bytes) -> Dict[str, Any]:
    if _sha256(raw) != EXPECTED_RESULT_SHA256:
        raise AdaptationCycleError("completed three-arm result bytes differ")
    if not isinstance(value, dict) or set(value) != RESULT_FIELDS:
        raise AdaptationCycleError("completed result schema differs")
    _validate_result_identity(value)
    _validate_result_decision(value)
    _validate_random_benchmark(value)
    return value


def _load_trusted_truth(corpus_root: Path) -> Tuple[Dict[str, Dict[str, Any]], bytes]:
    value, raw = _load_json(corpus_root / "protected" / "truth.json")
    if _sha256(raw) != EXPECTED_TRUTH_SHA256:
        raise AdaptationCycleError("protected truth bytes differ")
    if (not isinstance(value, list) or len(value) != 32
            or not all(isinstance(row, dict) and set(row) == TRUTH_ROW_FIELDS
                       for row in value)):
        raise AdaptationCycleError("protected truth schema differs")
    truth = {}
    for row in value:
        challenge = row["challenge"]
        if (not isinstance(challenge, str) or challenge in truth
                or row["truth"] not in {"defect", "clean"}
                or type(row["critical"]) is not bool
                or not isinstance(row["expected_behavior"], str)):
            raise AdaptationCycleError("protected truth mapping differs")
        truth[challenge] = row
    return truth, raw


def _load_frozen_corpus(corpus_root: Path, truth: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    try:
        catalog = selector_comparison.load_catalog(corpus_root)
    except selector_comparison.SelectorError as exc:
        raise AdaptationCycleError("frozen corpus validation failed") from exc
    if len(catalog) != 32 or set(catalog) != set(truth):
        raise AdaptationCycleError("catalog and trusted truth memberships differ")
    manifest_raw = (corpus_root / "manifest.json").read_bytes()
    public_raw = (corpus_root / "public" / "challenges.json").read_bytes()
    manifest = json.loads(manifest_raw)
    if (manifest.get("corpus_version") != EXPECTED_CORPUS_VERSION
            or manifest.get("freeze_digest") != EXPECTED_CORPUS_FREEZE_DIGEST
            or manifest.get("artifacts", {}).get("public/challenges.json")
            != _sha256(public_raw)
            or _sha256(manifest_raw) != EXPECTED_MANIFEST_SHA256
            or _sha256(public_raw) != EXPECTED_PUBLIC_PROJECTION_SHA256):
        raise AdaptationCycleError("frozen corpus identity differs")
    return {
        "catalog": catalog,
        "manifest_sha256": EXPECTED_MANIFEST_SHA256,
        "public_projection_sha256": EXPECTED_PUBLIC_PROJECTION_SHA256,
    }


def _selection_metrics(
    selected: Any, catalog: Sequence[str], truth: Dict[str, Dict[str, Any]]
) -> Dict[str, int]:
    if (not isinstance(selected, list) or len(selected) != BUDGET
            or not all(isinstance(item, str) for item in selected)
            or len(selected) != len(set(selected))
            or not set(selected) <= set(catalog)):
        raise AdaptationCycleError("malformed selection")
    return {
        "defect_count": sum(
            truth[item]["truth"] == "defect" for item in selected
        ),
        "critical_count": sum(
            truth[item]["truth"] == "defect" and truth[item]["critical"] is True
            for item in selected
        ),
        "clean_count": sum(truth[item]["truth"] == "clean" for item in selected),
    }


def _leakage_verdict(
    leakage_inputs: Any, selected: Sequence[str], catalog: Sequence[str]
) -> Dict[str, Any]:
    if not isinstance(leakage_inputs, list) or not all(isinstance(item, str) for item in leakage_inputs):
        raise AdaptationCycleError("malformed candidate leakage declaration")
    detected = (
        selected == sorted(catalog, reverse=True)[:BUDGET]
    )
    inputs = sorted(set(leakage_inputs) | {"D/C-local-ID-prefix"} if detected else set(leakage_inputs))
    rejected = bool(inputs)
    return {
        "rejected": rejected,
        "inputs": inputs,
        "reason": (
            "D/C local-ID prefix signal was declared or deterministically detected; "
            "the measured score cannot override leakage"
        ) if rejected else "no forbidden candidate input declared or detected",
        "score_may_override": False,
    }


def evaluate_candidate(
    candidate: Dict[str, Any], catalog: Sequence[str],
    truth: Dict[str, Dict[str, Any]],
) -> Dict[str, Any]:
    """Evaluate one declared candidate against the trusted truth mapping."""
    if not isinstance(candidate, dict) or not isinstance(
        candidate.get("selected"), list
    ):
        raise AdaptationCycleError("malformed candidate selection")
    metrics = _selection_metrics(candidate["selected"], catalog, truth)
    leakage = _leakage_verdict(
        candidate.get("leakage_inputs"), candidate["selected"], catalog
    )
    return {
        "metrics": metrics,
        "leakage": leakage,
        "eligible": not leakage["rejected"],
    }


def _reverse_result(catalog: Sequence[str], truth: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    candidate = {
        "selected": sorted(catalog, reverse=True)[:BUDGET],
        "leakage_inputs": ["D/C-local-ID-prefix"],
    }
    evaluated = evaluate_candidate(candidate, catalog, truth)
    metrics = evaluated["metrics"]
    return {
        "proposal_id": "reverse-lexical",
        "fixed": True,
        "selection_rule": "reverse-lexical-under-budget",
        "selected_ids": candidate["selected"],
        "measured": {
            "primary_true_defects": metrics["defect_count"],
            "primary_mean": float(metrics["defect_count"]),
            "critical_mean": float(metrics["critical_count"]),
            "clean_mean": float(metrics["clean_count"]),
            "unique_defect_count": metrics["defect_count"],
        },
        "leakage": evaluated["leakage"],
        "eligible": evaluated["eligible"],
        "score_note": "8/8 recorded and rejected; leakage is decisive",
    }


def _random_block_result(
    catalog: Sequence[str], truth: Dict[str, Dict[str, Any]]
) -> Dict[str, Any]:
    repetitions = []
    all_defects = set()
    for seed in FIXED_RANDOM_SEEDS:
        selected = selector_comparison.random_select(
            list(catalog), BUDGET, seed=seed
        )["selected"]
        metrics = _selection_metrics(selected, catalog, truth)
        repetitions.append({
            "seed": seed,
            "selected_ids": selected,
            "true_defect_count": metrics["defect_count"],
            "critical_count": metrics["critical_count"],
            "clean_count": metrics["clean_count"],
        })
        all_defects.update(item for item in selected if truth[item]["truth"] == "defect")
    defect_total = sum(item["true_defect_count"] for item in repetitions)
    critical_total = sum(item["critical_count"] for item in repetitions)
    clean_total = sum(item["clean_count"] for item in repetitions)
    count = len(repetitions)
    repetition_verdicts = [
        _leakage_verdict([], repetition["selected_ids"], catalog)
        for repetition in repetitions
    ]
    repetition_inputs = {
        item for verdict in repetition_verdicts for item in verdict["inputs"]
    }
    return {
        "proposal_id": "random-block-45-46-47",
        "fixed": True,
        "selection_rule": "seeded-shuffle-full-block",
        "seeds": list(FIXED_RANDOM_SEEDS),
        "selection_mode": "evaluate-all-repetitions",
        "repetitions": repetitions,
        "measured": {
            "primary_mean": round(defect_total / count, 6),
            "critical_mean": round(critical_total / count, 6),
            "clean_mean": round(clean_total / count, 6),
            "unique_defect_count": len(all_defects),
        },
        "leakage": {
            "rejected": bool(repetition_inputs),
            "inputs": sorted(repetition_inputs),
            "reason": (
                next(
                    (verdict["reason"] for verdict in repetition_verdicts if verdict["rejected"]),
                    "no forbidden candidate input declared or detected",
                )
            ),
            "score_may_override": False,
        },
        "eligible": not repetition_inputs,
        "exceeds_benchmark": defect_total / count > EXPECTED_RANDOM_MEAN,
    }


def _compose(reverse: Dict[str, Any], random_block: Dict[str, Any]) -> Dict[str, Any]:
    winner = random_block if random_block["eligible"] and random_block["exceeds_benchmark"] else None
    return {
        "action": "compose-strategy" if winner else "no-change",
        "composed_strategy": winner["proposal_id"] if winner else None,
        "reason": (
            "non-leaking candidate exceeded the measured benchmark"
            if winner
            else "no non-leaking candidate exceeded the random benchmark mean 6.0"
        ),
        "approved_default": "retain-deterministic-lexical-baseline",
    }


def run_adaptation_cycle(
    plan_path: Path, result_path: Path, corpus_root: Path
) -> Dict[str, Any]:
    """Run the one permitted offline Propose-Probe-Compose cycle."""
    try:
        _, plan_raw = evaluation_plan_v2.load_plan(plan_path)
    except evaluation_plan_v2.EvaluationPlanError as exc:
        raise AdaptationCycleError("approved plan bytes differ") from exc
    result_raw_value, result_raw = _load_json(result_path)
    result = _validate_completed_result(result_raw_value, result_raw)
    truth, truth_raw = _load_trusted_truth(Path(corpus_root))
    frozen = _load_frozen_corpus(Path(corpus_root), truth)
    catalog = frozen["catalog"]

    reverse = _reverse_result(catalog, truth)
    random_block = _random_block_result(catalog, truth)
    compose = _compose(reverse, random_block)
    report = {
        "schema_version": 1,
        "cycle_id": "GRRR-adaptation-cycle-1",
        "method": "offline-propose-probe-compose",
        "status": "complete",
        "inputs": {
            "approved_plan": {"path": "corpus/evaluation-plan-v2-proposed.json", "sha256": _sha256(plan_raw)},
            "completed_result": {"path": "docs/evidence/jev-selector-measurement/three-arm-result-20261103T214701Z/report.json", "sha256": _sha256(result_raw)},
            "frozen_corpus": {
                "version": EXPECTED_CORPUS_VERSION,
                "freeze_digest": EXPECTED_CORPUS_FREEZE_DIGEST,
                "manifest_sha256": frozen["manifest_sha256"],
                "public_projection_sha256": frozen["public_projection_sha256"],
            },
            "protected_truth": {"path": "corpus/protected/truth.json", "sha256": _sha256(truth_raw)},
        },
        "benchmark": {
            "source": "completed-three-arm-random-arm",
            "mean": result["arms"]["random"]["primary_mean"],
            "repetition_values": result["arms"]["random"]["primary_repetition_values"],
            "cherry_picking": "forbidden",
        },
        "proposals": [reverse, random_block],
        "compose": compose,
        "authority": dict.fromkeys(("promotion", "admission", "execution", "production_mutation", "merge", "push"), False),
        "controls": {"offline": True, "model_calls": 0, "credential_reads": 0, "protected_runtime_access": False, "no_automatic_rerun": True, "operator_review_required": True},
    }
    serialized = json.dumps(report, sort_keys=True, indent=2, ensure_ascii=True)
    lowered = serialized.lower()
    if any(marker in lowered for marker in FORBIDDEN_OUTPUT_MARKERS):
        raise AdaptationCycleError("report failed output sanitization")
    return report
