# Spendability evidence-gap remediation design (GRRR-z3w9 Stage B)

## Status

This is a design and evidence-gap plan only. It grants no authority, does not
access or mutate `/Library/GRRR`, does not write spendability, does not
reconcile, and does not authorize replay, promotion, admission, production
mutation, merge, or push.

The input is the independently approved Stage A read-only baseline:

- Baseline SHA-256:
  `7608cbe6fc5f671b88573eca8b642ebfbc172f0cb920f75d60ca34cfa60c730a`
- Database SHA-256:
  `9c6ff2561a364ed982cd5477dd4b200c995da6910c9a17aa3d3c411a962d64f3`
- Active binding SHA-256:
  `9c5194dd12ff7601917fcccc293c459db09a41da8bad9fa9983cbef618d453f8`
- Evidence-contract SHA-256:
  `c179b6c9640a5d848f70bb9b7e6ac3833223a6c55ddf9bfa0b2dbe68a6c82b37`
- Independent Stage A review:
  `STAGE_A_REVIEW: APPROVED_BASELINE_CAPTURE`

The current result remains `valid=false`, `spendable=null`, with no allowed
mutation and no execution authority. Reproducing known encumbrance is useful
evidence, but it is not completeness or spendability.

## Measured starting point

Stage A retained:

- 11 POC reservations.
- 8 settled meter rows totaling `208,265,788` execution-us.
- 3 paired-null pending holds, each with a `300,000,000` execution-us maximum.
- No overhead rows.
- `state.stopped=0`.
- One store-identity row.
- Known execution-us encumbrance of `1,108,265,788` in both POC and milestone
  scope.

The unresolved pending reservation IDs are:

- `69523b39a51c44739114313c9325028c`
- `b34d8b9d106e42eab3a3e43daac98ddd`
- `d375ce6a2d924646bec71df64e939a5b`

Unknown history remains unbounded. It must not be represented as a zero upper
bound.

## Design principles

1. **Sidecar evidence only.** Historical rows are never edited, normalized,
   rebuilt, or migrated to make a validator pass.
2. **Raw bytes remain authoritative.** A projection may explain or map a row,
   but can never replace its BLOB, null placement, type, or source digest.
3. **Gate order is honest.** A later review cannot mask an earlier unresolved
   schema, quiescence, provenance, arithmetic, or completeness gate.
4. **No unknown-to-zero conversion.** Missing evidence retains the full hold
   and leaves `spendable=null`.
5. **No gate is inferred from an aggregate.** Known encumbrance, row count,
   checksum shape, and stop-bit state are not issuer authentication, interval
   coverage, overhead completeness, or authorization.
6. **Authority remains separate.** Every protected read, protected write,
   reconciliation decision, replay, admission, promotion, merge, and push needs
   its own exact operator approval.

## Evidence bundle

The future remediation bundle is an immutable sidecar named by the Stage B
plan as `spendability-evidence-bundle-v2`. It must contain:

1. The Stage A baseline hash and immutable source inventory.
2. A canonical raw-schema inventory.
3. A separately reviewed schema-compatibility mapping.
4. A quiescence record acquired under the store's approved writer-exclusion
   protocol.
5. Per-reservation provenance records.
6. Per-meter issuer/measurement records.
7. A disposition record for each pending hold.
8. A historical completeness map.
9. Overhead-domain coverage evidence.
10. Independent review and operator-decision references, initially unresolved.
11. A fail-closed outcome record.

The bundle records both a raw digest and a canonical projection for every
source object. It never substitutes the projection for the raw object.

## 1. Schema compatibility

### Gap

Stage A first fails `schema_fingerprint` because the approved validator's
version-one semantic fingerprint does not directly accept the captured SQLite
DDL and implicit index inventory. The baseline also correctly fails
`baseline_rows` and `row_joins` where the current projection differs from the
contract's synthetic representation.

### Remediation

Build a versioned, read-only compatibility adapter. It must produce both:

- `raw_schema_sha256`, a digest over the exact canonical SQLite inventory; and
- `mapped_contract_schema_sha256`, a digest over the separately reviewed
  contract-level object mapping.

The raw inventory must include:

- every `sqlite_master` kind, name, table association, and exact SQL text;
- `PRAGMA table_info` for every table;
- `PRAGMA index_list` and `PRAGMA index_xinfo` for every table;
- foreign-key and constraint inventories;
- SQLite application metadata relevant to schema identity;
- the ordering and canonicalization rules used by the digest;
- the captured database hash, device, inode, mode, owner, ACL, and link count.

The compatibility map must explain each semantic object:

| Contract object | Required raw evidence |
|---|---|
| `state` | exact `state` DDL and one-row `id=1` invariant |
| `reservations` | exact reservation DDL and column/nullability map |
| `metering` | exact meter DDL, primary key, and unique reservation constraint |
| `overhead` | exact overhead DDL and primary key |
| `store_identity` | exact store DDL and one-row identity invariant |
| `state_id_unique` | `id INTEGER PRIMARY KEY CHECK(id=1)` |
| `reservation_id_unique` | reservations primary-key index/constraint |
| `reservation_key_unique` | reservations key-unique index/constraint |
| `metering_id_unique` | metering primary-key index/constraint |
| `metering_reservation_unique` | metering reservation-unique constraint |
| `overhead_key_unique` | overhead primary-key constraint |

SQLite-generated index names are not stable semantics. They are evidence, not
the mapping itself. An unexpected object, missing constraint, altered DDL
fragment, changed nullability, or ambiguous mapping fails the schema gate.

### Acceptance

- The adapter is exercised against an exact synthetic copy of the Stage A raw
  schema inventory.
- Every semantic object maps to precisely one raw constraint.
- No extra schema object is ignored.
- The raw and mapped digests are distinct and both retained.
- Until independent review accepts this mapping, `schema_fingerprint` remains
  unresolved and `spendable=null`.

## 2. Quiescence and writer exclusion

### Gap

Stable file hashes and a process-name snapshot do not prove that no evaluator,
runner, recovery process, or SQLite writer could mutate the store during
capture. Stage A therefore correctly leaves quiescence unresolved.

### Remediation

The trusted parent must produce a quiescence record while holding the store's
approved exclusive launch/writer lock. The record must bind:

- lock path, device, inode, mode, owner, ACL, and link count;
- lock acquisition and release timestamps;
- lock identity before open, after open, and after release;
- proof that all approved store mutators use this same lock;
- database hash and metadata before lock acquisition;
- database hash and metadata while the lock is held;
- database hash and metadata after lock release;
- absence of journal, WAL, SHM, temporary, and sidecar files;
- UID/GID process inventory;
- the exact code and toolchain hashes used by the parent;
- failure behavior on lock contention or identity drift.

Hash stability alone is not enough. The capture is quiescent only if the lock
protocol is proven to cover every writer and the database identity remains
unchanged across acquisition, observation, and release.

### Acceptance

- The trusted parent proves exclusive writer exclusion, not merely idle process
  names.
- Database bytes and metadata remain stable throughout the locked window.
- A competing writer or lock failure produces an explicit fail-closed record.
- Until this record is independently reviewed, quiescence remains unresolved.

## 3. Per-row provenance

### Gap

The current reservation BLOBs name request bindings and maxima, and meter BLOBs
contain an evidence digest, reservation ID, and usage. They do not authenticate
the issuer, measurement window, source code, policy, request authorization, or
evidence-object bytes. Therefore all rows remain untrusted for reconciliation.

### Remediation

For every reservation, collect a sidecar provenance record containing:

- reservation ID, key, run, stage, maximum, binding, actual, and receipt;
- original request bytes and request digest;
- authenticated principal or service identity;
- issuer code, toolchain, policy, and runtime profile digests;
- approved request-authorization record;
- dispatch operation ID and idempotency key;
- start and end measurement boundaries;
- source evidence path and raw-byte digest;
- canonical projection digest;
- meter or settlement linkage;
- stop, cancellation, failure, or completion linkage where applicable;
- reviewer and capture references.

For every meter row, locate and hash the original evidence object named by the
meter's `evidence` digest. The record must prove that the trusted issuer created
the measurement under the approved identity and toolchain. A digest-shaped
field or source pointer alone remains untrusted.

Historical records cannot be retroactively authenticated by a new label. If no
original issuer evidence exists, the row remains unresolved and conservatively
encumbered.

### Acceptance

- Each of the 11 reservations has a unique provenance record.
- Each of the 8 meters has an authenticated issuer/measurement record.
- Every non-null request binding is reproduced exactly by the original request.
- Every null request binding has separate authorization-boundary proof.
- Every projected value is digest-bound to raw source bytes.
- Any ambiguity, duplicate candidate, unauthenticated issuer, or missing source
  leaves the row unresolved.

## 4. Pending-hold dispositions

### Gap

The three paired-null pending holds have maxima but no final observation,
cessation proof, dispatch outcome, stale-handle accounting, or baseline-identity
proof. They cannot be treated as zero usage or released.

### Remediation

Each pending reservation requires one disposition record:

1. **Live hold**: prove no dispatch completed, no cancellation occurred, the
   evaluator is stopped or otherwise unable to mutate the hold, and the full
   maximum remains encumbering.
2. **Expired**: prove the approved expiry policy, exact boundary, no effect,
   and unchanged baseline after expiry.
3. **Cancelled**: prove operator/request identity, cancellation operation,
   cessation, no effect, and durable receipt.
4. **Failed/not dispatched**: prove request outcome, error identity, operation
   completion, no unbounded residual process, and unchanged baseline.
5. **Unresolved**: retain the full maximum and leave spendability null.

Every disposition must bind:

- reservation ID and original maximum;
- request and idempotency identities;
- operation ID;
- final observation or explicit non-observation proof;
- process/group cessation where a dispatch occurred;
- evaluator stop/halt state;
- pre/post database hashes;
- stale-handle accounting;
- source artifact digests;
- independent review status.

No disposition may be inferred from `stopped=0`, a missing row, elapsed time,
or a supervisor exit code alone.

### Acceptance

- All three listed pending IDs have explicit disposition records.
- Each disposition is one of the approved outcomes above.
- Missing evidence selects `unresolved`, retains the full maximum, and leaves
  `spendable=null`.
- No pending hold is removed or settled by this Stage B design.

## 5. Historical completeness

### Gap

Known arithmetic does not establish the complete campaign boundary. Stage A
does not prove all prior runs, side stores, failed attempts, overlaps,
preparation costs, review costs, paid-service records, stop cause, or recovery
lineage.

### Remediation

Build a completeness map rooted in the exact active ancestry:

1. registration prior active binding;
2. registration receipt;
3. recovery prior active binding;
4. recovery intent;
5. recovery receipt;
6. recovery completion record;
7. current active binding;
8. current raw database snapshot.

For each lineage transition, retain authorization, implementation review,
baseline hash, before/after database identity, writer lock record, and unchanged
or exactly authorized postcondition.

The completeness map must enumerate:

- every campaign, store, profile, stage, ceiling, and prior-history receipt;
- every reservation and run mapping;
- every dispatch, cancellation, failure, stop, and replay operation;
- every preparation, selection, execution, review, and other overhead item;
- measurement windows, clocks, time zones, units, and overlap boundaries;
- every paid-service decision and proof;
- every side ledger, export, manual adjustment, refund, or replay effect;
- every failed or interrupted recovery attempt;
- every lost, truncated, never-created, or unauthenticated record;
- every store mutation surface and its authorization state.

An empty domain is complete only when retained provenance affirmatively proves
that no such record could exist in the covered boundary. Otherwise absence is
unknown. Unbounded unknown history leaves `spendable=null`.

### Acceptance

- Every Stage A source artifact maps to one lineage transition or is explicitly
  unexplained.
- Every one of the 11 current reservations maps to a complete request and
  disposition chain.
- Every historical transition is authorization- and identity-bound.
- Every overhead category has affirmative coverage or remains unresolved.
- No arithmetic result is called complete until this map passes review.

## 6. Overhead-domain completeness

The empty overhead table is not historical zero. For each category —
preparation, selection, execution, review, and other — the bundle must prove:

- the responsible process or actor;
- the covered time and campaign boundary;
- the source records checked;
- whether costs were zero, measurable, or unknown;
- how intervals overlap;
- the exact units and clocks;
- the tool and code hashes used to inspect the domain.

If no proven upper bound exists, the category remains unknown and contributes
no invented zero to availability arithmetic.

## 7. Arithmetic remediation

The version-two projection must calculate:

```text
known_encumbered[scope,dimension] =
  sum(settled actual[scope,dimension])
  + sum(pending maximum[scope,dimension])
```

It must also represent:

- each row contribution;
- overflow checks;
- stage-to-scope expansion;
- separately disclosed overhead;
- proven unknown upper bounds, initially null/unresolved;
- ceiling comparison;
- negative-availability failure behavior.

The current 11 POC rows reproduce `1,108,265,788` execution-us in POC and
milestone scope, but that calculation cannot become a spendability decision
until schema, quiescence, provenance, pending evidence, overhead, completeness,
review, and authorization gates pass.

## 8. Review and authorization gates

The bundle initially records:

- independent review: unresolved;
- operator decision: unresolved;
- authorization binding: unresolved;
- dispatch authorization: absent;
- allowed mutations: empty;
- execution authorized: false.

Before any reconciler implementation is accepted, an independent reviewer must
approve:

- this gap plan;
- the raw-schema compatibility map;
- the quiescence capture contract;
- provenance schemas and failure behavior;
- pending-disposition rules;
- completeness map;
- arithmetic rules;
- the exact future implementation diff and tests.

Only then may the operator separately authorize a protected read or bounded
implementation. A protected write or reconciliation requires another explicit
authorization and cannot follow from this design.

## 9. Fail-closed outcome

Until every mandatory gate passes, the only valid outcome remains:

```json
{
  "valid": false,
  "spendable": null,
  "allowed_mutations": [],
  "execution_authorized": false
}
```

The first failed gate must reflect the actual earliest unresolved evidence
condition. A missing independent review cannot hide an unresolved schema,
quiescence, row, provenance, arithmetic, or completeness gate.

## 10. Implementation sequence

1. Add no-protected-access unit tests for the machine-readable gap plan.
2. Implement the schema adapter against the retained Stage A raw schema.
3. Design the locked quiescence capture record.
4. Define provenance and pending-disposition sidecar schemas.
5. Define the historical completeness map.
6. Obtain independent review of this design.
7. Stop at the protected-read authorization boundary.
8. Only later, and only with separate authorization, collect protected evidence.
9. Only after complete evidence and review, propose a reconciliation decision.

This Stage B slice stops after step 6. It performs no protected access.
