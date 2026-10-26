# Spendability reconciliation evidence contract (GRRR-z3w9)

**Contract status: design and mandatory-evidence contract only.** This document
defines what a future, separately authorized accounting reconciler must prove
before it may report any non-null spendability result. It implements nothing,
changes no accounting state, and grants no execution authority. The independent
review basis is `SPENDABILITY_REVIEW: BLOCKED_MISSING_EVIDENCE`.

The current answer is therefore fixed:

```text
historical_unknowns = "unresolved"
spendable           = null
allowed_mutations   = []
execution_authorized = false
```

Current receipt and inventory data are insufficient. A future reconciler must
continue returning `spendable=null` until every mandatory evidence, historical
completeness, integrity, provenance, arithmetic, review, staging, and protected
operation gate passes. Clearing the stop bit, passing schema validation, or
showing that known encumbrance is below a ceiling is not spendability proof.

## Purpose and non-goals

### Purpose

This contract gives reviewers and any future implementer a fail-closed
specification for:

1. authenticating and freezing the complete accounting baseline;
2. proving the history that produced that baseline is complete;
3. binding every reservation, meter, pending hold, and overhead row to trusted
   provenance and exact source bytes;
4. deriving only conservative, integer, stage-aware resource conclusions; and
5. creating one-time, stale-resistant reconciliation evidence that cannot turn
   absence of evidence into an allowance.

### Non-goals

This document does not:

- implement, stage, install, or authorize a reconciler;
- mutate, upgrade, export from, or access the protected v3 accounting store;
- settle, release, reduce, or zero a reservation or unknown history;
- convert `null`, absent, stale, duplicate, ambiguous, or untrusted values to
  zero or another convenient value;
- create a new campaign, store, allowance, stage, currency, or ceiling;
- authorize replay, dispatch, guest/VM execution, admission, promotion,
  production mutation, merge, or push; or
- convert the completed stop-only v3 transition into spendability authority.

## Terminology

| Term | Contract meaning |
|---|---|
| **Baseline** | The exact immutable source set being reconciled: active binding, complete receipt ancestry, database bytes, schema, row inventory, metadata, and retained provenance. |
| **Reservation** | One durable request hold with `id`, idempotency `key`, request `binding`, `run`, `stage`, and bounded `maximum`. |
| **Settled reservation** | A reservation whose `actual` and `receipt` are both present and prove a trusted meter result. |
| **Pending reservation** | A reservation whose `actual` and `receipt` are both null. Its entire maximum remains held. |
| **Meter record** | The exact canonical body bytes whose SHA-256 receipt is stored with a settled usage value. A digest-shaped row alone is not issuer proof. |
| **Known encumbrance** | Exact integer sums of trusted settled actual usage plus full maxima of every pending row. It is a liability projection, not available balance. |
| **Unknown history** | Any event, cost, run, binding, issuer, measurement boundary, stop cause, or artifact that cannot be authenticated and placed in the complete lineage. It has no zero value. |
| **Spendability** | A future non-null decision only after every mandatory gate passes. Until then its sole valid value is JSON `null`. |
| **Reconciliation record** | A future one-time attempt record binding the exact baseline, code/toolchain, reviewer decisions, authorization, operation, result, and postcondition evidence. It is not a signature. |
| **Protected operation** | A separately authorized parent-mediated action against protected accounting state. No command or schema in this document is permission to perform one. |

## Current evidence boundary

The independently reviewed current facts are:

- v3 is read-only and fail-closed, with unresolved history and null spendability.
- `stopped=0`; this stop disposition alone grants no runtime writes or allowance.
- `allowed_mutations=[]` and `execution_authorized=false`.
- There are 11 reservations, all in POC scope.
- There are 8 metering rows whose validated execution usage totals
  208,265,788 execution-us.
- There are 3 pending reservations. Each has null `actual` and null `receipt`
  and a 300,000,000 execution-us maximum, so their pending maxima total
  900,000,000 execution-us.
- Known execution-us encumbrance is therefore
  208,265,788 + 900,000,000 = 1,108,265,788 for both POC and milestone scope.
- The reviewed aggregate reservation maxima total 3,300,000,000 execution-us.

These observations establish only known encumbrance. They do not establish the
completeness of the 11 reservations, trust in the 8 meter issuers or evidence
bindings, dispositions for the 3 pending rows, absence of historical overhead
or other costs, or usable headroom under either ceiling. Existing inventory
validation checks shape and some joins, but it is not a generic constraint
proof, issuer authentication, or historical completeness proof.

## Mandatory baseline evidence

A reconciliation input is admissible only when all of the following is present
and bound by canonical hashes:

1. **Exact active ancestry**: the v3 active binding, prior active binding,
   registration receipt, recovery intent, recovery receipt, and completion
   record in their exact required ancestry. Missing, extra, replaced, partial,
   or unexplained artifacts fail the baseline.
2. **Authenticated store identity**: campaign, store ID, prior-history receipt,
   protected directory, database path, filesystem device and inode, ownership,
   modes, ACLs, link count, and absence of symlinks or unexplained sidecars.
3. **Stable database snapshot**: exact database bytes and SHA-256, a read-only
   schema inventory, integrity result, journal mode, absence of journal/WAL/SHM
   sidecars, and proof that bytes did not change during capture.
4. **Exact schema fingerprint**: tables, indexes, triggers, views, column
   declarations, constraints, and canonical SQL text. An unexpected schema
   object or fingerprint mismatch is an integrity failure, not a migration
   opportunity.
5. **Complete row multiset**: every `reservations`, `metering`, `overhead`,
   `state`, and `store_identity` cell, including exact BLOB bytes and null
   placement, plus a digest over the canonical row multiset rather than only a
   row count.
6. **Toolchain and observer identity**: pinned interpreter, code, source and
   installer digests, reviewer/reconciliation principal, measurement tool,
   policy version, host identity, capture time, and parent-attestation chain.
7. **Quiescence evidence**: no unexplained writer or evaluator handle, a stable
   capture window, and coordination with the protected store's lock/exclusion
   protocol. Read-only observation must not weaken or bypass writer exclusion.
8. **Independent review record**: a review of this exact contract, future
   implementation diff, input schema, failure behavior, protected operation
   plan, and baseline fingerprint, with its own authenticated provenance.
9. **Exact operator decision**: a separately authenticated decision naming the
   bounded action and binding the implementation, review, baseline, row-set,
   and evidence-bundle hashes. Root ownership is only an attestation, not a
   signature and not authority.

Every item is a gate. The first failure or unknown prevents a non-null result.

## Historical completeness evidence

Before arithmetic can be interpreted, the complete lineage must answer:

- Which campaign, store, profiles, stages, ceilings, and prior-history receipt
  produced every row, and where each boundary began and ended?
- Why the historical stop occurred; when and how it was observed; what work,
  writers, meters, reviewers, cancellations, and failures were in flight; and
  exactly how the reviewed stop-only v3 transition was authorized and verified.
- Which run, dispatch, execution, cancellation, cessation, evidence export, and
  review artifacts correspond to every reservation, including null request
  bindings and all 11 current POC rows.
- What preparation, selector, execution, review, and other overhead was
  incurred, including time zones, units, clocks, overlap, and boundaries.
- What records or artifacts were lost, never created, retained elsewhere,
  truncated, or cannot be authenticated. Each such fact remains an explicit
  unknown with a conservative upper bound where one is proven.
- Whether any side store, duplicate ledger, replay, cancellation, refund,
  manual adjustment, or out-of-band event could affect this store's history.
- Whether every pending hold is still live, definitively expired without
  effect, interrupted with unknown effect, or otherwise disposed; each claim
  requires its own trusted evidence and cessation/result proof.

An empty table or zero count is not completeness proof. Absence of a recorded
cost is an unknown unless retained provenance affirmatively proves the empty
domain. No future result may collapse an unresolved history question to zero.

## Per-row evidence contracts

### Reservation evidence contract

For every reservation, the future input bundle must retain and authenticate:

- exact `id`, idempotency `key`, request BLOB, `run`, and `stage`;
- canonical maximum resource vector and original request bytes;
- authenticated requester, evaluator principal, profile, policy, and toolchain;
- request-binding bytes and their meaning, including proof that a null binding
  was valid for that historical path rather than missing data;
- dispatch/refusal/cancellation outcome, run relation, and monotonic operation
  history;
- current disposition: settled, pending, expired, interrupted, or unknown;
- every source row digest and the immutable baseline digest; and
- reviewer determination that the trusted history, not merely the row shape,
  supports that disposition.

All 11 current reservations require this evidence. Their aggregate 3.3 billion
execution-us maximum does not excuse per-row provenance.

### Meter evidence contract

For every metering row, the future bundle must prove:

- exact body BLOB bytes and SHA-256 receipt;
- one unambiguous reservation join and matching usage representation;
- authenticated evaluator issuer, code and meter identity, and policy version;
- the event being measured, start/end semantics, clock, units, and time zone;
- trusted evidence artifact bytes referenced by the meter;
- execution and cessation/result evidence, including failed or cancelled work;
- no overflow, clipping, retry, duplicate count, or later mutation; and
- why this issuer and measurement method were trusted for that historical run.

The current eight meter rows are digest-shaped records. Their 208,265,788
execution-us total cannot release holds until issuer, request-binding, evidence,
and measurement-window provenance passes for each row.

### Pending reservation evidence contract

A pending disposition requires a separate evidence chain proving:

- `actual=null` and `receipt=null` occur exactly as a pair;
- the original maximum remains fully held;
- the request was or was not dispatched, with exact operation outcomes;
- no paid, queued, running, retried, or late-settling effect remains;
- trusted cessation and final observation evidence, where completion is claimed;
- why expiration, cancellation, failure, or non-disposition is authoritative;
- all stale handles and idempotency retries are accounted for; and
- the baseline row and every referenced artifact remain unchanged.

Each of the three current 300,000,000 execution-us holds needs this evidence.
Until then, the full 900,000,000 execution-us hold remains. Unavailable or
ambiguous evidence can never settle, release, or reduce it.

### Overhead evidence contract

For every overhead row and every claimed-empty category, evidence must identify:

- exact key, category, duration, units, clock, and time zone;
- requester, observer, activity, and relation to preparation/selection work;
- whether intervals overlap and whether they are wall, CPU, review, or mixed;
- exact retained source bytes and operation/evidence joins; and
- why the category inventory is complete for the campaign and history.

There are currently zero recorded overhead rows. Zero is not historical proof:
absence of overhead evidence must keep completeness unresolved. Overhead is
disclosed separately and is not netted against execution usage or a reservation.

## Canonical JSON and field rules

Any future implementation must define one versioned canonical form before
creating receipts:

- UTF-8 JSON serialized as ASCII with lexicographically sorted keys, compact
  separators, no NaN or Infinity, and no trailing whitespace.
- Decode with duplicate-key rejection; missing and extra fields are failures.
- Preserve source BLOB bytes separately from decoded projections. A projection
  may add labels but can never replace source evidence.
- `sha256` fields are exactly 64 lowercase hexadecimal characters and bind the
  exact canonical or raw byte form named by the field.
- Resource vectors contain exactly `currency`, `money_cents`, `execution_us`,
  and `review_us`; currency is currently `USD`.
- Resource integers are nonnegative, less than 2^63, and have strict integer
  type: booleans are not integers. Every addition and ceiling comparison checks
  overflow.
- Identifiers use the approved bounded identifier grammar. Empty strings,
  traversal, control characters, executable content, and unknown formats fail.
- `spendability` is required to be JSON `null` whenever any mandatory evidence,
  completeness, or provenance gate is unresolved; it may be non-null only after
  every such gate passes.
- A historical reservation request `binding` may be null only when separate
  provenance evidence proves the authorization/request boundary. Without that
  evidence, the binding remains unknown and forces `spendable=null`.
- Reservation `actual` and `receipt` are a paired-present/paired-null field
  set: both must be present for a settled row or both null for a pending row;
  one-sided null is invalid.
- All other fields are non-null unless this contract explicitly defines a
  bounded null semantic for that field.
- Unknown actions, stages, currencies, categories, versions, states, labels,
  and statuses fail closed. Implementations must not default, coerce, repair,
  or normalize them.
- Every reconciliation record names its schema version, canonicalization
  version, baseline multiset digest, row digests, and exact code/toolchain.

## Exact joins, uniqueness, and arithmetic

### Joins and uniqueness

The following invariants are mandatory:

1. `reservations.id` is unique and `reservations.key` is unique.
2. `metering.id` is unique and `metering.reservation` is unique.
3. Every meter joins exactly one reservation. There is no orphan meter.
4. A settled reservation has exactly one bound meter row whose body names that
   reservation and whose SHA-256 equals the stored meter ID.
5. Reservation `actual` and `receipt` are both present or both null.
6. A non-null reservation receipt equals the joined meter ID.
7. Decoded meter `usage` canonically equals the reservation `actual`.
8. Reservation request BLOB fields exactly reproduce the row's `run`, maximum,
   and stage. Request-binding provenance is supplied outside the row when null.
9. Overhead keys are unique and category values are approved.
10. State and store identity produce exactly one approved row matching the
    active binding.
11. No row, meter, artifact, or schema object may have multiple plausible joins
    or dispositions. Ambiguity fails even when one candidate is digest-valid.

### Arithmetic

For each resource dimension `d` and cumulative scope `s`:

```text
known_encumbered[s,d] =
    sum(actual[d] for settled reservations in scope s)
  + sum(maximum[d] for pending reservations in scope s)
```

Rules:

- Use exact bounded integers only; reject overflow rather than wrap or clamp.
- Settled usage must not exceed its original maximum. An overrun is a hard
  failure and cannot be clipped.
- Pending maxima are included in every applicable scope until per-row evidence
  passes a separately reviewed disposition.
- Unknown history and unproven rows receive a conservative proven upper bound;
  with no proven bound, spendability remains null.
- Overhead sums are separate disclosure, not execution arithmetic and not a
  release of holds.
- `known_encumbered` above a ceiling is a baseline integrity failure. It does
  not become zero available budget.
- The current execution-us check must reproduce 1,108,265,788 for both scopes
  from admissible rows, but reproduction alone does not pass completeness.

## Conservative spendability derivation

A future decision may consider availability only if every baseline and
completeness gate passes. It must then derive, per stage and dimension:

```text
conservative_available[s,d] =
    approved_ceiling[s,d]
  - known_encumbered[s,d]
  - independently_proven_unknown_upper_bound[s,d]
```

Additional mandatory properties:

- Any negative value is an integrity/state failure, never zero availability.
- Any unresolved bound makes `spendable=null`, not a partial numeric remainder.
- Fresh work must pass both POC and milestone checks as applicable; a remaining
  milestone amount cannot bypass a POC cap.
- Separate overhead and review dimensions cannot be substituted for one another.
- A result is valid only for the exact baseline, row multiset, policy, toolchain,
  and authorization hashes recorded in the one-time attempt.
- The result is an accounting projection, not a dispatch lease and not replay
  authority.

For the current evidence, every completeness or provenance gate is unavailable
or unresolved, so the only valid result is `spendable=null`.

## Unknown and pending fail-closed rules

- Missing, malformed, stale, duplicate, ambiguous, late, unauthenticated, or
  partial evidence fails the affected gate and the entire non-null decision.
- A pending hold always contributes its full maximum.
- An interrupted or timeout outcome is unknown until operation identity and all
  effects are resolved; it never licenses duplicate effects.
- No null-to-zero conversion, best-effort join, row repair, schema migration,
  VACUUM, rebuild, retry, or automatic settlement is permitted.
- A repeated query may return the exact immutable prior decision only after
  revalidating the baseline; otherwise it is stale and must refuse.
- Passing schema validation, checksum shape, row counts, no-guest tests, or the
  stop-only recovery review cannot substitute for history and provenance proof.
- Error output must name the first failed mandatory gate and preserve all
  observed source evidence for independent review.

## POC-in-milestone scope

All POC charges count against both POC and milestone scope. Milestone-only
charges count against milestone but do not erase or reset POC usage. There is no
fresh store, campaign, allowance, stage, currency, or ceiling. The 11 current
POC reservations therefore produce the reviewed 1,108,265,788 execution-us
encumbrance in both scopes. Independent replay is POC-only and receives no new
POC-sized allowance merely by selecting or interpreting milestone scope.

## One-time and stale-resistant reconciliation records

Every future reconciliation operation must create:

1. an exclusive-create intent record before observation or any protected write;
2. a baseline claim binding active ancestry, database hash, schema fingerprint,
   canonical row-multiset digest, metadata, and provenance bundle hashes;
3. a code/toolchain claim binding the exact reconciler and dependency bytes;
4. an independent review decision bound to that implementation and baseline;
5. an exact operator authorization bound to the review, action, and hashes;
6. an outcome receipt containing every gate result, first failure, row joins,
   integer inputs and sums, decision, postcondition hashes, and uncertainty; and
7. a completion/postflight record proving whether the protected state remained
   unchanged or changed exactly as separately authorized.

Records must be immutable, append-only, durably published, and never overwritten.
Every record carries a unique attempt ID, exact baseline digest, and monotonic
creation context. Reuse against a changed active binding, database hash, schema,
row multiset, policy, toolchain, authorization, or wall-clock validity bound is
stale and must fail. An uncertain or partial operation records uncertainty and
blocks retry; it cannot be made idempotent by deleting or replacing evidence.
Protected records are attestations, not signatures; operator and reviewer
identity must be authenticated independently.

## Adversarial acceptance cases

A future implementation review must include at least these fail-closed cases:

| # | Adversarial input | Required result |
|---:|---|---|
| 1 | Missing active, registration, recovery, or completion artifact | Baseline failure; `spendable=null` |
| 2 | Changed database bytes, inode, owner, mode, ACL, link, or sidecar | Integrity failure; no repair |
| 3 | Unexpected schema object or fingerprint | Refuse before row interpretation |
| 4 | Duplicate reservation ID, idempotency key, meter ID, or meter join | Ambiguity failure |
| 5 | Orphan meter or receipt without settled reservation | Join failure; no adoption |
| 6 | `actual` null with non-null `receipt`, or the reverse | Invalid pairing |
| 7 | Actual or meter usage above maximum | Hard failure; no clipping |
| 8 | Noncanonical JSON, duplicate key, trailing bytes, or changed BLOB | Decode/byte mismatch failure |
| 9 | Boolean presented as integer, negative value, float, or overflow | Type/overflow failure |
| 10 | Unknown stage, currency, profile, category, action, or version | Fail closed |
| 11 | One or all pending rows omitted | Baseline incomplete; holds remain |
| 12 | Pending null changed to zero usage | Refuse and preserve full maximum |
| 13 | POC row omitted from milestone arithmetic | Scope failure |
| 14 | Valid digest but unauthenticated issuer, evidence, or measurement window | Provenance failure |
| 15 | Null request binding without historical authorization proof | Unknown binding; no spendability |
| 16 | Empty overhead treated as historical zero without completeness proof | Unknown history; `spendable=null` |
| 17 | Partial stop/recovery or interrupted-operation lineage | Recovery-required; no retry |
| 18 | Reused reconciliation record or changed baseline after authorization | Stale attempt failure |
| 19 | Counts/checksums match but row multiset or provenance differs | Refuse; count equality is not identity |
| 20 | Known encumbrance below ceiling with any unresolved gate | `spendable=null` |
| 21 | Exactly reproduces 1,108,265,788 execution-us from incomplete evidence | `spendable=null`; arithmetic is not completeness |
| 22 | All gates pass but no exact dispatch authorization is presented | Accounting projection only; no execution |
| 23 | Every otherwise accepted source shape retains one unresolved mandatory evidence, completeness, or provenance gate | Legitimate unresolved-gate decision; `spendable=null` |
| 24 | Pending row has both `actual=null` and `receipt=null`, with authenticated pending evidence and the full maximum retained | Legitimate paired-null pending row; hold remains at full maximum |
| 25 | Null historical request binding is supported by separate provenance proving the authorization/request boundary | Legitimate provenance-backed null binding; all other gates still apply |
| 26 | Null historical request binding lacks that separate provenance | Invalid null binding; remains unknown and forces `spendable=null` |
| 27 | Settled row has exactly one of `actual` or `receipt` null | Invalid one-sided null; refuse |
| 28 | Non-null `spendability` is returned while any mandatory evidence, completeness, or provenance gate is unresolved | Invalid non-null decision; must return `spendable=null` |

Tests must exercise both accepted source shapes and every failure above without
writing protected state. Mocks may exercise parsing only; they cannot establish
protected integration, historical provenance, or spendability.

## Implementation, review, staging, and protected-operation gates

Each gate is separate and requires new exact evidence:

1. **Contract gate**: independent review accepts this evidence contract and its
   fail-closed arithmetic; approval does not authorize code.
2. **Implementation gate**: exact bounded implementation authorization, tests,
   no-guest suites on both required interpreters, diff checks, explicit-path
   `pvg verify`, coverage, and independent exact-diff review all pass.
3. **Staging gate**: exact immutable code and record schemas are installed in the
   separately approved protected bootstrap location; ownership, modes, ACLs,
   ancestors, interpreter/toolchain identities, and hashes are independently
   verified before operation.
4. **Protected read gate**: separately authorized parent-mediated read-only
   baseline capture proves stable bytes, complete ancestry, quiescence, row
   multiset, and provenance. Failure blocks every later gate.
5. **Reconciliation decision gate**: an independently reviewed, exact operator
   authorization names the one-time action and binds every baseline and code
   hash. Until all mandatory evidence and completeness gates pass, the only
   allowed published decision remains unresolved/null.
6. **Protected mutation gate, if ever separately authorized**: exclusive writer
   exclusion, intent, exact bounded transition, synchronous durability, complete
   outcome receipt, postflight hashes, and unchanged-or-exactly-authorized state
   must be captured. No automatic retry is allowed after uncertainty.
7. **Independent postoperation review gate**: a fresh reviewer verifies raw
   artifacts, arithmetic, gate outcomes, absence of unexplained effects, and
   preservation of pending/unknown holds.
8. **Replay gate**: actual trusted reconstruction, spendability, fresh isolation,
   execution, receipts, and PM acceptance remain separate authorizations. None
   is granted by this contract or a reconciliation result.

## Explicit no-authority statement

This document has no operational authority. It does not authorize accessing or
mutating `/Library/GRRR`, opening the evaluator-owned store, implementing or
running a reconciler, clearing unknowns, settling or releasing holds, changing
ceilings, replaying work, launching a VM or guest, changing identities, staging,
admitting, promoting, mutating production, merging, or pushing. Current receipt
data is insufficient, and every future reconciler must keep returning
`spendable=null` until every mandatory evidence and completeness gate passes and
all separately required implementation, review, staging, and protected-operation
authorizations are proven.
