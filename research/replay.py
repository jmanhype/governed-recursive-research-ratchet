"""Independent replay evidence contracts; no claimant output is a gate verdict.

The corpus's specification_digest is a reference label, not a content hash.
This module resolves explicit maintainer assertions from the pinned archive.
Decision helpers are pure; only the dedicated evaluator may issue receipts.
"""
import io
import fcntl
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import tarfile
import threading
import time
import uuid
from typing import Optional

from common import EVALUATOR, RUNNER, GATES, Failure, call, canonical, digest, fields, identifier, require
from persistent_budget import PersistentBudget, PROFILES as ACCOUNTING_PROFILES
from ledger import Ledger, export_snapshot
from corpus_execution import CorpusExecutor, SUPERVISOR, HELPER, validate_request
import replay_profile
from replay_profile import PROFILE, IMAGE, RECEIPT, validate_receipt
from replay_fixtures import CLEAN, SEEDED, REBUILD, INTERRUPTION, seeds as replay_seeds
from replay_prerequisites import REPLAY_ROOT, POLICY_SHA256, inspect_corpus, validate_policy
from replay_smoke import require_identity
from trusted_execution import protected_bytes, root_record
from trusted_transport import AuthenticatedServer, control_call
from validated_corpus import SOURCE_ARCHIVE, SOURCE_COMMIT

SPEC_MEMBER = 'wikilinks_test.go'
SPEC_SHA256 = '218eebc6314ce14c555c579db24b85ccc4ccb425e3cd51f93d1c52a9049da570'
SPEC_CASE = 'TestParseWikilinks/link with display text'
CHALLENGE = 'GRRR-VC-D011'
FINDINGS = ('Verified defect', 'Not reproduced', 'Specification ambiguity',
            'Inconclusive', 'Invalid claim')
INPUTS = Path('/Library/GRRR/replay-inputs')
BASELINE = CLEAN
MODES = {'normal': (SEEDED,), 'failed-rebuild': (REBUILD,),
         'interruption': (INTERRUPTION,), 'two-failures': (SEEDED, CLEAN, CLEAN)}


def scope(mode: str) -> dict:
    require(mode in MODES, 'GateBlocked', 'Unregistered replay mode')
    return {'scope': 'D011-independent-replay-v2', 'mode': mode, 'challenge': CHALLENGE,
            'baseline': BASELINE, 'candidates': list(MODES[mode]), 'profile': PROFILE,
            'maximum_guest_launches': 2 * len(MODES[mode]), 'work_seconds': 473,
            'total_seconds': 480, 'interrupt_after_command_seconds': 60,
            'contract_admission_authorized': False}


def runtime(mode: str) -> Path:
    scope(mode)
    return REPLAY_ROOT / ('d011-independent-v2-' + mode)


SCOPE = scope('normal')
ROOT = runtime('normal')


def validate_scope(value: dict, mode: str = 'normal') -> dict:
    require(canonical(value) == canonical(scope(mode)), 'GateBlocked', 'Unapproved independent replay scope')
    return value


def preflight() -> None:
    """Never inherit the lifecycle smoke's deliberately separate allowance."""
    require('independent-replay' in ACCOUNTING_PROFILES, 'GateBlocked',
            'Cumulative campaign accounting has no registered independent-replay profile; '
            'reviewed migration is required, never initialize a fresh replay allowance')


def scope_event(kind: str, **values: object) -> dict:
    """Shared parent lifecycle evidence remains distinct from evaluator verdicts."""
    require(kind in ('runtime-smoke-parent-lifecycle', 'runtime-smoke-complete'),
            'InvalidInput', 'Unregistered parent replay event')
    return dict(SCOPE, kind=kind.replace('runtime-smoke', 'independent-replay-parent'), **values)


class ParentProtocol:
    """Selected only by the reviewed launcher's exact fixed mode grammar."""
    def __init__(self, mode: str) -> None:
        self.mode, self.ROOT, self.SCOPE = mode, runtime(mode), scope(mode)
        self.role_prefix = 'replay-' + mode

    def validate_scope(self, value: dict) -> dict:
        return validate_scope(value, self.mode)

    def preflight(self) -> None:
        preflight()
        replay_profile.validate_inputs()

    def configure(self, config: dict) -> dict:
        return replay_profile.configure(config)

    def scope_event(self, kind: str, **values: object) -> dict:
        require(not set(values).intersection(set(self.SCOPE) | {'kind'}),
                'InvalidInput', 'Parent scope cannot be overridden')
        require(kind in ('runtime-smoke-parent-lifecycle', 'runtime-smoke-complete'),
                'InvalidInput', 'Unknown parent event')
        return dict(self.SCOPE, kind=kind.replace('runtime-smoke', 'independent-replay-parent'), **values)


def read_plan(mode: str = 'normal') -> dict:
    plan = root_record(runtime(mode) / 'plan.json')
    fields(plan, {'run', 'scope', 'policy_sha256'})
    identifier(plan['run'])
    validate_scope(plan['scope'], mode)
    require(plan['policy_sha256'] == POLICY_SHA256, 'StaleBinding', 'Policy binding differs')
    return plan


class ReplayExecutor(CorpusExecutor):
    """Fresh accepted offline guest per invocation; never reuse the smoke run."""
    def __init__(self, mode: str = 'normal') -> None:
        require_identity(RUNNER)
        self.mode, self.runtime = mode, runtime(mode)
        self.interruptions = {}
        self.plan = read_plan(mode)
        self.policy = validate_policy(protected_bytes(self.runtime / 'policy.json', POLICY_SHA256))
        super().__init__(self.runtime / 'runner')

    def validate_inputs(self) -> dict:
        return replay_profile.validate_inputs()

    def validate_configuration(self, value: dict) -> dict:
        return replay_profile.validate_config(value)

    def input_image(self) -> Path:
        return replay_profile.ROOT / 'input.iso'

    def artifact_identity(self) -> dict:
        return replay_profile.identity()

    def command_watchdog(self, run: str, challenge: str) -> object:
        if challenge != INTERRUPTION:
            return None
        seconds = scope(self.mode)['interrupt_after_command_seconds']
        def interrupt() -> None:
            with self.lock:
                self.interruptions[run] = {'kind': 'fixed-replay-command-interruption', 'bound_seconds': seconds}
                self.stop(run)
        timer = threading.Timer(seconds, interrupt)
        timer.start()
        return timer

    def finalize_result(self, run: str, result: dict) -> dict:
        result = super().finalize_result(run, result)
        with self.lock:
            if run in self.interruptions:
                result = dict(result, interruption=self.interruptions[run])
        return result

    def handle(self, uid: int, message: dict) -> dict:
        require(uid == EVALUATOR, 'Unauthorized', 'Authenticated evaluator required')
        if message.get('action') == 'dispatch':
            validate_request(message)
            require(message['challenge'] in (BASELINE, *MODES[self.mode])
                    and message['run'].startswith(self.plan['run'] + '-'),
                    'GateBlocked', 'Only fixed replay run and challenges permitted')
            with self.lock:
                require(self.launches < scope(self.mode)['maximum_guest_launches'],
                        'BudgetExceeded', 'Reviewed guest count exhausted')
        return super().handle(uid, message)

    def spawn_guest(self, args: list) -> subprocess.Popen:
        require_identity(RUNNER)
        require(shutil.disk_usage(self.runtime).free >= self.policy['limits']['minimum_host_free_bytes'],
                'BudgetExceeded', 'Approved disk floor unavailable')
        return subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, cwd=self.root / 'scratch',
                                env={'PATH': '/usr/bin:/bin', 'HOME': '/var/empty', 'LC_ALL': 'C'},
                                start_new_session=False)


def runner(mode: str = 'normal') -> int:
    require_identity(RUNNER)
    executor = ReplayExecutor(mode)
    data = AuthenticatedServer(runtime(mode) / 'ipc/executor.sock', executor.handle)
    control = AuthenticatedServer(runtime(mode) / 'ipc/executor-control.sock', executor.handle, control=True)
    try:
        threading.Event().wait()
    finally:
        data.close()
        control.close()
    return 0


def maintainer_specification(archive: bytes, challenge: str) -> dict:
    """Read, never extract/execute, the exact upstream table case and assertion."""
    require(len(archive) == 716800 and digest(archive) == SOURCE_ARCHIVE,
            'IntegrityFailure', 'Pinned source archive differs')
    identifier(challenge)
    if challenge != CHALLENGE:
        return {'status': 'not-run', 'reason': 'No reviewed direct maintainer mapping',
                'source_commit': SOURCE_COMMIT, 'archive_sha256': SOURCE_ARCHIVE}
    with tarfile.open(fileobj=io.BytesIO(archive), mode='r:') as source:
        members = [member for member in source.getmembers() if member.name == SPEC_MEMBER]
        require(len(members) == 1 and members[0].isfile() and members[0].size <= 262144,
                'IntegrityFailure', 'Maintainer specification member differs')
        stream = source.extractfile(members[0])
        require(stream is not None, 'IntegrityFailure', 'Maintainer specification unavailable')
        with stream:
            raw = stream.read(262145)
    require(digest(raw) == SPEC_SHA256, 'IntegrityFailure', 'Maintainer test bytes differ')
    # Full-file pin protects both the table and its assertion loop; these anchors
    # make the exact semantic correspondence explicit rather than filename-only.
    assertions = (b'func TestParseWikilinks(t *testing.T)', b'name: "link with display text"',
                  b'text: "The [[Sr PM Agent|PM]] handles this."',
                  b'{Title: "Sr PM Agent", Display: "PM", Raw: "[[Sr PM Agent|PM]]"}',
                  b'if g.Display != want.Display {')
    require(all(raw.count(anchor) == 1 for anchor in assertions),
            'IntegrityFailure', 'Direct maintainer assertion changed')
    return {'status': 'pass', 'source_commit': SOURCE_COMMIT,
            'archive_sha256': SOURCE_ARCHIVE, 'member': SPEC_MEMBER,
            'member_sha256': SPEC_SHA256, 'case': SPEC_CASE,
            'expected_behavior': 'Wikilink display text is captured.',
            'correspondence': 'The upstream table expects Display PM and its loop compares '
                              'g.Display with want.Display; D011 removes display capture.'}


def observation_outcome(observation: dict) -> str:
    """Classify a decoded observation, not execution completion or fixture truth."""
    fields(observation, {'version', 'challenge', 'test', 'build_exit',
                         'build_output_sha256', 'repetitions', 'internal_error'}, {'build_output'})
    require(type(observation['build_exit']) is int and observation['build_exit'] in (0, 1, 2)
            and type(observation['internal_error']) is bool, 'InvalidInput', 'Invalid build outcome')
    repetitions = observation['repetitions']
    require(isinstance(repetitions, list) and len(repetitions) == 3,
            'InvalidInput', 'Three observations required')
    exits, hashes = [], []
    for item in repetitions:
        fields(item, {'exit', 'output_sha256'})
        require(type(item['exit']) is int and 0 <= item['exit'] <= 2,
                'InvalidInput', 'Invalid probe exit')
        exits.append(item['exit'])
        hashes.append(identifier(item['output_sha256'], True))
    if observation['internal_error'] or observation['build_exit'] != 0:
        return 'inconclusive'  # A failed rebuild is never a reproduced defect.
    if len(set(hashes)) != 1 or len(set(exits)) != 1:
        return 'inconclusive'
    return 'clean' if exits == [0, 0, 0] else 'failure'


def finding(outcome: str, specification: dict, baseline: str) -> str:
    """Pure decision rule; calling this cannot issue a trusted ReplayReceipt."""
    require(outcome in ('clean', 'failure', 'inconclusive')
            and baseline in ('clean', 'failure', 'inconclusive'),
            'InvalidInput', 'Unknown observation outcome')
    if baseline != 'clean' or outcome == 'inconclusive':
        return 'Inconclusive'
    if outcome == 'clean':
        return 'Not reproduced'
    if specification.get('status') != 'pass':
        return 'Specification ambiguity'
    require(specification.get('member_sha256') == SPEC_SHA256
            and specification.get('archive_sha256') == SOURCE_ARCHIVE
            and specification.get('case') == SPEC_CASE,
            'IntegrityFailure', 'Unsupported specification confirmation')
    return 'Verified defect'


def gate_inventory() -> dict:
    """All gates start not-run; missing work can never silently become a pass."""
    return {name: {'status': 'not-run', 'evidence': []} for name in GATES}


def failure_transition(previous: int, reproduced: bool, approved_threshold: Optional[int]) -> dict:
    """Pure proposed state transition, persisted atomically by the evaluator."""
    require(type(previous) is int and previous >= 0 and type(reproduced) is bool,
            'InvalidInput', 'Invalid consecutive failure state')
    require(type(approved_threshold) is int and approved_threshold == 2,
            'GateBlocked', 'Exact two-failure policy must be approved before execution')
    require(previous < approved_threshold, 'Stopped', 'Run already stopped')
    count = 0 if reproduced else previous + 1
    return {'consecutive_failures': count, 'stopped': count >= approved_threshold,
            'retain_previous_evidence': True, 'release_unknown_reservations': False}


def candidate_identity(archive: bytes, seed: dict) -> str:
    """Reconstruct source identities in memory from trusted bytes, never build on host."""
    require(digest(archive) == SOURCE_ARCHIVE, 'IntegrityFailure', 'Source archive differs')
    expected = {'anchor': 'if len(m) > 4 {', 'challenge': CHALLENGE, 'file': 'wikilinks.go',
                'kind': 'single-unique-replacement', 'replacement': 'if false {'}
    require(seed == expected, 'StaleBinding', 'Reviewed D011 seed differs')
    return _source_identity(archive, seed)


def _source_identity(archive: bytes, seed: dict) -> str:
    """Internal byte reconstruction from one of the compiled replay seeds."""
    require(digest(archive) == SOURCE_ARCHIVE, 'IntegrityFailure', 'Source archive differs')
    files = {}
    with tarfile.open(fileobj=io.BytesIO(archive), mode='r:') as source:
        for member in source.getmembers():
            path = Path(member.name)
            require(member.isfile() and not path.is_absolute() and '..' not in path.parts
                    and member.name not in files and member.size <= 1048576,
                    'IntegrityFailure', 'Unsafe source archive member')
            with source.extractfile(member) as stream:
                raw = stream.read(1048577)
            if member.name == seed['file']:
                anchor = seed['anchor'].encode()
                require(raw.count(anchor) == 1, 'IntegrityFailure', 'Seed anchor differs')
                raw = raw.replace(anchor, seed['replacement'].encode(), 1)
            files[member.name] = digest(raw)
    require(seed['file'] in files or seed['kind'] == 'clean-control', 'IntegrityFailure', 'Seed source absent')
    return digest(canonical(files))


class ReplaySession:
    """UID-320-only transactional replay. Root-reviewed scope is the request.

    Root's lock and process-group watchdog cover the entire session. A second
    evaluator cannot race this one, even using an independent SQLite connection.
    Pending attempts after crash are not resumed or given new dispatch keys.
    """
    def __init__(self, mode: str = 'normal') -> None:
        require_identity(EVALUATOR)
        preflight()
        self.mode, self.runtime = mode, runtime(mode)
        self.started = time.monotonic()
        self.plan = read_plan(mode)
        self.home = self.runtime / 'evaluator'
        require(self.home.stat().st_uid == EVALUATOR and self.home.stat().st_mode & 0o077 == 0,
                'Unauthorized', 'Replay state must be private evaluator storage')
        self.lock = os.open(self.home / 'session.lock', os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
        try:
            fcntl.flock(self.lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            os.close(self.lock)
            raise Failure('RecoveryRequired', 'Another evaluator owns this replay')
        self.budget = PersistentBudget('independent-replay')
        self.ledger = Ledger(self.home / 'replay-ledger')
        self.policy = validate_policy((self.home / 'policy.json').read_bytes())
        self.threshold = self.policy['stop_after_consecutive_independent_replay_failures']
        failure_transition(0, True, self.threshold)
        self.config = replay_profile.validate_config(root_record(self.runtime / 'runner/config.json'))
        self.identities = inspect_corpus(INPUTS / 'corpus', protected=True)
        archive = protected_bytes(INPUTS / 'source.tar', SOURCE_ARCHIVE)
        manifest = root_record(INPUTS / 'corpus/manifest.json')
        seeds = json.loads(protected_bytes(INPUTS / 'corpus/protected/seeds.json',
                                          manifest['artifacts']['protected/seeds.json']))
        seed = next(item for item in seeds if item['challenge'] == CHALLENGE)
        self.specification = maintainer_specification(archive, CHALLENGE)
        preparation = json.loads(protected_bytes(replay_profile.ROOT / 'preparation.json', RECEIPT))
        self.toolchain = preparation['primary_iso_readback']['go.tgz']['sha256']
        identifier(self.toolchain, True)
        self.allegation = {'challenge': CHALLENGE, 'source': SOURCE_ARCHIVE,
                          'candidate': candidate_identity(archive, seed),
                          'evaluator': self.config['host_code'], 'policy': POLICY_SHA256,
                          'seed': digest(canonical(seed))}
        self.reference = digest(canonical(self.allegation))
        self.source_reconstructions = {item['challenge']: _source_identity(archive, item) for item in replay_seeds()}
        self.ledger.db.execute('CREATE TABLE IF NOT EXISTS replay_state('
                               'run TEXT PRIMARY KEY, failures INTEGER NOT NULL, '
                               'stopped INTEGER NOT NULL, pending TEXT)')
        self.ledger.db.execute('INSERT OR IGNORE INTO replay_state VALUES(?,0,0,NULL)', (self.plan['run'],))
        require(self.state()[2] is None, 'RecoveryRequired', 'Unfinished attempt requires inspection')
        self.record({'kind': 'replay-allegation-requested', 'allegation': self.allegation,
                     'reference': self.reference, 'request_scope': self.plan['scope']})

    def state(self) -> tuple:
        return self.ledger.db.execute('SELECT failures,stopped,pending FROM replay_state WHERE run=?',
                                      (self.plan['run'],)).fetchone()

    def record(self, value: dict) -> dict:
        try:
            return self.ledger.append(EVALUATOR, value, self.ledger.tip(), uuid.uuid4().hex)
        except Exception:
            self.budget.halt()
            raise

    def reserve(self) -> dict:
        require(not self.state()[1] and self.state()[2] is None, 'Stopped', 'Replay run stopped or pending')
        return self.budget.reserve(EVALUATOR, self.plan['run'],
                                  {'currency': 'USD', 'money_cents': 0,
                                   'execution_us': 480000000, 'review_us': 0}, uuid.uuid4().hex,
                                  binding=self.reference)

    def reproduce(self, principal: int, allegation: str, policy: str, reservation: str) -> dict:
        """Execute trusted baseline and seed in different new offline VMs.

        Principal is the operator in the immutable parent execution profile, not
        a challenger payload role. This method is not an unauthenticated endpoint.
        """
        require_identity(EVALUATOR)
        require(type(principal) is int and principal == self.config['operator_uid'],
                'Unauthorized', 'Reviewed operator request required')
        if allegation != self.reference or policy != POLICY_SHA256:
            gates = gate_inventory()
            gates['source_environment_identity'] = {'status': 'fail', 'evidence': [self.reference]}
            rejected = {'type': 'ReplayReceipt', 'version': 1, 'run': self.plan['run'],
                        'attempt': uuid.uuid4().hex, 'finding': 'Invalid claim', 'gates': gates,
                        'execution_complete': False, 'verified': False, 'admission': 'blocked',
                        'promotion': 'disabled', 'reservation_state': 'unchanged'}
            hashed = self.ledger.object(canonical(rejected))
            self.record({'kind': 'replay-invalid-claim', 'objects': [hashed]})
            error = Failure('StaleBinding', 'Allegation/evaluator/policy binding differs')
            error.record['receipt'] = hashed
            raise error
        identifier(reservation)
        previous, stopped, pending = self.state()
        require(not stopped and pending is None, 'Stopped', 'Run stopped or has an unresolved attempt')
        row = self.budget.db.execute('SELECT run,binding,actual FROM reservations WHERE id=?',
                                     (reservation,)).fetchone()
        require(row is not None and row[0] == self.plan['run'] and row[2] is None
                and json.loads(row[1])['binding'] == digest(canonical(
                    {'profile': 'independent-replay', 'request_binding': self.reference})),
                'BudgetUnknown', 'Fresh allegation-bound reservation required')
        attempt = uuid.uuid4().hex
        def mark_pending(db: object, receipt: dict) -> None:
            db.execute('UPDATE replay_state SET pending=? WHERE run=?', (attempt, self.plan['run']))
        self.ledger.append_atomic(EVALUATOR, {'kind': 'replay-started', 'attempt': attempt,
                                  'reservation': reservation, 'allegation': self.reference},
                                  self.ledger.tip(), attempt, mark_pending)
        gates = gate_inventory()
        evidence = self.ledger.object(canonical(self.allegation))
        self.record({'kind': 'replay-inputs', 'objects': [evidence]})
        gates['source_environment_identity'] = {'status': 'pass', 'evidence': [evidence]}
        started = time.monotonic()
        observations, runs = [], []
        error, decision, completed = None, 'Inconclusive', False
        try:
            attempt_index = sum(json.loads(row[0]).get('kind') == 'independent-replay-receipt'
                                for row in self.ledger.db.execute('SELECT body FROM events'))
            require(attempt_index < len(MODES[self.mode]), 'Stopped', 'Fixed attempt sequence exhausted')
            for challenge in (BASELINE, MODES[self.mode][attempt_index]):
                request = {'action': 'dispatch', 'version': 1,
                           'run': self.plan['run'] + '-' + uuid.uuid4().hex[:16],
                           'arm': 'validated-corpus', 'challenge': challenge, 'variant': challenge,
                           'key': uuid.uuid4().hex, 'reservation': reservation, 'epoch': 0, 'probe': None}
                runs.append(request['run'])
                remaining = 465 - (time.monotonic() - self.started)
                require(remaining > 0, 'Stopped', 'Replay evaluator work bound exhausted')
                result = call(self.runtime / 'ipc/executor.sock', request, timeout=remaining)
                raw = self.ledger.object(canonical(result))
                self.record({'kind': 'replay-raw-observation', 'request': request, 'objects': [raw]})
                validate_receipt(result, request, self.config['execution_profile'])
                observations.append((raw, observation_outcome(result['guest']['candidate_observation'])))
                for gate in ('isolation', 'protected_asset_integrity', 'trusted_observation'):
                    gates[gate] = {'status': 'pass', 'evidence': [item[0] for item in observations]}
            completed = True
            baseline, candidate = observations[0][1], observations[1][1]
            spec = self.ledger.object(canonical(self.specification))
            self.record({'kind': 'replay-specification', 'objects': [spec]})
            gates['baseline_correctness'] = {'status': 'pass' if baseline == 'clean' else 'fail',
                                            'evidence': [observations[0][0]]}
            gates['specification_traceability'] = {'status': self.specification['status'], 'evidence': [spec]}
            gates['independent_replay'] = {'status': 'pass' if candidate == 'failure' else 'fail',
                                          'evidence': [observations[1][0]]}
            decision = finding(candidate, self.specification, baseline)
            # This checks known cessation/ack separately from a successful probe.
            for run in runs:
                acknowledgement = control_call(self.runtime / 'ipc/executor-control.sock',
                                              {'action': 'stop', 'run': run}, expected_uid=RUNNER, timeout=2)
                require(acknowledgement.get('acknowledged') is True
                        and acknowledgement.get('fenced') is True,
                        'RecoveryRequired', 'Replay stop acknowledgment missing')
            measured = {'currency': 'USD', 'money_cents': 0,
                        'execution_us': math.ceil((time.monotonic() - started) * 1000000), 'review_us': 0}
            meter = self.budget.meter(EVALUATOR, reservation, measured, observations[-1][0])
            settled = self.budget.settle(EVALUATOR, reservation, meter)
            usage = self.ledger.object(canonical(settled))
            self.record({'kind': 'replay-settled', 'objects': [usage]})
            gates['budget_state'] = {'status': 'pass', 'evidence': [usage]}
        except Exception as exc:
            error = exc.record if isinstance(exc, Failure) else Failure('RecoveryRequired', 'Replay outcome unknown').record
            decision = 'Inconclusive'
            gates['independent_replay'] = {'status': 'error', 'evidence': [self.reference]}
            gates['budget_state'] = {'status': 'error', 'evidence': [reservation]}
            self.budget.halt()  # Unknown usage never releases its reservation.
            for run in runs:
                try:
                    control_call(self.runtime / 'ipc/executor-control.sock', {'action': 'stop', 'run': run},
                                 expected_uid=RUNNER, timeout=2)
                except Exception:
                    self.record({'kind': 'replay-stop-unconfirmed', 'run': run, 'reservation': reservation})
        transition = failure_transition(previous, decision == 'Verified defect', self.threshold)
        stop = transition['stopped'] or error is not None
        if stop:
            self.budget.halt()
        gates['evidence_integrity_currency'] = {'status': 'pass', 'evidence': [self.ledger.tip()]}
        receipt = {'type': 'ReplayReceipt', 'version': 1, 'run': self.plan['run'], 'attempt': attempt,
                   'allegation': self.reference, 'finding': decision, 'gates': gates,
                   'execution_complete': completed, 'verified': decision == 'Verified defect',
                   'admission': 'blocked', 'promotion': 'disabled', 'error': error,
                   'reservation': reservation, 'reservation_state': 'held' if error else 'settled',
                   'identities': dict(self.allegation, image=IMAGE, profile=PROFILE,
                                      supervisor=SUPERVISOR, helper=HELPER, toolchain=self.toolchain),
                   'environment_differences': {'fresh_guest_runs': runs,
                                               'mode': self.mode, 'replay_profile': PROFILE,
                                               'source_reconstructions': self.source_reconstructions,
                                               'prior_smoke_reused': False},
                   'consecutive_failures': transition['consecutive_failures'], 'stopped': stop}
        hashed = self.ledger.object(canonical(receipt))
        def finish(db: object, event_receipt: dict) -> None:
            db.execute('UPDATE replay_state SET failures=?,stopped=?,pending=NULL WHERE run=?',
                       (transition['consecutive_failures'], int(stop), self.plan['run']))
        self.ledger.append_atomic(EVALUATOR, {'kind': 'independent-replay-receipt', 'objects': [hashed],
                                  'attempt': attempt, 'finding': decision}, self.ledger.tip(), uuid.uuid4().hex, finish)
        return receipt

    def export(self) -> dict:
        snapshot = self.ledger.snapshot({'kind': 'replay-export', 'admission': 'blocked'}, uuid.uuid4().hex)
        return export_snapshot(snapshot, self.home / ('export-' + uuid.uuid4().hex))

    def close(self) -> None:
        self.budget.db.close()
        self.ledger.close()
        os.close(self.lock)


def validate_mode_results(mode: str, results: list, observations: list) -> None:
    """Validate actual mode evidence; matching a finding string alone is not proof."""
    expected = {'normal': ['Verified defect'], 'failed-rebuild': ['Inconclusive'],
                'interruption': ['Inconclusive'],
                'two-failures': ['Verified defect', 'Not reproduced', 'Not reproduced']}
    require(mode in MODES and [item['finding'] for item in results] == expected[mode],
            'IntegrityFailure', 'Fixed replay findings differ')
    require(len(observations) == 2 * len(results)
            and len({request['run'] for request, _ in observations}) == len(observations),
            'IntegrityFailure', 'Fresh replay observation count differs')
    for index, (request, result) in enumerate(observations):
        require(request['challenge'] == (BASELINE if index % 2 == 0 else MODES[mode][index // 2]),
                'IntegrityFailure', 'Fixed replay fixture sequence differs')
        if mode != 'interruption' or index == 0:
            require(result['transport_complete'] is True and result['error'] is None,
                    'IntegrityFailure', 'Expected complete observation absent')
    if mode == 'failed-rebuild':
        require(observations[-1][1]['guest']['candidate_observation']['build_exit'] != 0
                and results[0]['reservation_state'] == 'settled' and results[0]['error'] is None,
                'IntegrityFailure', 'Actual failed rebuild absent')
    elif mode == 'interruption':
        last = observations[-1][1]
        require(last['transport_complete'] is False and last['ceased'] is True
                and last.get('interruption') == {'kind': 'fixed-replay-command-interruption', 'bound_seconds': 60}
                and (last['error'] or {}).get('code') in ('Stopped', 'Unavailable')
                and last['seconds'] >= 60 and last['raw_bytes'] > 0
                and results[0]['reservation_state'] == 'held' and results[0]['stopped'],
                'IntegrityFailure', 'Bounded interrupted guest and conservative hold absent')
    elif mode == 'two-failures':
        require([item['consecutive_failures'] for item in results] == [0, 1, 2]
                and [item['stopped'] for item in results] == [False, False, True]
                and all(item['reservation_state'] == 'settled' for item in results),
                'IntegrityFailure', 'Retained two-failure stop sequence absent')
    require(all(item['admission'] == 'blocked' and item['promotion'] == 'disabled' for item in results),
            'IntegrityFailure', 'Fixture execution cannot authorize admission')


def evaluator(mode: str = 'normal') -> int:
    require_identity(EVALUATOR)
    session = ReplaySession(mode)
    try:
        results = []
        for _ in MODES[mode]:
            reserved = session.reserve()
            results.append(session.reproduce(session.config['operator_uid'], session.reference, POLICY_SHA256, reserved['id']))
        observations = []
        for row in session.ledger.db.execute('SELECT body FROM events ORDER BY seq'):
            event = json.loads(row[0])
            if event.get('kind') == 'replay-raw-observation':
                observations.append((event['request'], json.loads((session.ledger.objects / event['objects'][0]).read_bytes())))
        validate_mode_results(mode, results, observations)
        session.export()
        return 0
    except Exception:
        session.budget.halt()
        session.export()
        raise
    finally:
        session.close()
