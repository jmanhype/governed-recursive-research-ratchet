# V4 no-guest verification — BLOCKED, NOT DELIVERED

PROOF:

Source merge/WIP commit: `c2c19ae92f4d318d0892bc77272b599043c0019f`,
parents `3869e0ff223bae5d4ae75080f33d4b6ba33efacc` and
`38f33c936b8249a57be81aebd639aa40c2f9de55`. Branch story/GRRR-z3w9.
The launcher hash-map conflict was resolved with the exact merged import closure;
accepted accounting recovery/security implementation and cessation tests remain
unchanged. The new replay boundary refuses v3 explicitly because it is read-only,
not because recovery is still missing. No authority was broadened.

Tests ran on `/usr/bin/python3` (3.9.6) and `/opt/homebrew/bin/python3` (3.14.3):

| Command (each interpreter) | System | Homebrew |
|---|---|---|
| `-m unittest discover -s tests -p 'unit_*replay*.py'` | 117 pass, 0 failures/errors/skips; 20.988s; exit 0 | 117 pass, 0 failures/errors/skips; 20.534s; exit 0 |
| `-m unittest discover -s tests -p 'unit_*.py'` | 274 executed/pass, 0 failures/skips; 1 class setup error; 25.063s; exit 1 | 274 executed/pass, 0 failures/skips; 1 class setup error; 23.909s; exit 1 |
| `scripts/test-story independent-replay` | 0 executed, 1 class setup error; exit 1 | 0 executed, 1 class setup error; exit 1 |
| `-m compileall -q research scripts tests` | exit 0 | exit 0 |
| `-m py_compile scripts/replay-root-prepare scripts/prepare-independent-replay-input scripts/test-story` | exit 0 | exit 0 |

The full suites are NOT passing: nine conservative-genesis tests never executed
because setUpClass raises `RuntimeError: preparation space floor`, requiring
15,350,000,000 bytes. The recorded filesystem available space was 10,358,388 KiB,
below that floor and the replay floor. No deletion or floor relaxation occurred.
The live read-only suite fails at `Dedicated UID/GID required`; no guest is run
or guest receipt produced. No tests are gated/skipped to manufacture green.
Coverage was not measured in this continuation; no percentage or live coverage
claim is made. Mocked preflight tests prove decision ordering only, not integration.

`pvg verify research/replay.py research/replay_smoke.py research/persistent_budget.py research/accounting_registration.py research/accounting_recovery.py scripts/replay-root-prepare tests/unit_replay_registration_boundary.py tests/unit_replay_smoke.py tests/unit_replay_accounting_recovery.py tests/unit_replay_cessation.py docs/INDEPENDENT-REPLAY-V4-REVIEW.md --include-tests --format=text`
returned `VERIFY: PASSED (9 files scanned, 0 issues)`, exit 0. Both
`git diff --check` and `git diff --cached --check` returned exit 0.
Logs are adjacent; source-SHA256SUMS binds exact relevant source bytes and
SHA256SUMS binds the evidence package. Compile/metadata checks are in checks.log.

## AC verification

| AC | Evidence | Status |
|---|---|---|
| 1 fresh trusted reconstruction/reservation/VM | preflight and exact import closure; focused tests | Partial; actual fresh VM and writable/spendable reservation unavailable |
| 2 specification-confirmed independent defect | existing pinned D011 maintainer mapping | Partial; no live independent reproduction |
| 3 receipt/findings/mandatory gates | pure helpers and conservative refusal | Partial; no actual ReplayReceipt |
| 4 required real success and fault modes | no-guest tests and explicit identity failure | Unmet; all live tests unexecuted |
| 5 retained failures/two-failure stop | existing pure transitions; inherited cessation tests | Partial; actual durable live sequence unproven |

LEARNINGS:
- Accepted v3 recovery releases only stop; null spendability and denied mutations
  are still hard blockers. Reconciliation is separate and prohibited here.
- Transitive recovery imports must be pinned after merging accepted code; hash
  assertions remain strict and accepted cessation behavior remains intact.
- Passing focused tests cannot conceal capacity-blocked full-suite setup or an
  identity-blocked live suite. Earlier documents are historical, not authorization.
- Knowledge search failed because this worktree has no `.vault` knowledge path;
  no raw issue files were read. Code graph coverage was stale/untracked/excluded
  for the exact changed paths; direct source review supplied the fallback.

DISCOVERED_BUG:
  title: Independent replay remains blocked by spendability, capacity and live identity gates
  context: The reviewed v3 accounting successor is stop-only read-only, preserves unknown usage/holds and denies every runtime mutation. Replay needs reservation/settlement writes but reconciliation and replay are expressly unauthorized. Both full suites also have a disk-floor class setup error; read-only live tests fail dedicated UID/GID setup. No safeguards were relaxed.
  affected_files: research/replay.py; research/persistent_budget.py; scripts/conservative-genesis; tests/integration/independent_replay.py
  discovered_during: GRRR-z3w9

Remaining parent gates: separately reviewed and explicitly authorized reconciliation
if writes/spendability are required; capacity above fixed floors; actual identities;
independent exact-byte replay review and immutable installation; separate replay
authorization; fresh four-mode VM execution and retained complete evidence; PM
acceptance. No reconciliation, replay, promotion, admission, production mutation,
push, privileged command, UID/GID setup or /Library/GRRR mutation occurred.

## nd_contract
status: blocked

### evidence
- Safe no-guest WIP integrated with accepted epic; exact source commit and counts above.
- Full suite capacity error and live identity error retained, not skipped success.

### proof
- [x] No-guest v3 refusal and merged import closure verified.
- [ ] AC #1: actual fresh replay and authorized budget unavailable.
- [ ] AC #2: live independent reproduction unproven.
- [ ] AC #3: actual complete receipt unavailable.
- [ ] AC #4: required live modes unexecuted.
- [ ] AC #5: actual durable failure sequence unproven.
