"""Fixed offline preflight adapter using the accepted executor's auth/stop state.

No operator-supplied shell or QEMU flags. Separate root-controlled configuration;
the synthetic Executor remains unchanged. Returned observations are not admission.
"""
import json
import base64
import os
from pathlib import Path
import selectors
import shutil
import signal
import subprocess
import threading
import time
import uuid
from common import EVALUATOR, RUNNER, Failure, canonical, digest, fields, identifier, require, serve
from execution import Executor, ASSETS


def input_mount_command(token: str) -> str:
    """Discover detached media by content, not QEMU's block enumeration order."""
    require(len(token) == 32 and all(c in '0123456789abcdef' for c in token),
            'InvalidInput', 'Invalid readiness token')
    return (
        "mkdir -p /inputs; grrr_input=; for grrr_dev in /dev/vd*; do "
        "test -b \"$grrr_dev\" || continue; "
        "test \"$(cat /sys/class/block/${grrr_dev##*/}/ro)\" = 1 || continue; "
        "mount -t iso9660 -o ro \"$grrr_dev\" /inputs || continue; "
        "if test -f /inputs/offline-guest.sh && "
        "awk '$2 == \"/inputs\" && $3 == \"iso9660\" && "
        "$4 ~ /(^|,)ro(,|$)/ {found=1} END {exit !found}' /proc/mounts; "
        "then grrr_input=$grrr_dev; break; fi; "
        "umount /inputs || break; done; "
        "test -n \"$grrr_input\" && printf '" + token + "\\n'"
    )


def validate_config(config: dict) -> dict:
    """Validate the fixed capability surface independently of filesystem trust."""
    fields(config, {'version', 'profile_sha256', 'image_sha256', 'license_review_sha256', 'qemu_sha256',
                    'network', 'shares', 'memory_mib', 'vcpus', 'command_seconds', 'total_seconds'})
    for key in ('profile_sha256', 'image_sha256', 'license_review_sha256', 'qemu_sha256'):
        identifier(config[key], True)
    require(all(type(config[key]) is int for key in ('version', 'memory_mib', 'vcpus', 'command_seconds', 'total_seconds')),
            'InvalidInput', 'Numeric configuration has wrong type')
    require(config['version'] == 1 and config['network'] is False and config['shares'] == []
            and config['memory_mib'] == 512 and config['vcpus'] == 1
            and config['command_seconds'] == 240 and config['total_seconds'] == 300,
            'GateBlocked', 'Offline capabilities or limits differ from approved profile')
    return config


def read_config(root: Path) -> dict:
    """Reject unknown/misconfigured capabilities before launching any VM."""
    path = root / 'offline-config.json'
    require(path.is_file() and not path.is_symlink(), 'Unavailable', 'Offline config missing')
    with os.fdopen(os.open(path, os.O_RDONLY | os.O_NOFOLLOW), 'rb') as stream:
        info = os.fstat(stream.fileno())
        require(info.st_uid == 0 and info.st_mode & 0o222 == 0,
                'Unauthorized', 'Offline configuration is not root-controlled')
        require(info.st_size <= 8192, 'InvalidInput', 'Offline configuration too large')
        raw = stream.read(8193)
    require(len(raw) <= 8192, 'InvalidInput', 'Offline configuration too large')
    return validate_config(json.loads(raw))


class OfflineExecutor(Executor):
    def __init__(self, root: Path) -> None:
        super().__init__(root)
        self.config = read_config(root)
        self.builds_consumed = 0

    def stop(self, run: str) -> dict:
        """Bound termination; record actual force-kill use rather than intent."""
        started = time.monotonic()
        with self.lock:
            self.fenced.add(run)
            process = self.active.get(run)
            if process and process.poll() is None:
                process.terminate()
        forced = False
        if process:
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                forced = True
                process.kill()
                process.wait(timeout=2)
        return {'run': run, 'ceased': process is None or process.poll() is not None,
                'seconds': time.monotonic() - started, 'forced': forced, 'fenced': True}

    def handle(self, uid: int, message: dict) -> dict:
        require(uid == EVALUATOR, 'Unauthorized', 'Executor peer is not evaluator')
        if message.get('action') == 'stop':
            fields(message, {'action', 'run'})
            started = time.monotonic()
            run = identifier(message['run'])
            with self.lock:
                self.fenced.add(run)
                process = self.active.get(run)
                if process and process.poll() is None:
                    process.terminate()
            return {'run': run, 'acknowledged': True, 'fenced': True,
                    'seconds': time.monotonic() - started}
        return super().handle(uid, message)

    def dispatch(self, principal: int, request: dict, reservation: str, fence: int, key: str) -> dict:
        require(principal == EVALUATOR, 'Unauthorized', 'Only evaluator dispatches offline profile')
        fields(request, {'run', 'variant', 'probe'})
        run = identifier(request['run'])
        identifier(reservation)
        identifier(key)
        require(type(fence) is int and fence == 0, 'StaleBinding', 'Offline epoch differs')
        require(request['variant'] == self.config['profile_sha256']
                and request['probe'] in (None, 'stop', 'force', 'watchdog', 'output'),
                'InvalidInput', 'Offline invocation is not allowlisted')
        require(read_config(self.root) == self.config, 'StaleBinding', 'Offline configuration changed')
        require(shutil.disk_usage(self.root).free >= 15000000000, 'BudgetExceeded', 'Insufficient host space')
        require(Path(self.qemu).is_file(), 'Unavailable', 'QEMU absent')
        require(digest(Path(self.qemu).read_bytes()) == self.config['qemu_sha256'],
                'IntegrityFailure', 'QEMU executable bytes changed')
        version = subprocess.run([self.qemu, '--version'], capture_output=True, timeout=5, check=True)
        require(b'version 11.1.2' in version.stdout, 'StaleBinding', 'QEMU version differs')
        expected = dict(ASSETS, **{'input.iso': self.config['image_sha256']})
        for name, hashed in expected.items():
            path = self.root / 'assets' / name
            require(path.is_file() and not path.is_symlink(), 'Unavailable', 'Offline dependency absent: ' + name)
            require(path.stat().st_uid == 0 and path.stat().st_mode & 0o222 == 0,
                    'Unauthorized', 'Offline asset not root read-only')
            require(digest(path.read_bytes()) == hashed, 'IntegrityFailure', 'Offline asset mismatch: ' + name)
        assets = self.root / 'assets'
        args = [self.qemu, '-machine', 'virt', '-cpu', 'host', '-accel', 'hvf', '-m', '512', '-smp', '1',
                '-kernel', str(assets / 'vmlinuz-virt'), '-initrd', str(assets / 'initramfs-virt'),
                '-append', 'modules=loop,squashfs,sd-mod,usb-storage console=ttyAMA0',
                '-cdrom', str(assets / 'alpine-virt-3.22.6-aarch64.iso'),
                '-drive', 'file=' + str(assets / 'input.iso') + ',if=none,id=inputs,format=raw,readonly=on',
                '-device', 'virtio-blk-device,drive=inputs',
                '-net', 'none', '-nographic', '-monitor', 'none', '-no-reboot', '-snapshot']
        with self.lock:
            require(run not in self.fenced, 'Stopped', 'Offline run fenced')
            require(key not in self.keys, 'StaleBinding', 'Offline dispatch key consumed')
            require(not self.active, 'BudgetExceeded', 'One active offline guest maximum')
            if request['probe'] is None:
                require(self.builds_consumed < 2, 'BudgetExceeded', 'Two independent builds already reserved')
                self.builds_consumed += 1
            self.keys[key] = request
            process = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                       cwd=self.root, env={'PATH': '/usr/bin:/bin', 'HOME': '/var/empty'})
            self.active[run] = process
        started = time.monotonic()
        captured = bytearray()
        selector = selectors.DefaultSelector()
        selector.register(process.stdout, selectors.EVENT_READ)
        watchdog = threading.Timer(293, self.stop, args=(run,))
        watchdog.start()

        def until(marker: bytes, seconds: float) -> bytes:
            begin = len(captured)
            deadline = min(started + 293, time.monotonic() + seconds)
            while time.monotonic() < deadline:
                with self.lock:
                    require(run not in self.fenced, 'Stopped', 'Offline run fenced')
                for _, _ in selector.select(0.05):
                    chunk = os.read(process.stdout.fileno(), 65536)
                    require(bool(chunk), 'Unavailable', 'Offline guest transport ended')
                    available = 1048576 - len(captured)
                    captured.extend(chunk[:available])
                    require(len(chunk) <= available, 'GateBlocked', 'Offline output cap exceeded')
                    if marker in captured[begin:]:
                        return bytes(captured[begin:])
                require(process.poll() is None, 'Unavailable', 'Offline guest exited')
            raise Failure('GateBlocked', 'Offline evaluator deadline exceeded')

        def send(command: str) -> None:
            process.stdin.write(command.encode('ascii') + b'\n')
            process.stdin.flush()

        error, observation = None, b''
        exit_code = None
        command_started = None
        command_seconds = None
        try:
            until(b'localhost login:', 30)
            send('root')
            until(b'localhost:~#', 5)
            send('stty -echo')
            until(b'localhost:~#', 5)
            token = uuid.uuid4().hex
            send(input_mount_command(token))
            until(token.encode(), 5)
            with self.lock:
                if request['probe'] == 'force':
                    os.kill(process.pid, signal.SIGSTOP)
                self.ready.add(run)
            if request['probe'] in ('stop', 'force'):
                until(b'NEVER-EMITTED', 300)
            elif request['probe'] == 'watchdog':
                send('sleep 241')
                until(b'NEVER-EMITTED', 240)
            elif request['probe'] == 'output':
                send('yes GRRR-OFFLINE-CAP')
                until(b'NEVER-EMITTED', 240)
            token = uuid.uuid4().hex
            command_started = time.monotonic()
            send("printf '" + token + "-BEGIN\\n'; sh /inputs/offline-guest.sh; r=$?; printf '" + token + "-EXIT:%s\\n' \"$r\"")
            raw = until((token + '-EXIT:').encode(), 240)
            if b'\n' not in raw.split((token + '-EXIT:').encode(), 1)[1]:
                raw += until(b'\n', 2)
            raw = raw.replace(b'\r\n', b'\n')
            observation, tail = raw.split((token + '-BEGIN\n').encode(), 1)[1].split((token + '-EXIT:').encode(), 1)
            exit_code = int(tail.split(b'\n', 1)[0])
        except (Failure, OSError, ValueError) as exc:
            error = exc.record if isinstance(exc, Failure) else Failure('Unavailable', type(exc).__name__).record
        finally:
            if command_started is not None:
                command_seconds = time.monotonic() - command_started
            termination = self.stop(run)
            watchdog.cancel()
            selector.close()
            process.stdin.close()
            process.stdout.close()
            with self.lock:
                self.active.pop(run, None)
                self.ready.discard(run)
        unchanged = all(digest((assets / name).read_bytes()) == hashed for name, hashed in expected.items())
        return {'run': run, 'pid': process.pid, 'command': args, 'assets': expected,
                'profile_sha256': self.config['profile_sha256'], 'assets_unchanged': unchanged,
                'qemu_version': version.stdout.decode().splitlines()[0], 'termination': termination,
                'observation_base64': base64.b64encode(observation).decode(),
                'raw_base64': base64.b64encode(bytes(captured)).decode(), 'error': error,
                'command_seconds': command_seconds,
                'exit_code': exit_code, 'seconds': time.monotonic() - started,
                'transport_complete': error is None}


if __name__ == '__main__':
    import sys
    root = Path(sys.argv[1]).resolve()
    serve(root.parent / 'ipc/executor.sock', OfflineExecutor(root).handle)
