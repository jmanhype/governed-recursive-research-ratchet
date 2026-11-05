"""Real local processes/rights/locks/children. NONPRODUCTION, no VM or installed UID proof."""
import array
import fcntl
import json
import multiprocessing
import os
from pathlib import Path
import socket
import sqlite3
import struct
import sys
import tempfile
import threading
import time
import unittest

from common import Failure, canonical, digest
from capstone_launch import Gate, LaunchBroker, MARKER, receive_ticket, send_ticket

H = 'a' * 64


def ticket(**changes):
    value = dict(schema='capstone-launch-ticket-v1', launch_id='1' * 64,
                 operation_id='2' * 64, control_run='3' * 64, epoch=0,
                 session_id='4' * 64, intent_anchor=H,
                 deadline_monotonic_ns=time.monotonic_ns() + 3_000_000_000)
    value.update(changes)
    return value


def rights_receiver(path, conn, pipe, mode):
    try:
        pipe.send('ready')
        if mode == 'queued':
            pipe.recv()
        received, lease = receive_ticket(conn, Gate(path), expected_uid=os.getuid(), timeout=2)
        with lease:
            pipe.send(('received', received, os.get_inheritable(lease.fd)))
            pipe.recv()
        pipe.send('closed')
    except BaseException as exc:
        pipe.send(('failure', type(exc).__name__, str(exc)))
    finally:
        conn.close()
        pipe.close()


def broker_worker(root, conn, pipe, lose_commit):
    broker = None
    db = sqlite3.connect(str(Path(root) / 'owned.sqlite'), isolation_level=None)
    db.execute('PRAGMA synchronous=FULL')
    db.execute('CREATE TABLE owned(launch TEXT PRIMARY KEY, body BLOB NOT NULL)')
    gate = Gate(Path(root) / 'gate')

    def resolve(leaf):
        if leaf != 'harmless':
            raise ValueError('catalog miss')
        return (sys.executable, '-c',
                "import sys,time; print('owned-child',flush=True); time.sleep(10)")

    def validate(t, r):
        if t['intent_anchor'] != H or t['epoch'] != 0 or r['state'] != 'intent':
            raise ValueError('intent mismatch')

    def commit(t, r, remaining):
        # A REAL independently-opened description must still be excluded while
        # the durable owned row is committed. No mock lock or mocked child.
        try:
            with gate.acquire(0.03):
                raise AssertionError('gate released before commit')
        except Failure:
            pass
        db.execute('BEGIN IMMEDIATE')
        db.execute('INSERT INTO owned VALUES(?,?)', (r['launch_id'], canonical(r)))
        db.commit()
        if lose_commit:
            raise Failure('Unavailable', 'source cut: COMMITTED lost')
        return dict(state='COMMITTED', launch_id=r['launch_id'], session_id=r['session_id'],
                    intent_anchor=t['intent_anchor'], owned_sha256=digest(canonical(r)))

    try:
        broker = LaunchBroker.open_public_fixture(gate, resolve, validate, commit)
        prepared = broker.prepare('2' * 64, '3' * 64, 0, 'harmless')
        pipe.send(prepared)
        try:
            result = broker.launch(conn, timeout=2)
            pipe.send(('launched', result, broker.read(prepared['launch_id'], timeout=2)))
        except Failure as exc:
            pipe.send(('launch-failed', exc.record['code'], broker.status(prepared['launch_id'])))
        command = pipe.recv()
        if command == 'cancel':
            pipe.send(broker.cancel(prepared['launch_id']))
        elif command == 'duplicate':
            try:
                broker.prepare('2' * 64, '3' * 64, 0, 'harmless')
                pipe.send('unexpected')
            except Failure as exc:
                pipe.send(exc.record['code'])
        pipe.send('done')
    except BaseException as exc:
        pipe.send(('unexpected', type(exc).__name__, str(exc)))
    finally:
        if broker:
            broker.close()
        db.close()
        conn.close()
        pipe.close()


class LaunchTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='grrr-backend-fixture-', dir='/private/tmp')
        self.root = Path(self.tmp.name)
        self.path = self.root / 'gate'
        self.path.touch(mode=0o600)
        self.gate = Gate(self.path)
        self.ctx = multiprocessing.get_context('spawn')
        self.processes, self.sockets, self.pipes = [], [], []

    def tearDown(self):
        for pipe in self.pipes:
            pipe.close()
        for sock in self.sockets:
            sock.close()
        for process in self.processes:
            process.join(3)
            if process.is_alive():
                process.terminate()
                process.join(2)
                self.fail('owned test process exceeded bound')
            self.assertEqual(process.exitcode, 0)
        self.tmp.cleanup()

    def launch_process(self, target, *args):
        left, right = socket.socketpair()
        parent, child = self.ctx.Pipe()
        process = self.ctx.Process(target=target, args=(str(self.root if target == broker_worker else self.path),
                                                       right, child) + args)
        process.start()
        right.close()
        child.close()
        self.sockets.append(left)
        self.pipes.append(parent)
        self.processes.append(process)
        self.assertTrue(parent.poll(5))
        return left, parent, parent.recv()

    def receive(self, pipe):
        self.assertTrue(pipe.poll(5), 'worker did not produce bounded result')
        return pipe.recv()

    def test_fresh_description_exclusion_and_close_release(self):
        with self.gate.acquire(1):
            with self.assertRaises(Failure):
                self.gate.acquire(0.03)
        with self.gate.acquire(1):
            pass

    def test_inode_replacement_denied(self):
        old = self.path.with_name('old')
        self.path.rename(old)
        self.path.touch(mode=0o600)
        with self.assertRaises(Failure):
            self.gate.acquire(1)

    def test_symlink_denied(self):
        alias = self.path.with_name('alias')
        alias.symlink_to(self.path)
        with self.assertRaises(OSError):
            Gate(alias)

    def test_queued_rights_keep_lock_after_sender_close(self):
        conn, pipe, ready = self.launch_process(rights_receiver, 'queued')
        self.assertEqual(ready, 'ready')
        lease = self.gate.acquire(1)
        sent = ticket()
        send_ticket(conn, sent, lease, expected_uid=os.getuid(), timeout=2)
        with self.assertRaises(Failure):
            lease.fd
        with self.assertRaises(Failure):
            self.gate.acquire(0.03)
        pipe.send('receive')
        got = self.receive(pipe)
        self.assertEqual(got, ('received', sent, False))
        with self.assertRaises(Failure):
            self.gate.acquire(0.03)
        pipe.send('release')
        self.assertEqual(self.receive(pipe), 'closed')
        with self.gate.acquire(1):
            pass

    def malformed(self, body, descriptors=None, marker=MARKER, tail=b''):
        conn, pipe, _ = self.launch_process(rights_receiver, 'normal')
        with self.gate.acquire(1) as lease:
            descriptors = [lease.fd] if descriptors is None else descriptors
            ancillary = [(socket.SOL_SOCKET, socket.SCM_RIGHTS, array.array('i', descriptors))] if descriptors else []
            conn.sendmsg([marker], ancillary)
            if body:
                conn.sendall(body + tail)
            conn.shutdown(socket.SHUT_WR)
        response = self.receive(pipe)
        self.assertEqual(response[0], 'failure', response)
        with self.gate.acquire(1):
            pass

    def test_missing_rights_denied(self):
        self.malformed(b'', descriptors=[])

    def test_duplicate_rights_denied(self):
        fd = os.open(self.path, os.O_RDONLY)
        try:
            self.malformed(b'', descriptors=[fd, fd])
        finally:
            os.close(fd)

    def test_wrong_inode_denied(self):
        other = self.root / 'other'
        other.touch(mode=0o600)
        fd = os.open(other, os.O_RDONLY)
        try:
            self.malformed(b'', descriptors=[fd])
        finally:
            os.close(fd)

    def test_partial_frame_denied_and_lock_released(self):
        self.malformed(struct.pack('!I', 100) + b'{')

    def test_wrong_marker_denied(self):
        self.malformed(b'', marker=b'X')

    def test_trailing_bytes_denied(self):
        raw = canonical(ticket())
        self.malformed(struct.pack('!I', len(raw)) + raw, tail=b'X')

    def test_expired_ticket_denied(self):
        raw = canonical(ticket(deadline_monotonic_ns=0))
        self.malformed(struct.pack('!I', len(raw)) + raw)

    def test_extra_fields_denied(self):
        raw = canonical(ticket(trust_me=True))
        self.malformed(struct.pack('!I', len(raw)) + raw)

    def test_peer_mismatch_closes_sender_lease_without_send(self):
        left, right = socket.socketpair()
        try:
            lease = self.gate.acquire(1)
            with self.assertRaises(Failure):
                send_ticket(left, ticket(), lease, expected_uid=320, timeout=1)
            with self.gate.acquire(1):
                pass
        finally:
            left.close()
            right.close()

    def test_actual_uid_required_for_production_broker(self):
        with self.assertRaises(Failure):
            LaunchBroker.open_existing(self.gate, None, None, None)

    def test_broker_receive_failure_closes_socket(self):
        broker = LaunchBroker.open_public_fixture(self.gate, None, None, None)
        left, right = socket.socketpair()
        try:
            left.sendall(b'X')
            left.shutdown(socket.SHUT_WR)
            with self.assertRaises(Failure):
                broker.launch(right, timeout=0.5)
            self.assertEqual(right.fileno(), -1)
        finally:
            broker.close(); left.close(); right.close()

    def threaded_handoff(self, action):
        entered, release = threading.Event(), threading.Event()
        budgets, results = [], []
        def command(_):
            return (sys.executable, '-c', "import time; time.sleep(10)")
        def validate(t, r):
            self.assertEqual(t['intent_anchor'], H)
        def commit(t, r, remaining):
            budgets.append(remaining)
            entered.set()
            if action in ('cancel', 'close'):
                if not release.wait(3):
                    raise Failure('Unavailable', 'Bounded source callback timeout')
            return dict(state='COMMITTED', launch_id=r['launch_id'], session_id=r['session_id'],
                        intent_anchor=t['intent_anchor'], owned_sha256=digest(canonical(r)))
        broker = LaunchBroker.open_public_fixture(self.gate, command, validate, commit)
        prepared = broker.prepare('2' * 64, '3' * 64, 0, 'harmless')
        left, right = socket.socketpair()
        sent = ticket(**{k: prepared[k] for k in ('launch_id', 'session_id', 'operation_id', 'control_run', 'epoch')})
        sent['deadline_monotonic_ns'] = time.monotonic_ns() + 10**12
        def launch():
            try:
                results.append(('ok', broker.launch(right, timeout=2)))
            except Failure as exc:
                results.append(('refused', exc.record['code']))
        worker = threading.Thread(target=launch)
        worker.start()
        try:
            send_ticket(left, sent, self.gate.acquire(1), expected_uid=os.getuid(), timeout=2)
            self.assertTrue(entered.wait(3))
            self.assertGreater(budgets[0], 0)
            self.assertLessEqual(budgets[0], 2)  # untrusted far-future ticket cannot extend budget
            if action in ('cancel', 'close'):
                if action == 'cancel':
                    self.assertTrue(broker.cancel(prepared['launch_id'])['reaped'])
                else:
                    broker.close()
                # Cancellation already released the handoff, even though the
                # commit callback is still blocked and launch has not returned.
                with self.gate.acquire(0.2):
                    pass
                self.assertEqual(broker.status(prepared['launch_id'])['record']['state'], 'unknown')
                self.assertIsNotNone(broker.status(prepared['launch_id'])['exit_code'])
                release.set()
                worker.join(3)
                self.assertEqual(results, [('refused', 'RecoveryRequired')])
            else:
                worker.join(3)
                self.assertEqual(results[0][0], 'ok')
                broker.close()
                with self.assertRaises(Failure):
                    broker.read(prepared['launch_id'], timeout=0.1)
                with self.assertRaises(Failure):
                    broker.write(prepared['launch_id'], b'x', timeout=0.1)
            self.assertFalse(worker.is_alive())
        finally:
            release.set()
            worker.join(3)
            broker.close(); left.close(); right.close()

    def test_cancel_pending_handoff_closes_gate_before_reap_and_rejects_late_commit(self):
        self.threaded_handoff('cancel')

    def test_close_pending_handoff_cannot_be_revived_by_commit(self):
        self.threaded_handoff('close')

    def test_local_deadline_caps_callback_and_closed_io_refuses(self):
        self.threaded_handoff('budget')

    def broker_case(self, lost=False, command='cancel'):
        conn, pipe, prepared = self.launch_process(broker_worker, lost)
        self.assertEqual(prepared['state'], 'intent')
        sent = ticket(**{k: prepared[k] for k in ('launch_id', 'operation_id', 'control_run', 'epoch', 'session_id')})
        send_ticket(conn, sent, self.gate.acquire(1), expected_uid=os.getuid(), timeout=2)
        result = self.receive(pipe)
        if lost:
            self.assertEqual(result[:2], ('launch-failed', 'Unavailable'))
            self.assertEqual(result[2]['record']['state'], 'unknown')
            self.assertIsNotNone(result[2]['exit_code'])
        else:
            self.assertEqual(result[0], 'launched', result)
            self.assertEqual(result[2], b'owned-child\n')
            self.assertEqual(result[1]['identity'], 'NONPRODUCTION')
        with self.gate.acquire(1):
            pass
        db = sqlite3.connect(str(self.root / 'owned.sqlite'))
        try:
            row = db.execute('SELECT body FROM owned').fetchall()
            self.assertEqual(len(row), 1)
            self.assertEqual(json.loads(row[0][0])['state'], 'owned')
        finally:
            db.close()
        pipe.send(command)
        outcome = self.receive(pipe)
        self.assertEqual(self.receive(pipe), 'done')
        return outcome

    def test_owned_child_real_spawn_commit_cancel_reap(self):
        result = self.broker_case()
        self.assertTrue(result['reaped'])
        self.assertEqual(result['exit_code'], -15)

    def test_lost_committed_holds_unknown_and_reaps(self):
        result = self.broker_case(lost=True)
        self.assertTrue(result['reaped'])

    def test_duplicate_operation_cannot_prepare_second_child(self):
        self.assertEqual(self.broker_case(command='duplicate'), 'RecoveryRequired')


if __name__ == '__main__':
    unittest.main()
