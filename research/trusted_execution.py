"""Dedicated v4 executor; no launch without root-owned exact execution approval."""
import base64
import json
import os
from pathlib import Path
import selectors
import shutil
import stat
import subprocess
import threading
import time
import uuid
from common import EVALUATOR, RUNNER, Failure, canonical, digest, fields, identifier, require, serve, unique_fields
from execution import ASSETS
from trusted_install import verify_qemu
from trusted_transport import AuthenticatedServer

PROFILE = 'a37c2ecff8094f1b52a97d214926b5040dd3afb480c63c617ccc78365b4fc205'
IMAGE = '57c48a6845d65b6b3674c80367af42c062cf079d7bbdc4491331a4945375d2b6'
SUPERVISOR = 'a9a0fd9a8471bc1859e5ab91c3746a139942562f719784fec51b8254eb8307d6'
HELPER = '14603a520a8a7d6f460aaa6057097da78e0cdba97a3e620ee8d4fcd3c5b62d2e'
RECEIPT = '3d280af9e69ff05300cb0058194db14995a2d4baf927ef84d24e1199c7e70fa7'
DEVELOPMENT_BINDING = '9fd432900036552fcdeb95ed1433937e01fbc45b73250aba91f6ed87a0efc209'
QEMU_MANIFEST = 'e40888d8d14bc9c2b8db38d8468bc53fdbf77421b284d9eacbbce1d37818b625'
QEMU_EXECUTABLE = '352108bbc46171ed74ee3ef0b74ac1f32403c7e076ebac623ce2c265724699da'
QEMU_ROOT = Path('/Library/GRRR/qemu')
QEMU_EXECUTABLE_PATH = QEMU_ROOT / 'bin/qemu-system-aarch64'
PRESERVED_ROOT = Path('/Library/GRRR/trusted-observation/v4')
PRESERVED_V4 = {
    'prepared-profile.json': PROFILE,
    'input.iso': IMAGE,
    'preparation.json': RECEIPT,
    'development-binding.json': DEVELOPMENT_BINDING,
    'supervisor': SUPERVISOR,
    'helper': HELPER,
}
PROTECTED_UID = 0
PROTECTED_GID = 0
PROTECTED_FILE_MODE = 0o444
PRESERVED_DIRECTORY_MODE = 0o755
PRESERVED_FILE_MAX_BYTES = 128 * 1024 * 1024
ROOT_RECORD_MAX_BYTES = 128 * 1024
VARIANTS = ('clean', 'forged-pass', 'altered-expectations', 'mutation', 'impersonation', 'oversized', 'malformed')
LIMITS = {'memory_mib': 1024, 'workspace_mib': 512, 'vcpus': 1, 'boot_seconds': 30,
          'command_seconds': 240, 'total_seconds': 300, 'stop_ack_seconds': 2,
          'term_grace_seconds': 5, 'kill_wait_seconds': 2, 'output_bytes': 1048576,
          'wire_bytes': 3145728, 'minimum_host_free_bytes': 15000000000}


def configuration_digest(config):
    return digest(canonical({key: value for key, value in config.items() if key != 'execution_profile'}))


def _acl_free(path: Path) -> bool:
    """Inspect the macOS ACL marker without interpreting file bytes as instructions."""
    try:
        output = subprocess.run(['/bin/ls', '-lde', str(path)], capture_output=True,
                                check=True, timeout=2, env={'PATH': '/usr/bin:/bin', 'LC_ALL': 'C'}).stdout
    except (OSError, subprocess.SubprocessError) as exc:
        raise Failure('Unauthorized', 'Protected path ACL could not be inspected') from exc
    fields = output.split(None, 1)
    return bool(fields) and b'+' not in fields[0]


def _safe_ancestors(path: Path) -> None:
    """Require root-owned, non-link, non-group/world-writable, ACL-free ancestors."""
    for ancestor in (path, *path.parents):
        try:
            info = ancestor.lstat()
        except OSError as exc:
            raise Failure('GateBlocked', 'Protected ancestor absent or unreadable') from exc
        require(not stat.S_ISLNK(info.st_mode) and info.st_uid == PROTECTED_UID
                and info.st_gid == PROTECTED_GID and info.st_mode & 0o022 == 0,
                'Unauthorized', 'Protected ancestor metadata differs')
        require(_acl_free(ancestor), 'Unauthorized', 'ACL-bearing protected ancestor')


def protected_bytes(path: Path, expected: str | None = None, maximum: int = PRESERVED_FILE_MAX_BYTES) -> bytes:
    """Open one no-follow root-owned 0444 regular file and optionally bind its bytes."""
    require(path.is_absolute(), 'Unauthorized', 'Absolute protected path required')
    try:
        before = path.lstat()
        require(not stat.S_ISLNK(before.st_mode), 'Unauthorized', 'Protected path symlink')
        descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
        with os.fdopen(descriptor, 'rb') as stream:
            info = os.fstat(stream.fileno())
            require(stat.S_ISREG(info.st_mode) and info.st_uid == PROTECTED_UID and info.st_gid == PROTECTED_GID
                    and stat.S_IMODE(info.st_mode) == PROTECTED_FILE_MODE and info.st_nlink == 1
                    and info.st_size <= maximum, 'Unauthorized', 'Protected file metadata differs')
            require(_acl_free(path), 'Unauthorized', 'ACL-bearing protected file')
            raw = stream.read(maximum + 1)
            require(_acl_free(path), 'IntegrityFailure', 'Protected file ACL changed during verification')
    except (OSError, ValueError) as exc:
        raise Failure('GateBlocked', 'Protected file absent or unreadable') from exc
    try:
        after = path.lstat()
    except OSError as exc:
        raise Failure('IntegrityFailure', 'Protected path vanished during verification') from exc
    require((before.st_dev, before.st_ino, before.st_mode, before.st_uid, before.st_gid, before.st_nlink)
            == (after.st_dev, after.st_ino, after.st_mode, after.st_uid, after.st_gid, after.st_nlink)
            and (after.st_dev, after.st_ino, after.st_mode, after.st_uid, after.st_gid, after.st_nlink)
            == (info.st_dev, info.st_ino, info.st_mode, info.st_uid, info.st_gid, info.st_nlink),
            'IntegrityFailure', 'Protected path changed during verification')
    require(len(raw) <= maximum, 'InvalidInput', 'Protected file too large')
    if expected is not None:
        require(digest(raw) == expected, 'IntegrityFailure', 'Protected file bytes differ')
    return raw


def validate_preserved_v4(root: Path = PRESERVED_ROOT) -> dict:
    """Verify the exact six-member preserved v4 namespace before any launch path."""
    require(root == PRESERVED_ROOT and root.is_absolute(), 'Unauthorized', 'Preserved v4 root differs')
    try:
        info = root.lstat()
        members = {entry.name for entry in root.iterdir()}
    except OSError as exc:
        raise Failure('GateBlocked', 'Preserved v4 root absent or unreadable') from exc
    _safe_ancestors(root)
    require(stat.S_ISDIR(info.st_mode) and info.st_uid == PROTECTED_UID and info.st_gid == PROTECTED_GID
            and stat.S_IMODE(info.st_mode) == PRESERVED_DIRECTORY_MODE and _acl_free(root),
            'Unauthorized', 'Preserved v4 directory metadata differs')
    require(members == set(PRESERVED_V4), 'IntegrityFailure', 'Preserved v4 member set differs')
    verified = {name: digest(protected_bytes(root / name, expected))
            for name, expected in PRESERVED_V4.items()}
    after = root.lstat()
    require((after.st_dev, after.st_ino, after.st_mode, after.st_uid, after.st_gid, after.st_nlink)
            == (info.st_dev, info.st_ino, info.st_mode, info.st_uid, info.st_gid, info.st_nlink)
            and {entry.name for entry in root.iterdir()} == members
            and _acl_free(root), 'IntegrityFailure', 'Preserved v4 root changed during verification')
    return verified


def root_record(path: Path) -> dict:
    """Check an opened file's ownership/mode, not a prior path-only stat."""
    raw = protected_bytes(path, maximum=ROOT_RECORD_MAX_BYTES)
    try:
        return json.loads(raw, object_pairs_hook=unique_fields)
    except ValueError as exc:
        raise Failure('GateBlocked', 'Required root record malformed') from exc


def validate_config(config: dict) -> dict:
    fields(config, {'version', 'profile', 'image', 'supervisor', 'helper', 'host_code', 'operator_uid', 'limits',
                    'network', 'host_shares', 'paid_dispatch', 'read_only_inputs',
                    'qemu_installation', 'accounting_binding', 'bootstrap_sha256', 'python_sha256', 'execution_profile'})
    identifier(config['host_code'], True)
    for name in ('qemu_installation', 'accounting_binding', 'bootstrap_sha256', 'python_sha256'):
        identifier(config[name], True)
    require(config['execution_profile'] == configuration_digest(config),
            'StaleBinding', 'Composed execution profile differs from reviewed configuration')
    require(config['version'] == 1 and type(config['version']) is int
            and config['profile'] == PROFILE and config['image'] == IMAGE
            and config['supervisor'] == SUPERVISOR and config['helper'] == HELPER and config['limits'] == LIMITS
            and config['qemu_installation'] == QEMU_MANIFEST
            and all(type(v) is int for v in config['limits'].values())
            and config['network'] is False and config['host_shares'] is False
            and config['paid_dispatch'] is False and config['read_only_inputs'] is True
            and type(config['operator_uid']) is int and config['operator_uid'] not in (0, EVALUATOR, RUNNER),
            'GateBlocked', 'Trusted profile capabilities differ')
    return config


def validate_approval(approval: dict, config: dict, review: dict) -> None:
    fields(approval, {'version', 'decision', 'operator_uid', 'profile', 'image', 'supervisor', 'helper',
                      'host_code', 'license_review_sha256', 'authorization_reference',
                      'qemu_installation', 'accounting_binding', 'bootstrap_sha256', 'python_sha256', 'execution_profile'})
    require(approval['version'] == 1 and type(approval['version']) is int
            and approval['decision'] == 'approved-trusted-execution'
            and all(approval[k] == config[k] for k in ('operator_uid', 'profile', 'image', 'supervisor', 'helper', 'host_code',
                                                      'qemu_installation', 'accounting_binding', 'bootstrap_sha256', 'python_sha256', 'execution_profile'))
            and approval['license_review_sha256'] == digest(canonical(review)),
            'GateBlocked', 'No execution approval for exact code/profile/license binding')
    identifier(approval['authorization_reference'], True)
    fields(review, {'version', 'decision', 'preparation_receipt', 'compiler', 'guest_toolchain',
                    'authorization_reference'})
    require(type(review['version']) is int and review['version'] == 1 and review['decision'] == 'approved-local-use'
            and review['preparation_receipt'] == RECEIPT
            and review['compiler'] == 'e670dfa79b080bad7f7d6b1d7131145c8c49068096650ebf0ac6292f098db60d'
            and review['guest_toolchain'] == '3f4227ce7b206a513e794f1393adb473a07b46e94d18bd15d1c684bbb7319797',
            'GateBlocked', 'Exact local-use provenance review absent')
    identifier(review['authorization_reference'], True)


def validate_request(message: dict) -> None:
    fields(message, {'action', 'version', 'run', 'arm', 'challenge', 'variant', 'key', 'reservation', 'epoch', 'probe'})
    for key in ('run', 'arm', 'key', 'reservation'):
        identifier(message[key])
    require(message['action'] == 'dispatch' and type(message['version']) is int and message['version'] == 1
            and message['arm'] == 'trusted-control' and message['challenge'] == 'vlt-lock-observation-001'
            and message['variant'] in VARIANTS and message['probe'] in (None, 'stop', 'deadline'),
            'InvalidInput', 'Unknown structured invocation')
    require(type(message['epoch']) is int and message['epoch'] == 0, 'StaleBinding', 'Invalid launch epoch')


def decode_guest(raw: bytes, run: str, variant: str) -> dict:
    require(len(raw) <= 1048576, 'InvalidInput', 'Oversized supervisor record')
    try:
        value = json.loads(raw, object_pairs_hook=unique_fields,
                           parse_constant=lambda x: (_ for _ in ()).throw(ValueError(x)))
    except (ValueError, UnicodeError) as exc:
        raise Failure('InvalidInput', 'Malformed/truncated supervisor record') from exc
    fields(value, {'version', 'run', 'challenge', 'variant', 'supervisor_sha256', 'supervisor_unchanged',
                   'candidate_credentials', 'candidate_exit_success', 'candidate_output', 'output_exceeded',
                   'kernel_lock_held_by_supervisor', 'note_absent_during_hold', 'observed_note', 'note_regular',
                   'seconds', 'candidate_cessation', 'verified', 'admission', 'scope'})
    require(type(value['version']) is int and value['version'] == 1 and value['run'] == run
            and value['variant'] == variant and value['challenge'] == 'vlt-lock-observation-001'
            and value['supervisor_sha256'] == SUPERVISOR and value['supervisor_unchanged'] is True
            and value['verified'] is False and value['admission'] == 'blocked',
            'IntegrityFailure', 'Supervisor binding/integrity differs')
    for key in ('candidate_exit_success', 'output_exceeded', 'kernel_lock_held_by_supervisor',
                'note_absent_during_hold', 'note_regular', 'candidate_cessation'):
        require(type(value[key]) is bool, 'InvalidInput', 'Supervisor flag has wrong type')
    status = value['candidate_credentials']
    require(isinstance(status, dict) and all(isinstance(k, str) and isinstance(v, str)
            and len(k) <= 80 and len(v) <= 2048 for k, v in status.items()) and len(status) <= 100,
            'InvalidInput', 'Invalid kernel credential record')
    require(status.get('Uid') == status.get('Gid') == '1000 1000 1000 1000'
            and status.get('Groups') == '' and status.get('NoNewPrivs') == '1'
            and all(status.get(k) == '0000000000000000' for k in ('CapEff', 'CapPrm', 'CapInh', 'CapBnd', 'CapAmb')),
            'IntegrityFailure', 'Candidate separation not observed')
    for key, cap in (('candidate_output', 524288), ('observed_note', 4096)):
        # Go represents an empty capture and absent note as nil []byte.
        if value[key] is None:
            require(key == 'candidate_output' or value['note_regular'] is False, 'InvalidInput', 'Missing note')
            continue
        require(isinstance(value[key], str), 'InvalidInput', 'Byte field must be base64')
        try:
            data = base64.b64decode(value[key], validate=True)
        except ValueError as exc:
            raise Failure('InvalidInput', 'Invalid base64 observation') from exc
        require(len(data) <= cap, 'InvalidInput', 'Observation exceeds inner cap')
    require(type(value['seconds']) in (int, float) and 0 <= value['seconds'] <= 240,
            'InvalidInput', 'Unknown/invalid supervisor duration')
    require(isinstance(value['scope'], str) and len(value['scope']) <= 200,
            'InvalidInput', 'Unbounded supervisor scope')
    return value


class TrustedExecutor:
    def __init__(self, root: Path) -> None:
        require(os.getuid() == RUNNER, 'Unauthorized', 'Trusted executor requires UID 321')
        self.root = root
        self.preserved = validate_preserved_v4()
        self.config = validate_config(root_record(root / 'config.json'))
        validate_approval(root_record(root / 'approval.json'), self.config, root_record(root / 'license.json'))
        self.lock = threading.RLock()
        self.active: dict[str, subprocess.Popen] = {}
        self.fenced: set[str] = set()
        self.requests: dict[str, dict] = {}
        self.results: dict[str, dict] = {}
        self.ready: set[str] = set()
        self.halted = False
        self.launches = 0

    def stop(self, run: str) -> dict:
        """Acknowledge fence immediately; dispatch owns bounded TERM/KILL wait."""
        started = time.monotonic()
        with self.lock:
            self.fenced.add(run)
            process = self.active.get(run)
            if process and process.poll() is None:
                process.terminate()
        return {'run': run, 'fenced': True, 'acknowledged': True, 'seconds': time.monotonic() - started}

    def handle(self, uid: int, message: dict) -> dict:
        require(uid == EVALUATOR, 'Unauthorized', 'Kernel-authenticated evaluator required')
        if message.get('action') in ('stop', 'status'):
            fields(message, {'action', 'run'})
            run = identifier(message['run'])
            if message['action'] == 'stop':
                return self.stop(run)
            with self.lock:
                return {'run': run, 'active': run in self.active, 'ready': run in self.ready,
                        'fenced': run in self.fenced, 'result': self.results.get(run),
                        'launches': self.launches, 'halted': self.halted}
        validate_request(message)
        return self.dispatch(message)

    def dispatch(self, message: dict) -> dict:
        run, key = message['run'], message['key']
        with self.lock:
            if key in self.requests:
                require(self.requests[key] == message, 'StaleBinding', 'Dispatch key changed request')
                require(run in self.results, 'RecoveryRequired', 'Effect pending; query status, do not dispatch again')
                return self.results[run]
            require(not self.halted and run not in self.fenced, 'Stopped', 'Executor fenced/stopped')
            require(run not in self.active and run not in self.results, 'StaleBinding', 'Run identifier already used')
            require(not self.active, 'BudgetExceeded', 'One active guest maximum')
            # Claim before slow verification. Reservation identifier is only
            # metadata, not launch authority; authenticated peer + current fence
            # and fresh approval remain mandatory at the actual launch.
            self.requests[key] = dict(message)
        require(validate_config(root_record(self.root / 'config.json')) == self.config,
                'StaleBinding', 'Configuration changed')
        validate_approval(root_record(self.root / 'approval.json'), self.config, root_record(self.root / 'license.json'))
        validate_preserved_v4()
        require(shutil.disk_usage(self.root).free >= 15000000000, 'BudgetExceeded', 'Host free space below floor')
        installation = root_record(self.root / 'qemu-installation.json')
        require(digest(canonical(installation)) == self.config['qemu_installation'],
                'IntegrityFailure', 'QEMU installation approval differs')
        executable = verify_qemu(installation)
        require(executable == QEMU_EXECUTABLE_PATH and digest(executable.read_bytes()) == QEMU_EXECUTABLE,
                'IntegrityFailure', 'Installed QEMU executable differs')
        assets = self.root / 'assets'
        expected = dict(ASSETS)
        for name, hashed in expected.items():
            path = assets / name
            require(path.is_file() and not path.is_symlink() and path.stat().st_uid == 0
                    and path.stat().st_mode & 0o222 == 0 and digest(path.read_bytes()) == hashed,
                    'IntegrityFailure', 'Untrusted or changed asset')
        args = [str(executable), '-no-user-config', '-L', str(Path(installation['root']) / 'data'),
                '-machine', 'virt', '-cpu', 'host', '-accel', 'hvf', '-m', '1024', '-smp', '1',
                '-kernel', str(assets / 'vmlinuz-virt'), '-initrd', str(assets / 'initramfs-virt'),
                '-append', 'modules=loop,squashfs,sd-mod,usb-storage console=ttyAMA0',
                '-cdrom', str(assets / 'alpine-virt-3.22.6-aarch64.iso'),
                '-drive', 'file=' + str(PRESERVED_ROOT / 'input.iso')
                        + ',if=none,id=inputs,format=raw,readonly=on',
                '-device', 'virtio-blk-device,drive=inputs', '-net', 'none', '-nographic',
                '-monitor', 'none', '-no-reboot', '-snapshot']
        with self.lock:
            require(not self.halted and run not in self.fenced and message['epoch'] == 0,
                    'Stopped', 'Epoch/fence changed before launch')
            require(not self.active, 'BudgetExceeded', 'Concurrent launch rejected')
            process = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                cwd=self.root, env={'PATH': '/usr/bin:/bin', 'HOME': '/var/empty',
                                   'LC_ALL': 'C', 'LANG': 'C',
                                   'TMPDIR': str(self.root / 'scratch')})
            self.active[run] = process
            self.launches += 1
        started = time.monotonic()
        raw = bytearray()
        selector = selectors.DefaultSelector()
        selector.register(process.stdout, selectors.EVENT_READ)
        timeout = 1 if message['probe'] == 'deadline' else 293

        def watchdog() -> None:
            self.halted = True
            self.stop(run)
        timer = threading.Timer(timeout, watchdog)
        timer.start()

        def until(marker: bytes, seconds: float) -> bytes:
            begin = len(raw)
            deadline = min(started + timeout, time.monotonic() + seconds)
            while time.monotonic() < deadline:
                with self.lock:
                    require(run not in self.fenced, 'Stopped', 'Run fenced during transport')
                for _, _ in selector.select(0.05):
                    chunk = os.read(process.stdout.fileno(), 65536)
                    require(bool(chunk), 'Unavailable', 'Incomplete guest transport')
                    available = 1048576 - len(raw)
                    raw.extend(chunk[:available])
                    require(len(chunk) <= available, 'GateBlocked', 'Guest output cap exceeded')
                    if marker in raw[begin:]:
                        return bytes(raw[begin:])
                require(process.poll() is None, 'Unavailable', 'Guest exited before complete observation')
            raise Failure('Stopped', 'Bounded watchdog/deadline exhausted')

        def send(command: str) -> None:
            process.stdin.write(command.encode('ascii') + b'\n')
            process.stdin.flush()

        guest, error, exit_code = None, None, None
        try:
            until(b'localhost login:', 30)
            send('root')
            until(b'localhost:~#', 5)
            send('stty -echo')
            until(b'localhost:~#', 5)
            token = uuid.uuid4().hex
            send("mkdir /inputs; mounted=; for dev in /dev/vd*; do "
                 "test -b \"$dev\" || continue; test \"$(cat /sys/class/block/${dev##*/}/ro)\" = 1 || continue; "
                 "mount -t iso9660 -o ro \"$dev\" /inputs || continue; "
                 "if test -f /inputs/guest.sh; then mounted=1; break; fi; umount /inputs || break; done; "
                 "test \"$mounted\" = 1 && printf '" + token + "\\n'")
            until(token.encode(), 5)
            with self.lock:
                self.ready.add(run)
            if message['probe'] == 'stop':
                until(b'NEVER-EMITTED', 240)
            request = {'version': 1, 'run': run, 'challenge': message['challenge'], 'variant': message['variant']}
            encoded = base64.b64encode(canonical(request)).decode()
            token = uuid.uuid4().hex
            # Token is host-root-shell only. Candidate stdout is captured inside
            # the pinned supervisor, never sent directly to this serial channel.
            send("printf '" + token + "-BEGIN\\n'; printf '%s' '" + encoded +
                 "' | base64 -d | sh /inputs/guest.sh; result=$?; printf '" + token + "-EXIT:%s\\n' \"$result\"")
            observed = until((token + '-EXIT:').encode(), 240)
            if b'\n' not in observed.split((token + '-EXIT:').encode(), 1)[1]:
                observed += until(b'\n', 2)
            observed = observed.replace(b'\r\n', b'\n')
            body, tail = observed.split((token + '-BEGIN\n').encode(), 1)[1].split((token + '-EXIT:').encode(), 1)
            exit_code = int(tail.split(b'\n', 1)[0])
            # Bootstrap checks print only pinned checksum lines. The one JSON
            # line comes from private supervisor stdout, never candidate pipes.
            records = [line for line in body.splitlines() if line.startswith(b'{')]
            require(len(records) == 1 and exit_code == 0, 'GateBlocked', 'Supervisor did not complete successfully')
            guest = decode_guest(records[0], run, message['variant'])
        except (Failure, OSError, ValueError) as exc:
            error = exc.record if isinstance(exc, Failure) else Failure('Unavailable', 'Transport/format failure').record
            if message['probe'] != 'stop':
                self.halted = True
        finally:
            self.stop(run)
            forced = False
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                forced = True
                process.kill()
                process.wait(timeout=2)
            timer.cancel()
            selector.close()
            process.stdin.close()
            process.stdout.close()
            with self.lock:
                self.active.pop(run, None)
                self.ready.discard(run)
        result = {'version': 1, 'run': run, 'key': key, 'reservation': message['reservation'],
                  'guest': guest, 'error': error, 'transport_complete': error is None,
                  'ceased': process.poll() is not None, 'forced': forced, 'seconds': time.monotonic() - started,
                  'raw_sha256': digest(bytes(raw)), 'raw_bytes': len(raw), 'raw_base64': base64.b64encode(raw).decode(),
                  'exit_code': exit_code, 'profile': PROFILE, 'image': IMAGE, 'supervisor': SUPERVISOR,
                  'helper': HELPER,
                  'execution_profile': self.config['execution_profile'],
                  'qemu_installation': self.config['qemu_installation']}
        with self.lock:
            self.results[run] = result
        return result


if __name__ == '__main__':
    import sys
    root = Path(sys.argv[1]).resolve(strict=True)
    executor = TrustedExecutor(root)
    data_server = AuthenticatedServer(root.parent / 'ipc/executor.sock', executor.handle)
    control_server = AuthenticatedServer(root.parent / 'ipc/executor-control.sock', executor.handle, control=True)
    threading.Event().wait()
