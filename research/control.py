"""Evaluator-owned safe stop with durable epoch fencing and cancellation."""
from __future__ import annotations
import math
import os
from pathlib import Path
import sqlite3
import time
import uuid
from typing import Callable
import json

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
        self.db.execute("""CREATE TABLE IF NOT EXISTS admission_fences(
          proposal TEXT PRIMARY KEY, run TEXT NOT NULL, epoch INTEGER NOT NULL,
          blocked INTEGER NOT NULL, event_digest TEXT NOT NULL, key TEXT UNIQUE NOT NULL)""")
        self.recoveries = self.ledger.root / 'recoveries'
        self.halted = bool(list(self.recoveries.glob('recovery-*.json')))
        self.best_effort_error = None

    def close(self) -> None:
        self.ledger.close()

    def register_launch(self, principal: int, run: str, pid: int, epoch: int) -> dict:
        require(principal == EVALUATOR, 'Unauthorized', 'Only evaluator registers launches')
        identifier(run)
        require(type(pid) is int and pid > 1 and type(epoch) is int and epoch >= 0,
                'InvalidInput', 'Invalid launch identity')
        with self.ledger.lock:
            require(not self.halted, 'RecoveryRequired', 'Control recovery is unresolved')
            require(self.can_launch(run, epoch, principal), 'Stopped', 'Run is fenced or epoch differs')
            event = {'kind': 'launch-tracked', 'run': run, 'pid': pid, 'epoch': epoch,
                     'recorded_ns': time.time_ns()}
            key = digest(b'launch\0' + run.encode('ascii'))

            def callback(db: sqlite3.Connection, receipt: dict) -> None:
                row = db.execute('SELECT epoch,stopping,stopped FROM control_runs WHERE run=?',
                                 (run,)).fetchone()
                require(row is None or row == (epoch, 0, 0),
                        'Stopped', 'Stop serialized before launch')
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
        return not self.halted and (row is None or (row == (epoch, 0, 0)
                                                    and self._tracked_epoch(run) == epoch))

    def _tracked_epoch(self, run: str) -> int:
        row = self.db.execute('SELECT epoch FROM tracked_launches WHERE run=?', (run,)).fetchone()
        return row[0] if row else 0

    def stop(self, principal: int, run: str, key: str, reason: str | None = None) -> dict:
        require(principal in (self.operator_uid, EVALUATOR),
                'Unauthorized', 'Only approved operator or watchdog may stop')
        identifier(run)
        identifier(key)
        require(reason is None or (isinstance(reason, str) and len(reason) <= 4096
                and all(32 <= ord(character) < 127 for character in reason)),
                'InvalidInput', 'Invalid stop reason')
        with self.ledger.lock:
            require(not self.halted, 'RecoveryRequired', 'Control recovery is unresolved')
            existing_key = self.db.execute(
                'SELECT operation FROM stop_operations WHERE key=?', (key,)).fetchone()
            if existing_key is not None:
                return self.stop_status(principal, existing_key[0])
            row = self.db.execute(
                'SELECT cr.epoch,so.operation,so.state,so.outcome FROM control_runs cr '
                'JOIN stop_operations so ON so.operation=cr.primary_operation WHERE cr.run=?',
                (run,)).fetchone()
            operation = digest(uuid.uuid4().hex.encode('ascii'))
            now = time.time_ns()
            if row is None:
                epoch, primary, state, outcome = 1, operation, 'stopping', {'cancellation': 'pending'}
                event = {'kind': 'safe-stop', 'run': run, 'operation': operation,
                         'actor_uid': principal, 'reason': reason, 'epoch': epoch,
                         'recorded_ns': now}
            else:
                epoch, primary, state, outcome = row
                outcome = json.loads(outcome)
                event = {'kind': 'safe-stop-reference', 'run': run, 'operation': operation,
                         'primary_operation': primary, 'actor_uid': principal, 'reason': reason,
                         'epoch': epoch, 'recorded_ns': now}

            def callback(db: sqlite3.Connection, receipt: dict) -> None:
                if row is None:
                    db.execute("""INSERT INTO control_runs VALUES(?,?,?,?,?,?,?,?)""",
                               (run, epoch, 1, 0, 0, 0, 'none', primary))
                else:
                    db.execute('UPDATE control_runs SET stopping=1 WHERE run=?', (run,))
                db.execute("""INSERT INTO stop_operations VALUES(?,?,?,?,?,?,?,?,?)""",
                           (operation, key, run, reason, epoch, receipt['digest'], primary,
                            state, canonical(outcome).decode('ascii')))

            try:
                receipt = self.ledger.append_atomic(EVALUATOR, event, self.ledger.tip(), key, callback)
            except BaseException as exc:
                self._failed_stop(run, exc)
                raise Failure('RecoveryRequired',
                              'Stop transaction failed; no durable acknowledgement') from exc
            return self.stop_status(principal, operation)

    def terminate(self, principal: int, operation: str) -> dict:
        require(principal == EVALUATOR, 'Unauthorized', 'Cancellation worker is evaluator-owned')
        identifier(operation, True)
        with self.ledger.lock:
            row = self.db.execute(
                'SELECT run,epoch,state,outcome FROM stop_operations WHERE operation=?',
                (operation,)).fetchone()
            require(row is not None, 'InvalidInput', 'Unknown stop operation')
            run, epoch, state, outcome_raw = row
            if state in ('stopped-safely', 'recovery-required'):
                return self.stop_status(EVALUATOR, operation)
            require(self.terminator is not None, 'RecoveryRequired',
                    'Trusted cancellation worker unavailable')
            try:
                outcome = self.terminator(run, self.term_grace_seconds, self.kill_wait_seconds)
                fields(outcome, {'ceased', 'forced', 'seconds', 'baseline_ok'})
                require(outcome['ceased'] is True and type(outcome['seconds']) in (int, float)
                        and math.isfinite(outcome['seconds']) and 0 <= outcome['seconds'] <= 15,
                        'RecoveryRequired', 'Cancellation cessation is unverified')
                baseline_ok = self.baseline_verifier(outcome) is True
            except (Failure, OSError, ValueError, TypeError) as exc:
                recovery = exc.record if isinstance(exc, Failure) else {'code': 'RecoveryRequired'}
                try:
                    self._record_recovery(operation, run, epoch, recovery)
                except BaseException:
                    self._write_recovery_marker(run, 'cancellation-recording-failed', recovery)
                    raise
                raise Failure('RecoveryRequired', 'Cancellation pending; safe stop not claimed') from exc
            state = 'stopped-safely' if baseline_ok else 'recovery-required'
            recovery = 'none' if baseline_ok else 'baseline-verification-failed'

            def callback(db: sqlite3.Connection, receipt: dict) -> None:
                db.execute("""UPDATE control_runs SET stopped=1,cancelled=1,baseline_ok=?,recovery=?
                              WHERE run=?""", (int(baseline_ok), recovery, run))
                db.execute("""UPDATE stop_operations SET state=?,outcome=?
                              WHERE operation=?""", (state, canonical(outcome).decode('ascii'), operation))
                db.execute('UPDATE tracked_launches SET tracked=0 WHERE run=?', (run,))

            event = {'kind': 'safe-stop-cancellation', 'run': run, 'operation': operation,
                     'epoch': epoch, 'outcome': outcome, 'baseline_ok': baseline_ok,
                     'recovery': recovery, 'recorded_ns': time.time_ns()}
            cancel_key = digest(('cancel\0' + operation).encode('ascii'))
            try:
                self.ledger.append_atomic(EVALUATOR, event, self.ledger.tip(), cancel_key, callback)
            except BaseException as exc:
                self._write_recovery_marker(run, 'cancellation-recording-failed',
                                            {'code': 'RecoveryRequired'})
                raise Failure('RecoveryRequired', 'Cancellation committed but is not acknowledged') from exc
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

    def _failed_stop(self, run: str, cause: BaseException) -> None:
        self.halted = True
        record = cause.record if isinstance(cause, Failure) else {'code': 'RecoveryRequired'}
        try:
            if self.terminator is not None:
                self.terminator(run, self.term_grace_seconds, self.kill_wait_seconds)
        except (Failure, OSError, ValueError, TypeError) as exc:
            self.best_effort_error = (exc.record if isinstance(exc, Failure)
                                      else {'code': 'RecoveryRequired'})
        self._write_recovery_marker(run, 'stop-transaction-failed', record)

    def _write_recovery_marker(self, run: str, reason: str, record: dict) -> None:
        identifier(run)
        require(reason in ('stop-transaction-failed', 'cancellation-recording-failed'),
                'InvalidInput', 'Unknown recovery reason')
        self.recoveries.mkdir(mode=0o700, exist_ok=True)
        require(self.recoveries.stat().st_uid == EVALUATOR
                and not self.recoveries.stat().st_mode & 0o077
                and not self.recoveries.is_symlink(),
                'IntegrityFailure', 'Unsafe recovery-marker directory')
        marker = self.recoveries / ('recovery-' + uuid.uuid4().hex + '.json')
        raw = canonical({'version': 1, 'run': run, 'reason': reason, 'record': record,
                         'recorded_ns': time.time_ns(), 'retry_authorized': False,
                         'promotion_authorized': False})
        descriptor = os.open(marker, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
        try:
            with os.fdopen(descriptor, 'wb', closefd=False) as stream:
                stream.write(raw)
                stream.flush()
                os.fsync(descriptor)
        finally:
            os.close(descriptor)
        directory = os.open(self.recoveries, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)

    def admission_fence(self, principal: int, run: str, proposal: str, key: str) -> dict:
        """Serialize control-side admission authority without any registry effect."""
        require(principal == EVALUATOR, 'Unauthorized', 'Only evaluator checks admission fence')
        identifier(run)
        identifier(proposal, True)
        identifier(key)
        with self.ledger.lock:
            require(not self.halted, 'RecoveryRequired', 'Control recovery is unresolved')
            row = self.db.execute(
                'SELECT epoch,stopping,stopped FROM control_runs WHERE run=?', (run,)).fetchone()
            epoch = 0 if row is None else row[0]
            blocked = row is not None and bool(row[1] or row[2])
            event = {'kind': 'admission-fence', 'run': run, 'proposal': proposal,
                     'epoch': epoch, 'blocked': blocked, 'registry_effect': False,
                     'recorded_ns': time.time_ns()}

            def callback(db: sqlite3.Connection, receipt: dict) -> None:
                current = db.execute('SELECT epoch,stopping,stopped FROM control_runs WHERE run=?',
                                     (run,)).fetchone()
                require(current == row, 'Stopped', 'Stop serialized before admission record')
                db.execute('INSERT INTO admission_fences VALUES(?,?,?,?,?,?)',
                           (proposal, run, epoch, int(blocked), receipt['digest'], key))

            receipt = self.ledger.append_atomic(EVALUATOR, event, self.ledger.tip(), key, callback)
            return {'run': run, 'proposal': proposal, 'epoch': epoch,
                    'admission': 'blocked' if blocked else 'allowed-before-registry',
                    'receipt': receipt['digest'], 'registry_effect': False,
                    'retry_authorized': False, 'promotion_authorized': False}

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
        if message['action'] == 'status':
            fields(message, {'action', 'operation'})
            return self.stop_status(uid, message['operation'])
        fields(message, {'action', 'run', 'key'}, {'reason'})
        require(message['action'] == 'stop', 'InvalidInput', 'Unknown control action')
        receipt = self.stop(uid, message['run'], message['key'], message.get('reason'))
        if receipt['state'] == 'stopping':
            return self.terminate(EVALUATOR, receipt['operation'])
        return receipt


class StopService:
    def __init__(self, path: Path, coordinator: StopCoordinator) -> None:
        self.coordinator = coordinator
        self.operator_server = AuthenticatedServer(path / 'operator-control.sock', coordinator.handle,
                                                   control=True,
                                                   allowed_uid=coordinator.operator_uid)
        self.watchdog_server = AuthenticatedServer(path / 'watchdog-control.sock', coordinator.handle,
                                                    control=True, allowed_uid=EVALUATOR)

    def close(self) -> None:
        self.operator_server.close()
        self.watchdog_server.close()
