# GRRR-43i8 frozen-runtime review correction

> Historical pre-install correction evidence. Installation/postflight subsequently
> passed: see [completed-install.md](completed-install.md). Recovery and replay
> remain denied/not-run. Original review state and measurements below are retained.

Implementation commit: `8820a6ba5ebaa5b503f3242b2f0c006df8a2ba2c`.
This supersedes the earlier runtime-freeze claim at `8f90d35`; the independent
review correctly found inherited mutation paths unguarded. Story remains
in_progress, not delivered. No protected operation or push was performed.

## PROOF

Version 2 opens `mode=ro`, bypassing chmod/schema initialization. A shared dynamic
guard runs before reserve, meter, settle, overhead and halt, including explicit
base-class calls. Every profile is frozen. Legacy handles check the current
binding and any partial registration output before mutation; legacy stopped
settlement/meter/overhead behavior is preserved before registration. Persistent
connection/cursor authorizers refresh before all SQL execution entrypoints so
already-prepared statements cannot retain a stale authorization decision.

Regressions assert refusal with unchanged DB bytes/inode and unchanged pending
holds for every mutator and all profiles, direct inherited calls, stale legacy
handles and cursors, duplicate metering/requests, zero reservations, and partial
registration. SQLite execute/executemany/executescript are also exercised. The
independent installer and baseline checks were not changed.

Commands from the story worktree; source tree corresponds exactly to the commit
above (commit changes no source bytes during final testing):

| Command | Result |
|---|---|
| `/usr/bin/python3 -m unittest discover -s tests -p unit_replay_accounting_registration.py` | 27 tests, 0 failures/errors/skips; 1.289s; OK |
| `/opt/homebrew/bin/python3 -m unittest discover -s tests -p unit_replay_accounting_registration.py` | 27 tests, 0 failures/errors/skips; 1.236s; OK |
| `/usr/bin/python3 -m unittest discover -s tests -p 'unit_*.py'` | 225 tests, 0 failures/errors/skips; 21.392s; OK |
| `/opt/homebrew/bin/python3 -m unittest discover -s tests -p 'unit_*.py'` | 225 tests, 0 failures/errors/skips; 20.981s; OK |
| `/usr/bin/python3 -m compileall -q research tests/unit_replay_accounting_registration.py scripts/replay-root-prepare` | exit 0 |
| `/opt/homebrew/bin/python3 -m compileall -q research tests/unit_replay_accounting_registration.py scripts/replay-root-prepare` | exit 0 |
| `pvg verify research/budget.py research/persistent_budget.py tests/unit_replay_accounting_registration.py scripts/replay-root-prepare docs/REPLAY-ACCOUNTING-REGISTRATION.md --format=text` | PASS, 3 Python files scanned, 0 issues; script/Markdown excluded by scanner |
| `git diff --check` and `git diff --cached --check` | exit 0 |

Interpreters: `/usr/bin/python3` 3.9.6, `/opt/homebrew/bin/python3` 3.14.3.
Full logs: `/tmp/GRRR-43i8-freeze-full-py39.log` and
`/tmp/GRRR-43i8-freeze-full-homebrew.log`. No final test warnings.

Coverage command:

```sh
/usr/bin/python3 -m trace --count --missing --summary \
  --file /tmp/GRRR-43i8-freeze-trace \
  --coverdir /tmp/GRRR-43i8-freeze-coverage \
  --module unittest discover -s tests -p unit_replay_accounting_registration.py
```

27 passed, 1.737s. Reported line coverage (not branch coverage): Budget 91%
(175 executable lines), PersistentBudget 97% (139), registration 90% (350), tests
99% (472). Output `/tmp/GRRR-43i8-freeze-coverage.log`.

Current source hashes:

```text
41548c9f1c9f8f58e48587deaf56cd236fa78cc5716e799da9d678ab6b95b500  research/budget.py
107602f75dc33e707639fa39a25d974511a1f0d28d8631a9ac36174bf8ed0c38  research/persistent_budget.py
fb0828433d35fe7f96e46d19a127a32b19104ab53113f4929be30fa3d441ca37  scripts/replay-root-prepare
```

## LEARNINGS

- The initial implementation checked reserve only; inherited settlement could
  release a hold. A freeze must protect every mutation and initialization path.
- SQLite `mode=ro` provides an additional engine boundary for newly opened frozen
  handles; stale legacy handles still require current binding checks.
- A failing regression demonstrated Python 3.9 reusing the previous SQL authorizer
  decision despite `cached_statements=0`. Rearming the authorizer before each
  execution makes the same already-used statement refuse after publication.
- These guards protect trusted runtime entrypoints, not arbitrary evaluator code
  intentionally disabling authorizers or opening another raw database connection.
  Installer quiescence and exclusive privileged-parent coordination remain required.

## nd_contract
status: in_progress

### evidence
- Implementation `8820a6ba5ebaa5b503f3242b2f0c006df8a2ba2c`; focused 27/27 and full 225/225 on both required interpreters.
- Corrected source Budget pin only; no installed closure changed.
- Independent re-review pending. No root/sudo, protected mutation, VM/QEMU, stop release, replay, delivery or push.

### proof
- [x] Runtime mutation freeze regression coverage across profiles, inherited APIs and stale handles; bytes/inode/holds unchanged.
- [x] Legacy behavior and full no-guest suites retained.
- [ ] AC2/5 protected registration/integration: BLOCKED, not-run.
- [ ] AC4 recovery: BLOCKED, not-authorized, not-run.
- [ ] Actual independent replay: BLOCKED, not-run.
