"""Read-only pinned CommandLineTools runtime identity; run BEFORE parent elevation."""
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys

RUNTIME = Path('/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9')
PYTHON = RUNTIME / 'bin/python3.9'
STDLIB = RUNTIME / 'lib/python3.9'
IDENTITY = '59073b8282cb4333c7719d4eac417c061c82f534bf11873d26bf2b26f7531526'
DATA_LINKS = {
    'lib/python3.9/config-3.9-darwin/libpython3.9.a': '../../../Python3',
    'lib/python3.9/config-3.9-darwin/libpython3.9.dylib': '../../../Python3',
}


def canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True, allow_nan=False).encode()


def check(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def snapshot() -> dict:
    """Bind the entire stdlib inventory plus actual interpreter/framework, without execution.

    The two development-link entries are inventoried but never followed or used
    as runtime entrypoints. Every executable/import path and ancestor is non-link.
    """
    paths = [PYTHON, RUNTIME / 'Python3', STDLIB, *sorted(STDLIB.rglob('*'))]
    ancestors = {parent for path in paths for parent in path.parents}
    for absent in (RUNTIME / 'lib/python39.zip', RUNTIME / 'pyvenv.cfg', RUNTIME / 'bin/pyvenv.cfg'):
        check(not os.path.lexists(absent), 'Unexpected runtime search input')
    result = {}
    for path in sorted(set(paths) | ancestors):
        info = path.lstat()
        check(info.st_uid == 0 and info.st_gid == 0 and info.st_mode & 0o022 == 0,
              'Unsafe runtime ownership/mode')
        listing = subprocess.run(['/bin/ls', '-lde', str(path)], capture_output=True,
                                 check=True, timeout=2, env={'PATH': '/usr/bin:/bin', 'LC_ALL': 'C'}).stdout
        check(bool(listing.split()) and b'+' not in listing.split()[0]
              and len(listing.splitlines()) == 1, 'Runtime ACL present')
        relative = str(path.relative_to(RUNTIME)) if RUNTIME in path.parents else str(path)
        entry = {'mode': stat.S_IMODE(info.st_mode), 'uid': info.st_uid, 'gid': info.st_gid}
        if stat.S_ISLNK(info.st_mode):
            check(relative in DATA_LINKS and os.readlink(path) == DATA_LINKS[relative],
                  'Unexpected runtime symlink')
            entry.update(kind='development-link-not-loaded', target=os.readlink(path))
        elif stat.S_ISDIR(info.st_mode):
            entry['kind'] = 'directory'
        else:
            check(stat.S_ISREG(info.st_mode) and info.st_nlink == 1, 'Runtime file type/link differs')
            entry.update(kind='file', sha256=hashlib.sha256(path.read_bytes()).hexdigest())
        result[relative] = entry
    build = subprocess.run(['/usr/bin/sw_vers', '-buildVersion'], check=True, capture_output=True,
                           timeout=2, env={'PATH': '/usr/bin:/bin'}).stdout.decode().strip()
    return {'version': 1, 'python': str(PYTHON), 'system_build': build, 'entries': result}


def verify_runtime(current: bool = False) -> dict:
    """Match reviewed runtime bytes/metadata and optionally the running interpreter."""
    if current:
        check(sys.executable == str(PYTHON), 'Direct reviewed interpreter required')
    value = snapshot()
    check(hashlib.sha256(canonical(value)).hexdigest() == IDENTITY, 'Runtime/dependency identity changed')
    return {'runtime_identity': IDENTITY, 'python': str(PYTHON), 'root_launch_authorized': False}
