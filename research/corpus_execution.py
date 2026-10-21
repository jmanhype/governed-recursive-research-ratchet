"""Dedicated UID-separated executor for one disposable corpus scenario per guest."""
import base64
import json
import os
from pathlib import Path
import selectors
import shutil
import subprocess
import threading
import time
import uuid

from common import EVALUATOR, RUNNER, Failure, canonical, digest, fields, identifier, require, serve
from execution import ASSETS
from trusted_execution import (QEMU_EXECUTABLE, QEMU_EXECUTABLE_PATH, QEMU_MANIFEST, configuration_digest,
                               protected_bytes, root_record, validate_approval, verify_qemu)
from trusted_install import record
from trusted_transport import AuthenticatedServer

PROFILE = '3d1e7a00e217c19e2ceb873b1e0d2f3e7bc7b26b5948b7015752e992aa0a7536'
IMAGE = '68914235e557c7a1a6e0ec82a52c4ac8204c7e92e32d44189da22bbd46fc06ea'
SUPERVISOR = '30ca782a41df8bc64b8c47310a8034c77f92a0c2008e2657ba0e7f50f1b7e26a'
HELPER = '8c1706ed51f37bc0e0f0cb0861409a4ed256bf7a34b20c118eb630fe05dfd6c8'
RECEIPT = '410feec29dd30e9663170b1871c8270ec65de628ca2e62efcca5c4bcb99f9127'
CORPUS_FREEZE = '30d463052af3e988638484a24ec03e1965d37e05bd358c0ecb243a249754d48c'
PRESERVED_ROOT = Path('/Library/GRRR/validated-corpus/v2')
PRESERVED = {'input.iso': IMAGE, 'preparation.json': RECEIPT, 'prepared-profile.json': PROFILE}
LIMITS = {'memory_mib': 1024, 'workspace_mib': 512, 'vcpus': 1, 'boot_seconds': 45,
          'command_seconds': 420, 'total_seconds': 480, 'stop_ack_seconds': 2,
          'term_grace_seconds': 5, 'kill_wait_seconds': 2, 'output_bytes': 1048576,
          'wire_bytes': 3145728, 'minimum_host_free_bytes': 15000000000}


def validate_preserved() -> dict:
    require(PRESERVED_ROOT.is_absolute() and not PRESERVED_ROOT.is_symlink(),
            'Unauthorized', 'Corpus preserved root differs')
    members = {entry.name for entry in PRESERVED_ROOT.iterdir()}
    require(members == set(PRESERVED), 'IntegrityFailure', 'Corpus preserved member set differs')
    return {name: digest(protected_bytes(PRESERVED_ROOT / name, expected))
            for name, expected in PRESERVED.items()}


def validate_config(config: dict) -> dict:
    fields(config, {'version', 'profile', 'image', 'supervisor', 'helper', 'host_code', 'operator_uid',
                    'limits', 'network', 'host_shares', 'paid_dispatch', 'read_only_inputs',
                    'qemu_installation', 'corpus_binding', 'accounting_binding', 'bootstrap_sha256', 'python_sha256',
                    'execution_profile'})
    identifier(config['host_code'], True); identifier(config['corpus_binding'], True); identifier(config['accounting_binding'], True)
    for name in ('qemu_installation', 'bootstrap_sha256', 'python_sha256'):
        identifier(config[name], True)
    require(config['version'] == 1 and type(config['version']) is int
            and config['profile'] == PROFILE and config['image'] == IMAGE
            and config['supervisor'] == SUPERVISOR and config['helper'] == HELPER
            and config['limits'] == LIMITS and config['network'] is False
            and config['host_shares'] is False and config['paid_dispatch'] is False
            and config['read_only_inputs'] is True and config['corpus_binding'] == CORPUS_FREEZE
            and config['accounting_binding'] == digest(canonical({'kind':'disposable-corpus-budget',
                                                                  'corpus_freeze':CORPUS_FREEZE,'profile':PROFILE}))
            and type(config['operator_uid']) is int and config['operator_uid'] not in (0, EVALUATOR, RUNNER)
            and config['execution_profile'] == configuration_digest(config),
            'GateBlocked', 'Corpus execution profile differs')
    return config


def validate_request(message: dict) -> None:
    fields(message, {'action', 'version', 'run', 'arm', 'challenge', 'variant', 'key',
                     'reservation', 'epoch', 'probe'})
    for name in ('run', 'arm', 'key', 'reservation'):
        identifier(message[name])
    challenge = message['challenge']
    valid = isinstance(challenge, str) and len(challenge) == 12 and challenge.startswith('GRRR-VC-') \
        and challenge[-4] in 'DC' and challenge[-3:].isdigit()
    require(message['action'] == 'dispatch' and message['version'] == 1 and message['arm'] == 'validated-corpus'
            and valid and message['variant'] == challenge and message['probe'] is None
            and type(message['epoch']) is int and message['epoch'] == 0,
            'InvalidInput', 'Unknown corpus invocation')


def decode_candidate(raw: bytes, challenge: str) -> dict:
    require(len(raw) <= 524288, 'InvalidInput', 'Oversized candidate observation')
    value = json.loads(raw)
    fields(value, {'version', 'challenge', 'test', 'build_exit', 'build_output_sha256',
                   'repetitions', 'internal_error'})
    require(value['version'] == 1 and value['challenge'] == challenge
            and value['test'] == 'TestGRRR' + challenge[-4:] and value['build_exit'] in (0, 1, 2)
            and isinstance(value['build_output_sha256'], str) and len(value['build_output_sha256']) == 64
            and value['internal_error'] is False and isinstance(value['repetitions'], list)
            and len(value['repetitions']) == 3, 'InvalidInput', 'Candidate observation differs')
    for repetition in value['repetitions']:
        fields(repetition, {'exit', 'output_sha256'})
        require(type(repetition['exit']) is int and 0 <= repetition['exit'] <= 2
                and isinstance(repetition['output_sha256'], str) and len(repetition['output_sha256']) == 64,
                'InvalidInput', 'Candidate repetition differs')
    return value


def decode_guest(raw: bytes, run: str, challenge: str) -> dict:
    require(len(raw) <= 1048576, 'InvalidInput', 'Oversized supervisor record')
    value = json.loads(raw)
    fields(value, {'version', 'run', 'challenge', 'variant', 'supervisor_sha256', 'supervisor_unchanged',
                   'candidate_credentials', 'candidate_exit_success', 'candidate_output', 'output_exceeded',
                   'kernel_lock_held_by_supervisor', 'seconds', 'candidate_cessation', 'verified', 'admission', 'scope'})
    require(value['version'] == 1 and value['run'] == run and value['challenge'] == challenge
            and value['variant'] == challenge and value['supervisor_sha256'] == SUPERVISOR
            and value['supervisor_unchanged'] is True and value['verified'] is False
            and value['admission'] == 'blocked' and value['candidate_exit_success'] is True
            and value['candidate_cessation'] is True and value['kernel_lock_held_by_supervisor'] is True
            and value['output_exceeded'] is False and 0 < value['seconds'] <= LIMITS['total_seconds'],
            'IntegrityFailure', 'Corpus supervisor binding differs')
    status = value['candidate_credentials']
    require(isinstance(status, dict) and status.get('Uid') == status.get('Gid') == '1000 1000 1000 1000'
            and status.get('Groups') == '' and status.get('NoNewPrivs') == '1'
            and all(status.get(key) == '0' * 16 for key in ('CapEff', 'CapPrm', 'CapInh', 'CapBnd', 'CapAmb')),
            'IntegrityFailure', 'Candidate separation not observed')
    candidate = base64.b64decode(value['candidate_output'], validate=True)
    value['candidate_observation'] = decode_candidate(candidate, challenge)
    return value


class CorpusExecutor:
    def __init__(self, root: Path):
        require(os.getuid() == RUNNER, 'Unauthorized', 'Corpus executor requires UID 321')
        self.root = root
        validate_preserved()
        self.config = validate_config(root_record(root / 'config.json'))
        validate_approval(root_record(root / 'approval.json'), self.config, root_record(root / 'license.json'))
        self.lock = threading.RLock(); self.active = {}; self.fenced = set()
        self.requests = {}; self.results = {}; self.ready = set(); self.halted = False; self.launches = 0

    def stop(self, run: str) -> dict:
        started = time.monotonic()
        with self.lock:
            self.fenced.add(run); process = self.active.get(run)
            if process and process.poll() is None: process.terminate()
        return {'run': run, 'fenced': True, 'acknowledged': True, 'seconds': time.monotonic() - started}

    def handle(self, uid: int, message: dict) -> dict:
        require(uid == EVALUATOR, 'Unauthorized', 'Kernel-authenticated evaluator required')
        if message.get('action') in ('stop', 'status'):
            fields(message, {'action', 'run'}); run = identifier(message['run'])
            if message['action'] == 'stop': return self.stop(run)
            with self.lock:
                return {'run': run, 'active': run in self.active, 'ready': run in self.ready,
                        'fenced': run in self.fenced, 'result': self.results.get(run),
                        'launches': self.launches, 'halted': self.halted}
        validate_request(message); return self.dispatch(message)

    def dispatch(self, message: dict) -> dict:
        run, key, challenge = message['run'], message['key'], message['challenge']
        with self.lock:
            if key in self.requests:
                require(self.requests[key] == message, 'StaleBinding', 'Dispatch key changed request')
                require(run in self.results, 'RecoveryRequired', 'Corpus effect pending')
                return self.results[run]
            require(not self.halted and run not in self.fenced, 'Stopped', 'Executor fenced/stopped')
            require(run not in self.active and run not in self.results, 'StaleBinding', 'Run identifier reused')
            require(not self.active, 'BudgetExceeded', 'One active corpus guest maximum')
            self.requests[key] = dict(message)
        validate_preserved(); validate_config(root_record(self.root / 'config.json'))
        validate_approval(root_record(self.root / 'approval.json'), self.config, root_record(self.root / 'license.json'))
        require(shutil.disk_usage(self.root).free >= LIMITS['minimum_host_free_bytes'],
                'BudgetExceeded', 'Host free space below floor')
        installation = root_record(self.root / 'qemu-installation.json')
        require(digest(canonical(installation)) == QEMU_MANIFEST, 'IntegrityFailure', 'QEMU approval differs')
        executable = verify_qemu(installation)
        require(executable == QEMU_EXECUTABLE_PATH and digest(executable.read_bytes()) == QEMU_EXECUTABLE,
                'IntegrityFailure', 'Installed QEMU differs')
        assets = self.root / 'assets'
        for name, hashed in ASSETS.items():
            path = assets / name
            require(path.is_file() and not path.is_symlink() and path.stat().st_uid == 0
                    and path.stat().st_mode & 0o222 == 0 and digest(path.read_bytes()) == hashed,
                    'IntegrityFailure', 'VM asset differs: ' + name)
        args = [str(executable), '-no-user-config', '-L', str(Path(installation['root']) / 'data'),
                '-machine', 'virt', '-cpu', 'host', '-accel', 'hvf', '-m', '1024', '-smp', '1',
                '-kernel', str(assets / 'vmlinuz-virt'), '-initrd', str(assets / 'initramfs-virt'),
                '-append', 'modules=loop,squashfs,sd-mod,usb-storage console=ttyAMA0',
                '-cdrom', str(assets / 'alpine-virt-3.22.6-aarch64.iso'),
                '-drive', f'file={PRESERVED_ROOT}/input.iso,if=none,id=inputs,format=raw,readonly=on',
                '-device', 'virtio-blk-device,drive=inputs', '-net', 'none', '-nographic',
                '-monitor', 'none', '-no-reboot', '-snapshot']
        with self.lock:
            require(not self.halted and run not in self.fenced, 'Stopped', 'Fence changed before launch')
            process = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                       stderr=subprocess.STDOUT, cwd=self.root,
                                       env={'PATH': '/usr/bin:/bin', 'HOME': '/var/empty', 'LC_ALL': 'C'},
                                       start_new_session=True)
            self.active[run] = process; self.launches += 1
        started = time.monotonic(); raw = bytearray(); selector = selectors.DefaultSelector()
        selector.register(process.stdout, selectors.EVENT_READ)

        def watchdog() -> None:
            self.halted = True; self.stop(run)
        timer = threading.Timer(475, watchdog); timer.start()

        def until(marker: bytes, seconds: float) -> bytes:
            begin = len(raw); deadline = min(started + 475, time.monotonic() + seconds)
            while time.monotonic() < deadline:
                with self.lock: require(run not in self.fenced, 'Stopped', 'Fenced during transport')
                for _ in selector.select(0.05):
                    chunk = os.read(process.stdout.fileno(), 65536)
                    require(bool(chunk), 'Unavailable', 'Incomplete guest transport')
                    available = 1048576-len(raw); raw.extend(chunk[:available])
                    require(len(chunk) <= available, 'GateBlocked', 'Guest output exceeded cap')
                    if marker in raw[begin:]: return bytes(raw[begin:])
                require(process.poll() is None, 'Unavailable', 'Guest exited before observation')
            raise Failure('Stopped', 'Corpus watchdog exhausted')

        def send(command: str) -> None:
            process.stdin.write(command.encode('ascii')+b'\n'); process.stdin.flush()

        guest = error = exit_code = None
        try:
            until(b'localhost login:', LIMITS['boot_seconds']); send('root'); until(b'localhost:~#', 10)
            send('stty -echo'); until(b'localhost:~#', 5)
            token = uuid.uuid4().hex
            send("mkdir /inputs; mounted=; for dev in /dev/vd*; do test -b \"$dev\" || continue; "
                 'test "$(cat /sys/class/block/${dev##*/}/ro)" = 1 || continue; '
                 'mount -t iso9660 -o ro "$dev" /inputs || continue; '
                 'if test -f /inputs/guest.sh; then mounted=1; break; fi; umount /inputs || break; done; '
                 'test "$mounted" = 1 && printf \''+token+'\\n\'')
            until(token.encode(), 10)
            with self.lock: self.ready.add(run)
            request = {'version': 1, 'run': run, 'challenge': challenge, 'variant': challenge}
            encoded = base64.b64encode(canonical(request)).decode()
            token = uuid.uuid4().hex
            send("printf '"+token+"-BEGIN\\n'; printf '%s' '"+encoded+
                 "' | base64 -d | sh /inputs/guest.sh; result=$?; printf '"+token+"-EXIT:%s\\n' \"$result\"")
            observed = until((token+'-EXIT:').encode(), LIMITS['command_seconds'])
            if b'\n' not in observed.split((token+'-EXIT:').encode(), 1)[1]:
                observed += until(b'\n', 2)
            observed = observed.replace(b'\r\n', b'\n')
            body, tail = observed.split((token+'-BEGIN\n').encode(), 1)[1].split((token+'-EXIT:').encode(), 1)
            exit_code = int(tail.split(b'\n', 1)[0]); records = [line for line in body.splitlines() if line.startswith(b'{')]
            require(len(records) == 1 and exit_code == 0, 'GateBlocked', 'Corpus supervisor failed')
            guest = decode_guest(records[0], run, challenge)
        except (Failure, OSError, ValueError) as exc:
            error = exc.record if isinstance(exc, Failure) else Failure('Unavailable', 'Corpus transport failed').record
            self.halted = True
        finally:
            self.stop(run); forced = False
            try: process.wait(timeout=5)
            except subprocess.TimeoutExpired: forced = True; process.kill(); process.wait(timeout=2)
            timer.cancel(); selector.close(); process.stdin.close(); process.stdout.close()
            with self.lock: self.active.pop(run, None); self.ready.discard(run)
        result = {'version': 1, 'run': run, 'key': key, 'reservation': message['reservation'],
                  'guest': guest, 'error': error, 'transport_complete': error is None,
                  'ceased': process.poll() is not None, 'forced': forced,
                  'seconds': time.monotonic()-started, 'raw_sha256': digest(bytes(raw)),
                  'raw_bytes': len(raw), 'raw_base64': base64.b64encode(raw).decode(), 'exit_code': exit_code,
                  'profile': PROFILE, 'image': IMAGE, 'supervisor': SUPERVISOR, 'helper': HELPER,
                  'execution_profile': self.config['execution_profile'], 'qemu_installation': QEMU_MANIFEST}
        with self.lock: self.results[run] = result
        return result


if __name__ == '__main__':
    import sys
    root = Path(sys.argv[1]).resolve(strict=True)
    executor = CorpusExecutor(root)
    data_server = AuthenticatedServer(root.parent/'ipc/executor.sock', executor.handle)
    control_server = AuthenticatedServer(root.parent/'ipc/executor-control.sock', executor.handle, control=True)
    threading.Event().wait()
