import json
import os
from pathlib import Path
import socket
import tempfile
import threading
import time
import unittest
from unittest.mock import patch
from common import Failure, canonical
from capstone_client import explicit_peer_call, production_client, test_client, test_endpoint
from capstone_service import RefusalService, test_service
from trusted_transport import AuthenticatedServer
from unit_capstone_contract import sample, bound_plan
from capstone_contract import operation_id


class PeerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='grrr-wcwy-', dir='/private/tmp')
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def test_real_refusal_channels(self):
        server = test_service(self.root)
        try:
            client = test_client(self.root)
            for action in ('Observe', 'Status', 'Stop', 'Start'):
                with self.subTest(action=action), self.assertRaises(Failure) as ctx:
                    client.call(sample(action))
                self.assertIn(ctx.exception.record['code'], ('RecoveryRequired', 'Unavailable'))
            req = sample('Observe'); req['request']['bindings']['accounting_version'] = 4
            with self.assertRaisesRegex(Failure, 'UnsupportedAccountingVersion:4'): client.call(req)
        finally:
            server.close()

    def test_wrong_server_before_payload(self):
        listener = socket.socket(socket.AF_UNIX); listener.bind(str(self.root/'data.sock')); listener.listen(1)
        observed = []
        def peer():
            conn, _ = listener.accept()
            with conn:
                conn.settimeout(2); observed.append(conn.recv(1))
        t = threading.Thread(target=peer); t.start()
        try:
            with self.assertRaisesRegex(Failure, 'before payload'):
                explicit_peer_call(self.root/'data.sock', sample('Observe'), expected_uid=os.getuid()+1)
        finally:
            t.join(3); listener.close()
        self.assertFalse(t.is_alive()); self.assertEqual(observed, [b''])

    def test_real_synthetic_response_parser_not_authority(self):
        receipt = sample('Receipt')
        server = AuthenticatedServer(self.root/'data.sock', lambda uid, r: receipt, allowed_uid=os.getuid())
        try:
            self.assertEqual(test_client(self.root).call(sample('Observe')), receipt)
        finally:
            server.close()

    def test_raw_response_bounds_and_errors(self):
        # Real sockets and kernel credentials; deliberately hostile wire peer.
        for index, raw in enumerate((b'{"ok":{},"ok":{}}\n', b'{"ok":{},"error":{}}\n',
                                    b'x'*4097+b'\n', b'{"error":{"code":"Invented"}}\n', b'{}')):
            endpoint = self.root/'control.sock'
            listener = socket.socket(socket.AF_UNIX); listener.bind(str(endpoint)); listener.listen(1)
            def peer():
                conn, _ = listener.accept()
                with conn:
                    conn.settimeout(2); conn.recv(4096)
                    try: conn.sendall(raw)
                    except OSError: pass
            t = threading.Thread(target=peer); t.start()
            try:
                with self.subTest(index=index), self.assertRaises(Failure):
                    explicit_peer_call(endpoint, sample('Status'), expected_uid=os.getuid())
            finally:
                t.join(3); listener.close(); endpoint.unlink()
            self.assertFalse(t.is_alive())

    def test_symlink_socket_refused_before_connect(self):
        endpoint = self.root/'data.sock'
        endpoint.symlink_to(self.root/'absent')
        with self.assertRaisesRegex(Failure, 'Unsafe fixture socket'):
            explicit_peer_call(endpoint, sample('Observe'), expected_uid=os.getuid())

    def test_wrong_client_before_payload_and_slot(self):
        called = []
        server = AuthenticatedServer(self.root/'data.sock', lambda uid, r: called.append(r), allowed_uid=os.getuid()+1)
        try:
            with socket.socket(socket.AF_UNIX) as conn:
                conn.settimeout(2); conn.connect(str(self.root/'data.sock'))
                self.assertIn(b'Unauthorized', conn.recv(4096))
            acquired = [server.slots.acquire(False) for _ in range(8)]
            self.assertEqual(acquired, [True]*8)
            for _ in acquired: server.slots.release()
            self.assertEqual(called, [])
        finally:
            server.close()

    def test_control_responsive_with_data_capacity_full(self):
        server = test_service(self.root); clients = []
        try:
            for _ in range(8):
                conn = socket.socket(socket.AF_UNIX); conn.connect(str(self.root/'data.sock')); clients.append(conn)
            deadline = time.monotonic()+0.7
            while server.data.slots._value and time.monotonic() < deadline: time.sleep(0.005)
            self.assertEqual(server.data.slots._value, 0)
            before = time.monotonic()
            with self.assertRaisesRegex(Failure, 'Operation capability absent'):
                test_client(self.root).call(sample('Status'), timeout=0.5)
            self.assertLess(time.monotonic()-before, 0.5)
        finally:
            for conn in clients: conn.close()
            server.close()

    def test_malformed_and_oversized_frames(self):
        server = test_service(self.root)
        try:
            for raw in (b'{}\n', b'{"action":"status","action":"stop"}\n', b'x'*4097+b'\n'):
                with socket.socket(socket.AF_UNIX) as conn:
                    conn.settimeout(2); conn.connect(str(self.root/'control.sock')); conn.sendall(raw)
                    response = json.loads(conn.recv(4096))
                    self.assertEqual(response['error']['code'], 'InvalidInput')
        finally:
            server.close()

    def test_no_protected_io_negative_guard_only(self):
        with patch('pathlib.Path.lstat', side_effect=AssertionError('metadata forbidden')):
            for path in ('/Library/GRRR/x', '/tmp/x/data.sock', '/private/tmp/../Library/GRRR/data.sock'):
                with self.assertRaises(Failure): test_endpoint(Path(path))
        with patch('builtins.open', side_effect=AssertionError('I/O forbidden')), patch('os.open', side_effect=AssertionError('I/O forbidden')):
            with self.assertRaises(Failure): production_client().call(sample('Observe'))
            with self.assertRaises(Failure): RefusalService(os.getuid()).handle(os.getuid(), sample('Observe'))

    def test_counterfeit_grant_cannot_start(self):
        p, _, _ = bound_plan()
        req = dict(action='start', version=1, plan=p, operation_id=operation_id(p['grant']['grant_id'], p['plan_sha256']))
        with self.assertRaisesRegex(Failure, 'GrantUnissued'):
            RefusalService(os.getuid()).handle(os.getuid(), req)
        for version in (True, 2, None):
            req = sample('Observe'); req['version'] = version
            with self.assertRaisesRegex(Failure, 'UnsupportedProtocolVersion'):
                RefusalService(os.getuid()).handle(os.getuid(), req)
