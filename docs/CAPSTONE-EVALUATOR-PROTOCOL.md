# Source-only implementation status

This document contains the exact accepted first-slice contract below, SHA-256
`9b0f0f5639a1f2f07539a1b1e22d33bb67e88e2dc78fe58ecc9925f356aaf8ad`.
The embedded historical PROPOSED heading is preserved verbatim. Independent
first-slice review does not accept full GRRR-q3hp or authorize runtime execution.

## Implemented limits

All record validation proves data consistency only. Raw decision bytes/context
are supplied explicitly; no Git provenance, protected configuration, issuance,
ancestry, admission inventory, clock continuity, or live authority is attested.
No installed descriptor or backend exists in this slice. `production_client()`
pins UID320 but always refuses without touching protected paths. Explicit-peer
RPC and `test_service(root)` operate only in private `/private/tmp/grrr-wcwy-*`
fixtures using the actual unprivileged UID, not UID320/321 isolation proof.

Observe cannot truthfully fill required Receipt.grant_bytes_sha256 without an
issued grant. It therefore returns RecoveryRequired, not a counterfeit Receipt.
Unsupported version claims (including v4) return UnsupportedAccountingVersion:n;
version1 returns GrantUnissued with unknown history/null allowance. These are
refusals, not discovered accounting observations. Start always refuses, including
consistent counterfeit grants. Status/stop return Unavailable and claim no effect.
The accepted future Receipt format is validated but is not issued by this service.
No capability installation, accounting readers/writers, journal, migration,
reconciliation, grant issuance, VM/replay, or production operation is implemented.

## Public source APIs

- `decode_record(raw: bytes, kind: str) -> dict`
- `validate_record(value: dict, kind: str) -> dict`
- `content_digest(value: dict, field: str) -> str`
- `operation_id(grant_id: str, plan_sha256: str) -> str`
- `verify_bytes(raw: bytes, expected: str) -> None`
- `bind_inputs(request: dict, invocation_raw: bytes, decision_json_raw: bytes,
  decision_markdown_raw: bytes, *, request_id: str,
  reviewed_package_commit: str, output_root: str) -> None`
- `bind_grant(plan: dict, grant_raw: bytes, authorization_raw: bytes, *,
  operator_uid: int) -> None`
- `start_request_digest(request: dict) -> str`
- `bind_observation(plan: dict, *, nonce: str, service_epoch: str, anchor: dict,
  now_ns: int, operator_uid: int) -> None` compares retained context/window only;
  it does not attest clock continuity, current state, or issuance.
- `explicit_peer_call(path: Path, request: dict, *, expected_uid: int,
  timeout: float = 2.0) -> dict` (public fixtures only)
- `test_endpoint(path: Path) -> str` (lexical validation before metadata)
- `production_client() -> Client`; `test_client(root: Path) -> Client`
- `Client(root: Optional[Path], expected_uid: int)`;
  `Client.call(request: dict, *, timeout: float = 2.0) -> dict`
- `RefusalService(operator_uid: int)`;
  `handle(authenticated_uid: int, request: dict) -> dict` is a transport callback,
  not a standalone authentication or authorization API.
- `test_service(root: Path) -> TestService`; `TestService(root: Path)`;
  `TestService.close() -> None` closes both ephemeral servers.

`./scripts/test-story evaluator-contract` is a source-only suite. Zero tests,
skips, failures or errors exit nonzero. Existing runtime modes are untouched.
All full-capstone gates remain NOT-RUN. Test results do not establish allowance,
spendability, installed endpoint integrity, cessation or settlement.

## Source-only journal prerequisite (GRRR-yt6a)

This later slice adds an **unwired local journal**, superseding only the earlier
statement that no source journal exists. It does not change the refusing service,
install a backend/schema, issue grants, or complete the driver/capstone contract.
`capstone_journal_schema.CORE_SQL/JOURNAL_SQL` declare exact source schema; there
is deliberately no production migration, empty-registry fallback or issuance API.

`open_existing(ledger: Ledger) -> Journal` requires actual UID320 before touching
the supplied trusted Ledger. It validates preinstalled schema, core hash chain,
idempotency correspondence, original preissued Grant bytes and replayed journal
state. It performs no filesystem open, DDL or repair. The existing ledger owner
must supply the trusted connection; Python objects are not an in-process sandbox.
The distinct `open_public_fixture(ledger, directory)` factory only accepts private
`/private/tmp/capstone-journal-fixture-*` public test directories, with lexical
rejection before metadata. It does not pretend that actual host UID501 is UID320.

Public Journal methods:

- `claim(start: dict, authenticated_uid: int) -> JournalRecord`
- `record_reserved(operation_id: str, reservation: str) -> JournalRecord`
- `mark_dispatch_pending(operation_id: str) -> tuple[JournalRecord, Optional[DispatchPermit]]`
- `request_stop(operation_id: str, authenticated_uid: int) -> JournalRecord`
- `status(operation_id: str, authenticated_uid: int) -> JournalRecord`

`JournalRecord` is frozen local data: operation_id, grant_id, plan_sha256,
start_request_sha256 (hex digest strings), operator_uid (int), state (str),
reservation (optional hex digest), stop_requested (bool), ledger_sequence (int).
It is **not** the full contract Operation, Receipt or Anchor and conveys no gate
passes, historical reconciliation, spendable allowance or permission to execute.
Authenticated UID is supplied by the trusted caller; this module adds no peer
authentication or transport. Reservation/pending methods are evaluator-internal,
not operator-facing RPCs, and never call a budget reservation API.

Grant consumption, operation insertion and hash-linked event commit in the SAME
SQLite database. Callback-time replay checks the entire prior chain and state
after BEGIN IMMEDIATE; a competing stale-tip append rolls back rather than forks
the chain. Contention refuses, with no automatic retry after an ambiguous error.
An identical claim returns current recorded state only; changed starts refuse.
Reservation references are immutable. Stop latches monotonically and is checked
in the reserved-to-pending transaction. Status uses a SELECT-only snapshot and
refuses absent or corrupt state rather than synthesizing success.

Only a committed live reserved-to-dispatch-pending transition returns a permit.
The opaque process-local permit has one `consume() -> None` use, rejects copies,
serialization and post-fork use, and contains no serializable authority token.
Cached callbacks, duplicates and reopened pending state never renew a permit.
There is no transition/recovery API for unknown state: unsupported or corrupted
persisted unknown histories refuse open, never repair or grant permission.
Loss of a permit is conservative and irreversible here. This mechanism **does
not solve stop-versus-real-send coupling**; no dispatcher or send exists.

`./scripts/test-story capstone-journal` runs only tiny public SQLite fixtures,
including separate-process races and actual process exits before/after COMMIT.
Zero/skipped/failing suites fail. Legacy durable-evidence unit tests remain unit
policy/storage regressions (their identity-constant patch is NOT kernel identity
proof). No VM, runtime identity, production installation or CI result is implied.
All full-capstone gates remain NOT-RUN; independent security/PM source review is
required before merge, and protected migration/issuance/execution remain gated.

## Exact accepted source-only contract (verbatim to end of file)

# GRRR-q3hp — proposed evaluator interface contract, 2026-11-04

**PROPOSED / NOT ACCEPTED / NOT DEPLOYED.** This specifies a source-only first
slice, not permission to run, install, reconcile, migrate, issue a grant or unlock
a stopped store. Existing runtime cannot execute accounting v4. Nothing below
claims that an endpoint, grant registry or usable allowance currently exists.

## 1. Ground truth and limits

P=`51ebc998e7c07018740ec53e389646a5b465cc75`;
R=`c928791cdaa72df91e61002c40317457b543b032`.
Read story `pvg issues show GRRR-q3hp --json` and prior mapping SHA-256
`631453fafb047f3a564ca8fc88813eb83f643d914a0d0f91b959c3b0242046bf`.
HEAD log: `0b2365e`, `710e6fb`, `845b47d`; `docs/findings/` absent.
Source references below are at P; mapping established unchanged relevant runtime
modules at R. No protected namespace access (including metadata), tests, builds,
VM/replay, network, tracker mutation or source edits were performed for this doc.

Existing: `research/common.py:63-115` kernel `getpeereid`, strict JSON and
authenticated client; `trusted_transport.py:12-128` pre-payload authentication,
dedicated status/stop capacity and explicit expected-peer control client.
`corpus_execution.py:161-198` requires runner UID321 and caller UID320, with only
in-memory dispatch deduplication. `replay.py:326-376` constructs mutating sessions;
`:426-431` persists pending before dispatch. These are not operator APIs.
`persistent_budget.py:73-81,158-194` rejects v4 and permits only unchanged v1 writes.
`ledger.py` supplies content objects, hash-chain `tip`, and `append_atomic` whose
callback transaction covers **only its own SQLite file**; constructor writes.
Retained `docs/evidence/replay-authority/stage-r/source/` file
`replay-successor-v4-v4_store_schema.py:15-61` has five tables and stopped=1;
its exact `EXPECTED_OBJECTS` has no grants/operations. Empty is not spendable.

## 2. Types and strict framing (all following types/APIs are NEW proposals)

Notation: records have exactly the listed fields; `?T` means explicit null or T,
not optional omission. Integers exclude bool; no NaN, floats, duplicate/unknown
keys. JSON uses existing `common.canonical`; H=64 lowercase hex SHA-256,
C=40 lowercase hex commit, I=existing `common.identifier`, N=integer >=0.
U is an exact integer 1..4294967294, excluding UID320/321 (and root0), and
must equal protected operator configuration. Rel is a nonempty canonical ASCII
relative POSIX path: reject empty/dot/dotdot components, leading slash, backslash
and NUL lexically before metadata; require exact reviewed/protected output-root equality.
Wire limit remains existing MAX_WIRE (control 4096); overlarge records refuse.
All digests over record content use canonical bytes; `*_bytes_sha256` fields bind
original file bytes, independently of normalized parsed representation.

```text
Vector = {currency:"USD", money_cents:N, execution_us:N, review_us:N}
DecisionBinding = {request_id:I, reviewed_package_commit:C,
  decision_json_bytes_sha256:H, decision_markdown_bytes_sha256:H, output_root:Rel}
Bindings = {driver_commit:C, driver_inventory:H, runtime_base:C,
  runtime_inventory:H, evaluator_inventory:H, runner_inventory:H,
  interpreter:H, bootstrap:H, qemu:H, vm_assets:H, corpus:H,
  replay_catalog:H, replay_image:H, execution_profile:H, policy:H,
  accounting_binding:H, accounting_version:N, decision:DecisionBinding,
  invocation_bytes_sha256:H}
Bounds = {maximum:Vector, stage:"poc", scope:H, floors:H,
  not_before_ns:N, expires_ns:N, receipt_max_age_ns:N}
Grant = {schema:"capstone-grant-v1", grant_id:H, operator_uid:U,
  authorization_bytes_sha256:H, bindings:Bindings, bounds:Bounds,
  review_anchor:H, issuance_anchor:H}
Request = {schema:"capstone-request-v1", run:I, bindings:Bindings,
  scope:H, maximum:Vector}
Anchor = {ledger_sequence:N, ledger_tip:H, accounting_snapshot:H,
  grant_registry_snapshot:H, installation:H}
Receipt = {schema:"capstone-observation-v1", nonce:H, operator_uid:U,
  grant_id:H, grant_bytes_sha256:H, authorization_bytes_sha256:H, bindings:Bindings,
  observed_ns:N, service_epoch:H, anchor:?Anchor,
  accounting:{version:?N, stopped:?bool, history:"verified"|"unknown",
    spendable:?Vector, held:?Vector},
  capability:"unsupported"|"observe-only"|"start-capable",
  grant_state:"unissued"|"available"|"consumed"|"unknown",
  blockers:list[Code], receipt_sha256:H}
Gate = {state:"pass"|"fail"|"not-run"|"error", evidence:?H, reason:?Code}
Plan = {schema:"capstone-plan-v1", request:Request, grant:Grant,
  grant_bytes_sha256:H, authorization_bytes_sha256:H, observation:Receipt,
  gates:map[existing common.GATES,Gate], plan_sha256:H}
Operation = {schema:"capstone-operation-v1", operation_id:H, grant_id:H,
  plan_sha256:H, start_request_sha256:H, state:State,
  reservation:?H, dispatch:"not-run"|"pending"|"completed"|"unknown",
  gates:map[existing common.GATES,Gate], anchor:Anchor, stop_requested:bool,
  result_object:?H, blockers:list[Code]}
Manifest = {schema:"capstone-manifest-v1", plan_sha256:H,
  operation_id:H, operation:?Operation, transport:"ok"|"unknown"|"refused",
  gates:map[existing common.GATES,Gate]}
State = "claimed"|"reserved"|"dispatch-pending"|"running"|
        "stop-pending"|"completed"|"stopped"|"recovery-required"
Code = existing common.Failure code enum accepted by control_call
```

Every gates map has exactly set(common.GATES): all eleven keys, none omitted or
unknown; this applies recursively to Plan, Operation and Manifest.
Receipt/plan self-digests exclude only their own digest field. They detect corruption,
NOT authentication. Missing observations stay null, not zero.
invocation_bytes_sha256 hashes original raw bytes of a separate exact
`{run,scope,maximum}` invocation; its parsed fields must equal derived Request.
It never substitutes for DecisionBinding or authenticates an approval.
Decision JSON/Markdown bytes come from their fixed Git paths at reviewed_package_commit,
not checkout claims. Verify both raw hashes, request_id, exact output_root, runtime
ancestry/admission-fix and every revision/budget inventory against protected issuance;
driver_commit is distinct from reviewed_package_commit. Decision artifacts remain
execution_authorized=false and issue no grant. Grant/Plan/Receipt bindings must agree.
grant_bytes_sha256 hashes the exact original issued Grant bytes, not reserialization;
the protected registry retains those same bytes/digest. Grant has no self-digest.
Grant.authorization_bytes_sha256 binds the exact external human authorization bytes;
Plan/Receipt must match it and protected issuance. Human authorization does not hash
a Plan containing itself, avoiding a cycle. Asset inventories remain reviewed exact
identities, never caller-selected paths; missing reviewed inventories/bounds refuse.
start_request_sha256 hashes canonical full `{action,version,plan,operation_id}`;
it includes the completed Plan and its digests, excludes no fields, and has no self-reference.

## 3. Public RPC and authentication

```text
observe(request:{action:"observe",version:1,nonce:H,request:Request,
                 authorization_bytes_sha256:H,grant_id:H}) -> Receipt
start(request:{action:"start",version:1,plan:Plan,
               operation_id:H}) -> Operation
status(request:{action:"status",version:1,operation_id:H,nonce:H}) -> Operation
stop(request:{action:"stop",version:1,operation_id:H}) -> Operation
```

Envelope is existing `{ok:...}` xor `{error:Failure.record}`. Unknown API version
returns InvalidInput, message `UnsupportedProtocolVersion`, retryable=false.
Unsupported accounting returns Receipt.capability=unsupported, spendable=null,
blockers=[RecoveryRequired]; start returns RecoveryRequired with message
`UnsupportedAccountingVersion:<n>`, never coerces n to 1 or uses another backend.
No discovered version or malformed binding may trigger a fallback transport.

New evaluator service runs exclusively as UID320. Its two sockets are fixed by a
reviewed protected installation descriptor: names `capstone-evaluator.sock` and
`capstone-control.sock`; CLI cannot choose endpoint/root/UID/profile. Operator UID
is taken from the protected existing configuration, never JSON. Server reuses
AuthenticatedServer(allowed_uid=configured_operator); data observe/start,
control status/stop. Client uses a NEW explicit-expected-UID=320 RPC helper built
from existing framing/control-call mechanics; do not use common.call basename
heuristic for new names. Client verifies server UID before sending payload;
server verifies operator UID before reading payload/taking capacity. Unavailable
getpeereid fails closed; no HTTP, local handle(320,...), sudo or role-field fallback.
Protected descriptor pins socket-parent ownership and service inventory; prevent
operator replacement of parent or socket. Kernel UID alone is not a source pin.
R is a historical runtime base, not authority for changed runtime bytes. New
inventory/package hashes require new review and a separately issued run grant.

Read-only `observe` validates protected grant issuance and the exact bindings;
it performs no grant consumption, journaling, lockfile creation, chmod, PRAGMA
write, recovery or session construction. It uses existing read-only handles under
the service's already-acquired writer-serialization lock. It must not construct
Ledger, Budget(write mode), PersistentBudget(v4) or ReplaySession. First slice
reports unsupported v4; later reviewed v4 reader opens existing DB mode=ro with
strict schema/identity checks and no implicit DB/journal creation or repair.

Freshness is a random request nonce plus authenticated live response, service
epoch, observation time and Anchor. Receipt is channel-attested, not portable
bearer authority. Prepare retains response digest and anchor separately from
the public export; offline hashes alone never authorize start. Start re-observes
under serialization: compare all bindings/anchor, approved age/window and grant
state. Restart epoch change or stale/changed anchor requires new prepare; unknown
clock continuity refuses. No TTL/default expiry is invented: missing approved
receipt_max_age/window blocks. Status is authenticated current state, not a
historical JSON success. Existing ledger export verification requires independently
retained trusted anchor, not one taken solely from the same untrusted export.

## 4. Grant issuance and conservative transaction sequence

Grant issuance is a separate protected, independently reviewed installation step,
not any RPC above and not part of source-only repair. It registers exact Grant
bytes/grant_bytes_sha256, its bound authorization_bytes_sha256, unique grant_id,
review/issuance anchors and configured operator UID
in evaluator-owned durable authority state. Operator-supplied Grant is only a
lookup/binding claim. A JSON approval bool, reference string, possession of an old
grant or an operator-written grant file cannot issue authority. No signing key or
new secret is required: protected issuance chain, kernel peer identity and pinned
bytes are the trust roots. Missing registry/issuance provenance means unissued.
Grant expiry, maximum, floors and scope must come from explicit reviewed bounds;
maximum must fit every existing cumulative cap including prior profiles/holds.
Unknown history forbids calculating a fresh remainder. stopped=true forbids start.

Proposed durable state lives in NEW tables in the existing evaluator ledger DB:
`capstone_grants(grant_id PRIMARY KEY, grant_bytes_sha256 UNIQUE, grant_body,
 consumed_by UNIQUE NULL)` and
`capstone_operations(operation_id PRIMARY KEY, grant_id UNIQUE,
 start_sha256, plan_sha256, state, reservation NULL, stop_requested)`.
grant_body preserves the original issued bytes, not a canonical reserialization.
Exact SQLite DDL/check constraints and upgrade validation belong to separately
reviewed ledger migration, NOT implicit CREATE on observe/start. These are not
added to the exact v4 budget schema. `operation_id=SHA256(canonical({grant_id,
plan_sha256}))`; changed plan cannot create a second operation for the same grant.

1. One UID320 owner holds an installation-wide existing-file advisory lock for
   its lifetime; all trusted accounting/ledger writers must honor this same lock.
   No coexistence with legacy writers/stale handles. Missing owner coordination
   blocks deployment. Within process serialize observe/start and state transitions;
   retain dedicated control responsiveness. A queued stop sets a cancellation
   latch checked before dispatch and is then durably recorded; no lost-stop race.
2. Validate all identities, live grant/window, floors, stop bit/history and budget;
   recompute plan/request hashes. BEGIN IMMEDIATE in ledger, consume grant and
   insert operation=claimed with a ledger event via append_atomic; commit durably.
   Repeated same start returns status ONLY; changed payload fails StaleBinding.
3. Reserve exact approved maximum in budget using deterministic operation key,
   then persist reservation reference and state=reserved in a second ledger
   transaction. No atomicity across budget and ledger files is claimed. Crash
   between steps means grant consumed, potential hold unresolved, no dispatch.
4. Commit dispatch-pending ledger event BEFORE any runner call, after final
   cancellation/identity/floor checks. Only the live owner which successfully
   committed this transition may send its one dispatch. Restart never resumes
   sending a persisted pending operation; response loss never resends dispatch.
5. Send only existing UID320->UID321 authenticated structured runner request with
   bound reservation/key. Existing ReplaySession cannot be dropped in unchanged:
   a reviewed v4 execution seam must avoid duplicate reservation/session writes.
   Meter/settle only verified results under existing evaluator rules; completion
   is separately journaled. Unknown effect retains maximum hold and recovery-required.
6. status never launches/retries/settles/releases. stop is cessation-only for this
   operator's recorded operation; persist stop-pending then authenticated runner
   control stop. Ack is not proof of cessation/settlement. Unknown/pending/crash
   remains held; no new operation/key/grant reuse, automatic refund or stop release.

## 5. Implementable first slice and later gates

First slice NEW `research/capstone_contract.py`: strict records/hash validators;
NEW `research/capstone_client.py`: pinned explicit-peer transport;
NEW `research/capstone_service.py`: read-only observation/refusal handlers with
v4 unsupported and start unconditionally blocked until all capabilities installed;
NEW `tests/unit_capstone_contract.py`, `tests/unit_capstone_peer.py` and public
contract documentation. No installation/startup hooks or protected paths in tests.
Driver CLI integration follows: `prepare --request --authorization --output`,
`run --plan --authorization --output`, with existing public path containment and
exclusive immutable outputs. Prepare runtime gates remain not-run, never inferred
from historical evidence. A blocked plan/manifest exits nonzero.

Later separate reviewed source/migration surfaces: new v4 read/write adapter,
new grant/operation registry migration, replay execution seam in replay.py,
service installation descriptor/launcher. Keep persistent_budget.py v1 guards,
retained v4 schema and milestone checklist unchanged. If operational v4 requires
schema evolution, name/version that successor explicitly; no silent v4 alteration.
Deployment, historical reconciliation, stop release, new revision run grant and
live VM validation are separate grants. This contract does not resolve them.

Bounded no-guest tests: strict parse/hash mismatches; counterfeit grant/receipt;
null history/allowance, stopped, unsupported-version and no downgrade; stale
nonce/epoch/anchor; no prepare writes/session constructors. Real Unix sockets
using an explicit test-only factory and the actual unprivileged test UID prove
accept/reject-before-payload, wrong expected server UID, framing and control capacity.
The production wrapper pins UID320 with no configurable downgrade; do not fake
getpeereid. Positive local socket tests are NOT production UID320/321 isolation,
installed-endpoint, VM, allowance, spendability or cessation evidence.
Future temp-store crash tests cut every transaction/send boundary, simultaneous
starts, changed payload, failed reserve, duplicate start and lost stop response;
assert consumed grant/retained holds/no duplicate sends. Synthetic stores prove
state-machine logic, NOT production UID320/321 isolation, installed v4 authority,
current spendability, VM execution, cessation or any capstone aggregate pass.
