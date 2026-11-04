---
id: GRRR-q3hp
title: "Bug: capstone lacks explicit executable driver wiring"
status: in_progress
priority: 0
type: bug
labels: [milestone-1, integration, discovered-by-pm]
parent: GRRR-2t3h
created_at: 2026-11-04T13:37:38Z
created_by: speed
updated_at: 2026-11-04T16:40:15Z
content_hash: "sha256:99db3eb8ba8029ee314b0721154872000e7567b0d037fff98f2f6c56b5db09cd"
blocks: [GRRR-6sso]
assignee: dev-GRRR-q3hp
follows: [GRRR-ev2w]
---

## Description
## Context
At independently reviewed package `51ebc998e7c07018740ec53e389646a5b465cc75`, `tests/e2e/milestone.py` is deliberately a repository-only historical-provenance checklist with no pass mode; its `main() -> int` always returns `1`. `./scripts/test-story milestone-e2e` merely launches that file. This accurately fails closed, but no separately reviewed executable capstone prepare/run driver is wired to the accepted VM, evaluator, runtime, corpus, and accounting components. Historical hashes and public/no-guest regressions are not VM execution proof.

A parent later reported, without granting access authority: active accounting is live successor version 4 with profiles `['independent-replay']` and binding `/Library/GRRR/accounting-poc2/a142cabb5badd79b10b464d0198184caf218088f4c352c1624076b7207813530`; its directory is mode 0700 owned by `_grrr_evaluator`, and parent stat of `budget.sqlite` was denied. Treat that as context only: this story must not assume mutable/spendable budget, inspect the protected database, or bypass evaluator identity. The optimizer/driver may consume only authenticated evaluator allowance receipts.

## Root Cause
The capstone delivery bundled truthful blocked checklist evidence but deferred the actual command/runtime orchestration. No explicit prepare/run command exists to bind exact revisions and authorization, obtain evaluator-owned budget/capability evidence, and launch the already implemented isolated path while preserving per-gate truth.

## USER INTENT
I can issue one explicit, independently reviewed prepare command and one explicit run command for the exact capstone package; missing capability, budget uncertainty, authorization mismatch, or a floor breach stops before VM launch with truthful records, and no checklist result pretends to be execution.

## MANDATORY PREIMPLEMENTATION MAPPING
Before implementation, produce a bounded architect mapping against current reviewed source. If any item below cannot be resolved from concrete source, stop and request that architectural mapping rather than inventing an interface:
1. authenticated evaluator transport/client and exact allowance/spendability receipt API for the observed version-4 store;
2. exact revision set (driver package, runtime base, corpus freeze, VM/QEMU assets, active accounting binding, request/authorization bytes);
3. safe ownership/UID flow from operator-facing command to evaluator authority and runner `CorpusExecutor`;
4. exact prepare-plan/run-manifest schemas, receipt locations, retry/idempotency semantics, and launch refusal ordering;
5. which existing tests cover each refusal and which proof remains live-only.

## Boundary Map
PRODUCES:
- `research/capstone_driver.py` -> explicit driver API/CLI with separate `prepare` and `run` modes; signatures must be frozen by the architect mapping before implementation
- `scripts/capstone-driver` -> exact separately reviewed operator command (`prepare ...`, then `run ...`; grammar fixed by mapping)
- `scripts/test-story` -> explicit `capstone-driver` dispatch that never launches a VM during no-guest/public tests and reports each missing prerequisite as not-run
- focused driver tests/public documentation -> exact prepare refusal, run refusal, binding, idempotency, and historical-evidence-not-pass cases

CONSUMES:
- GRRR-0g4n: scripts/test-story -> current `milestone-e2e` behavior: run `python -I -S -B tests/e2e/milestone.py` and propagate its return code; preserve mandatory nonzero behavior for missing capability, skipped work, or failure
- GRRR-z3w9: research/replay_runtime.py -> `snapshot() -> dict`; `verify_runtime(current: bool = False) -> dict`; `verify_runtime(current=True)` requires `sys.executable == '/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/bin/python3.9'`, returns `runtime_identity`, `python`, and `root_launch_authorized: False`
- GRRR-w1lt: research/corpus_execution.py -> module functions `validate_preserved() -> dict`, `validate_config(config: dict) -> dict`, `validate_request(message: dict) -> None`; `CorpusExecutor(root: Path)` requires runner UID 321 and validates protected/approval records; `handle(uid: int, message: dict) -> dict` requires kernel-authenticated evaluator UID 320 and accepts `{'action':'status','run':...}` or validated dispatch/stop requests; `stop(run: str) -> dict`; `dispatch(message: dict) -> dict`. The mapping must establish the authenticated caller, not invoke this directly as optimizer
- GRRR-d8ji: research/persistent_budget.py -> `PersistentBudget(profile: str) -> None`; `totals(principal: int) -> dict`; `require_mutable() -> None`; `reserve(principal: int, run: str, maximum: dict, key: str, stage: str = 'poc', binding: str = None) -> dict`. Existing source also validates protected bindings; this story must not perform raw SQLite/database access from the driver
- GRRR-6sso: tests/e2e/milestone.py -> existing `checklist() -> dict` and `main() -> int`; observed package docstring/main are checklist-only and `main()` returns 1. Repair adds real driver wiring but must not reinterpret its historical provenance as a gate pass

## Acceptance Criteria
1. [State] A bounded, independently reviewable architecture mapping resolves every mandatory unknown above from concrete source and freezes exact command grammar, schemas, revisions, UID/transport boundaries, receipt APIs, and failure ordering. Implementation starts only after this mapping is accepted; unresolved mapping is a blocker, not permission to guess.
2. [Event] `prepare` performs no VM launch or protected mutation. It binds the exact driver/runtime/corpus/VM/accounting/request revisions and fresh external authorization, verifies authenticated evaluator capability and allowance/spendability receipts (never raw DB access), checks configured floors, and emits an immutable, individually truthful gate/plan record. Missing capability, unknown budget, non-spendable/insufficient budget, stale/mismatched authorization/revision, or floor breach stops with a precise per-gate `not-run/error/blocked` record before launch.
3. [Event] `run` is a separate command and refuses every prepare mismatch, replayed/stale authorization, unknown outcome, changed protected identity, or unmet gate before dispatch. It uses only the mapped authenticated evaluator path and existing isolated corpus/replay components; no source optimization or alternate host/container execution. A dispatch result and each mandatory gate remain separately recorded, with no aggregate code manufacturing a pass.
4. [Unwanted] Public/no-guest tests prove CLI parsing, exact revision/authorization binding, prepare/run separation, idempotent refusal, all enumerated prelaunch denials, truthful not-run records, and rejection of historical provenance as runtime proof. They explicitly do not prove VM execution. Real VM/evaluator/ledger integration remains mandatory live-only evidence requiring separate explicit authorization; this repair cannot close GRRR-6sso by itself.
5. [Unwanted] No contract admission, promotion, protected recovery/reset/stop-release, network/paid call, secret read, production mutation, merge, or push is added or performed. Existing capstone ACs remain unchanged. `milestone-e2e` continues to fail closed unless every mandatory runtime gate has fresh evidence; the explicit driver is the only route to attempt that later proof.

## Testing Requirements
- Unit/public no-guest tests: MANDATORY, no mocks for parsing/binding/refusal behavior; use synthetic receipts/plans only where protected inputs are intentionally denied, and label no-guest coverage as non-runtime proof.
- Integration/live tests: mandatory and distinct, real VM/evaluator/ledger only; absent authorization/prerequisite must leave tests not-run/blocked, never skipped-green. No environment-variable shortcut to green.
- Commands, both interpreters where applicable, exit codes, executed/failure/not-run counts, source hashes, and protected/non-protected scope must be captured. Run `./scripts/test-story capstone-driver` plus focused tests and `pvg verify`; true runtime command output belongs only to a separately authorized run.

## OUT OF SCOPE
- Changing GRRR-6sso ACs, thresholds, capstone semantics, or acceptance authority; this is blocker wiring only.
- New optimization strategy, source selector changes, admission/promotion capability, protected recovery/reset/stop release, VM provisioning changes, network access, secrets, merges, or pushes.
- Treating `PersistentBudget` construction, historical hashes, public tests, or parent observations as authenticated spendability or VM proof.

## DIFF BUDGET
Honest discovery result: mapping plus wiring is expected to touch ~8-12 files and stay under 1,200 changed LOC including tests/contract documentation. If architect mapping shows more surfaces, update this budget via pvg before implementation; gross overrun requires PM investigation.

## Skills To Use
- `architect` for the bounded mapping prerequisite
- `developer` only after mapping
- `pvg` and `nd`
- independent security/architecture review of exact driver bytes
- `pm_acceptor` for evidence-based acceptance

## Discovered During
GRRR-6sso review at reviewed package `51ebc998e7c07018740ec53e389646a5b465cc75`; parent source inspection confirmed checklist-only docstring/main. No protected run occurred.

## nd_contract
status: new

### evidence
- Created 2026-11-04 from bounded parent DISCOVERED_BUG and `git show 51ebc998...` API inspection; no VM/replay/protected accounting/network/source edit performed.
- Exact source commitments recorded in Boundary Map. Parent-reported live version-4 accounting is context only and was not accessed.

### proof
- [ ] AC #1: mapping complete and independently reviewed before implementation.
- [ ] AC #2: prepare binds exact identities and fails closed before launch.
- [ ] AC #3: run preserves separate execution/gate truth through authenticated path.
- [ ] AC #4: no-guest limits explicit; live-only runtime proof remains mandatory.
- [ ] AC #5: denied authority matrix and unchanged capstone ACs verified.

## Acceptance Criteria


## Design


## Notes
Dependency/evidence update: GRRR-6sso is now blocked by this repair. This blocker wiring does not change any capstone AC and does not constitute or authorize VM/replay execution. True capstone closure still requires separately authorized live runtime/evaluator/ledger proof plus all existing review and human gates.
2026-11-04 fresh capacity update after operator reported more space: df -k / and /System/Volumes/Data both returned 15110888 KiB available = 15473549312 bytes. This clears only the 15350000000-byte preparation CAPACITY floor by 123549312 bytes. It remains below the 16106127360-byte replay CAPACITY floor by 632578048 bytes. These arithmetic checks are not full preparation/preflight approval or VM runtime proof. Source floors verified at reviewed package 51ebc998e7c07018740ec53e389646a5b465cc75. Existing v4 runtime incompatibility and missing authenticated capability findings remain unchanged; no VM/replay, cleanup, protected access/mutation, budget reconciliation, source edit, commit, merge or push occurred.
2026-11-04 operator explicitly authorized: "Clean out the 633 we need cleared". Scope is a bounded inactive regenerable cache cleanup to clear the existing replay capacity floor, not VM/replay or a gate waiver. Fresh audit found go-build already 8KiB, npm content cache648KiB, pip8040KiB, Homebrew/Gradle caches absent. A bounded worker is auditing Cargo download archives and inactive Xcode module cache only, preserving active Codex/Chrome, all runtimes, repositories, GRRR evidence/protected state and production data. No broader deletion, process termination, privileged action or source edit is authorized. Actual reclamation and floor result will be recorded only after measurement.
2026-11-04 proposed v4 evaluator interface contract retained below. Artifact /tmp/grrr-q3hp-v4-interface-contract-20261104.md,225 lines,SHA256 f7b4ef7223cbede243eaa39c3dcbd4f8cbe4e2a8d3686fdcbe30eef3bc358cd3. PROPOSED, NOT ACCEPTED, NOT DEPLOYED; no source implementation or live capability claimed. It defines a minimal source-only contract/client/read-only refusal-service slice and separately gated later adapter/migration/authorization work. Independent review is still required; raw reviewed JSON/Markdown request-binding semantics must be made explicit before implementation. Existing 11 common.GATES match the approved capstone inventory; no missing-gate concern is asserted. User-directed remediation does not silently authorize installation, v4 writes, new revision execution, reconciliation or capstone acceptance.
2026-11-04 independent FIRST_SLICE_V2_REVIEW: APPROVED for exact /tmp/grrr-q3hp-v4-interface-contract-v2-20261104.md SHA2569b0f0f5639a1f2f07539a1b1e22d33bb67e88e2dc78fe58ecc9925f356aaf8ad (250lines). Reviewed repairs: separate exact decisionJSON+Markdown/requestID/package/outputroot from invocation; raw Grant and human-authorization digests; exactlyall11gates; strict operatorUID; defined start-envelope digest; explicit nonproduction localpeer tests. Approval permits ONLY source-only contract/hash validators, explicit-peer client, read-only observation/refusal façade and no-guest local-peer tests. It does NOT accept full q3hp mapping, livev4, grant issuance/migration, spendability, protected access, installation, driver integration or VM/runtime. Existing v1 mutation guards remain unchanged. Source prerequisite is being split from driver because q3hp AC1 cannot be bypassed; failed SrPM stream produced no issue/source effects and was stopped. Implementation is not yet claimed.

## nd_contract
status: in_progress

### evidence
- Operator-directed prerequisite repair selected by pvg loop next after native deferral of escalated GRRR-6sso; rejection-x3 and all capstone ACs remain intact.
- Claimed atomically via pvg story claim. Story branch/worktree prepared from epic 0b2365e; no source implementation started.
- Proposed first-slice interface contract f7b4ef7223cbede243eaa39c3dcbd4f8cbe4e2a8d3686fdcbe30eef3bc358cd3 is under independent review; code changes remain gated by that review.

### proof
- [ ] AC #1: full implementation mapping remains incomplete; first source-only slice proposal review pending.
- [ ] AC #2: no prepare runtime capability implemented or certified.
- [ ] AC #3: no run/replay authorized for new revisions.
- [ ] AC #4: no new code/tests executed yet.
- [ ] AC #5: denied authority matrix remains in force; no protected mutation or deployment.

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
Wire limit remains existing MAX_WIRE (control 4096); overlarge records refuse.
All digests over record content use canonical bytes; `*_bytes_sha256` fields bind
original file bytes, independently of normalized parsed representation.

```text
Vector = {currency:"USD", money_cents:N, execution_us:N, review_us:N}
Bindings = {driver_commit:C, driver_inventory:H, runtime_base:C,
  runtime_inventory:H, evaluator_inventory:H, runner_inventory:H,
  interpreter:H, bootstrap:H, qemu:H, vm_assets:H, corpus:H,
  replay_catalog:H, replay_image:H, execution_profile:H, policy:H,
  accounting_binding:H, accounting_version:N, request_bytes_sha256:H}
Bounds = {maximum:Vector, stage:"poc", scope:H, floors:H,
  not_before_ns:N, expires_ns:N, receipt_max_age_ns:N}
Grant = {schema:"capstone-grant-v1", grant_id:H, operator_uid:N,
  bindings:Bindings, bounds:Bounds, review_anchor:H, issuance_anchor:H}
Request = {schema:"capstone-request-v1", run:I, bindings:Bindings,
  scope:H, maximum:Vector}
Anchor = {ledger_sequence:N, ledger_tip:H, accounting_snapshot:H,
  grant_registry_snapshot:H, installation:H}
Receipt = {schema:"capstone-observation-v1", nonce:H, operator_uid:N,
  grant_id:H, authorization_bytes_sha256:H, bindings:Bindings,
  observed_ns:N, service_epoch:H, anchor:?Anchor,
  accounting:{version:?N, stopped:?bool, history:"verified"|"unknown",
    spendable:?Vector, held:?Vector},
  capability:"unsupported"|"observe-only"|"start-capable",
  grant_state:"unissued"|"available"|"consumed"|"unknown",
  blockers:list[Code], receipt_sha256:H}
Gate = {state:"pass"|"fail"|"not-run"|"error", evidence:?H, reason:?Code}
Plan = {schema:"capstone-plan-v1", request:Request, grant:Grant,
  authorization_bytes_sha256:H, observation:Receipt,
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

Receipt/plan self-digests exclude their own digest field. They provide corruption
detection, NOT signatures/authentication. Missing values stay null, not zero.
Request.bindings.request_bytes_sha256 is forbidden self-reference: set this field
to SHA-256 of the separately supplied original request payload containing exactly
`{run,scope,maximum}`; Request is the derived bound representation in Plan.
Grant has no digest self-reference: its external byte digest is in the plan/receipt.
Asset inventory digests reference reviewed exact inventories, never arbitrary
driver-provided filesystem paths. Missing reviewed inventories/bounds refuse.

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
bytes/hash, unique grant_id, review/issuance anchors and configured operator UID
in evaluator-owned durable authority state. Operator-supplied Grant is only a
lookup/binding claim. A JSON approval bool, reference string, possession of an old
grant or an operator-written grant file cannot issue authority. No signing key or
new secret is required: protected issuance chain, kernel peer identity and pinned
bytes are the trust roots. Missing registry/issuance provenance means unissued.
Grant expiry, maximum, floors and scope must come from explicit reviewed bounds;
maximum must fit every existing cumulative cap including prior profiles/holds.
Unknown history forbids calculating a fresh remainder. stopped=true forbids start.

Proposed durable state lives in NEW tables in the existing evaluator ledger DB:
`capstone_grants(grant_id PRIMARY KEY, grant_sha256 UNIQUE, grant_body,
 consumed_by UNIQUE NULL)` and
`capstone_operations(operation_id PRIMARY KEY, grant_id UNIQUE,
 start_sha256, plan_sha256, state, reservation NULL, stop_requested)`.
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
using actual local kernel UID prove accept/reject-before-payload, wrong expected
server UID, malformed framing and control capacity. Do not fake getpeereid.
Future temp-store crash tests cut every transaction/send boundary, simultaneous
starts, changed payload, failed reserve, duplicate start and lost stop response;
assert consumed grant/retained holds/no duplicate sends. Synthetic stores prove
state-machine logic, NOT production UID320/321 isolation, installed v4 authority,
current spendability, VM execution, cessation or any capstone aggregate pass.

## 2026-11-04 Authorized Regenerable Compiler-Cache Cleanup - Verified

Operator authorized: "Clean out the 633 we need cleared".

Only generated files older than one day with extensions .pcm or .swiftmodule were removed from the user's Darwin Clang ModuleCache. No compiler process was detected; bounded lsof exited 1 with empty output/stderr (no open cache file found). Root/ancestor symlinks, user ownership, root identity, per-file device/inode/size/blocks/mtime, and single-link checks guarded deletion. No rm-rf or privileged identity was used.

- Deleted files: 1096; allocated bytes removed: 788574208.
- Selected and deleted inventories match exactly, both SHA-256 ab3fd94ef061ed355f2d50b7aaec7338f2fc4c7e1959cc5ae2b6097e4651b8a7.
- Cleanup script SHA-256: 8676654deb44a5ff3d47b74adb0b68033111a1abcc053c133577a24f1d9953b4.
- Raw result SHA-256: 124456aa85354b298add7217b2a96a9e19eefe2ca434020c4f74d9e706ff324c.
- Raw script observation: free bytes before 15390605312; after 16171376640; net increase 780771328. Other host activity can affect this net figure.
- Later independent df observation: free bytes 16162504704; preparation floor 15350000000 PASS; replay floor 16106127360 PASS with 56377344 bytes headroom. This is a point-in-time capacity check only, not authorization or a full preflight/runtime pass.
- Compiler cache remained present at 8 KiB; zero .pcm/.swiftmodule files remained. The next build can regenerate those modules.
- Artifacts: /tmp/grrr-clang-cache-cleanup-20261104.sh, .result.txt, .selected-inventory.txt, .deleted-inventory.txt. Core scalar results and hashes are retained in nd independently of temporary file lifetime.
- An initial post-clean awk display expression had a syntax error; it performed no deletion. The final floor calculation was independently recomputed from fresh df output using the tool orchestrator; no failed calculation was counted as a pass.

Active Codex updater, all application/runtime installations, repositories, GRRR evidence, replay inputs, protected accounting and production data were not altered. Chrome's cache-only dialog was inspected, found under 1 MB, and canceled without deleting browsing data; a temporary version tab was closed, restoring the original settings tab. No npm cache or other application's data was deleted.

Source HEAD remains 0b2365e30ab5858cb419f4f4ce9b2ce001850541 with a clean source checkout. No /Library/GRRR access or mutation, VM/replay, spendability write/reconciliation, stop clearing, admission, promotion, merge, push or credential use occurred. The v4 compatibility and authenticated-interface blockers remain; this cleanup does not satisfy them. Headroom is narrow and must be rechecked before any future launch.

# GRRR-q3hp bounded architecture mapping

**MAPPING_RESULT: BLOCKED_BY_MISSING_CAPABILITY**

Date: 2026-11-04. Scope: source-only prerequisite mapping, not implementation approval.
Package P = `51ebc998e7c07018740ec53e389646a5b465cc75`.
Runtime R = `c928791cdaa72df91e61002c40317457b543b032`.
Every source citation below is at P unless explicitly marked R.
`git diff R P --` for the seven requested research modules returned no differences;
their cited semantics therefore apply at both exact revisions, not necessarily HEAD.
Current checkout log: `0b2365e`, `710e6fb`, `845b47d`; `docs/findings/` absent.
Read `pvg issues show GRRR-q3hp --json`. No tracker mutation, tests, builds,
network, VM, privileged identity, or access whatsoever to `/Library/GRRR` occurred.
Source references to that namespace were read from Git objects only.
Graph tools were unavailable; exact-revision `git show`/numbered source was used.

## 1. Decisive capability gaps

1. **The existing runtime rejects accounting v4.** `PersistentBudget.validate_store`
   accepts only versions 1/2/3 (`research/persistent_budget.py:73-81`).
   `require_mutable` allows only exact unchanged v1 (`:158-166`);
   `reserve` rechecks it (`:184-194`). `replay.preflight` independently requires v1
   (`research/replay.py:69-86`). Constructing a budget cannot fix this.
2. **No authenticated evaluator allowance/spendability receipt API exists in the
   bounded inspected interfaces.** `totals(principal)` is an in-process method;
   v3 explicitly projects `spendable=None` (`persistent_budget.py:152-156`).
   There is no v4 receipt issuer/client/schema/freshness contract in these files.
3. **The supplied Stage O adapter is not a live adapter.** At
   `docs/evidence/replay-authority/stage-r/source/replay-successor-v4-stage_o_runtime_adapter.py:6-40`,
   it accepts only exact hypothetical uninstalled v3 observation, emits
   `execution_authorized=False`, and has an empty mutation allowlist.
   Do not upgrade its `source_prepared:pass` into capability or allowance.
4. **Sandbox schema verification is not spendability.**
   `.../replay-successor-v4-v4_store_schema.py:46-61` creates an empty stopped store;
   `.../replay-successor-v4-postflight_verifier.py:33-63` verifies exact bytes,
   physical identity, schema, stopped bit and empty tables. It returns
   `{stopped:True, empty:True, verified:True}`, not an allowance receipt.
   `.../replay-successor-v4-protected_preflight.py:12-38` is lexical sandbox
   containment, explicitly excluding Library paths, not evaluator preflight.
5. **Operator-to-evaluator prepare/run service is absent in inspected scope.**
   Replay evaluator is a fixed privileged process entry, not a socket handler
   (`research/replay.py:566-587`). A client transport primitive does not establish
   an authorized endpoint or caller rights. Never call `handle(320, ...)` locally.
6. **Cross-restart capstone authorization consumption/idempotency is absent.**
   Existing replay pending state is conservative, but no capstone plan/manifest
   schema or one-use external authorization receipt is defined by these modules.

Parent's reported active v4, independent-replay profile, private evaluator-owned
store and denied parent database access are context, not independently verified.
Budget totals remain unknown. Reported 5.8 GB free is below replay's exact
16,106,127,360-byte floor (`research/replay_fixtures.py:14`), so no live work is
permitted even if the missing capability were subsequently implemented.

## 2. Exact existing identity/transport flow

- Operator UID is a configured non-root, non-320, non-321 identity, not a request
  role (`corpus_execution.py:43-61`, `replay_profile.py:38-54`).
- Reviewed parent provisioning/identity switching is outside the enumerated
  interfaces. `ParentProtocol` defines fixed replay scope/config/preflight hooks,
  not an operator-facing authenticated allowance service (`replay.py:96-117`).
- UID 320 evaluator: `ReplaySession.__init__` enforces identity, preflight,
  root-owned plan, private evaluator storage and nonblocking session lock;
  then opens budget/ledger and writes replay state (`replay.py:326-376`).
  It must not be constructed during mutation-free prepare.
- `reproduce` requires UID 320 and exact configured operator principal, allegation
  and policy; the source explicitly says it is NOT an unauthenticated endpoint
  (`replay.py:396-425`). It marks attempt pending before dispatch (`:426-431`).
- UID 320 sends structured requests to runner `ipc/executor.sock` using
  `common.call`; server peer is authenticated as UID 321 before payload is sent
  (`research/common.py:94-115`, explicitly inspected at R).
- UID 321 `runner` installs separate data/control `AuthenticatedServer`s
  (`replay.py:192-201`). Server authenticates UID 320 before reading bytes or
  occupying a request slot; control and dispatch actions are separated
  (`trusted_transport.py:12-24,36-75`). This is kernel peer identity, not JSON UID.
- `ReplayExecutor` subclasses `CorpusExecutor`, pins replay artifacts/scope and
  enforces run prefix/guest count (`replay.py:129-180`). Base initialization
  requires UID 321, protected artifacts/config and approval
  (`corpus_execution.py:161-168`); `handle` requires UID 320 (`:177-186`).
- Dispatch wire fields are exactly `action,version,run,arm,challenge,variant,key,
  reservation,epoch,probe`; action dispatch, arm validated-corpus, epoch 0,
  probe null, challenge=variant (`corpus_execution.py:65-76`). Status/stop have
  exactly action/run (`:179-185`). These are runner interfaces, not driver APIs.
- Existing control client authenticates explicit expected server UID before send
  (`trusted_transport.py:104-128`). Unknown transport outcome is not a retry grant.
- Replay evaluator reserves, obtains fresh isolated observations, validates each,
  meters and settles under its own authority (`replay.py:389-394,443-481`).
  Failure halts budget, retains unknown reservation and records inconclusive
  (`:482-516`). No driver-issued receipt can replace those evaluator records.

## 3. Existing bindings and receipts

- CLT interpreter path and full runtime identity are pinned in
  `replay_runtime.py:10-15,29-71`; `verify_runtime(current=True)` requires the
  direct interpreter and returns `root_launch_authorized:False`.
- Corpus freeze is `dfa75ef2bf3d43fd4f750094fe643afe4f204812c0ae2426276bedb471fa8529`
  (`corpus_execution.py:20-27`); replay uses its separate fixed catalog/image,
  not arbitrary corpus challenges (`replay_profile.py:10-15,38-54`).
- QEMU manifest/executable pins are in `trusted_execution.py:24-27`; VM kernel,
  initramfs and ISO pins are in `research/execution.py:15-17`. Runner verifies
  them before launch (`corpus_execution.py:203-225`). No asset paths supplied
  by a driver may override those compiled identities.
- Config binds host_code, interpreter/bootstrap, QEMU, corpus, active accounting
  digest and composed execution_profile (`replay_profile.py:29-54`). Approval
  binds matching config fields and license-review digest plus an authorization
  reference (`trusted_execution.py:160-178`). Reference shape is not one-use proof.
- Existing protected replay plan is exactly `{run,scope,policy_sha256}`
  (`replay.py:120-126`). It is NOT a capstone prepare-plan and cannot be silently
  extended: the validator rejects unknown fields.
- Replay receipts live as content-addressed ledger objects; export is a snapshot
  under evaluator home (`replay.py:499-521`). Raw protected receipts are not
  public caller inputs. No public authenticated allowance-receipt location is
  mapped. New driver package/request/authorization hashes cannot be inferred
  from old package P or the existing old-revision run grant.

## 4. Minimum safe grammar and schema decision

**Executable ready/run grammar cannot be frozen from existing interfaces.**
There is no honest command that satisfies q3hp AC2/AC3 today. The only safe
implementation-ready surface is local parse/binding/refusal/report glue, after
mapping acceptance; it must keep every attempted run blocked.

Candidate CLI surface for a later accepted contract (proposal, NOT existing API):
`scripts/capstone-driver prepare --request REQUEST --authorization AUTH --output PLAN`
`scripts/capstone-driver run --plan PLAN --authorization AUTH --output MANIFEST`
No endpoint, identity, profile, code, asset, accounting path, shell command or
skip-gate override flag. Inputs must be bounded local public records; never raw
protected receipts. Paths must be lexically rejected before metadata access.

Minimum future plan bindings: exact driver package and source inventory; R;
corpus freeze and replay catalog/image/profile; QEMU/VM/interpreter/bootstrap;
accounting binding digest/version; exact request and external authorization
byte digests; evaluator-issued capability/allowance identity and freshness;
operator identity; fixed scope/maxima/floors; per-gate status/evidence.
Run manifest must bind the exact plan digest, consumed authorization, durable
operation identity and separate dispatch/gate outcomes. Unknowns remain explicit.
These are required semantics, **not an invented accepted schema**. Exact receipt
fields, authority signatures/channel, TTL, consumption store and receipt
publication contract remain blockers. Do not implement against guessed fields.

Refusal order for future wiring:
1. Parse exact grammar and bounded bytes; lexical path rejection before I/O.
2. Validate record schemas/digests; reject historical-only, stale/reused or
   wrong-revision authorization before contacting authority or launching anything.
3. Read-only local runtime/source/floor checks; record unperformed gates not-run.
4. Authenticate mapped evaluator; require exact current capability and fresh
   allowance/spendability receipt. Missing service/v4/unknown funds => blocked.
5. On run, recheck plan, all identities/floors and authorization; evaluator must
   atomically claim authorization/operation and reserve before authenticated
   runner dispatch. Missing atomic capability => blocked, not best-effort launch.
6. Separately retain dispatch and gate outcomes; unknown effect => no redispatch,
   no reservation release, no manufactured aggregate pass.

Existing runner key behavior is in-memory: same key+same message returns cached
result only if complete; changed message rejects; pending requires recovery
(`corpus_execution.py:188-198`). This is NOT durable driver idempotency.
Replay session rejects persisted pending attempts (`replay.py:326-331,370-374`).
A caller-side file or random new key must not bypass that refusal.

## 5. Minimal surfaces and focused evidence

Ready glue after acceptance: new `research/capstone_driver.py`, new
`scripts/capstone-driver`, explicit no-guest `scripts/test-story` dispatch,
focused CLI/binding/refusal tests and public command/schema documentation.
Preserve `tests/e2e/milestone.py` checklist semantics: all mandatory gates not-run,
historical hashes explicitly non-proof, unconditional return 1 (`:86-123`).
Current script dispatch simply propagates that result (`scripts/test-story:7-10`).

Required capability work is NOT merely those files: authenticated evaluator
service/client contract; reviewed v4 accounting adapter/receipt issuer;
durable plan/authorization consumption integration; reviewed launcher binding.
Likely integration touchpoints are `persistent_budget.py`, `replay.py` and
transport/launcher code, but exact minimal files cannot be asserted before the
missing authority contract is resolved. Do not relax v1-only guards as wiring.
The 8-12 file/1,200 LOC budget must be reassessed if those capabilities are in scope.

Existing source tests (read, NOT run):
- `tests/unit_replay_registration_boundary.py:15-38`: unknown versions and
  registered/stop-only modes refuse before protected input/mutation.
- `tests/unit_independent_replay.py:59-138`: failed rebuild/nondeterminism/forged
  logs, all gates not-run, policy/scope/accounting and caller refusals.
- `tests/unit_replay_successor_runtime.py:61-270`: hypothetical status cannot
  authorize execution; claimed install/store and reused future receipt rejected.
  These tests do not certify the stage-r retained adapter as a deployed service.
- `tests/e2e/milestone_checklist.py:48-83`: missing/malformed history and execution
  option attempts cannot produce success.

New focused public tests must exercise real parsing and binding code without
mocking it: duplicate/unknown fields, exact bytes changed, stale/reused auth,
prepare/run separation, protected path lexical rejection, unavailable/wrong-peer
service, unsupported v4, unknown/null/insufficient allowance, floor breach,
changed identity, pending/unknown outcome, and historic-provenance-only input.
Synthetic authority records test rejection only, not authentication or VM proof.
Later authorized live tests must independently prove real peer identities,
current v4 receipts/reservation, fresh VM observations, cessation and settlement.
No tests were executed here under the disk-floor prohibition. No capstone pass,
budget balance, deployed capability, or runtime authority is claimed.

## 2026-11-04 Source Mapping and Capacity Evidence - Implementation Blocked

Independent architecture mapping by `/root/grrr_q3hp_trust_boundary_mapping` returned `BLOCKED_BY_MISSING_CAPABILITY`. Parent verified the 196-line artifact exists at `/tmp/grrr-q3hp-architecture-mapping-20261104.md` with SHA-256 `631453fafb047f3a564ca8fc88813eb83f643d914a0d0f91b959c3b0242046bf`. The full mapping is appended separately for durable nd readback; it is source-only evidence, not implementation approval or deployed capability.

Concrete findings at reviewed package `51ebc998e7c07018740ec53e389646a5b465cc75` / runtime `c928791cdaa72df91e61002c40317457b543b032`:
- `PersistentBudget.validate_store` accepts versions 1/2/3, not v4; `require_mutable` and replay preflight require v1.
- No authenticated v4 allowance/spendability receipt API was identified in the bounded inspected interfaces.
- The retained Stage O adapter is hypothetical/uninstalled and grants no execution authority; a sandbox schema verifier is not a spendability or capability receipt.
- Operator-to-evaluator service wiring and cross-restart one-use authorization consumption are unresolved.
- Therefore a prepare/run wrapper alone cannot safely launch this capstone. Do not weaken version guards or instantiate the evaluator session during mutation-free prepare. Do not implement guessed schemas or claim a mapping pass.

Capacity audit artifact `/tmp/grrr-capacity-audit-20261104.txt` was independently checked on disk: 148,693 bytes, SHA-256 `f366259c07712e34ba32ebca3911ab424fe3b81320ded31c745fbc1b1c731de5`.

Measured cache-size ceilings (not guaranteed reclaimed bytes):
- Codex cache: 1,892,179,968 bytes; active runtime, not approved for cleanup.
- Go build cache: 1,366,118,400 bytes.
- Chrome Default Cache: 1,297,309,696 bytes; active browser.
- Chrome Default Code Cache: 606,470,144 bytes; active browser.
- pip cache: 8,232,960 bytes.
- Requested Homebrew cache path absent; no alternate-path search or inferred broader zero.
- Total measured ceiling: 5,170,311,168 bytes.

Parent's later `df -k /` observation reported 5,663,168 KiB available, or 5,799,084,032 bytes. Even an ideal recovery of every measured cache byte would yield only 10,969,395,200 bytes, still 5,136,732,160 bytes below the 16,106,127,360-byte replay floor, with no safety margin. Active Codex/Chrome caveats further reduce what could safely be considered. No cleanup, purge, quit, termination, reboot or deletion occurred.

Workflow writeback also exposed a tool failure: `pvg story reject GRRR-6sso` refused with `property "assignee" not found`. Live status/labels remained unchanged. A subsequent normal atomic `pvg nd claim ... --agent pm-rejection-writeback` without force was refused because GRRR-q3hp blocks the story. No force claim, manual label/status workaround, raw issue-file edit, or pvg-core change was used. The independent PM rejection is substantive but not a landed transition; do not claim otherwise.

Current result: GRRR-q3hp AC1 mapping is blocked by concrete missing trusted capability; no implementation has begun. Capstone runtime evidence and cumulative allowances remain unestablished. Source checkout remains untouched; no protected mutation, VM/replay, network/inference, credential, admission, promotion, merge or push occurred. The exact-old-revision conditional grant does not silently authorize new implementation or deployment.

## History
- 2026-11-04T13:37:44Z dep_added: blocks GRRR-6sso
- 2026-11-04T16:04:26Z status: open -> in_progress
- 2026-11-04T16:04:26Z auto-follows: linked to predecessor GRRR-ev2w
- 2026-11-04T16:04:26Z claimed by dev-GRRR-q3hp

## Links
- Parent: [[GRRR-2t3h]]
- Blocks: [[GRRR-6sso]]
- Follows: [[GRRR-ev2w]]

## Comments
