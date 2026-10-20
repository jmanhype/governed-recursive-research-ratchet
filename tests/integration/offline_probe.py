"""Real service/OS negative probes. Never read or emit credential bytes."""
import json
import os
from pathlib import Path
import sys
import uuid
from common import Failure, call


def main(base: Path, mode: str) -> None:
    if mode == 'protected-paths':
        binding = json.loads((base / 'binding.json').read_bytes())
        paths = [base / 'evaluator/policy.json', base / 'evaluator/license-review.json',
                 Path(binding['operator_home']) / '.ssh', Path(binding['operator_home']) / '.aws',
                 Path(binding['operator_home']) / '.codex/auth.json']
        denied = []
        for path in paths:
            try:
                fd = os.open(path, os.O_RDONLY)
            except (PermissionError, FileNotFoundError):
                denied.append(str(path))
            else:
                os.close(fd)
                raise AssertionError('Runner could open protected path; no contents read')
        for path in (base / 'evaluator/unauthorized', base / 'runner/assets/unauthorized'):
            try:
                fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            except PermissionError:
                continue
            else:
                os.close(fd)
                raise AssertionError('Runner could write protected asset directory')
        print(json.dumps({'denied_open_paths': denied, 'credential_bytes_read': 0}))
        return
    if mode == 'unauthorized-peer':
        request = {'action': 'status', 'run': 'probe'}
        expected = 'Unauthorized'
    else:
        # Root-owned public binding, not payload identity, chooses the pinned variant.
        config = json.loads((base.parent / 'probe-config.json').read_bytes())
        request = {'action': 'dispatch', 'request': {'run': uuid.uuid4().hex,
                   'variant': config['profile_sha256'], 'probe': None},
                   'reservation': uuid.uuid4().hex, 'epoch': 0, 'key': uuid.uuid4().hex}
        expected = 'IntegrityFailure' if mode == 'image' else 'Unavailable'
    try:
        call(base / 'ipc/executor.sock', request, timeout=10)
    except Failure as exc:
        assert exc.record['code'] == expected, exc.record
        print(json.dumps({'expected_failure': exc.record}))
    else:
        raise AssertionError('Unsafe request unexpectedly succeeded')


if __name__ == '__main__':
    main(Path(sys.argv[1]), sys.argv[2])
