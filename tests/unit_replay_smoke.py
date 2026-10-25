"""Real no-guest smoke boundaries; no root/VM identity substitution or skipped proof."""
import os
import importlib.machinery
import importlib.util
from pathlib import Path
import signal
import subprocess
import sys
import time
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'research'))
from common import Failure
from replay_prerequisites import (PREPARED_MODE, read_private_file, private_record,
                                  approved_account_groups, validate_service_groups, ACCOUNT_NAMES)
from replay_smoke import (SCOPE, CHALLENGE, SmokeExecutor, scope_event, validate_scope,
                          runner, evaluator, launch, cease_groups, present_groups, validate_result)


class RuntimeSmoke(unittest.TestCase):
    def test_real_macos_account_vectors_and_nonmember_rejection(self):
        for uid in (320, 321):
            observed = {int(value) for value in subprocess.check_output(
                ['/usr/bin/id', '-G', ACCOUNT_NAMES[uid]]).split()}
            self.assertEqual(observed, {uid, 12, 61, 100, 701})
            self.assertEqual(approved_account_groups(uid), observed)
            validate_service_groups(uid, list(observed))
            for extra in (0, 20, 80, 501, 99999, 641 - uid):
                with self.subTest(uid=uid, extra=extra), self.assertRaises(Failure):
                    validate_service_groups(uid, list(observed | {extra}))
            with self.assertRaises(Failure):
                validate_service_groups(uid, [uid])

    def test_prepared_private_record_contract(self):
        self.assertEqual(PREPARED_MODE, 0o400)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'prepared.json'
            path.write_bytes(b'{"root_installation":"prepared"}')
            path.chmod(PREPARED_MODE)
            self.assertEqual(read_private_file(path, os.getuid(), os.getgid()), path.read_bytes())
            with self.assertRaises(Failure):
                private_record(path)  # User-owned fixture is not root-positive proof.
            for mode in (0o444, 0o600):
                path.chmod(mode)
                with self.assertRaises(Failure):
                    read_private_file(path, os.getuid(), os.getgid())
            path.chmod(PREPARED_MODE)
            link = Path(directory) / 'link'
            link.symlink_to(path)
            with self.assertRaises(Failure):
                read_private_file(link, os.getuid(), os.getgid())
            subprocess.run(['/bin/chmod', '+a', 'everyone allow read', str(path)], check=True)
            try:
                with self.assertRaises(Failure):
                    read_private_file(path, os.getuid(), os.getgid())
            finally:
                subprocess.run(['/bin/chmod', '-N', str(path)], check=True)
        source = (ROOT / 'scripts/replay-root-prepare').read_text()
        self.assertIn("'verdict_engine': 'not-installed'}), 0, PREPARED_MODE)", source)

    def test_real_early_stop_registers_and_ceases_child(self):
        result = subprocess.run([sys.executable, '-I', '-S', '-B',
                                str(ROOT / 'tests/replay_smoke_process_probe.py'), '--early-stop'],
                               capture_output=True, timeout=12, env={'PATH': '/usr/bin:/bin', 'LC_ALL': 'C'})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(b'registered-before-stop; no-orphan', result.stdout)

    def test_exhausted_observation_still_kills_term_resistant_group(self):
        self.assert_process_group_ceased('--ignore-term', exhausted=True)

    def test_installed_closure_is_exact_and_bytes_match(self):
        loader = importlib.machinery.SourceFileLoader('smoke_root_contract', str(ROOT / 'scripts/replay-root-prepare'))
        module = importlib.util.module_from_spec(importlib.util.spec_from_loader(loader.name, loader))
        loader.exec_module(module)
        self.assertEqual(set(module.CODE), {'budget.py', 'persistent_budget.py', 'accounting_registration.py', 'accounting_recovery.py', 'ledger.py', 'replay_smoke.py', 'replay.py', 'corpus_evaluation.py',
                         'replay_runtime.py', 'common.py', 'corpus_execution.py', 'execution.py',
                         'trusted_execution.py', 'trusted_install.py', 'trusted_transport.py',
                         'validated_corpus.py', 'replay_prerequisites.py',
                         'replay_profile.py', 'replay_fixtures.py', 'corpus_probes.py'})
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

    def assert_process_group_ceased(self, mode, exhausted=False):
        process = subprocess.Popen([sys.executable, '-I', '-S', '-B',
                                    str(ROOT / 'tests/replay_smoke_process_probe.py'), mode],
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                                   env={'PATH': '/usr/bin:/bin', 'LC_ALL': 'C'}, start_new_session=True)
        try:
            # Child PID line is emitted only after the real same-group child starts.
            child = int(process.stdout.readline())
            self.assertEqual(os.getpgid(child), process.pid)
            started = time.monotonic()
            ceased = cease_groups([process], time.monotonic() - 1 if exhausted else time.monotonic() + 7)
            self.assertEqual(ceased, not exhausted)
            process.wait(timeout=2)
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
