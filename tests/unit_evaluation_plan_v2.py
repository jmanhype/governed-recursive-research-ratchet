"""Tests for the proposed three-arm evaluation plan; no selector execution."""

import copy
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "research"))

from evaluation_plan_v2 import (  # noqa: E402
    DEFAULT_PLAN_PATH,
    EvaluationPlanError,
    load_plan,
    validate_plan,
)


class EvaluationPlanV2Tests(unittest.TestCase):
    def setUp(self):
        self.plan, self.raw = load_plan()

    def test_plan_loads_and_top_level_schema_is_exact(self):
        self.assertEqual(self.plan["schema_version"], 2)
        self.assertEqual(self.plan["state"], "proposed")
        self.assertEqual(self.raw, DEFAULT_PLAN_PATH.read_bytes())

    def test_execution_and_approval_flags_remain_false(self):
        approval = self.plan["approval"]
        self.assertEqual(approval["state"], "not-approved")
        self.assertIs(approval["measurement_started"], False)
        self.assertIs(approval["execution_authorized"], False)
        self.assertTrue(self.plan["review"][
            "independent_design_review_required_before_approval"
        ])
        self.assertTrue(self.plan["review"][
            "execution_requires_separate_operator_authorization"
        ])

    def test_corpus_binding_is_exact(self):
        corpus = self.plan["corpus"]
        truth_hash = __import__("hashlib").sha256(
            (ROOT / "corpus" / "protected" / "truth.json").read_bytes()
        ).hexdigest()
        manifest = __import__("json").loads(
            (ROOT / "corpus" / "manifest.json").read_bytes()
        )
        self.assertEqual(
            corpus["freeze_digest"],
            "dfa75ef2bf3d43fd4f750094fe643afe4f204812c0ae2426276bedb471fa8529",
        )
        self.assertEqual(corpus["version"], "GRRR-validated-corpus-v2.2-isolated")
        self.assertEqual(corpus["protected_truth"], "corpus/protected/truth.json")
        self.assertEqual(corpus["protected_truth_sha256"], truth_hash)
        self.assertEqual(
            manifest["artifacts"]["protected/truth.json"], truth_hash
        )

    def test_exploratory_run_is_excluded_from_confirmatory_repetitions(self):
        prior = self.plan["prior_evidence"]
        self.assertEqual(prior["classification"], "exploratory-capability-run")
        self.assertEqual(prior["run_id"], "6cf35082f34a4149b67293c7b53d9740")
        self.assertIs(prior["confirmatory_reuse"], False)

    def test_three_arms_use_equal_selection_budget(self):
        arms = self.plan["arms"]
        self.assertEqual(
            arms["deterministic-lexical"]["selected_budget_per_repetition"], 8
        )
        self.assertEqual(arms["random"]["selected_budget_per_repetition"], 8)
        self.assertEqual(arms["jev-guided"]["selected_budget_per_repetition"], 8)
        self.assertEqual(arms["random"]["seeds"], [42, 43, 44])
        self.assertEqual(arms["jev-guided"]["repetition_count"], 3)
        self.assertTrue(arms["jev-guided"]["fresh_repetition_requirement"])

    def test_call_retry_and_token_budgets_are_conservative(self):
        budget = self.plan["budget"]
        self.assertEqual(budget["confirmatory_jev_scoring_calls"], 96)
        self.assertEqual(budget["retries_allowed"], 0)
        self.assertEqual(
            budget["cumulative_call_ceiling_including_exploratory"], 128
        )
        self.assertLess(
            budget["projected_cumulative_input_tokens"],
            budget["hard_cumulative_input_token_ceiling"],
        )
        self.assertLess(
            budget["projected_cumulative_output_tokens"],
            budget["hard_cumulative_output_token_ceiling"],
        )
        self.assertIsNone(budget["usd"])

    def test_metrics_are_selector_quality_only(self):
        metrics = self.plan["metrics"]
        self.assertEqual(metrics["evaluation_scope"], "selector-quality-only")
        self.assertIn("verified defect", metrics["not_claims"])
        self.assertIn("contract admission", metrics["not_claims"])

    def test_uncertainty_and_default_decision_rule_are_fixed(self):
        self.assertEqual(self.plan["uncertainty"]["seed"], 20261103)
        self.assertEqual(self.plan["uncertainty"]["resamples"], 10000)
        self.assertEqual(
            self.plan["decision_rule"]["default"],
            "retain-deterministic-lexical-baseline",
        )
        self.assertEqual(
            self.plan["decision_rule"]["otherwise"], "inconclusive"
        )

    def test_outbound_privacy_and_fail_closed_conditions_are_exact(self):
        privacy = self.plan["privacy"]
        self.assertEqual(privacy["outbound_allowlist"], ["challenge_ref", "category"])
        for forbidden in ("local D/C challenge IDs", "kind", "protected truth", "credentials"):
            self.assertIn(forbidden, privacy["prohibited_outbound"])
        self.assertEqual(privacy["credential_echo"], "fail-closed")
        self.assertFalse(self.plan["failure"]["automatic_rerun"])

    def test_validator_rejects_schema_and_authorization_mutations(self):
        mutations = []

        def mutate(name, value):
            item = copy.deepcopy(self.plan)
            item[name] = value
            mutations.append(item)

        mutate("schema_version", 2.0)
        mutate("state", "approved")
        mutate("approval", {"state": "approved", "measurement_started": False,
                            "execution_authorized": False})
        mutate("arms", {})
        mutate("budget", {"usd": 0.0})
        for item in mutations:
            with self.subTest(item=item):
                with self.assertRaises(EvaluationPlanError):
                    validate_plan(item, self.raw)

    def test_reproducibility_and_safety_semantics_are_frozen(self):
        arms = self.plan["arms"]
        uncertainty = self.plan["uncertainty"]
        decision = self.plan["decision_rule"]
        self.assertEqual(
            arms["random"]["selection"],
            "Python stdlib random.Random(seed).shuffle over the canonical manifest challenge_ids order, followed by the first eight IDs",
        )
        self.assertEqual(arms["random"]["seeds"], [42, 43, 44])
        self.assertEqual(
            arms["jev-guided"]["ranking"],
            "descending expected_defect_weight, then descending raw score, then ascending opaque challenge_ref",
        )
        self.assertEqual(
            uncertainty["procedure"],
            "initialize rng=random.Random(20261103) exactly once; for iteration 0 through 9999 inclusive, for each arm in fixed order deterministic-lexical, random, jev-guided, append [rng.choice(primary_values) for _ in range(3)] and compute its arithmetic mean",
        )
        self.assertEqual(
            uncertainty["sampling_api"],
            "random.Random.choice called three times per arm per bootstrap iteration",
        )
        self.assertEqual(
            uncertainty["percentile_method"],
            "nearest-rank: lower index ceil(0.025*10000)-1 and upper index ceil(0.975*10000)-1 on each sorted bootstrap vector",
        )
        self.assertEqual(decision["jev_wins"]["minimum_mean_margin_over_both_baselines"], 1.0)
        self.assertEqual(self.plan["privacy"]["credential_echo"], "fail-closed")
        self.assertEqual(self.plan["failure"]["next_action"],
                         "operator-review-required; do not automatically rerun")

    def test_isolated_invalid_json_fixtures_reject(self):
        cases = [
            b'{"schema_version":2,"schema_version":2}',
            b'{"schema_version":NaN}',
            b'{"schema_version":2,}',
        ]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "invalid-plan.json"
            for raw in cases:
                with self.subTest(raw=raw):
                    path.write_bytes(raw)
                    with self.assertRaises(EvaluationPlanError):
                        load_plan(path)


if __name__ == "__main__":
    unittest.main()
