"""Evaluator-owned safe stop with durable epoch fencing and cancellation."""
from __future__ import annotations
import math
import os
from pathlib import Path
import sqlite3
import time
from typing import Callable
import uuid

from common import EVALUATOR, RUNNER, Failure, canonical, digest, fields, identifier, require
from ledger import Ledger
from trusted_transport import AuthenticatedServer

TERMINATOR = Callable[[str, int, int], dict]
BASELINE = Callable[[dict], bool]


class StopCoordinator:
    def __init__(self, root: Path, *, operator_uid: int, terminator: TERMINATOR = None,
                 baseline_verifier: BASELINE = None, term_grace_seconds: int = 1,
                 kill_wait_seconds: int = 1) -> None:
        require(os.getuid() == EVALUATOR, 'Unauthorized', 'Safe-stop coordinator requires evaluator')
        require(type(operator_uid) is int and operator_uid not in (0, EVALUATOR, RUNNER),
                'InvalidInput', 'Separate operator identity required')
        require(type(term_grace_seconds) is int and 0 < term_grace_seconds <= 5
                and type(kill_wait_seconds) is int and 0 < kill_wait_seconds <= 5,
                'InvalidInput', 'Unsafe cancellation bounds')
        self.operator_uid = operator_uid
        self.terminator = terminator
        self.baseline_verifier = baseline_verifier or (lambda outcome: outcome.get('baseline_ok') is True)
        self.term_grace_seconds = term_grace_seconds
        self.kill_wait_seconds = kill_wait_seconds
        self.ledger = Ledger(root)
        self.db = self.ledger.db
        self.db.execute("""CREATE TABLE IF NOT EXISTS control_runs(
          run TEXT PRIMARY KEY, epoch INTEGER NOT NULL, stopping INTEGER NOT NULL,
          stopped INTEGER NOT NULL, cancelled INTEGER NOT NULL, baseline_ok INTEGER NOT NULL,
          recovery TEXT NOT NULL, primary_operation TEXT NOT NULL)""")
        self.db.execute("""CREATE TABLE IF NOT EXISTS stop_operations(
          operation TEXT PRIMARY KEY, key TEXT UNIQUE NOT NULL, run TEXT NOT NULL,
          reason TEXT, epoch INTEGER NOT NULL, event_digest TEXT NOT NULL,
          primary_operation TEXT NOT NULL, state TEXT NOT NULL, outcome TEXT NOT NULL)""")
        self.db.execute("""CREATE TABLE IF NOT EXISTS tracked_launches(
          run TEXT PRIMARY KEY, pid INTEGER NOT NULL, epoch INTEGER NOT NULL,
          tracked INTEGER NOT NULL)""")

    def close(self) -> None:
        self.ledger.close()

    def register_launch(self, principal: int, run: str, pid: int, epoch: int) -> dict:
        require(principal == EVALUATOR, 'Unauthorized', 'Only evaluator registers launches')
        identifier(run)
        require(type(pid) is int and pid > 1 and type(epoch) is int and epoch >= 0,
                'InvalidInput', 'Invalid launch identity')
        require(self.can_launch(run, epoch, principal), 'Stopped', 'Run is fenced or epoch differs')
        event = {'kind': 'launch-tracked', 'run': run, 'pid': pid, 'epoch': epoch,
                 'recorded_ns': time.time_ns()}
        key = digest(b'launch\0' + run.encode('ascii'))

        def callback(db: sqlite3.Connection, receipt: dict) -> None:
            db.execute('INSERT INTO tracked_launches VALUES(?,?,?,1)', (run, pid, epoch))

        receipt = self.ledger.append_atomic(EVALUATOR, event, self.ledger.tip(), key, callback)
        return dict(receipt, run=run, pid=pid, epoch=epoch, launch_lease=False)

    def can_launch(self, run: str, epoch: int, principal: int = None) -> bool:
        if principal is None:
            principal = EVALUATOR
        require(principal == EVALUATOR, 'Unauthorized', 'Launch check is evaluator-only')
        identifier(run)
        require(type(epoch) is int and epoch >= 0, 'InvalidInput', 'Invalid epoch')
        row = self.db.execute('SELECT epoch,stopping,stopped FROM control_runs WHERE run=?',
                              (run,)).fetchone()
        return row is None or (row == (epoch, 0, 0) and self._tracked_epoch(run) == epoch)

    def _tracked_epoch(self, run: str) -> int:
        row = self.db.execute('SELECT epoch FROM tracked_launches WHERE run=?', (run,)).fetchone()
        return row[0] if row else 0

    def stop(self, principal: int, run: str, key: str, reason: str | None = None) -> dict:
        require(principal == self.operator_uid, 'Unauthorized', 'Only approved operator may stop')
        identifier(run)
        identifier(key)
        require(reason is None or (isinstance(reason, str) and len(reason) <= 4096
                and all(32 <= ord(character) < 127 for character in reason)),
                'InvalidInput', 'Invalid stop reason')
        existing_key = self.db.execute(
            'SELECT operation FROM stop_operations WHERE key=?', (key,)).fetchone()
        if existing_key is not None:
            return self.stop_status(principal, existing_key[0])
        row = self.db.execute(
            'SELECT cr.epoch,so.operation,so.state,so.outcome FROM control_runs cr '
            'JOIN stop_operations so ON so.operation=cr.primary_operation WHERE cr.run=?', (run,)).fetchone()
        operation = digest(uuid.uuid4().hex.encode('ascii'))
        now = time.time_ns()
        if row is None:
            epoch, primary, state, outcome = 1, operation, 'stopping', {'cancellation': 'pending'}
            event = {'kind': 'safe-stop', 'run': run, 'operation': operation,
                     'reason': reason, 'epoch': epoch, 'recorded_ns': now}
        else:
            epoch, primary, state, outcome = row
            event = {'kind': 'safe-stop-reference', 'run': run, 'operation': operation,
                     'primary_operation': primary, 'reason': reason, 'epoch': epoch,
                     'recorded_ns': now}

        def callback(db: sqlite3.Connection, receipt: dict) -> None:
            if row is None:
                db.execute("""INSERT INTO control_runs VALUES(?,?,?,?,?,?,?,?)""",
                           (run, epoch, 1, 0, 0, 0, 'none', primary))
            db.execute("""INSERT INTO stop_operations VALUES(?,?,?,?,?,?,?,?,?)""",
                       (operation, key, run, reason, epoch, receipt['digest'], primary,
                        state, canonical(outcome).decode('ascii')))

        receipt = self.ledger.append_atomic(EVALUATOR, event, self.ledger.tip(), key, callback)
        return self.stop_status(principal, operation)

    def terminate(self, principal: int, operation: str) -> dict:
        require(principal == EVALUATOR, 'Unauthorized', 'Cancellation worker is evaluator-owned')
        identifier(operation, True)
        row = self.db.execute(
            'SELECT run,epoch,state,outcome FROM stop_operations WHERE operation=?',
            (operation,)).fetchone()
        require(row is not None, 'InvalidInput', 'Unknown stop operation')
        run, epoch, state, outcome_raw = row
        if state in ('stopped-safely', 'recovery-required'):
            return self.stop_status(EVALUATOR, operation)
        require(self.terminator is not None, 'RecoveryRequired', 'Trusted cancellation worker unavailable')
        try:
            outcome = self.terminator(run, self.term_grace_seconds, self.kill_wait_seconds)
            fields(outcome, {'ceased', 'forced', 'seconds', 'baseline_ok'})
            require(outcome['ceased'] is True and type(outcome['seconds']) in (int, float)
                    and math.isfinite(outcome['seconds']) and 0 <= outcome['seconds'] <= 15,
                    'RecoveryRequired', 'Cancellation cessation is unverified')
            baseline_ok = self.baseline_verifier(outcome) is True
        except (Failure, OSError, ValueError, TypeError) as exc:
            recovery = exc.record if isinstance(exc, Failure) else {'code': 'RecoveryRequired'}
            self._record_recovery(operation, run, epoch, recovery)
            raise Failure('RecoveryRequired', 'Cancellation pending; safe stop not claimed') from exc
        state = 'stopped-safely' if baseline_ok else 'recovery-required'
        recovery = 'none' if baseline_ok else 'baseline-verification-failed'

        def callback(db: sqlite3.Connection, receipt: dict) -> None:
            db.execute("""UPDATE control_runs SET stopped=1,cancelled=1,baseline_ok=?,recovery=?
                          WHERE run=?""", (int(baseline_ok), recovery, run))
            db.execute("""UPDATE stop_operations SET state=?,outcome=?
                          WHERE operation=?""", (state, canonical(outcome).decode('ascii'), operation))

        event = {'kind': 'safe-stop-cancellation', 'run': run, 'operation': operation,
                 'epoch': epoch, 'outcome': outcome, 'baseline_ok': baseline_ok,
                 'recovery': recovery, 'recorded_ns': time.time_ns()}
        cancel_key = digest(('cancel\0' + operation).encode('ascii'))
        self.ledger.append_atomic(EVALUATOR, event, self.ledger.tip(), cancel_key, callback)
        return self.stop_status(EVALUATOR, operation)

    def _record_recovery(self, operation: str, run: str, epoch: int, recovery: dict) -> None:
        def callback(db: sqlite3.Connection, receipt: dict) -> None:
            db.execute("UPDATE control_runs SET recovery='cancellation-unverified' WHERE run=?", (run,))
            db.execute("UPDATE stop_operations SET state='recovery-required',outcome=? WHERE operation=?",
                       (canonical(recovery).decode('ascii'), operation))

        event = {'kind': 'safe-stop-recovery-required', 'run': run, 'operation': operation,
                 'epoch': epoch, 'recovery': recovery, 'recorded_ns': time.time_ns()}
        recovery_key = digest(('recover\0' + operation + '\0' + uuid.uuid4().hex).encode('ascii'))
        self.ledger.append_atomic(EVALUATOR, event, self.ledger.tip(), recovery_key, callback)

    def stop_status(self, principal: int, operation: str) -> dict:
        require(principal in (EVALUATOR, self.operator_uid), 'Unauthorized', 'Stop status identity denied')
        identifier(operation, True)
        row = self.db.execute(
            'SELECT operation,key,run,reason,epoch,event_digest,primary_operation,state,outcome '
            'FROM stop_operations WHERE operation=?', (operation,)).fetchone()
        require(row is not None, 'InvalidInput', 'Unknown stop operation')
        return {'operation': row[0], 'key': row[1], 'run': row[2], 'reason': row[3],
                'epoch': row[4], 'receipt': row[5], 'primary_operation': row[6],
                'state': row[7], 'outcome': __import__('json').loads(row[8]),
                'retry_authorized': False, 'promotion_authorized': False}

    def handle(self, uid: int, message: dict) -> dict:
        fields(message, {'action', 'run', 'key'}, {'reason'})
        if message['action'] == 'status':
            return self.stop_status(uid, message['run'])
        require(message['action'] == 'stop', 'InvalidInput', 'Unknown control action')
        receipt = self.stop(uid, message['run'], message['key'], message.get('reason'))
        if receipt['state'] == 'stopping':
            return self.terminate(EVALUATOR, receipt['operation'])
        return receipt


class StopService:
    def __init__(self, path: Path, coordinator: StopCoordinator) -> None:
        self.coordinator = coordinator
        self.server = AuthenticatedServer(path, coordinator.handle,
                                          allowed_uid=coordinator.operator_uid)

    def close(self) -> None:
        self.server.close()
