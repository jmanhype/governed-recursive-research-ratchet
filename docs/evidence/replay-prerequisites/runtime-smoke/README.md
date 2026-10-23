# GRRR-w1lt runtime-smoke review evidence

Base: `f1db89ff954ddbf91aa9d8156fd2d78dad12e244`. This report concerns the
new bounded runtime service package, not a live execution. Earlier successful
parent namespace preparation at 3f2658b is recorded separately and unchanged.

## Commands / proof

Run from the story worktree under each exact interpreter `/usr/bin/python3`
(3.9.6) and `/opt/homebrew/bin/python3` (3.14.3):

- `PYTHON -B -m unittest discover -s tests -p 'unit_replay*.py'`:
  28 tests per interpreter, no failures/errors/skips in final logs.
- `PYTHON -B -m unittest discover -s tests -p 'unit_*.py'`:
  194 tests per interpreter, no failures/errors/skips in final logs.
- `pvg verify research/replay_smoke.py research/replay_prerequisites.py research/corpus_execution.py scripts/replay-root-prepare tests/unit_replay_smoke.py tests/replay_smoke_process_probe.py docs/REPLAY-RUNTIME-SMOKE.md docs/REPLAY-PREREQUISITES.md --format=text`:
  passed, 5 Python files scanned, zero issues. Extensionless launcher is loaded
  by real tests; all 12 installed CODE hashes are checked against source bytes.
- `git diff --check`: passed. SHA256SUMS binds this report, final logs and changed
  code/contract/test sources; paths are relative to the repository root.

The eight new tests exercise exact C001 policy/scope and types; evidence semantic
denials; incomplete/misbound lifecycle results; actual non-root identity refusal
before effects; real launcher role refusal; exact code inventory/hashes; real
harmless child/grandchild process groups stopped by TERM; and TERM-resistant
groups killed/reaped within the seven-second cessation budget. No mocks, skips,
environment gates, UID substitution, QEMU or VM execution supply these results.

Initial local iterations exposed bare-pass static-check failures and macOS
`killpg(pid, 0)` returning EPERM for an already-empty group; both were corrected.
A transient hash assertion failure occurred while updating the smoke pin during
an earlier test run. All final logs are from the complete rerun after pinning.
These failures are not guest/runtime-positive evidence.

## AC boundary

| AC | Reviewable evidence | Remaining live gate |
|---|---|---|
| 1 | Original immutable policy and identities unchanged; exact one-shot C001 scope | New smoke review approval, not original approval reuse |
| 2 | Root-only installed closure and namespace verifier; original preparation succeeded per parent | New code installation and fresh smoke namespace ownership readback |
| 3 | Existing protected locked preflight reused, exact floor rechecked at guest spawn | Parent positive updated preflight before execution |
| 4 | Executable UID-separated lifecycle, smoke-only Budget/Ledger, bounded parent cessation | **NOT-RUN:** real offline VM service/stop/watchdog/accounting lifecycle and UID denial probes |
| 5 | Scope denies independent replay/admission; no verdict engine/ReplayReceipt | GRRR-z3w9 independent replay remains separate and not-run |

## LEARNINGS / recovery

Process-group ownership must include QEMU, not only its executor service. Concurrent
TERM/KILL grace periods avoid multiplying the approved bound across services.
Group absence must be observed separately from the service's exit status. The
original corpus spawn behavior remains unchanged; only smoke uses inherited
group membership and the stricter parent deadline.

All failures retain exclusive partial smoke state, root logs and evaluator
unknown reservations. No automatic retry, cleanup, corpus truth/probe mutation,
old ledger relabeling or counter reset is permitted. Parent TERM/INT enters
cleanup; root SIGKILL or host failure needs manual trusted-parent recovery.

No root, QEMU, VM, paid dispatch, /Library/GRRR mutation, push, delivery or
acceptance was performed by this worker. Story remains **in_progress**. Exact
future sanitized parent commands and new review/install fields are in
`docs/REPLAY-RUNTIME-SMOKE.md`. Independent review, installation, runtime prelaunch
audit, positive root provisioning/access probes and actual service/VM lifecycle
are all **not-run** for this revision. No DISCOVERED_BUG is deferred outside this
scope; the observed process-group probe behavior was corrected here.
