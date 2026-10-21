# Read-only evidence collection

At story HEAD 4143b9c before changes, installed conservative-genesis inspected as
ordinary UID; no root identity or QEMU invocation. No copy/build of database.

Commands:
```
/usr/bin/python3 -I -S -B scripts/reconcile-installed-accounting
/usr/bin/python3 -I -S -B scripts/reconcile-installed-accounting --markdown
/usr/bin/python3 -B -m unittest discover -s tests -p unit_installed_reconciliation.py
/opt/homebrew/bin/python3 -B -m unittest discover -s tests -p unit_installed_reconciliation.py
pvg verify scripts/reconcile-installed-accounting tests/unit_installed_reconciliation.py --include-tests
```

Output redirected to report.json, REPORT.md, system-tests.txt, homebrew-tests.txt
and pvg.txt respectively. JSON and Markdown are separate read-only observations;
free-space measurements may differ slightly. Hashes before/after match installed
DB/receipt/active; exact inode/device matches parent binding. SQLite uses
`mode=ro&immutable=1` plus query_only; no journal/temporary store is created.

Full suite NOT run: its preparation-builder tests require >=15.35 GB free and
create local database copies. Current ~12.95 GB is below that preparation floor
and the 15 GB execution floor. Only the three scoped no-copy read-only tests were
run under both Python installations (3/3 each). pvg scans the .py test; the
extensionless report script was independently executed.

The 48 reservation/48 observation/8 stop counts cover all preserved attempts,
not merely the accepted exports' 5/5/4 plus six unmapped reservations. Event-key
rows and exact sources are included for independent matching. Sums are explicitly
non-authoritative; without identity/stage/interval reconciliation they cannot
be imported as charges or used to release the full admission encumbrances.
