# GRRR-w1lt smoke security-review corrections

Base: 6b90f0100d09fa3acc66724127f34ecc12934237. No privileged execution.
This revision addresses exactly the three blocking lifecycle findings:

1. Prepared-marker creation and consumption share PREPARED_MODE=0400. The new
   private reader checks root ownership/GID, safe ancestors/ACLs, a regular
   single-link file, exact mode, 16 KiB bound, O_NOFOLLOW/O_NONBLOCK opening and
   stable metadata before/after reading. Public protected_bytes is unchanged.
   Real user-owned fixture tests prove the reader's mode/read/ACL/symlink checks,
   and the root wrapper rejects that fixture. This is not root-positive proof.
2. Cessation observation errors/timeouts cannot escape past the KILL phase.
   Every tracked group receives a KILL attempt on uncertain observation; uncertain
   results remain false. A real TERM-resistant child/grandchild with an already
   exhausted deadline is still killed, while the returned cessation result is
   false. Normal TERM and bounded TERM-resistant KILL tests remain passing.
3. Parent TERM/INT only sets deferred stop intent. A child is registered before
   the next checkpoint can raise. A real subprocess regression signals the parent
   from the child's pre-exec interval (while Popen waits for exec), proves stop
   intent, proves registration, then confirms complete group cessation/no orphan.

## PROOF commands and measured results

From the story worktree, under each required interpreter `/usr/bin/python3`
(3.9.6) and `/opt/homebrew/bin/python3` (3.14.3):

- `PYTHON -B -m unittest discover -s tests -p 'unit_replay*.py'`: 31 passed each.
- `PYTHON -B -m unittest discover -s tests -p 'unit_*.py'`: 197 passed each.
- No errors, failures, skips, mocks, UID substitution or environment gates in
  these final runs. No QEMU/VM execution is represented by the process tests.
- `pvg verify` on explicit changed code, tests, contract and evidence files:
  passed, 4 Python files scanned, 0 issues. Extensionless root script is loaded
  in real tests and all 12 installed code pins are verified against source.
- `git diff --check` and staged check passed. SHA256SUMS binds the changed
  implementation, current installation contract, report and exact output logs.

## AC / remaining gates

| AC | Evidence | Status |
|---|---|---|
| 1 | Original policy unchanged; C001-only scope retained | New independent review required |
| 2 | Strict private marker reader matches original 0400 creator | New package root-positive install/readback not-run |
| 3 | Existing protected asset/runtime/preflight checks unchanged | Updated positive parent preflight not-run |
| 4 | Corrected KILL fail-safe and signal-safe child registration; real harmless regressions | Actual parent VM/service/accounting/stop lifecycle NOT-RUN |
| 5 | No verdict/ReplayReceipt/admission implementation or counter mutation | GRRR-z3w9 remains separate |

The exact future sanitized command is unchanged and recorded in
`docs/REPLAY-RUNTIME-SMOKE.md`, alongside updated launcher/code hashes. The parent
must renew independent review, archive/update installation/review, rerun the
sanitized runtime audit and perform root-positive namespace/access/unchanged-asset
probes and actual offline C001 service/accounting/normal/timeout/stop lifecycle.
AC #4 remains unresolved. No delivery, acceptance, push, root/QEMU/VM execution
or /Library/GRRR mutation occurred. Story stays in_progress.

LEARNINGS: authorization metadata must match its producer's exact mode; process
observation failure cannot disable forced cessation; asynchronous stop intent
must not unwind the child-creation/registration interval.
DISCOVERED_BUG: all three reviewed findings corrected here; none deferred.
