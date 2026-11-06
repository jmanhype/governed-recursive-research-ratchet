"""Locked-description launch handoff and owned-child mechanics.

This module is not an installation factory or an authorization issuer. A trusted
evaluator must commit its intent, consume its Journal DispatchPermit, then send
the ticket. The broker's trusted callbacks validate that intent and commit the
owned result in the evaluator, without reacquiring the gate. There is no PID
adoption or restart/resend API. Public fixtures use the actual unprivileged UID.
"""
import array
import errno
import fcntl
import json
import os
from pathlib import Path
import selectors
import signal
import socket
import stat
import struct
import subprocess
import threading
import time
import uuid

from common import (EVALUATOR, RUNNER, MAX_WIRE, Failure, canonical, digest,
                    fields, identifier, peer_uid, require, unique_fields)

MARKER = b'G'
TICKET_FIELDS = {'schema', 'launch_id', 'session_id', 'operation_id',
                 'control_run', 'epoch', 'intent_anchor', 'deadline_monotonic_ns'}
_OPEN = object()


def _remaining(deadline):
    value = (deadline - time.monotonic_ns()) / 1_000_000_000
    require(value > 0, 'Unavailable', 'Absolute handoff deadline expired')
    return value


def _deadline(seconds):
    require(type(seconds) in (int, float) and 0 < seconds <= 15,
            'InvalidInput', 'Deadline outside source protocol bound')
    return time.monotonic_ns() + int(seconds * 1_000_000_000)


def _ticket(value):
    fields(value, TICKET_FIELDS)
    require(value['schema'] == 'capstone-launch-ticket-v1', 'InvalidInput', 'Wrong launch ticket schema')
    for name in ('launch_id', 'session_id', 'operation_id', 'control_run', 'intent_anchor'):
        identifier(value[name], True)
    for name in ('epoch', 'deadline_monotonic_ns'):
        require(type(value[name]) is int and value[name] >= 0, 'InvalidInput', 'Ticket integer differs')
    return value


class GateLease:
    """One owned reference to a locked open-file description. CLOSE, never unlock."""
    def __init__(self, fd, token):
        require(token is _OPEN, 'Unauthorized', 'Use gate acquisition or authenticated receive')
        self._fd, self._pid = fd, os.getpid()
        self._lock = threading.Lock()

    @property
    def fd(self):
        require(self._pid == os.getpid() and self._fd is not None,
                'Unavailable', 'Gate lease closed or inherited')
        return self._fd

    def close(self):
        # Closing an inherited reference is safe; it never explicitly unlocks
        # the parent's open description. Do not silently use an inherited lease.
        with self._lock:
            if self._fd is not None:
                fd, self._fd = self._fd, None
                os.close(fd)

    def __enter__(self):
        self.fd
        return self

    def __exit__(self, *unused):
        self.close()

    def __reduce_ex__(self, protocol):
        raise TypeError('Gate lease is not serializable')


class Gate:
    """Existing gate identity; each contender opens a fresh description.

    Construct only from a topology-validated path. Device/inode/owner/mode are
    captured without creation and rechecked at every acquisition/receive.
    """
    def __init__(self, path):
        self.path = Path(path)
        fd = os.open(self.path, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC)
        try:
            st = os.fstat(fd)
            require(stat.S_ISREG(st.st_mode) and st.st_nlink == 1,
                    'IntegrityFailure', 'Gate is not a single-link regular inode')
            self.identity = (st.st_dev, st.st_ino, st.st_uid, st.st_gid, st.st_mode)
        finally:
            os.close(fd)

    def validate(self, fd):
        st = os.fstat(fd)
        require((st.st_dev, st.st_ino, st.st_uid, st.st_gid, st.st_mode) == self.identity
                and st.st_nlink == 1 and stat.S_ISREG(st.st_mode),
                'IntegrityFailure', 'Transferred gate inode differs')
        require(fcntl.fcntl(fd, fcntl.F_GETFL) & os.O_ACCMODE == os.O_RDONLY,
                'IntegrityFailure', 'Gate must be read-open')
        current = os.stat(self.path, follow_symlinks=False)
        require((current.st_dev, current.st_ino, current.st_uid, current.st_gid, current.st_mode)
                == self.identity and current.st_nlink == 1,
                'IntegrityFailure', 'Gate path was replaced')

    def acquire(self, timeout):
        deadline = _deadline(timeout)
        fd = os.open(self.path, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC)
        try:
            self.validate(fd)
            while True:
                _remaining(deadline)
                try:
                    fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    self.validate(fd)
                    return GateLease(fd, _OPEN)
                except BlockingIOError:
                    time.sleep(min(0.005, _remaining(deadline)))
        except BaseException:
            os.close(fd)
            raise


def send_ticket(conn, ticket, lease, *, expected_uid, timeout):
    """Transfer once, closing the sender's copy on EVERY send outcome.

    No retry is safe after sendmsg. The socket queue can already own the lock
    even when subsequent framing fails. Caller must query the known intent.
    """
    try:
        require(peer_uid(conn) == expected_uid, 'Unauthorized', 'Broker peer differs')
        raw = canonical(_ticket(ticket))
        require(len(raw) <= MAX_WIRE, 'InvalidInput', 'Ticket exceeds wire maximum')
        deadline = min(_deadline(timeout), ticket['deadline_monotonic_ns'])
        conn.settimeout(_remaining(deadline))
        count = conn.sendmsg([MARKER], [(socket.SOL_SOCKET, socket.SCM_RIGHTS,
                                        array.array('i', [lease.fd]))])
        require(count == 1, 'RecoveryRequired', 'Ambiguous gate transfer; do not resend')
        conn.settimeout(_remaining(deadline))
        conn.sendall(struct.pack('!I', len(raw)) + raw)
        conn.shutdown(socket.SHUT_WR)
    finally:
        lease.close()


def receive_ticket(conn, gate, *, expected_uid, timeout):
    """Authenticate before allocation; reject ancillary data anywhere but marker.

    recvmsg is used for the complete frame so malicious extra rights cannot
    disappear into recv(). All installed descriptors are closed on every error.
    Receiver does NOT call flock on the received description.
    """
    require(peer_uid(conn) == expected_uid, 'Unauthorized', 'Evaluator peer differs')
    deadline, owned = _deadline(timeout), []
    itemsize = array.array('i').itemsize

    def read(count, rights=False):
        conn.settimeout(_remaining(deadline))
        data, ancillary, flags, _ = conn.recvmsg(count, socket.CMSG_SPACE(16 * itemsize))
        found = []
        ancillary_valid = True
        for level, kind, payload in ancillary:
            if level == socket.SOL_SOCKET and kind == socket.SCM_RIGHTS:
                decoded = array.array('i')
                decoded.frombytes(payload[:len(payload) - len(payload) % itemsize])
                for fd in decoded:
                    owned.append(fd)
                    os.set_inheritable(fd, False)
                    found.append(fd)
                ancillary_valid = ancillary_valid and len(payload) % itemsize == 0
            else:
                ancillary_valid = False
        require(not (flags & (socket.MSG_CTRUNC | socket.MSG_TRUNC)) and ancillary_valid,
                'InvalidInput', 'Invalid or truncated ancillary data')
        require((rights and len(ancillary) == 1 and len(found) == 1)
                or (not rights and not ancillary), 'InvalidInput', 'Wrong rights inventory')
        require(bool(data), 'InvalidInput', 'Incomplete handoff frame')
        return data

    def exact(count):
        result = bytearray()
        while len(result) < count:
            result.extend(read(count - len(result)))
        return bytes(result)

    try:
        require(read(1, rights=True) == MARKER, 'InvalidInput', 'Wrong handoff marker')
        gate.validate(owned[0])
        length = struct.unpack('!I', exact(4))[0]
        require(0 < length <= MAX_WIRE, 'InvalidInput', 'Ticket length differs')
        raw = exact(length)
        try:
            ticket = json.loads(raw, object_pairs_hook=unique_fields)
        except (ValueError, UnicodeError) as exc:
            raise Failure('InvalidInput', 'Malformed launch ticket') from exc
        _ticket(ticket)
        require(canonical(ticket) == raw, 'InvalidInput', 'Noncanonical launch ticket')
        _remaining(min(deadline, ticket['deadline_monotonic_ns']))
        # Framing is request-half-closed; EOF proves there are no trailing bytes
        # or ancillary messages. The full-duplex response remains available.
        conn.settimeout(_remaining(deadline))
        tail, ancillary, flags, _ = conn.recvmsg(1, socket.CMSG_SPACE(16 * itemsize))
        for level, kind, payload in ancillary:
            if level == socket.SOL_SOCKET and kind == socket.SCM_RIGHTS:
                decoded = array.array('i')
                decoded.frombytes(payload[:len(payload) - len(payload) % itemsize])
                for fd in decoded:
                    owned.append(fd)
                    os.set_inheritable(fd, False)
        require(not tail and not ancillary and not flags, 'InvalidInput', 'Trailing handoff data')
        lease = GateLease(owned.pop(), _OPEN)
        return ticket, lease
    finally:
        for fd in owned:
            os.close(fd)


class _Child:
    def __init__(self, process):
        self.process = process
        self.lock = threading.RLock()
        self.io_lock = threading.Lock()
        self.exit_code = None

    def configure_io(self):
        for stream in (self.process.stdin, self.process.stdout, self.process.stderr):
            os.set_blocking(stream.fileno(), False)

    def poll(self):
        # poll() may reap. Every signal and every reap is under the same lock,
        # and a reaped child is never signalled (PID reuse cannot be adopted).
        with self.lock:
            if self.exit_code is None:
                self.exit_code = self.process.poll()
            return self.exit_code

    def send_signal(self, number):
        with self.lock:
            if self.poll() is None:
                try:
                    os.kill(self.process.pid, number)
                except ProcessLookupError:
                    self.poll()

    def wait(self, seconds):
        deadline = _deadline(seconds)
        while self.poll() is None:
            time.sleep(min(0.005, _remaining(deadline)))
        return self.exit_code

    def cancel(self, grace, kill_wait):
        self.send_signal(signal.SIGTERM)
        try:
            return self.wait(grace)
        except Failure:
            self.send_signal(signal.SIGKILL)
            return self.wait(kill_wait)

    def close_pipes(self):
        with self.io_lock:
            for stream in (self.process.stdin, self.process.stdout, self.process.stderr):
                stream.close()


class LaunchBroker:
    """No arbitrary argv on wire, no caller-supplied readiness flags.

    prepare resolves a trusted compiled catalog callback, stores it only in the
    current boot, and returns an inert intent record. launch requires that exact
    prepared identity plus authenticated transferred lease and trusted callbacks.
    resolve_command, validate_intent and commit_owned belong to reviewed service
    wiring, not to a request. This primitive alone does not qualify that wiring.
    """
    def __init__(self, gate, resolve_command, validate_intent, commit_owned, *,
                 expected_uid, token, nonproduction=False):
        require(token is _OPEN, 'Unauthorized', 'Use explicit broker factory')
        self.gate, self.resolve_command = gate, resolve_command
        self.validate_intent, self.commit_owned = validate_intent, commit_owned
        self.expected_uid, self.nonproduction = expected_uid, nonproduction
        self.owner_start = digest(uuid.uuid4().bytes)
        self.pid, self.lock = os.getpid(), threading.RLock()
        self.prepared, self.children, self.records = {}, {}, {}
        self.handoffs = {}
        self.unusable = False

    @classmethod
    def open_existing(cls, gate, resolve_command, validate_intent, commit_owned):
        require(os.getuid() == RUNNER, 'Unauthorized', 'Actual broker UID required')
        return cls(gate, resolve_command, validate_intent, commit_owned,
                   expected_uid=EVALUATOR, token=_OPEN)

    @classmethod
    def open_public_fixture(cls, gate, resolve_command, validate_intent, commit_owned):
        root = gate.path.parent
        require(root.parent == Path('/private/tmp') and root.name.startswith('grrr-backend-fixture-')
                and os.getuid() not in (0, EVALUATOR, RUNNER, 322),
                'Unauthorized', 'Public fixture path/identity differs')
        st = root.lstat()
        require(stat.S_ISDIR(st.st_mode) and st.st_uid == os.getuid()
                and stat.S_IMODE(st.st_mode) == 0o700, 'Unauthorized', 'Fixture root is not private')
        return cls(gate, resolve_command, validate_intent, commit_owned,
                   expected_uid=os.getuid(), token=_OPEN, nonproduction=True)

    def _live(self):
        require(self.pid == os.getpid() and not self.unusable,
                'RecoveryRequired', 'Broker boot/session no longer usable')

    def prepare(self, operation_id, control_run, epoch, leaf):
        identifier(operation_id, True)
        identifier(control_run, True)
        require(type(epoch) is int and epoch >= 0, 'InvalidInput', 'Epoch differs')
        with self.lock:
            self._live()
            require(all(r['operation_id'] != operation_id for r in self.records.values()),
                    'RecoveryRequired', 'Operation already has a launch; query only')
            command = tuple(self.resolve_command(leaf))
            require(command and all(type(a) is str and '\x00' not in a for a in command)
                    and Path(command[0]).is_absolute(), 'GateBlocked', 'Compiled command differs')
            launch, session = digest(uuid.uuid4().bytes), digest(uuid.uuid4().bytes)
            record = dict(schema='capstone-launch-v1', launch_id=launch,
                          operation_id=operation_id, control_run=control_run,
                          epoch=epoch, session_id=session, state='intent', pid=None,
                          owner_start=self.owner_start, evidence=[])
            self.records[launch], self.prepared[launch] = record, command
            return dict(record)

    def launch(self, conn, *, timeout):
        deadline = _deadline(timeout)
        try:
            ticket, lease = receive_ticket(conn, self.gate, expected_uid=self.expected_uid, timeout=timeout)
        except BaseException:
            conn.close()
            raise
        # Trusted broker bound survives parsing and is never extended by the
        # sender's ticket. The callback gets only this remaining local budget.
        deadline = min(deadline, ticket['deadline_monotonic_ns'])
        child, launch = None, ticket['launch_id']
        try:
            with self.lock:
                self._live()
                require(launch in self.prepared, 'RecoveryRequired', 'Unknown or already used launch')
                record = self.records[launch]
                require(all(ticket[k] == record[k] for k in
                            ('launch_id', 'session_id', 'operation_id', 'control_run', 'epoch')),
                        'StaleBinding', 'Prepared launch identity differs')
                _remaining(deadline)
                self.gate.validate(lease.fd)
                # Callback verifies exact durable evaluator intent, not a bool.
                # It must raise on denial. Broker has no ledger writer handle.
                self.validate_intent(dict(ticket), dict(record))
                _remaining(deadline)
                command = self.prepared.pop(launch)  # one shot even if spawn fails
                process = subprocess.Popen(command, stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True,
                    start_new_session=False)
                child = _Child(process)
                self.children[launch] = child
                self.handoffs[launch] = (lease, conn)
                child.configure_io()  # any failure now has an owned teardown handle
                record = dict(record, state='owned', pid=process.pid)
                self.records[launch] = record
            # No owner map lock across evaluator RPC. Gate IS still held.
            committed = self.commit_owned(dict(ticket), dict(record),
                                          _remaining(deadline))
            with self.lock:
                self._live()  # close/cancel cannot be revived by a late ACK
                require(self.handoffs.get(launch) == (lease, conn),
                        'RecoveryRequired', 'Launch handoff was abandoned')
                require(committed == {'state': 'COMMITTED', 'launch_id': launch,
                                      'session_id': record['session_id'],
                                      'intent_anchor': ticket['intent_anchor'],
                                      'owned_sha256': digest(canonical(record))},
                        'RecoveryRequired', 'Missing or mismatched durable COMMITTED')
                _remaining(deadline)
                lease.close()
                self.handoffs.pop(launch)
            return self.status(launch)
        except BaseException:
            with self.lock:
                self.unusable = True
                if launch in self.records:
                    self.records[launch] = dict(self.records[launch], state='unknown')
                self.handoffs.pop(launch, None)
            # Lost COMMITTED closes gate BEFORE teardown/wait. Stop can commit
            # against the durable intent during this cleanup; it is not absence.
            lease.close()
            conn.close()
            if child is not None:
                try:
                    child.cancel(1, 1)
                except Failure:
                    pass  # unknown remains unknown, never a cessation assertion
            raise
        finally:
            lease.close()

    def status(self, launch_id):
        with self.lock:
            require(self.pid == os.getpid() and launch_id in self.records,
                    'Unavailable', 'No owned launch in this boot')
            result = dict(self.records[launch_id])
            child = self.children.get(launch_id)
            code = child.poll() if child else None
            return {'record': result, 'exit_code': code,
                    'identity': 'NONPRODUCTION' if self.nonproduction else 'installed-broker'}

    def _child(self, launch):
        with self.lock:
            require(self.pid == os.getpid() and launch in self.children,
                    'Unavailable', 'Child is not owned by this broker boot')
            return self.children[launch]

    def read(self, launch, *, stream='stdout', maximum=65536, timeout=1):
        require(stream in ('stdout', 'stderr') and type(maximum) is int and 0 < maximum <= 65536,
                'InvalidInput', 'Read bound differs')
        deadline, child = _deadline(timeout), self._child(launch)
        with child.io_lock, selectors.DefaultSelector() as selector:
            pipe = getattr(child.process, stream)
            require(not pipe.closed, 'Unavailable', 'Owned output pipe is closed')
            fd = pipe.fileno()
            selector.register(fd, selectors.EVENT_READ)
            require(bool(selector.select(_remaining(deadline))), 'Unavailable', 'Read deadline expired')
            return os.read(fd, maximum)

    def write(self, launch, data, *, timeout=1):
        require(type(data) is bytes and len(data) <= 65536, 'InvalidInput', 'Write bound differs')
        deadline, child = _deadline(timeout), self._child(launch)
        offset = 0
        with child.io_lock, selectors.DefaultSelector() as selector:
            require(not child.process.stdin.closed, 'Unavailable', 'Owned input pipe is closed')
            fd = child.process.stdin.fileno()
            selector.register(fd, selectors.EVENT_WRITE)
            while offset < len(data):
                require(bool(selector.select(_remaining(deadline))), 'Unavailable', 'Write deadline expired')
                offset += os.write(fd, data[offset:])
        return offset

    def cancel(self, launch, *, grace=1, kill_wait=1):
        with self.lock:
            child = self._child(launch)
            self._abort_handoff(launch)
        code = child.cancel(grace, kill_wait)
        with self.lock:
            if self.records[launch]['state'] != 'unknown':
                self.records[launch] = dict(self.records[launch], state='ceased')
        return {'launch_id': launch, 'owner_start': self.owner_start, 'exit_code': code,
                'reaped': True, 'identity': 'NONPRODUCTION' if self.nonproduction else 'installed-broker'}

    def _abort_handoff(self, launch):
        # Caller holds owner-map lock; spawn cannot be racing this operation.
        # Release the received description BEFORE any signal/wait, and retain
        # unknown even if the trusted RPC later returns an exact COMMITTED.
        pending = self.handoffs.pop(launch, None)
        if pending is not None:
            self.unusable = True
            self.records[launch] = dict(self.records[launch], state='unknown')
            lease, conn = pending
            lease.close()
            conn.close()

    def close(self):
        # Explicit bounded teardown, never leave a worker-owned child behind.
        with self.lock:
            self.unusable = True
            for launch in list(self.handoffs):
                self._abort_handoff(launch)
            children = list(self.children.values())
        failures = []
        for child in children:
            try:
                child.cancel(1, 1)
            except Failure as exc:
                failures.append(exc)
            finally:
                child.close_pipes()
        if failures:
            raise failures[0]
