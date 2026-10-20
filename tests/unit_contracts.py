"""Supplementary pure-contract tests; do not substitute for real identity/VM suite."""
from pathlib import Path
import sys
import unittest
import os
import tempfile
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'research'))
from common import Failure, GATES, PACKETS, canonical, digest, fields, identifier, runtime_binding, socket_path
from policy import default_policy
from runner import parser


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


if __name__ == '__main__':
    unittest.main(verbosity=2)
