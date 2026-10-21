import json
import os
from pathlib import Path
import sys

runtime = Path(sys.argv[1]).absolute()
if os.getuid() == 320:
    raise SystemExit('Probe must run as a non-evaluator identity')
denials = {}
for name in ('ledger.sqlite', 'objects'):
    try:
        (runtime / 'evaluator' / name).stat()
        denials[name] = False
    except PermissionError:
        denials[name] = True
try:
    (runtime / 'evaluator' / 'ledger.sqlite').open('rb').close()
    denials['ledger-open'] = False
except OSError:
    denials['ledger-open'] = True
try:
    list((runtime / 'evaluator' / 'objects').iterdir())
    denials['object-list'] = False
except PermissionError:
    denials['object-list'] = True
if not all(denials.values()):
    print(json.dumps({'uid': os.getuid(), 'denials': denials}, sort_keys=True))
    raise SystemExit('non-evaluator filesystem access was not denied')
print(json.dumps({'uid': os.getuid(), 'denials': denials, 'ledger_mutated': False}, sort_keys=True))
