"""Dedicated evaluator path. Raw candidate data never supplies expectations."""
import base64
import math
import os
from pathlib import Path
import time
import uuid
from persistent_budget import PersistentBudget
from common import EVALUATOR, Failure, call, canonical, digest, fields, require
from ledger import Ledger
from trusted_execution import PROFILE, IMAGE, SUPERVISOR, decode_guest, root_record, validate_config

EXPECTED = b'SUPERVISOR-OWNED-CONTENT\n'


def validate_receipt(value: dict, request: dict, execution_profile: str, installation: str) -> dict:
    fields(value, {'version', 'run', 'key', 'reservation', 'guest', 'error', 'transport_complete',
                   'ceased', 'forced', 'seconds', 'raw_sha256', 'raw_bytes', 'raw_base64',
                   'exit_code', 'profile', 'image', 'supervisor', 'execution_profile', 'qemu_installation'})
    require(type(value['version']) is int and value['version'] == 1
            and all(value[k] == request[k] for k in ('run', 'key', 'reservation'))
            and value['profile'] == PROFILE and value['image'] == IMAGE and value['supervisor'] == SUPERVISOR
            and value['execution_profile'] == execution_profile and value['qemu_installation'] == installation,
            'StaleBinding', 'Receipt binding differs')
    require(all(type(value[k]) is bool for k in ('ceased', 'forced', 'transport_complete'))
            and value['ceased'] and type(value['seconds']) in (float, int)
            and math.isfinite(value['seconds']) and 0 < value['seconds'] <= 300,
            'BudgetUnknown', 'Cessation or elapsed cost not proven')
    require(isinstance(value['raw_base64'], str) and len(value['raw_base64']) <= 1398104,
            'InvalidInput', 'Unbounded raw transport')
    try:
        raw = base64.b64decode(value['raw_base64'], validate=True)
    except ValueError as exc:
        raise Failure('InvalidInput', 'Malformed raw transport') from exc
    require(type(value['raw_bytes']) is int and len(raw) == value['raw_bytes'] <= 1048576
            and digest(raw) == value['raw_sha256'], 'IntegrityFailure', 'Raw transport binding differs')
    # Only complete structured results may reduce an outstanding reservation.
    require(value['transport_complete'] and value['error'] is None
            and type(value['exit_code']) is int and value['exit_code'] == 0,
            'BudgetUnknown', 'Incomplete observation; worst-case reservation retained')
    decode_guest(canonical(value['guest']), request['run'], request['variant'])
    return value


def verdict(guest: dict, expected: bytes) -> dict:
    """Control success is not correctness, replay, review, or admission."""
    note = base64.b64decode(guest['observed_note'] or '', validate=True)
    correct = (guest['variant'] == 'clean' and guest['candidate_exit_success']
               and guest['candidate_cessation'] and not guest['output_exceeded']
               and guest['kernel_lock_held_by_supervisor'] and guest['note_absent_during_hold']
               and guest['note_regular'] and note == expected)
    return {'trusted_observation': 'pass', 'baseline_correctness': 'pass' if correct else 'fail',
            'independent_replay': 'not-run', 'reviewer_outcome': 'not-run',
            'verified': False, 'admission': 'blocked'}


class Session:
    def __init__(self, root: Path) -> None:
        require(os.getuid() == EVALUATOR, 'Unauthorized', 'Actual evaluator UID 320 required')
        self.root = root
        self.endpoint = root.parent / 'ipc/executor.sock'
        self.control = root.parent / 'ipc/executor-control.sock'
        self.config = validate_config(root_record(root.parent / 'runner/config.json'))
        self.expected = (root / 'expectation').read_bytes()
        require(self.expected == EXPECTED, 'IntegrityFailure', 'Protected expectation differs')
        self.budget = PersistentBudget('trusted-observation')
        require(self.budget.binding_hash == self.config['accounting_binding'],
                'RecoveryRequired', 'Persistent accounting approval differs')
        self.ledger = Ledger(root)
        self.pending = {}

    def record(self, event: dict) -> None:
        try:
            self.ledger.append(EVALUATOR, event, self.ledger.tip(), uuid.uuid4().hex)
        except Exception:
            self.budget.halt()
            raise Failure('RecoveryRequired', 'Evidence persistence failed; no new effects')

    def prepare(self, variant='clean', probe=None) -> dict:
        run = uuid.uuid4().hex
        request = {'action': 'dispatch', 'version': 1, 'run': run, 'arm': 'trusted-control',
                   'challenge': 'vlt-lock-observation-001', 'variant': variant,
                   'key': uuid.uuid4().hex, 'reservation': 'unreserved', 'epoch': 0, 'probe': probe}
        maximum = {'currency': 'USD', 'money_cents': 0, 'execution_us': 300000000, 'review_us': 0}
        reserved = self.budget.reserve(EVALUATOR, run, maximum, request['key'],
                                       binding=digest(canonical(request)))
        request['reservation'] = reserved['id']
        self.record({'kind': 'reserved-before-dispatch', 'request': request, 'maximum': maximum,
                     'dispatch_lease': False, 'verified': False})
        self.pending[run] = (request, time.monotonic())
        return request

    def accept(self, request: dict, result: dict) -> dict:
        require(request['run'] in self.pending, 'StaleBinding', 'Unknown evaluator invocation')
        try:
            validate_receipt(result, request, self.config['execution_profile'], self.config['qemu_installation'])
            # Charge the larger measurement. Overhead or delayed receipt is never
            # subtracted from execution or treated as free; >maximum fails closed.
            seconds = max(result['seconds'], time.monotonic() - self.pending[request['run']][1])
            usage = {'currency': 'USD', 'money_cents': 0,
                     'execution_us': math.ceil(seconds * 1000000), 'review_us': 0}
            hashed = self.ledger.object(canonical(result))
            self.record({'kind': 'trusted-receipt', 'objects': [hashed], 'run': request['run']})
            meter = self.budget.meter(EVALUATOR, request['reservation'], usage, hashed)
            self.budget.settle(EVALUATOR, request['reservation'], meter)
            decision = verdict(result['guest'], self.expected)
            self.record({'kind': 'gate', 'run': request['run'], 'decision': decision})
            return decision
        except Failure as exc:
            self.record({'kind': 'gate', 'run': request['run'], 'trusted_observation': 'fail',
                         'admission': 'blocked', 'reservation': 'held', 'error': exc.record})
            raise

    def execute(self, variant='clean', probe=None) -> tuple[dict, dict]:
        request = self.prepare(variant, probe)
        try:
            result = call(self.endpoint, request)
            return result, self.accept(request, result)
        except Failure as exc:
            self.record({'kind': 'execution-failed', 'run': request['run'], 'error': exc.record,
                         'trusted_observation': 'fail', 'admission': 'blocked', 'reservation': 'held'})
            raise
