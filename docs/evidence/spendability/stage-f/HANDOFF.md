# Stage F external evidence request — operator handoff

## Purpose

The Stage E bundle is structurally valid but deliberately unresolved. Stage F
asks for the exact evidence required before provenance, pending dispositions,
overhead, or historical completeness can be classified.

This request grants no spendability, reconciliation, replay, admission,
promotion, production-mutation, merge, or push authority.

## Exact request

- Request: `REQUEST.json`
- SHA-256: `6c59851d15fa44afccc3907e0aa0bedd7eb629095898d50b51a53079183cf919`
- Basis Stage E bundle SHA-256:
  `52f08fc740feee1e48de7fb79b83ccb684324339dab386c383805ec136956467`
- Basis Stage E package SHA-256:
  `36b9bfb4ae2f3d2245c4d60624e0c06548caf528578ab2ce888dfef4b2d0cc09`
- Database SHA-256:
  `9c6ff2561a364ed982cd5477dd4b200c995da6910c9a17aa3d3c411a962d64f3`

## Evidence requested

The request contains 30 mandatory evidence items:

| Domain | Count | What must be proven |
|---|---:|---|
| Reservation provenance | 11 | Original request, issuer, toolchain, authorization, measurement boundary, source artifact, and meter/settlement join where settled |
| Pending disposition | 3 | Dispatch outcome, final observation or explicit non-observation, cessation, evaluator stop/halt state, stale handles, and unchanged baseline |
| Historical lineage | 8 | Exact registration/recovery/current ancestry record and its authorization, review, identity, and postcondition |
| Operation history | 1 | Complete dispatch, cancellation, failure, stop, replay, overlap, and receipt inventory |
| Side-store history | 1 | Side ledgers, exports, manual adjustments, refunds, duplicate effects, and replay interactions |
| Overhead domains | 5 | Preparation, selection, execution, review, and other: actor, boundary, intervals, units, overlap, and measured cost or affirmative nonexistence |
| Global history | 1 | Campaign/store lineage, stop cause, paid services, lost/truncated/never-created records, recovery history, and absence boundaries |

## Where to look first

Search only systems that can plausibly own the original record:

1. original evaluator request and response logs;
2. scheduler or dispatcher operation logs;
3. evaluator stop, halt, and cessation records;
4. original meter or settlement receipts;
5. registration, recovery, and completion archives;
6. reviewed accounting exports or custodian backups;
7. review-session and paid-service approval records;
8. independently retained copies in an operator-owned archive.

Do not search or expose unrelated private data. Do not send credentials,
API tokens, private holdout fixtures, proprietary source, or raw unrelated logs.

## Response format

For every request item ID, provide one record classified as:

- `supplied`;
- `unavailable`;
- `lost`; or
- `never-created`.

A supplied record must include:

- immutable artifact bytes or an exact durable copy;
- SHA-256 and byte count;
- source system and custodian;
- artifact creation and retrieval timestamps;
- retrieval method and chain of custody;
- redaction justification if applicable;
- enough original context to authenticate identity, boundary, and effect.

For unavailable, lost, or never-created evidence, record:

- exact systems searched;
- custodians contacted;
- time ranges and identifiers queried;
- search commands or method descriptions;
- why the boundary is complete enough to classify absence.

An empty result is not proof unless the searched boundary affirmatively covers
the requested domain.

## Failure conditions

Evidence will be rejected if it is:

- a claimant-authored replacement;
- a digest without original bytes;
- an unauthenticated summary;
- a redaction that removes identity, boundary, or authorization;
- a conflicting duplicate with no way to choose the original;
- an inferred effect based only on an exit code or stop bit;
- an unknown cost converted to zero;
- overlapping time intervals counted twice;
- an absence claim without a documented search boundary;
- or language attempting to grant reconciliation or replay authority.

## Operator decision boundary

External evidence can only answer: **where is the original record?**

It cannot:

- set spendability;
- release holds;
- mutate accounting;
- authorize reconciliation;
- authorize replay;
- admit contracts;
- promote software;
- merge branches;
- or push commits.

The trusted evaluator and an independent reviewer must later classify any
supplied evidence, and the operator must separately authorize every protected
operation.
