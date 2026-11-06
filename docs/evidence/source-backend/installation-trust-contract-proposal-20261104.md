# Installation import trust contract — proposed dependency closure

**PROPOSED — NOT ACCEPTED; NO SCHEMA, IMPLEMENTATION OR PRODUCTION AUTHORITY.**

This bounded design extends `installation-cycle-v2-spec-20261104.md`, verified
SHA-256 `599503fffda03576882642c57928a76d66659c2a28e0ee4518f6d1b5c5f21027`.
It proposes definitions for that document's unresolved import/history/custody
interfaces. It does not change its existing record fields, accept its schemas,
incorporate the sibling authority-records proposal, or claim live provisioning.
Inspected HEAD: `b2aab47`, `419c312`, `2b60146`; `docs/findings/` absent.

## 1. Representation and scope

Inherit C, B, D, H, N, U, I, V, bounds, canonical-byte rejection and closed-record
rules from the pinned proposal. All fields are required; no additional fields.
Every `*_bytes_sha256` below means B of the complete canonical original record.
The legacy spelling `import_review` in ApprovalV2 resolves exclusively to
B(ImportIntentReviewV1); it is not a semantic upgrade of an old ImportReview.
`issuance_history_sha256` resolves exclusively to B(IssuanceHistoryV1).
`root_import_receipt_sha256` resolves exclusively to B(RootImportReceiptV1).
Predecessor references remain the base proposal's D activation identifier.
No record includes its own hash or a detached authentication envelope hash.
All evidence references require an accepted type-specific resolver; opaque hashes
without that resolver block acceptance and execution.

## 2. ImportIntentReviewV1 (entry-local, before registry)

Exact schema:

```text
{schema:"capstone-import-intent-review-v1", phase:"pre-registry-import-intent",
 verdict:"pass"|"fail", installation_id:H, generation:N, ledger_lineage_id:H,
 installation_core_sha256:H, authorization_bytes_sha256:H,
 campaign_spec_sha256:H, campaign_id:I, issuance_id:H,
 receipt_max_age_ns:N, floors:H, history_checkpoint_bytes_sha256:H,
 reviewer_identity_sha256:H, reviewed_at_ns:N, expires_ns:N,
 evidence:[H], blockers:[I]}
```

Generation >=1. Evidence/blockers are sorted unique sets. Pass requires nonempty
evidence, empty blockers and reviewed_at_ns < expires_ns. Receipt age must satisfy
the independently approved timing policy; this record cannot set a weaker bound.
Verifier joins every candidate ApprovalV2 field except `import_review` to this
record and joins authorization/core/spec/operator/floors to the pinned proposal.
The core D value, authorization B value and checkpoint identity must match exactly.
The issuance/campaign mapping is prospective: review grants no issuance and does
not insert it into committed history. History check must reject already used IDs
or other existing liabilities incompatible with the proposed entry. Execution
idempotency remains a separate existing-ledger operation returning original bytes.

The reviewer independently retrieves original authorization, core, spec and
checkpoint through authenticated custody. It must have the provisioned
`installation-import-intent` role. UID322 alone is insufficient. No registry,
descriptor, final review, receipt or activation reference is permitted, directly
or transitively through evidence. Review cannot depend on its consuming approval.
Final-pair review checks that every entry has this independently authenticated,
unexpired review; a candidate-provided pass object is not evidence.

## 3. Complete history and checkpoint (before candidate core)

Exact evidence container:

```text
{schema:"capstone-issuance-history-v1", installation_id:H,
 ledger_lineage_id:H, sequence:N, tip:H,
 ledger_prefix_bytes_sha256:H, issuance_index_bytes_sha256:H,
 original_bundle_index_bytes_sha256:H, liability_evidence_bytes_sha256:H,
 lineage_origin_evidence_bytes_sha256:H}
```

This is IssuanceHistoryV1. Referents are immutable, complete checkpoint-bounded
exports in existing independently accepted ledger/index/bundle/accounting
formats, not invented replacement ledger rows. Export hashes cover entire exact
bytes, including ordering and framing. An absent accepted canonical export format
is a blocking external dependency, not permission to serialize arbitrarily.
Large exports are bounded streams in those formats; no JSON list-limit exemption,
truncation, omission or unapproved sharding is implied by this container.

Exact attestation:

```text
{schema:"capstone-history-checkpoint-v1", installation_id:H,
 ledger_lineage_id:H, sequence:N, tip:H, issuance_history_sha256:H,
 predecessor_activation_sha256:H|null, authority_identity_sha256:H,
 captured_at_ns:N, evidence:[H]}
```

This is HistoryCheckpointV1; evidence is sorted, unique and nonempty. The
provisioned `ledger-history-attestor` attests independently checked full history,
not merely a hash supplied by the operator. Each pair-review/receipt/activation
checkpoint and history hash must equal this record's values. A successor's
predecessor must be current root activation; genesis requires independently
accepted lineage-origin evidence. Empty files or a caller-declared genesis fail.
All authoritative history from genesis through sequence/tip is replayed and the
indexes are independently rebuilt and compared, including intent-only holds,
unknown outcomes, stopped grants, original bundles and consumption. Account for
prior installations/global liabilities through separately accepted accounting
evidence; a new installation identity never resets allowance.

The history and exports cannot reference this checkpoint or the candidate import.
References to already committed predecessor activations are backward edges only.
This attestation alone does not prove freshness: the installer checks the actual
current ledger, authoritative root predecessor and complete export provenance.

## 4. RootImportReceiptV1 (durable preparation, not activation)

Exact schema:

```text
{schema:"capstone-root-import-receipt-v1", phase:"prepared-installation-import",
 installation_id:H, generation:N, ledger_lineage_id:H,
 installation_core_sha256:H, descriptor_bytes_sha256:H,
 registry_bytes_sha256:H, pair_review_bytes_sha256:H,
 predecessor_activation_sha256:H|null,
 ledger_checkpoint:{sequence:N,tip:H}, issuance_history_sha256:H,
 history_checkpoint_bytes_sha256:H, installer_identity_sha256:H,
 prepared_at_ns:N, expires_ns:N, import_operation_id:H}
```

The trusted installer assigns a random unique operation ID in its durable journal;
callers cannot select/reuse it. Prepared_at < expires. All identity, predecessor,
pair, core, checkpoint and history joins are exact. Receipt preparation means all
referenced immutable objects and independent review authentication have been
verified and durably staged, not that the active pointer changed. It has no
ActivationV2 hash, pointer hash, publication proof or downstream reference.
Preparation/retry never renews review windows or manufactures a fresh issuance.

ActivationV2 references B(receipt) and the same exact pair/history/predecessor.
Its activated_at_ns must be trusted installer time in the intersection of receipt,
pair-review and every import-intent review validity window, with preparation no
later than activation. Root publication authenticates those bytes and timestamp;
the timestamp alone proves nothing. Review/receipt expiry controls import, not
automatic retroactive deactivation of an already authenticated committed import.
Existing execution authorization/JIT freshness checks continue independently.

## 5. Authentication, identity and immutable custody

Required interface: `resolve_authenticated(expected_type, B, required_role,
trusted_installation, trusted_lineage)` returns the exact immutable bytes plus
independently verified provenance, or fails. The caller cannot supply a trust
root, store path, accepted role, UID mapping or verification-success boolean.
Hash equality proves integrity only. Root-owned copies of unauthenticated caller
objects remain unauthenticated.

Identity hashes identify independently provisioned authority records with exact
role/scope and validity/revocation policy. Installer, import-intent reviewer,
final-pair reviewer and history attestor are separately authorized capabilities;
collapsing those roles requires explicit independent acceptance. Runtime roles
and UID322's actual-plan verification confer none of them. Installation identity
is root-assigned; operator UID is never an installation, reviewer or lineage ID.

Provenance may be a provisioned immutable authority-owned store or independently
verified detached signature, but the deployment MUST select and pin one exact
mechanism per record type before acceptance. Signature variant requires pinned
algorithm, domain-separated type/role/B/scope message, key bootstrap, revocation
and historical-verification rules; this proposal selects none by assumption.
Authentication evidence is external to the hashed payload. It may bind payload B
but no earlier payload hashes that evidence. Review evidence itself cannot hide a
forward reference. Trust-root rotation or revoked/unknown provenance fences until
an independently approved policy resolves it; do not trust current filesystem
ownership as proof of historical authentication.

Production stores and pointer are fixed provisioned locations opened through
retained no-follow handles with all base ownership/mode/ACL/ancestor/single-link
and replacement checks. Exact locations and platform primitives remain a blocking
deployment profile; no candidate-controlled paths or generic temp fallback.
No protected path, including metadata, was accessed to draft this contract.

## 6. Publication, fencing and recovery state machine

Root maintains a durable per-installation administrative journal outside all
runtime/reviewer write authority. Proposed states are FENCED -> PREPARED ->
COMMITTED -> ACTIVE. They are installer states, NOT new backend ledger events.
Each transition is authenticated, monotonic and bound to the operation ID and
current predecessor. Any ambiguity stays FENCED; absence is never genesis.

1. Acquire the exclusive administrative lease and fence every issuance/dispatch
   owner. Drain live work; unresolved execution or owner acknowledgments block
   activation. Preserve all existing holds. Freeze ledger writes while taking the
   checkpoint and producing candidate/import/final reviews. Timeout requires
   separately authorized abandonment/unfencing, not partial publication.
2. Validate the actual complete ledger is still exactly the checkpoint, not just
   a descendant, before preparation and commit. This stricter activation rule
   avoids reviewing one history and publishing another. Runtime after activation
   may append and must prove descent/replay under the base rules.
3. Persist immutable dependencies, authenticated provenance and receipt before
   any consuming activation; fsync objects and containing directories. PREPARED
   binds receipt B. Build and durably persist exact ActivationV2 bytes. Journal
   COMMITTED binds B(activation), D(activation), receipt B, operation ID, previous
   high-water generation and new generation. No backward edit to receipt.
4. Atomically compare predecessor/high-water and publish the trusted active
   pointer to that committed activation; durably sync its directory. Only after
   journal/pointer/ledger agree and stale handles are invalidated may ACTIVE be
   recorded and owners unfenced. Runtime requires all three to agree; pointer
   existence alone never permits execution. Generation must be predecessor+1.

Cross-file publication is not assumed atomic. Any crash cut, partial fsync,
conflicting predecessor, live owner, unknown lease state or pointer/journal
disagreement fences. Recovery is an explicitly authorized root procedure with an
independently authenticated decision binding the operation ID, observed journal,
pointer, activation and checkpoint evidence. It may finish publishing the exact
already committed activation only after revalidation and quiescence; no regenerated
bytes, changed timestamps, reminted IDs or automatic repair. Abandoned preparation
is retained; its IDs/provenance cannot silently be recycled. A committed generation
is never rolled back or reused, even if publication did not finish.

Recovery of lost/restored high-water state requires an independently maintained
freshness/rollback witness. Local signatures and hash chains alone cannot detect
restoring a mutually consistent old disk snapshot. No witness, stale witness or
uncertain global liabilities means continued fencing; a new installation ID does
not bypass it. Witness mechanism and recovery approval identity are unselected
external dependencies. Root compromise is outside the assumed threat model.

## 7. Acyclicity and compatibility invariant

Topological order: accepted preexisting provenance/lineage and frozen ledger
exports -> history -> checkpoint -> core -> authorization -> import-intent review
-> registry -> descriptor -> final-pair review -> prepared receipt -> activation
-> commit journal/pointer/publication evidence. Prior generation records can be
ancestors; never same-generation downstream evidence. Checkpoint/core need not
hash each other. Final review's history hash joins through resolved intent reviews;
receipt binds the checkpoint explicitly. No self-hash or hash fixed point exists.

Do not add these records to InstallationV3/CoreV2/P. Do not append an activation
event to the backend ledger or reinterpret existing issuance/journal schemas.
No old ImportReview, installation v1/v2, grants or approvals convert on read.
Only the exact new version tuple and authenticated dependencies may be accepted
by a future separately approved backend. Existing parsers and golden bytes remain
unchanged. All eleven gates, seven journeys, reservations, JIT, actual-plan,
postrun, stop and intent-only RecoveryRequired constraints remain mandatory.

## 8. Required fail-closed tests — design obligations, NOT RUN

- Canonical/type/bounds tests for each exact schema, every extra/missing field,
  duplicate keys, invalid Unicode, bool-as-int, expiry edges and byte mutation;
  golden B values and base D vectors. Deterministically construct the complete DAG
  twice; detect every direct/transitive same-generation back-edge in evidence.
- Change each intent mapping, authorization byte hash, core, checkpoint or role;
  reject before registry acceptance. Substitute old ImportReview/new fields or
  mixed versions; reject without fallback. Legacy golden bytes stay identical.
- Substitute a registry sharing core; replay a review from another installation,
  generation, lineage, operation or authority; forge a root-owned copy/pass JSON;
  wrong/revoked/unprovisioned signer or store must fail authentication.
- Truncate exports, omit an intent-only hold/bundle/index entry, fork ledger,
  replace lineage, restore empty DB or hide prior-installation liabilities; reject.
  Mutation after checkpoint and before commit fences, even if a valid descendant.
- Race activation and issuance/dispatch, two installers, stale open handles and
  predecessor changes. No dispatch crosses the fence; no competing generation
  publishes; unknown owner state blocks. Retained holds cannot be released.
- Crash/fault at every write, fsync, journal and pointer step including ACTIVE;
  test real permitted private-temp primitives. Inconsistency never auto-recovers.
  Authorized recovery preserves exact bytes and never decreases high-water or
  remints IDs. Full old-snapshot restore without an external fresh witness fences.
- Expired prepared receipt cannot activate; retry cannot renew evidence. Existing
  committed authority is not extended by receipt validation or repeated reads.
- Omit each required gate/provenance source individually; fail closed. Instrument
  all protected accesses including metadata and require zero in source fixtures.
  NONPRODUCTION test stores cannot certify live custody, provisioning or recovery.

## 9. Explicit remaining acceptance blockers

1. Independently accept this delta and its pinned parent, canonicalization source
   hash/golden bytes, and every type-specific review/source/policy resolver.
2. Freeze existing canonical ledger/index/bundle/liability/origin export formats;
   prove complete replay and uniqueness enforcement without backend schema changes.
3. Provision exact paths, role identities, authentication mechanism, revocation,
   trusted time/clock rollback policy and genesis/global-liability authority.
4. Specify platform-tested lease/fence acknowledgments, durable journal encoding,
   atomic compare/publication primitives, rollback witness and recovery approver.
   This state machine is a requirement, not evidence those primitives work.
5. Independently test implementation and separately authorize exact-target live
   qualification. No install, protected access, spendability, VM/replay, admission,
   reconciliation, hold release, production mutation, commit or push is authorized.

Until resolved: **GAPS_FOUND / implementation and activation blocked**. This file
is the only artifact changed for this assignment; no runtime tests were performed.
