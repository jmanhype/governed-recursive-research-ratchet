"""Real committed evidence, no fake receipts or database creation."""
from pathlib import Path
import runpy
import unittest

ROOT = Path(__file__).resolve().parents[1]


class Genesis(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = runpy.run_path(str(ROOT / 'scripts/propose-accounting-genesis'))['proposal'](ROOT)

    def test_all_attempts_and_sources_are_preserved(self):
        self.assertEqual(len(self.report['attempts']), 12)
        self.assertTrue(self.report['measurements'])
        self.assertTrue(all(row['sources'] for row in self.report['events']))
        self.assertEqual(len({row['event_sha256'] for row in self.report['events']}),
                         len(self.report['events']))

    def test_unknowns_encumber_both_ceilings_without_fake_upper_bound(self):
        self.assertEqual(self.report['bounds']['poc']['conservative_admission_hold']['review_us'], 3600_000000)
        self.assertEqual(self.report['bounds']['milestone']['conservative_admission_hold']['review_us'], 10800_000000)
        for bound in self.report['bounds'].values():
            self.assertIsNone(bound['historical_usage_upper_bound'])
            self.assertFalse(bound['lower_bound_authoritative'])

    def test_no_migration_or_campaign_stop_inference(self):
        self.assertFalse(self.report['migration_authorized'])
        self.assertFalse(self.report['database_created'])
        self.assertIsNone(self.report['campaign_stop_state'])
        self.assertEqual(self.report['execution_gate'], 'blocked')
        for event in self.report['events']:
            if str(event['kind']).startswith('stop-') and event['run']:
                self.assertEqual(event['stop_scope'], 'run')
