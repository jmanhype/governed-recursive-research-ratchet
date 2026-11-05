# Installation commitment cycle repair, specification v2

**STATUS: PROPOSED — NOT ACCEPTED, NOT IMPLEMENTATION OR EXECUTION AUTHORITY.**

This is a new delta for independent review, not a reinterpretation of accepted
bytes. Inputs: accepted base executable-backend v2, original JIT amendment, JIT
v3, integration corrections (in that increasing precedence), and the rejected
installation-commitment-cycle proposal. Existing approvals remain source-only.
The sibling authority-records proposal is NOT accepted or silently incorporated.
Worktree HEAD inspected: `b2aab47`, `419c312`, `2b60146`; `docs/findings/` absent.

## 1. Closed representation and version boundary

Specification revision v2 is NOT descriptor version v2: accepted
`capstone-installation-v2` already has different semantics. This proposal uses
`capstone-installation-v3`. Never dispatch on field presence, a caller flag or
successful fallback parsing. Each record has exactly the fields listed here;
reject extras, missing fields, duplicate JSON keys, floats, booleans as integers,
invalid Unicode and noncanonical bytes before semantic use.

`C` is the accepted base `common.canonical` byte encoding; freeze its source hash
and golden bytes at implementation acceptance. Parsing must round-trip to exactly
the input bytes under C. H is lowercase `[0-9a-f]{64}`; N is integer
0..9007199254740991; U is an integer `0 < U < 4294967295` excluding
320, 321 and 322. `raw` is canonical padded
RFC4648 standard base64 with no whitespace whose decode/reencode is identical.
Identifier I and Vector V retain their exact accepted base validators, not new
coercions. All JSON records max 16MiB, depth <40, at most 65536 nodes; wire inputs
also obey MAX_WIRE, with no splitting or truncation. Lists below max 256 unless
explicitly stated otherwise. Size checks precede allocation and identity checks
precede payload processing as required by the accepted transport.

`B(raw_bytes)=SHA256(raw_bytes)`; `D(tag,x)=SHA256(ASCII(tag)||0x00||C(x))`.
Every SHA result is H. B always means exact stored bytes, never a projection.
Every D tag below is literal and distinct. Schema and tag are both checked.
No selfhash fields are added to records. Hash references resolve exact original
canonical bytes of the expected type; absence or wrong type refuses.

## 2. Exact record schemas

Define P as this exact field set, all H except operator_uid:U:

```
operator_uid, source_manifest_sha256, runtime_manifest_sha256,
evaluator_manifest_sha256, runner_manifest_sha256, interpreter_sha256,
bootstrap_sha256, qemu_manifest_sha256, assets_sha256, corpus_sha256,
replay_catalog_sha256, replay_image_sha256, execution_profile_sha256,
policy_sha256, accounting_binding_sha256, baseline_endorsement_sha256,
floors_sha256, timing_policy_sha256, reviewer_manifest_sha256
```

InstallationCoreV2 has exactly `{schema:"capstone-installation-core-v2",
installation_id:H, generation:N, ledger_lineage_id:H, ...P}`. Generation >=1;
installation_id is a separately root-assigned random 256-bit installation identity,
not a user identifier, pathname or descriptor hash. ledger_lineage_id is the
preexisting independently accepted lineage identity, never inferred from an empty
database. `core_hash=D("installation-core-v2",core)`.

InstallationV3 has exactly `{schema:"capstone-installation-v3",
installation_id:H,generation:N,ledger_lineage_id:H,...P,
authorization_registry_sha256:H}`. Projection to core changes ONLY the schema
literal to `capstone-installation-core-v2` and omits ONLY the registry field.
This is a typed constructor, not arbitrary JSON field stripping. Its computed
core_hash must equal every selected authorization's commitment.

AuthorizationV2 has exactly:

```
{schema:"capstone-authorization-v2", action:"capstone-execute",
 operator_uid:U, campaign_spec_sha256:H, baseline_endorsement_sha256:H,
 installation_core_sha256:H, installation_id:H, generation:N,
 ledger_lineage_id:H, not_before_ns:N, expires_ns:N, maximum:V,
 leaf_ids:[H], review_anchor:H}
```

There is NO installation_sha256 field. leaf_ids follow approved spec index order,
are unique and exhaust exactly that spec; window is nonempty, maximum equals the
complete finite spec maximum. Static review/JIT procedure, source review and human
approval remain mandatory separate authenticated provenance, not hash-shaped
assertions. review_anchor retains its accepted meaning; absent concretely accepted
record-resolution rules block implementation acceptance, not authorize guessing.

ApprovalV2 has exactly:

```
{schema:"capstone-approval-v2", authorization_sha256:H, authorization_raw:raw,
 campaign_spec_sha256:H, campaign_id:I, issuance_id:H,
 receipt_max_age_ns:N, floors:H, import_review:H}
```

RegistryV2 has exactly `{schema:"capstone-approval-registry-v2",
installation_id:H,generation:N,ledger_lineage_id:H,installation_core_sha256:H,
entries:[ApprovalV2]}`. Entries are nonempty, sorted by authorization_sha256;
authorization hash, campaign_id and issuance_id each unique. Entry raw bytes must
be AuthorizationV2 and B(decoded raw)==authorization_sha256. All joins (spec,
operator, baseline, floors, core, generation, lineage, finite leaves and limits)
must match; registry fields cannot override authorization fields.

`import_review` retains only approval of the PRE-registry import intent and its
entry's authorization/spec/issuance mapping, never final-pair provenance. Its
accepted resolver must not require this registry or descriptor hash: otherwise
the cycle remains and this proposal fails acceptance. No old ImportReview record
gets a new meaning. A separate, newly accepted typed import-intent record is
required if the current resolver lacks those semantics. The exact schema of that
record is an explicit dependency in §7, not a runtime fallback.

FinalPairReviewV2 has exactly:

```
{schema:"capstone-installation-pair-review-v2", phase:"final-installation-pair",
 verdict:"pass"|"fail", installation_id:H, generation:N, ledger_lineage_id:H,
 installation_core_sha256:H, descriptor_bytes_sha256:H, registry_bytes_sha256:H,
 predecessor_activation_sha256:H|null, ledger_checkpoint:{sequence:N,tip:H},
 issuance_history_sha256:H, reviewer_identity_sha256:H,
 reviewed_at_ns:N, expires_ns:N, evidence:[H], blockers:[I]}
```

Evidence and blockers are sorted unique sets. Pass requires empty blockers,
nonempty evidence, nonempty time window, and independently accepted full-history
issuance/custody evidence. reviewer_identity_sha256 resolves an independently
provisioned review authority; no candidate-selected reviewer identity. UID322's
actual-plan verifier role alone grants NO installation-review or import authority.

ActivationV2 has exactly:

```
{schema:"capstone-installation-activation-v2", installation_id:H,generation:N,
 ledger_lineage_id:H, descriptor_bytes_sha256:H, registry_bytes_sha256:H,
 pair_review_bytes_sha256:H, predecessor_activation_sha256:H|null,
 ledger_checkpoint:{sequence:N,tip:H}, issuance_history_sha256:H,
 activated_at_ns:N, root_import_receipt_sha256:H}
```

Pair-review and activation identifiers are respectively
`D("installation-pair-review-v2",review)` and
`D("installation-activation-v2",activation)`; fields ending bytes_sha256 use B,
not those identifiers. predecessor_activation_sha256 uses the D identifier.
RootImportReceipt is external evidence, authenticated by the trusted installer,
binding the exact final descriptor/registry/review byte hashes and predecessor,
generation, lineage and checkpoint, but NOT the resulting ActivationV2 hash.
It cannot contain a forward reference to activation. Its independently accepted
schema/custody interface is a prerequisite, not defined by this source proposal.

## 3. Construction DAG and final-pair provenance

Order: accepted source/policy/static evidence and lineage checkpoint -> core ->
finite AuthorizationV2 -> independent entry import-intent review -> RegistryV2 ->
InstallationV3 -> independent FinalPairReviewV2 -> root import receipt ->
ActivationV2 -> trusted active-generation pointer. Each arrow hashes only earlier
immutable bytes. No earlier node contains a downstream review, activation or
pointer hash. Final-pair review is deliberately outside descriptor and registry.

The reviewer must obtain the exact pair through independently authenticated
custody, validate the entire graph and finite authority, and produce the review in
its independently controlled immutable store. Root import verifies that review
through that store, not operator-supplied JSON. Runtime verifies root-established
immutable custody, exact hashes, approved reviewer identity and active-generation
provenance. File existence, root-looking fields, copied reviews, caller booleans,
repository fixtures and matching core hashes cannot satisfy these checks.

Installation, registry, final review, activation, root import receipt and active
pointer must be opened by fixed root-established no-follow retained handles with
the accepted ownership/mode/ACL/single-link/ancestor and replacement checks.
No path/UID/trust-store override. Exact paths, provisioned authority identities,
receipt authentication and atomic pointer protocol require a separately accepted
installation contract; runtime is unavailable until that contract exists.

## 4. Generation, ledger lineage and replay rules

Trusted root activation state is outside operator/evaluator/broker/reviewer write
authority. It remembers the highest activated generation and exact activation D
identifier per installation_id. A descriptor's own generation is NOT a monotonic
oracle. Root is a trust assumption, not an adversary this design claims to defeat.
Restoring the trusted root activation state is a separately authorized recovery;
if its freshness or rollback status is uncertain, fence execution.

Genesis requires independently approved genesis lineage evidence and generation
1 with null predecessor, not a fresh empty DB chosen by a factory. Successor must
be previous generation+1, same installation_id and ledger_lineage_id, and refer
to the exact current activation. Root import serializes activation under its
exclusive administrative lease; objects durable before references, root pointer
atomic and directory-fsynced. Crash, conflicting predecessor or uncertain commit
fences execution pending separately authorized recovery; no automatic remint or
pointer repair. Activation cannot run while old-generation work remains live or
uncertain; complete quiescence and retained unresolved holds are prerequisites.

Every factory open, issuance and preclaim/prelaunch check compares the actual
active pointer and exact pair, not a cached core. Generation advance invalidates
old handles; administrative activation requires all runtime owners fenced first.
Replayed lower/equal generation with different bytes refuses; re-reading identical
active bytes is read-only validation, not new issuance or approval extension.
An unapproved registry substitution sharing the core fails final-pair provenance.
An entire copied pair on another installation or lineage fails trusted identity.

The current ledger must independently validate chain and complete issuance index,
and descend from the exact approved checkpoint (sequence AND tip). Same lineage
string or tip alone is insufficient. issuance_history_sha256 commits the complete
canonical independently reviewed issuance-history evidence at that checkpoint;
all subsequent issuance/consumption/stop/unknown records are replayed and retained.
Missing, truncated, divergent, empty, replaced or restored ledger refuses. Across
generations retain authorization, issuance_id, campaign_id and grant uniqueness,
original bundles, consumption, stop and intent-only holds. Never regenerate IDs
to bypass prior use. Changing installation_id does not create a clean allowance:
new installation provenance must account for prior global liabilities and lineage.

Existing backend/journal schemas, version-1 Ledger envelope, issuance algorithm,
receipt-derived anchors, intent-only RecoveryRequired and stored-byte idempotent
export remain unchanged. No new ledger schema or hidden activation event is
authorized here. If those existing rows/replay cannot enforce the stated joins,
implementation must stop for a separately reviewed delta, not omit them.

## 5. Compatibility and mandatory boundaries

The new backend accepts ONLY the tuple InstallationV3/CoreV2/RegistryV2/
ApprovalV2/AuthorizationV2 plus authenticated final review and activation v2.
Mixed tuples, old schema with new fields, new schema with old fields, unknown
versions and missing discriminator refuse. Legacy v1 and accepted installation
v2 parsers retain their old meanings and remain isolated; no conversion on read,
re-signing, auto migration, fallback authority or reuse of old execution grants.
Existing source approval does NOT approve this schema delta. Separate design,
implementation, PM and exact-target live approvals are all still required.

All eleven gates remain: source_environment_identity, isolation,
protected_asset_integrity, baseline_correctness, trusted_observation,
independent_replay, specification_traceability, evidence_integrity_currency,
budget_state, reviewer_outcome, action_specific_human_approval. All seven original
capstone journeys remain. Static, actual-plan and postrun reviews stay distinct;
JIT current-anchor checks, peer identities, crash fencing, stop semantics,
accounting caps/liabilities and reservation-before-dispatch remain mandatory.
No protected access (including metadata), install, schema activation, spendability,
reconciliation, stop release, VM/replay, admission, promotion, production change,
commit or push is granted. No migration plan is authorized by this document.

## 6. Required acceptance tests (NOT RUN; design obligations)

1. Golden canonical bytes and B/D vectors for every new schema: NUL framing,
   tag/schema distinction, sorted entries, base64, duplicate keys, depth/size,
   invalid Unicode, integer bounds, bools, nulls, unknown fields and versions.
   Construct two identical graphs deterministically without hash fixed points.
2. Parameterized mutation of EVERY P/core field, identity, generation and lineage
   breaks matching authority. Projection omits exactly registry and replaces only
   schema; added/removed fields fail before hashing. Raw byte mutation fails B.
3. Each mixed old/new tuple refuses without fallback. Existing v1/v2 golden
   fixtures preserve original hashes/semantics. No old grant is reinterpreted.
4. Same core with alternate registry, reordered/duplicate entry, substituted raw
   auth, changed issuance mapping, missing auth or different final pair refuses.
   Even a valid alternative pair requires its own independently retrieved review
   and active root provenance; copied JSON is never sufficient.
5. Reject wrong reviewer custody/identity/phase, fail verdict, nonempty blockers,
   expired or missing reviews/receipts, wrong pair hashes and a root import receipt
   that does not bind exact bytes. Prove pre-import evidence has no forward hash.
6. Copy whole valid graph to another trusted installation/lineage; replay old
   generation, forge high generation, fork predecessor, race two activations,
   replace pointer, restore old root state: reject or fence, never execute.
   Run crash cuts before/after each fsync/reference publication; no auto repair.
7. Empty/divergent/truncated/restored ledger, wrong checkpoint sequence/tip,
   incomplete issuance history, duplicate issuance across generations, old stopped
   campaign, intent-only issuance and partial accounting all refuse new authority.
   Repeated committed issuance returns original bytes, no timestamp renewal.
8. Generation change while a handle is open or between observation and dispatch
   refuses; activation cannot race live/uncertain owners. Complete retained holds
   and global liabilities are required even for a newly assigned installation_id.
9. Remove each of eleven gates individually; remove JIT/source/static/result
   provenance individually: fail closed. Final pair acceptance never substitutes
   human execution approval, live qualification or runtime evidence.
10. Tests use only explicit NONPRODUCTION private-temp stores and real permitted
    local process/SQLite primitives, never patch production identity checks.
    Instrument all protected-path operations, including metadata; zero accesses
    required. Source tests cannot certify root provisioning or live activation.

## 7. Unresolved dependencies and acceptance stop conditions

This specifies the acyclic commitment and rejection rules, not a complete live
installer. Independently approve exact ImportIntentReview/RootImportReceipt and
issuance-history evidence schemas, trust bootstrap/custody, fixed paths, authority
identities and durable activation/recovery protocol before implementation relying
on them. Resolve source/static/policy review schemas separately; the sibling
proposal cannot supply accepted authority. Freeze canonicalization vectors and
confirm existing issuance index can enforce every join without schema changes.
Absent any item: GAPS_FOUND / implementation blocked, not permissive defaults.
This proposal does not claim those dependencies are implemented or satisfied.

No executable tests or runtime operations were performed for this document.
