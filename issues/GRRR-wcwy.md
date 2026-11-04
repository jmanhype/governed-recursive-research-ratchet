---
id: GRRR-wcwy
title: "Source-only evaluator protocol and authenticated refusal boundary"
status: open
priority: 0
type: task
parent: GRRR-2t3h
created_at: 2026-11-04T16:45:10Z
created_by: speed
updated_at: 2026-11-04T16:45:10Z
content_hash: "sha256:a76e0b65cb0e5f17ae7b401fe98344f2cf6b43a1391bfdf01ded97ff07fecbc8"
---

## Description
## Context
This is a source-only prerequisite to GRRR-q3hp, not a capstone or runtime delivery. The existing runtime rejects accounting v4; no installed v4 allowance issuer or durable grant capability is established. This first component must provide strict protocol validation, explicit-peer transport and truthful read-only refusal behavior without claiming those missing capabilities.
Independent review FIRST_SLICE_V2_REVIEW: APPROVED covers ONLY the contract below, SHA-256 9b0f0f5639a1f2f07539a1b1e22d33bb67e88e2dc78fe58ecc9925f356aaf8ad. It does not approve full GRRR-q3hp mapping or live execution.
Routing note: CoS was unavailable; a GLM Sr PM attempt disconnected without side effects; a Qwen Sr PM attempt exceeded its bounded window without creating an issue and was interrupted. The coordinator transcribes the independently reviewed scope through the public tracker API as the allowed final routine-work fallback. No private issue files are edited.

## USER INTENT
The later bounded evaluator must have a tested, exact, authenticated wire boundary that refuses unsupported or unissued authority rather than interpreting a caller's JSON/hash as permission. Source-component proof must remain visibly distinct from VM, accounting and production evidence.

## Acceptance Criteria
1. Implement strict bounded schema and hash validators for the accepted records. Every nested field and eleven-gate map is exact; reject duplicate keys, unknown/missing keys, bool-as-int, NaN/floats, invalid UID/digests, unsafe relative paths and inconsistent raw-byte bindings. Distinguish decision JSON/Markdown/requestID/reviewed package/output root from invocation, human authorization and issued Grant bytes. Parser output is data consistency, never permission or provenance attestation.
2. Implement bounded explicit-expected-server-UID transport derived from existing primitives. Authenticate kernel peer identity before sending payload; server authenticates before reading payload/taking capacity. Production wrapper pins evaluator UID320 with no caller downgrade; explicit unprivileged test factory is unmistakably nonproduction. No HTTP or basename fallback and no new persistent daemon/install/startup hook.
3. Implement only a read-only observation/refusal facade. No installed authority backend is assumed. Accounting v4 remains unsupported, grants/history/allowance absent or unknown stay unissued/null/unknown, and start is unconditionally blocked. Status/stop without actual capability must return failure, never fabricate completion, cessation or settlement. Do not construct Budget, Ledger, PersistentBudget or ReplaySession, open protected stores or perform migrations/issuance.
4. Add real no-guest parsing/binding and AF_UNIX local-peer tests, without mocking positive parsing or peer authentication. Actual unprivileged test UID is not production320/321 evidence. Test counterfeit/changed hashes, missing gates, unknown/null budget, wrong peer before payload, malformed/oversized framing, unavailable capabilities and control responsiveness. Negative syscall guards may assert no forbidden I/O, but are not runtime integration proof. Explicit suite entrypoint must fail on zero tests, skipped required tests or any failure.
5. Preserve existing common/trusted_transport behavior and all persistent_budget/replay/ledger/v4-schema guards and existing test-story modes. Add only an explicit evaluator-contract source-test mode; do not make milestone-e2e green or add a runtime shortcut. Document raw hashes, no-guest limits, proposed/uninstalled capability and deferred deployment.
6. Run the focused suite with existing Python3.14,3.12 and protected-runtime-compatible CLT3.9 where present, using standard library only. Missing interpreter or local peer capability is a reported blocker, not skipped success. Capture exact commands, tests-run/failure/skip counts, outputs, measured coverage if available (otherwise explicitly unmeasured), file/diff hashes and remaining warnings. Do not fabricate coverage or CI.
7. This component cannot close GRRR-q3hp/GRRR-6sso. No protected access/mutation, grant issuance, v4 reconciliation/write adapter, stop release, ledger migration, VM/replay, network/paid research call, secret use, provisioning, production mutation, admission, promotion, merge or push. Source commits/delivery are not authorized yet: retain reviewed WIP and evidence until explicit local-commit authorization.

## Boundary Map
PRODUCES (new APIs, not existing capability):
- research/capstone_contract.py -> decode_record(raw: bytes, kind: str) -> dict; validate_record(value: dict, kind: str) -> dict; typed raw-byte/binding/hash helpers documented with exact signatures. These validate consistency only, not authority.
- research/capstone_client.py -> explicit-peer bounded RPC helper and production-pinned/test-only client factories, with exact public typed signatures documented by implementation.
- research/capstone_service.py -> read-only observation/refusal facade and explicit local test factory, never protected backend or production startup.
- tests/unit_capstone_contract.py and tests/unit_capstone_peer.py -> real source-only adversarial tests.
- tests/unit_capstone_suite.py -> explicit no-guest runner refusing zero/skip/failure.
- scripts/test-story -> evaluator-contract mode only, preserving existing modes.
- docs/CAPSTONE-EVALUATOR-PROTOCOL.md -> exact accepted contract and scope limitations.
CONSUMES:
- research/common.py at epic0b2365e -> canonical(value: Any) -> bytes; digest(value: bytes) -> str; unique_fields(pairs: list[tuple[str, Any]]) -> dict; peer_uid(conn: socket.socket) -> int; MAX_WIRE=3145728; EVALUATOR=320; RUNNER=321; exact eleven GATES; Failure(code: str,message: str,operation: str='unknown').
- research/trusted_transport.py -> AuthenticatedServer(path: Path,handler,*,control=False,allowed_uid=320), close(); control_call(path: Path,request: dict,*,expected_uid: int,timeout: float) -> dict. Reuse where semantics fit; derive only necessary stricter explicit framing behavior.
- accepted source-only contract below; future production capabilities remain absent.

## Testing Requirements
No new external dependency or environment-variable skip gate. Tests use private temporary public fixtures and actual local AF_UNIX credentials. All ordinary positive transport/parser behavior is real, not mocked. Negative effect guards are labeled unit evidence. Preserve all existing tests. Test-only source work does not invoke VM/candidate or protected preflight. Full capstone gates remain not-run.

## OUT OF SCOPE
Driver CLI/prepare-run integration; actual authenticated v4 balance issuer; writable adapter; new grant registry; protected migration/installation; long-lived host daemon; historical budget reconciliation; new experiment run grant; source optimization/adaptation; protected execution or production changes.

## DIFF BUDGET
Approximately 8 source/test/doc files, under1200 changed LOC. Gross overrun requires recorded investigation, not deletion/weakening of tests or required fields.

## nd_contract
status: new

### evidence
- Created from independently approved first-slice contract9b0f...; source implementation not yet present.
- Original capstone remains deferred/rejected-x3; no acceptance or runtime authorization is inferred.

### proof
- [ ] AC1: strict record and byte-binding implementation/tests.
- [ ] AC2: actual local explicit-peer and pre-payload refusal tests.
- [ ] AC3: truthful unsupported/read-only effects.
- [ ] AC4: nonzero/no-skip real source-only test suite.
- [ ] AC5: old guards and modes unchanged.
- [ ] AC6: measured commands/counts/outputs/hashes, honest coverage.
- [ ] AC7: source-only scope and no protected/runtime authority.

## Accepted source-only contract
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

## Acceptance Criteria


## Design


## Notes


## History


## Links
- Parent: [[GRRR-2t3h]]

## Comments
