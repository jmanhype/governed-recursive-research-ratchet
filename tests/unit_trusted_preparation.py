"""Supplementary static/format checks; no guest or candidate process is launched."""
import importlib.machinery
import importlib.util
import json
from pathlib import Path
import struct
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
loader = importlib.machinery.SourceFileLoader('trusted_prepare', str(ROOT / 'scripts/prepare-trusted-observation'))
spec = importlib.util.spec_from_loader(loader.name, loader)
prepare = importlib.util.module_from_spec(spec)
loader.exec_module(prepare)
from common import Failure, digest


class TrustedPreparation(unittest.TestCase):
    def test_development_proposal_remains_disabled_and_byte_bound(self) -> None:
        raw = (ROOT / 'docs/TRUSTED-OBSERVATION-PROFILE-PROPOSAL.json').read_bytes()
        self.assertEqual(digest(raw), prepare.PROPOSAL)
        profile = json.loads(raw)
        self.assertFalse(profile['dispatch_enabled'])
        self.assertEqual((profile['memory_mib'], profile['workspace_mib'], profile['vcpus']), (1024, 512, 1))
        self.assertIsNone(profile['input_image_sha256'])
        self.assertIsNone(profile['supervisor_sha256'])

    def test_space_reserves_future_writes_before_side_effect(self) -> None:
        class Disk:
            free = prepare.FLOOR + 100
        with patch.object(prepare.shutil, 'disk_usage', return_value=Disk()):
            self.assertEqual(prepare.space(ROOT, 100), Disk.free)
            with self.assertRaises(Failure):
                prepare.space(ROOT, 101)

    def test_elf_parser_rejects_host_binary_and_dynamic_guest(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'binary'
            path.write_bytes(b'not an ELF')
            with self.assertRaises(Failure):
                prepare.elf_identity(path)
            raw = bytearray(128)
            raw[:6] = b'\x7fELF\x02\x01'
            struct.pack_into('<H', raw, 18, 183)
            struct.pack_into('<Q', raw, 32, 64)
            struct.pack_into('<HH', raw, 54, 56, 1)
            path.write_bytes(raw)
            self.assertEqual(prepare.elf_identity(path)['machine'], 'AArch64')
            struct.pack_into('<I', raw, 64, 3)
            path.write_bytes(raw)
            with self.assertRaises(Failure):
                prepare.elf_identity(path)

    def test_bootstrap_hides_original_supervisor_media(self) -> None:
        script = (ROOT / 'research/trusted-guest.sh').read_text()
        self.assertIn('mount -o move /inputs /root/inputs', script)
        self.assertIn('chmod 700 /root', script)
        self.assertIn('size=512m,nosuid,nodev', script)
        self.assertIn('chmod 600 /dev/console /dev/ttyAMA0 /dev/vd*', script)
        self.assertIn('chmod 1777 /work/vault', script)
        self.assertIn('exec /work/control/supervisor', script)
        self.assertNotIn('chmod 700 /inputs', script)

    def test_supervisor_launch_has_no_shell_or_control_descriptors(self) -> None:
        source = (ROOT / 'research/trusted-supervisor/supervisor_linux.go').read_text()
        self.assertIn('Uid: 1000, Gid: 1000, Groups: []uint32{}', source)
        self.assertIn('cmd.Stdin = null', source)
        self.assertIn('Setsid:', source)
        self.assertNotIn('ExtraFiles:', source)
        self.assertNotIn('exec.CommandContext(ctx, "/bin/sh"', source)
        self.assertIn('PR_SET_NO_NEW_PRIVS', source)
        self.assertIn('PR_CAPBSET_DROP', source)
        self.assertIn('syscall.O_NOFOLLOW', source)


if __name__ == '__main__':
    unittest.main(verbosity=2)
