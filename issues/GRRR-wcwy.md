---
id: GRRR-wcwy
title: "Source-only evaluator protocol and authenticated refusal boundary"
status: in_progress
priority: 0
type: task
parent: GRRR-2t3h
created_at: 2026-11-04T16:45:10Z
created_by: speed
updated_at: 2026-11-04T17:34:48Z
content_hash: "sha256:a12252540f91d226d40c0b2849ecfc7b140a84a735fbf1988386107210c68454"
blocks: [GRRR-q3hp]
labels: [milestone-1, source-only, security-boundary, delivered]
assignee: dev-GRRR-wcwy
follows: [GRRR-ev2w, GRRR-888u]
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


## nd_contract
status: delivered

### evidence
- Transitioned via pvg story deliver on 2026-11-04.

### proof
- [ ] Developer evidence block must remain authoritative above this contract.


## Implementation Evidence (DELIVERED SOURCE COMPONENT)

PROOF:

### Commit
- Branch: story/GRRR-wcwy
- Producing commit: 8cf7d0d86d5103de3709d432a8c35b8101020440
- Parent: 0b2365e30ab5858cb419f4f4ce9b2ce001850541
- Exact eight reviewed files, 1034 insertions and 2 deletions, within 1200-line budget. No additional runtime modules changed. Root epic is not yet merged.
- Operator explicitly authorized local source commits, PM delivery and PM-accepted epic merges. The earlier WIP-only commit restriction is superseded for this local-source workflow only. No push or protected authority is granted.

### CI/Test Results
- Local post-commit commands, each run synchronously in .claude/worktrees/dev-GRRR-wcwy:
  - /opt/homebrew/bin/python3 -B scripts/test-story evaluator-contract (Python3.14.3)
  - /Users/speed/miniconda3/bin/python3 -B scripts/test-story evaluator-contract (Python3.12.7)
  - /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/bin/python3.9 -B scripts/test-story evaluator-contract (Python3.9.6)
- EACH reports SOURCE_ONLY tests=19 failures=0 errors=0 skipped=0; full capstone NOT-RUN; exit0. These are19 repeated source tests, not57 distinct scenarios or isolated corpus observations. Nine contract tests and ten local-peer tests execute real parsers and real AF_UNIX credentials; positive authentication is not mocked. Negative effect guards are explicitly unit evidence.
- Existing full VM/corpus/replay suites and11 capstone gates were NOT RUN under this source-only scope. They remain mandatory live gates for GRRR-6sso; no historical/protocol test upgrades them to pass. No external CI is claimed.
- Raw producing-commit command arrays, stdout/stderr, durations and SHA256s: .git/paivot/wip/GRRR-wcwy/post-commit-20261104/runs.json plus run0..run4.stdout/stderr. Exact source hashes and commit.txt retained there. Verification script /tmp/grrr-wcwy-commit-verify-20261104.py.

### Coverage
- Producing-commit command: /opt/homebrew/bin/python3 -B -m trace --count --summary --missing --coverdir <repo>/.git/paivot/wip/GRRR-wcwy/post-commit-20261104/coverage tests/unit_capstone_suite.py
- Measured standard-library trace LINE coverage: capstone_contract95.6%, capstone_client96.9%, capstone_service93.5%. Branch coverage and VM/runtime coverage are unmeasured; this is not a full-milestone coverage percentage. Raw summary run4.stdout and annotated coverage files retained; the traced suite also executed19 tests with no errors/failures/skips.

### Independent Security Review
- SOURCE_SLICE_REVIEW: APPROVED, no material in-scope defect found, exact all-eight per-file hashes match.
- /tmp/grrr-wcwy-security-code-review-20261104.md SHA256 f18b42dd36979b9bb13fabe7ef3d71b7b99b2bb9c9898187f857fcd902de778b.
- Independent reviewer ran19 tests twice on Python3.14.3; retained log SHA256 e6c65e47d612ed90d56be91a1820d90351d2c7fa9953ce963c31dc70ddcdc755. Review/log also retained in .git/paivot/wip/GRRR-wcwy/parent-verify-20261104/.
- Review is not PM acceptance, protected issuance, installation, spendability, UID320/321 or VM proof.

### pvg verify
- Command: pvg verify research/capstone_contract.py research/capstone_client.py research/capstone_service.py tests/unit_capstone_contract.py tests/unit_capstone_peer.py tests/unit_capstone_suite.py scripts/test-story docs/CAPSTONE-EVALUATOR-PROTOCOL.md --format=text
- Output: VERIFY: PASSED (6 files scanned, 0 issues), exit0. All explicit paths were supplied; six eligible Python files scanned. git diff --check clean before commit, working tree clean after commit.
- Existing common.py, trusted_transport.py, budget.py, persistent_budget.py, replay.py and ledger.py byte-identical to parent. Existing modes are preserved; only evaluator-contract source dispatch added.

### AC Verification
| AC | Requirement | Source | Test/evidence | Result |
|---|---|---|---|---|
| 1 | Exact bounded nested schemas,11 gates, distinct original-byte bindings and consistency-only meaning | capstone_contract.py | ContractTests9 tests, explicit raw input changes and type/schema adversaries | PASS source-only |
| 2 | Explicit peer-before-payload, production-pinned refusal and test-only factory | capstone_client.py; capstone_service.py uses unchanged AuthenticatedServer | PeerTests wrong-server/client-before-payload/slot; real same-UID sockets | PASS local-peer only |
| 3 | Unsupported v4, unknown/unissued allowance, unconditional start refusal, absent status/stop failure | RefusalService.handle; production_client | real_refusal_channels, counterfeit_grant_cannot_start, no_protected_io negative guard | PASS refusal surface |
| 4 | Real public no-guest parsing/transport and nonzero/no-skip suite | unit_capstone_suite.py and both test modules | 19 executed,0fail/0error/0skip on all3 interpreters | PASS source-only |
| 5 | Legacy guards/modes unchanged; exact scope docs | scripts/test-story; docs/CAPSTONE-EVALUATOR-PROTOCOL.md | parent diff; exact accepted contract is doc suffix; static scan clean | PASS |
| 6 | Measured commands/counts/outputs/hashes and honest coverage | post-commit evidence directory | exact producing SHA, raw results and trace line coverage above | PASS |
| 7 | No protected/runtime authority; no q3hp/6sso closure | documentation and unchanged guarded modules | no protected access, install, issue, mutation, VM/replay, secret/network call, admission/promotion/prod, merge or push | PASS boundary |

### Observations and Routing
- No installed authority descriptor/backend exists. This component intentionally refuses observe instead of inventing an issued raw Grant digest. Hash consistency is not provenance/authentication/authority. v4 remains unsupported and starts cannot dispatch. Actual driver, allowance, protected install and live capstone are not delivered by this story.
- CoS is unavailable. GLM and Qwen review attempts returned no artifact within bounds and were interrupted; only the artifact-producing fresh security review was accepted. A subsequent bounded GLM deliver-only attempt likewise produced no side effect and was interrupted. Parent performed authorized mechanical commit/delivery as final routine fallback, not a new implementation or independent PM decision.
- bd sync --from-main was attempted and reports no beads database; no competing tracker was initialized. Existing shared pvg nd vault remains authoritative; sync uses --no-push.
- Actual disk measurement remains below the replay floor despite the operator's capacity report. No cache deletion, VM, or candidate execution was performed; source tests are tiny public fixtures only.

LEARNINGS:
- Unissued authority cannot honestly populate an issued-Grant observation; fail with RecoveryRequired rather than manufacture a receipt.
- A valid hash/schema is consistency, not protected provenance or permission; test-only kernel peer results must stay visibly nonproduction.
- Preserve exact WIP/test/review evidence outside disposable worktrees and bind post-commit evidence to the producing revision.
- Bound unavailable worker routes and do not count silence, missing gates or stale tracker summaries as acceptance.

## nd_contract
status: delivered

### evidence
- Commit8cf7d0d86d5103de3709d432a8c35b8101020440;19 source tests per interpreter,0fail/0error/0skip on3.14/3.12/3.9; static6eligible files0issues.
- Independent source security review approved exact bytes, not PM or runtime authority.
- Raw source/test/coverage/review manifests retained outside disposable worktree; no protected access, VM/replay, mutation, merge or push.

### proof
- [x] AC1 strict schemas and raw bindings.
- [x] AC2 actual explicit-peer local refusal boundary.
- [x] AC3 truthful unissued/unsupported/absent capability failures.
- [x] AC4 nonzero no-skip source suite.
- [x] AC5 existing guarded modules/modes unchanged and scope documented.
- [x] AC6 producing-commit raw test/hash/line-coverage evidence.
- [x] AC7 source-only scope; q3hp and capstone remain unaccepted.

# Local-source workflow authorization

Operator response: "Authorized and you have enough space now".
This directly approves the preceding bounded request: local commits, PM delivery,
and PM-accepted merges into epic/GRRR-2t3h for reviewed source repairs.

It does not authorize main merges, pushes, protected accounting changes, protected
installation, replay, permanent contract admission, promotion or production changes.
Source acceptance still requires tests and independent PM review. No missing gate
may be waived. Prior source-only WIP commit restriction is superseded only for this
local-source workflow; protected/run restrictions remain intact.

Fresh capacity observation at kickoff: df available10638548KiB, below the replay
floor16106127360bytes. The operator's space report does not replace measured
preflight. No cleanup or live execution is authorized by this source-workflow grant.

## nd_contract
status: in_progress

### evidence
- Independent source security review SOURCE_SLICE_REVIEW: APPROVED; no material in-scope defect found in exact eight-file WIP. Review /tmp/grrr-wcwy-security-code-review-20261104.md SHA256 f18b42dd36979b9bb13fabe7ef3d71b7b99b2bb9c9898187f857fcd902de778b.
- Reviewer independently reran /opt/homebrew/bin/python3 -B scripts/test-story evaluator-contract twice on Python3.14.3. Each run: tests19, failures0, errors0, skipped0. Retained second output /tmp/grrr-wcwy-security-test-20261104.log SHA256 e6c65e47d612ed90d56be91a1820d90351d2c7fa9953ce963c31dc70ddcdc755.
- Parent independently reproduced the same19 source tests on Python3.14.3,3.12.7,3.9.6, all non-skipped and exit0; raw commands/stdout/stderr and hashes retained in .git/paivot/wip/GRRR-wcwy/parent-verify-20261104/. runs.json SHA256 3e084bfa1469fa3d1e00b4fe94f36d829e70e404d5ad387ddecb9aba00f26871; hashes.json SHA256 5f4c94dffd868fcd784269fce32a8806c20dc998db11aaf03520a3270f2c9c60.
- Parent reverified all eight WIP file hashes after review, copied exact review/test artifacts outside the disposable worktree, confirmed git diff --check clean, and preserved the unchanged legacy guards. Retention script /tmp/grrr-wcwy-retain-review-20261104.py. No source commit or worktree removal occurred.
- Routing: CoS unavailable (tunnel-client-not-seen). GLM Coding Plan and Qwen Ambassador review attempts exceeded bounded windows without a review artifact and were interrupted; neither was treated as approval. A fresh bounded Astra security-review escalation produced the above exact-file artifact. All completed/interrupted review handles were stopped; no recursive delegation.
- This approval is SOURCE ONLY, not PM acceptance or deployment approval. No installed descriptor, authenticated v4 authority backend, issued allowance, production UID320/321 or VM proof exists in this slice. Observe refuses unissued authority, v4 is unsupported, start always refuses, absent status/stop capability claims no cessation or settlement.
- Fresh df available10751936KiB (11009982464 bytes), below replay floor16106127360 bytes. Space is time-sensitive; no live launch was attempted. Capacity and missing executable/runtime capabilities remain distinct blockers.
- bd sync --from-main reported no beads database; no competing tracker was initialized. Shared PAIVOT nd remains authoritative and was synced locally without push.
- Source commit/delivery and accepted-story merge have not been authorized for this repair. Requesting one bounded standing local-source workflow grant must not be interpreted as permission for main merge/push, protected reads/installations, reconciliation/stop release/VM/replay, admission/promotion or production changes. Original exact-target run authorization is not silently transferred to changed runtime bytes.

### proof
- [x] AC1 strict bounded schemas/raw binding helpers implemented and source-reviewed.
- [x] AC2 actual unprivileged AF_UNIX peer-before-payload/slot tests; production wrapper remains pinned and unavailable.
- [x] AC3 truthful unissued/unsupported refusals; no fabricated allowance, observation or effects.
- [x] AC4 source suite19 tests, no skip/failure/error on all three interpreters, plus independent reviewer replay on3.14.
- [x] AC5 exact accepted contract retained and legacy guarded modules unchanged; only explicit evaluator-contract source mode added.
- [x] AC6 commands/raw outputs/hashes retained; coverage limitations explicitly documented.
- [x] AC7 no protected access, runtime authority, new research call, secret use, reconciliation, stop release, replay, admission, promotion, production mutation, commit, delivery, acceptance, merge or push.
- [ ] Explicit source-commit authorization, committed delivery and independent PM acceptance. Story remains in_progress, not delivered/accepted.
- [ ] Full GRRR-q3hp driver and GRRR-6sso capstone readiness: NOT SATISFIED and not authorized by this source review.

## nd_contract
status: in_progress

### evidence
- Parent verified base HEAD 0b2365e30ab5858cb419f4f4ce9b2ce001850541, epic root clean, docs/findings absent, and live queue waiting on exactly GRRR-wcwy. GRRR-q3hp remains blocked and the full capstone GRRR-6sso remains deferred/rejected, not accepted.
- Verified all eight WIP source hashes against author manifest and raw diff SHA256 458c1c8ae3f13c080dd9c1532998381e7e80d89c973b5b884d47c02085a4082a. git diff --check passes. Existing common.py, trusted_transport.py, budget.py, persistent_budget.py, replay.py, ledger.py are byte-identical to HEAD. Accepted contract SHA256 9b0f0f5639a1f2f07539a1b1e22d33bb67e88e2dc78fe58ecc9925f356aaf8ad is an exact documentation suffix.
- Parent reran /opt/homebrew/bin/python3 -B scripts/test-story evaluator-contract (Python3.14.3); /Users/speed/miniconda3/bin/python3 -B scripts/test-story evaluator-contract (Python3.12.7); /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/bin/python3.9 -B scripts/test-story evaluator-contract (Python3.9.6). EACH reported tests=19, failures=0, errors=0, skipped=0, exit0. These are 19 repeated source tests, not 57 distinct scenarios or VM observations.
- Exact WIP, author evidence and independent parent stdout/stderr/commands/hashes retained outside the disposable worktree under .git/paivot/wip/GRRR-wcwy/parent-verify-20261104/. Verification script /tmp/grrr-wcwy-parent-verify-20261104.py. No worktree recovery/removal may discard this WIP.
- CoS readiness check failed tunnel-client-not-seen; fresh independent code review dispatched to allowed GLM Coding Plan route /root/review_evaluator_source_wip. Review verdict pending; author tests are not independent acceptance.
- Observe truthfully refuses without issued grant bytes; accounting v4 remains unsupported. All starts refuse; status/stop claim no cessation/settlement. Data/hash consistency is not issuance, provenance, allowance or authentication. Local unprivileged AF_UNIX tests are not UID320/321 or VM proof.
- No protected /Library/GRRR metadata/content access or mutation, runtime installation, allowance issuance, reconciliation, stop release, VM/replay, new Jev call, secret use, admission, promotion, source commit/delivery/merge or push performed. Disk is below live execution floors, so no runtime readiness is claimed.
- bd sync --status reported no beads database. The existing shared PAIVOT nd vault remains the project source of record; no competing beads database was initialized.

### proof
- [x] AC1-4 source implementation and focused tests reproduced by parent, subject to independent review.
- [x] AC5 existing tracked guards and modes unchanged except explicit evaluator-contract source mode.
- [x] AC6 all three existing interpreters ran 19 non-skipped tests with raw evidence retained. Author line-coverage output retained, not independently claimed as branch/runtime coverage.
- [x] AC7 scope maintained: no full milestone acceptance or runtime authority inferred.
- [ ] Independent code review of exact WIP and any resulting rework.
- [ ] Explicit source-commit authorization, committed delivery and independent PM acceptance.

## nd_contract
status: in_progress

### evidence
- Selected by pvg loop next, claimed atomically, and isolated at .claude/worktrees/dev-GRRR-wcwy on story/GRRR-wcwy from epic0b2365e.
- Security/IPC implementation delegated as one bounded task to /root/implement_evaluator_source_boundary, against independently approved contract9b0f0f5639a1f2f07539a1b1e22d33bb67e88e2dc78fe58ecc9925f356aaf8ad.
- Existing interpreters verified: Homebrew3.14.3, Miniconda3.12.7, CLT3.9.6. No new dependencies/installations or external service needed.
- Only small source-only unittest fixtures are permitted; actual VM/preparation/replay remains forbidden while below its floor. Host disk space has fallen again; no stable replay capacity is claimed.
- No source commit/delivery/acceptance is authorized yet. Uncommitted WIP must be preserved before any worktree recovery/removal; never force-clean it.

### proof
- [ ] AC1-6: implementation and measured source-test evidence pending.
- [x] AC7 boundary: capstone remains deferred/rejected-x3; no protected/runtime authority is granted.

## Implementation Evidence

PROOF:

### CI/Test Results
Commands run:
- /opt/homebrew/bin/python3 -B scripts/test-story evaluator-contract
- /Users/speed/miniconda3/bin/python3 -B scripts/test-story evaluator-contract
- /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/bin/python3.9 -B scripts/test-story evaluator-contract
- pvg verify research/capstone_contract.py research/capstone_client.py research/capstone_service.py tests/unit_capstone_contract.py tests/unit_capstone_peer.py tests/unit_capstone_suite.py scripts/test-story docs/CAPSTONE-EVALUATOR-PROTOCOL.md --format=text
Summary: PASS source19 tests on EACH3interpreters; failures0/errors0/skipped0, each exit0; static PASS6eligible files0issues. Full capstone/VM/replay NOT-RUN. Producing SHA8cf7d0d86d5103de3709d432a8c35b8101020440.

- Commands run:
  - /opt/homebrew/bin/python3 -B scripts/test-story evaluator-contract
  - /Users/speed/miniconda3/bin/python3 -B scripts/test-story evaluator-contract
  - /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/bin/python3.9 -B scripts/test-story evaluator-contract
  - pvg verify research/capstone_contract.py research/capstone_client.py research/capstone_service.py tests/unit_capstone_contract.py tests/unit_capstone_peer.py tests/unit_capstone_suite.py scripts/test-story docs/CAPSTONE-EVALUATOR-PROTOCOL.md --format=text
- Summary: source unit/local-peer PASS (19 tests on EACH of Python3.14.3,3.12.7,3.9.6; failures0, errors0, skipped0; all exit0); static PASS (6 eligible files,0issues). VM/corpus/replay/build and full capstone11 gates NOT-RUN, not skipped-green. No external CI claimed.
- Coverage: stdlib trace LINE coverage contract95.6%, client96.9%, service93.5%, measured on producing commit by /opt/homebrew/bin/python3 -B -m trace --count --summary --missing --coverdir <repo>/.git/paivot/wip/GRRR-wcwy/post-commit-20261104/coverage tests/unit_capstone_suite.py. Branch/runtime coverage unmeasured. These source results are not VM or allowance evidence.
- Raw command arrays/stdout/stderr/hash manifests: .git/paivot/wip/GRRR-wcwy/post-commit-20261104/runs.json and run0..run4.stdout/stderr. Earlier detailed delivery proof, AC mapping and all historical notes are preserved above.

### Commit
- Branch: story/GRRR-wcwy
- SHA: 8cf7d0d86d5103de3709d432a8c35b8101020440
- Exact reviewed8files,1034insertions/2deletions, existing guarded modules unchanged; no push.

### Independent Review and Scope
- SOURCE_SLICE_REVIEW: APPROVED. Exact security review SHA256 f18b42dd36979b9bb13fabe7ef3d71b7b99b2bb9c9898187f857fcd902de778b; independent19-test replay twice on3.14,0fail/error/skip. Retained review and log under .git/paivot/wip/GRRR-wcwy/parent-verify-20261104/.
- Operator authorized local source commits, PM delivery and only PM-accepted epic merges. This supersedes historical WIP-only source restrictions, not protected/runtime gates. No main/push/protected install/write/reconcile/stop release/VM/replay/admit/promote/prod authority.
- No installed authority backend or descriptor: v4 unsupported, observe refuses absent issuance, start always blocked, status/stop absent. Data consistency is not provenance/authentication/authority. Full q3hp/6sso remain unaccepted.
- Delivery-note repair is append-only: native append-notes insertion left earlier contracts after newer ones and the first proof used a noncanonical heading. This canonical proof was inserted at Notes EOF through the official pvg nd edit editor API, using one apply_patch insertion. No prior text, code, criteria, hashes or gate was changed; no pvg/nd implementation was modified.

### AC Verification
| AC # | Requirement | Code Location | Test Location | Status |
|---|---|---|---|---|
| 1 | exact schemas11gates/raw bindings, consistency only | capstone_contract.py | ContractTests9 | PASS source |
| 2 | authenticated peer-before-payload/slot, explicit test-only boundary | capstone_client.py; capstone_service.py | PeerTests10 with actual AF_UNIX credentials | PASS local only |
| 3 | truthful unsupported/unissued/start refusal and no fabricated effects | RefusalService; production_client | real_refusal_channels; counterfeit_grant_cannot_start | PASS refusal |
| 4 | real bounded19test suite, no zero/skip green | unit_capstone_suite.py | 3 producing-commit interpreter runs | PASS source |
| 5 | existing guards/modes preserved and exact contract docs | scripts/test-story; protocol docs | exact diff/hash/static evidence | PASS |
| 6 | actual commands/counts/coverage/source hashes | retained post-commit evidence | run0..run4 and manifests | PASS |
| 7 | source-only and no protected/full-capstone authority | documented scope and unchanged modules | reviewed exact bytes; no protected effects | PASS boundary |

LEARNINGS:
- Never fabricate an observation digest from unissued authority; fail closed.
- Keep actual local-peer source tests distinct from production identity, VM and allowance proof.
- Preserve old notes byte-for-byte, but verify the authoritative proof is actually at Notes EOF rather than trusting append placement.

## nd_contract
status: delivered

### evidence
- Producing SHA8cf7d0d86d5103de3709d432a8c35b8101020440,19source tests per3interpreters,0fail/error/skip, static6eligible files0issues. Exact raw results/review retained.
- Local source commit/delivery authorized; independent security review approved. PM acceptance pending. No merge/push/protected/runtime operation.

### proof
- [x] AC #1: strict schemas and original-byte consistency bindings.
- [x] AC #2: actual unprivileged AF_UNIX peer-before-payload/slot boundary.
- [x] AC #3: unsupported/unissued/absent capability refusals, no claimed effect.
- [x] AC #4:19 source tests,0fail/error/skip, all3interpreters.
- [x] AC #5: existing guarded modules/modes unchanged, exact contract docs retained.
- [x] AC #6: producing-commit commands/results/hash/line-coverage evidence.
- [x] AC #7: no protected authority or capstone closure implied.

## History
- 2026-11-04T16:46:17Z dep_added: blocks GRRR-q3hp
- 2026-11-04T16:46:19Z status: open -> in_progress
- 2026-11-04T16:46:19Z auto-follows: linked to predecessor GRRR-ev2w
- 2026-11-04T16:46:19Z claimed by dev-GRRR-wcwy
- 2026-11-04T17:31:38Z status: in_progress -> in_progress
- 2026-11-04T17:31:38Z auto-follows: linked to predecessor GRRR-888u

## Links
- Parent: [[GRRR-2t3h]]
- Blocks: [[GRRR-q3hp]]
- Follows: [[GRRR-ev2w]], [[GRRR-888u]]

## Comments
