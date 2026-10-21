"""Real installed read-only evidence; no copies/builds or privileged operations."""
from pathlib import Path
import runpy
import unittest


class InstalledReconciliation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        script = Path(__file__).resolve().parents[1] / 'scripts/reconcile-installed-accounting'
        cls.report = runpy.run_path(str(script))['inspect']()

    def test_pins_and_database_unchanged(self):
        row = self.report['installed']
        self.assertEqual(row['pins_before'], row['pins_after'])
        self.assertEqual(row['artifact_count'], 259)
        self.assertTrue(row['zero_reservations'])

    def test_unknowns_never_become_finite_upper_bound(self):
        self.assertTrue(all(v is None for v in self.report['historical_worst_case'].values()))
        self.assertEqual(self.report['migration_safety_stopped'], 1)
        self.assertIsNone(self.report['historical_campaign_stop'])
        self.assertFalse(self.report['mutation_performed'])

    def test_evidence_keys_and_attempts_preserved(self):
        self.assertEqual(len(self.report['attempts']), 12)
        for event in self.report['reservation_evidence']:
            self.assertIn(event['event_sha256'], self.report['reservation_event_maximum_seconds'])
            self.assertTrue(event['sources'])
