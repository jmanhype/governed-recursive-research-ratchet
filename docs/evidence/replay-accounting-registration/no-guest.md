# GRRR-43i8 registration-only verification

> Historical pre-install test evidence. The blocked/not-run installation status
> below is superseded by [completed-install.md](completed-install.md).
> Recovery/replay authorization is still absent; original measurements remain unchanged.

Status: implementation WIP, BLOCKED for privileged ACs; not delivered.
Tested source tree: `8f90d35c9008478c4258f07c171442e84de11235`.
No protected installation/mutation, root/sudo, stop release, guest/VM/QEMU,
independent replay, promotion, admission or push was performed.

## PROOF

Commands ran from `.claude/worktrees/dev-GRRR-43i8` on 2026-10-23.

| Command | Result |
|---|---|
| `/usr/bin/python3 -m unittest discover -s tests -p unit_replay_accounting_registration.py` | Python 3.9.6: 23 tests, 0 failures, 0 errors, 0 skipped; 0.923s; OK |
| `/opt/homebrew/bin/python3 -m unittest discover -s tests -p unit_replay_accounting_registration.py` | Python 3.14.3: 23 tests, 0 failures, 0 errors, 0 skipped; 0.860s; OK |
| `/usr/bin/python3 -m unittest discover -s tests -p 'unit_*.py'` | 221 tests, 0 failures, 0 errors, 0 skipped; 20.915s; OK |
| `/opt/homebrew/bin/python3 -m unittest discover -s tests -p 'unit_*.py'` | 221 tests, 0 failures, 0 errors, 0 skipped; 20.461s; OK |
| `/usr/bin/python3 -m compileall -q research tests/unit_replay_accounting_registration.py scripts/replay-root-prepare` | exit 0 |
| `/opt/homebrew/bin/python3 -m compileall -q research tests/unit_replay_accounting_registration.py scripts/replay-root-prepare` | exit 0 |
| `pvg verify research/accounting_registration.py research/budget.py research/persistent_budget.py tests/unit_replay_accounting_registration.py scripts/replay-root-prepare docs/REPLAY-ACCOUNTING-REGISTRATION.md --format=text` | PASS: 4 files scanned, 0 issues; extensionless script and Markdown not scanned |
| `git diff --check` and `git diff --cached --check` | exit 0 |

Full test stdout/stderr captures: `/tmp/GRRR-43i8-final-full-py39.log` and
`/tmp/GRRR-43i8-final-full-homebrew.log`. Both end with `Ran 221 tests` / `OK`.
No final suite warnings. These are no-guest units, not protected integration.

Coverage command (stdlib trace; not branch coverage):

```sh
/usr/bin/python3 -m trace --count --missing --summary \
  --file /tmp/GRRR-43i8-trace-final \
  --coverdir /tmp/GRRR-43i8-coverage-final \
  --module unittest discover -s tests -p unit_replay_accounting_registration.py
```

23 tests passed in 1.285s. Reported executable-line coverage: registration module
90% (350 lines), Budget 86% (162 lines), PersistentBudget 97% (91 lines), tests
99% (383 lines). Coverage output `/tmp/GRRR-43i8-coverage-final.log`.
The Homebrew interpreter lacks third-party `coverage`; no dependency was installed.
An initial trace without `--missing` reports a misleading executed-only denominator;
that result is explicitly discarded and is not the coverage claim above.

Source SHA256 values:

```text
74975c0da25303f05a7701008d87a22be7d8e6ed029bdee619f626a0d6ee10ab  research/accounting_registration.py
576b77e2bcc1782ab5cdc8fad80ad7b550e110f2f617280982b93363e0974a23  research/budget.py
d658334fc35228cac1b70c8e9e0e1c173bff90ca51d5470dbfbfa6da463e606b  research/persistent_budget.py
1285f6bf5f1e1973c5539437e99021b85c872b7452aa93564037ba3f59a41183  scripts/replay-root-prepare
```

## AC disposition

| AC | Implementation/test support | Remaining blocker |
|---|---|---|
| 1 | Reviewed proposal; exact pinned parent-observed identities; read-only snapshot code captures all raw rows and unknowns | Actual protected inventory/provenance not collected by worker; implementation review pending |
| 2 | Root-only, exclusive, receipt-first/atomic binding source; temporary fixture byte/inode preservation tests | Protected registration NOT RUN; no integration proof |
| 3 | Exact existing shared ceilings; POC-only replay; no DB writes/new store/reset; full uncertain holds retained | Independent review of implementation remains required |
| 4 | No recovery command; stop preserved; changed stopped DB rejects verification; duplicate/zero requests refuse | Recovery NOT AUTHORIZED/NOT RUN; separate decision and review required |
| 5 | Read-only baseline/postflight source; ACL/mode/link/identity/tamper/partial tests, fault injection before/after activation | Protected before/after verification NOT RUN |
| 6 | Legacy denies replay; registered store remains frozen/stopped; no dispatch authority added | Actual replay remains blocked behind registration/recovery and all replay gates |

## LEARNINGS

- A profile registration need not migrate SQLite: only the root binding changes;
  the exact stopped database, original binding bytes and all unknown holds remain.
- Idempotent duplicate reservation lookup previously preceded stop checking;
  fail-closed ordering must deny it before returning an old reservation.
- Updating Budget requires refreshing the checkout smoke launcher's source pin;
  that does not update or approve its installed closure.
- Legacy `PROFILES` is consumed by fixtures/clients; retain that three-profile API
  and add explicit `REGISTERED_PROFILES` rather than changing legacy semantics.
- Unit root emulation must restore original directory modes, not assume 0555:
  Python 3.14 Path.replace uses the patched os.replace where Python 3.9 differs.

Initial fixture permission errors, source-pin/legacy export regression failures,
and the Python 3.14 fixture-mode mismatch were fixed before the final clean runs.
Future parent commands and remaining privileged-parent exclusion obligation are
in `docs/REPLAY-ACCOUNTING-REGISTRATION.md`. Story remains in_progress.
