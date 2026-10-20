"""Real evaluator-UID request to separate runner with root-pinned absent VM path."""
import json
import os
from pathlib import Path
import sys
from common import EVALUATOR, PACKETS, Failure, call, canonical, digest


def main() -> None:
    assert os.getuid() == EVALUATOR, 'Real evaluator identity required'
    request = {'action': 'dispatch', 'request': {'run': 'absent-vm-control',
        'variant': digest(canonical(PACKETS['clean'])), 'probe': 'stop'},
        'reservation': 'negative-reservation', 'epoch': 0, 'key': 'absent-vm-control'}
    try:
        call(Path(sys.argv[1]) / 'ipc/executor.sock', request, timeout=5)
    except Failure as exc:
        assert exc.record['code'] == 'Unavailable', exc.record
        assert exc.record['message'] == 'Approved VM executable absent', exc.record
        print(json.dumps({'control': 'absent-vm', 'expected_failure': exc.record}, sort_keys=True))
        return
    raise AssertionError('Absent VM unexpectedly dispatched')


if __name__ == '__main__':
    main()
