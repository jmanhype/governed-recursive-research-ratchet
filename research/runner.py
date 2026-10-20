"""Approved standalone grammar and accessible snapshot projections."""
import argparse
import json
from pathlib import Path
import uuid
from common import Failure, call


def parser() -> argparse.ArgumentParser:
    cli = argparse.ArgumentParser(description='Bounded synthetic walkthrough only. Inspect: status/evidence. Emergency stop: stop RUN. Recovery unavailable.')
    commands = cli.add_subparsers(dest='action', required=True)
    start = commands.add_parser('start')
    for flag in ('policy', 'challenge', 'variant'):
        start.add_argument('--' + flag, required=True)
    for action in ('status', 'review', 'evidence', 'decide', 'stop', 'recover'):
        child = commands.add_parser(action)
        child.add_argument('run')
        if action == 'evidence':
            child.add_argument('--level', choices=['decision', 'technical', 'audit'], required=True)
            child.add_argument('--format', choices=['text', 'markdown', 'json'], required=True)
        if action == 'decide':
            child.add_argument('--action', dest='decision', choices=['approve-evidence', 'admit-contract', 'reject', 'needs-evidence', 'request-change'], required=True)
            child.add_argument('--target', required=True)
        if action == 'stop':
            child.add_argument('--key')
            child.add_argument('--reason')
        if action == 'recover':
            child.add_argument('--plan')
            child.add_argument('--execute', action='store_true')
    return cli


def projection(snapshot: dict, format: str, level: str) -> str:
    report = snapshot['events'][-1]['event']
    if format == 'json':
        return json.dumps(snapshot if level == 'audit' else dict(report, snapshot_id=snapshot['snapshot_id']), sort_keys=True)
    lines = ['Run: ' + report['run'], 'Snapshot: ' + snapshot['snapshot_id'],
             'Candidate: ' + report['candidate'], 'Evaluator: ' + report['evaluator'],
             'Policy: ' + report['policy'], 'Execution: ' + report['execution'],
             'Assertion: ' + report['assertion'], 'Verified: BLOCKED; admission: BLOCKED',
             'Scope: ' + report['scope'], 'Next: ' + report['next_action']]
    if level != 'decision':
        lines += [name + ': ' + gate['state'] for name, gate in report['gates'].items()]
    return ('# Bounded challenge evidence\n\n' if format == 'markdown' else '') + '\n'.join(lines)


def main(root: Path) -> int:
    args = vars(parser().parse_args())
    format = args.pop('format', 'text')
    level = args.pop('level', 'decision')
    request = {key: value for key, value in args.items() if value is not None}
    if request['action'] == 'start':
        request.update(key=uuid.uuid4().hex, epoch=0)
    try:
        result = call(root / '.runtime/ipc/evaluator.sock', request)
        if request['action'] == 'evidence':
            print(projection(result, format, level))
        else:
            print(json.dumps(result, sort_keys=True))
        return 3 if result.get('assertion') == 'fail' or result.get('execution') == 'error' else 0
    except Failure as exc:
        print(json.dumps({'error': exc.record}, sort_keys=True))
        return 3
