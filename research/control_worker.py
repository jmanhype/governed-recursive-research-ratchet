#!/usr/bin/env python3
"""UID-321 safety worker: cancels tracked siblings without runner cooperation."""
from __future__ import annotations
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
from common import EVALUATOR, RUNNER, Failure, digest, fields, identifier, require
from trusted_transport import AuthenticatedServer


def process_state(pid: int) -> str | None:
    try:
        raw = subprocess.check_output(['/bin/ps', '-o', 'state=', '-p', str(pid)],
                                      timeout=1, stderr=subprocess.DEVNULL)
    except (OSError, subprocess.SubprocessError):
        return None
    value = raw.decode('ascii', 'ignore').strip()
    return value or None


def process_uid(pid: int) -> int:
    try:
        raw = subprocess.check_output(['/bin/ps', '-o', 'uid=', '-p', str(pid)],
                                      timeout=1, stderr=subprocess.DEVNULL)
        return int(raw.decode('ascii', 'ignore').strip())
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        raise Failure('RecoveryRequired', 'Tracked process identity is unavailable') from exc


def signal_process(pid: int, number: int) -> None:
    try:
        if os.getpgid(pid) == pid:
            os.killpg(pid, number)
        else:
            os.kill(pid, number)
    except ProcessLookupError:
        return


class ControlWorker:
    def __init__(self, baseline: Path, expected_digest: str) -> None:
        require(os.getuid() == RUNNER, 'Unauthorized', 'Safety worker requires runner identity')
        require(baseline.is_file() and not baseline.is_symlink(),
                'IntegrityFailure', 'Protected baseline absent')
        require(len(expected_digest) == 64 and all(char in '0123456789abcdef' for char in expected_digest),
                'InvalidInput', 'Baseline digest malformed')
        self.baseline = baseline
        self.expected_digest = expected_digest

    def handle(self, uid: int, message: dict) -> dict:
        require(uid == EVALUATOR, 'Unauthorized', 'Evaluator peer required')
        fields(message, {'action', 'run', 'pid', 'term_grace_seconds',
                         'kill_wait_seconds', 'baseline_digest'})
        require(message['action'] == 'stop', 'InvalidInput', 'Worker only performs safety stop')
        run = identifier(message['run'])
        pid, grace, wait = message['pid'], message['term_grace_seconds'], message['kill_wait_seconds']
        require(type(pid) is int and pid > 1 and pid != os.getpid(),
                'InvalidInput', 'Tracked process identity invalid')
        require(type(grace) is int and 0 < grace <= 5 and type(wait) is int and 0 < wait <= 5,
                'InvalidInput', 'Cancellation bounds differ from approved policy')
        require(message['baseline_digest'] == self.expected_digest,
                'StaleBinding', 'Baseline binding differs')
        require(process_uid(pid) == RUNNER, 'Unauthorized', 'Refusing to cancel a non-runner process')
        started = time.monotonic()
        signal_process(pid, signal.SIGTERM)
        deadline = started + grace
        while time.monotonic() < deadline and process_state(pid) not in (None, 'Z'):
            time.sleep(0.01)
        forced = process_state(pid) not in (None, 'Z')
        if forced:
            signal_process(pid, signal.SIGKILL)
            deadline = time.monotonic() + wait
            while time.monotonic() < deadline and process_state(pid) not in (None, 'Z'):
                time.sleep(0.01)
        ceased = process_state(pid) in (None, 'Z')
        require(ceased, 'RecoveryRequired', 'Tracked process cessation is unverified')
        baseline_ok = digest(self.baseline.read_bytes()) == self.expected_digest
        elapsed = time.monotonic() - started
        return {'ceased': True, 'forced': forced, 'seconds': elapsed, 'baseline_ok': baseline_ok}


def main() -> int:
    if len(sys.argv) != 4:
        print('Usage: control_worker.py CONTROL_SOCKET BASELINE BASELINE_SHA256', file=sys.stderr)
        return 2
    path, baseline, expected = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
    require(not path.exists() and path.parent.is_dir(), 'RecoveryRequired', 'Unsafe control socket path')
    worker = ControlWorker(baseline, expected)
    server = AuthenticatedServer(path, worker.handle, control=True, allowed_uid=EVALUATOR)
    try:
        while True:
            time.sleep(3600)
    finally:
        server.close()


if __name__ == '__main__':
    raise SystemExit(main())
