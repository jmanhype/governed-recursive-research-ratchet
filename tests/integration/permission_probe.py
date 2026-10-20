"""Run as real runner identity before any VM experiment; no imports of protected code."""
import json
import os
from pathlib import Path
import socket


def main() -> None:
    assert os.getuid() == 321, 'Real runner identity required'
    for name in ('.runtime/evaluator/policy.json', '.runtime/evaluator/ledger.sqlite', 'research/evaluator.py'):
        try:
            Path(name).read_bytes()
        except PermissionError:
            print('PASS denied read:', name)
        else:
            raise AssertionError('Protected read unexpectedly allowed: ' + name)
        assert not os.access(name, os.W_OK), 'Protected write unexpectedly allowed'
    with socket.socket(socket.AF_UNIX) as conn:
        conn.settimeout(2)
        conn.connect('.runtime/ipc/evaluator.sock')
        conn.sendall(b'{"action":"list","role":"operator"}\n')
        result = json.loads(conn.recv(4096))
        assert result['error']['code'] == 'Unauthorized', result
        print('PASS denied kernel-peer impersonation')


if __name__ == '__main__':
    main()
