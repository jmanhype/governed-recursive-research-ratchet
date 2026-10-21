"""Pre-authenticated IPC with independent control capacity and absolute read bounds."""
import json
import os
from pathlib import Path
import socket
import threading
import time
from common import EVALUATOR, Failure, MAX_WIRE, canonical, peer_uid, require, unique_fields
from common import fields, receive, socket_path


class AuthenticatedServer:
    def __init__(self, path: Path, handler, *, control=False, allowed_uid=EVALUATOR):
        self.path, self.handler = path, handler
        self.control, self.allowed_uid = control, allowed_uid
        self.closed = threading.Event()
        self.slots = threading.BoundedSemaphore(4 if control else 8)
        self.listener = socket.socket(socket.AF_UNIX)
        self.listener.bind(str(path))
        os.chmod(path, 0o666)
        self.listener.listen(64)
        self.listener.settimeout(0.1)
        self.thread = threading.Thread(target=self.accept, daemon=True)
        self.thread.start()

    @staticmethod
    def reject(conn, message):
        try:
            conn.settimeout(0.05)
            conn.sendall(canonical({'error': Failure('Unauthorized', message).record}) + b'\n')
        except OSError:
            conn.close()
        finally:
            conn.close()

    def accept(self):
        while not self.closed.is_set():
            try:
                conn, _ = self.listener.accept()
            except (TimeoutError, socket.timeout):
                continue
            except OSError:
                return
            # Authenticate before reading even one request byte or taking a slot.
            try:
                require(peer_uid(conn) == self.allowed_uid, 'Unauthorized', 'Peer identity denied before payload')
            except Failure:
                self.reject(conn, 'Peer identity denied before payload')
                continue
            if not self.slots.acquire(blocking=False):
                self.reject(conn, 'Request capacity unavailable; query control endpoint')
                continue
            threading.Thread(target=self.respond, args=(conn,), daemon=True).start()

    def receive(self, conn):
        deadline = time.monotonic() + (0.25 if self.control else 1.0)
        maximum = 4096 if self.control else MAX_WIRE
        raw = bytearray()
        while not raw.endswith(b'\n'):
            remaining = deadline - time.monotonic()
            require(remaining > 0, 'InvalidInput', 'Initial request read deadline exceeded')
            conn.settimeout(remaining)
            chunk = conn.recv(min(65536, maximum + 1 - len(raw)))
            require(bool(chunk), 'InvalidInput', 'Incomplete initial request')
            raw.extend(chunk)
            require(len(raw) <= maximum, 'InvalidInput', 'Initial request exceeds cap')
        try:
            value = json.loads(raw, object_pairs_hook=unique_fields,
                parse_constant=lambda x: (_ for _ in ()).throw(ValueError(x)))
        except (ValueError, UnicodeError) as exc:
            raise Failure('InvalidInput', 'Malformed initial request') from exc
        require(isinstance(value, dict), 'InvalidInput', 'Request must be structured object')
        require((value.get('action') in ('stop', 'status')) == self.control,
                'InvalidInput', 'Action requires its dedicated channel')
        return value

    def respond(self, conn):
        try:
            with conn:
                try:
                    message = self.receive(conn)
                    response = {'ok': self.handler(self.allowed_uid, message)}
                except (TimeoutError, socket.timeout):
                    response = {'error': Failure('InvalidInput', 'Initial request read deadline exceeded').record}
                except Failure as exc:
                    response = {'error': exc.record}
                except Exception:
                    response = {'error': Failure('RecoveryRequired', 'Unhandled outcome; do not retry effects').record}
                conn.settimeout(1)
                try:
                    conn.sendall(canonical(response) + b'\n')
                except OSError:
                    # Effects are not replayed when response transport is lost.
                    conn.close()
        finally:
            self.slots.release()

    def close(self):
        self.closed.set()
        self.listener.close()
        self.thread.join(timeout=1)


def control_call(path: Path, request: dict, *, expected_uid: int, timeout: float) -> dict:
    """Call a dedicated control endpoint and authenticate its server UID first."""
    import socket
    require(timeout > 0 and timeout <= 15, 'InvalidInput', 'Control timeout differs from bounds')
    with socket.socket(socket.AF_UNIX) as conn:
        conn.settimeout(timeout)
        try:
            conn.connect(socket_path(path))
            require(peer_uid(conn) == expected_uid, 'Unauthorized', 'Control server identity mismatch')
            conn.sendall(canonical(request) + b'\n')
            response = receive(conn)
        except (OSError, TimeoutError) as exc:
            raise Failure('Unavailable', 'Control endpoint unavailable; query durable state') from exc
    fields(response, set(), {'ok', 'error'})
    require(len(response) == 1, 'InvalidInput', 'Ambiguous control response')
    if 'error' in response:
        error = response['error']
        fields(error, {'code', 'message', 'operation', 'retryable', 'receipt'})
        require(error['code'] in ('Unauthorized', 'InvalidInput', 'StaleBinding', 'GateBlocked',
                'BudgetUnknown', 'BudgetExceeded', 'Stopped', 'IntegrityFailure', 'Unavailable',
                'RecoveryRequired') and isinstance(error['message'], str)
                and len(error['message']) <= 1024 and error['retryable'] is False,
                'RecoveryRequired', 'Unknown control error; do not retry effects')
        raise Failure(error['code'], error['message'], error['operation'])
    return response['ok']
