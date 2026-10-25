# GRRR-43i8 incremental BLOB review correction

> Historical pre-install correction evidence. The pending-install/re-review state
> below is superseded by [completed-install.md](completed-install.md).
> Recovery-not-run statements below are historical; separately authorized stop-only
> v3 proof is in [the current recovery report](../accounting-recovery/REPORT.md).
> Reconciliation/replay remain denied; original test measurements are unchanged.

Implementation: `2dbf825e93376c6df5b974e339ea7846a9bc9165`.
The second review correctly identified that SQLite incremental BLOB writes bypass
SQL authorizers on stale writable connections. This correction forbids writable
`blobopen` entirely: no accounting operation needs it. Denial precedes native API
lookup for every table/column, database name, profile, and registration state.
Only literal `readonly=True` is accepted; native read-only access is preserved.
Python 3.9 lacks native blobopen and explicitly raises sqlite3.NotSupportedError
for read-only requests; writable requests still refuse on that interpreter.

## PROOF

Commands from story worktree at the implementation SHA above:

| Command | Result |
|---|---|
| `/usr/bin/python3 -m unittest discover -s tests -p unit_replay_accounting_registration.py` | Python 3.9.6: 30 passed, 0 failures/errors/skips, 1.433s |
| `/opt/homebrew/bin/python3 -m unittest discover -s tests -p unit_replay_accounting_registration.py` | Python 3.14.3: 30 passed, 0 failures/errors/skips, 1.365s |
| `/usr/bin/python3 -m unittest discover -s tests -p 'unit_*.py'` | 228 passed, 0 failures/errors/skips, 21.908s |
| `/opt/homebrew/bin/python3 -m unittest discover -s tests -p 'unit_*.py'` | 228 passed, 0 failures/errors/skips, 20.640s |
| `/usr/bin/python3 -m compileall -q research tests/unit_replay_accounting_registration.py` | exit 0 |
| `/opt/homebrew/bin/python3 -m compileall -q research tests/unit_replay_accounting_registration.py` | exit 0 |
| `pvg verify research/persistent_budget.py tests/unit_replay_accounting_registration.py docs/REPLAY-ACCOUNTING-REGISTRATION.md --format=text` | PASS: 2 files scanned, 0 issues; Markdown not scanned |
| `git diff --check` and `git diff --cached --check` | exit 0 |

Logs: `/tmp/GRRR-43i8-blob-full-py39.log` and
`/tmp/GRRR-43i8-blob-full-homebrew.log`; final suites report OK, no warnings.
Regressions iterate every column of reservations, metering, overhead, state and
store_identity. They cover defaults and nonboolean readonly inputs, all registered
profiles, legacy handles before/after publication and partial-registration handles.
Tests assert unchanged bytes/inode, cumulative totals and pending holds. Native
read-only reads succeed on 3.14; both write() and item assignment refuse. The 3.9
unsupported-read assertion executes rather than skipping a test.

Coverage command:

```sh
/usr/bin/python3 -m trace --count --missing --summary \
  --file /tmp/GRRR-43i8-blob-trace --coverdir /tmp/GRRR-43i8-blob-coverage \
  --module unittest discover -s tests -p unit_replay_accounting_registration.py
```

30 passed in 2.395s. Python 3.9 reported executable-line coverage: PersistentBudget
96% (146 lines), Budget 91% (175 lines). Not branch coverage; native read-only BLOB
behavior is exercised separately by the Python 3.14 run. Coverage log:
`/tmp/GRRR-43i8-blob-coverage.log`.

New PersistentBudget SHA256:
`ef038d60706f8f103387a6f41c28695da605f541666fa231abaa99e2af9255af`.
Budget, bootstrap and source launcher pins are unchanged; full suites verify
the existing launcher pins. No installed artifact changed.

## LEARNINGS

- The prior freeze correction covered SQL but missed a separate SQLite mutation
  API. An authorizer is not a complete incremental-BLOB write boundary.
- Denying unused writable BLOB access is smaller and safer than handing out a
  wrapper whose write, slice assignment, lifetime and stale-state semantics would
  all need auditing. Native read-only handles remain useful and safe.
- Handles opened by older code cannot be retroactively revoked by this override.
  Installer writer/process quiescence and exclusive-parent operation remain
  mandatory. Deliberate base-C-method invocation/guard disabling by arbitrary
  evaluator code is not sandboxed by this trusted API, as documented previously.
- pvg initially flagged NotImplementedError for absent native support as a stub;
  the final code uses the specific sqlite3.NotSupportedError with executed tests.

## nd_contract
status: in_progress

### evidence
- Code `2dbf825e93376c6df5b974e339ea7846a9bc9165`; focused 30/30 and full 228/228 both required interpreters.
- No root/sudo, protected mutation, QEMU/VM, stop release, replay, delivery or push.
- Independent re-review pending; installer baseline and quiescence requirements unchanged.

### proof
- [x] Writable incremental BLOB access refused across profiles, stale/partial states and protected tables/columns; bytes/inode/holds preserved.
- [x] Read-only native BLOB behavior preserved; Python 3.9 compatibility refusal tested without skips.
- [ ] AC2/5 protected installation/postflight: BLOCKED, not-run.
- [ ] AC4 recovery: BLOCKED, not-authorized, not-run.
- [ ] Actual independent replay: BLOCKED, not-run.
