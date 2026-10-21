"""No-mock validation of the frozen vlt corpus and its protected boundaries."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'research'))
del sys
from common import Failure
import validated_corpus


class ValidatedCorpus(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = validated_corpus.validate(ROOT)

    def test_counts_categories_and_independence(self):
        self.assertEqual(self.result['defects'], 24)
        self.assertEqual(self.result['clean'], 8)
        self.assertEqual(self.result['critical'], 16)
        self.assertEqual(self.result['variants'], 32)
        self.assertEqual(len(validated_corpus.CATEGORIES), 10)
        manifest = validated_corpus.load_json(ROOT / 'corpus/manifest.json')
        self.assertEqual(set(manifest['categories']), set(validated_corpus.CATEGORIES))
        self.assertEqual(len(manifest['challenge_ids']), 32)

    def test_public_projection_omits_protected_truth(self):
        public = validated_corpus.load_json(ROOT / 'corpus/public/challenges.json')
        public_specs = validated_corpus.load_json(ROOT / 'corpus/public/spec-map.json')
        self.assertEqual(len(public), len(public_specs), 32)
        for challenge, spec in zip(public, public_specs):
            self.assertNotIn('expected_behavior', spec)
            self.assertNotIn('critical', spec)
            self.assertNotRegex(challenge['public_fixture'], r'anchor|replacement|truth|holdout')

    def test_seed_recipes_reproduce_against_exact_pinned_source(self):
        _, files = validated_corpus.pinned_source()
        seeds = validated_corpus.load_json(ROOT / 'corpus/protected/seeds.json')
        public = validated_corpus.load_json(ROOT / 'corpus/public/challenges.json')
        variants = [validated_corpus.apply_seed(files, seed) for seed in seeds]
        self.assertEqual(len(variants), 32)
        self.assertEqual(len(set(variants)), 32)
        for seed, challenge, variant in zip(seeds, public, variants):
            self.assertEqual(challenge['variant'], variant)
            if seed['kind'] == 'clean-control':
                self.assertIsNone(seed['anchor'])
            else:
                self.assertEqual(files[seed['file']].count(seed['anchor'].encode('utf-8')), 1)

    def test_plan_is_pre_registered_and_measurement_is_blocked(self):
        plan = validated_corpus.load_json(ROOT / 'corpus/evaluation-plan.json')
        self.assertEqual(plan['arm_order'], ['deterministic-risk', 'random', 'jev-guided'])
        self.assertEqual(plan['randomized_repetitions'], 3)
        self.assertFalse(plan['approval']['measurement_started'])
        self.assertEqual(plan['approval']['state'], 'not-approved')
        self.assertTrue(plan['stopping']['stop_on_hard_gate_failure'])
        self.assertIn('unique detected truth labels', plan['cost']['denominator'])

    def test_accepted_v4_observation_is_internally_verified(self):
        reference = self.result['accepted_v4_observation']
        self.assertEqual(reference['completed'], 8)
        self.assertEqual(reference['clean_pass'], 2)
        self.assertEqual(reference['fault_fail'], 6)
        self.assertEqual(reference['receipt'],
                         '64869aa6d0c4d550dfaa794a71f14266ba0b7ef21a1b902efb44f38f391fd672')

    def test_concurrent_read_validation_is_deterministic(self):
        with ThreadPoolExecutor(max_workers=3) as pool:
            results = list(pool.map(lambda _: validated_corpus.validate(ROOT), range(3)))
        self.assertEqual({item['freeze_digest'] for item in results},
                         {self.result['freeze_digest']})

    def test_public_artifact_tamper_fails_closed(self):
        path = ROOT / 'corpus/public/challenges.json'
        original = path.read_bytes()
        try:
            path.write_bytes(original.replace(b'public_fixture', b'tampered_fixture', 1))
            with self.assertRaises(Failure):
                validated_corpus.validate(ROOT)
        finally:
            path.write_bytes(original)
        self.assertEqual(validated_corpus.validate(ROOT)['freeze_digest'], self.result['freeze_digest'])

    def test_missing_required_path_fails_closed(self):
        with tempfile.TemporaryDirectory() as folder:
            empty = Path(folder)
            (empty / 'corpus').mkdir()
            with self.assertRaises(FileNotFoundError):
                validated_corpus.validate(empty)

    def test_downstream_gates_remain_not_run(self):
        self.assertEqual(self.result['status'], 'static-validation-pass; seeded isolated execution not-run')
        self.assertEqual(self.result['blocked_gates']['seeded_variant_execution'], 'not-run')
        self.assertEqual(self.result['blocked_gates']['independent_replay'], 'not-run')
        self.assertEqual(self.result['blocked_gates']['admission'], 'blocked')
        self.assertFalse(self.result['verified'])
        self.assertEqual(self.result['admission'], 'blocked')


if __name__ == '__main__':
    unittest.main(verbosity=2)
