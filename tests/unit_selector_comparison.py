"""Tests for the equal-budget selector comparison."""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "research"))

from selector_comparison import (
    ARMS,
    CORPUS_FREEZE_DIGEST,
    SelectorError,
    deterministic_select,
    jev_select,
    load_catalog,
    random_select,
    run_comparison,
    validate_selections,
)


CATALOG = [f"GRRR-VC-{i:04d}" for i in range(1, 33)]


class TestSelectorComparison(unittest.TestCase):
    def test_deterministic_selects_lexical_order(self):
        result = deterministic_select(CATALOG, 8)
        self.assertEqual(result["selected"], sorted(CATALOG)[:8])

    def test_deterministic_is_reproducible(self):
        a = deterministic_select(CATALOG, 8, seed=123)
        b = deterministic_select(CATALOG, 8, seed=123)
        self.assertEqual(a["selected"], b["selected"])

    def test_random_selects_with_seed(self):
        result = random_select(CATALOG, 8, seed=42)
        self.assertEqual(len(result["selected"]), 8)
        self.assertNotEqual(result["selected"], sorted(CATALOG)[:8])

    def test_random_is_reproducible_with_same_seed(self):
        a = random_select(CATALOG, 8, seed=42)
        b = random_select(CATALOG, 8, seed=42)
        self.assertEqual(a["selected"], b["selected"])

    def test_random_different_with_different_seed(self):
        a = random_select(CATALOG, 8, seed=42)
        b = random_select(CATALOG, 8, seed=99)
        self.assertNotEqual(a["selected"], b["selected"])

    def test_jev_unavailable(self):
        result = jev_select(CATALOG, 8)
        self.assertFalse(result.get("available", False))
        self.assertEqual(result["selected"], [])
        self.assertIn("unavailable", result.get("reason", "").lower())

    def test_run_comparison_all_arms(self):
        result = run_comparison(CATALOG, 8)
        self.assertEqual(set(result["arms"]), set(ARMS))

    def test_comparison_incomplete_without_jev(self):
        result = run_comparison(CATALOG, 8)
        self.assertFalse(result["comparison_complete"])
        self.assertEqual(result["outcome"], "incomplete-jev-unavailable")

    def test_validate_selections_passes(self):
        result = run_comparison(CATALOG, 8)
        validate_selections(result["arms"])

    def test_corrupt_arms_reject(self):
        with self.assertRaises(SelectorError):
            validate_selections({"deterministic": {}})

    def test_equal_budget(self):
        result = run_comparison(CATALOG, 8)
        for arm in ("deterministic", "random"):
            self.assertEqual(result["arms"][arm]["budget"], 8)

    def test_catalog_freeze_digest_bound(self):
        result = run_comparison(CATALOG, 8)
        self.assertEqual(result["corpus_freeze_digest"], CORPUS_FREEZE_DIGEST)


if __name__ == "__main__":
    unittest.main()
