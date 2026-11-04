"""Repository-only capstone evidence checklist, NOT an authorized runtime executor.

Historical Git blob integrity cannot establish live gate currency or approval.
This entrypoint has no pass mode: completing the real journey requires a separately
reviewed implementation and human authorization, not editing a manifest status.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[2]
BASE = '845b47d221773eb4157491d35f57dce47ce8afe6'
INDEX = ROOT / 'docs/evidence/milestone-packet/evidence-index.json'
GATES = {
    'source_environment_identity': 'Current approved source, license, build and environment identity receipts.',
    'isolation': 'Authorized disposable offline VM and boundary-probe receipts for the full journey.',
    'protected_asset_integrity': 'Authorized before/after protected integrity receipts, not host inspection here.',
    'baseline_correctness': 'Fresh independently observed clean-baseline pass paired with recurrence rejection.',
    'trusted_observation': 'Evaluator-authenticated observations for every required challenge and negative case.',
    'independent_replay': 'Independent replay receipts across the required seed set; D011 alone is insufficient.',
    'specification_traceability': 'Reviewed requirement mappings and ambiguous-spec rejection for every seed.',
    'evidence_integrity_currency': 'Independent trusted-anchor verification including tamper/truncate/missing cases.',
    'budget_state': 'Independent USD receipt plus cumulative execution/review/reservation accounting within caps.',
    'reviewer_outcome': 'Independent acceptance of this exact complete capstone snapshot; none claimed here.',
    'action_specific_human_approval': 'Fresh exact-target preflight/replay/admission grants; historical grants are not reusable.',
}
JOURNEYS = {
    'AC1': 'Unedited authorized clean-environment start/monitor/report/replay/review/admission/recurrence transcript.',
    'AC2': 'At least 20 validated representative seeds plus negatives through all gates; 100% critical, >=90% others; zero invalid admissions.',
    'AC3': 'Full equal-budget comparison cost evidence: retained three-arm selector result has USD unknown and is selector-quality-only.',
    'AC4': 'Hung executor cessation, idempotency, races, each durable crash transition, pre-stop admission listing and verified restoration or Recovery required.',
    'AC5': 'Full forged/stale/missing/budget/protected-write/ambiguous-spec matrix and export attacks with matching CLI/Markdown/JSON safe actions.',
    'AC6': 'Actual keyboard/screen-reader inspection, reject/request evidence/stop walkthrough with measured review burden.',
    'AC7': 'Final exact-revision architecture/business/design mapping with complete runtime receipts, cost/warning/block/rollback evidence.',
}
ARTIFACT_IDS = frozenset((
    'architecture', 'business', 'design', 'corpus', 'lifecycle', 'snapshot',
    'replay_receipt', 'export_verification', 'contract', 'authorization',
    'admission', 'stop', 'durable', 'jev_design', 'jev_result', 'jev_review',
    'jev_manifest', 'adaptation', 'scorecard',
))


def git_bytes(*arguments: str) -> bytes:
    """Read local Git objects only; never execute artifact contents or hooks."""
    return subprocess.run(['git', '--no-replace-objects', *arguments], cwd=ROOT,
                          check=True, capture_output=True, timeout=10).stdout


def inspect_artifact(name: str, item: dict) -> dict:
    """Verify the named historical blob, without elevating it to a gate pass."""
    result = {'id': name, 'status': 'error'}
    try:
        path, revision, expected = item['path'], item['revision'], item['sha256']
        if (set(item) != {'path', 'revision', 'sha256'} or
                not re.fullmatch(r'[0-9a-f]{40}', revision) or
                not re.fullmatch(r'[0-9a-f]{64}', expected) or
                not path.startswith(('docs/', 'corpus/', 'reports/')) or
                any(part in ('', '.', '..') for part in path.split('/'))):
            raise ValueError('invalid historical artifact reference')
        git_bytes('merge-base', '--is-ancestor', revision, BASE)
        data = git_bytes('show', revision + ':' + path)
        if data != git_bytes('show', BASE + ':' + path) or sha256(data).hexdigest() != expected:
            raise ValueError('historical bytes or digest differ')
        result.update(status='hash-matched', **item)
    except (KeyError, TypeError, ValueError, OSError, subprocess.SubprocessError) as exc:
        result['reason'] = type(exc).__name__ + ': historical artifact could not be verified'
    return result


def checklist() -> dict:
    """Enumerate every missing mandatory gate, even when provenance is broken."""
    provenance = []
    try:
        index = json.loads(INDEX.read_bytes())
        if (set(index) != {'base_revision', 'scope', 'artifacts'} or
                index['base_revision'] != BASE or index['scope'] != 'historical-provenance-only' or
                set(index['artifacts']) != ARTIFACT_IDS):
            raise ValueError('evidence index schema or inventory differs')
        provenance = [inspect_artifact(name, index['artifacts'][name]) for name in sorted(ARTIFACT_IDS)]
    except (OSError, KeyError, TypeError, ValueError) as exc:
        provenance = [{'id': 'evidence-index', 'status': 'error', 'reason': type(exc).__name__}]
    return {
        'schema_version': 1, 'mode': 'repository-only-evidence-checklist',
        'base_revision': BASE, 'execution': 'not-run', 'finding': 'Inconclusive',
        'decision': 'blocked', 'effect': 'none', 'verified': False,
        'admission': 'blocked', 'promotion': 'disabled',
        'gates': [{'id': name, 'status': 'not-run', 'missing_evidence': requirement}
                  for name, requirement in GATES.items()],
        'acceptance_criteria': [{'id': name, 'status': 'not-run', 'missing_evidence': requirement}
                                for name, requirement in JOURNEYS.items()],
        'provenance': provenance,
        'summary': {'required_gates': len(GATES), 'required_journeys': len(JOURNEYS),
                    'executed': 0, 'passed': 0, 'failed': 0, 'not_run': len(GATES) + len(JOURNEYS),
                    'skipped': 0, 'provenance_hash_matched': sum(p['status'] == 'hash-matched' for p in provenance),
                    'provenance_errors': sum(p['status'] == 'error' for p in provenance)},
        'next_action': 'Stop. Obtain missing evidence and separately scoped human authorization; do not rerun paid calls or protected actions.',
        'warning': 'Hash-matched historical records are not fresh gate passes, independent authentication, complete export verification, or full E2E results.',
    }


def main() -> int:
    """Return nonzero because mandatory capstone evidence is missing, never skipped."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--json', action='store_true', help='same checklist in structured form')
    args = parser.parse_args()
    report = checklist()
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print('BLOCKED: milestone-e2e; repository-only evidence checklist, NOT a runtime E2E pass')
        for group in ('gates', 'acceptance_criteria'):
            for item in report[group]:
                print(f"{item['id']}: {item['status']} -- {item['missing_evidence']}")
        for item in report['provenance']:
            print(f"Historical {item['id']}: {item['status']}")
        print('Summary: ' + json.dumps(report['summary'], sort_keys=True))
        print(report['warning'])
        print(report['next_action'])
    return 1


if __name__ == '__main__':
    raise SystemExit(main())
