"""Observation failure regressions; real unprivileged process-group kill proof."""
import signal
import subprocess
import time
import unittest
from unittest.mock import patch, Mock

import unit_replay_smoke as smoke_tests
import replay_smoke as smoke
from common import Failure


class CessationObservation(unittest.TestCase):
    def test_transient_term_inventory_timeout_advances_to_real_kill_and_absence(self):
        original = smoke.present_groups
        observations = []
        def observe(groups, deadline):
            if not observations:
                observations.append('timeout')
                raise subprocess.TimeoutExpired(['/bin/ps'], 0.2)
            result = original(groups, deadline)
            observations.append(result)
            return result
        # The unchanged integration-style assertion verifies actual SIGKILL exit,
        # elapsed <7s and actual process-group absence; only one observation fails.
        with patch.object(smoke, 'present_groups', observe):
            smoke_tests.RuntimeSmoke.assert_process_group_ceased(self, '--ignore-term')
        self.assertEqual(observations[0], 'timeout')
        self.assertIn(set(), observations[1:])

    def test_persistent_unknown_observation_never_reports_success(self):
        process = Mock(pid=12345)
        with patch.object(smoke.os, 'killpg') as kill, \
             patch.object(smoke, 'present_groups', side_effect=subprocess.TimeoutExpired('ps', 0.2)):
            self.assertFalse(smoke.cease_groups([process], time.monotonic() + 7))
        self.assertEqual(kill.call_args_list, [unittest.mock.call(12345, signal.SIGTERM),
                                              unittest.mock.call(12345, signal.SIGKILL)])

    def test_exhausted_deadline_still_kills_but_never_claims_success(self):
        process = Mock(pid=12345)
        with patch.object(smoke.os, 'killpg') as kill, patch.object(smoke, 'present_groups') as observe:
            self.assertFalse(smoke.cease_groups([process], time.monotonic() - 1))
        observe.assert_not_called()
        self.assertEqual(kill.call_args_list[-1], unittest.mock.call(12345, signal.SIGKILL))

    def test_final_inventory_arriving_after_deadline_is_not_proof(self):
        output = subprocess.CompletedProcess([], 0, stdout=b'1 1\n')
        with patch.object(smoke.time, 'monotonic', side_effect=[1.0, 3.0]), \
             patch.object(smoke.subprocess, 'run', return_value=output):
            with self.assertRaises(Failure):
                smoke.present_groups({12345}, 2.0)

    def test_malformed_or_empty_inventory_is_uncertain(self):
        for raw in (b'', b'bad inventory\n', b'1 2 3\n'):
            output = subprocess.CompletedProcess([], 0, stdout=raw)
            with patch.object(smoke.subprocess, 'run', return_value=output), self.assertRaises(Failure):
                smoke.present_groups({12345}, time.monotonic() + 7)
