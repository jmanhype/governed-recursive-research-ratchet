"""Retain real source-only test outputs; never a capstone/installed verdict."""
from pathlib import Path
import hashlib
import json
import re
import subprocess
import time

ROOT = Path('/Users/speed/Documents/Codex/2026-10-19/3e4m-b-4/outputs/governed-recursive-research-ratchet')
WORK = ROOT / '.claude/worktrees/dev-GRRR-k3j7'
OUT = ROOT / '.git/paivot/wip/GRRR-k3j7' / ('current-tests-' + str(time.time_ns()))
OUT.mkdir(parents=True)
modules = ['unit_capstone_contract','unit_capstone_peer','unit_capstone_journal',
           'unit_durable_evidence','unit_capstone_backend_contract',
           'unit_capstone_backend_launch','unit_capstone_backend_review','unit_capstone_backend_composition',
           'unit_capstone_backend_index','unit_capstone_installation_record']
runtimes = ['/opt/homebrew/bin/python3','/Users/speed/miniconda3/bin/python3',
 '/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/bin/python3.9']
rows = []
for index, runtime in enumerate(runtimes):
    cmd = [runtime,'-B','/tmp/grrr-k3j7-guarded-source-suite-20261104.py'] + modules
    p = subprocess.run(cmd,cwd=WORK,capture_output=True,timeout=120)
    stem = 'python-' + str(index)
    (OUT/(stem+'.stdout')).write_bytes(p.stdout)
    (OUT/(stem+'.stderr')).write_bytes(p.stderr)
    match = re.search(rb'PARENT_SOURCE_ONLY tests=(\d+) failures=0 errors=0 skipped=0 protected_attempts=0;',p.stdout)
    row = dict(command=cmd,returncode=p.returncode,tests=int(match[1]) if match else None,
               stdout_sha256=hashlib.sha256(p.stdout).hexdigest(),stderr_sha256=hashlib.sha256(p.stderr).hexdigest())
    rows.append(row)
    print(json.dumps(row),flush=True)
    if p.returncode != 0 or match is None or row['tests'] == 0:
        break
# Explicit mandatory suite entrypoint is exercised separately; guard runs above
# inspect source effects but do not turn fixture identities into live authority.
cmd = [runtimes[0],'-B','tests/unit_capstone_backend_suite.py']
p = subprocess.run(cmd,cwd=WORK,capture_output=True,timeout=120)
(OUT/'entrypoint.stdout').write_bytes(p.stdout)
(OUT/'entrypoint.stderr').write_bytes(p.stderr)
match = re.search(rb'SOURCE_ONLY BACKEND_WIP tests=(\d+) failures=0 errors=0 skipped=0;',p.stdout)
rows.append(dict(command=cmd,returncode=p.returncode,tests=int(match[1]) if match else None,
    stdout_sha256=hashlib.sha256(p.stdout).hexdigest(),stderr_sha256=hashlib.sha256(p.stderr).hexdigest()))
files = ['research/capstone_backend_contract.py','tests/unit_capstone_backend_contract.py',
         'research/capstone_launch.py','research/capstone_review.py','research/capstone_review_service.py',
         'research/capstone_backend_schema.py','research/capstone_backend_index.py',
         'tests/unit_capstone_backend_index.py','tests/unit_capstone_backend_review.py',
         'tests/unit_capstone_backend_launch.py','tests/unit_capstone_backend_composition.py',
         'tests/unit_capstone_backend_suite.py','research/capstone_installation_record.py',
         'tests/unit_capstone_installation_record.py']
receipt = dict(source_only=True,installed_qualification=False,vm_execution=False,
    base=subprocess.check_output(['git','rev-parse','HEAD'],cwd=WORK).decode().strip(),runs=rows,
    files=[dict(path=name,sha256=hashlib.sha256((WORK/name).read_bytes()).hexdigest()) for name in files])
(OUT/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('EVIDENCE='+str(OUT),flush=True)
print(json.dumps(rows[-1]),flush=True)
raise SystemExit(int(len(rows)!=4 or any(r['returncode']!=0 or not r['tests'] for r in rows)))
