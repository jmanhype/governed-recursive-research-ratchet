#!/usr/bin/env python3
"""Actual operator/runner identity probes against dedicated control sockets."""
from __future__ import annotations
import json
import os
from pathlib import Path
import sys
from common import EVALUATOR, Failure
from trusted_transport import control_call


def main() -> int:
    modes = ('authorized-operator', 'denied-runner', 'denied-watchdog-operator',
             'unavailable-control')
    if len(sys.argv) != 3 or sys.argv[2] not in modes:
        print('Usage: safe_stop_probe.py RUNTIME MODE', file=sys.stderr)
        return 2
    runtime, mode = Path(sys.argv[1]).absolute(), sys.argv[2]
    ipc = runtime / 'ipc'
    if mode == 'authorized-operator':
        path, request = ipc / 'operator-control.sock', {
            'action': 'stop', 'run': 'run-operator', 'key': 'operator-stop',
            'reason': 'urgent-host-control-proof'}
    elif mode == 'denied-runner':
        path, request = ipc / 'operator-control.sock', {
            'action': 'stop', 'run': 'run-operator', 'key': 'forged-operator'}
    elif mode == 'denied-watchdog-operator':
        path, request = ipc / 'watchdog-control.sock', {
            'action': 'stop', 'run': 'run-watchdog', 'key': 'forged-watchdog'}
    else:
        path, request = ipc / 'operator-control.sock', {
            'action': 'stop', 'run': 'run-operator', 'key': 'post-integration-stop'}
    try:
        result = control_call(path, request, expected_uid=EVALUATOR, timeout=5)
        outcome = {'mode': mode, 'uid': os.getuid(), 'denied': False, 'result': result}
        code = 0 if mode == 'authorized-operator' else 1
    except Failure as exc:
        outcome = {'mode': mode, 'uid': os.getuid(), 'denied': True, 'error': exc.record}
        expected = mode != 'authorized-operator'
        if mode == 'unavailable-control':
            expected = exc.record['code'] == 'Unavailable'
        code = 0 if expected else 1
    print(json.dumps(outcome, sort_keys=True))
    return code


if __name__ == '__main__':
    raise SystemExit(main())
