"""Parent-interpreter guard/test runner; NOT an OS sandbox or live proof."""
import builtins
import os
from pathlib import Path
import re
import sqlite3
import sys
import unittest

ROOT = Path('/Users/speed/Documents/Codex/2026-10-19/3e4m-b-4/outputs/governed-recursive-research-ratchet/.claude/worktrees/dev-GRRR-k3j7')
attempts = []

def protected(value):
    if not isinstance(value, (str, bytes, os.PathLike)):
        return False
    value = os.fsdecode(value)
    if value.startswith('file:'):
        value = value[5:].split('?', 1)[0]
    if not value.startswith('/'):
        value = os.path.join(os.getcwd(), value)
    value = '/' + os.path.normpath(value).lstrip('/')
    value = value.lower()
    return value == '/library/grrr' or value.startswith('/library/grrr/')

def deny(operation, value):
    if protected(value):
        attempts.append((operation, os.fsdecode(value)))
        raise PermissionError('Parent source harness forbids protected access')

def wrap(fn, name):
    def guarded(path, *args, **kwargs):
        deny(name, path)
        return fn(path, *args, **kwargs)
    return guarded

for name in ('stat', 'lstat', 'open', 'listdir', 'scandir', 'access', 'readlink'):
    setattr(os, name, wrap(getattr(os, name), 'os.' + name))
builtins.open = wrap(builtins.open, 'builtins.open')
sqlite3.connect = wrap(sqlite3.connect, 'sqlite3.connect')

def audit(event, args):
    if event in ('open', 'os.listdir', 'os.scandir', 'os.remove', 'os.rmdir',
                 'os.rename', 'os.symlink', 'os.link', 'os.chmod', 'os.utime',
                 'sqlite3.connect'):
        for value in args[:2]:
            deny(event, value)
    if event == 'socket.connect':
        sock, address = args
        if sock.family not in (1,):
            raise PermissionError('Source suite cannot connect to IP networks')
        deny(event, address)
    if event == 'subprocess.Popen':
        executable, argv, cwd, env = args
        if any(protected(arg) for arg in argv if isinstance(arg, (str, bytes))):
            raise PermissionError('Protected subprocess argument refused')
        if re.search(r'(^|[-/])(qemu|sudo|launchctl|docker|podman|curl|wget|ssh|osascript)(-|$)', os.fsdecode(executable)):
            raise PermissionError('Not a harmless source-test child')

sys.addaudithook(audit)
sys.path[:0] = [str(ROOT / 'research'), str(ROOT / 'tests')]
def main():
    names = sys.argv[1:]
    if not names or any(not re.fullmatch(r'unit_[a-z0-9_]+', name) for name in names):
        raise SystemExit('Explicit source-only module names required')
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromNames(names))
    print('PARENT_SOURCE_ONLY tests=%d failures=%d errors=%d skipped=%d protected_attempts=%d; guard=parent-interpreter-only; no VM/UID/OS-isolation proof' %
          (result.testsRun, len(result.failures), len(result.errors), len(result.skipped), len(attempts)))
    if attempts:
        print('FORBIDDEN_ATTEMPTS', attempts)
    return int(result.testsRun == 0 or not result.wasSuccessful() or bool(result.skipped) or bool(attempts))

if __name__ == '__main__':
    raise SystemExit(main())
