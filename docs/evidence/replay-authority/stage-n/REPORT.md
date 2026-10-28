# Stage N replay-successor authority contract — candidate, design-only

## Scope

This stage answers the approved Stage M finding with a schema and exact
candidate contract for a **version-4 fresh replay successor**. It does not
implement a runtime store, install or access `/Library/GRRR`, reconcile
spendability, dispatch replay, promote or admit anything, merge, or push.

## Contract decision

The only valid decision is:

```text
candidate-fresh-replay-successor-poc
```

It is deliberately not labeled approved. Independent review, exact installer,
review, and operator authorization identities remain `null`/required. A binding
cannot contain a fabricated device or inode; both are represented as
`required-at-install`.

## Predecessor status is not resolved

The candidate binds the approved retained evidence identities and preserves:

- spendability: `null`;
- historical status: `unresolved`;
- zero final classifications;
- no whole-archive absence claim;
- all original POC and milestone ceilings fully encumbered;
- all three unresolved 300,000,000-microsecond holds and their exact IDs, now
  derived independently from the retained Stage A baseline;
- no hold release.

The relationship remains `fresh-successor-not-reconciliation`.

## Proposed bounded amendment

Because the predecessor fully encumbers the original ceilings, any successor
charge requires an explicit operator-approved **incremental amendment before
any charge**. The candidate proposes:

- four exact modes: normal, failed-rebuild, interruption, two-failures;
- 480,000,000 execution microseconds per session;
- 1,920,000,000 execution microseconds aggregate;
- zero money and zero review time in the static candidate;
- at most twelve guest launches;
- two-consecutive-independent-replay-failure stop policy, still requiring
  operator approval before execution.

This is a proposal only. It does not increase a live budget.

## Guards, failure, and rollback

The candidate keeps every authority flag false and requires per-run operator
approval. Admission remains blocked, promotion disabled, and automatic merge and
push false.

Installation must be exclusive-parent controlled, install-once, leave the
predecessor read-only, and refuse without retry while preserving partial
evidence. Rollback is scoped only to the new successor namespace, must verify
the baseline, and cannot roll back or reset the predecessor.

## Verification

- Initial independent review rejected one incorrect hold ID:
  `b34d8b9d106e42eab4a3e43daac98ddd` instead of
  `b34d8b9d106e42eab3a3e43daac98ddd`.
- Correction pin now uses the retained Stage A ID, and a new regression hashes
  the baseline and derives all pending IDs from its actual/receipt-null rows.
- Focused Stage N tests after correction:
  - Homebrew Python 3.14.3: 28/28 passed.
  - Miniconda Python 3.12.7: 28/28 passed.
- Full no-guest unit suites after correction:
  - Homebrew Python 3.14.3: 512/512 passed.
  - Miniconda Python 3.12.7: 512/512 passed.
- Deterministic contract emission was byte-identical.
- The known Homebrew-only `ResourceWarning` from the prior full run was traced
  to an unclosed temporary SQLite connection in `unit_spendability_stage_c`.
  The fixture now closes that connection; focused Stage C ran under
  `-W error::ResourceWarning` and passed 46/46.
- `pvg verify`: PASS.
- `git diff --check`: PASS.

## Remaining gates

The initial independent review is rejected and preserved. Fresh narrow re-review
of the corrected WIP returned:

```text
STAGE_N_NARROW_REWORK_REVIEW: APPROVED
```

Approval covers only the design contract. Runtime adapter design, exact
installer/review/authorization bytes, protected installation, budget amendment,
reconciliation decision, dedicated identities, replay execution, PM acceptance,
merge, and push remain separately gated.
