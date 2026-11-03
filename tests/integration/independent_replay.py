"""Mandatory real evaluator integration. Missing identity/infrastructure is an error.

No fallback runs candidates on the host. Fault-injection evidence is mandatory;
unit-level changed dictionaries do not satisfy failed-build/interrupt proof.
"""
import copy
import json
import sqlite3
from types import SimpleNamespace
from pathlib import Path
import sys
import unittest

if __name__ == '__main__':
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'research'))

from common import EVALUATOR, Failure, GATES, canonical, digest, require
from replay_profile import validate_receipt
from replay import (CHALLENGE, INPUTS, POLICY_SHA256, SOURCE_ARCHIVE, ReplaySession,
                    maintainer_specification, observation_outcome, finding, MODES,
                    runtime, read_plan, validate_scope, validate_mode_results)
from replay_smoke import require_identity
from trusted_execution import protected_bytes, root_record


class IndependentReplay(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        require_identity(EVALUATOR)
        # Parent modes execute once, terminate their services, and retain evidence.
        # Tests consume all four namespaces without creating new allowances/runs.
        cls.modes = {}
        for mode in MODES:
            read_plan(mode)
            home = runtime(mode) / 'evaluator/replay-ledger'
            require(home.stat().st_uid == EVALUATOR and home.stat().st_mode & 0o077 == 0,
                    'Unauthorized', 'Private real evaluator evidence required')
            with sqlite3.connect((home / 'ledger.sqlite').as_uri() + '?mode=ro', uri=True) as db:
                events = [json.loads(row[0]) for row in db.execute('SELECT body FROM events ORDER BY seq')]
            observations, receipts = [], []
            for event in events:
                if event['kind'] in ('replay-raw-observation', 'independent-replay-receipt'):
                    hashed = event['objects'][0]
                    raw = (home / 'objects' / hashed).read_bytes()
                    require(digest(raw) == hashed, 'IntegrityFailure', 'Live evidence object differs')
                    if event['kind'] == 'replay-raw-observation':
                        observations.append((event['request'], json.loads(raw)))
                    else:
                        receipts.append(json.loads(raw))
            validate_mode_results(mode, receipts, observations)
            cls.modes[mode] = (receipts, observations)
        cls.receipt = cls.modes['normal'][0][0]
        cls.observations = cls.modes['normal'][1]
        cls.session = SimpleNamespace(config=root_record(runtime('normal') / 'runner/config.json'),
            specification=maintainer_specification(protected_bytes(INPUTS / 'source.tar', SOURCE_ARCHIVE), CHALLENGE))

    def test_valid_seed_real_fresh_vms_and_specification(self) -> None:
        self.assertEqual(self.receipt['finding'], 'Verified defect')
        self.assertTrue(self.receipt['execution_complete'])
        self.assertEqual(len(self.observations), 2)
        self.assertNotEqual(self.observations[0][0]['run'], self.observations[1][0]['run'])
        self.assertEqual(set(self.receipt['gates']), set(GATES))
        self.assertEqual(self.receipt['admission'], 'blocked')
        self.assertEqual(self.receipt['gates']['reviewer_outcome']['status'], 'not-run')

    def test_clean_baseline_real_observation_is_not_defect(self) -> None:
        self.assertEqual(len(self.observations), 2)
        outcome = observation_outcome(self.observations[0][1]['guest']['candidate_observation'])
        self.assertEqual(outcome, 'clean')
        self.assertEqual(finding(outcome, self.session.specification, 'clean'), 'Not reproduced')

    def test_forged_pass_logs_rejected_not_replayed(self) -> None:
        self.assertEqual(len(self.observations), 2)
        request, result = self.observations[1]
        changed = copy.deepcopy(result)
        changed['raw_base64'] = 'UEFTUw=='
        with self.assertRaises(Failure):
            validate_receipt(changed, request, self.session.config['execution_profile'])

    def test_candidate_modified_harness_or_fixture_cannot_confirm_spec(self) -> None:
        archive = protected_bytes(INPUTS / 'source.tar', SOURCE_ARCHIVE)
        for marker in (b'link with display text', b'if g.Display != want.Display'):
            with self.subTest(marker=marker), self.assertRaises(Failure):
                maintainer_specification(archive.replace(marker, b'x' * len(marker), 1), CHALLENGE)

    def test_stale_candidate_evaluator_binding_rejected(self) -> None:
        with self.assertRaises(Failure):
            validate_scope(dict(read_plan()['scope'], profile='0' * 64))
        request, result = self.observations[1]
        changed = copy.deepcopy(result)
        changed['execution_profile'] = '0' * 64
        with self.assertRaises(Failure):
            validate_receipt(changed, request, self.session.config['execution_profile'])

    def test_missing_source_object_cannot_confirm_spec(self) -> None:
        with self.assertRaises(Failure):
            maintainer_specification(b'', CHALLENGE)

    def test_ambiguous_requirement_blocks_verification(self) -> None:
        archive = protected_bytes(INPUTS / 'source.tar', SOURCE_ARCHIVE)
        ambiguous = maintainer_specification(archive, 'GRRR-VC-D001')
        outcome = observation_outcome(self.observations[1][1]['guest']['candidate_observation'])
        self.assertEqual(finding(outcome, ambiguous, 'clean'), 'Specification ambiguity')

    def test_real_failed_rebuild_evidence_required(self) -> None:
        failed = [result for _, result in self.modes['failed-rebuild'][1]
                  if result['guest']['candidate_observation']['build_exit'] != 0]
        self.assertTrue(failed, 'Mandatory live failed-rebuild execution is absent; parsing is not proof')

    def test_real_interrupted_replay_evidence_required(self) -> None:
        interrupted = [result for _, result in self.modes['interruption'][1]
                       if result.get('interruption') ==
                       {'kind': 'fixed-replay-command-interruption', 'bound_seconds': 60}]
        self.assertTrue(interrupted, 'Mandatory live interrupted replay execution is absent; '
                        'a missing stop acknowledgment alone is not interruption proof')

    def test_two_real_failure_receipts_retained_with_stop(self) -> None:
        receipts = self.modes['two-failures'][0]
        self.assertTrue(any(item['consecutive_failures'] == 2 and item['stopped'] for item in receipts),
                        'Mandatory two-consecutive live failure sequence absent')
        self.assertGreaterEqual(len(receipts), 3, 'Earlier failures must remain beside a successful fresh receipt')


def run_tests() -> int:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(IndependentReplay)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() and result.testsRun == 10 and not result.skipped else 1


if __name__ == '__main__':
    raise SystemExit(run_tests())
