"""UID-320 evaluator for real disposable corpus fixture observations."""
import base64
import math
import os
from pathlib import Path
import time
import uuid

from budget import Budget
from common import EVALUATOR, Failure, call, canonical, digest, fields, require
from corpus_execution import (HELPER, IMAGE, PROFILE, SUPERVISOR, QEMU_MANIFEST, decode_guest,
                              validate_config)
from ledger import Ledger
from trusted_execution import root_record


def validate_receipt(value: dict, request: dict, execution_profile: str) -> dict:
    return _validate_receipt(value, request, execution_profile,
                             {'profile': PROFILE, 'image': IMAGE, 'supervisor': SUPERVISOR, 'helper': HELPER})


def _validate_receipt(value: dict, request: dict, execution_profile: str, identity: dict) -> dict:
    """Shared parser; public protocol entrypoints supply compiled artifact pins."""
    fields(value, {'version', 'run', 'key', 'reservation', 'guest', 'error', 'transport_complete',
                   'ceased', 'forced', 'seconds', 'raw_sha256', 'raw_bytes', 'raw_base64', 'exit_code',
                   'profile', 'image', 'supervisor', 'helper', 'execution_profile', 'qemu_installation'})
    require(value['version'] == 1 and all(value[key] == request[key] for key in ('run', 'key', 'reservation'))
            and all(value[key] == hashed for key, hashed in identity.items())
            and value['execution_profile'] == execution_profile
            and value['qemu_installation'] == QEMU_MANIFEST,
            'StaleBinding', 'Corpus receipt binding differs')
    require(all(type(value[key]) is bool for key in ('ceased', 'forced', 'transport_complete'))
            and value['ceased'] and not value['forced'] and type(value['seconds']) in (int, float)
            and math.isfinite(value['seconds']) and 0 < value['seconds'] <= 480,
            'BudgetUnknown', 'Cessation or duration not proven')
    raw = base64.b64decode(value['raw_base64'], validate=True)
    require(len(raw) == value['raw_bytes'] <= 1048576 and digest(raw) == value['raw_sha256'],
            'IntegrityFailure', 'Raw transport binding differs')
    require(value['transport_complete'] and value['error'] is None and value['exit_code'] == 0,
            'BudgetUnknown', 'Incomplete corpus observation')
    decode_guest(canonical(value['guest']), request['run'], request['challenge'])
    return value


def verdict(guest: dict, truth: dict) -> dict:
    observation = guest['candidate_observation']; repetitions = observation['repetitions']
    exits = [item['exit'] for item in repetitions]; hashes = [item['output_sha256'] for item in repetitions]
    deterministic = len(set(exits)) == 1 and len(set(hashes)) == 1
    passed = observation['build_exit'] == 0 and exits == [0, 0, 0]
    faulty = (observation['build_exit'] != 0 or exits[0] != 0) and deterministic
    expected = 'clean' if truth['truth'] == 'clean' else 'defect'
    actual = 'clean' if passed else 'defect' if faulty else 'ambiguous'
    return {'fixture_validation': 'pass' if actual == expected and deterministic else 'fail',
            'expected': expected, 'observed': actual, 'deterministic': deterministic,
            'repetitions': exits, 'independent_replay': 'not-run', 'reviewer_outcome': 'not-run',
            'verified': False, 'admission': 'blocked'}


class CorpusSession:
    def __init__(self, root: Path):
        require(os.getuid() == EVALUATOR, 'Unauthorized', 'Actual evaluator UID 320 required')
        self.root = root
        self.endpoint = root.parent/'ipc/executor.sock'; self.control = root.parent/'ipc/executor-control.sock'
        self.config = validate_config(root_record(root.parent/'runner/config.json'))
        self.budget = Budget(root/'budget.sqlite')
        self.ledger = Ledger(root/'ledger')
        self.truth = {item['challenge']: item for item in self._json(root/'corpus/truth.json')}
        manifest = self._json(root/'corpus/manifest.json')
        require(manifest['freeze_digest'] == self.config['corpus_binding'] and set(self.truth) == set(manifest['challenge_ids']),
                'StaleBinding', 'Protected corpus projection differs')
        self.pending = {}

    @staticmethod
    def _json(path: Path):
        value = __import__('json').loads(path.read_bytes()); require(isinstance(value, (dict, list)), 'InvalidInput', 'Malformed corpus record')
        return value

    def record(self, event: dict) -> None:
        try: self.ledger.append(EVALUATOR, event, self.ledger.tip(), uuid.uuid4().hex)
        except Exception:
            self.budget.halt(); raise Failure('RecoveryRequired', 'Evidence persistence failed')

    def prepare(self, challenge: str) -> dict:
        run = uuid.uuid4().hex
        request = {'action': 'dispatch', 'version': 1, 'run': run, 'arm': 'validated-corpus',
                   'challenge': challenge, 'variant': challenge, 'key': uuid.uuid4().hex,
                   'reservation': 'unreserved', 'epoch': 0, 'probe': None}
        maximum = {'currency': 'USD', 'money_cents': 0, 'execution_us': 480000000, 'review_us': 0}
        reserved = self.budget.reserve(EVALUATOR, run, maximum, request['key'],
                                        binding=digest(canonical(request)))
        request['reservation'] = reserved['id']; self.record({'kind': 'corpus-reserved', 'request': request,
                                                              'maximum': maximum, 'verified': False})
        self.pending[run] = (request, time.monotonic()); return request

    def accept(self, request: dict, result: dict) -> dict:
        require(request['run'] in self.pending, 'StaleBinding', 'Unknown corpus invocation')
        seconds = max(result['seconds'], time.monotonic()-self.pending[request['run']][1])
        usage = {'currency': 'USD', 'money_cents': 0, 'execution_us': math.ceil(seconds*1000000), 'review_us': 0}
        hashed = self.ledger.object(canonical(result))
        self.record({'kind': 'corpus-raw-receipt', 'objects': [hashed], 'run': request['run'],
                     'challenge': request['challenge'], 'validated': False})
        try:
            validate_receipt(result, request, self.config['execution_profile'])
        except Failure as exc:
            self.record({'kind': 'corpus-validation-failed', 'run': request['run'],
                         'challenge': request['challenge'], 'objects': [hashed], 'error': exc.record,
                         'reservation': 'held'})
            raise
        self.record({'kind': 'corpus-receipt', 'objects': [hashed], 'run': request['run'],
                     'challenge': request['challenge']})
        meter = self.budget.meter(EVALUATOR, request['reservation'], usage, hashed)
        self.budget.settle(EVALUATOR, request['reservation'], meter)
        decision = verdict(result['guest'], self.truth[request['challenge']])
        self.record({'kind': 'corpus-gate', 'run': request['run'], 'challenge': request['challenge'],
                     'decision': decision})
        return decision

    def execute(self, challenge: str) -> tuple[dict, dict]:
        request = self.prepare(challenge)
        try:
            result = call(self.endpoint, request); return result, self.accept(request, result)
        except Failure as exc:
            self.record({'kind': 'corpus-failed', 'run': request['run'], 'challenge': challenge,
                         'error': exc.record, 'admission': 'blocked', 'reservation': 'held'})
            raise
