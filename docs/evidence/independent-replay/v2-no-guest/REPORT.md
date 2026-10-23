# V2 no-guest proof — partial WIP only

## PROOF

Source identity is recorded in `source-SHA256SUMS`; commit identity is appended
to the story after committing these exact source bytes. No guest, QEMU, sudo,
root execution, protected mutation, push or paid call occurred.

Commands from the GRRR-z3w9 worktree:

- `/usr/bin/python3 scripts/prepare-independent-replay-input /private/tmp/grrr-independent-replay-input-v1`
  — exit 0; 9 primary-ISO members verified; 71,954,432-byte image, no execution.
- `/usr/bin/python3 -m unittest discover -s tests -p 'unit_*.py'`
  — 225 passed, 0 failed/errors/skipped, 20.399 seconds (`full-system.txt`).
- `/opt/homebrew/bin/python3 -m unittest discover -s tests -p 'unit_*.py'`
  — 225 passed, 0 failed/errors/skipped, 19.489 seconds (`full-homebrew.txt`).
- `/usr/bin/python3 -m unittest discover -s tests -p 'unit_*replay*.py'`
  and the same command with `/opt/homebrew/bin/python3`
  — 59 passed each, 0 failed/errors/skipped (`focused-*.txt`).
- `/usr/bin/python3 -m trace --count --missing --summary --coverdir /private/tmp/grrr-replay-v2-coverage --module unittest discover -s tests -p 'unit_*replay*.py'`
  — 59 passed; replay.py 41% of 476 executable lines, replay_fixtures.py 100%
  of 31, replay_profile.py 45% of 44 (`coverage-system.txt`). Protected/live
  branches remain unexecuted; this is not execution coverage of the required VMs.
- `pvg verify research/replay.py research/replay_fixtures.py research/replay_profile.py research/replay_smoke.py research/corpus_execution.py research/corpus_evaluation.py scripts/replay-root-prepare scripts/prepare-independent-replay-input tests/unit_replay_inputs.py tests/unit_replay_smoke.py tests/integration/independent_replay.py docs/INDEPENDENT-REPLAY-WIP.md docs/INDEPENDENT-REPLAY-V2-REVIEW.md --include-tests --format=text`
  — exit 0, reported 9 files scanned, 0 issues. This is not security approval.
- Both interpreters: `-m py_compile research/replay.py research/replay_profile.py research/replay_fixtures.py research/corpus_execution.py research/corpus_evaluation.py research/replay_smoke.py scripts/prepare-independent-replay-input scripts/replay-root-prepare tests/integration/independent_replay.py tests/unit_replay_inputs.py`
  — exit 0. Both also passed `-m compileall -q research scripts tests`.
- `git diff --check` — exit 0. `git diff --name-only -- corpus` — empty.
- `/usr/bin/python3 scripts/test-story independent-replay` — exit 1,
  0 tests run, 1 setup error, 0 skipped: actual dedicated UID/GID unavailable.
  This is a blocking live gate, not a passing integration result.

An earlier verify run identified the no-op result hook as a stub. It was replaced
by explicit run-binding validation preserving the corpus receipt shape; the
final verify and both final suites above passed. No RED tests were weakened.

## AC status

| AC | Evidence | Status |
|---|---|---|
| 1 fresh evaluator reconstruction/reservation/VM | New byte-pinned replay profile, source reconstructions, fixed executor hooks | Draft only; cumulative registration/recovery and actual execution blocked |
| 2 authoritative specification | Existing pinned upstream D011 assertion plus matching replay clean/seed probes | Byte/spec mapping tested; live reproduction unproven |
| 3 Finding and mandatory gates | Explicit mode checks and existing receipt/gate rules | Draft; no actual independent ReplayReceipt |
| 4 real success/failure integration | Separate clean, seed, syntax-error and bounded-interruption inputs; four one-shot modes; post-run integration | Required live suite blocked, 0 tests executed |
| 5 durable two-failure stop | Fixed success/negative/negative mode, shared cumulative store, retained ledger objects/holds | Pure state tests pass; real durable sequence unproven |

## LEARNINGS

- The generic supervisor can consume a separate replay catalog unchanged; D/C
  identifier syntax is not a license to relabel frozen corpus evidence.
- Reusing verified primary-ISO source/toolchain/supervisor bytes avoided host
  candidate execution and preserved corpus v2.2 completely.
- Negative fixture modes need distinct immutable namespaces, but not distinct
  accounting allowances. Stop recovery is separate from profile registration.
- A timed command interruption proves dispatched guest interruption, not that a
  slow build reached the sleeping probe. The limitation is explicit in review.
- Source/fixture preparation and unit success do not satisfy live ACs. Read-only
  post-run integration cannot manufacture missing evaluator evidence.

## nd_contract
status: new

### evidence
- Partial v2 preparation and implementation only; exact source hashes and logs here.
- Independent review, protected accounting migration/recovery and live gates blocked.

### proof
- [ ] AC #1: actual fresh cumulative-budget-bound replay unproven.
- [ ] AC #2: independent live specification violation unproven.
- [ ] AC #3: actual complete ReplayReceipt unproven.
- [ ] AC #4: actual four-mode integration unproven.
- [ ] AC #5: actual durable two-failure stop unproven.
