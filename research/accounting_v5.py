"""Operational v5 accounting for an already provisioned SQLite store.

The object never provisions, migrates, activates, reconciles, resets, or
unstops a store. SQLite BEGIN IMMEDIATE serializes every effect across
processes. Unknown storage outcomes halt and never release an unsettled hold.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import sqlite3
import threading
from functools import wraps
from typing import Any, Callable

from common import Failure, canonical, digest, fields, identifier, require


DIMENSIONS = ('money_cents', 'execution_us', 'review_us')
CEILINGS = {'poc': (5000, 21600_000000, 3600_000000),
            'milestone': (15000, 86400_000000, 10800_000000)}
TABLES = ('reservations', 'metering', 'overhead', 'state', 'store_identity')
COLUMNS = {
    'reservations': [
        (0, 'id', 'TEXT', 0, None, 1), (1, 'key', 'TEXT', 1, None, 0),
        (2, 'binding', 'BLOB', 1, None, 0), (3, 'run', 'TEXT', 1, None, 0),
        (4, 'stage', 'TEXT', 1, None, 0), (5, 'maximum', 'BLOB', 1, None, 0),
        (6, 'actual', 'BLOB', 0, None, 0), (7, 'receipt', 'TEXT', 0, None, 0),
    ],
    'metering': [
        (0, 'id', 'TEXT', 0, None, 1),
        (1, 'reservation', 'TEXT', 1, None, 0),
        (2, 'body', 'BLOB', 1, None, 0),
    ],
    'overhead': [
        (0, 'key', 'TEXT', 0, None, 1), (1, 'category', 'TEXT', 1, None, 0),
        (2, 'duration_us', 'INTEGER', 1, None, 0),
    ],
    'state': [(0, 'id', 'INTEGER', 0, None, 1), (1, 'stopped', 'INTEGER', 1, None, 0)],
    'store_identity': [
        (0, 'campaign', 'TEXT', 1, None, 0), (1, 'store_id', 'TEXT', 1, None, 0),
        (2, 'prior_history_receipt', 'TEXT', 1, None, 0),
    ],
}


def resource(value: dict) -> dict:
    fields(value, {'currency', *DIMENSIONS})
    require(value['currency'] == 'USD', 'InvalidInput', 'Only USD accounting is supported')
    require(all(type(value[name]) is int and 0 <= value[name] <= 2**63 - 1
                for name in DIMENSIONS), 'InvalidInput',
            'Resource values must be finite nonnegative integers')
    return dict(value)


def exact_json(raw: bytes) -> dict:
    def unique(pairs: list[tuple[str, Any]]) -> dict:
        value = {}
        for key, item in pairs:
            require(key not in value, 'InvalidInput', 'Duplicate accounting field')
            value[key] = item
        return value

    try:
        value = json.loads(raw, object_pairs_hook=unique,
                           parse_constant=lambda text: (_ for _ in ()).throw(ValueError(text)))
    except (ValueError, TypeError, UnicodeError) as exc:
        raise Failure('IntegrityFailure', 'Accounting JSON is invalid') from exc
    require(isinstance(value, dict) and canonical(value) == raw, 'IntegrityFailure',
            'Accounting JSON is not canonical')
    return value


def storage_guard(method: Callable[..., Any]) -> Callable[..., Any]:
    """Halt on uncertain storage outcome; never retry or release its effect."""
    @wraps(method)
    def guarded(self: OperationalAccountingV5, *args: Any, **kwargs: Any) -> Any:
        with self.lock:
            try:
                return method(self, *args, **kwargs)
            except Failure as exc:
                if exc.record['code'] == 'IntegrityFailure':
                    self.failed = True
                    self._halt_after_failure()
                raise
            except (sqlite3.Error, OSError) as exc:
                self.failed = True
                self._halt_after_failure()
                raise Failure('RecoveryRequired',
                              'Accounting outcome unknown; conservative hold retained') from exc
    return guarded


class OperationalAccountingV5:
    """A separate existing-store writer with no lifecycle authority."""

    def __init__(self, path: Path, *, allowed_uid: int,
                 connection_factory: Callable[..., sqlite3.Connection] = sqlite3.connect) -> None:
        require(type(allowed_uid) is int and allowed_uid >= 0, 'Unauthorized',
                'Accounting UID must be explicit')
        require(os.getuid() == allowed_uid, 'Unauthorized',
                'Accounting process UID differs from the allowed evaluator')
        require(isinstance(path, Path) and not path.is_symlink(), 'InvalidInput',
                'Accounting path must be an existing regular file')
        try:
            info = path.lstat()
        except FileNotFoundError as exc:
            raise Failure('InvalidInput', 'Accounting store does not exist') from exc
        parent = path.parent.stat()
        require(parent.st_uid == allowed_uid and parent.st_mode & 0o077 == 0
                and info.st_uid == allowed_uid and info.st_mode & 0o077 == 0
                and info.st_nlink == 1, 'Unauthorized', 'Accounting store is not privately owned')
        self.lock = threading.RLock()
        self.path = path
        self.allowed_uid = allowed_uid
        self.existing_identity = (info.st_dev, info.st_ino)
        self.failed = False
        self.stop_persistence_unknown = False
        self.db = None
        try:
            self.db = connection_factory(
                path.as_uri() + '?mode=rw', uri=True, timeout=5,
                check_same_thread=False, isolation_level=None, cached_statements=0,
            )
            self._validate_schema()
            self.lineage = self._validate_rows()
        except Failure as exc:
            self._close()
            if exc.record['code'] in ('IntegrityFailure', 'InvalidInput'):
                raise
            raise Failure('RecoveryRequired', 'Accounting store could not be opened') from exc
        except (sqlite3.Error, OSError) as exc:
            self.failed = True
            self._halt_after_failure()
            self._close()
            raise Failure('RecoveryRequired', 'Accounting store outcome is unknown') from exc

    def close(self) -> None:
        with self.lock:
            self._close()

    def _close(self) -> None:
        if self.db is not None:
            self.db.close()
            self.db = None

    def __enter__(self) -> 'OperationalAccountingV5':
        return self

    def __exit__(self, kind: Any, value: Any, trace: Any) -> None:
        self.close()

    def _validate_schema(self) -> None:
        require(self.db is not None, 'Stopped', 'Accounting connection is closed')
        for suffix in ('-journal', '-wal', '-shm'):
            require(not os.path.lexists(str(self.path) + suffix), 'IntegrityFailure',
                    'Partial accounting journal present')
        schema = self.db.execute('SELECT type,name,tbl_name FROM sqlite_master').fetchall()
        require(all(row[0] in ('table', 'index') for row in schema), 'IntegrityFailure',
                'Unexpected accounting schema object')
        require({row[1] for row in schema if row[0] == 'table'} == set(TABLES),
                'IntegrityFailure', 'Accounting tables differ from v5 layout')
        for table in TABLES:
            require(self.db.execute('PRAGMA table_info(' + table + ')').fetchall()
                    == COLUMNS[table], 'IntegrityFailure',
                    'Accounting columns or constraints differ')
        require(self.db.execute('PRAGMA integrity_check').fetchall() == [('ok',)],
                'IntegrityFailure', 'Accounting integrity check failed')
        require(self.db.execute('PRAGMA journal_mode').fetchall() == [('delete',)],
                'IntegrityFailure', 'Accounting journal mode differs')

    def _validate_rows(self) -> dict:
        state = self.db.execute('SELECT id,stopped FROM state').fetchall()
        require(state == [(1, 0)] or state == [(1, 1)], 'IntegrityFailure',
                'Accounting stop state is invalid')
        identity = self.db.execute(
            'SELECT campaign,store_id,prior_history_receipt FROM store_identity').fetchall()
        require(len(identity) == 1, 'IntegrityFailure', 'Accounting lineage is absent or duplicated')
        campaign, store_id, prior_history = identity[0]
        for value in (campaign, store_id, prior_history):
            identifier(value, True)
        require(store_id != campaign, 'IntegrityFailure', 'Accounting lineage identifiers collide')

        reservations = self.db.execute(
            'SELECT id,key,binding,run,stage,maximum,actual,receipt FROM reservations').fetchall()
        meters = self.db.execute('SELECT id,reservation,body FROM metering').fetchall()
        meter_map = {}
        reservation_ids = {row[0] for row in reservations}
        for receipt, reservation, body in meters:
            require(identifier(receipt, True) == receipt and identifier(reservation)
                    and reservation in reservation_ids and reservation not in meter_map
                    and digest(bytes(body)) == receipt, 'IntegrityFailure',
                    'Meter lineage is orphaned, duplicated, or changed')
            meter = exact_json(bytes(body))
            fields(meter, {'reservation', 'usage', 'evidence'})
            require(meter['reservation'] == reservation, 'IntegrityFailure',
                    'Meter binds another reservation')
            identifier(meter['evidence'], True)
            resource(meter['usage'])
            meter_map[reservation] = (receipt, meter['usage'])

        totals = {stage: dict.fromkeys(DIMENSIONS, 0) for stage in CEILINGS}
        pending = 0
        for reservation, key, request, run, stage, maximum, actual, receipt in reservations:
            require(identifier(reservation) and identifier(key) and identifier(run)
                    and stage in CEILINGS, 'IntegrityFailure', 'Reservation identity is invalid')
            maximum_value = resource(exact_json(bytes(maximum)))
            request_value = exact_json(bytes(request))
            fields(request_value, {'run', 'maximum', 'stage', 'binding'})
            require(request_value == {'run': run, 'maximum': maximum_value,
                                      'stage': stage, 'binding': request_value['binding']}
                    and (request_value['binding'] is None
                         or identifier(request_value['binding'], True)), 'IntegrityFailure',
                    'Reservation request differs from its stored hold')
            if reservation in meter_map and actual is None:
                # A trusted meter receipt may exist before settlement; the hold
                # remains counted at maximum until settlement completes.
                require(receipt is None, 'IntegrityFailure', 'Settlement is partial')
            elif reservation in meter_map:
                require(meter_map[reservation]
                        == (receipt, resource(exact_json(bytes(actual)))),
                        'IntegrityFailure', 'Settlement is not bound to trusted metering')
            used = maximum_value
            if actual is not None:
                used = resource(exact_json(bytes(actual)))
                require(reservation in meter_map, 'IntegrityFailure',
                        'Settlement lacks trusted metering')
            else:
                require(receipt is None, 'IntegrityFailure', 'Settlement is partial')
                pending += 1
            for scope in CEILINGS:
                if scope == 'milestone' or stage == 'poc':
                    for name in DIMENSIONS:
                        totals[scope][name] += used[name]
        for stage, ceiling in CEILINGS.items():
            require(all(totals[stage][name] <= cap
                        for name, cap in zip(DIMENSIONS, ceiling)), 'BudgetExceeded',
                    'Carried accounting exceeds ' + stage + ' ceiling')
        for key, category, duration in self.db.execute(
                'SELECT key,category,duration_us FROM overhead').fetchall():
            require(identifier(key) and category in ('preparation', 'selector')
                    and type(duration) is int and 0 <= duration <= 2**63 - 1,
                    'IntegrityFailure', 'Overhead lineage is invalid')
        return {'campaign': campaign, 'store_id': store_id,
                'prior_history_receipt': prior_history, 'pending': pending,
                'totals': totals, 'stopped': state[0][1] == 1}

    def authorized(self, principal: int) -> None:
        require(type(principal) is int and principal == self.allowed_uid
                and os.getuid() == self.allowed_uid, 'Unauthorized',
                'Accounting principal is not the injected evaluator')

    def _halt_after_failure(self) -> None:
        try:
            if self.db is None:
                raise sqlite3.ProgrammingError('connection closed')
            self.db.execute('UPDATE state SET stopped=1 WHERE id=1')
            self.db.commit()
            require(self.db.execute('SELECT stopped FROM state').fetchone() == (1,),
                    'Stopped', 'Stop state did not persist')
        except (sqlite3.Error, OSError, Failure):
            self.stop_persistence_unknown = True

    def _transaction(self, operation: Callable[[dict], Any]) -> Any:
        require(not self.failed and self.db is not None, 'Stopped',
                'Accounting object failed; recovery required')
        info = self.path.lstat()
        require((info.st_dev, info.st_ino) == self.existing_identity and info.st_nlink == 1
                and not self.path.is_symlink(), 'RecoveryRequired',
                'Accounting path identity changed')
        commit_attempted = False
        self.db.execute('BEGIN IMMEDIATE')
        try:
            self._validate_schema()
            state = self._validate_rows()
            result = operation(state)
            commit_attempted = True
            self.db.commit()
            return result
        except BaseException:
            if not commit_attempted:
                self.db.rollback()
            raise

    @storage_guard
    def reserve(self, principal: int, run: str, maximum: dict, key: str,
                stage: str = 'poc', binding: str | None = None) -> dict:
        self.authorized(principal)
        identifier(run)
        identifier(key)
        require(stage in CEILINGS, 'InvalidInput', 'Unknown accounting stage')
        if binding is not None:
            identifier(binding, True)
        maximum = resource(maximum)
        body = canonical({'binding': binding, 'maximum': maximum, 'run': run, 'stage': stage})

        def effect(state: dict) -> dict:
            require(not state['stopped'], 'Stopped', 'Accounting is halted; reset is unauthorized')
            previous = self.db.execute(
                'SELECT id,binding FROM reservations WHERE key=?', (key,)).fetchone()
            if previous is not None:
                require(bytes(previous[1]) == body, 'StaleBinding',
                        'Reservation key changed request')
                return {'id': previous[0], 'run': run, 'maximum': maximum,
                        'dispatch_lease': False, 'existing': True}
            projected = {name: state['totals'][name] for name in ('poc', 'milestone')}
            for scope, ceiling in CEILINGS.items():
                if scope == 'poc' and stage != 'poc':
                    continue
                require(all(projected[scope][name] + maximum[name] <= cap
                            for name, cap in zip(DIMENSIONS, ceiling)), 'BudgetExceeded',
                        scope + ' resource ceiling exhausted')
            reservation = digest(body + state['store_id'].encode('ascii'))
            identifier(reservation, True)
            self.db.execute(
                'INSERT INTO reservations VALUES(?,?,?,?,?,?,NULL,NULL)',
                (reservation, key, body, run, stage, canonical(maximum)))
            return {'id': reservation, 'run': run, 'maximum': maximum,
                    'dispatch_lease': False, 'existing': False}

        return self._transaction(effect)

    @storage_guard
    def meter(self, principal: int, reservation: str, usage: dict, evidence: str) -> dict:
        self.authorized(principal)
        identifier(reservation)
        identifier(evidence, True)
        usage = resource(usage)
        body = canonical({'evidence': evidence, 'reservation': reservation, 'usage': usage})
        receipt = digest(body)

        def effect(state: dict) -> dict:
            del state
            row = self.db.execute(
                'SELECT maximum FROM reservations WHERE id=?', (reservation,)).fetchone()
            require(row is not None, 'InvalidInput', 'Unknown reservation')
            maximum = resource(exact_json(bytes(row[0])))
            require(all(usage[name] <= maximum[name] for name in DIMENSIONS),
                    'BudgetExceeded', 'Meter exceeded reservation; hold retained')
            previous = self.db.execute(
                'SELECT id FROM metering WHERE reservation=?', (reservation,)).fetchone()
            require(previous is None or previous[0] == receipt, 'StaleBinding',
                    'Trusted meter receipt changed')
            self.db.execute('INSERT OR IGNORE INTO metering VALUES(?,?,?)',
                            (receipt, reservation, body))
            return {'reservation': reservation, 'receipt': receipt}

        return self._transaction(effect)

    @storage_guard
    def settle(self, principal: int, reservation: str, receipt: str) -> dict:
        self.authorized(principal)
        identifier(reservation)
        identifier(receipt, True)

        def effect(state: dict) -> dict:
            del state
            meter = self.db.execute(
                'SELECT body FROM metering WHERE id=? AND reservation=?',
                (receipt, reservation)).fetchone()
            require(meter is not None, 'BudgetUnknown',
                    'Trusted metering missing; reservation retained')
            usage = exact_json(bytes(meter[0]))['usage']
            resource(usage)
            settled = self.db.execute(
                'SELECT actual,receipt FROM reservations WHERE id=?', (reservation,)).fetchone()
            require(settled is not None, 'InvalidInput', 'Unknown reservation')
            if settled[0] is not None:
                require(resource(exact_json(bytes(settled[0]))) == usage
                        and settled[1] == receipt, 'StaleBinding',
                        'Reservation already settled by another receipt')
            else:
                self.db.execute('UPDATE reservations SET actual=?,receipt=? WHERE id=?',
                                (canonical(usage), receipt, reservation))
            return {'reservation': reservation, 'receipt': receipt, 'usage': usage,
                    'dispatch_lease': False}

        return self._transaction(effect)

    @storage_guard
    def halt(self, principal: int) -> None:
        self.authorized(principal)

        def effect(state: dict) -> None:
            del state
            self.db.execute('UPDATE state SET stopped=1 WHERE id=1')

        return self._transaction(effect)

    @storage_guard
    def snapshot(self, principal: int) -> dict:
        self.authorized(principal)
        return self._transaction(lambda state: dict(state, reservations=self.db.execute(
            'SELECT id,key,stage,actual IS NULL FROM reservations ORDER BY id').fetchall()))


AccountingV5 = OperationalAccountingV5
