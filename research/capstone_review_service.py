"""Peer-first independent reviewer/context RPC, separate from operator traffic.

The installed service takes an ALREADY bound, installer-approved socket; this
module never provisions protected topology. Public factories create private
temporary sockets and label their local identity NONPRODUCTION. Context lives
only in the current evaluator process and is destroyed on unregister/close.
"""
import base64
import json
import os
from pathlib import Path
import socket
import threading
import time

from common import (EVALUATOR, Failure, MAX_WIRE, canonical, digest, fields,
                    identifier, peer_uid, require, unique_fields)
from capstone_review import REVIEWER, _fixture_root, request_hash

IPC = Path('/Library/GRRR/capstone-v1/ipc')
CONTEXT_FIELDS = {'action', 'version', 'campaign_operation_id', 'leaf_id',
                  'actual_plan_bytes_sha256', 'nonce', 'service_epoch'}


class ReviewClient:
    """Retrieve from the authenticated reviewer, then enforce exact bindings.

    The expected mapping is resolved by trusted evaluator policy/approval joins,
    not extracted from a caller's Plan gates. No direct copied-JSON acceptance
    entrypoint exists here. Independent verifier implementation remains a
    separate trusted service dependency.
    """
    def __init__(self, path, uid, timeout, identity):
        self.path, self.uid, self.timeout, self.identity = path, uid, timeout, identity

    @classmethod
    def open_existing(cls, *, timeout):
        require(os.getuid() == EVALUATOR, 'Unauthorized', 'Actual evaluator UID required')
        return cls(IPC / 'reviewer.sock', REVIEWER, timeout, 'installed-review-client')

    @classmethod
    def open_public_fixture(cls, root, *, timeout=2):
        return cls(_fixture_root(root) / 'reviewer.sock', os.getuid(), timeout, 'NONPRODUCTION')

    def review_and_get(self, request, expected):
        key = request_hash(request)
        first = review_call(self.path, request, expected_uid=self.uid, timeout=self.timeout)
        # Even a fresh review response is not accepted without retrieval from
        # the durable independently owned request index.
        result = review_call(self.path, dict(action='get-review', version=2, request_sha256=key),
                             expected_uid=self.uid, timeout=self.timeout)
        require(first == result, 'IntegrityFailure', 'Review retrieval changed original bytes')
        fields(result, {'request_sha256', 'review_sha256', 'review_raw'})
        from capstone_backend_contract import decode_raw, decode_record
        from capstone_contract import decode_record as decode_v1, operation_id
        raw = decode_raw(result['review_raw'])
        review = decode_record(raw, 'ReviewV2')
        plan_raw = decode_raw(request['actual_plan_raw'])
        plan = decode_v1(plan_raw, 'Plan')
        require(result['request_sha256'] == key and result['review_sha256'] == digest(raw),
                'IntegrityFailure', 'Review retrieval digest differs')
        keys = {'reviewer_identity', 'verifier_inventory', 'policy_sha256',
                'source_review_sha256', 'static_review_sha256', 'authorization_bytes_sha256',
                'campaign_spec_sha256', 'campaign_plan_sha256', 'leaf_id', 'grant_bytes_sha256',
                'operation_id', 'actual_plan_sha256', 'actual_plan_bytes_sha256',
                'observation_sha256', 'service_epoch', 'anchor'}
        fields(expected, keys | {'evidence'})
        require(all(review[k] == expected[k] for k in keys)
                and review['evidence'] == expected['evidence'],
                'StaleBinding', 'Independent review exact approved bindings differ')
        require(review['phase'] == 'actual-plan-prelaunch' and review['verdict'] == 'pass'
                and review['blockers'] == [] and review['leaf_id'] == request['leaf_id']
                and review['actual_plan_bytes_sha256'] == digest(plan_raw)
                and review['actual_plan_sha256'] == plan['plan_sha256']
                and review['operation_id'] == operation_id(plan['grant']['grant_id'], plan['plan_sha256'])
                and review['observation_sha256'] == digest(canonical(plan['observation']))
                and review['anchor'] == plan['observation']['anchor']
                and review['service_epoch'] == plan['observation']['service_epoch'],
                'GateBlocked', 'Review phase, verdict or actual Plan differs')
        bounds = plan['grant']['bounds']
        require(review['reviewed_ns'] <= time.time_ns() < review['expires_ns']
                <= min(bounds['expires_ns'], plan['observation']['observed_ns'] + bounds['receipt_max_age_ns']),
                'StaleBinding', 'Review expired or extends observation authority')
        return raw


def _read(conn, deadline):
    raw = bytearray()
    while not raw.endswith(b'\n'):
        left = deadline - time.monotonic()
        require(left > 0, 'Unavailable', 'Review RPC absolute deadline expired')
        conn.settimeout(left)
        data = conn.recv(min(65536, MAX_WIRE + 1 - len(raw)))
        require(bool(data), 'InvalidInput', 'Incomplete review RPC')
        raw.extend(data)
        require(len(raw) <= MAX_WIRE, 'InvalidInput', 'Review RPC exceeds wire bound')
    try:
        value = json.loads(raw, object_pairs_hook=unique_fields,
                           parse_constant=lambda x: (_ for _ in ()).throw(ValueError(x)))
    except (ValueError, UnicodeError, RecursionError) as exc:
        raise Failure('InvalidInput', 'Malformed review RPC') from exc
    require(canonical(value) + b'\n' == bytes(raw), 'InvalidInput', 'Noncanonical review RPC')
    return value


def review_call(path, request, *, expected_uid, timeout):
    """Trusted wiring selects path/peer; no payload role/UID is accepted."""
    require(type(timeout) in (int, float) and 0 < timeout <= 15,
            'InvalidInput', 'Review RPC timeout bound differs')
    raw = canonical(request) + b'\n'
    require(len(raw) <= MAX_WIRE, 'InvalidInput', 'Review RPC exceeds wire bound')
    deadline = time.monotonic() + timeout
    with socket.socket(socket.AF_UNIX) as conn:
        conn.settimeout(timeout)
        conn.connect(str(path))
        require(peer_uid(conn) == expected_uid, 'Unauthorized', 'Review RPC peer differs')
        conn.settimeout(max(0.000001, deadline - time.monotonic()))
        conn.sendall(raw)
        response = _read(conn, deadline)
    fields(response, set(), {'ok', 'error'})
    require(len(response) == 1, 'InvalidInput', 'Ambiguous review RPC response')
    if 'error' in response:
        error = response['error']
        fields(error, {'code', 'message', 'operation', 'retryable', 'receipt'})
        require(error['code'] in ('Unauthorized', 'InvalidInput', 'StaleBinding', 'GateBlocked',
                'BudgetUnknown', 'BudgetExceeded', 'Stopped', 'IntegrityFailure', 'Unavailable',
                'RecoveryRequired') and type(error['message']) is str and len(error['message']) <= 1024
                and error['retryable'] is False, 'RecoveryRequired', 'Unrecognized reviewer error')
        raise Failure(error['code'], error['message'], error['operation'])
    return response['ok']


class ReviewContext:
    """In-memory prospective bytes; never reconstructs an owner from a row.

    validate_current is trusted evaluator wiring. It must resolve the CURRENT
    owner/campaign/anchor/static joins, raising on stale/stopped/lost ownership.
    No truthy callback result, caller pass flag or supplied anchor is authority.
    """
    def __init__(self, validate_current):
        self.pid, self.lock = os.getpid(), threading.RLock()
        self.validate_current = validate_current
        self.entries = {}

    def register(self, campaign, leaf, plan_raw, observation_raw, owner):
        from capstone_contract import decode_record
        identifier(campaign, True)
        identifier(leaf, True)
        require(owner is not None, 'Unauthorized', 'Live owner capability is absent')
        plan = decode_record(plan_raw, 'Plan')
        observation = decode_record(observation_raw, 'Receipt')
        require(canonical(plan) == plan_raw and canonical(observation) == observation_raw
                and plan['observation'] == observation and observation['anchor'] is not None,
                'StaleBinding', 'Prospective actual Plan/receipt bytes differ')
        with self.lock:
            require(self.pid == os.getpid() and (campaign, leaf) not in self.entries,
                    'RecoveryRequired', 'Context already registered or inherited')
            self.validate_current(campaign, leaf, owner, plan_raw, observation)
            self.entries[campaign, leaf] = (plan_raw, observation_raw, owner)

    def handle(self, request):
        from capstone_contract import decode_record
        fields(request, CONTEXT_FIELDS)
        require(request['action'] == 'review-context' and type(request['version']) is int
                and request['version'] == 2, 'InvalidInput', 'Wrong context request')
        for name in CONTEXT_FIELDS - {'action', 'version'}:
            identifier(request[name], True)
        key = request['campaign_operation_id'], request['leaf_id']
        with self.lock:
            require(self.pid == os.getpid() and key in self.entries,
                    'Unavailable', 'No live selected review context')
            plan_raw, receipt_raw, owner = self.entries[key]
            receipt = decode_record(receipt_raw, 'Receipt')
            require(request['actual_plan_bytes_sha256'] == digest(plan_raw)
                    and request['nonce'] == receipt['nonce']
                    and request['service_epoch'] == receipt['service_epoch'],
                    'StaleBinding', 'Review context nonce/epoch/bytes differ')
            self.validate_current(key[0], key[1], owner, plan_raw, receipt)
            return dict(schema='capstone-jit-context-v2', campaign_operation_id=key[0], leaf_id=key[1],
                        actual_plan_bytes_sha256=digest(plan_raw),
                        observation_raw=base64.b64encode(receipt_raw).decode('ascii'),
                        anchor=receipt['anchor'], service_epoch=receipt['service_epoch'])

    def unregister(self, campaign, leaf):
        with self.lock:
            self.entries.pop((campaign, leaf), None)

    def close(self):
        with self.lock:
            self.entries.clear()


class ReviewHandler:
    def __init__(self, store, verifier):
        self.store, self.verifier = store, verifier

    def handle(self, request):
        if request.get('action') == 'review-plan':
            request_hash(request)
            return self.store.review(request, self.verifier)
        fields(request, {'action', 'version', 'request_sha256'})
        require(request['action'] == 'get-review' and type(request['version']) is int
                and request['version'] == 2, 'InvalidInput', 'Wrong get-review request')
        return self.store.get(identifier(request['request_sha256'], True))


class ReviewServer:
    """Dedicated capacity, bounded peer-first parsing, explicit joined teardown."""
    def __init__(self, listener, handler, expected_uid, timeout, nonproduction):
        require(type(timeout) in (int, float) and 0 < timeout <= 15,
                'InvalidInput', 'Review server deadline differs')
        self.listener, self.handler = listener, handler
        self.expected_uid, self.timeout = expected_uid, timeout
        self.identity = 'NONPRODUCTION' if nonproduction else 'installed-review-endpoint'
        self.closed, self.lock = threading.Event(), threading.Lock()
        self.slots = threading.BoundedSemaphore(4)
        self.workers, self.connections = set(), set()
        listener.settimeout(0.1)
        self.thread = threading.Thread(target=self._accept)
        self.thread.start()

    @classmethod
    def open_existing(cls, listener, handler, *, role, timeout):
        require(role in ('reviewer', 'context'), 'InvalidInput', 'Unknown review endpoint role')
        uid = REVIEWER if role == 'reviewer' else EVALUATOR
        expected = EVALUATOR if role == 'reviewer' else REVIEWER
        path = IPC / ('reviewer.sock' if role == 'reviewer' else 'review-context.sock')
        require(os.getuid() == uid, 'Unauthorized', 'Actual review endpoint principal differs')
        require(listener.family == socket.AF_UNIX and listener.getsockname() == str(path)
                and listener.getsockopt(socket.SOL_SOCKET, socket.SO_ACCEPTCONN) == 1,
                'Unauthorized', 'Expected existing fixed review listener')
        # Full retained inode/ACL/inventory validation belongs to InstallationV2;
        # this low-level factory alone is not installed topology qualification.
        return cls(listener, handler, expected, timeout, False)

    @classmethod
    def open_public_fixture(cls, root, handler, *, role, timeout=2):
        root = _fixture_root(root)
        require(role in ('reviewer', 'context'), 'InvalidInput', 'Unknown fixture endpoint')
        listener = socket.socket(socket.AF_UNIX)
        try:
            listener.bind(str(root / (role + '.sock')))
            os.chmod(root / (role + '.sock'), 0o600)
            listener.listen(8)
            return cls(listener, handler, os.getuid(), timeout, True)
        except BaseException:
            listener.close()
            raise

    def _accept(self):
        while not self.closed.is_set():
            try:
                conn, _ = self.listener.accept()
            except socket.timeout:
                continue
            except OSError:
                return
            # No read, payload allocation or callback before kernel credentials.
            try:
                require(peer_uid(conn) == self.expected_uid, 'Unauthorized', 'Reviewer peer denied')
            except Failure:
                conn.close()
                continue
            if not self.slots.acquire(False):
                conn.close()
                continue
            worker = threading.Thread(target=self._respond, args=(conn,))
            with self.lock:
                self.workers.add(worker)
                self.connections.add(conn)
            worker.start()

    def _respond(self, conn):
        try:
            with conn:
                deadline = time.monotonic() + self.timeout
                try:
                    request = _read(conn, deadline)
                    response = {'ok': self.handler.handle(request)}
                except Failure as exc:
                    response = {'error': exc.record}
                except Exception:
                    response = {'error': Failure('RecoveryRequired', 'Reviewer outcome uncertain').record}
                raw = canonical(response) + b'\n'
                require(len(raw) <= MAX_WIRE, 'InvalidInput', 'Reviewer result exceeds wire bound')
                left = deadline - time.monotonic()
                require(left > 0, 'Unavailable', 'Reviewer RPC deadline expired')
                conn.settimeout(left)
                conn.sendall(raw)
        except (Failure, OSError):
            pass  # durable result remains retrievable; never rerun effects
        finally:
            with self.lock:
                self.workers.discard(threading.current_thread())
                self.connections.discard(conn)
            self.slots.release()

    def close(self):
        self.closed.set()
        self.listener.close()
        self.thread.join(self.timeout + 1)
        with self.lock:
            workers, connections = list(self.workers), list(self.connections)
        for conn in connections:
            try:
                conn.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
        deadline = time.monotonic() + self.timeout + 1
        for worker in workers:
            worker.join(max(0, deadline - time.monotonic()))
        require(not self.thread.is_alive() and all(not w.is_alive() for w in workers),
                'RecoveryRequired', 'Trusted reviewer handler exceeded shutdown bound')
