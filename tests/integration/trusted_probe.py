"""Run as actual non-evaluator service/operator UID; never dispatch a guest."""
import os
from pathlib import Path
import sys
from common import Failure, call, canonical, require

root = Path(sys.argv[1])
require(os.getuid() not in (0, 320), 'Unauthorized', 'Probe requires non-evaluator identity')
denials = {}
for relative in ('evaluator/expectation', 'evaluator/budget.sqlite'):
    try:
        (root / relative).read_bytes()
        denials[relative] = False
    except PermissionError:
        denials[relative] = True
try:
    call(root / 'ipc/executor.sock', {'action': 'status', 'run': 'probe'})
    denials['peer_role'] = False
except Failure as exc:
    denials['peer_role'] = exc.record['code'] == 'Unauthorized'
for relative in ('code/trusted_execution.py', 'runner/config.json'):
    try:
        fd = os.open(root / relative, os.O_WRONLY | os.O_NOFOLLOW)
        os.close(fd)
        denials[relative] = False
    except PermissionError:
        denials[relative] = True
require(all(denials.values()), 'GateBlocked', 'Host privilege denial not observed')
print(canonical({'uid': os.getuid(), 'denials': denials, 'guest_started': False}).decode())
