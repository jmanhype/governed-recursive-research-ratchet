import hashlib
import json
import os
from pathlib import Path


capture = json.loads(Path('/private/tmp/grrr-stage-d-capture.json').read_bytes())


def digest(path):
    value = hashlib.sha256()
    with open(path, 'rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            value.update(chunk)
    return value.hexdigest()


active = '/Library/GRRR/accounting-poc2/active.json'
lock = '/Library/GRRR/accounting-poc2/launch.lock'
database = capture['database_path']
checks = {
    'active': digest(active) == capture['active']['sha256'],
    'lock': digest(lock) == capture['lock_file']['sha256'],
    'database': digest(database) == capture['quiescence']['database_sha256'],
    'active_inode': os.stat(active).st_ino == capture['active']['stat']['inode'],
    'lock_inode': os.stat(lock).st_ino == capture['lock_file']['inode'],
    'database_inode': os.stat(database).st_ino == capture['raw_schema']['database']['inode'],
}
result = {
    'schema_version': 1,
    'kind': 'GRRR-z3w9 Stage D postcapture immutable identity verification',
    'all_immutable': all(checks.values()),
    'checks': checks,
    'database_sha256': digest(database),
    'authority': {
        'write': False, 'reconcile': False, 'replay': False,
        'promotion': False, 'admission': False, 'merge': False, 'push': False,
    },
}
print(json.dumps(result, sort_keys=True, indent=2))
raise SystemExit(0 if all(checks.values()) else 1)
