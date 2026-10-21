"""Reconciliation reports never authorize spend or convert unknowns to zero."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'research'))
from accounting_reconciliation import micros, summarize
from common import Failure


class Reconciliation(unittest.TestCase):
    def event(self, **changes):
        event = {'kind': 'reserved', 'reservation': 'r1', 'run': 'run1',
                 'maximum_seconds': 300, 'money_cents': 0, 'review_seconds': None}
        event.update(changes)
        return {'source': 'accepted.json', 'event': event}

    def test_empty_and_complete_looking_input_stay_blocked(self):
        for events in ([], [self.event(review_seconds=1)]):
            report = summarize(events)
            self.assertEqual(report['execution_gate'], 'blocked')
            self.assertFalse(report['migration_authorized'])
            self.assertIsNone(report['campaign_totals'])
            self.assertIsNone(report['remaining_allowance'])
            self.assertTrue(report['unresolved_history'])

    def test_duplicate_snapshot_not_double_counted(self):
        report = summarize([self.event(), self.event()])
        self.assertEqual(len(report['known_legacy_reservations']), 1)
        row = report['known_legacy_reservations'][0]
        self.assertEqual(row['maximum_execution_us'], 300_000_000)
        self.assertIsNone(row['reported_review_seconds'])
        self.assertFalse(row['settled'])

    def test_conflicting_reservation_not_chosen_as_authority(self):
        report = summarize([self.event(), self.event(maximum_seconds=400)])
        self.assertEqual(len(report['conflicts']), 1)
        self.assertFalse(report['migration_authorized'])

    def test_stop_ack_does_not_clear_campaign_stop(self):
        report = summarize([self.event(kind='stop-outcome', outcome={'ceased': True})])
        self.assertIsNone(report['campaign_stop_state'])
        self.assertEqual(len(report['known_stop_events']), 1)

    def test_unmapped_legacy_reservation_is_preserved_not_invented(self):
        item = self.event()
        del item['event']['reservation']
        report = summarize([item])
        self.assertEqual(report['conflicts'][0]['kind'], 'unmapped_legacy_reservation')
        self.assertEqual(report['conflicts'][0]['reported_maximum_seconds'], 300)
        self.assertIsNone(report['conflicts'][0]['reported_reserved_total_seconds'])
        self.assertEqual(report['known_legacy_reservations'], [])
        self.assertTrue(report['unresolved_history'])

    def test_invalid_or_unknown_maxima_rejected(self):
        for value in (None, True, -1, 0, 1.5, '300', 2**63):
            with self.subTest(value=value), self.assertRaises(Failure):
                summarize([self.event(maximum_seconds=value)])

    def test_duration_conversion_and_nonfinite_rejection(self):
        self.assertEqual(micros('1.0000001'), '1000000.1000000')
        for value in (True, -1, 'NaN', 'Infinity', 10**20):
            with self.subTest(value=value), self.assertRaises(Failure):
                micros(value)

    def test_forged_pass_and_cost_do_not_settle(self):
        report = summarize([self.event(kind='observation', execution_seconds=None,
                                      raw='PASS', verified=True)])
        row = report['known_legacy_observations'][0]
        self.assertIsNone(row['reported_execution_us'])
        self.assertFalse(row['settlement_authorized'])
        self.assertNotIn('raw', row)
