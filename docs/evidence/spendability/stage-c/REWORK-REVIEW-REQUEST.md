# GRRR-z3w9 Stage C narrower rework review request

## Exact scope

Review only whether commit `0a14675502da7b31ac40ca1fcbf2970b2f76be30`
corrects the five findings from `REVIEW-2-REJECTED.md`. This is a changed,
narrower review brief; do not repeat the broader Stage B architecture review.

Do not access or mutate `/Library/GRRR`, write spendability, reconcile, replay,
promote, admit, mutate production, merge, or push.

## Exact identities

- Commit: `0a14675502da7b31ac40ca1fcbf2970b2f76be30`
- Module:
  `research/spendability_stage_c.py`
  SHA-256 `5641d4a5fea35b3838a92d1b16f79f275153f1ff85d90333fd1655a23b1c9a7f`
- Tests:
  `tests/unit_spendability_stage_c.py`
  SHA-256 `364726172e8bf7558892fc55a56391e2a4a7b00f27530308c08bd33231923949`
- System full-suite log:
  SHA-256 `3908ab97624bc0834360358c5524a67a51c64ce132297dcc5d387b1a2ceaf078`
- Homebrew full-suite log:
  SHA-256 `b1221f49f43242787c0939acbbe7c134069ffb36c462363395e1a55691cb1f90`

## Five required corrections

1. Confirm the adapter maps actual SQLite semantics: metering `_1=id/pk`,
   `_2=reservation/u`; reservations `_1=id/pk`, `_2=key/u`; key xinfo uses
   `seqno=0`, and auxiliary rowid uses `seqno=1,cid=-1`. Tests must generate
   the fixture through real in-memory SQLite PRAGMAs.
2. Confirm provenance binds exact immutable Stage A baseline bytes to
   `STAGE_A_BASELINE_SHA256`, validates canonical raw BLOB projections, unique
   reservation IDs, unique meter joins, paired actual/receipt state, and
   meter-body receipt/usage joins.
3. Confirm quiescence validation binds the approved lock path/protocol/no-ACL
   representation, ordered observation timestamps, and observed-vs-expected
   toolchain identities; Stage C must reject an approved review claim and leave
   writer-exclusion proof unresolved.
4. Confirm a provenance meter group marked `missing` cannot assert meter ID or
   usage evidence.
5. Confirm pending disposition enforces a status-specific dispatch/evaluator
   causal matrix, especially rejecting `failed_not_dispatched` with dispatched
   evidence.

## Verification already recorded

- Focused Stage C tests: **46/46 passed** on Python 3.9.6 and 3.14.3.
- Full no-guest suites: **363/363 passed** on both interpreters.
- `pvg verify` selected module/tests: PASS.
- `git diff --check` and `git diff --cached --check`: PASS.

## Required verdict

Return exactly one:

- `STAGE_C_NARROW_REWORK_REVIEW: APPROVED`
- `STAGE_C_NARROW_REWORK_REVIEW: REJECTED`

For rejection, list only a defect in one of the five scoped corrections. This
approval remains implementation-schema approval only; it is not historical
completeness, spendability, protected-operation authority, or replay authority.
