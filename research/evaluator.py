"""Protected evaluator: transport auth, reservations, assertions, durable evidence."""
import os
from pathlib import Path
import threading
import time
import uuid
import sqlite3
from common import (EVALUATOR, RUNNER, DENIED, GATES, VARIANTS, Failure, call,
                    canonical, digest, fields, identifier, require, serve)
from ledger import Ledger, verifySnapshot
from policy import loadPolicy
from budget import Budget
from observation import validate_observation, gate


class Evaluator:
    def __init__(self, root: Path) -> None:
        self.root = root
        require((root / 'policy.json').is_file(), 'Unavailable', 'Missing protected policy')
        self.policy_ref = digest((root / 'policy.json').read_bytes())
        self.policy = loadPolicy(os.getuid(), root / 'policy.json', self.policy_ref)
        self.ledger = Ledger(root)
        require(self.ledger.tip() == '0' * 64, 'RecoveryRequired', 'Restart recovery is not implemented')
        self.lock = threading.RLock()
        self.runs: dict[str, dict] = {}
        self.keys: dict[str, tuple[dict, str]] = {}
        self.bindings: dict[str, dict] = {}
        self.reserved = 0
        self.halted = False
        self.cessation_unknown: set[str] = set()
        self.budget = Budget(root / 'budget.sqlite')
        self.preflight = False
        self.stops: dict[str, tuple[str, dict]] = {}
        self.executor = root.parent / 'ipc/executor.sock'
        self.identity = digest(b''.join(p.read_bytes() for p in sorted((root / 'code').glob('*.py'))))

    def event(self, record: dict, key: str) -> dict:
        try:
            return self.ledger.snapshot(dict(record, recorded_ns=time.time_ns(),
                                            evaluator=self.identity, policy=self.policy_ref), key)
        except (OSError, sqlite3.Error):
            self.halted = True
            # A full evaluator store must not prevent direct executor fencing.
            # Never retry the failed write or a possibly dispatched effect.
            for run, state in self.runs.items():
                if state['execution'] == 'running':
                    state['epoch'] = 1
                    try:
                        call(self.executor, {'action': 'stop', 'run': run}, timeout=8)
                    except Failure:
                        self.cessation_unknown.add(run)
            raise Failure('RecoveryRequired', 'Evaluator store unavailable; work halted')

    def audit(self, uid: int, code: str) -> None:
        # Deliberately exclude arbitrary request strings and raw data from audit metadata.
        self.event({'kind': 'denied', 'actor_uid': uid, 'code': code, 'objects': []}, uuid.uuid4().hex)

    def start(self, request: dict, uid: int, probe: str | None = None) -> dict:
        fields(request, {'action', 'policy', 'challenge', 'variant', 'key', 'epoch'})
        identifier(request['key'])
        identifier(request['variant'], True)
        identifier(request['policy'], True)
        require(request['challenge'] == 'grrr-walk-001' and request['variant'] in VARIANTS,
                'InvalidInput', 'Unknown frozen challenge or variant')
        require(type(request['epoch']) is int and request['epoch'] == 0,
                'StaleBinding', 'Stale epoch')
        with self.lock:
            require(not self.halted, 'Stopped', 'Evaluator halted; explicit recovery required')
            if request['key'] in self.bindings:
                require(self.bindings[request['key']] == request, 'StaleBinding',
                        'Key reused for a different request, including a denied attempt')
            else:
                self.bindings[request['key']] = request.copy()
            loadPolicy(EVALUATOR, self.root / 'policy.json', request['policy'])
            if request['key'] in self.keys:
                previous, run = self.keys[request['key']]
                require(previous == request, 'StaleBinding', 'Key reused for a different request')
                return self.runs[run]
            require(probe or self.preflight, 'GateBlocked', 'Direct stop preflight required before candidate execution')
            require(not any(r['execution'] == 'running' for r in self.runs.values()),
                    'BudgetExceeded', 'Concurrent challenge limit reached')
            require(self.reserved + 300 <= 21600, 'BudgetExceeded', 'POC cumulative reservation exhausted')
            run = uuid.uuid4().hex
            reservation = uuid.uuid4().hex
            reserved = self.budget.reserve(EVALUATOR, run,
                {'currency': 'USD', 'money_cents': 0, 'execution_us': 300_000000, 'review_us': 0},
                request['key'], binding=digest(canonical(request)))
            reservation = reserved['id']
            self.reserved = self.budget.totals(EVALUATOR)['charged_and_reserved']['poc']['execution_us'] / 1000000
            self.runs[run] = {'run': run, 'execution': 'running', 'epoch': 0,
                              'verified': False, 'admission': 'blocked', 'snapshot_id': None}
            self.keys[request['key']] = (request.copy(), run)
            self.event({'kind': 'reserved', 'run': run, 'actor_uid': uid, 'reservation': reservation,
                        'maximum_seconds': 300, 'reserved_total_seconds': self.reserved,
                        'money_cents': 0, 'paid_dispatch': False, 'review_seconds': 0,
                        'objects': []}, request['key'])
        timer = threading.Timer(300, self.deadline, args=(run,))
        timer.start()
        dispatch_started = time.monotonic_ns()
        try:
            observed = call(self.executor, {'action': 'dispatch',
                'request': {'run': run, 'variant': request['variant'], 'probe': probe},
                'reservation': reservation, 'epoch': 0, 'key': request['key']})
            observed = validate_observation(observed, run)
        except Failure as exc:
            self.halted = True
            # The dispatch may have executed: retain its maximum, fence without
            # retrying dispatch, and report no trusted usage on transport loss.
            try:
                call(self.executor, {'action': 'stop', 'run': run}, timeout=8)
            except Failure:
                self.cessation_unknown.add(run)
            observed = {'error': exc.record, 'transport_complete': False, 'observation': '',
                        'exit_code': None, 'seconds': None, 'assets_unchanged': False,
                        'termination': {'ceased': False}}
        finally:
            timer.cancel()
        with self.lock:
            assertion = observed['transport_complete'] and observed['observation'] == b'CLEAN\n'.hex() and observed['exit_code'] == 0
            gates = {gate: {'state': 'not-run', 'evidence': None} for gate in GATES}
            raw_bytes = bytes.fromhex(observed.pop('raw', ''))
            raw_object = self.ledger.object(raw_bytes)
            observed['raw_digest'] = raw_object
            observed['raw_bytes'] = len(raw_bytes)
            raw_hash = self.ledger.object(canonical(observed))
            for name in ('source_environment_identity', 'isolation'):
                gates[name] = {'state': 'pass' if observed['transport_complete'] else 'error', 'evidence': raw_hash}
            gates['trusted_observation'] = dict(gate(observed), evidence=raw_hash)
            gates['protected_asset_integrity'] = {'state': 'pass' if observed['assets_unchanged'] else 'fail', 'evidence': raw_hash}
            gates['baseline_correctness'] = {'state': 'pass' if assertion else 'fail', 'evidence': raw_hash}
            # Host elapsed includes overlapping time in each independent arm.
            # A timeout, absent receipt or uncertain cessation retains the hold.
            settlement = None
            if observed['transport_complete'] and observed['termination']['ceased']:
                elapsed = (time.monotonic_ns() - dispatch_started + 999) // 1000
                try:
                    meter = self.budget.meter(EVALUATOR, reservation,
                        {'currency': 'USD', 'money_cents': 0, 'execution_us': elapsed, 'review_us': 0}, raw_hash)
                    settlement = self.budget.settle(EVALUATOR, reservation, meter)
                except (Failure, sqlite3.Error, OSError):
                    self.halted = True
            gates['budget_state'] = {'state': 'fail' if self.halted else 'pass', 'evidence': reservation}
            gates['evidence_integrity_currency'] = {'state': 'pass', 'evidence': raw_hash}
            stopped = self.runs[run]['epoch'] != 0
            report = {'run': run, 'candidate': request['variant'], 'challenge': request['challenge'],
                      'arm': 'synthetic-only', 'evaluator': self.identity, 'policy': self.policy_ref,
                      'execution': 'stopped' if stopped else ('completed' if observed['transport_complete'] else 'error'),
                      'assertion': 'pass' if assertion else 'fail',
                      'finding': 'no-synthetic-fault-observed' if assertion else 'synthetic-walkthrough-fault',
                      'verified': False, 'admission': 'blocked', 'decision': 'not-run',
                      'gates': gates, 'objects': [raw_hash, raw_object], 'reservation': reservation,
                      'reserved_seconds': 300, 'reserved_total_seconds': self.reserved,
                      'execution_seconds': observed['seconds'], 'review_seconds': None,
                      'incremental_money_cents': 0, 'epoch': self.runs[run]['epoch'],
                      'budget': self.budget.totals(EVALUATOR), 'settlement': settlement,
                      'usage_status': 'settled' if settlement else 'maximum-retained',
                      'cessation_verified': observed['termination']['ceased'],
                      'next_action': 'Inspect evidence; replay/review/admission unavailable',
                      'scope': 'Not a vlt defect, Verified defect, or admission candidate'}
            if probe or not observed['transport_complete']:
                report['finding'] = 'not-evaluated'
            report['probe'] = probe
            report['isolation_verified'] = observed.get('isolation_verified', False)
            report['observation_error'] = observed['error']
            snapshot = self.event(dict(report, kind='observation'), uuid.uuid4().hex)
            verifySnapshot(snapshot, snapshot['receipt']['digest'])
            report.update(snapshot_id=snapshot['snapshot_id'], anchor=snapshot['receipt']['digest'])
            self.runs[run] = report
            (self.root / (run + '.json')).write_bytes(canonical(snapshot))
            if (probe == 'stop' and stopped and observed['termination']['ceased']
                    and observed['assets_unchanged'] and observed.get('isolation_verified')
                    and observed['error'] and observed['error']['code'] == 'Stopped'):
                self.preflight = True
            return report

    def deadline(self, run: str) -> None:
        self.halted = True
        try:
            self.stop(run, 'watchdog-' + run, EVALUATOR)
        except Failure:
            self.audit(EVALUATOR, 'RecoveryRequired')

    def stop(self, run: str, key: str, uid: int) -> dict:
        with self.lock:
            require(run in self.runs, 'InvalidInput', 'Unknown run')
            if key in self.stops:
                previous, result = self.stops[key]
                require(previous == run, 'StaleBinding', 'Stop key bound to another run')
                return result
            self.runs[run]['epoch'] = 1
            self.event({'kind': 'stop-fenced', 'run': run, 'actor_uid': uid,
                        'epoch': self.runs[run]['epoch'], 'objects': []}, key)
        result = call(self.executor, {'action': 'stop', 'run': run}, timeout=8)
        with self.lock:
            self.event({'kind': 'stop-outcome', 'run': run, 'outcome': result, 'objects': []}, key)
            outcome = dict(result, outcome='stopped' if result['ceased'] else 'recovery-required')
            self.stops[key] = (run, outcome)
        return outcome

    def handle(self, uid: int, request: dict) -> dict:
        try:
            require(uid == self.policy['operator_uid'], 'Unauthorized', 'Operator peer required')
            action = request.get('action')
            if action in DENIED:
                raise Failure('GateBlocked', 'Capability explicitly denied: ' + action)
            if action in ('start', 'preflight', 'probe-output', 'probe-deadline'):
                probe = {'start': None, 'preflight': 'stop', 'probe-output': 'output', 'probe-deadline': 'deadline'}[action]
                return self.start(request, uid, probe)
            if action == 'list':
                fields(request, {'action'})
                return {'runs': list(self.runs), 'policy': self.policy_ref, 'preflight': self.preflight}
            fields(request, {'action', 'run'}, {'key', 'reason', 'target', 'decision', 'plan', 'execute'})
            run = identifier(request['run'])
            if action == 'stop':
                identifier(request.get('key', run))
                require(len(request.get('reason', '')) <= 200 and '\n' not in request.get('reason', ''),
                        'InvalidInput', 'Stop reason must be bounded single-line text')
                return self.stop(run, request.get('key', run), uid)
            require(run in self.runs, 'InvalidInput', 'Unknown run')
            if action in ('decide', 'recover', 'review'):
                raise Failure('GateBlocked', 'Review, decisions, admission and recovery are not-run/unavailable')
            if action == 'status':
                with self.lock:
                    status = dict(self.runs[run])
                if status['execution'] == 'running':
                    status['executor'] = call(self.executor, {'action': 'status', 'run': run}, timeout=2)
                return status
            if action == 'evidence':
                import json
                snapshot = json.loads((self.root / (run + '.json')).read_bytes())
                return verifySnapshot(snapshot, self.runs[run]['anchor'])
            raise Failure('InvalidInput', 'Unknown action')
        except Failure as exc:
            if not self.halted:
                self.audit(uid, exc.record['code'])
            raise


if __name__ == '__main__':
    import sys
    root = Path(sys.argv[1]).resolve()
    try:
        evaluator = Evaluator(root)
        serve(root.parent / 'ipc/evaluator.sock', evaluator.handle)
    except Failure as exc:
        print(canonical({'error': exc.record}).decode(), flush=True)
        raise SystemExit(3)
