"""Analyze completed Jev repetitions locally; never access network or secrets."""

import argparse
import hashlib
import json
import random
import sys
from pathlib import Path
from typing import Dict, List, Sequence

import evaluation_plan_v2
import selector_comparison


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_PLAN = ROOT / "corpus/evaluation-plan-v2-proposed.json"
DEFAULT_REPETITIONS = (
    ROOT / "docs/evidence/jev-selector-measurement/confirmatory-repetition-1-20261103T214533Z",
    ROOT / "docs/evidence/jev-selector-measurement/confirmatory-repetition-2-20261103T214623Z",
    ROOT / "docs/evidence/jev-selector-measurement/confirmatory-repetition-3-20261103T214701Z",
)
PILOT = ROOT / "docs/evidence/jev-selector-measurement/run-20261103T201719Z"
TRUTH = ROOT / "corpus/protected/truth.json"


class AnalysisRefused(RuntimeError):
    """The completed evidence does not satisfy the approved design."""


def _load_json(path: Path):
    try:
        return json.loads(path.read_bytes())
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise AnalysisRefused(f"invalid JSON: {path.name}") from exc


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _selected_truth(selected: Sequence[str], truth: Dict[str, Dict]):
    defects = sum(truth[item]["truth"] == "defect" for item in selected)
    critical = sum(
        truth[item]["truth"] == "defect" and truth[item]["critical"] is True
        for item in selected
    )
    clean = sum(truth[item]["truth"] == "clean" for item in selected)
    return defects, critical, clean


def _arm_result(selections: List[List[str]], truth: Dict[str, Dict]):
    rows = [_selected_truth(selected, truth) for selected in selections]
    primary = [row[0] for row in rows]
    return {
        "selected_by_repetition": selections,
        "primary_repetition_values": primary,
        "primary_mean": sum(primary) / len(primary),
        "mean_critical": sum(row[1] for row in rows) / len(rows),
        "mean_clean": sum(row[2] for row in rows) / len(rows),
        "unique_defects": len({
            item
            for selected in selections
            for item in selected
            if truth[item]["truth"] == "defect"
        }),
    }


def _bootstrap(values: Dict[str, List[int]]):
    rng = random.Random(20261103)
    result = {name: [] for name in values}
    for _ in range(10000):
        for name in ("deterministic-lexical", "random", "jev-guided"):
            result[name].append(
                sum(rng.choice(values[name]) for _ in range(3)) / 3
            )
    intervals = {}
    for name, samples in result.items():
        ordered = sorted(samples)
        intervals[name] = {
            "lower": ordered[249],
            "upper": ordered[9749],
        }
    return intervals


def analyze(
    plan_path: Path = DEFAULT_PLAN,
    repetitions=DEFAULT_REPETITIONS,
) -> Dict:
    plan, _ = evaluation_plan_v2.load_plan(plan_path)
    truth_rows = _load_json(TRUTH)
    truth = {row["challenge"]: row for row in truth_rows}
    catalog = selector_comparison.load_catalog(ROOT / "corpus")

    deterministic = [
        selector_comparison.deterministic_select(catalog, 8)["selected"]
        for _ in range(3)
    ]
    random_arm = [
        selector_comparison.random_select(catalog, 8, seed=seed)["selected"]
        for seed in (42, 43, 44)
    ]
    jev_reports = []
    jev_selections = []
    for directory in repetitions:
        report = _load_json(directory / "report.json")
        if (report.get("status") != "complete"
                or report.get("adapter_outcome") != "complete"
                or report.get("attempts") != {
                    "attempted_calls": 32,
                    "returned_responses": 32,
                    "retry_count": 0,
                }
                or report.get("selector_result", {}).get("model") != ["jev-1.14.0"]):
            raise AnalysisRefused("Jev repetition evidence differs")
        jev_reports.append(report)
        jev_selections.append(report["selector_result"]["selected"])

    selections = {
        "deterministic-lexical": deterministic,
        "random": random_arm,
        "jev-guided": jev_selections,
    }
    arms = {
        name: _arm_result(value, truth)
        for name, value in selections.items()
    }
    primary = {
        name: result["primary_repetition_values"]
        for name, result in arms.items()
    }
    intervals = _bootstrap(primary)
    for name, result in arms.items():
        result["bootstrap_95"] = intervals[name]

    det = arms["deterministic-lexical"]["primary_mean"]
    rnd = arms["random"]["primary_mean"]
    jev = arms["jev-guided"]["primary_mean"]
    jev_lower = intervals["jev-guided"]["lower"]
    jev_wins = (
        jev >= det + 1.0
        and jev >= rnd + 1.0
        and jev_lower > max(det, rnd)
    )

    confirmatory_input = sum(
        report["usage"]["input_tokens"] for report in jev_reports
    )
    confirmatory_output = sum(
        report["usage"]["output_tokens"] for report in jev_reports
    )
    pilot = _load_json(PILOT / "report.json")
    cumulative_input = confirmatory_input + pilot["usage"]["input_tokens"]
    cumulative_output = confirmatory_output + pilot["usage"]["output_tokens"]
    if (confirmatory_input != 37644 or confirmatory_output != 2208
            or cumulative_input != 50192 or cumulative_output != 2944):
        raise AnalysisRefused("token accounting differs")

    return {
        "schema_version": 1,
        "status": "complete",
        "evaluation_scope": "selector-quality-only",
        "design_sha256": evaluation_plan_v2.EXPECTED_PLAN_SHA256,
        "protected_truth_sha256": _sha256(TRUTH),
        "arms": arms,
        "decision": {
            "pre_registered_default": "retain-deterministic-lexical-baseline",
            "jev_wins": jev_wins,
            "outcome": "jev-wins" if jev_wins else "inconclusive-jev-did-not-win",
            "measured_leading_arm": max(
                arms, key=lambda name: arms[name]["primary_mean"]
            ),
            "permitted_claim": "descriptive selection-quality measurement only",
        },
        "usage": {
            "confirmatory_jev_calls": 96,
            "confirmatory_retries": 0,
            "cumulative_calls_including_pilot": 128,
            "confirmatory_input_tokens": confirmatory_input,
            "confirmatory_output_tokens": confirmatory_output,
            "cumulative_input_tokens": cumulative_input,
            "cumulative_output_tokens": cumulative_output,
            "usd": None,
            "usd_status": "unknown-until-independent-receipt",
        },
        "jev_run_ids": [report["run_id"] for report in jev_reports],
        "not_claims": [
            "software optimization",
            "verified defect",
            "independent replay",
            "contract admission",
            "promotion",
        ],
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Analyze completed three-arm Jev evidence without network access."
    )
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        report = analyze()
        args.output.write_text(
            json.dumps(report, sort_keys=True, indent=2, ensure_ascii=True) + "\n",
            encoding="ascii",
        )
    except (AnalysisRefused, OSError) as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 2
    print(json.dumps({
        "status": report["status"],
        "outcome": report["decision"]["outcome"],
        "output": str(args.output.resolve()),
    }, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
