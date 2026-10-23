"""Evaluator-owned resource accounting; reservations are not launch authority.

Integer microseconds and USD cents avoid float rounding at ceilings. SQLite
BEGIN IMMEDIATE serializes separate connections/processes, not just threads.
Unknown outcomes never release a reservation. No paid capability is added.
"""
from __future__ import annotations
import json
import os
from pathlib import Path
import sqlite3
import threading
import uuid
from functools import wraps
from typing import Callable, Any
from common import EVALUATOR, Failure, canonical, digest, fields, identifier, require

DIMENSIONS = ('money_cents', 'execution_us', 'review_us')
CEILINGS = {'poc': (5000, 21600_000000, 3600_000000),
            'milestone': (15000, 86400_000000, 10800_000000)}


def storage_guard(method: Callable) -> Callable:
    """Uncertain store outcome halts subsequent work; never retry its effect."""
    @wraps(method)
    def guarded(self: 'Budget', *args: Any, **kwargs: Any) -> Any:
        try:
            if self.existing_identity is not None:
                info = self.path.lstat()
                require((info.st_dev, info.st_ino) == self.existing_identity and info.st_nlink == 1
                        and not self.path.is_symlink(), 'RecoveryRequired', 'Persistent accounting path changed')
            return method(self, *args, **kwargs)
        except (sqlite3.Error, OSError) as exc:
            self.failed = True
            try:
                self.halt()
            except (sqlite3.Error, OSError):
                self.stop_persistence_unknown = True
            raise Failure('RecoveryRequired', 'Accounting store failed; conservative holds retained') from exc
    return guarded


def vector(value: dict) -> dict:
    """Require known finite nonnegative maxima, including an explicit currency."""
    fields(value, {'currency', *DIMENSIONS})
    require(value['currency'] == 'USD', 'BudgetUnknown', 'Only approved USD accounting exists')
    require(all(type(value[k]) is int and 0 <= value[k] <= 2**63 - 1 for k in DIMENSIONS),
            'BudgetUnknown', 'Resource maxima must be finite nonnegative integers')
    return dict(value)


class Budget:
    """One protected database for POC and milestone; POC is never reset away."""
    def __init__(self, path: Path, *, existing: bool = False) -> None:
        require(os.getuid() == EVALUATOR, 'Unauthorized', 'Budget requires evaluator identity')
        require(not path.is_symlink() and path.parent.stat().st_uid == EVALUATOR
                and path.parent.stat().st_mode & 0o077 == 0,
                'Unauthorized', 'Budget parent is not private evaluator storage')
        self.lock = threading.RLock()
        self.path = path
        self.existing_identity = (path.stat().st_dev, path.stat().st_ino) if existing else None
        self.failed = False
        self.stop_persistence_unknown = False
        self.db = sqlite3.connect(path.as_uri() + '?mode=rw' if existing else path,
                                  uri=existing, timeout=5, check_same_thread=False, isolation_level=None)
        os.chmod(path, 0o600)
        self.db.execute('PRAGMA synchronous=FULL')
        self.db.executescript("""
          CREATE TABLE IF NOT EXISTS reservations(
            id TEXT PRIMARY KEY, key TEXT UNIQUE NOT NULL, binding BLOB NOT NULL,
            run TEXT NOT NULL, stage TEXT NOT NULL, maximum BLOB NOT NULL,
            actual BLOB, receipt TEXT);
          CREATE TABLE IF NOT EXISTS metering(
            id TEXT PRIMARY KEY, reservation TEXT UNIQUE NOT NULL, body BLOB NOT NULL);
          CREATE TABLE IF NOT EXISTS overhead(
            key TEXT PRIMARY KEY, category TEXT NOT NULL, duration_us INTEGER NOT NULL);
          CREATE TABLE IF NOT EXISTS state(id INTEGER PRIMARY KEY CHECK(id=1), stopped INTEGER NOT NULL);
          INSERT OR IGNORE INTO state VALUES(1,0);
        """)

    def authorized(self, principal: int) -> None:
        """Payload roles cannot satisfy the current process identity requirement."""
        require(principal == EVALUATOR and os.getuid() == EVALUATOR,
                'Unauthorized', 'Evaluator-only accounting')

    def halt(self) -> None:
        """A persistent stop bit survives missing receipts or storage errors."""
        with self.lock:
            self.db.execute('UPDATE state SET stopped=1 WHERE id=1')

    @storage_guard
    def reserve(self, principal: int, run: str, maximum: dict, key: str,
                stage: str = 'poc', binding: str | None = None) -> dict:
        """Reserve all dimensions atomically; changed duplicate keys are rejected."""
        self.authorized(principal)
        require(not self.failed, 'Stopped', 'Accounting store failed; recovery required')
        identifier(run)
        identifier(key)
        maximum = vector(maximum)
        require(stage in CEILINGS, 'InvalidInput', 'Unknown budget stage')
        if binding is not None:
            identifier(binding, True)
        body = canonical({'run': run, 'maximum': maximum, 'stage': stage, 'binding': binding})
        with self.lock:
            try:
                self.db.execute('BEGIN IMMEDIATE')
                require(self.db.execute('SELECT stopped FROM state').fetchall() == [(0,)],
                        'Stopped', 'Budget stopped; explicit recovery required')
                previous = self.db.execute('SELECT id,binding FROM reservations WHERE key=?', (key,)).fetchone()
                if previous:
                    require(bytes(previous[1]) == body, 'StaleBinding', 'Reservation key changed request')
                    self.db.commit()
                    return {'id': previous[0], 'run': run, 'maximum': maximum, 'dispatch_lease': False}
                rows = self.db.execute('SELECT stage,maximum,actual FROM reservations').fetchall()
                for ceiling_stage, ceiling in CEILINGS.items():
                    # Every POC charge also counts against milestone; milestone
                    # charges do not erase or consume the separate POC allowance.
                    if ceiling_stage == 'poc' and stage != 'poc':
                        continue
                    values = [json.loads(actual if actual is not None else reserved)
                              for row_stage, reserved, actual in rows
                              if ceiling_stage == 'milestone' or row_stage == 'poc']
                    require(all(sum(v[k] for v in values) + maximum[k] <= cap
                                for k, cap in zip(DIMENSIONS, ceiling)),
                            'BudgetExceeded', ceiling_stage + ' resource ceiling exhausted')
                reservation = uuid.uuid4().hex
                self.db.execute('INSERT INTO reservations VALUES(?,?,?,?,?,?,NULL,NULL)',
                                (reservation, key, body, run, stage, canonical(maximum)))
                self.db.commit()
            except BaseException:
                self.db.rollback()
                raise
        return {'id': reservation, 'run': run, 'maximum': maximum, 'dispatch_lease': False}

    @storage_guard
    def meter(self, principal: int, reservation: str, usage: dict, evidence: str) -> dict:
        """Register evaluator-measured usage, never a wire-supplied actual vector.

        Caller must have authenticated and validated the execution receipt. The
        current evaluator process measures elapsed time itself. This method is
        intentionally absent from the operator/runner request allowlist.
        """
        self.authorized(principal)
        identifier(reservation)
        identifier(evidence, True)
        usage = vector(usage)
        body = canonical({'reservation': reservation, 'usage': usage, 'evidence': evidence})
        receipt = digest(body)
        with self.lock:
            row = self.db.execute('SELECT maximum FROM reservations WHERE id=?', (reservation,)).fetchone()
            require(row is not None, 'InvalidInput', 'Unknown reservation')
            maximum = json.loads(row[0])
            if any(usage[k] > maximum[k] for k in DIMENSIONS):
                self.halt()
                raise Failure('BudgetExceeded', 'Meter exceeded reservation; conservative hold retained')
            previous = self.db.execute('SELECT id FROM metering WHERE reservation=?', (reservation,)).fetchone()
            require(previous is None or previous[0] == receipt, 'StaleBinding', 'Metering receipt changed')
            self.db.execute('INSERT OR IGNORE INTO metering VALUES(?,?,?)', (receipt, reservation, body))
        return {'reservation': reservation, 'receipt': receipt}

    @storage_guard
    def settle(self, principal: int, reservation: str, actual: dict) -> dict:
        """Only a previously stored trusted meter receipt can release a hold."""
        self.authorized(principal)
        identifier(reservation)
        fields(actual, {'reservation', 'receipt'})
        require(actual['reservation'] == reservation, 'StaleBinding', 'Receipt binds another reservation')
        identifier(actual['receipt'], True)
        with self.lock:
            try:
                self.db.execute('BEGIN IMMEDIATE')
                row = self.db.execute('SELECT body FROM metering WHERE id=? AND reservation=?',
                                      (actual['receipt'], reservation)).fetchone()
                require(row is not None, 'BudgetUnknown', 'Trusted metering missing; reservation retained')
                usage = json.loads(row[0])['usage']
                self.db.execute('UPDATE reservations SET actual=?,receipt=? WHERE id=?',
                                (canonical(usage), actual['receipt'], reservation))
                self.db.commit()
            except BaseException:
                self.db.rollback()
                raise
        return dict(actual, usage=usage, dispatch_lease=False)

    @storage_guard
    def disclose_overhead(self, principal: int, category: str, duration_us: int, key: str) -> None:
        """Preparation/selector overhead is disclosed, never netted from execution."""
        self.authorized(principal)
        identifier(key)
        require(category in ('preparation', 'selector') and type(duration_us) is int
                and 0 <= duration_us <= 2**63 - 1, 'InvalidInput', 'Invalid overhead record')
        with self.lock:
            previous = self.db.execute('SELECT category,duration_us FROM overhead WHERE key=?', (key,)).fetchone()
            require(previous is None or previous == (category, duration_us), 'StaleBinding', 'Overhead key changed')
            self.db.execute('INSERT OR IGNORE INTO overhead VALUES(?,?,?)', (key, category, duration_us))

    @storage_guard
    def totals(self, principal: int) -> dict:
        """Project charged usage plus outstanding worst-case holds in both stages."""
        self.authorized(principal)
        with self.lock:
            rows = self.db.execute('SELECT stage,maximum,actual FROM reservations').fetchall()
            stages = {}
            for stage in CEILINGS:
                values = [json.loads(a if a is not None else m) for s, m, a in rows
                          if stage == 'milestone' or s == 'poc']
                stages[stage] = dict(currency='USD', **{k: sum(v[k] for v in values) for k in DIMENSIONS})
            return {'charged_and_reserved': stages, 'pending': sum(a is None for _, _, a in rows),
                    'overhead_us': dict(self.db.execute('SELECT category,SUM(duration_us) FROM overhead GROUP BY category')),
                    'stopped': bool(self.db.execute('SELECT stopped FROM state').fetchone()[0])}
