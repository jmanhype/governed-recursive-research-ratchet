"""Exact-target operator driver: install once or independently verify only."""
import hashlib
import json
import os
from pathlib import Path
import stat
import sys

assert os.getuid() == 0 and os.geteuid() == 0, 'root required'
assert sys.flags.isolated and sys.flags.no_site and sys.dont_write_bytecode, 'isolated flags required'
assert sys.version_info[:2] == (3, 9), 'reviewed system Python 3.9 required'
assert sys.executable == '/Applications/Xcode.app/Contents/Developer/usr/bin/python3', 'system interpreter differs'
assert sys.argv[1:] in (['--install'], ['--verify']), 'explicit single action required'
STAGED = Path('/Library/GRRR/bootstrap/recovery-v4')
BASE = Path('/Library/GRRR/accounting-poc2')
HASHES = {
    'accounting_recovery_v4.py': '79bce91b4a5054bc2e59e05e9d3e55f924715f2ee44f34a61cc716b7a72c79d7',
    'accounting_recovery_planner_v4.py': '3a2c6fa896ba59f864af215de3b55fe88bb83544a87fe6c425c43a506e9aa61c',
    'records/plan.json': '4603b443783e8bfc91f6a1c1c408f54cd8f3f073aaf35f14af9278d01d8f0953',
    'records/review.json': '1bcb3351e435ff476c35e5df713b6facd519a9fa96d0670db9f2df13388ea2dc',
    'records/authorization.json': '5d1deb5fe0c26e378233c0a1fa1c1104fa60ce8aaee38673b2fd4efa9f6e026e',
}
for directory in (Path('/Library'), Path('/Library/GRRR'), STAGED.parent, STAGED, STAGED / 'records', BASE):
    info = directory.lstat()
    assert stat.S_ISDIR(info.st_mode) and info.st_uid == 0 and not (info.st_mode & 0o022)
for name, expected in HASHES.items():
    path = STAGED / name
    info = path.lstat()
    assert stat.S_ISREG(info.st_mode) and info.st_uid == 0 and stat.S_IMODE(info.st_mode) == 0o444
    assert info.st_nlink == 1 and hashlib.sha256(path.read_bytes()).hexdigest() == expected, name
sys.path.insert(0, str(STAGED))
import accounting_recovery_v4 as module
assert module.__file__ == str(STAGED / 'accounting_recovery_v4.py')
plan = json.loads((STAGED / 'records/plan.json').read_bytes())
review = json.loads((STAGED / 'records/review.json').read_bytes())
authorization = json.loads((STAGED / 'records/authorization.json').read_bytes())
module.approval(plan, review, authorization)
before = module.snapshot(BASE)
print('ACTION', sys.argv[1], flush=True)
print('EXACT_HASHES', json.dumps(HASHES, sort_keys=True), flush=True)
print('PRE_STATE', json.dumps(before['inventory']['tables']['state']), flush=True)
if sys.argv[1] == '--install':
    assert module.canonical(before) == module.canonical(plan['baseline']), 'live baseline drift'
    result = module.apply_install(BASE, plan, review, authorization, privileged=True)
else:
    result = module.verify(BASE)
after = module.snapshot(BASE)
module.unchanged(plan['baseline']['inventory'], after['inventory'])
assert after['active_hex'] == plan['baseline']['active_hex']
assert after['metadata'] == plan['baseline']['metadata']
assert result['outcome'] == 'published-durable'
assert result['receipt']['historical_unknowns'] == 'unresolved'
assert result['receipt']['spendable'] == 'unknown'
print('OUTCOME', result['outcome'], flush=True)
print('POST_STATE', json.dumps(after['inventory']['tables']['state']), flush=True)
print('ACTIVE_BYTES_AND_METADATA_UNCHANGED', True, flush=True)
print('SCHEMA_HISTORY_HOLDS_UNKNOWNS_UNCHANGED', True, flush=True)
print('RECEIPT', module.canonical(result['receipt']).decode(), flush=True)
for record in sorted((BASE / 'recovery-v4').iterdir()):
    print('RECORD', record.name, module.digest(module.read(record)), flush=True)
