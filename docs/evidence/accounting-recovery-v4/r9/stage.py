"""Operator-only staging. No accounting write or recovery installation."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import sys

assert os.geteuid() == 0 and os.getuid() == 0
assert sys.flags.isolated and sys.flags.no_site and sys.dont_write_bytecode
SOURCE = Path('/private/tmp/grrr-recovery-v4-r9-source')
DST = Path('/Library/GRRR/bootstrap/recovery-v4')
EXPECTED = {
    'accounting_recovery_v4.py': '79bce91b4a5054bc2e59e05e9d3e55f924715f2ee44f34a61cc716b7a72c79d7',
    'accounting_recovery_planner_v4.py': '3a2c6fa896ba59f864af215de3b55fe88bb83544a87fe6c425c43a506e9aa61c',
}

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def root_directory(path):
    info = path.lstat()
    assert stat.S_ISDIR(info.st_mode) and info.st_uid == 0
    assert not (stat.S_IMODE(info.st_mode) & 0o022)

for parent in (Path('/Library'), Path('/Library/GRRR'), DST.parent, DST, DST / 'records'):
    root_directory(parent)
source = {name: (SOURCE / name).read_bytes() for name in EXPECTED}
assert {name: sha(raw) for name, raw in source.items()} == EXPECTED
history = DST.parent / 'recovery-v4-history'
if not history.exists():
    history.mkdir(mode=0o755)
root_directory(history)
archive = history / 'rev8-4db1623-f01aa240'
assert not archive.exists(), 'rev8 already archived; inspect instead of restaging'
shutil.copytree(DST, archive)

def publish(path, raw):
    pending = path.with_name(path.name + '.r9-pending')
    fd = os.open(pending, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    try:
        with os.fdopen(fd, 'wb', closefd=False) as out:
            out.write(raw)
            out.flush()
        os.fchmod(fd, 0o444)
        os.fsync(fd)
    finally:
        os.close(fd)
    os.replace(pending, path)
    directory = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(directory)
    finally:
        os.close(directory)

for name, raw in source.items():
    publish(DST / name, raw)
sys.path.insert(0, str(DST))
from accounting_recovery_planner_v4 import build
from accounting_recovery_v4 import approval, canonical
records = build()
approval(records['plan'], records['review'], records['authorization'])
inv = records['plan']['baseline']['inventory']
assert inv['tables']['state']['rows'] == [[['i', 1], ['i', 1], ['i', 1]]]
assert not (Path('/Library/GRRR/accounting-poc2') / 'recovery-v4').exists()
assert records['plan']['sources'] == EXPECTED
for name, record in records.items():
    publish(DST / 'records' / (name + '.json'), canonical(record))
manifest = dict(EXPECTED)
for name in ('plan', 'review', 'authorization'):
    manifest['records/' + name + '.json'] = sha(canonical(records[name]))
body = ['# Recovery v4 exact review packet, r9\n',
        '\nPrepared for review; not independent approval or execution proof.\n',
        '\nAction: release-v4-stop-retain-unknowns. No reconciliation or replay.\n',
        '\n## Exact staged hashes\n']
for name, value in sorted(manifest.items()):
    body.append('- `%s`: `%s`\n' % (name, value))
body.append('\n## Exact baseline\n```json\n' + canonical(records['plan']['baseline']).decode() + '\n```\n')
for name, raw in source.items():
    body.append('\n## %s\n```python\n%s\n```\n' % (name, raw.decode()))
publish(DST / 'packet-r9.md', ''.join(body).encode())
print(json.dumps({'outcome': 'staged-not-installed', 'archive': str(archive),
                  'hashes': manifest, 'state': inv['tables']['state'],
                  'table_counts': {key: len(value['rows']) for key, value in inv['tables'].items()}},
                 sort_keys=True))
