"""Parent synthetic presentation probe: no actual admission or replay."""
import copy
import json
import sys

sys.path[:0] = ['/Users/speed/Documents/Codex/2026-10-19/3e4m-b-4/outputs/governed-recursive-research-ratchet/.claude/worktrees/dev-GRRR-n49g/research']
from admission import GATE_INVENTORY
from review_report import build_report, to_json, to_markdown, to_plain_text

def data():
    return {'receipt': {'finding': 'Verified defect', 'verified': True,
                        'gates': {name: {'status': 'pass'} for name in GATE_INVENTORY}},
            'lifecycle': {'evaluator_succeeded': True}}

checks = 0
outcomes = []
for gates in ({}, {name: {'status': 'pass'} for name in sorted(GATE_INVENTORY)[:-1]},
              {'unrelated': {'status': 'pass'}}):
    item = data()
    item['receipt']['gates'] = gates
    report = build_report(item)
    assert report['gates_total'] == len(GATE_INVENTORY), report
    assert not report['recommendation'].lower().startswith('approve'), report
    assert report['decision_state'] != 'Ready for action', report
    checks += 1
    outcomes.append({'case': 'missing-required-gates', 'report': report})
for cost in (None, True, False, -1, float('nan'), float('inf'), '0', {}):
    item = data()
    item['receipt']['cost_usd'] = cost
    report = build_report(item)
    assert report['cost_usd'] is None, report
    assert '$0' not in to_plain_text(report), report
    assert '$0' not in to_markdown(report), report
    assert json.loads(to_json(report))['cost_usd'] is None
    checks += 1
for cost in (0, 0.0, 2.5):
    item = data()
    item['receipt']['cost_usd'] = cost
    before = copy.deepcopy(item)
    report = build_report(item)
    assert report['cost_usd'] == cost, report
    assert item == before
    checks += 1
    outcomes.append({'case': 'explicit-reported-cost', 'report': report})
print(json.dumps({'synthetic_only': True, 'checks_passed': checks, 'outcomes': outcomes},
                 sort_keys=True, indent=2, allow_nan=False))
