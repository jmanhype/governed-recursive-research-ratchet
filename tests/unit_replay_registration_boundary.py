"""Pure boundary tests; no registered binding can imply replay authorization."""
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'research'))
from common import Failure
from persistent_budget import PROFILES, REGISTERED_PROFILES
from replay import MODES, ParentProtocol, preflight


class RegistrationBoundary(unittest.TestCase):
    def test_legacy_registration_and_unknown_versions_all_fail_closed(self) -> None:
        bindings = [
            {'version': 1, 'profiles': list(PROFILES)},
            {'version': 2, 'profiles': list(REGISTERED_PROFILES)},
            {'version': 3, 'profiles': list(REGISTERED_PROFILES)},
            {'version': True, 'profiles': list(REGISTERED_PROFILES)},
        ]
        for binding in bindings:
            with self.subTest(binding=binding), patch('replay.root_record', return_value=binding):
                with self.assertRaises(Failure) as caught:
                    preflight()
                self.assertEqual(caught.exception.record['code'], 'GateBlocked')

    def test_registered_modes_refuse_before_input_access(self) -> None:
        binding = {'version': 2, 'profiles': list(REGISTERED_PROFILES)}
        for mode in MODES:
            with self.subTest(mode=mode), patch('replay.root_record', return_value=binding), \
                    patch('replay.replay_profile.validate_inputs') as inputs:
                with self.assertRaises(Failure) as caught:
                    ParentProtocol(mode).preflight()
                self.assertIn('registration-only and frozen', str(caught.exception))
                inputs.assert_not_called()

    def test_stop_only_recovery_refuses_every_mode_before_inputs_or_mutation(self) -> None:
        binding = {'version': 3, 'profiles': list(REGISTERED_PROFILES),
                   'recovery_sha256': 'a' * 64}
        # The active binding does not itself carry spendability/stop authority;
        # v3's reviewed contract is read-only even when recovery cleared stop.
        for mode in MODES:
            with self.subTest(mode=mode), patch('replay.root_record', return_value=binding), \
                    patch('replay.replay_profile.validate_inputs') as inputs, \
                    patch('replay.PersistentBudget') as budget:
                with self.assertRaises(Failure) as caught:
                    ParentProtocol(mode).preflight()
                self.assertEqual(caught.exception.record['code'], 'GateBlocked')
                self.assertIn('v3 is stop-only read-only', str(caught.exception))
                inputs.assert_not_called()
                budget.assert_not_called()


if __name__ == '__main__':
    unittest.main(verbosity=2)
