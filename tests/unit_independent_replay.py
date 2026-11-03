"""No-guest contracts only; these tests do not certify independent execution."""
import copy
import importlib.machinery
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'research'))
from common import Failure, GATES, digest
from replay import (CHALLENGE, SCOPE, SPEC_SHA256, ReplaySession, ReplayExecutor,
                    candidate_identity, maintainer_specification, observation_outcome,
                    finding, failure_transition, gate_inventory, validate_scope, evaluator, runner, preflight)


class IndependentReplayContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.archive = Path('/Library/GRRR/replay-inputs/source.tar').read_bytes()
        cls.spec = maintainer_specification(cls.archive, CHALLENGE)

    def observation(self, exit_code: int = 1) -> dict:
        return {'version': 1, 'challenge': 'D011', 'test': 'TestGRRRD011',
                'build_exit': 0, 'build_output_sha256': 'a' * 64, 'internal_error': False,
                'repetitions': [{'exit': exit_code, 'output_sha256': 'b' * 64} for _ in range(3)]}

    def test_exact_upstream_spec_bytes_and_assertion(self) -> None:
        self.assertEqual(self.spec['status'], 'pass')
        self.assertEqual(self.spec['member_sha256'], SPEC_SHA256)
        self.assertEqual(self.spec['case'], 'TestParseWikilinks/link with display text')

    def test_tampered_source_harness_or_fixture_is_not_specification(self) -> None:
        for marker in (b'link with display text', b'if g.Display != want.Display'):
            with self.subTest(marker=marker), self.assertRaises(Failure):
                maintainer_specification(self.archive.replace(marker, b'x' * len(marker), 1), CHALLENGE)

    def test_missing_source_object_fails(self) -> None:
        with self.assertRaises(Failure):
            maintainer_specification(b'', CHALLENGE)

    def test_unmapped_requirement_remains_ambiguous(self) -> None:
        unknown = maintainer_specification(self.archive, 'GRRR-VC-D001')
        self.assertEqual(unknown['status'], 'not-run')
        self.assertEqual(finding('failure', unknown, 'clean'), 'Specification ambiguity')

    def test_reconstruct_seeded_candidate_from_actual_archive(self) -> None:
        seeds = json.loads((ROOT / 'corpus/protected/seeds.json').read_bytes())
        seed = next(item for item in seeds if item['challenge'] == CHALLENGE)
        value = candidate_identity(self.archive, seed)
        self.assertEqual(len(value), 64)
        self.assertEqual(value, candidate_identity(self.archive, seed))
        seed['replacement'] = 'if true {'
        with self.assertRaises(Failure):
            candidate_identity(self.archive, seed)

    def test_failed_rebuild_is_inconclusive_not_defect(self) -> None:
        value = self.observation()
        value['build_exit'] = 1
        self.assertEqual(observation_outcome(value), 'inconclusive')
        self.assertEqual(finding('inconclusive', self.spec, 'clean'), 'Inconclusive')

    def test_clean_negative_never_becomes_defect(self) -> None:
        outcome = observation_outcome(self.observation(0))
        self.assertEqual(outcome, 'clean')
        self.assertEqual(finding(outcome, self.spec, 'clean'), 'Not reproduced')

    def test_repeated_assertion_failure_requires_spec_and_baseline(self) -> None:
        self.assertEqual(observation_outcome(self.observation()), 'failure')
        self.assertEqual(finding('failure', self.spec, 'clean'), 'Verified defect')
        self.assertEqual(finding('failure', self.spec, 'failure'), 'Inconclusive')
        self.assertEqual(finding('failure', {'status': 'not-run'}, 'clean'), 'Specification ambiguity')

    def test_nondeterminism_is_inconclusive(self) -> None:
        value = self.observation()
        value['repetitions'][2]['exit'] = 0
        self.assertEqual(observation_outcome(value), 'inconclusive')
        value = self.observation()
        value['repetitions'][2]['output_sha256'] = 'c' * 64
        self.assertEqual(observation_outcome(value), 'inconclusive')

    def test_forged_pass_logs_and_unknown_fields_rejected(self) -> None:
        value = self.observation()
        value['PASS'] = True
        with self.assertRaises(Failure):
            observation_outcome(value)
        value = self.observation()
        value['repetitions'][0]['output_sha256'] = 'PASS'
        with self.assertRaises(Failure):
            observation_outcome(value)

    def test_each_mandatory_gate_starts_not_run(self) -> None:
        gates = gate_inventory()
        self.assertEqual(set(gates), set(GATES))
        self.assertTrue(all(gate == {'status': 'not-run', 'evidence': []} for gate in gates.values()))

    def test_policy_approval_required_even_for_success(self) -> None:
        for threshold in (None, True, 2.0, 1, 3):
            with self.subTest(threshold=threshold), self.assertRaises(Failure):
                failure_transition(0, True, threshold)

    def test_unregistered_cumulative_accounting_blocks_before_dispatch(self) -> None:
        with self.assertRaises(Failure) as caught:
            preflight()
        self.assertEqual(caught.exception.record['code'], 'GateBlocked')
        self.assertIn('Cumulative campaign accounting', str(caught.exception))

    def test_two_failures_stop_and_success_does_not_erase_history(self) -> None:
        first = failure_transition(0, False, 2)
        self.assertFalse(first['stopped'])
        second = failure_transition(first['consecutive_failures'], False, 2)
        self.assertTrue(second['stopped'])
        self.assertFalse(second['release_unknown_reservations'])
        reset = failure_transition(1, True, 2)
        self.assertEqual(reset['consecutive_failures'], 0)
        self.assertTrue(reset['retain_previous_evidence'])
        with self.assertRaises(Failure):
            failure_transition(2, True, 2)

    def test_scope_and_actual_identity_fail_closed(self) -> None:
        validate_scope(SCOPE)
        changed = dict(SCOPE, challenge='GRRR-VC-D001')
        with self.assertRaises(Failure):
            validate_scope(changed)
        for action in (ReplaySession, ReplayExecutor, evaluator, runner):
            with self.subTest(action=action.__name__), self.assertRaises(Failure):
                action()

    def test_checkout_root_command_refuses_unprivileged_caller(self) -> None:
        result = subprocess.run([sys.executable, '-I', '-S', '-B',
                                 str(ROOT / 'scripts/replay-root-prepare'), '--independent-replay'],
                                capture_output=True, timeout=10)
        self.assertEqual(result.returncode, 1)
        self.assertFalse(json.loads(result.stdout)['execution_authorized'])

    def test_reviewed_import_inventory_matches_checkout(self) -> None:
        loader = importlib.machinery.SourceFileLoader('replay_root_contract', str(ROOT / 'scripts/replay-root-prepare'))
        module = importlib.util.module_from_spec(importlib.util.spec_from_loader(loader.name, loader))
        loader.exec_module(module)
        self.assertIn('replay.py', module.CODE)
        self.assertIn('corpus_evaluation.py', module.CODE)
        for name, hashed in module.CODE.items():
            self.assertEqual(digest((ROOT / 'research' / name).read_bytes()), hashed, name)


if __name__ == '__main__':
    unittest.main(verbosity=2)
