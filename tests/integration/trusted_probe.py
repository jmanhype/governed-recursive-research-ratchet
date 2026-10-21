"""Run as actual non-evaluator service/operator UID; never dispatch a guest."""
import os
from pathlib import Path
import sys
import socket
import tempfile
from common import Failure, call, canonical, require, receive
from trusted_execution import root_record

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
for name in ('executor.sock', 'executor-control.sock'):
    peers = []
    try:
        for _ in range(16):
            conn = socket.socket(socket.AF_UNIX)
            conn.settimeout(2)
            conn.connect(str(root / 'ipc' / name))
            peers.append(conn)  # no payload: pre-auth rejection must still arrive
        denials[name + '-preauth'] = all(receive(conn)['error']['code'] == 'Unauthorized' for conn in peers)
    finally:
        for conn in peers:
            conn.close()
installation = root_record(root / 'runner/qemu-installation.json')
executable = Path(installation['root']) / installation['executable']
try:
    fd = os.open(executable, os.O_WRONLY | os.O_NOFOLLOW)
    os.close(fd)
    denials['qemu-write'] = False
except PermissionError:
    denials['qemu-write'] = True
with tempfile.TemporaryDirectory() as temporary:
    replacement = Path(temporary) / 'replacement'
    replacement.write_bytes(b'not executable')
    try:
        os.replace(replacement, executable)
        denials['qemu-replace'] = False
    except PermissionError:
        denials['qemu-replace'] = True
require(all(denials.values()), 'GateBlocked', 'Host privilege denial not observed')
print(canonical({'uid': os.getuid(), 'denials': denials, 'guest_started': False}).decode())
