"""Mandatory suite: actual evaluator identity, actual store, no skipped success.

Supervisor-dependent execution remains explicitly blocked pending authorization.
BudgetChecks uses actual SQLite and no mocks; only the separate BudgetUnit class
substitutes identity, and that class is never collected here.
"""
import json
import os
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'research'))
sys.path.insert(0, str(ROOT / 'tests'))
from common import EVALUATOR, Failure, require
from unit_trusted_observation import BudgetChecks


class ActualIdentityBudget(BudgetChecks, unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        require(os.getuid() == EVALUATOR, 'Unauthorized',
                'AWAITING_PARENT_IDENTITY_RUN: actual evaluator UID 320 required')


class MandatoryGuestObservation(unittest.TestCase):
    def test_approved_pinned_supervisor_and_guest_controls(self) -> None:
        proposal = json.loads((ROOT / 'docs/TRUSTED-OBSERVATION-PROFILE-PROPOSAL.json').read_bytes())
        require(proposal['authorization'] == 'approved' and proposal['dispatch_enabled'] is True,
                'GateBlocked', 'Trusted-observation supervisor profile is proposal-only; mandatory guest gates not-run')
        # Editing a draft cannot manufacture launch authority. Until reviewed
        # implementation exists, even a relabeled proposal remains blocked.
        raise Failure('GateBlocked', 'No registered trusted-observation supervisor executor exists')


if __name__ == '__main__':
    suite = unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromTestCase(cls)
                               for cls in (ActualIdentityBudget, MandatoryGuestObservation))
    required = suite.countTestCases()
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print(json.dumps({'required': required, 'executed': result.testsRun,
                      'skipped': len(result.skipped), 'failures': len(result.failures),
                      'errors': len(result.errors), 'mandatory_guest_gate': 'not-run'}))
    raise SystemExit(0 if result.wasSuccessful() and result.testsRun == required and not result.skipped else 1)
