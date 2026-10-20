"""Version-one bounded wire format. No caller-supplied role is authoritative."""
import ctypes
import hashlib
import json
import os
from pathlib import Path
import re
import socket
from typing import Any, Callable

MAX_WIRE = 3 * 1024 * 1024
EVALUATOR = 320
RUNNER = 321
GATES = ('source_environment_identity', 'isolation', 'protected_asset_integrity',
         'baseline_correctness', 'trusted_observation', 'independent_replay',
         'specification_traceability', 'evidence_integrity_currency', 'budget_state',
         'reviewer_outcome', 'action_specific_human_approval')
DENIED = ('main-merge', 'production-mutation', 'patch-generation',
          'harness-adaptation', 'paid-call')
PACKETS = {name: {'version': 1, 'command': command} for name, command in
           [('clean', "printf 'CLEAN\\n'"), ('faulty', "printf 'PASS\\n'")]}


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=True, allow_nan=False).encode('ascii')


def digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


VARIANTS = {digest(canonical(packet)): packet for packet in PACKETS.values()}


class Failure(Exception):
    def __init__(self, code: str, message: str, operation: str = 'unknown') -> None:
        self.record = {'code': code, 'message': message, 'operation': operation,
                       'retryable': False, 'receipt': None}
        super().__init__(message)


def require(condition: bool, code: str, message: str) -> None:
    if not condition:
        raise Failure(code, message)


def identifier(value: Any, hashed: bool = False) -> str:
    pattern = r'[0-9a-f]{64}' if hashed else r'[a-zA-Z0-9][a-zA-Z0-9-]{0,63}'
    require(isinstance(value, str) and re.fullmatch(pattern, value) is not None,
            'InvalidInput', 'Malformed identifier or digest')
    return value


def fields(record: dict, required: set[str], optional: set[str] = frozenset()) -> None:
    require(isinstance(record, dict) and required <= record.keys()
            and record.keys() <= required | optional, 'InvalidInput', 'Unknown or missing fields')


def peer_uid(conn: socket.socket) -> int:
    uid, gid = ctypes.c_uint(), ctypes.c_uint()
    libc = ctypes.CDLL(None, use_errno=True)
    require(libc.getpeereid(conn.fileno(), ctypes.byref(uid), ctypes.byref(gid)) == 0,
            'Unauthorized', 'Peer credentials unavailable')
    return uid.value


def receive(conn: socket.socket) -> dict:
    data = bytearray()
    while not data.endswith(b'\n'):
        chunk = conn.recv(min(65536, MAX_WIRE + 1 - len(data)))
        require(bool(chunk), 'InvalidInput', 'Incomplete wire record')
        data.extend(chunk)
        require(len(data) <= MAX_WIRE, 'InvalidInput', 'Wire record too large')
    try:
        value = json.loads(data)
    except (ValueError, UnicodeError) as exc:
        raise Failure('InvalidInput', 'Invalid JSON') from exc
    require(isinstance(value, dict), 'InvalidInput', 'Expected object')
    return value


def call(path: Path, request: dict, timeout: float = 310) -> dict:
    with socket.socket(socket.AF_UNIX) as conn:
        conn.settimeout(timeout)
        try:
            conn.connect(socket_path(path))
            expected_uid = EVALUATOR if path.name == 'evaluator.sock' else RUNNER
            require(peer_uid(conn) == expected_uid, 'Unauthorized', 'Server peer identity mismatch')
            conn.sendall(canonical(request) + b'\n')
            response = receive(conn)
        except (OSError, TimeoutError) as exc:
            raise Failure('Unavailable', 'Endpoint unavailable; query operation before retry') from exc
    if 'error' in response:
        error = response['error']
        raise Failure(error['code'], error['message'], error['operation'])
    return response['ok']


def socket_path(path: Path) -> str:
    """Use short absolute temp-runtime paths; retain relative support on macOS."""
    absolute = str(path.resolve())
    return absolute if len(os.fsencode(absolute)) < 100 else os.path.relpath(path, Path.cwd())


def runtime_binding(root: Path) -> dict:
    """Read parent-owned local endpoint metadata, never a request-supplied role."""
    path = root / '.runtime-endpoint.json'
    require(path.is_file() and not path.is_symlink(), 'Unavailable', 'Parent runtime binding absent')
    stat = path.stat()
    require(stat.st_uid in (0, os.getuid()) and stat.st_mode & 0o022 == 0,
            'Unauthorized', 'Runtime binding has unsafe ownership/mode')
    value = json.loads(path.read_bytes())
    fields(value, {'runtime', 'evidence', 'version'})
    require(value['version'] == 1, 'InvalidInput', 'Runtime binding version invalid')
    runtime = Path(value['runtime'])
    require(runtime.parent == Path('/private/tmp') and runtime.name.startswith('grrr-')
            and not runtime.is_symlink(), 'InvalidInput', 'Runtime must be a dedicated temp directory')
    evidence = Path(value['evidence'])
    require(evidence.parent == root / 'docs/evidence/bounded-challenge'
            and evidence.name.startswith('attempt-'), 'InvalidInput', 'Attempt evidence location invalid')
    return value


def serve(path: Path, handler: Callable[[int, dict], dict]) -> None:
    import threading
    require(not path.exists(), 'RecoveryRequired', 'Existing endpoint requires inspection')
    listener = socket.socket(socket.AF_UNIX)
    listener.bind(socket_path(path))
    os.chmod(path, 0o666)  # Authentication is kernel peer credentials, not payload/umask.
    listener.listen(8)
    slots = threading.BoundedSemaphore(8)

    def respond(conn: socket.socket) -> None:
        with conn:
            conn.settimeout(310)
            try:
                response = {'ok': handler(peer_uid(conn), receive(conn))}
            except Failure as exc:
                response = {'error': exc.record}
            except Exception:
                response = {'error': Failure('RecoveryRequired', 'Unhandled outcome; inspect evidence').record}
            try:
                conn.sendall(canonical(response) + b'\n')
            except OSError:
                import sys
                print('Response transport lost; effects must be queried, not repeated', file=sys.stderr)
        slots.release()

    while True:
        conn, _ = listener.accept()
        if not slots.acquire(blocking=False):
            conn.close()
            continue
        threading.Thread(target=respond, args=(conn,), daemon=True).start()
