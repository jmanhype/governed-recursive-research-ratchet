import json
import importlib.util
import importlib.machinery
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from contextlib import ExitStack
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "research"))

from harness_adaptation import (
    AdaptationCycleError,
    evaluate_candidate,
    run_adaptation_cycle,
)


PLAN = ROOT / "corpus/evaluation-plan-v2-proposed.json"
RESULT = ROOT / "docs/evidence/jev-selector-measurement/three-arm-result-20261103T214701Z/report.json"
CORPUS = ROOT / "corpus"
TRUTH = CORPUS / "protected/truth.json"


def load_truth():
    return {
        row["challenge"]: row
        for row in json.loads(TRUTH.read_text(encoding="utf-8"))
    }


def real_report():
    return run_adaptation_cycle(PLAN, RESULT, CORPUS)


def run_cli(output, summary):
    return subprocess.run([
        sys.executable, str(ROOT / "scripts/run-harness-adaptation-cycle"),
        "--plan", str(PLAN), "--result", str(RESULT),
        "--corpus-root", str(CORPUS), "--output", str(output),
        "--summary-output", str(summary),
    ], cwd=ROOT, text=True, capture_output=True)


def load_cli_module():
    path = ROOT / "scripts/run-harness-adaptation-cycle"
    loader = importlib.machinery.SourceFileLoader(path.name, str(path))
    spec = importlib.util.spec_from_file_location(path.name, path, loader=loader)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class HarnessAdaptationTest(unittest.TestCase):
    def test_exact_input_binding_and_fixed_proposals(self):
        report = real_report()
        expected = {
            ("approved_plan", "sha256"): "97ec4b8ccc34b3fc4da4fcfbef33b49bbb3f4f1c445cfecdb752715ddf034be1",
            ("completed_result", "sha256"): "b7bb2ec8717e8921e16f9a3e312f6ad46839a125634dc6e3d144499cc841fefb",
            ("protected_truth", "sha256"): "7cf9f99f5836c4e3e147df2866d54480a706f2665a732fbf61bd1a0d0b4c52ea",
            ("frozen_corpus", "freeze_digest"): "dfa75ef2bf3d43fd4f750094fe643afe4f204812c0ae2426276bedb471fa8529",
            ("frozen_corpus", "manifest_sha256"): "32fb59c74ea96653c50e3deea0d66474bafdd78caf96c3e9c4c589aba703e354",
            ("frozen_corpus", "public_projection_sha256"): "c6aa57a2eb595fd2fe35ae817295df2220738b8538755826c5af11af648fd361",
        }
        for (section, field), value in expected.items():
            self.assertEqual(report["inputs"][section][field], value)
        self.assertEqual([item["proposal_id"] for item in report["proposals"]], [
            "reverse-lexical", "random-block-45-46-47"
        ])
        self.assertTrue(all(item["fixed"] for item in report["proposals"]))
        self.assertEqual(report["proposals"][1]["seeds"], [45, 46, 47])
        self.assertEqual(report["proposals"][1]["selection_mode"], "evaluate-all-repetitions")

    def test_reverse_lexical_scores_eight_but_leakage_rejects(self):
        report = real_report()
        reverse = report["proposals"][0]
        expected_ids = [f"GRRR-VC-D{number:03}" for number in range(24, 16, -1)]
        self.assertEqual(reverse["selected_ids"], expected_ids)
        self.assertEqual(reverse["measured"]["primary_true_defects"], 8)
        self.assertEqual(reverse["measured"]["primary_mean"], 8.0)
        self.assertTrue(reverse["leakage"]["rejected"])
        self.assertFalse(reverse["leakage"]["score_may_override"] or reverse["eligible"])

    def test_fixed_random_block_metrics_and_honest_comparison(self):
        report = real_report()
        block = report["proposals"][1]
        self.assertEqual(
            [item["true_defect_count"] for item in block["repetitions"]], [4, 6, 4]
        )
        self.assertEqual(block["measured"], {
            "primary_mean": round(14 / 3, 6),
            "critical_mean": round(10 / 3, 6),
            "clean_mean": round(10 / 3, 6),
            "unique_defect_count": 12,
        })
        self.assertEqual(report["benchmark"]["mean"], 6.0)
        self.assertEqual(report["benchmark"]["repetition_values"], [6, 6, 6])
        self.assertFalse(block["exceeds_benchmark"])

    def test_no_compose_default_and_false_authority(self):
        report = real_report()
        self.assertEqual(report["compose"]["action"], "no-change")
        self.assertIsNone(report["compose"]["composed_strategy"])
        self.assertEqual(report["compose"]["approved_default"], "retain-deterministic-lexical-baseline")
        self.assertFalse(any(report["authority"].values()))
        self.assertTrue(report["controls"]["no_automatic_rerun"])
        self.assertEqual(report["controls"]["model_calls"], 0)

    def test_plan_result_and_truth_tampering_fails_closed(self):
        with tempfile.TemporaryDirectory() as name:
            temp = Path(name)
            plan = temp / "plan.json"
            result = temp / "result.json"
            shutil.copyfile(PLAN, plan)
            shutil.copyfile(RESULT, result)
            plan.write_bytes(PLAN.read_bytes() + b" ")
            with self.assertRaisesRegex(AdaptationCycleError, "plan bytes differ"):
                run_adaptation_cycle(plan, RESULT, CORPUS)
            result.write_bytes(RESULT.read_bytes() + b"\n")
            with self.assertRaisesRegex(AdaptationCycleError, "result bytes differ"):
                run_adaptation_cycle(PLAN, result, CORPUS)
            corpus = temp / "corpus"
            shutil.copytree(CORPUS, corpus)
            truth_path = corpus / "protected/truth.json"
            truth_path.write_bytes(TRUTH.read_bytes() + b" ")
            with self.assertRaisesRegex(AdaptationCycleError, "truth bytes differ"):
                run_adaptation_cycle(PLAN, RESULT, corpus)
            manifest_path = corpus / "manifest.json"
            truth_path.write_bytes(TRUTH.read_bytes())
            manifest_path.write_bytes(manifest_path.read_bytes() + b" ")
            with self.assertRaisesRegex(
                AdaptationCycleError, "frozen corpus identity differs"
            ):
                run_adaptation_cycle(PLAN, RESULT, corpus)

    def test_malformed_selection_and_declared_candidate_leakage_fail(self):
        truth = load_truth()
        catalog = sorted(truth)
        malformed = {"selected": catalog[:7], "leakage_inputs": []}
        with self.assertRaisesRegex(AdaptationCycleError, "malformed selection"):
            evaluate_candidate(malformed, catalog, truth)
        malformed["selected"] = catalog[:7] + ["not-in-catalog"]
        with self.assertRaisesRegex(AdaptationCycleError, "malformed selection"):
            evaluate_candidate(malformed, catalog, truth)
        leaked = {"selected": catalog[:8], "leakage_inputs": ["D/C-local-ID-prefix"]}
        evaluated = evaluate_candidate(leaked, catalog, truth)
        self.assertTrue(evaluated["leakage"]["rejected"])
        self.assertFalse(evaluated["eligible"])

    def test_undeclared_reverse_lexical_leakage_is_detected(self):
        truth = load_truth()
        catalog = sorted(truth)
        reverse = sorted(catalog, reverse=True)[:8]
        undeclared = evaluate_candidate({"selected": reverse, "leakage_inputs": []}, catalog, truth)
        self.assertTrue(undeclared["leakage"]["rejected"])
        self.assertEqual(undeclared["leakage"]["inputs"], ["D/C-local-ID-prefix"])
        self.assertFalse(undeclared["eligible"])

    def test_defect_composition_alone_does_not_trigger_leakage(self):
        truth = load_truth()
        catalog = sorted(truth)
        defect_ids = sorted(item for item in catalog if truth[item]["truth"] == "defect")
        evaluated = evaluate_candidate(
            {"selected": defect_ids[:8], "leakage_inputs": []}, catalog, truth
        )
        self.assertEqual(evaluated["metrics"]["defect_count"], 8)
        self.assertFalse(evaluated["leakage"]["rejected"])
        self.assertTrue(evaluated["eligible"])

    def test_protected_paths_reject_before_path_syscalls(self):
        cli = load_cli_module()
        unsafe_paths = [
            Path("/Library/GRRR/adaptation.json"),
            Path("/Library//GRRR/adaptation.json"),
            Path("//Library/GRRR/adaptation.json"),
            Path("/tmp/../Library/GRRR/adaptation.json"),
            Path("/Library/GRRR/../../tmp/adaptation.json"),
            "/Library/GRRR/adaptation\0.json",
        ]
        guards = [
            mock.patch.object(cli.os.path, "realpath"),
            mock.patch.object(cli.os.path, "normpath"),
            mock.patch.object(cli.os.path, "abspath"),
            mock.patch.object(cli.os, "stat"),
            mock.patch.object(cli.os, "lstat"),
            mock.patch.object(cli.os, "readlink"),
            mock.patch.object(cli.os, "open"),
        ]
        with ExitStack() as stack:
            active_guards = [stack.enter_context(guard) for guard in guards]
            for path in unsafe_paths:
                self.assertTrue(cli.protected_path(path))
            for guard in active_guards:
                guard.assert_not_called()

    def test_unsafe_and_duplicate_outputs_fail_closed(self):
        unsafe = Path("/Library/GRRR/adaptation.json")
        with tempfile.TemporaryDirectory() as name:
            physical = Path(name).resolve()
            summary = physical / "summary.md"
            refused = run_cli(unsafe, summary)
            self.assertEqual(refused.returncode, 2)
            self.assertIn("unsafe or protected output", refused.stderr)
            self.assertFalse(summary.exists())
            output = physical / "report.json"
            output.touch()
            duplicate = run_cli(output, summary)
            self.assertEqual(duplicate.returncode, 2)
            self.assertIn("JSON output already", duplicate.stderr)
            self.assertFalse(summary.exists())

    def test_non_immediate_symlink_ancestor_fails_closed(self):
        with tempfile.TemporaryDirectory() as name:
            physical = Path(name).resolve()
            target = physical / "real" / "nested"
            target.mkdir(parents=True)
            (target / "sub").mkdir()
            link = physical / "link"
            link.symlink_to(target, target_is_directory=True)
            output = link / "sub" / "cycle.json"
            summary = physical / "cycle.md"
            refused = run_cli(output, summary)
            self.assertEqual(refused.returncode, 2, refused.stderr)
            self.assertIn("unsafe output ancestor", refused.stderr)
            self.assertFalse(output.exists() or summary.exists())

    def test_markdown_reservation_race_preserves_all_entries(self):
        cli = load_cli_module()
        with tempfile.TemporaryDirectory() as name:
            physical = Path(name).resolve()
            output = physical / "cycle.json"
            summary = physical / "cycle.md"
            concurrent_markdown = b"concurrent operator markdown\n"
            original_validation = cli._validated_parents
            markdown_before_failure = None

            def create_markdown_during_validation(json_path, markdown_path):
                validated = original_validation(json_path, markdown_path)
                markdown_path.write_bytes(concurrent_markdown)
                nonlocal markdown_before_failure
                markdown_before_failure = markdown_path.read_bytes()
                return validated

            with mock.patch.object(
                cli, "_validated_parents", side_effect=create_markdown_during_validation
            ):
                with self.assertRaises(FileExistsError):
                    cli.write_outputs(real_report(), output, summary)

            self.assertEqual(output.read_bytes(), b"")
            markdown_after_failure = summary.read_bytes()
            self.assertEqual(markdown_before_failure, concurrent_markdown)
            self.assertEqual(markdown_after_failure, markdown_before_failure)

    def test_reservation_failure_never_deletes_entries_not_created_here(self):
        cli = load_cli_module()
        with tempfile.TemporaryDirectory() as name:
            physical = Path(name).resolve()
            output = physical / "cycle.json"
            summary = physical / "cycle.md"
            concurrent_json = b"concurrent JSON reservation\n"
            concurrent_markdown = b"concurrent Markdown reservation\n"
            original_validation = cli._validated_parents
            json_before_failure = markdown_before_failure = None

            def create_both_during_validation(json_path, markdown_path):
                validated = original_validation(json_path, markdown_path)
                json_path.write_bytes(concurrent_json)
                markdown_path.write_bytes(concurrent_markdown)
                nonlocal json_before_failure, markdown_before_failure
                json_before_failure = json_path.read_bytes()
                markdown_before_failure = markdown_path.read_bytes()
                return validated

            with mock.patch.object(
                cli, "_validated_parents", side_effect=create_both_during_validation
            ):
                with self.assertRaises(FileExistsError):
                    cli.write_outputs(real_report(), output, summary)

            json_after_failure = output.read_bytes()
            markdown_after_failure = summary.read_bytes()
            self.assertEqual(json_before_failure, concurrent_json)
            self.assertEqual(markdown_before_failure, concurrent_markdown)
            self.assertEqual(json_after_failure, json_before_failure)
            self.assertEqual(markdown_after_failure, markdown_before_failure)

    def test_lexical_traversal_output_fails_closed(self):
        with tempfile.TemporaryDirectory() as name:
            physical = Path(name).resolve()
            safe = physical / "safe"
            safe.mkdir()
            output = f"{safe}/../safe/cycle.json"
            summary = physical / "cycle.md"
            refused = run_cli(output, summary)
            self.assertEqual(refused.returncode, 2, refused.stderr)
            self.assertIn("unsafe or protected output", refused.stderr)
            self.assertFalse((safe / "cycle.json").exists() or summary.exists())

    def test_real_cli_generates_deterministic_sanitized_outputs(self):
        with tempfile.TemporaryDirectory() as name:
            physical = Path(name).resolve()
            output = physical / "cycle.json"
            summary = physical / "cycle.md"
            completed = run_cli(output, summary)
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertIn('"compose":"no-change"', completed.stdout)
            report = json.loads(output.read_text(encoding="ascii"))
            self.assertEqual(report, real_report())
            markdown = summary.read_text(encoding="ascii")
            self.assertIn("no composed strategy change", markdown)
            self.assertIn("8/8", markdown)
            self.assertIn("14/3", markdown)
            combined = (output.read_text() + markdown).lower()
            for forbidden in ("expected_behavior", "raw provider response", "/library/grrr"):
                self.assertNotIn(forbidden, combined)
            duplicate = run_cli(output, summary)
            self.assertEqual(duplicate.returncode, 2)
            self.assertIn("already exists", duplicate.stderr)


if __name__ == "__main__":
    unittest.main()
