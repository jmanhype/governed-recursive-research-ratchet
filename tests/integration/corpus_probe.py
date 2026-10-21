"""Actual non-evaluator host probe for the corpus runtime; never dispatches work."""
import json
import os
from pathlib import Path
import socket
import tempfile

from common import RUNNER, canonical, peer_uid, receive, require, unique_fields


def denied(path: Path, mode: int) -> bool:
    return not os.access(path, mode)


root = Path(__import__('sys').argv[1])
require(os.getuid() not in (0, 320), 'Unauthorized', 'Probe requires a non-evaluator identity')
denials = {
    'evaluator-expectation-read': denied(root/'evaluator/expectation', os.R_OK),
    'evaluator-budget-read': denied(root/'evaluator/budget.sqlite', os.R_OK),
    'trusted-execution-write': denied(root/'code/trusted_execution.py', os.W_OK),
    'runner-config-write': denied(root/'runner/config.json', os.W_OK),
}
for name in ('executor.sock', 'executor-control.sock'):
    with socket.socket(socket.AF_UNIX) as conn:
        conn.settimeout(2); conn.connect(str(root/'ipc'/name))
        require(peer_uid(conn) == RUNNER, 'Unauthorized', 'Corpus server identity differs')
        conn.sendall(canonical({'action': 'status', 'run': 'probe'})+b'\n')
        response = receive(conn)
        denials[name+'-peer-role'] = response.get('error', {}).get('code') == 'Unauthorized'
record_path = root/'runner/qemu-installation.json'
record_info = record_path.lstat()
require(record_info.st_uid == 0 and record_info.st_gid == 0
        and record_info.st_nlink == 1 and not record_path.is_symlink()
        and record_info.st_mode & 0o222 == 0, 'Unauthorized', 'QEMU record metadata differs')
installation = json.loads(record_path.read_bytes(), object_pairs_hook=unique_fields)
executable = Path(installation['root'])/installation['executable']
denials['qemu-write'] = denied(executable, os.W_OK)
with tempfile.TemporaryDirectory() as folder:
    replacement = Path(folder)/'replacement'; replacement.write_bytes(b'not-executable')
    try:
        os.replace(replacement, executable); denials['qemu-replace'] = False
    except PermissionError:
        denials['qemu-replace'] = True
require(all(denials.values()), 'GateBlocked', 'Corpus host privilege denial not observed')
print(canonical({'uid': os.getuid(), 'denials': denials, 'guest_started': False}).decode())
