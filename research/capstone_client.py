"""Explicit-peer source-only IPC. No installed production descriptor exists here."""
import json
import os
import re
from pathlib import Path
import socket
import stat
import time
from typing import Optional
from common import EVALUATOR, Failure, MAX_WIRE, canonical, peer_uid, require, unique_fields
from capstone_contract import CODES, validate_record


def test_endpoint(path: Path) -> str:
    """Lexical rejection precedes ALL metadata; private, public fixtures only."""
    text = str(path)
    parts = text.split('/')
    require(len(parts) == 5 and parts[:3] == ['', 'private', 'tmp']
            and re.fullmatch(r'grrr-wcwy-[A-Za-z0-9_-]+', parts[3]) is not None
            and parts[4] in ('data.sock', 'control.sock')
            and all(p not in ('.', '..') for p in parts) and '\\' not in text
            and len(os.fsencode(text)) < 100, 'InvalidInput', 'Not a public test endpoint')
    parent = path.parent.lstat()
    require(stat.S_ISDIR(parent.st_mode) and parent.st_uid == os.getuid()
            and parent.st_mode & 0o077 == 0, 'Unauthorized', 'Unsafe fixture parent')
    return text


def _receive(conn: socket.socket, maximum: int, deadline: float) -> dict:
    raw = bytearray()
    while not raw.endswith(b'\n'):
        remaining = deadline - time.monotonic()
        require(remaining > 0, 'Unavailable', 'Response deadline exceeded')
        conn.settimeout(remaining)
        chunk = conn.recv(min(65536, maximum + 1 - len(raw)))
        require(bool(chunk), 'InvalidInput', 'Incomplete response')
        raw.extend(chunk)
        require(len(raw) <= maximum, 'InvalidInput', 'Response exceeds bound')
    try:
        result = json.loads(raw, object_pairs_hook=unique_fields,
                            parse_constant=lambda x: (_ for _ in ()).throw(ValueError(x)))
    except (ValueError, UnicodeError, RecursionError) as exc:
        raise Failure('InvalidInput', 'Malformed response') from exc
    require(type(result) is dict and set(result) in ({'ok'}, {'error'}), 'InvalidInput', 'Invalid envelope')
    if 'error' in result:
        e = result['error']
        require(type(e) is dict and set(e) == {'code', 'message', 'operation', 'retryable', 'receipt'}
                and type(e['code']) is str and e['code'] in CODES and type(e['message']) is str
                and len(e['message']) <= 1024 and type(e['operation']) is str
                and len(e['operation']) <= 128 and e['retryable'] is False and e['receipt'] is None,
                'RecoveryRequired', 'Malformed remote failure')
        raise Failure(e['code'], e['message'], e['operation'])
    require(type(result['ok']) is dict, 'InvalidInput', 'Expected record response')
    return result['ok']


def explicit_peer_call(path: Path, request: dict, *, expected_uid: int, timeout: float = 2.0) -> dict:
    """Public fixture transport, not a production endpoint override."""
    endpoint = test_endpoint(path)
    require(type(expected_uid) is int and 0 < expected_uid < 4294967295,
            'InvalidInput', 'Invalid expected UID')
    require(type(timeout) in (int, float) and 0 < timeout <= 15, 'InvalidInput', 'Invalid timeout')
    action = request.get('action') if type(request) is dict else None
    require(type(action) is str and action in ('observe', 'start', 'status', 'stop'),
            'InvalidInput', 'Invalid action')
    validate_record(request, action.title())
    control = action in ('status', 'stop')
    require(path.name == ('control.sock' if control else 'data.sock'), 'InvalidInput', 'Wrong channel')
    maximum = 4096 if control else MAX_WIRE
    raw = canonical(request) + b'\n'
    require(len(raw) <= maximum, 'InvalidInput', 'Request exceeds bound')
    deadline = time.monotonic() + timeout
    with socket.socket(socket.AF_UNIX) as conn:
        conn.settimeout(timeout)
        try:
            metadata = path.lstat()
            require(stat.S_ISSOCK(metadata.st_mode) and metadata.st_uid == os.getuid(),
                    'Unauthorized', 'Unsafe fixture socket')
            conn.connect(endpoint)
            try:
                uid = peer_uid(conn)
            except (AttributeError, OSError) as exc:
                raise Failure('Unauthorized', 'Kernel credentials unavailable') from exc
            require(uid == expected_uid, 'Unauthorized', 'Server identity differs before payload')
            conn.sendall(raw)
            response = _receive(conn, maximum, deadline)
        except (OSError, TimeoutError) as exc:
            raise Failure('Unavailable', 'Transport unavailable; no effect inferred') from exc
    return validate_record(response, 'Receipt' if action == 'observe' else 'Operation')


class Client:
    def __init__(self, root: Optional[Path], expected_uid: int) -> None:
        self._root, self._expected_uid = root, expected_uid

    def call(self, request: dict, *, timeout: float = 2.0) -> dict:
        if self._root is None:
            raise Failure('Unavailable', 'Reviewed production descriptor not installed')
        action = request.get('action') if type(request) is dict else None
        name = 'control.sock' if action in ('status', 'stop') else 'data.sock'
        return explicit_peer_call(self._root / name, request, expected_uid=self._expected_uid, timeout=timeout)


def production_client() -> Client:
    """Pinned UID320; no endpoint, UID, or profile override and no protected I/O."""
    return Client(None, EVALUATOR)


def test_client(root: Path) -> Client:
    require(os.getuid() not in (0, 320, 321), 'Unauthorized', 'Unprivileged fixture required')
    test_endpoint(root / 'data.sock')
    return Client(root, os.getuid())
