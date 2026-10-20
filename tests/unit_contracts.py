"""Supplementary pure-contract tests; do not substitute for real identity/VM suite."""
from pathlib import Path
import sys
import unittest
import os
import tempfile
import json
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'research'))
from common import Failure, GATES, PACKETS, canonical, digest, fields, identifier, runtime_binding, socket_path
from policy import default_policy
from runner import parser
from execution import isolation_verified


class Contracts(unittest.TestCase):
    def test_packet_identity_and_forged_pass_distinct(self) -> None:
        self.assertNotEqual(digest(canonical(PACKETS['clean'])), digest(canonical(PACKETS['faulty'])))
        self.assertEqual(PACKETS['clean']['command'], "printf 'CLEAN\\n'")

    def test_identifiers_reject_traversal(self) -> None:
        for value in ('../private', '/tmp/x', 'x\n', '', None):
            with self.assertRaises(Failure):
                identifier(value)

    def test_allowlist_rejects_roles_and_expected_answers(self) -> None:
        for name in ('role', 'expected', 'shell', 'token'):
            with self.assertRaises(Failure):
                fields({'action': 'start', name: 'x'}, {'action'})

    def test_registered_limits_and_inventory(self) -> None:
        policy = default_policy(501)
        self.assertEqual(policy['gates'], list(GATES))
        self.assertEqual(policy['limits']['challenge_seconds'], 300)
        self.assertFalse(policy['paid_dispatch'])

    def test_cli_exact_grammar(self) -> None:
        args = parser().parse_args(['decide', 'run1', '--action', 'admit-contract', '--target', 'a' * 64])
        self.assertEqual(args.action, 'decide')
        self.assertEqual(args.decision, 'admit-contract')

    def test_short_temporary_socket_path(self) -> None:
        path = Path('/private/tmp/grrr-unit/ipc/evaluator.sock')
        self.assertEqual(socket_path(path), str(path))

    def test_runtime_binding_is_local_and_restricted(self) -> None:
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[1]) as directory:
            root = Path(directory)
            path = root / '.runtime-endpoint.json'
            value = {'version': 1, 'runtime': '/private/tmp/grrr-unit',
                     'evidence': str(root / 'docs/evidence/bounded-challenge/attempt-unit')}
            path.write_bytes(canonical(value))
            os.chmod(path, 0o600)
            self.assertEqual(runtime_binding(root), value)
            os.chmod(path, 0o666)
            with self.assertRaises(Failure):
                runtime_binding(root)
            os.chmod(path, 0o600)
            path.write_bytes(canonical(dict(value, runtime='/Users/operator/Documents/runtime')))
            with self.assertRaises(Failure):
                runtime_binding(root)
            path.unlink()
            target = root / 'binding.json'
            target.write_bytes(canonical(value))
            path.symlink_to(target)
            with self.assertRaises(Failure):
                runtime_binding(root)

    def test_isolation_inventory_is_exact_not_color_interpreted(self) -> None:
        clean = b'ISOLATION\nNET-BEGIN\nlo\nNET-END\ntmpfs / tmpfs rw 0 0\nRESET-CLEAN\n'
        self.assertTrue(isolation_verified(clean))
        for bad in (clean.replace(b'lo\n', b'\x1b[1;36mlo\x1b[m\n'),
                    clean.replace(b'lo\n', b'lo\neth0\n'),
                    clean.replace(b'RESET-CLEAN\n', b''),
                    clean.replace(b'tmpfs / tmpfs', b'host /mnt virtiofs')):
            self.assertFalse(isolation_verified(bad))

    def test_recorded_preflight_failure_preceded_operator_stop(self) -> None:
        path = Path(__file__).resolve().parents[1] / 'docs/evidence/bounded-challenge/attempt-20261020T152048Z-d6f75d1f/protected-diagnostic.json'
        diagnostic = json.loads(path.read_bytes())
        observation = next(row for row in diagnostic['events'] if row['event']['kind'] == 'observation')
        stopped = next(row for row in diagnostic['events'] if row['event']['kind'] == 'stop-fenced')
        self.assertLess(observation['sequence'], stopped['sequence'])
        object_id = observation['event']['objects'][0]
        actual = diagnostic['objects'][object_id]
        self.assertEqual(digest(canonical(actual)), object_id)
        self.assertEqual(actual['error']['message'], 'Guest isolation/reset check failed')
        isolation = bytes.fromhex(actual['isolation'])
        self.assertIn(b'\x1b[1;36mlo\x1b[m', isolation)
        self.assertNotIn(b'\nlo\n', isolation)


if __name__ == '__main__':
    unittest.main(verbosity=2)
