"""Source-only local journal. No budget authority, transport, or dispatch.

The supplied Ledger is a trusted dependency, not an untrusted caller object.
Production ownership comes from the existing evaluator boundary. Python object
encapsulation is not a sandbox against hostile code in the evaluator process.
"""
from dataclasses import dataclass
import json
import os
from pathlib import Path
import sqlite3
import threading
from typing import Optional, Tuple

from common import EVALUATOR, RUNNER, Failure, canonical, digest, identifier, require, unique_fields
from capstone_contract import decode_record, start_request_digest, validate_record
from capstone_journal_schema import validate_schema
from ledger import Ledger

FORMAT = 'capstone-local-journal-v1'
_OPEN = object()
_MINT = object()


@dataclass(frozen=True)
class JournalRecord:
    """Local state only, deliberately NOT capstone Operation/Receipt/Anchor."""
    operation_id: str
    grant_id: str
    plan_sha256: str
    start_request_sha256: str
    operator_uid: int
    state: str
    reservation: Optional[str]
    stop_requested: bool
    ledger_sequence: int


class DispatchPermit:
    """Opaque, one-use, nonserializable and invalid after fork. No send API.

    consume() returns None once, then refuses. It does NOT couple stop to any
    external send. No permission is recoverable from a JournalRecord.
    """
    __slots__ = ('__pid', '__used', '__lock')

    def __init__(self, token: object) -> None:
        require(token is _MINT, 'Unauthorized', 'Permit cannot be constructed')
        self.__pid, self.__used, self.__lock = os.getpid(), False, threading.Lock()

    def consume(self) -> None:
        with self.__lock:
            require(self.__pid == os.getpid() and not self.__used,
                    'Unavailable', 'Permit unavailable')
            self.__used = True

    def __reduce_ex__(self, protocol):
        raise TypeError('Process-local permit cannot be serialized or copied')

    def __copy__(self):
        raise TypeError('Process-local permit cannot be copied')

    def __deepcopy__(self, memo):
        raise TypeError('Process-local permit cannot be copied')


def _json(raw):
    require(type(raw) is bytes, 'IntegrityFailure', 'Expected stored bytes')
    value = json.loads(raw, object_pairs_hook=unique_fields)
    require(canonical(value) == raw, 'IntegrityFailure', 'Noncanonical journal record')
    return value


def _record(value):
    return JournalRecord(**{k: value[k] for k in JournalRecord.__dataclass_fields__})


def _binding(start, grant):
    validate_record(start, 'Start')
    gid, raw, hashed, auth, uid, consumed = grant
    decoded = decode_record(raw, 'Grant')
    plan = start['plan']
    require(plan['grant'] == decoded and gid == decoded['grant_id']
            and digest(raw) == hashed == plan['grant_bytes_sha256']
            and auth == decoded['authorization_bytes_sha256'] == plan['authorization_bytes_sha256']
            and type(uid) is int and uid == decoded['operator_uid'],
            'StaleBinding', 'Original issued grant/authorization differs')


def _validate_value(value, grants):
    require(type(value) is dict and set(value) == set(JournalRecord.__dataclass_fields__) | {'start'},
            'IntegrityFailure', 'Journal record fields differ')
    start = value['start']
    validate_record(start, 'Start')
    gid = start['plan']['grant']['grant_id']
    require(gid in grants, 'IntegrityFailure', 'Grant missing')
    _binding(start, grants[gid])
    require(value['operation_id'] == start['operation_id'] and value['grant_id'] == gid
            and value['plan_sha256'] == start['plan']['plan_sha256']
            and value['start_request_sha256'] == start_request_digest(start)
            and type(value['operator_uid']) is int and value['operator_uid'] == grants[gid][4]
            and type(value['stop_requested']) is bool
            and type(value['ledger_sequence']) is int and value['ledger_sequence'] > 0
            and value['state'] in ('claimed', 'reserved', 'dispatch-pending', 'unknown'),
            'IntegrityFailure', 'Journal record binding/state differs')
    if value['reservation'] is not None:
        identifier(value['reservation'], True)
    require((value['state'] == 'claimed') == (value['reservation'] is None),
            'IntegrityFailure', 'Reservation/state differs')


def _transition(old, new, action):
    """Validate the entire transition, not just selected mutable fields."""
    expected = dict(old, ledger_sequence=new['ledger_sequence']) if old else None
    if action == 'claim':
        require(old is None and new['state'] == 'claimed' and new['reservation'] is None
                and new['stop_requested'] is False, 'IntegrityFailure', 'Invalid claim')
        return
    require(old is not None, 'IntegrityFailure', 'Transition without claim')
    if action == 'reserve':
        require(old['state'] == 'claimed' and not old['stop_requested']
                and new['reservation'] is not None, 'Stopped', 'Cannot reserve')
        expected.update(state='reserved', reservation=new['reservation'])
    elif action == 'pending':
        require(old['state'] == 'reserved' and not old['stop_requested'],
                'Stopped', 'Dispatch cannot become pending')
        expected.update(state='dispatch-pending')
    elif action == 'stop':
        require(not old['stop_requested'], 'IntegrityFailure', 'Stop already latched')
        expected.update(stop_requested=True)
    else:
        raise Failure('IntegrityFailure', 'Unknown journal transition')
    require(new == expected, 'IntegrityFailure', 'Invalid journal transition')


def _validate(db, tentative=None):
    """Full snapshot replay, including core chain and idempotency correspondence.

    In an append callback the last event is tentative: validate its chain link,
    but compare durable operations to the prefix BEFORE that event.
    """
    validate_schema(db)
    grants = {}
    for row in db.execute('SELECT * FROM capstone_grants'):
        gid, raw, hashed, auth, uid, consumed = row
        g = decode_record(raw, 'Grant')
        require(gid == g['grant_id'] and hashed == digest(raw)
                and auth == g['authorization_bytes_sha256']
                and type(uid) is int and uid == g['operator_uid'],
                'IntegrityFailure', 'Corrupt grant row')
        if consumed is not None:
            identifier(consumed, True)
        grants[gid] = row
    expected, prior, keys = {}, '0' * 64, {}
    events = db.execute('SELECT seq,prior,hash,body FROM events ORDER BY seq').fetchall()
    for sequence, (seq, parent, hashed, raw) in enumerate(events, 1):
        require(seq == sequence and parent == prior and hashed == digest(prior.encode() + raw),
                'IntegrityFailure', 'Nonlinear or corrupt ledger chain')
        event = _json(raw)
        key = identifier(event['idempotency_key'])
        require(key not in keys and type(event['version']) is int and event['version'] == 1,
                'IntegrityFailure', 'Duplicate event key/version')
        keys[key] = (seq, parent, hashed, raw)
        prior = hashed
        if tentative is not None and seq == tentative:
            require(seq == len(events), 'IntegrityFailure', 'Tentative event not last')
            continue
        if event.get('format') == FORMAT:
            require(set(event) == {'format', 'action', 'record', 'idempotency_key', 'version'},
                    'IntegrityFailure', 'Journal event fields differ')
            value = event['record']
            _validate_value(value, grants)
            oid = value['operation_id']
            require(value['ledger_sequence'] == seq, 'IntegrityFailure', 'Sequence binding differs')
            _transition(expected.get(oid), value, event['action'])
            expected[oid] = value
    actual_keys = {r[0]: tuple(r[1:]) for r in db.execute('SELECT key,seq,prior,hash,body FROM idempotency')}
    require(keys == actual_keys, 'IntegrityFailure', 'Idempotency history differs')
    actual = {}
    for oid, gid, raw in db.execute('SELECT * FROM capstone_operations'):
        value = _json(raw)
        _validate_value(value, grants)
        require(oid == value['operation_id'] and gid == value['grant_id'],
                'IntegrityFailure', 'Operation index differs')
        actual[oid] = value
    require(actual == expected, 'IntegrityFailure', 'Operation history differs')
    owners = {v['grant_id']: oid for oid, v in expected.items()}
    require(len(owners) == len(expected) and all(row[5] == owners.get(gid) for gid, row in grants.items()),
            'IntegrityFailure', 'Grant consumption history differs')
    return grants, actual, prior, len(events)


class Journal:
    def __init__(self, ledger: Ledger, token: object) -> None:
        require(token is _OPEN and isinstance(ledger, Ledger), 'Unauthorized', 'Use an existing-ledger factory')
        self._ledger = ledger
        self._read(lambda grants, records, tip, count: None)

    def _read(self, callback):
        db = self._ledger.db
        with self._ledger.lock:
            require(not db.in_transaction, 'RecoveryRequired', 'Unexpected active transaction')
            try:
                db.execute('BEGIN')
                result = callback(*_validate(db))
                db.rollback()  # SELECT-only snapshot, never a status write
                return result
            except BaseException as exc:
                db.rollback()
                if isinstance(exc, (sqlite3.Error, ValueError, TypeError, KeyError)):
                    raise Failure('IntegrityFailure', 'Invalid existing journal') from exc
                raise

    @staticmethod
    def _authorized(records, oid, uid):
        identifier(oid, True)
        require(oid in records, 'Unavailable', 'Operation absent')
        value = records[oid]
        require(type(uid) is int and uid == value['operator_uid'], 'Unauthorized', 'Operator differs')
        return value

    def status(self, operation_id: str, authenticated_uid: int) -> JournalRecord:
        return self._read(lambda g, r, t, n: _record(self._authorized(r, operation_id, authenticated_uid)))

    def _change(self, action, prepare):
        """A cached append NEVER counts as a new transition or mints a permit.

        Contention fails closed; the caller may read status and explicitly retry.
        No transaction is automatically retried after an ambiguous commit error.
        """
        with self._ledger.lock:
            value, changed, tip, count = self._read(prepare)
            if not changed:
                return _record(value), False
            value = dict(value, ledger_sequence=count + 1)
            event = dict(format=FORMAT, action=action, record=value)
            key = digest(canonical(event))
            applied = []

            def commit(db, receipt):
                grants, records, current, total = _validate(db, receipt['sequence'])
                require(receipt['prior'] == tip and receipt['sequence'] == count + 1
                        and current == receipt['digest'] and total == count + 1,
                        'StaleBinding', 'Concurrent ledger append')
                fresh, needed, fresh_tip, fresh_count = prepare(grants, records, tip, count)
                require(needed and dict(fresh, ledger_sequence=count + 1) == value,
                        'StaleBinding', 'Concurrent journal transition')
                _validate_value(value, grants)
                _transition(records.get(value['operation_id']), value, action)
                if action == 'claim':
                    db.execute('UPDATE capstone_grants SET consumed_by=? WHERE grant_id=?',
                               (value['operation_id'], value['grant_id']))
                    db.execute('INSERT INTO capstone_operations VALUES(?,?,?)',
                               (value['operation_id'], value['grant_id'], canonical(value)))
                else:
                    db.execute('UPDATE capstone_operations SET record=? WHERE operation_id=?',
                               (canonical(value), value['operation_id']))
                _validate(db)
                applied.append(True)

            self._ledger.append_atomic(EVALUATOR, event, tip, key, commit)
            require(applied == [True], 'RecoveryRequired', 'Cached append cannot renew a transition')
            return _record(value), True

    def claim(self, start: dict, authenticated_uid: int) -> JournalRecord:
        # Freeze mutable caller data before crossing the transaction boundary.
        start = decode_record(canonical(validate_record(start, 'Start')), 'Start')
        gid, oid = start['plan']['grant']['grant_id'], start['operation_id']

        def prepare(grants, records, tip, count):
            require(gid in grants, 'Unavailable', 'Grant is not issued')
            grant = grants[gid]
            require(type(authenticated_uid) is int and authenticated_uid == grant[4],
                    'Unauthorized', 'Operator differs')
            _binding(start, grant)
            if grant[5] is not None:
                require(grant[5] == oid and records[oid]['start'] == start,
                        'StaleBinding', 'Consumed grant start differs')
                return records[oid], False, tip, count
            value = dict(operation_id=oid, grant_id=gid, plan_sha256=start['plan']['plan_sha256'],
                         start_request_sha256=start_request_digest(start), operator_uid=authenticated_uid,
                         state='claimed', reservation=None, stop_requested=False,
                         ledger_sequence=count + 1, start=start)
            return value, True, tip, count
        return self._change('claim', prepare)[0]

    def _update(self, oid, action, reservation=None, uid=None):
        identifier(oid, True)
        def prepare(grants, records, tip, count):
            require(oid in records, 'Unavailable', 'Operation absent')
            old = records[oid]
            value = dict(old)
            if action == 'stop':
                self._authorized(records, oid, uid)
                value['stop_requested'] = True
            elif action == 'reserve':
                if old['reservation'] is not None:
                    require(old['reservation'] == reservation, 'StaleBinding', 'Reservation is immutable')
                    return old, False, tip, count
                value.update(state='reserved', reservation=reservation)
            elif action == 'pending':
                if old['state'] in ('dispatch-pending', 'unknown'):
                    return old, False, tip, count
                value['state'] = 'dispatch-pending'
            changed = value != old
            if changed:
                _transition(old, value, action)
            return value, changed, tip, count
        return self._change(action, prepare)

    def record_reserved(self, operation_id: str, reservation: str) -> JournalRecord:
        identifier(reservation, True)
        return self._update(operation_id, 'reserve', reservation)[0]

    def mark_dispatch_pending(self, operation_id: str) -> Tuple[JournalRecord, Optional[DispatchPermit]]:
        record, applied = self._update(operation_id, 'pending')
        return record, DispatchPermit(_MINT) if applied else None

    def request_stop(self, operation_id: str, authenticated_uid: int) -> JournalRecord:
        return self._update(operation_id, 'stop', uid=authenticated_uid)[0]


def open_existing(ledger: Ledger) -> Journal:
    """No constructor, DDL, issuance, repair, filesystem open, or UID override."""
    require(os.getuid() == EVALUATOR, 'Unauthorized', 'Evaluator UID required')
    return Journal(ledger, _OPEN)


def open_public_fixture(ledger: Ledger, directory: Path) -> Journal:
    """Explicit NONPRODUCTION factory; caller preinstalls public fixture data.

    Only private /private/tmp/capstone-journal-fixture-* directories, never a
    protected path. Actual host UID is retained; Ledger methods are unmodified.
    """
    require(os.getuid() not in (0, EVALUATOR, RUNNER), 'Unauthorized',
            'Public fixtures require an actual unprivileged UID')
    require(type(directory) is type(Path()) and directory.is_absolute()
            and directory.parent == Path('/private/tmp')
            and directory.name.startswith('capstone-journal-fixture-')
            and '..' not in directory.parts, 'InvalidInput', 'Not a public fixture path')
    require(not directory.is_symlink() and directory.stat().st_uid == os.getuid()
            and directory.stat().st_mode & 0o077 == 0, 'Unauthorized', 'Fixture is not private')
    require(isinstance(ledger, Ledger), 'InvalidInput', 'Expected fixture Ledger')
    rows = ledger.db.execute('PRAGMA database_list').fetchall()
    require([row[2] for row in rows if row[1] == 'main'] == [str(directory / 'ledger.sqlite')],
            'InvalidInput', 'Fixture database path differs')
    require(not (directory / 'ledger.sqlite').is_symlink(), 'InvalidInput', 'Symlink fixture database')
    return Journal(ledger, _OPEN)
