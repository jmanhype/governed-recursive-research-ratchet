"""Supplementary offline policy tests; no VM or target execution is claimed."""
from pathlib import Path
import os
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'research'))
from common import Failure, canonical, digest
from offline import compliance_gate, proposed_profile, require_profile_approval, toolchain_inventory
from policy import default_policy


class OfflineContracts(unittest.TestCase):
    def test_profile_cannot_change_synthetic_policy(self) -> None:
        before = canonical(default_policy(501))
        profile = proposed_profile(501, 'a' * 64)
        self.assertEqual(profile['limits']['memory_mib'], 1024)
        self.assertEqual(profile['workspace_mib'], 512)
        self.assertNotIn('workspace_mib', default_policy(501))
        self.assertEqual(default_policy(501)['limits']['memory_mib'], 512)
        self.assertEqual(profile['limits'], dict(default_policy(501)['limits'], memory_mib=1024))
        self.assertEqual(profile['per_invocation_seconds'], 300)
        self.assertEqual(profile['builds'], 2)
        self.assertFalse(profile['network'])
        self.assertFalse(profile['host_shares'])
        self.assertFalse(profile['paid_dispatch'])
        self.assertEqual(profile['approval'], 'required')
        profile['limits']['command_seconds'] = 240
        self.assertEqual(before, canonical(default_policy(501)))

    def test_service_identity_cannot_be_operator(self) -> None:
        for uid in (0, 320, 321, True):
            with self.assertRaises(Failure):
                proposed_profile(uid, 'a' * 64)

    def test_proposal_requires_inventory_digest(self) -> None:
        for value in ('', '../escape', 'a' * 63, None):
            with self.assertRaises(Failure):
                proposed_profile(501, value)

    def test_missing_approval_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(Failure) as failure:
                require_profile_approval(Path(directory) / 'absent', proposed_profile(501, 'a' * 64))
            self.assertEqual(failure.exception.record['code'], 'GateBlocked')

    def test_writable_or_symlink_approval_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'approval'
            path.write_bytes(b'{}')
            os.chmod(path, 0o666)
            with self.assertRaises(Failure):
                require_profile_approval(path, proposed_profile(501, 'a' * 64))
            link = Path(directory) / 'link'
            link.symlink_to(path)
            with self.assertRaises(Failure):
                require_profile_approval(link, proposed_profile(501, 'a' * 64))

    def test_license_label_is_not_clearance(self) -> None:
        component = {'name': 'x', 'version': '1', 'sha256': 'a' * 64, 'origin': 'https://example.org',
                     'license': 'MIT', 'notices': ['LICENSE'], 'obligations': ['retain license'],
                     'compliance_evidence': '', 'separate_review': None}
        inventory = {'components': [component], 'complete': True, 'unresolved': []}
        with self.assertRaises(Failure):
            compliance_gate(inventory)
        component['compliance_evidence'] = 'b' * 64
        compliance_gate(inventory)
        for license_id in ('GPL-2.0-only', 'AGPL-3.0-only', 'BSL-1.1', 'noncommercial', 'source-available', 'unclear'):
            component['license'] = license_id
            with self.assertRaises(Failure):
                compliance_gate(inventory)

    def test_incomplete_and_empty_inventory_rejected(self) -> None:
        for value in ({'components': [], 'complete': True, 'unresolved': []},
                      {'components': [], 'complete': False, 'unresolved': ['VM licenses']}):
            with self.assertRaises(Failure):
                compliance_gate(value)

    def test_missing_and_corrupt_toolchain_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            archive = Path(directory) / 'go.tar.gz'
            with self.assertRaises(Failure):
                toolchain_inventory(archive)
            archive.write_bytes(b'corrupt')
            with self.assertRaises(Failure):
                toolchain_inventory(archive)


if __name__ == '__main__':
    unittest.main(verbosity=2)
