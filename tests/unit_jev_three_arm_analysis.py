"""Tests for local three-arm analysis of completed Jev repetitions."""

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "research"))

from jev_three_arm_analysis import analyze  # noqa: E402


class ThreeArmAnalysisTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = analyze()

    def test_design_and_truth_bindings(self):
        self.assertEqual(
            self.result["design_sha256"],
            "97ec4b8ccc34b3fc4da4fcfbef33b49bbb3f4f1c445cfecdb752715ddf034be1",
        )
        self.assertEqual(
            self.result["protected_truth_sha256"],
            "7cf9f99f5836c4e3e147df2866d54480a706f2665a732fbf61bd1a0d0b4c52ea",
        )

    def test_primary_repetition_values(self):
        self.assertEqual(
            self.result["arms"]["deterministic-lexical"]["primary_repetition_values"],
            [0, 0, 0],
        )
        self.assertEqual(
            self.result["arms"]["random"]["primary_repetition_values"],
            [6, 6, 6],
        )
        self.assertEqual(
            self.result["arms"]["jev-guided"]["primary_repetition_values"],
            [5, 6, 4],
        )

    def test_secondary_metrics(self):
        self.assertEqual(self.result["arms"]["deterministic-lexical"]["mean_clean"], 8.0)
        self.assertEqual(self.result["arms"]["random"]["mean_clean"], 2.0)
        self.assertEqual(self.result["arms"]["jev-guided"]["mean_clean"], 3.0)
        self.assertEqual(self.result["arms"]["random"]["unique_defects"], 14)
        self.assertEqual(self.result["arms"]["jev-guided"]["unique_defects"], 7)

    def test_bootstrap_intervals(self):
        self.assertEqual(
            self.result["arms"]["deterministic-lexical"]["bootstrap_95"],
            {"lower": 0.0, "upper": 0.0},
        )
        self.assertEqual(
            self.result["arms"]["random"]["bootstrap_95"],
            {"lower": 6.0, "upper": 6.0},
        )
        self.assertEqual(
            self.result["arms"]["jev-guided"]["bootstrap_95"],
            {"lower": 4.0, "upper": 6.0},
        )

    def test_pre_registered_decision_is_inconclusive_for_jev(self):
        self.assertFalse(self.result["decision"]["jev_wins"])
        self.assertEqual(
            self.result["decision"]["outcome"],
            "inconclusive-jev-did-not-win",
        )
        self.assertEqual(self.result["decision"]["measured_leading_arm"], "random")

    def test_exact_call_and_token_accounting(self):
        usage = self.result["usage"]
        self.assertEqual(usage["confirmatory_jev_calls"], 96)
        self.assertEqual(usage["confirmatory_retries"], 0)
        self.assertEqual(usage["cumulative_calls_including_pilot"], 128)
        self.assertEqual(usage["confirmatory_input_tokens"], 37644)
        self.assertEqual(usage["confirmatory_output_tokens"], 2208)
        self.assertEqual(usage["cumulative_input_tokens"], 50192)
        self.assertEqual(usage["cumulative_output_tokens"], 2944)
        self.assertIsNone(usage["usd"])


if __name__ == "__main__":
    unittest.main()
