"""Narrow runner-identity VM adapter. Candidate commands never execute on host."""
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
from common import EVALUATOR, RUNNER, VARIANTS, Failure, digest, fields, identifier, require, serve

ASSETS = {'alpine-virt-3.22.6-aarch64.iso': '09d601858d72484c89d576fb735215cccf54a92a03e67ca4a7fa7e4b8ec4a7a2',
          'vmlinuz-virt': 'dd37c4460f933ec909ff022c34944ff7e1a5300aff99750e3bdc02cd4074c332',
          'initramfs-virt': '899b8023e92db85345375b3ad10c2c9e5b977dc35a0429489ab2476ebad507ec'}
QEMU = '/opt/homebrew/bin/qemu-system-aarch64'


class Executor:
    def __init__(self, root: Path) -> None:
        require(os.getuid() == RUNNER, 'Unauthorized', 'Executor requires runner identity')
        self.root = root
        self.lock = threading.RLock()
        self.active: dict[str, subprocess.Popen] = {}
        self.fenced: set[str] = set()
        self.keys: dict[str, dict] = {}

    def stop(self, run: str) -> dict:
        started = time.monotonic()
        with self.lock:
            self.fenced.add(run)
            process = self.active.get(run)
            if process and process.poll() is None:
                process.terminate()
        if process:
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=2)
        return {'run': run, 'ceased': process is None or process.poll() is not None,
                'seconds': time.monotonic() - started, 'fenced': True}

    def dispatch(self, principal: int, request: dict, reservation: str,
                 fence: int, key: str) -> dict:
        require(principal == EVALUATOR, 'Unauthorized', 'Only evaluator may dispatch')
        fields(request, {'run', 'variant', 'probe'})
        run = identifier(request['run'])
        identifier(reservation)
        identifier(key)
        require(fence == 0, 'StaleBinding', 'Stale execution epoch')
        require(request['variant'] in VARIANTS and type(request['probe']) is bool,
                'InvalidInput', 'Variant not frozen/allowlisted')
        require(Path(QEMU).is_file(), 'Unavailable', 'Approved VM executable absent')
        version = subprocess.run([QEMU, '--version'], capture_output=True, timeout=5, check=True)
        require(b'version 11.1.2' in version.stdout, 'StaleBinding', 'QEMU version changed')
        require(shutil.disk_usage(self.root).free >= 15000000000,
                'BudgetExceeded', 'Host free space below approved minimum')
        before = {}
        for name, expected in ASSETS.items():
            path = self.root / 'assets' / name
            require(path.is_file() and not path.is_symlink(), 'Unavailable', 'VM asset absent')
            before[name] = digest(path.read_bytes())
            require(before[name] == expected, 'IntegrityFailure', 'VM asset hash changed')
        args = [QEMU, '-machine', 'virt', '-cpu', 'host', '-accel', 'hvf', '-m', '512',
                '-smp', '1', '-kernel', str(self.root / 'assets/vmlinuz-virt'),
                '-initrd', str(self.root / 'assets/initramfs-virt'), '-append',
                'modules=loop,squashfs,sd-mod,usb-storage console=ttyAMA0',
                '-cdrom', str(self.root / 'assets/alpine-virt-3.22.6-aarch64.iso'),
                '-net', 'none', '-nographic', '-monitor', 'none', '-no-reboot', '-snapshot']
        with self.lock:
            require(run not in self.fenced, 'Stopped', 'Run fenced')
            require(key not in self.keys, 'StaleBinding', 'Dispatch key already consumed')
            require(not self.active, 'BudgetExceeded', 'One active guest maximum')
            self.keys[key] = request
            process = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                       stderr=subprocess.STDOUT, cwd=self.root,
                                       env={'PATH': '/usr/bin:/bin', 'HOME': '/var/empty'},
                                       start_new_session=False)
            self.active[run] = process
        started = time.monotonic()
        captured = bytearray()
        selector = selectors.DefaultSelector()
        selector.register(process.stdout, selectors.EVENT_READ)

        def until(marker: bytes, seconds: float) -> bytes:
            begin = len(captured)
            deadline = min(started + 300, time.monotonic() + seconds)
            while time.monotonic() < deadline:
                with self.lock:
                    require(run not in self.fenced, 'Stopped', 'Emergency stop fenced guest')
                for _, _ in selector.select(0.05):
                    chunk = os.read(process.stdout.fileno(), 65536)
                    require(bool(chunk), 'Unavailable', 'Guest transport ended')
                    fits = len(captured) + len(chunk) <= 1048576
                    captured.extend(chunk[:1048576 - len(captured)])
                    require(fits, 'GateBlocked', 'Guest output exceeded cap')
                    if marker in captured[begin:]:
                        return bytes(captured[begin:])
                require(process.poll() is None, 'Unavailable', 'Guest exited before observation')
            raise Failure('GateBlocked', 'Evaluator-approved deadline exceeded')

        def send(command: str) -> None:
            process.stdin.write(command.encode('ascii') + b'\n')
            process.stdin.flush()

        error = None
        observation = b''
        exit_code = None
        isolation = b''
        try:
            until(b'localhost login:', 30)
            send('root')
            until(b'localhost:~#', 10)
            send('stty -echo')
            until(b'localhost:~#', 5)
            marker = uuid.uuid4().hex
            # Bootstrap is evaluator-authored; guest has no writable host mount.
            send("printf 'ISOLATION\\n'; ls /sys/class/net; cat /proc/mounts; "
                 "test ! -e /tmp/grrr-reset && echo RESET-CLEAN; touch /tmp/grrr-reset; "
                 f"printf '{marker}\\n'")
            isolation = until(marker.encode(), 5).replace(b'\r\n', b'\n')
            require(b'RESET-CLEAN\n' in isolation and b'\nlo\n' in isolation
                    and b'eth0' not in isolation and b'9p' not in isolation
                    and b'virtiofs' not in isolation, 'GateBlocked', 'Guest isolation/reset check failed')
            if request['probe']:
                # Pre-experiment emergency-stop exercise: deliberately await control cancellation.
                until(b'NEVER-EMITTED', 300)
            token = uuid.uuid4().hex
            send(f"printf '{token}-BEGIN\\n'; " + VARIANTS[request['variant']]['command'] +
                 f"; r=$?; printf '{token}-EXIT:%s\\n' \"$r\"")
            raw = until((token + '-EXIT:').encode(), 5)
            if b'\n' not in raw.split((token + '-EXIT:').encode(), 1)[1]:
                raw += until(b'\n', 5)
            raw = raw.replace(b'\r\n', b'\n')
            observation, tail = raw.split((token + '-BEGIN\n').encode(), 1)[1].split((token + '-EXIT:').encode(), 1)
            exit_code = int(tail.split(b'\n', 1)[0])
        except Failure as exc:
            error = exc.record
        finally:
            termination = self.stop(run)
            selector.close()
            process.stdin.close()
            process.stdout.close()
            with self.lock:
                self.active.pop(run, None)
        unchanged = all(digest((self.root / 'assets' / name).read_bytes()) == hashed
                        for name, hashed in before.items())
        return {'run': run, 'command': args, 'qemu_version': version.stdout.decode().splitlines()[0],
                'assets': before, 'assets_unchanged': unchanged, 'observation': observation.hex(),
                'exit_code': exit_code, 'raw': bytes(captured).hex(), 'isolation': isolation.hex(),
                'termination': termination, 'seconds': time.monotonic() - started,
                'error': error, 'transport_complete': error is None}

    def handle(self, uid: int, message: dict) -> dict:
        require(uid == EVALUATOR, 'Unauthorized', 'Executor peer is not evaluator')
        if message.get('action') == 'stop':
            fields(message, {'action', 'run'})
            return self.stop(identifier(message['run']))
        fields(message, {'action', 'request', 'reservation', 'epoch', 'key'})
        require(message['action'] == 'dispatch', 'InvalidInput', 'Unknown executor action')
        return self.dispatch(uid, message['request'], message['reservation'], message['epoch'], message['key'])


if __name__ == '__main__':
    import sys
    root = Path(sys.argv[1]).resolve()
    serve(root.parent / 'ipc/executor.sock', Executor(root).handle)
