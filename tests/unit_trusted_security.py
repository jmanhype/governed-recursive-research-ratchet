"""Nonprivileged real Unix-socket and immutable-path negative controls."""
import importlib.machinery
import importlib.util
import os
from pathlib import Path
import socket
import struct
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'research'))
from common import Failure, canonical, receive
from trusted_install import immutable, macho_loads, verify_qemu
from trusted_transport import AuthenticatedServer
from budget import Budget
from persistent_budget import PROFILES, validate_store


class PersistentValidation(unittest.TestCase):
    """Unit identity substitution only; actual UID-320 proof remains mandatory."""
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.path = Path(self.folder.name) / 'budget.sqlite'
        self.budget_uid = patch('budget.EVALUATOR', os.getuid())
        self.validation_uid = patch('persistent_budget.EVALUATOR', os.getuid())
        self.budget_uid.start()
        self.validation_uid.start()
        self.store = Budget(self.path)
        self.store.db.execute('CREATE TABLE store_identity(campaign TEXT,store_id TEXT,prior_history_receipt TEXT)')
        self.store.db.execute('INSERT INTO store_identity VALUES(?,?,?)', ('a' * 64, 'b' * 64, 'c' * 64))
        info = self.path.stat()
        self.binding = {'version': 1, 'campaign': 'a' * 64, 'store_id': 'b' * 64,
            'prior_history_receipt': 'c' * 64, 'directory': str(self.path.parent),
            'device': info.st_dev, 'inode': info.st_ino, 'profiles': list(PROFILES)}

    def tearDown(self):
        self.store.db.close()
        self.validation_uid.stop()
        self.budget_uid.stop()
        self.folder.cleanup()

    def test_existing_identity_and_stop_are_preserved(self):
        validate_store(self.binding, self.path)
        self.store.halt()
        validate_store(self.binding, self.path)
        other = Budget(self.path, existing=True)
        try:
            self.assertTrue(other.totals(os.getuid())['stopped'])
        finally:
            other.db.close()

    def test_missing_stop_row_is_not_repaired(self):
        self.store.db.execute('DELETE FROM state')
        with self.assertRaises(Failure):
            validate_store(self.binding, self.path)
        self.assertEqual(self.store.db.execute('SELECT * FROM state').fetchall(), [])

    def test_changed_history_identity_fails(self):
        self.store.db.execute('UPDATE store_identity SET prior_history_receipt=?', ('d' * 64,))
        with self.assertRaises(Failure):
            validate_store(self.binding, self.path)

    def test_replaced_store_inode_fails_even_with_same_bytes(self):
        backup = self.path.with_suffix('.copy')
        backup.write_bytes(self.path.read_bytes())
        backup.chmod(0o600)
        backup.replace(self.path)
        with self.assertRaises(Failure):
            validate_store(self.binding, self.path)

    def test_settled_usage_without_meter_cannot_hide_prior_cost(self):
        maximum = {'currency': 'USD', 'money_cents': 5000, 'execution_us': 1, 'review_us': 0}
        self.store.reserve(os.getuid(), 'run', maximum, 'key')
        self.store.db.execute('UPDATE reservations SET actual=?, receipt=?',
                             (canonical(dict(maximum, money_cents=0)), '0' * 64))
        with self.assertRaises(Failure):
            validate_store(self.binding, self.path)


class SocketSecurity(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory(prefix='grrr-socket-', dir='/private/tmp')
        self.root = Path(self.folder.name)
        self.servers = []
        self.calls = []

    def tearDown(self):
        for server in self.servers:
            server.close()
        self.folder.cleanup()

    def server(self, name, control=False, allowed=None):
        def handler(uid, message):
            self.calls.append((uid, message))
            return {'acknowledged': True}
        server = AuthenticatedServer(self.root / name, handler, control=control,
                                     allowed_uid=os.getuid() if allowed is None else allowed)
        self.servers.append(server)
        return server

    def connection(self, name):
        conn = socket.socket(socket.AF_UNIX)
        conn.settimeout(2)
        conn.connect(str(self.root / name))
        return conn

    def test_unauthorized_peer_rejected_without_payload_or_slots(self):
        server = self.server('data', allowed=os.getuid() + 10000)
        peers = [self.connection('data') for _ in range(24)]
        try:
            for peer in peers:
                self.assertEqual(receive(peer)['error']['code'], 'Unauthorized')
            self.assertFalse(self.calls)
        finally:
            for peer in peers:
                peer.close()

    def test_idle_data_saturation_cannot_consume_control_capacity(self):
        self.server('data')
        self.server('control', control=True)
        peers = [self.connection('data') for _ in range(24)]
        try:
            started = time.monotonic()
            with self.connection('control') as conn:
                conn.sendall(canonical({'action': 'stop', 'run': 'saturation'}) + b'\n')
                self.assertTrue(receive(conn)['ok']['acknowledged'])
            self.assertLess(time.monotonic() - started, 2)
            self.assertEqual(len(self.calls), 1)
        finally:
            for peer in peers:
                peer.close()

    def test_initial_read_deadline_is_absolute(self):
        self.server('data')
        with self.connection('data') as conn:
            started = time.monotonic()
            conn.sendall(b'{')
            self.assertEqual(receive(conn)['error']['code'], 'InvalidInput')
            self.assertLess(time.monotonic() - started, 1.5)
        self.assertFalse(self.calls)

    def test_control_channel_cannot_dispatch_effects(self):
        self.server('control', control=True)
        with self.connection('control') as conn:
            conn.sendall(canonical({'action': 'dispatch'}) + b'\n')
            self.assertEqual(receive(conn)['error']['code'], 'InvalidInput')
        self.assertFalse(self.calls)


class InstallationSecurity(unittest.TestCase):
    def test_mutable_executable_ancestors_are_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            executable = Path(folder) / 'qemu'
            executable.write_bytes(b'not an executable')
            executable.chmod(0o555)
            with self.assertRaises(Failure):
                immutable(executable)
            link = Path(folder) / 'link'
            link.symlink_to(executable)
            with self.assertRaises(Failure):
                immutable(link)

    def test_homebrew_installation_never_authorized(self):
        with self.assertRaises(Failure):
            verify_qemu({'version': 1, 'root': '/opt/homebrew/bin', 'executable': 'qemu-system-aarch64',
                         'files': {}, 'system_build': 'unknown', 'review_reference': 'a' * 64,
                         'build_record_sha256': 'b' * 64, 'data_files': {}})

    def test_macho_dependency_parser_rejects_truncated_or_fat(self):
        for raw in (b'', b'\xca\xfe\xba\xbe' + b'\0' * 64, b'\xcf\xfa\xed\xfe' + b'\0' * 12 +
                    struct.pack('<II', 1, 8) + b'\0' * 8 + struct.pack('<II', 12, 100)):
            with self.assertRaises(Failure):
                macho_loads(raw)

    def test_macho_dependency_names_are_measured_not_executed(self):
        name = b'/opt/homebrew/lib/unsafe.dylib\0'
        command = struct.pack('<III', 12, 12 + len(name), 12) + name
        raw = b'\xcf\xfa\xed\xfe' + b'\0' * 12 + struct.pack('<II', 1, len(command)) + b'\0' * 8 + command
        self.assertEqual(macho_loads(raw), (['/opt/homebrew/lib/unsafe.dylib'], []))

    def test_bootstrap_is_standalone_and_no_checkout_import_precedes_snapshot(self):
        loader = importlib.machinery.SourceFileLoader('root_bootstrap_unit', str(ROOT / 'scripts/trusted-root-bootstrap'))
        spec = importlib.util.spec_from_loader(loader.name, loader)
        module = importlib.util.module_from_spec(spec)
        loader.exec_module(module)
        with self.assertRaises(RuntimeError):
            module.main()  # actual nonroot process fails before any copy/import/launch
        self.assertNotIn('common', module.__dict__)
        with self.assertRaises(RuntimeError):
            module.unique([('files', {}), ('files', {'evil.py': 'x'})])


if __name__ == '__main__':
    unittest.main()
