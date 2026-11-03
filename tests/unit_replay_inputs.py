"""No-guest evidence for replay-only fixture bytes and fixed dispatch contracts."""
import importlib.machinery
import importlib.util
import io
import json
from pathlib import Path
import sys
import tarfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'research'))
from common import Failure, canonical, digest
from corpus_execution import CorpusExecutor, PRESERVED_ROOT, PROFILE as CORPUS_PROFILE
from corpus_probes import PROBES
from replay import MODES, ParentProtocol, ReplayExecutor, scope, runtime, validate_scope, validate_mode_results
from replay_fixtures import CLEAN, SEEDED, REBUILD, INTERRUPTION, catalog, probes, seeds
import replay_profile


class ReplayInputContracts(unittest.TestCase):
    def test_same_semantic_assertion_in_clean_and_seeded(self) -> None:
        values = probes()
        self.assertEqual(set(values), {CLEAN, SEEDED, REBUILD, INTERRUPTION})
        clean = values[CLEAN].replace(b'C901', b'D901')
        self.assertEqual(clean, values[SEEDED])
        self.assertIn(PROBES['D011'].encode(), clean)
        self.assertIn(b'time.Sleep(300 * time.Second)', values[INTERRUPTION])

    def test_catalog_is_fresh_and_content_bound(self) -> None:
        values = seeds()
        self.assertEqual(values[0]['kind'], 'clean-control')
        self.assertEqual(values[1]['replacement'], 'if false {')
        self.assertEqual(values[2]['replacement'], 'if GRRR_REPLAY_INVALID_SYNTAX { {')
        self.assertEqual(catalog()['seed_sha256'], digest(canonical(values)))
        values.clear()
        self.assertEqual(len(seeds()), 4)

    def test_actual_pinned_source_has_exact_seed_anchors(self) -> None:
        raw = Path('/Library/GRRR/replay-inputs/source.tar').read_bytes()
        with tarfile.open(fileobj=io.BytesIO(raw)) as archive:
            source = archive.extractfile('wikilinks.go').read()
        for seed in seeds()[1:3]:
            self.assertEqual(source.count(seed['anchor'].encode()), 1)
        # Syntax is deliberately broken before guest compilation, not a fake receipt.
        broken = source.replace(seeds()[2]['anchor'].encode(), seeds()[2]['replacement'].encode())
        self.assertIn(b'if GRRR_REPLAY_INVALID_SYNTAX { {', broken)

    def test_default_corpus_identity_and_path_unchanged(self) -> None:
        executor = object.__new__(CorpusExecutor)
        self.assertEqual(executor.input_image(), PRESERVED_ROOT / 'input.iso')
        self.assertEqual(executor.artifact_identity()['profile'], CORPUS_PROFILE)
        self.assertIsNone(executor.command_watchdog('run', INTERRUPTION))

    def test_default_receipt_shape_and_run_binding_preserved(self) -> None:
        executor = object.__new__(CorpusExecutor)
        result = {'run': 'run', 'guest': None}
        self.assertIs(executor.finalize_result('run', result), result)
        with self.assertRaises(Failure):
            executor.finalize_result('other', result)

    def test_matching_finding_alone_is_not_mode_execution_proof(self) -> None:
        expected = {'normal': ['Verified defect'], 'failed-rebuild': ['Inconclusive'],
                    'interruption': ['Inconclusive'],
                    'two-failures': ['Verified defect', 'Not reproduced', 'Not reproduced']}
        for mode, findings in expected.items():
            with self.subTest(mode=mode), self.assertRaises(Failure):
                validate_mode_results(mode, [{'finding': value} for value in findings], [])

    def test_replay_path_and_identity_cannot_come_from_request(self) -> None:
        executor = object.__new__(ReplayExecutor)
        self.assertEqual(executor.input_image(), replay_profile.ROOT / 'input.iso')
        self.assertEqual(executor.artifact_identity(), replay_profile.identity())
        self.assertNotEqual(executor.artifact_identity()['profile'], CORPUS_PROFILE)

    def test_modes_distinct_one_shot_namespaces_and_scopes(self) -> None:
        self.assertEqual(len({runtime(mode) for mode in MODES}), 4)
        for mode in MODES:
            value = scope(mode)
            validate_scope(value, mode)
            self.assertEqual(value['maximum_guest_launches'], 2 * len(MODES[mode]))
            self.assertEqual(value['profile'], replay_profile.PROFILE)
            protocol = ParentProtocol(mode)
            self.assertEqual(protocol.role_prefix, 'replay-' + mode)
            with self.assertRaises(Failure):
                protocol.scope_event('runtime-smoke-complete', mode='forged')
            changed = dict(value, profile=CORPUS_PROFILE)
            with self.assertRaises(Failure):
                validate_scope(changed, mode)
        with self.assertRaises(Failure):
            scope('caller-command')

    def test_all_modes_refuse_unregistered_accounting(self) -> None:
        for mode in MODES:
            with self.subTest(mode=mode), self.assertRaises(Failure) as caught:
                ParentProtocol(mode).preflight()
            self.assertEqual(caught.exception.record['code'], 'GateBlocked')

    def test_preparation_floor_failure_has_no_side_effects(self) -> None:
        loader = importlib.machinery.SourceFileLoader('replay_preparation', str(ROOT / 'scripts/prepare-independent-replay-input'))
        module = importlib.util.module_from_spec(importlib.util.spec_from_loader(loader.name, loader))
        loader.exec_module(module)
        with self.assertRaises(Failure):
            module.space(ROOT, 10**18)


if __name__ == '__main__':
    unittest.main(verbosity=2)
