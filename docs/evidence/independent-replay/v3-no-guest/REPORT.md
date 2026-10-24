# V3 no-guest verification — BLOCKED, NOT DELIVERED

PROOF:

Source bytes are bound by source-SHA256SUMS in this directory. WIP commit SHA
is appended to the live GRRR-z3w9 story after commit. Starting WIP 6079af6;
merged epic 6afd643 without conflicts. No accounting/security source or test
diff remains relative to that epic (persistent_budget.py, accounting_registration.py,
budget.py, unit_replay_accounting_registration.py).

From the dev-GRRR-z3w9 worktree, with Python 3.9.6 and 3.14.3 respectively:

| Command (each interpreter) | System | Homebrew |
|---|---|---|
| `-m unittest discover -s tests -p 'unit_*replay*.py'` | 91 pass, 0 errors/failures/skips; 17.419s | 91 pass, 0 errors/failures/skips; 16.784s |
| `-m unittest discover -s tests -p 'unit_*.py'` | 248 executed/pass, 0 test failures; 1 class setup error; 21.231s; exit 1 | 248 executed/pass, 0 test failures; 1 class setup error; 20.033s; exit 1 |
| `scripts/test-story independent-replay` | 0 executed, 1 class setup error, 0 skips; exit 1 | 0 executed, 1 class setup error, 0 skips; exit 1 |
| `-m compileall -q research scripts tests` | exit 0 | exit 0 |
| `-m py_compile scripts/replay-root-prepare scripts/prepare-independent-replay-input scripts/test-story` | exit 0 | exit 0 |

The exact interpreters were `/usr/bin/python3` and `/opt/homebrew/bin/python3`.
The nine conservative-genesis tests did not execute because their class setup
requires 15,350,000,000 bytes free. The measured 13,212,716 KiB free is below
that threshold and the replay 15-GiB floor. This is not a passing full suite.
The live suite only reads existing evidence; its actual UID/GID prerequisite
rejected this operator process before tests. No guest was attempted.

Initial runs are retained separately: focused 91 with 3 failed hash assertions;
full 248 with those same 3 failures plus the disk setup error. The merge had
retained a stale persistent_budget.py launcher pin. The pin was corrected to
the accepted epic bytes, not by weakening the hash assertions.

`pvg verify research/replay.py research/replay_fixtures.py research/replay_profile.py research/replay_smoke.py research/corpus_execution.py research/corpus_evaluation.py research/persistent_budget.py research/accounting_registration.py scripts/replay-root-prepare scripts/prepare-independent-replay-input tests/unit_replay_inputs.py tests/unit_replay_smoke.py tests/unit_replay_registration_boundary.py tests/integration/independent_replay.py docs/INDEPENDENT-REPLAY-V3-REVIEW.md --include-tests --format=text`
returned `VERIFY: PASSED (12 files scanned, 0 issues)`, exit 0.
Both `git diff --check` and `git diff --cached --check` returned exit 0.

`/usr/bin/python3 -m trace --count --missing --summary --coverdir /private/tmp/grrr-replay-v3-coverage --module unittest discover -s tests -p 'unit_replay_registration_boundary.py'`
passed 2 tests. Boundary-only coverage: replay.py 20% of 480 executable lines,
new test module 96% of 33 lines. This is not full-suite or live coverage.
Focused suites include real non-privileged SQLite/filesystem/authorization
tests inherited from accepted registration; new mocks test only pure preflight
decisions and never establish integration evidence.

## AC verification

| AC | Package evidence | Actual status |
|---|---|---|
| 1 | Replay profile/fixtures, cumulative-binding preflight, exact import closure | Partial; fresh VM and authorized reservation unproven |
| 2 | Pinned D011 maintainer assertion mapping | Partial; no independent live reproduction |
| 3 | Pure finding/gate helpers and four-mode result validation | Partial; no actual ReplayReceipt |
| 4 | Four-mode read-only integration suite and no-guest tests | Unmet; all live integration unexecuted |
| 5 | Pure failure transition tests, retained-mode draft | Partial; durable live sequence unproven |

LEARNINGS:
- Registration v2 deliberately freezes every mutation; successful registration
  is neither an executable budget profile nor stop-recovery authorization.
- Import closures need transitive dependencies and updated pins after merges.
- A passing focused suite does not conceal a disk-blocked full-suite class.
- Future commands need a new recovery implementation and independent review;
  presenting exact grammar does not authorize or validate execution.

DISCOVERED_BUG:
  title: Independent replay remains blocked by recovery and capacity prerequisites
  context: Registered v2 accounting is intentionally frozen. No approved recovery implementation exists; free disk also blocks conservative-genesis setup and replay floor. Live tests reject the operator UID/GID. No safeguards were relaxed.
  affected_files: research/replay.py; research/persistent_budget.py; scripts/conservative-genesis; tests/integration/independent_replay.py
  discovered_during: GRRR-z3w9

DISCOVERED_BUG:
  title: Story worktree knowledge search cannot resolve vault
  context: pvg notes search independent-replay returned vault directory not found for dev-GRRR-z3w9/.vault. Live pvg nd worked using the git-common shared vault. No raw issue data was accessed or vault routing modified.
  affected_files: worktree knowledge vault configuration
  discovered_during: GRRR-z3w9

## nd_contract
status: new

### evidence
- No-guest WIP only; independent review and live gates remain blocked.

### proof
- [ ] AC #1: real fresh replay unproven.
- [ ] AC #2: independent live specification violation unproven.
- [ ] AC #3: actual complete receipt unproven.
- [ ] AC #4: mandatory live integrations unexecuted.
- [ ] AC #5: durable failure/stop sequence unproven.
