"""Isolated identity entry: only root-controlled staged code enters sys.path."""
import os
from pathlib import Path
import runpy
import sys

root = Path(__file__).absolute().parent
if not (sys.flags.isolated and sys.flags.no_site and sys.flags.dont_write_bytecode):
    raise SystemExit('Isolated Python required')
if root.is_symlink() or root.stat().st_uid != 0 or root.stat().st_mode & 0o022:
    raise SystemExit('Root-controlled code directory required')
if sys.argv[1] not in ('trusted_execution.py', 'trusted_observation.py', 'trusted_probe.py'):
    raise SystemExit('Unregistered identity program')
for path in root.iterdir():
    if path.is_symlink() or not path.is_file() or path.stat().st_uid != 0 or path.stat().st_mode & 0o222:
        raise SystemExit('Code snapshot changed')
target = root / sys.argv[1]
sys.path.insert(0, str(root))
sys.argv = [str(target), *sys.argv[2:]]
runpy.run_path(str(target), run_name='__main__')
