"""Real no-guest smoke boundaries; no root/VM identity substitution or skipped proof."""
import os
import importlib.machinery
import importlib.util
from pathlib import Path
import signal
import subprocess
import sys
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'research'))
from common import Failure
from replay_smoke import (SCOPE, CHALLENGE, SmokeExecutor, scope_event, validate_scope,
                          runner, evaluator, launch, cease_groups, present_groups, validate_result)


class RuntimeSmoke(unittest.TestCase):
    def test_installed_closure_is_exact_and_bytes_match(self):
        loader = importlib.machinery.SourceFileLoader('smoke_root_contract', str(ROOT / 'scripts/replay-root-prepare'))
        module = importlib.util.module_from_spec(importlib.util.spec_from_loader(loader.name, loader))
        loader.exec_module(module)
        self.assertEqual(set(module.CODE), {'budget.py', 'ledger.py', 'replay_smoke.py',
                         'replay_runtime.py', 'common.py', 'corpus_execution.py', 'execution.py',
                         'trusted_execution.py', 'trusted_install.py', 'trusted_transport.py',
                         'validated_corpus.py', 'replay_prerequisites.py'})
        for name, hashed in module.CODE.items():
            self.assertEqual(module.sha((ROOT / 'research' / name).read_bytes()), hashed)

    def test_incomplete_or_unbound_results_fail_before_protected_reads(self):
        request = {'run': 'smoke', 'key': 'key', 'reservation': 'reservation'}
        value = dict(request, ceased=True, transport_complete=True, forced=False,
                     error=None, exit_code=0, seconds=1)
        for key, invalid in (('run', 'other'), ('reservation', 'other'), ('ceased', False),
                             ('transport_complete', False), ('forced', True), ('exit_code', 1),
                             ('seconds', float('nan')), ('seconds', 481), ('seconds', True)):
            with self.subTest(key=key), self.assertRaises(Failure):
                validate_result(dict(value, **{key: invalid}), request)

    def test_exact_c001_scope_and_numeric_types(self):
        self.assertEqual(validate_scope(dict(SCOPE)), SCOPE)
        for key in SCOPE:
            altered = dict(SCOPE)
            altered[key] = 'unapproved'
            with self.subTest(key=key), self.assertRaises(Failure):
                validate_scope(altered)
        for altered in (dict(SCOPE, attempts=True), dict(SCOPE, work_seconds=475),
                        dict(SCOPE, challenge='GRRR-VC-D001'), dict(SCOPE, total_seconds=481),
                        dict(SCOPE, extra=True)):
            with self.assertRaises(Failure):
                validate_scope(altered)

    def test_evidence_cannot_be_promoted_or_relabeled(self):
        result = scope_event('runtime-smoke-complete', children_ceased=True)
        self.assertEqual(result['challenge'], CHALLENGE)
        self.assertFalse(result['independent_replay_authorized'])
        self.assertFalse(result['contract_admission_authorized'])
        for key in ('verdict', 'verified', 'ReplayReceipt', 'admission', 'scope',
                    'independent_replay_authorized', 'contract_admission_authorized'):
            with self.subTest(key=key), self.assertRaises(Failure):
                scope_event('runtime-smoke-complete', **{key: True})
        with self.assertRaises(Failure):
            scope_event('ReplayReceipt')

    def test_actual_unprivileged_identity_refused_before_effects(self):
        self.assertNotIn(os.getuid(), (0, 320, 321))
        for action in (SmokeExecutor, runner, evaluator, lambda: launch(None, {}, {})):
            with self.subTest(action=action), self.assertRaises(Failure):
                action()
        executor = object.__new__(SmokeExecutor)
        with self.assertRaises(Failure):
            executor.spawn_guest(['/nonexistent/unapproved-executable'])

    def test_script_roles_and_parent_mode_refuse_operator(self):
        for mode in ('--runtime-smoke', '--smoke-runner', '--smoke-evaluator'):
            result = subprocess.run([sys.executable, '-I', '-S', '-B',
                                     str(ROOT / 'scripts/replay-root-prepare'), mode],
                                    capture_output=True, timeout=10)
            self.assertEqual(result.returncode, 1)
            self.assertIn(b'"execution_authorized":false', result.stdout)

    def test_real_service_and_child_process_group_cessation(self):
        self.assert_process_group_ceased('--spawn')

    def test_real_term_resistant_group_is_killed_within_deadline(self):
        self.assert_process_group_ceased('--ignore-term')

    def assert_process_group_ceased(self, mode):
        process = subprocess.Popen([sys.executable, '-I', '-S', '-B',
                                    str(ROOT / 'tests/replay_smoke_process_probe.py'), mode],
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                                   env={'PATH': '/usr/bin:/bin', 'LC_ALL': 'C'}, start_new_session=True)
        try:
            # Child PID line is emitted only after the real same-group child starts.
            child = int(process.stdout.readline())
            self.assertEqual(os.getpgid(child), process.pid)
            started = time.monotonic()
            self.assertTrue(cease_groups([process], time.monotonic() + 7))
            self.assertLess(time.monotonic() - started, 7)
            if mode == '--ignore-term':
                self.assertEqual(process.returncode, -signal.SIGKILL)
            self.assertIsNotNone(process.poll())
            self.assertFalse(present_groups({process.pid}, time.monotonic() + 1))
        finally:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except (ProcessLookupError, PermissionError):
                process.poll()
            process.wait(timeout=3)
            process.stdout.close()
            process.stderr.close()


if __name__ == '__main__':
    unittest.main()
