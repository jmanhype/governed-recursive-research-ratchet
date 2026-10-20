"""Pure negative-boundary tests; never substitute for the real offline suite."""
import copy
from pathlib import Path
import sys
import subprocess
import tarfile
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'research'))
from common import Failure
from offline_execution import validate_config, read_config, input_mount_command
from offline import clone_asset, package_source, verify_base_iso_go
from common import digest


class OfflineRuntimeContracts(unittest.TestCase):
    def test_base_iso_check_rejects_absent_primary_namespace(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            image = Path(directory) / 'invalid.iso'
            image.write_bytes(b'not-an-iso')
            with self.assertRaises(Failure):
                verify_base_iso_go(image)

    def test_go_archive_transport_is_verified_and_guest_only(self) -> None:
        root = Path(__file__).resolve().parents[1]
        guest = (root / 'research/offline-guest.sh').read_text()
        self.assertNotIn('/inputs/go/bin', guest)
        self.assertIn('3f4227ce7b206a513e794f1393adb473a07b46e94d18bd15d1c684bbb7319797  /inputs/go.tgz', guest)
        self.assertIn('tar -xzf /inputs/go.tgz -C /work', guest)
        self.assertIn('GOROOT=/work/go PATH=/work/go/bin:', guest)
        self.assertIn('size=350m', guest)
        preparation = (root / 'scripts/prepare-offline-assets').read_text()
        self.assertNotIn('bundle.extractall(media', preparation)
        self.assertIn("shutil.copyfile(archive, media / 'go.tgz')", preparation)
        self.assertIn('verify_base_iso_go(input_iso)', preparation)

    def test_source_tar_preserves_hidden_paths_case_bytes_and_modes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            records = {}
            for name, mode in [('.github/workflows/ci.yml', '100644'), ('.gitignore', '100644'),
                               ('LICENSE', '100644'), ('Run.sh', '100755')]:
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(name.encode())
                records[name] = {'sha256': digest(name.encode()), 'mode': mode}
            (root / 'untracked').write_text('excluded')
            package_source(root, records, root / 'source.tar')
            with tarfile.open(root / 'source.tar') as archive:
                self.assertEqual(set(archive.getnames()), set(records))
                for member in archive:
                    self.assertEqual(member.mode, int(records[member.name]['mode'], 8) & 0o777)
                    self.assertEqual(archive.extractfile(member).read(), member.name.encode())

    def test_actual_route_predicate_rejects_route_rows(self) -> None:
        guest = (Path(__file__).resolve().parents[1] / 'research/offline-guest.sh').read_text()
        predicate = next(line for line in guest.splitlines() if line.startswith("awk 'NF && !(NR"))
        expression = predicate.split("'", 2)[1]
        for routes, expected in [('', 0), ('Iface Destination Gateway\n', 0),
                                  ('Iface Destination Gateway\neth0 00000000 0100000A\n', 1),
                                  ('eth0 00000000 0100000A\n', 1)]:
            self.assertEqual(subprocess.run(['/usr/bin/awk', expression], input=routes,
                                           text=True, capture_output=True).returncode, expected)

    def test_guest_distinguishes_boot_snapshot_from_detached_input(self) -> None:
        guest = (Path(__file__).resolve().parents[1] / 'research/offline-guest.sh').read_text()
        self.assertNotIn('/sys/class/block/vda/ro', guest)
        self.assertIn('/sys/class/block/vdb/ro', guest)
        self.assertIn('$1 == "/dev/vda" && $2 == "/media/vda"', guest)
        self.assertIn('$1 == "/dev/vdb" && $2 == "/inputs"', guest)
        self.assertIn('! touch /inputs/unauthorized-write', guest)
        self.assertIn('set -eu', guest)

    def test_input_discovery_is_not_boot_device_assumption(self) -> None:
        command = input_mount_command('a' * 32)
        self.assertNotIn('/dev/vda', command)
        self.assertIn('for grrr_dev in /dev/vd*', command)
        self.assertIn('umount /inputs || break', command)
        self.assertIn('mount -t iso9660 -o ro', command)
        self.assertIn('/sys/class/block/${grrr_dev##*/}/ro', command)
        self.assertIn('/proc/mounts', command)

    def test_missing_input_cannot_emit_readiness(self) -> None:
        command = input_mount_command('b' * 32)
        self.assertIn('grrr_input=;', command)
        self.assertIn('test -f /inputs/offline-guest.sh &&', command)
        self.assertIn('test -n "$grrr_input" && printf', command)
        with self.assertRaises(Failure):
            input_mount_command("'; arbitrary-command")

    def setUp(self) -> None:
        self.config = {'version': 1, 'profile_sha256': 'a' * 64, 'image_sha256': 'b' * 64,
            'license_review_sha256': 'c' * 64, 'qemu_sha256': 'd' * 64, 'network': False, 'shares': [],
            'memory_mib': 512, 'vcpus': 1, 'command_seconds': 240, 'total_seconds': 300}

    def test_exact_registered_configuration(self) -> None:
        self.assertEqual(validate_config(self.config), self.config)

    def test_network_or_share_never_becomes_allowed(self) -> None:
        for key, value in [('network', True), ('network', 'none'), ('shares', ['/Users']),
                           ('memory_mib', 1024), ('vcpus', 2), ('command_seconds', 241), ('total_seconds', 301)]:
            config = dict(self.config, **{key: value})
            with self.assertRaises(Failure):
                validate_config(config)

    def test_no_unknown_command_or_qemu_injection(self) -> None:
        for key in ('command', 'qemu_args', 'network_device', 'role', 'principal'):
            with self.assertRaises(Failure):
                validate_config(dict(self.config, **{key: 'arbitrary'}))

    def test_numbers_are_not_booleans(self) -> None:
        for key in ('version', 'vcpus', 'memory_mib'):
            with self.assertRaises(Failure):
                validate_config(dict(self.config, **{key: True}))

    def test_missing_binding_rejected(self) -> None:
        for key in ('profile_sha256', 'image_sha256', 'license_review_sha256'):
            config = dict(self.config)
            config.pop(key)
            with self.assertRaises(Failure):
                validate_config(config)

    def test_configuration_absence_is_not_default_success(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(Failure) as raised:
                read_config(Path(directory))
            self.assertEqual(raised.exception.record['code'], 'Unavailable')

    def test_actual_clone_is_independent_and_never_overwrites(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source, destination = Path(directory) / 'source', Path(directory) / 'destination'
            source.write_bytes(b'pinned-asset')
            clone_asset(source, destination)
            self.assertEqual(destination.read_bytes(), b'pinned-asset')
            source.write_bytes(b'changed-source')
            self.assertEqual(destination.read_bytes(), b'pinned-asset')
            with self.assertRaises(Failure):
                clone_asset(source, destination)


if __name__ == '__main__':
    unittest.main(verbosity=2)
