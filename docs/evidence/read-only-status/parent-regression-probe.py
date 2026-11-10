"""Synthetic presentation checks only; no actual admission or replay."""
import copy
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "research"))
from common import GATES
from review_report import build_report, to_json, to_markdown, to_plain_text


def fixture():
    return {"receipt": {"finding": "Verified defect", "verified": True,
                        "gates": {name: {"status": "pass"} for name in GATES}},
            "lifecycle": {"evaluator_succeeded": True}}


checks = 0
for gates in ({}, {name: {"status": "pass"} for name in GATES[:-1]},
              {"unrelated": {"status": "pass"}}):
    item = fixture()
    item["receipt"]["gates"] = gates
    report = build_report(item)
    assert report["verification"]["gates"]["required_total"] == 11
    assert not report["verification"]["evidence_review_eligible"]
    assert report["recommendation"] == "Needs more evidence"
    assert not any(report["action_authorization"]["authorities"].values())
    checks += 1
for cost in (None, True, False, -1, float("nan"), float("inf"), "0", {}):
    item = fixture()
    item["receipt"]["cost_usd"] = cost
    report = build_report(item)
    assert report["budget"]["cost_usd"] is None
    assert "$0" not in to_plain_text(report)
    assert "$0" not in to_markdown(report)
    assert json.loads(to_json(report))["budget"]["cost_usd"] is None
    checks += 1
for cost in (0, 0.0, 2.5):
    item = fixture()
    item["receipt"]["cost_usd"] = cost
    before = copy.deepcopy(item)
    report = build_report(item)
    assert report["budget"]["cost_usd"] == cost
    assert item == before
    assert report["budget"]["settled_accounting"] is False
    checks += 1
item = fixture()
for name in ("reviewer_outcome", "action_specific_human_approval"):
    item["receipt"]["gates"][name]["status"] = "not-run"
report = build_report(item)
assert report["verification"]["gates"]["required_passed"] == 9
assert not report["verification"]["evidence_review_eligible"]
checks += 1
print(json.dumps({"synthetic_only": True, "checks_passed": checks,
                  "required_gates": 11, "no_actions_authorized": True},
                 sort_keys=True, indent=2, allow_nan=False))
