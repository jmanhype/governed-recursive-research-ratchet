"""Real CLI checks for the blocked checklist, not the protected capstone journey.

No mocks, candidate execution, network calls, credentials, or protected paths.
Disposable Git repositories exercise unavailable/corrupted provenance honestly.
"""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
FILES = ('scripts/test-story', 'tests/e2e/milestone.py',
         'docs/evidence/milestone-packet/evidence-index.json')


def invoke(root: Path, *args: str) -> subprocess.CompletedProcess:
    """Invoke exactly the operator entrypoint under the current interpreter."""
    return subprocess.run([sys.executable, '-B', str(root / 'scripts/test-story'),
                           'milestone-e2e', *args], cwd=root, capture_output=True,
                          text=True, timeout=120)


class ChecklistCLI(unittest.TestCase):
    """Outcome-level checks for evidence enumeration and fail-closed status."""

    def assert_blocked(self, result: subprocess.CompletedProcess) -> dict:
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertEqual(result.stderr, '')
        report = json.loads(result.stdout)
        self.assertEqual(report['decision'], 'blocked')
        self.assertFalse(report['verified'])
        self.assertEqual(report['effect'], 'none')
        self.assertEqual(len(report['gates']), 11)
        self.assertEqual({item['id'] for item in report['acceptance_criteria']},
                         {'AC1', 'AC2', 'AC3', 'AC4', 'AC5', 'AC6', 'AC7'})
        for item in report['gates'] + report['acceptance_criteria']:
            self.assertEqual(item['status'], 'not-run')
            self.assertTrue(item['missing_evidence'])
        self.assertEqual(report['summary']['executed'], 0)
        self.assertEqual(report['summary']['passed'], 0)
        self.assertEqual(report['summary']['not_run'], 18)
        self.assertEqual(report['summary']['skipped'], 0)
        return report

    def test_operator_text_and_json_keep_missing_gates_blocked(self) -> None:
        report = self.assert_blocked(invoke(ROOT, '--json'))
        self.assertEqual(report['summary']['provenance_hash_matched'], 19)
        self.assertEqual(report['summary']['provenance_errors'], 0)
        text = invoke(ROOT)
        self.assertEqual(text.returncode, 1)
        self.assertEqual(text.stderr, '')
        for item in report['gates'] + report['acceptance_criteria']:
            self.assertIn(item['id'] + ': not-run', text.stdout)
            self.assertIn(item['missing_evidence'], text.stdout)
        self.assertIn('NOT a runtime E2E pass', text.stdout)

    def test_absent_historical_objects_never_hide_mandatory_inventory(self) -> None:
        with tempfile.TemporaryDirectory(prefix='grrr-capstone-cli-') as directory:
            root = Path(directory)
            for name in FILES:
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / name, target)
            subprocess.run(['git', 'init', '-q', str(root)], check=True, capture_output=True)
            report = self.assert_blocked(invoke(root, '--json'))
            self.assertEqual(report['summary']['provenance_hash_matched'], 0)
            self.assertEqual(report['summary']['provenance_errors'], 19)

    def test_malformed_index_never_hides_mandatory_inventory(self) -> None:
        with tempfile.TemporaryDirectory(prefix='grrr-capstone-cli-') as directory:
            root = Path(directory)
            for name in FILES:
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / name, target)
            (root / FILES[2]).write_text('{broken', encoding='utf-8')
            report = self.assert_blocked(invoke(root, '--json'))
            self.assertEqual(report['summary']['provenance_errors'], 1)

    def test_skip_or_execution_options_are_not_authority(self) -> None:
        for option in ('--skip-missing', '--allow-protected', '--execute'):
            with self.subTest(option=option):
                result = invoke(ROOT, option)
                self.assertEqual(result.returncode, 2)
                self.assertIn('unrecognized arguments', result.stderr)


if __name__ == '__main__':
    unittest.main(verbosity=2)
