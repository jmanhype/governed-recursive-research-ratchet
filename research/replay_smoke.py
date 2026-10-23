"""One-shot C001 runtime lifecycle only. No allegation verdict or ReplayReceipt."""
import base64
import fcntl
import math
import os
from pathlib import Path
import shutil
import signal
import subprocess
import threading
import time
import uuid

from common import EVALUATOR, RUNNER, Failure, call, canonical, digest, fields, require
from budget import Budget
from ledger import Ledger
from corpus_execution import (CorpusExecutor, CORPUS_FREEZE, PROFILE, IMAGE, SUPERVISOR,
                              HELPER, LIMITS as CORPUS_LIMITS, decode_guest, validate_request)
from execution import ASSETS
from replay_prerequisites import (REPLAY_ROOT, LOCK, POLICY_SHA256, check_absent,
                                  protected_preflight, validate_policy, approved_account_groups,
                                  validate_service_groups, ACCOUNT_NAMES)
from trusted_execution import configuration_digest, protected_bytes, root_record, QEMU_MANIFEST
from trusted_install import immutable
from trusted_transport import AuthenticatedServer, control_call

SMOKE = REPLAY_ROOT / 'runtime-smoke'
CHALLENGE = 'GRRR-VC-C001'
SCOPE = {'scope': 'C001-runtime-lifecycle-only', 'challenge': CHALLENGE, 'attempts': 1,
         'work_seconds': 473, 'total_seconds': 480, 'independent_replay_authorized': False,
         'contract_admission_authorized': False}


def validate_scope(value: dict) -> dict:
    """Pin every scope field, including integer types and explicit denials."""
    require(canonical(value) == canonical(SCOPE), 'GateBlocked', 'Unapproved runtime smoke scope')
    return value


def require_identity(uid: int) -> None:
    """Require the actual dedicated identity, not caller-supplied role fields."""
    require(os.getuid() == uid and os.geteuid() == uid and os.getgid() == uid
            and os.getegid() == uid,
            'Unauthorized', 'Dedicated UID/GID required')
    validate_service_groups(uid, os.getgroups())


def scope_event(kind: str, **values: object) -> dict:
    """Events cannot be promoted to a verdict or independent replay receipt."""
    require(kind in {'runtime-smoke-reserved', 'runtime-smoke-transport', 'runtime-smoke-settled',
                     'runtime-smoke-failed', 'runtime-smoke-stop-unconfirmed',
                     'runtime-smoke-parent-lifecycle', 'runtime-smoke-complete'}
            and not set(values).intersection(set(SCOPE) | {'kind', 'verdict', 'verified', 'ReplayReceipt', 'admission'}),
            'InvalidInput', 'Smoke evidence scope cannot be overridden')
    return dict(SCOPE, kind=kind, **values)


def read_plan() -> dict:
    plan = root_record(SMOKE / 'plan.json')
    fields(plan, {'run', 'scope', 'policy_sha256'})
    validate_scope(plan['scope'])
    require(plan['policy_sha256'] == POLICY_SHA256 and isinstance(plan['run'], str)
            and len(plan['run']) == 32 and all(c in '0123456789abcdef' for c in plan['run']),
            'GateBlocked', 'Smoke policy/run binding differs')
    return plan


class SmokeExecutor(CorpusExecutor):
    """Exact accepted C001 supervisor/probes; parent owns the entire process group."""
    def __init__(self) -> None:
        require_identity(RUNNER)
        self.plan = read_plan()
        self.policy = validate_policy(protected_bytes(SMOKE / 'policy.json', POLICY_SHA256))
        self.claimed = False
        super().__init__(SMOKE / 'runner')

    def handle(self, uid: int, message: dict) -> dict:
        require(uid == EVALUATOR and message.get('run') == self.plan['run'],
                'Unauthorized', 'Evaluator and exact smoke run required')
        if message.get('action') == 'dispatch':
            validate_request(message)
            require(message['challenge'] == CHALLENGE and message['variant'] == CHALLENGE
                    and message['key'] == self.plan['run'], 'GateBlocked', 'Only approved C001 smoke allowed')
            with self.lock:
                require(not self.claimed, 'Stopped', 'One-shot smoke already attempted')
                self.claimed = True
        return super().handle(uid, message)

    def spawn_guest(self, args: list) -> subprocess.Popen:
        require_identity(RUNNER)
        require(shutil.disk_usage(SMOKE).free >= self.policy['limits']['minimum_host_free_bytes'],
                'BudgetExceeded', 'Approved 15 GiB floor unavailable')
        # Root starts this service in a dedicated process group. Inheriting it
        # makes parent TERM/KILL cover the guest even if the service fails.
        return subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, cwd=self.root / 'scratch',
                                env={'PATH': '/usr/bin:/bin', 'HOME': '/var/empty', 'LC_ALL': 'C'},
                                start_new_session=False)


def runner() -> int:
    """Start bounded authenticated data/control endpoints as runner, not root."""
    require_identity(RUNNER)
    executor = SmokeExecutor()
    data = AuthenticatedServer(SMOKE / 'ipc/executor.sock', executor.handle)
    control = AuthenticatedServer(SMOKE / 'ipc/executor-control.sock', executor.handle, control=True)
    try:
        threading.Event().wait()
    finally:
        data.close()
        control.close()
    return 0


def validate_result(value: dict, request: dict) -> None:
    """Validate transport/cessation/isolation only; never inspect corpus truth."""
    require(isinstance(value, dict) and value.get('run') == request['run']
            and value.get('key') == request['key'] and value.get('reservation') == request['reservation'],
            'StaleBinding', 'Smoke result binding differs')
    require(value.get('ceased') is True and value.get('transport_complete') is True
            and value.get('forced') is False and value.get('error') is None
            and value.get('exit_code') == 0, 'RecoveryRequired', 'Smoke lifecycle not proven')
    seconds = value.get('seconds')
    require(type(seconds) in (float, int) and math.isfinite(seconds) and 0 < seconds <= 480,
            'BudgetUnknown', 'Smoke duration unknown')
    require(value.get('profile') == PROFILE and value.get('image') == IMAGE
            and value.get('supervisor') == SUPERVISOR and value.get('helper') == HELPER
            and value.get('qemu_installation') == QEMU_MANIFEST
            and value.get('execution_profile') == root_record(SMOKE / 'runner/config.json')['execution_profile'],
            'IntegrityFailure', 'Smoke artifact binding differs')
    raw = base64.b64decode(value['raw_base64'], validate=True)
    require(len(raw) == value['raw_bytes'] <= 1048576 and digest(raw) == value['raw_sha256'],
            'IntegrityFailure', 'Smoke raw evidence differs')
    # This checks candidate credentials and supervisor isolation, not expected
    # C001 answers. No verdict() or CorpusSession is imported or called.
    decode_guest(canonical(value['guest']), request['run'], CHALLENGE)


def evaluator() -> int:
    """Reserve one zero-money runtime smoke and preserve all uncertain holds."""
    require_identity(EVALUATOR)
    plan = read_plan()
    policy = validate_policy((SMOKE / 'evaluator/policy.json').read_bytes())
    require(policy['limits']['paid_cost_units'] == 0, 'GateBlocked', 'Paid smoke denied')
    budget = Budget(SMOKE / 'evaluator/smoke-budget.sqlite')
    journal = Ledger(SMOKE / 'evaluator/smoke-ledger')
    def record(kind: str, **values) -> None:
        journal.append(EVALUATOR, scope_event(kind, **values), journal.tip(), uuid.uuid4().hex)
    request = {'action': 'dispatch', 'version': 1, 'run': plan['run'], 'arm': 'validated-corpus',
               'challenge': CHALLENGE, 'variant': CHALLENGE, 'key': plan['run'],
               'reservation': 'unreserved', 'epoch': 0, 'probe': None}
    maximum = {'currency': 'USD', 'money_cents': 0, 'execution_us': 480000000, 'review_us': 0}
    started = time.monotonic()
    try:
        reservation = budget.reserve(EVALUATOR, plan['run'], maximum, plan['run'],
                                     binding=digest(canonical(request)))
        request['reservation'] = reservation['id']
        record('runtime-smoke-reserved', reservation=reservation['id'], maximum=maximum)
        result = call(SMOKE / 'ipc/executor.sock', request, timeout=470)
        raw_object = journal.object(canonical(result))
        record('runtime-smoke-transport', objects=[raw_object], reservation='held')
        validate_result(result, request)
        stop_started = time.monotonic()
        stopped = control_call(SMOKE / 'ipc/executor-control.sock',
                               {'action': 'stop', 'run': plan['run']}, expected_uid=RUNNER, timeout=2)
        require(stopped.get('acknowledged') is True and stopped.get('fenced') is True
                and time.monotonic() - stop_started <= 2, 'RecoveryRequired', 'Stop acknowledgment unproven')
        usage = {'currency': 'USD', 'money_cents': 0,
                 'execution_us': math.ceil((time.monotonic() - started) * 1000000), 'review_us': 0}
        meter = budget.meter(EVALUATOR, reservation['id'], usage, raw_object)
        budget.settle(EVALUATOR, reservation['id'], meter)
        record('runtime-smoke-settled', objects=[raw_object], usage=usage)
        return 0
    except Exception as exc:
        budget.halt()
        record('runtime-smoke-failed', reservation='held', error=type(exc).__name__)
        try:
            control_call(SMOKE / 'ipc/executor-control.sock', {'action': 'stop', 'run': plan['run']},
                         expected_uid=RUNNER, timeout=2)
        except Exception:
            record('runtime-smoke-stop-unconfirmed', reservation='held')
        return 1
    finally:
        budget.db.close()
        journal.close()


def present_groups(groups: set, deadline: float) -> set:
    """Read kernel process inventory; macOS killpg(0) may return EPERM for an empty group."""
    remaining = deadline - time.monotonic()
    require(remaining > 0, 'RecoveryRequired', 'Cessation observation deadline exhausted')
    raw = subprocess.run(['/bin/ps', '-axo', 'pgid=,pid='], check=True, capture_output=True,
                         timeout=min(0.2, remaining), env={'PATH': '/usr/bin:/bin', 'LC_ALL': 'C'}).stdout
    lines = raw.splitlines()
    require(bool(lines), 'RecoveryRequired', 'Empty cessation process inventory')
    active = set()
    for line in lines:
        columns = line.split()
        require(len(columns) == 2 and all(part.isdigit() for part in columns),
                'RecoveryRequired', 'Malformed cessation process inventory')
        if int(columns[0]) in groups:
            active.add(int(columns[0]))
    return active


def cease_groups(processes: list, deadline: float) -> bool:
    """Signal all service/guest groups concurrently, never multiply grace periods."""
    uncertain = False
    for sig, allowance in ((signal.SIGTERM, 5), (signal.SIGKILL, 2)):
        for process in processes:
            try:
                os.killpg(process.pid, sig)
            except ProcessLookupError:
                continue
            except OSError:
                uncertain = True
        until = min(deadline, time.monotonic() + allowance)
        while time.monotonic() < until:
            # Group existence, not just service exit, establishes guest cessation.
            try:
                for process in processes:
                    process.poll()
                absent = not present_groups({p.pid for p in processes}, deadline)
            except (Failure, OSError, subprocess.SubprocessError):
                uncertain = True
                break  # Still advance to KILL for every tracked group.
            if absent:
                if not uncertain:
                    return True
                break
            time.sleep(0.02)
    return False


class DeferredStop:
    """Signal handlers only record intent; never unwind an in-flight Popen."""
    def __init__(self) -> None:
        self.requested = False

    def handler(self, signum: int, frame: object) -> None:
        self.requested = True

    def checkpoint(self) -> None:
        require(not self.requested, 'Stopped', 'Parent stop requested')

    def spawn(self, processes: list, args: list, **kwargs) -> subprocess.Popen:
        self.checkpoint()
        process = subprocess.Popen(args, **kwargs)
        processes.append(process)
        # Every successfully created child is tracked before stop can unwind.
        self.checkpoint()
        return process


def launch(parent: object, review: dict, code: dict) -> int:
    """Root-only, one-shot parent lifecycle; no automatic retry or namespace reset."""
    require(os.getuid() == 0 and os.geteuid() == 0, 'Unauthorized', 'Root parent required')
    validate_scope(review['smoke'])
    immutable(LOCK)
    with os.fdopen(os.open(LOCK, os.O_RDONLY | os.O_NOFOLLOW), 'rb') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        protected_preflight(parent.INPUTS / 'corpus', parent.INPUTS / 'vm',
                            parent.INPUTS / 'source.tar', parent.INPUTS / 'policy.json',
                            lock.fileno(), installed=True)
        check_absent(SMOKE)
        os.umask(0o077)
        SMOKE.mkdir(mode=0o711)
        SMOKE.chmod(0o711)
        expected = {'.': {'kind': 'directory', 'uid': 0, 'gid': 0, 'mode': 0o711}}
        def emit(name: str, raw: bytes, owner: int = 0, mode: int = 0o444) -> None:
            parent.write(SMOKE / name, raw, owner, mode)
            expected[name] = {'kind': 'file', 'uid': owner, 'gid': owner, 'mode': mode, 'raw': raw}
        for name, owner, mode in (('private', 0, 0o700), ('ipc', 0, 0o1777),
                                 ('runner', 0, 0o755), ('runner/assets', 0, 0o755),
                                 ('runner/scratch', RUNNER, 0o700), ('evaluator', EVALUATOR, 0o700)):
            path = SMOKE / name
            path.mkdir(mode=mode)
            os.chown(path, owner, owner)
            path.chmod(mode)
            expected[name] = {'kind': 'directory', 'uid': owner, 'gid': owner, 'mode': mode}
        policy = parent.read(parent.INPUTS / 'policy.json', POLICY_SHA256)
        emit('policy.json', policy)
        emit('evaluator/policy.json', policy, EVALUATOR, 0o400)
        plan = {'run': uuid.uuid4().hex, 'scope': SCOPE, 'policy_sha256': POLICY_SHA256}
        emit('plan.json', canonical(plan))
        emit('private/review.json', canonical(review), mode=0o400)
        for name, hashed in ASSETS.items():
            source = parent.INPUTS / 'vm' / (name if name.endswith('.iso') else 'boot/' + name)
            immutable(source)
            emit('runner/assets/' + name, protected_bytes(source, hashed))
        license_review = root_record(Path('/Library/GRRR/validated-corpus/v2-records/license.json'))
        config = {'version': 1, 'profile': PROFILE, 'image': IMAGE, 'supervisor': SUPERVISOR,
                  'helper': HELPER, 'host_code': digest(canonical(parent.CODE)), 'operator_uid': 501,
                  'limits': CORPUS_LIMITS, 'network': False, 'host_shares': False,
                  'paid_dispatch': False, 'read_only_inputs': True, 'qemu_installation': QEMU_MANIFEST,
                  'corpus_binding': CORPUS_FREEZE,
                  'accounting_binding': digest(canonical({'kind': 'disposable-corpus-budget',
                                                         'corpus_freeze': CORPUS_FREEZE, 'profile': PROFILE})),
                  'bootstrap_sha256': digest(parent.read(parent.SELF)),
                  'python_sha256': digest(parent.PYTHON.read_bytes())}
        config['execution_profile'] = configuration_digest(config)
        approval = {key: config[key] for key in ('version', 'operator_uid', 'profile', 'image',
                    'supervisor', 'helper', 'host_code', 'qemu_installation', 'accounting_binding',
                    'bootstrap_sha256', 'python_sha256', 'execution_profile')}
        approval.update(decision='approved-trusted-execution',
                        license_review_sha256=digest(canonical(license_review)),
                        authorization_reference=review['review_reference'])
        emit('runner/config.json', canonical(config))
        emit('runner/approval.json', canonical(approval))
        emit('runner/license.json', canonical(license_review))
        emit('runner/qemu-installation.json', parent.read(Path('/Library/GRRR/qemu/installation.json')))
        parent.verify_destination(SMOKE, expected)
        processes, logs = [], []
        started = time.monotonic()
        success = False
        stop = DeferredStop()
        def start(role: str, uid: int) -> subprocess.Popen:
            approved_account_groups(uid)
            def identity() -> None:
                os.initgroups(ACCOUNT_NAMES[uid], uid)
                os.setgid(uid)
                os.setuid(uid)
                os.umask(0o077)
            log = (SMOKE / ('private/' + role + '.log')).open('xb')
            logs.append(log)
            process = stop.spawn(processes, [str(parent.PYTHON), '-I', '-S', '-B', str(parent.SELF),
                                        '--smoke-' + role], cwd=SMOKE,
                                       env={'PATH': '/usr/bin:/bin', 'LC_ALL': 'C'},
                                       stdout=log, stderr=subprocess.STDOUT,
                                       preexec_fn=identity, start_new_session=True)
            return process
        try:
            signal.signal(signal.SIGTERM, stop.handler)
            signal.signal(signal.SIGINT, stop.handler)
            service = start('runner', RUNNER)
            ready_deadline = min(started + 473, time.monotonic() + 15)
            while time.monotonic() < ready_deadline and service.poll() is None:
                stop.checkpoint()
                if all((SMOKE / ('ipc/' + name)).is_socket()
                       for name in ('executor.sock', 'executor-control.sock')):
                    break
                time.sleep(0.02)
            require(service.poll() is None
                    and (SMOKE / 'ipc/executor-control.sock').is_socket(),
                    'Unavailable', 'Smoke service failed to become ready')
            evaluator_process = start('evaluator', EVALUATOR)
            while evaluator_process.poll() is None and time.monotonic() < started + 473:
                stop.checkpoint()
                time.sleep(0.02)
            stop.checkpoint()
            success = evaluator_process.poll() == 0
        finally:
            signal.signal(signal.SIGTERM, signal.SIG_IGN)
            signal.signal(signal.SIGINT, signal.SIG_IGN)
            try:
                ceased = cease_groups(processes, started + 480)
            except (Failure, OSError, subprocess.SubprocessError):
                ceased = False
            elapsed = time.monotonic() - started
            for log in logs:
                log.flush()
                os.fsync(log.fileno())
                log.close()
            parent.write(SMOKE / 'private/lifecycle.json',
                         canonical(scope_event('runtime-smoke-parent-lifecycle', children_ceased=ceased,
                                               elapsed_seconds=elapsed, evaluator_succeeded=success,
                                               exit_codes=[p.poll() for p in processes])), 0, 0o400)
        require(ceased and elapsed <= 480 and success,
                'RecoveryRequired', 'Runtime lifecycle incomplete; preserve state, never retry')
        print(canonical(scope_event('runtime-smoke-complete', children_ceased=True)).decode())
        return 0
