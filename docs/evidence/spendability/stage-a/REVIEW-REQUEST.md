# GRRR-z3w9 Stage A independent review request

## Exact scope

Review only the protected read-only baseline capture and fail-closed
spendability evidence package for GRRR-z3w9. This request grants no authority.
Do not write spendability, reconcile, release a hold, replay, promote, admit,
mutate production, merge, or push.

## Exact identities

- Story branch: `story/GRRR-z3w9`
- Tested integration commit: `c80f77ae8f39c13b59b4571c7948f19c4528c6a6`
- Evidence contract: `docs/SPENDABILITY-RECONCILIATION-EVIDENCE-CONTRACT.md`
- Baseline SHA-256: `7608cbe6fc5f671b88573eca8b642ebfbc172f0cb920f75d60ca34cfa60c730a`
- Capture program SHA-256: `b54fbf5dcafa87cf5853fe1555718661a40f53e51ea348ac84d0fc2d1bff777b`
- Validation SHA-256: `27347dcd1b6fcf41ddb074e2a71294b51dfabca97fc8096377077e3a0eb49e49`
- Artifact identities are listed by `PACKAGE.json`; that manifest does not
  circularly bind its own hash.

## Review questions

1. Does `CAPTURE.py` perform only read-only access to
   `/Library/GRRR/accounting-poc2`, open SQLite read-only/immutable, avoid
   protected writes, and preserve raw source rows separately from projections?
2. Does `BASELINE.json` bind the active ancestry, database bytes/stat identity,
   schema, all 11 reservations, all 8 meter rows, empty overhead, state, store
   identity, and three pending maxima without converting unknowns to zero?
3. Does the captured known execution-us encumbrance reproduce
   `1,108,265,788` in both POC and milestone scope while remaining only a
   known-encumbrance calculation?
4. Does `VALIDATION.json` correctly fail closed with `spendable=null`,
   `valid=false`, and an earlier unresolved schema/quiescence gate rather than
   claiming independent review is the first unresolved fact?
5. Are unresolved schema compatibility, writer exclusion, review, operator
   decision, provenance, pending evidence, overhead completeness, historical
   completeness, unknown upper bound, meter-body compatibility, and
   authorization-binding gates retained as blockers?
6. Is any statement or field capable of authorizing reconciliation, mutation,
   replay, promotion, admission, merge, or push?

## Required reviewer format

Return exactly one verdict:

- `STAGE_A_REVIEW: APPROVED_BASELINE_CAPTURE`
- `STAGE_A_REVIEW: REJECTED_BASELINE_CAPTURE`
- `STAGE_A_REVIEW: BLOCKED_MISSING_EVIDENCE`

Then list any required correction as an exact file and condition. A blocked
result is valid if the evidence is honestly incomplete; do not approve a
non-null spendability decision from this package.
