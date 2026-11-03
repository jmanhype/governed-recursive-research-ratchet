# GRRR-z3w9: merged registration, no-guest WIP — BLOCKED

## Scope and measured boundary

Merged epic `6afd643` into replay WIP `6079af6` without conflicts. Preserved
accepted accounting code and tests; no recovery, stop release, protected write,
VM, QEMU, candidate execution, admission, promotion, or push performed.

Read-only active.json observation on 2026-10-24 confirms version 2, profiles
synthetic/offline/trusted-observation/independent-replay, and registration hash
`fb2132f1dce4867d0a28895215ef9d5f9ad1ea947b3a373de5efd7ddad04f397`.
The original DB hash is `2347a548429cd8bf07048e15898de1432c960d7a08743e17dc31d39efdb5bbaf`
per accepted registration; this worker cannot read the UID-320-only database and
does not claim to have rehashed it. Parent reports stopped=1 and
execution_authorized=false. Accepted registration freezes all mutation APIs,
stale SQL handles and writable BLOB access; those safeguards are unchanged.

`df -k .` measured 13,212,716 KiB available, below 15 GiB. No disk cleanup or
floor relaxation was attempted. The graph index dated 2026-10-23T18:45:46Z was
stale/untracked for relevant code; exact source reads replaced graph claims.
Knowledge search failed because the worktree has no .vault knowledge directory;
the live shared story was read with pvg nd, not raw issue files.

## Integration changes

- Replay preflight now reads the protected active binding, recognizes the
  registered profile and refuses frozen v2 before input access or namespace
  creation. Unknown versions also fail closed; no future recovery schema is
  invented. Registration is not execution authorization.
- The launcher pins the required accounting_registration.py import as well as
  the merged budget implementation. Exact import-closure tests remain enforced.
- Four one-shot modes, replay-only inputs and the existing cumulative store
  remain unchanged. No smoke/corpus receipt is relabeled and no allowance is
  initialized. This remains a draft without real independent replay receipts.

## Parent-mediated authorization plan — NOT independently approved commands

The v2 command inventory remains exact grammar, but **cannot run successfully
against the accepted registered store**. No recovery command currently exists.
Do not run SQL, remove registration, edit active.json, replace the DB, reset a
namespace, or execute modes as a batch to get around that fact.

1. Obtain a separately scoped recovery design/implementation and independent
   review preserving the same inode/store/history, every charge and unknown
   hold, and stopped evidence. It must define an append-only recovery receipt,
   execution binding and mutation semantics compatible with accepted freeze
   guards. Recovery must not be inferred from registration authorization.
2. Obtain explicit operator authorization for that exact recovery action, and
   a separate approved disk-capacity action restoring at least 15 GiB free.
3. Independently review the entire replay diff, fixture/specification bytes,
   cumulative budget linkage, four modes, watchdog/stop policy, cleanup,
   evaluator identities and immutable import closure. Bind approval to exact
   reviewed source hashes; no existing root approval is reusable.
4. Separately authorize immutable installation and each one-shot execution.
   Review decision is `approved-D011-independent-replay-<mode>` and replay scope
   is exactly `replay.scope(<mode>)`. Only the trusted parent may install/launch.
   The fixed invocation for each separately approved mode is:

```sh
/usr/bin/env -i PATH=/usr/bin:/bin LC_ALL=C /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/bin/python3.9 -I -S -B /Library/GRRR/bootstrap/replay-root-prepare --independent-replay-normal
/usr/bin/env -i PATH=/usr/bin:/bin LC_ALL=C /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/bin/python3.9 -I -S -B /Library/GRRR/bootstrap/replay-root-prepare --independent-replay-failed-rebuild
/usr/bin/env -i PATH=/usr/bin:/bin LC_ALL=C /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/bin/python3.9 -I -S -B /Library/GRRR/bootstrap/replay-root-prepare --independent-replay-interruption
/usr/bin/env -i PATH=/usr/bin:/bin LC_ALL=C /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/bin/python3.9 -I -S -B /Library/GRRR/bootstrap/replay-root-prepare --independent-replay-two-failures
```

Interruption and two-failure modes stop the shared store. Any subsequent mode
requires fresh independently reviewed recovery; no automatic restart or reset.
After actual approved runs, use the real UID-320 evaluator with independently
installed tests to run `./scripts/test-story independent-replay`. No mock or
no-guest suite can replace those observations.

## AC disposition

All five story ACs remain PARTIAL/UNPROVEN at the live boundary. Byte/spec
mapping, receipt helpers and state-transition unit tests are not reproduction.
No AC is delivered, no defect is verified, and admission stays blocked.
Independent review of this package is still required; this document is not that
review. The source diff exceeds the original ~6-file/1000-line estimate already
in v2 and requires PM investigation, not silent waiver.
