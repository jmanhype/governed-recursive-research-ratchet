import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import stat


CAPTURE = Path('/Users/speed/Documents/Codex/2026-10-19/3e4m-b-4/outputs/governed-recursive-research-ratchet/.claude/worktrees/dev-GRRR-z3w9/docs/evidence/spendability/stage-d/CAPTURE.json')
ACTIVE = Path('/Library/GRRR/accounting-poc2/active.json')
LOCK = Path('/Library/GRRR/accounting-poc2/launch.lock')
IDENTITY = ('st_dev', 'st_ino', 'st_mode', 'st_uid', 'st_gid', 'st_nlink')


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def timestamp(value):
    return dt.datetime.fromisoformat(value.replace('Z', '+00:00'))


def stable_read(path):
    before = path.lstat()
    descriptor = os.open(str(path), os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0)
                         | getattr(os, 'O_NONBLOCK', 0))
    try:
        opened = os.fstat(descriptor)
        chunks = []
        while True:
            chunk = os.read(descriptor, 1024 * 1024)
            if not chunk:
                break
            chunks.append(chunk)
        final = os.fstat(descriptor)
    finally:
        os.close(descriptor)
    after = path.lstat()
    if not stat.S_ISREG(opened.st_mode):
        raise RuntimeError('non-regular file: ' + str(path))
    if not all(getattr(before, name) == getattr(opened, name) == getattr(final, name)
               == getattr(after, name) for name in IDENTITY):
        raise RuntimeError('path/descriptor identity differs: ' + str(path))
    raw = b''.join(chunks)
    info = {
        'sha256': digest(raw), 'device': opened.st_dev, 'inode': opened.st_ino,
        'mode': stat.S_IMODE(opened.st_mode), 'uid': opened.st_uid,
        'gid': opened.st_gid, 'nlink': opened.st_nlink, 'size': opened.st_size,
    }
    return raw, info


capture_raw, _ = stable_read(CAPTURE)
capture_hash = digest(capture_raw)
capture = json.loads(capture_raw)
observed_at = dt.datetime.now(dt.timezone.utc).isoformat(timespec='microseconds').replace('+00:00', 'Z')
capture_completed = capture['completed_at']
if not timestamp(observed_at) > timestamp(capture_completed):
    raise RuntimeError('postcapture observation is not after capture completion')

active_raw, active_observed = stable_read(ACTIVE)
lock_raw, lock_observed = stable_read(LOCK)
database = Path(capture['database_path'])
database_raw, database_observed = stable_read(database)

active_expected = dict(
    capture['active']['descriptor_identity'],
    sha256=capture['active']['sha256'],
)
lock_expected = dict(
    capture['lock_file']['path_released'],
    sha256=capture['lock_file']['sha256'],
)
database_expected = dict(
    capture['raw_schema']['database'],
    sha256=capture['raw_schema']['database']['sha256'],
)


def matches(expected, observed):
    keys = ('sha256', 'device', 'inode')
    return all(expected[name] == observed[name] for name in keys)


checks = {
    'active': matches(active_expected, active_observed),
    'lock': matches(lock_expected, lock_observed),
    'database': matches(database_expected, database_observed),
}
result = {
    'schema_version': 1,
    'kind': 'GRRR-z3w9 Stage D postcapture immutable identity verification',
    'capture_path': str(CAPTURE),
    'capture_sha256': capture_hash,
    'capture_completed_at': capture_completed,
    'observed_at': observed_at,
    'chronology_after_capture': timestamp(observed_at) > timestamp(capture_completed),
    'expected': {'active': active_expected, 'lock': lock_expected,
                 'database': database_expected},
    'observed': {'active': active_observed, 'lock': lock_observed,
                 'database': database_observed},
    'checks': checks,
    'all_immutable': all(checks.values()),
    'database_sha256': database_observed['sha256'],
    'authority': {
        'protected_access': False, 'write': False, 'reconcile': False,
        'replay': False, 'promotion': False, 'admission': False,
        'merge': False, 'push': False,
    },
}
print(json.dumps(result, sort_keys=True, indent=2))
raise SystemExit(0 if all(checks.values()) else 1)
