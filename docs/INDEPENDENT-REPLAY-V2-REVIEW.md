# GRRR-z3w9 v2 continuation — NOT delivered, installed or live-approved

## Concrete preparation artifact

Unprivileged command (no guest, candidate build or candidate execution):

```
/usr/bin/python3 scripts/prepare-independent-replay-input /private/tmp/grrr-independent-replay-input-v1
```

The 71,954,432-byte ISO remains at that path. `prepared-SHA256SUMS` and both
preparation records are retained in `docs/evidence/independent-replay/v2-no-guest/`.
The ISO SHA256 is `977783b9bae0b76e7288afbf31e9018b86a7345072b5729257f8392d45e256cf`.
Its profile SHA256 is `01cc844ee183f88c4d897e3be523add2708d07c0c6913fda992a3899be9e8de3`.
Primary ISO readback verifies every member. This is preparation evidence only.
Final free space was 17,855,049,728 bytes; no worker cleanup occurred.

Corpus v2.2 was not changed. Replay-only wire IDs C901/D901/D902/C902 use the
existing generic supervisor protocol, not corpus membership. C901 and D901 have
byte-identical D011 assertions after test-name normalization; D901 applies the
existing D011 seed. D902 inserts invalid syntax into the actual pinned source,
so a future guest Go build must fail. C902 sleeps for 300 seconds per probe;
the runner's fixed 60-second command timer fences/stops its QEMU and records a
distinct interruption marker. The 473+5+2 parent bound still contains all work.
This establishes bounded interruption of a dispatched fixture, not proof that
the sleeping probe was reached: a slow guest build can still be in progress.

## Implemented draft, review required

- Default corpus executor hooks retain original image/profile/path and receipts.
  Replay overrides select only compiled pins and the fixed protected replay
  input path. There are no caller-supplied artifact hashes or monkeypatches.
- Four immutable parent modes have distinct one-shot namespaces. All continue
  to use `PersistentBudget('independent-replay')`, never the smoke budget.
- Normal uses fresh clean-D011 and seeded-D011 VMs. Failed-rebuild uses clean
  plus syntax-error source. Interruption retains unknown usage. Two-failures
  runs seeded success, clean negative, clean negative, retaining all three
  receipts and stopping at counts 0, 1, 2. All attempts share the parent bound.
- Each root mode validates its expected raw mode evidence before reporting
  execution success. This never grants admission or promotion.
- `tests/integration/independent_replay.py` now reads all four completed
  evaluator-owned namespaces, rather than rerunning the consumed normal mode
  or expecting normal mode alone to somehow produce all fault evidence.

## Protected accounting proposal — no implementation or authorization

The active successor store is reportedly stopped and has no independent-replay
profile. Neither its files nor `/Library/GRRR` were modified by this worker.
Every parent mode intentionally refuses at preflight before namespace creation.

Independent review must define and approve a protected migration/recovery:

1. Acquire the campaign's existing dispatch lock; stop all producers and verify
   cessation. Independently retain the active binding, inode/device/store ID,
   database SHA256, integrity result, all reservation/metering/overhead rows,
   stop state and history receipt. No new campaign or empty allowance.
2. Extend the registered profile set and protected binding through a separately
   reviewed tool. Preserve the same campaign and physical accounting authority,
   ceilings and every settled charge/unknown hold. Validate old row equality
   and cumulative totals, including preparations/reviews as applicable.
3. Treat clearing a stop as a separate explicit operator-approved recovery,
   backed by causal inspection and an append-only recovery receipt. Registration
   alone cannot clear it. Uncertain usage stays reserved; no recasting corpus or
   smoke events as replay. No blanket SQL update is proposed here.
4. Rebind exact reviewed replay code/profile to that authority and revalidate
   before every reservation. Failed/interrupted runs must never automatically
   retry, obtain a fresh namespace allowance, or erase previous evidence.

This proposal deliberately does not change `persistent_budget.py`; an approved
implementation of it is required before any live mode can succeed. Interruption
and two-failure modes both halt the shared store; do not chain them with an
automatic reset. Each subsequent execution needs an independently reviewed
recovery that preserves all prior usage/holds.

## Exact future parent commands — currently expected to refuse

First independently review the complete diff, source reconstruction, fixture
catalog/ISO readback, import closure, accounting migration/recovery, receipt
gates, interruption timing and cleanup. The existing root approval must NOT be
reused. Install only independently reviewed immutable bytes, never checkout
code as root. The input namespace must contain exactly the three entries in
`replay_profile.PINS`, not the staging directory's media/SHA256SUMS files.

For each mode, review decision is exactly
`approved-D011-independent-replay-<mode>`, and `review.replay` is the exact
`replay.scope(<mode>)`. Bind the current launcher SHA256, exact CODE mapping,
approved runtime/preexec fields and independent review reference. A review for
one mode cannot authorize another. Future parent commands are:

```sh
/usr/bin/env -i PATH=/usr/bin:/bin LC_ALL=C /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/bin/python3.9 -I -S -B /Library/GRRR/bootstrap/replay-root-prepare --independent-replay-normal
/usr/bin/env -i PATH=/usr/bin:/bin LC_ALL=C /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/bin/python3.9 -I -S -B /Library/GRRR/bootstrap/replay-root-prepare --independent-replay-failed-rebuild
/usr/bin/env -i PATH=/usr/bin:/bin LC_ALL=C /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/bin/python3.9 -I -S -B /Library/GRRR/bootstrap/replay-root-prepare --independent-replay-interruption
/usr/bin/env -i PATH=/usr/bin:/bin LC_ALL=C /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/bin/python3.9 -I -S -B /Library/GRRR/bootstrap/replay-root-prepare --independent-replay-two-failures
```

The order above is an inventory, not a runnable batch or permission to reset a
stop. Every namespace is single-use and must be preserved on partial failure.
After separately approved immutable test installation, the actual UID-320
evaluator must run `./scripts/test-story independent-replay` to inspect all
four namespaces. The ordinary operator invocation currently fails on actual
UID/GID, as required. No fake identity, skip, or host candidate fallback exists.

## Remaining gates

No live guest or independent receipt was produced. Actual clean/seeded rebuilds,
failed rebuild, interrupted guest cessation/hold, durable two-failure stop,
independent snapshot anchoring, runtime identity separation and the cumulative
recovery path remain unproven. Security review, reviewer outcome, action-specific
human approval, contract admission, comparison and promotion remain blocked.
