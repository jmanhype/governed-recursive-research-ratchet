# Executable capstone backend design v2 — 2026-11-04
IMPLEMENTATION_DESIGN: READY_FOR_REVIEW
Proposed source implementation contract, NOT accepted design, q3hp AC1 proof,
installed authority, allowance, or execution permission. Independent acceptance
precedes source implementation; concrete implemented mapping acceptance precedes
q3hp wiring. One substantive backend story plus wiring, not refusal-only slices.

## Evidence, limits, review disposition
Verified HEAD `2b601462ba0ffb5aee6239aa22b06c26801dfaf9`; previous `2dc0b3a`,
`9a439a0`; clean git status; `docs/findings/` absent. Originals preserved:
design SHA `340a6667eeddf8d86c093a873ef4a7410d9d262c31aa645b4a47ac6e9f1ef05c`,
review SHA `511557d6a6c2dcb468228ec6a4960f6f07bef2356b415444a46bb8d69c6a4a3a`.
Bounded Verify-tier exact-source fallback: capstone_journal.py, its schema,
ledger.py, control.py, control_worker.py, trusted_transport.py, capstone_contract.py,
ARCHITECTURE.md:184–236,285–313. Graph unavailable; no exhaustive audit claimed.
Supplied spendability/reserved-replay audits trusted within scope EXCEPT scalar
minimum across resource units is rejected. No source/test/build/runtime/tracker,
protected-path metadata/content, private archive, network, install or git mutation.
F1 resolved in §3: immutable approval versus unique durable issuance, original bytes.
F2 resolved in §6: transferred locked open-file description and explicit close protocol.
F3 resolved in §4–5: stable campaign control_run, SQL-only hook, complete projection.
These are reviewable design resolutions, not tested implementation claims.

## 1. Source ownership and delivery scope
| File | Proposed concrete responsibility |
|---|---|
| NEW research/capstone_installation.py | open_installed(role), no-create handles/identity checks; separate unprivileged open_public_fixture(root) |
| NEW research/capstone_backend_contract.py | strict records below, campaign validation, phase gate requirements |
| NEW research/capstone_backend_schema.py | literal backend-v1 DDL/constraints and exact read-only schema/replay validation; NOT installer |
| NEW research/capstone_authority.py | validate_current_capture; administrative issue_campaign(handles, auth_raw, spec_raw); no wire issuer |
| NEW research/capstone_accounting.py | v4 observe; explicit v5 reserve_leaf/meter_leaf/settle_leaf/halt; no activation/recovery/release |
| NEW research/capstone_backend.py | EvaluatorBackend.open_existing, observe/start/status/stop, durable projection and actual scheduling |
| NEW research/replay_material.py | shared load_material and spec/observation/verdict functions extracted once |
| NEW research/capstone_replay.py | execute_leaf(context, leaf, permit), finish_pair; pre-reserved leaves, fresh guests |
| NEW research/capstone_launch.py | LaunchBroker prepare/launch/read/write/cancel/status, real owned handles and FD protocol |
| NEW research/capstone_corpus_profile.py | full frozen-corpus material/spec/receipt mapping, not D011-only |
| research/trusted_transport.py | authenticated bounded connect_send/PendingReply plus separate sendmsg/recvmsg FD channel, restrictive socket modes |
| research/control.py, control_worker.py | no-DDL StopCoordinator.open_existing; SQL-only backend stop hook, cancellation outside ledger lock, child-owning broker mode |
| research/replay.py, corpus_execution.py | shared material/validation extraction and installed broker seam; unchanged legacy v1 guards/default factory |
| research/capstone_client.py, capstone_service.py | installed_client and UID320 service; retain unavailable production_client and fixture-only test_endpoint guards |
| NEW research/capstone_driver.py, scripts/capstone-driver | q3hp two-command grammar and immutable public outputs; no accounting access |
Additional focused tests/unit_capstone_backend_*.py, unit_capstone_driver.py,
scripts/test-story and protocol/architecture docs. Journal v1 and its replay/schema
are UNCHANGED; no new object uses reserved capstone_ SQL namespace. Existing Ledger
constructor creates schema, so installed opening must reuse validated existing-ledger
factory, never invoke constructor. No runtime DDL/repair or hidden installation.

## 2. Installed trust and bounded records
Fixed descriptor `/Library/GRRR/capstone-v1/installation.json`, fixed ipc sockets;
no caller root/path/URL/UID/environment/profile/backend override. UIDs320 evaluator,
321 broker constants. Operator UID must match root descriptor, approval and peer.
Root/code/descriptor root:wheel, directories0755, files0444, single-link regular
files, no symlink ancestor or writable alternate ACL. Ledger/accounting UID320
0700; broker state UID321 0700. IPC root-owned with exact approved traversal/socket
ACLs, not transport's existing0666. No-follow retained dirfds, byte hashes, identity
rechecks reject replacement. Installer establishes topology; factories never repair.
Authenticate operator before payload/allocation, UID320 before client sends, UID320
before broker reads; broker replies must be UID321 bound to exact session/launch.
Separate control slots/threads independent of runner IO. No caller bool is evidence.

InstallationV1 exact fields: schema, operator_uid, source_manifest_sha256,
runtime_manifest_sha256, evaluator_manifest_sha256, runner_manifest_sha256,
interpreter_sha256, bootstrap_sha256, qemu_manifest_sha256, assets_sha256,
corpus_sha256, replay_catalog_sha256, replay_image_sha256, execution_profile_sha256,
policy_sha256, accounting_binding_sha256, baseline_endorsement_sha256,
authorization_registry_sha256, floors_sha256, timing_policy_sha256.
schema=`capstone-installation-v1`; all fields except operator_uid are H digests.
Inventory=SHA256(canonical sorted [{relative_path,mode,sha256}]); reviewed exhaustive
runtime closure, not Git coincidence. Full40hex commits plus exact clean executable
closure; pin interpreter/import/bootstrap, QEMU code/data and assets separately.
Frozen corpus=`dfa75ef2bf3d43fd4f750094fe643afe4f204812c0ae2426276bedb471fa8529`.
New image/catalog/backend/runtime/live binding pins UNKNOWN until built/reviewed;
old P/R artifacts or parent statements cannot substitute. Installation remains gated.

H=64hex, I=existing identifier, N=nonnegative integer (bool rejected), U=operator UID,
V=unchanged Vector(currency=USD,money_cents,execution_us,review_us), raw=canonical
base64 of exact original bytes; nullable marked ?. No extras/duplicate keys/floats.
C(x)=common.canonical(x), SHA bytes exact. Domain hash D(tag,x)=SHA256(ASCII(tag)
+ one NUL byte + C(x)); never concatenate textual hashes without canonical framing.
Bundles <=16MiB/256 leaves; each wire v1 record <=MAX_WIRE; refuse, never truncate.
All record names below have literal schema values explicitly specified.

CampaignSpecV1 (`capstone-campaign-spec-v1`)={schema,campaign_id:I,
shared_bindings:Bindings without invocation_bytes_sha256,policy:H,coverage:H,
leaves:[Leaf],maximum:V,expires_ns:N}.
Leaf={index:N,leaf_id:H,pair_id:H,purpose:corpus|replay,challenge:I,
role:baseline|candidate,attempt:N,request:Request,invocation_raw:raw,maximum:V,predecessor:?N}.
Indices contiguous0..n-1; unique leaf IDs and distinct request.run; predecessors
smaller indices. Coverage enumerates every frozen seed/clean negative/spec; pair_id
identifies a predeclared pair with distinct baseline/candidate leaves. Maximum is
exact componentwise sum including all retries/baselines/negatives. No added leaves.
Hash construction, in this exact order (no unspecified “material tuple”):
1. Skeleton={schema:"capstone-campaign-skeleton-v1",campaign_id,shared_bindings,
policy,coverage,maximum,expires_ns,leaves:[{index,pair_id,purpose,challenge,role,
attempt,maximum,predecessor,run}]}; run is the predeclared request.run, not derived.
2. S=D("campaign-skeleton-v1",Skeleton); scope=D("leaf-scope-v1",{skeleton:S,index}).
3. invocation_raw=base64(C({run,scope,maximum})); Request={schema:"capstone-request-v1",
run,scope,maximum,bindings:{...shared_bindings,invocation_bytes_sha256:SHA256(decoded invocation_raw)}}.
4. leaf_id=D("campaign-leaf-v1",Leaf with ONLY leaf_id omitted); spec bytes=C(spec).
Spec raw must equal those canonical bytes. pair_id is a predeclared H, NOT a hash
of resulting leaves. shared_bindings.policy==policy; complete spec hash has no grant.
Golden byte/hash vectors cover NUL framing, ordering, index/run changes and base64.

AuthorizationV1 (`capstone-authorization-v1`)={schema,action:capstone-execute,
operator_uid:U,campaign_spec_sha256:H,baseline_endorsement_sha256:H,
installation_sha256:H,not_before_ns:N,expires_ns:N,maximum:V,leaf_ids:[H],review_anchor:H}.
Approval enumerates exact finite leaves/total. SHA256(auth_raw) binds original bytes,
not reserialization. Matching caller JSON is never issuance or import permission.
PrepareBundleV1 (`capstone-prepare-bundle-v1`)={schema,campaign_spec_raw:raw,
grant_bundle_raw:raw,decision_json_raw:raw,decision_markdown_raw:raw}.
GrantBundleV1 (`capstone-grant-bundle-v1`)={schema,campaign_spec_sha256:H,
grants:[{leaf_id:H,grant_raw:raw}]} ordered by leaf index.
CampaignPlanV1 (`capstone-campaign-plan-v1`)={schema,campaign_spec_raw:raw,
grant_bundle_raw:raw,decision_json_raw:raw,decision_markdown_raw:raw,
authorization_bytes_sha256:H,leaves:[{leaf_id:H,plan:Plan}],gates:Gates,campaign_plan_sha256:H}.
Selfhash=SHA256(C(record omitting ONLY campaign_plan_sha256)); each unchanged v1
Plan requires actual authenticated observation. Root plan is NOT journal Plan.
FailureRecordV1 (`capstone-failure-v1`)={schema,phase:prepare|run,input_sha256:?H,
authorization_sha256:?H,campaign_plan_sha256:?H,leaf_id:?H,operation_id:?H,code:Code,
gates:Gates,effects:none|possible|recorded,next_action:correct-input|query-status|operator-recovery,created_ns:N}.
CampaignManifestV1 (`capstone-campaign-manifest-v1`)={schema,campaign_plan_sha256:H,
leaves:[{leaf_id:H,manifest:Manifest}],gates:Gates,execution:completed|partial|not-run|unknown,
verification:blocked|verified,admission:blocked,promotion:disabled,failures:[FailureRecordV1]}.

## 3. Immutable approval versus one-time durable issuance (F1)
Root-installed immutable registry bytes are C({schema:"capstone-approval-registry-v1",
entries:[ApprovalV1]}) sorted by authorization_sha256, unique authorization and
campaign_id. ApprovalV1={schema:"capstone-approval-v1",authorization_sha256:H,
authorization_raw:raw,campaign_spec_sha256:H,campaign_id:I,issuance_id:H,
receipt_max_age_ns:N,floors:H,import_review:H}. Issuance_id is fixed by approved
import, UNIQUE across entries; import_review resolves independent approval bytes.
Registry hash in descriptor is immutable inventory, NOT mutable consumption state.
Reinstallation must retain ledger lineage/issuance uniqueness; fresh empty ledger
without independently accepted lineage is refused. No import endpoint on service.

New installed ledger schema literal `capstone-backend-index-v1`; SQL tables below
have exact columns (TEXT H/I/enums, INTEGER N/bool, BLOB canonical record bytes).
All columns NOT NULL unless marked ?; FKs enforced, DELETE journal/FULL synchronous.
PK/UNIQUE plus named indices stated below are exhaustive; no other indices/triggers.
Every table has delete-denial trigger backend_v1_<suffix>_no_delete. Immutable tables
also update-denial trigger _no_update; mutable tables allow ONLY transitions below,
with immutable key/identity columns enforced by _guard_update trigger plus replay.
Exact sqlite_master SQL and implicit-index inventory must be frozen in schema module
and tested; runtime rejects additions/shadows/attachments, opens existing only.
* backend_v1_issuance(auth_hash PK, campaign_id UNIQUE, issuance_id UNIQUE,
  spec_hash, registry_hash, auth_raw BLOB, spec_raw BLOB, intent_anchor,
  phase: intent|issued, bundle_raw ?BLOB, issued_anchor ?TEXT).
  Only intent->issued may set bundle_raw/issued_anchor once; all others immutable.
* backend_v1_campaign(campaign_id PK FK issuance.campaign_id, control_run UNIQUE,
  issuance_id UNIQUE FK issuance.issuance_id, stop_epoch INTEGER, stopped INTEGER,
  stop_operation ?TEXT, stop_anchor ?TEXT). Initially epoch0/stopped0/nulls;
  only monotonic stop transition0->1 (epoch0->1), never release/reset/delete.
* backend_v1_leaf(campaign_id FK campaign, leaf_index INTEGER, leaf_id UNIQUE,
  grant_id UNIQUE FK capstone_grants, request_run UNIQUE, request_hash,
  PRIMARY KEY(campaign_id,leaf_index)); immutable, exact finite approved cardinality.
* backend_v1_binding(operation_id PK, grant_id UNIQUE FK leaf.grant_id,
  plan_hash,start_hash,start_raw BLOB,bind_anchor); immutable. operation_id is
  unchanged capstone_contract.operation_id(grant_id,plan_hash), not issuer-selected.
* backend_v1_launch(launch_id PK, operation_id UNIQUE FK binding, control_run,
  epoch INTEGER, session_id, intent_anchor, record BLOB); only record mutable.
* backend_v1_projection(operation_id PK FK binding, record BLOB); only record mutable.
No SQL reference from binding to capstone_operations: binding precedes journal claim.
No row is itself authority: full backend event replay and cross-index joins required.
Only indices beyond implicit PK/UNIQUE: none (<=256 leaves makes scans bounded).

All backend state events use exact envelope {format:"capstone-backend-event-v1",
action,record,idempotency_key,version:1}; Ledger supplies last two. action is one of
issuance-intent,issuance-commit,bind,launch-intent,launch-update,projection.
record contains affected rows as {table,rows:[{column names}]} list,
table from above allowlist; BLOBs encoded raw. To avoid self-hash cycles, OMIT only
receipt-derived fields for the current transition: issuance-intent.intent_anchor,
issuance-commit.issued_anchor, bind.bind_anchor, launch-intent.intent_anchor and
projection.record.last_event. Reducer supplies receipt.digest AFTER event hashing;
all other columns are present. Projection Operation.anchor is the validated PRE-event
snapshot; status rebases it read-only. Stop hook similarly derives stop_anchor and
projection.last_event from stop receipt, never embeds its own hash in event bytes.
Replay checks action-specific legal
transitions, full equality, original bytes and anchors to event receipt. Stop hook
uses existing safe-stop event plus exact backend_stop extension in §4, not envelope.
Unknown backend action/schema/version refuses; journal ignores non-journal formats
as today while still checking core chain/idempotency. Backend validation is separate.

Issuer holds exclusive ledger writer lease through lookup/append. Require registry
entry and original auth/spec bytes equality, approval/bounds/source validation.
If auth row issued: verify replay/registry/rows, return STORED bundle_raw byte-for-byte,
even if expired/consumed/stopped (export is not renewed authority); changed inputs,
registry issuance_id/mapping, extra/missing leaf or grant bytes refuse. Do not call
Ledger.append_atomic with today's tip for cached issuance; its idempotency API binds
original prior/body. A prior intent-only row returns RecoveryRequired, no export/mint.
If absent: append issuance-intent atomically inserting intent row; key=D("issue-intent-v1",
{authorization:auth_hash}); row intent_anchor is this receipt.digest. No grants yet.
In SAME uninterrupted issuer invocation, construct deterministic grants:
grant_id=D("issued-leaf-grant-v1",{issuance_id,authorization:auth_hash,spec:spec_hash,leaf_id});
Grant fields use exact Request bindings/scope/maximum, approved UID/auth/review_anchor,
intent_anchor as issuance_anchor, stage=poc, approval window/floors/receipt age.
Append issuance-commit and in ONE callback insert all capstone_grants with
consumed_by=NULL, finite leaf rows, campaign row, and change issuance row to issued
with exact bundle bytes/receipt. Key=D("issue-commit-v1",{authorization:auth_hash}).
control_run=D("campaign-control-v1",{issuance_id,campaign_id}); no control_runs row
yet, matching existing StopCoordinator's absent-means-epoch0 behavior.
Objects precede references; orphan objects grant no authority. Export only after
commit and validation. Crash before intent: no grants, identical deterministic IDs
if retried. Crash after intent/before commit: intent-only held, no automatic resume.
Crash at/after commit: transaction is all-or-none; issued returns original bundle
or intent refuses, never a second set. Per-grant uniqueness alone is NOT the guard.

## 4. Campaign control, unclaimed leaves and transaction composition (F3)
Stable authority is StopCoordinator on campaign.control_run, NEVER request.run.
Each leaf request.run remains its immutable workload identifier. All per-leaf final
checks join grant->leaf->campaign->control_run; epoch0 only while not stopped and
no recovery. Missing campaign/control inconsistency blocks, never creates allowance.
Start binds exact Start to binding row in its own backend bind event BEFORE calling
Journal.claim. Serialize this and claim using the campaign control gate in §6;
no nested transactions. Bind/claim/reserve crash gaps are recovery-required holds.
Unbound grants cannot start after campaign stop. Authenticated v1 Stop resolves
operation_id through binding, then stops ENTIRE campaign (document this scope);
unknown operation_id refuses, not guessed. Operator may stop before any Start using
existing direct control action {action:stop,run:control_run,key,reason?}; no new CLI.
control_run is deterministically available from issued campaign. No fake Operation
is invented for an unclaimed/unbound leaf: control returns typed stop receipt instead.

StopCoordinator.stop acquires §6 gate, then ledger.lock; existing append_atomic is
the ONLY transaction. Its callback updates existing control_runs/stop_operations and
invokes SQL-only backend_stop_hook(db,receipt,control_run,epoch,operation,primary).
Hook performs no Journal call, append, BEGIN/COMMIT, object IO or broker RPC. It updates
campaign stop columns and any existing projection stop flags in that SAME transaction.
safe-stop/ref event includes backend_stop={schema:"capstone-campaign-stop-v1",
campaign_id,control_run,epoch,primary_operation,affected_operations:[H]} (sorted
all bindings, including preclaim). Replay reconstructs exact updates from this event.
First stop increments0->1, repeated new key references SAME primary/epoch, same key
returns original receipt. Reject same key used for different run/reason. Stop on an
unclaimed campaign fences its complete finite leaf set with ONE campaign row.
Legacy tracked_launches keyed only by run/pid cannot represent this campaign; do not
populate it in backend mode. StopCoordinator's backend adapter uses backend_v1_launch
for all children and campaign epoch; legacy behavior outside backend mode unchanged.
After durable stop commit return ack BEFORE cancellation. Release gate/ledger locks;
cancel via independent broker channel outside both locks. Reacquire gate then ledger
to verify same primary/epoch and append final cancellation outcome. No guest waits
inside control/ledger locks. Baseline verification is independent protected evidence,
not current default outcome.get('baseline_ok') bool. Failure means recovery, not safe.
Journal.request_stop for EXISTING journal operations may run later, each standalone
transaction, as subordinate diagnostic latch. False/missing journal stop bit never
overrides campaign stop. Crash before/after subordinate latches leaves authoritative
stop intact; startup does not repair journal or reissue permits. No journal v1 replay
change, journal completion states or synthetic claim for unclaimed leaves.

## 5. Full Operation projection and crash state
Projection row is C({schema:"capstone-backend-projection-v1",operation:Operation,
last_event:H}); Operation is exact existing capstone-operation-v1 with ALL fields:
schema literal; operation_id/grant_id/plan_sha256/start_request_sha256 from immutable
binding+Start; reservation from validated journal/accounting join or null; gates
from stored phase-tagged gate evidence, not caller plan assertions; anchor={ledger_sequence,
ledger_tip,accounting_snapshot,grant_registry_snapshot,installation} from consistent
validated snapshot and pinned identities; stop_requested=campaign.stopped OR journal
latch; result_object nullable content digest; blockers are exact existing Codes.
Projection event records evaluator evidence, not a cached status assertion. Status
replays durable events/joins to current snapshot, overlays stop/recovery and current
Anchor read-only; never writes or treats JournalRecord as public Operation.
| Durable evidence (precedence recovery > stop > ordinary progress) | state / dispatch |
|---|---|
| binding without journal claim, missing join, partial accounting intent, abandoned session/launch | recovery-required / unknown if dispatch intent exists, otherwise not-run |
| claim; no reserve intent | claimed / not-run |
| committed matched reservation | reserved / not-run |
| journal pending + launch intent, no confirmed child | dispatch-pending / pending; after ambiguity/restart recovery-required / unknown |
| broker physical-child result committed with owner/session identity | running / pending |
| campaign stop committed, cancellation unfinished | stop-pending / prior dispatch (unknown stays unknown) |
| verified cessation AND integrity for every campaign launch | stopped / completed if dispatch outcome known, otherwise unknown |
| verified normal exit, immutable observation, integrity, meter/settle completion | completed / completed |
Normal execution completion does not imply verified finding/all gates. Any uncertain
cut preserves holds and adds RecoveryRequired; no safe-stop/settle from PID absence.
result_object references C({schema:"capstone-backend-result-v1",kind:execution|stop,
operation_id,control_run,epoch,evidence:[H],stop_receipt:?H,stop_outcome:?H}); referenced
typed StopReceipt={schema:"capstone-stop-receipt-v1",control_run,operation_id,
epoch,ledger_sequence,ledger_tip,cancellation:pending|verified|recovery-required};
StopOutcome={schema:"capstone-stop-outcome-v1",control_run,operation_id,epoch,
state:pending|verified|recovery-required,launches:[{launch_id,cessation_evidence:?H}],
baseline_evidence:?H,blockers:Codes}. Receipt acknowledges commit only; verified
requires independently validated cessation for ALL intents and baseline. All11 gates retained.
Before claim there is no valid v1 Operation; binding-only exception is a recoverable
attempt with real Start identity, explicitly recovery-required, never claimed success.

## 6. Physical launch/stop kernel serialization and ownership (F2)
Choose BSD flock on an existing fixed gate inode, with SCM_RIGHTS transferring the
SAME locked open-file description, NOT a second flock in broker. Installation supplies
root-owned fixed ipc/control-gate, read-open ACLs only for320/321; inode replacement
denied. flock exclusive on read-open FD must be source/live-qualified on target OS.
Evaluator uses fresh O_RDONLY|O_NOFOLLOW|O_CLOEXEC open per acquisition, verifies inode,
LOCK_EX|LOCK_NB deadline loop; never dup a global gate FD between local contenders.
One gate serializes all campaigns (bounded finite dispatch, deliberate simplicity).
Order gate -> ledger.lock -> short SQL; NEVER hold SQL/ledger.lock across IPC. Writer
lease is separate, does not prevent control transactions; no guest wait under either.

Broker prepare allocates launch_id/session_id with NO child, pins compiled QEMU args
from installation+leaf (never caller argv). Launch record schema=`capstone-launch-v1`:
{schema,launch_id,operation_id,control_run,epoch,session_id,state:intent|owned|ceased|unknown,
pid:?N,owner_start:H,evidence:[H]}; pid diagnostic only; owner_start is fresh broker
boot nonce; identity keys immutable. Intent durable in evaluator DB precedes child.
Broker owns real Popen/unreaped child handle and all pipes; no setsid, no child FD
inheritance (close_fds plus explicit close in spawn actions). IO RPC bounded separately.
Broker owns no ledger writer FD. Peer/session/one-shot launch IDs checked before work.

Launch sequence (all deadlines monotonic and installation timing-policy bound):
1. Evaluator acquires gate, checks campaign epoch/no-stop, journal reservation,
current allowance/floors/gates; appends launch-intent; calls journal pending and
consumes its returned LIVE permit once. Pending with no permit refuses, including restart.
2. Over fresh authenticated AF_UNIX stream sendmsg carries one fixed one-byte marker
and exactly ONE SCM_RIGHTS gate FD; then bounded length-prefixed LaunchTicketV1 bytes:
{schema:"capstone-launch-ticket-v1",launch_id,session_id,operation_id,control_run,
epoch,intent_anchor,deadline_monotonic_ns}. Full receive <=MAX_WIRE before action;
ancillary truncation, wrong FD count/type/inode, extra data, timeout or partial frame
closes ALL received FDs/socket without launch. Broker never reacquires flock.
Receiver immediately marks received FD noninheritable before any spawn/thread handoff.
3. Evaluator CLOSES its gate copy after send attempt, NEVER LOCK_UN. Kernel/socket
queue or broker owns the transferred lock until its last copy closes. If zero bytes
sent, own close releases; ambiguous sends are never retried. Evaluator holds no gate
copy/ledger lock while bounded reply wait; stop tries separate fresh open description.
4. Broker validates full ticket/current session/deadline and intent binding; it may
physically spawn ONLY while holding received locked FD. Child is immediately inserted
into owner map before any other broker handler can observe it; precommitted evaluator
intent already tracks this exact launch as possibly active. Spawn error is still an
audited outcome, not a new permit. Broker sends child-created result to dedicated
evaluator handoff handler, which commits owned record with PID+owner_start in existing
intent row and replies COMMITTED. This handler uses ledger.lock, NOT gate (broker holds it).
5. Broker accepts only matching COMMITTED before closing gate copy. No LOCK_UN anywhere
in handoff: closing evaluator's duplicate cannot unlock broker's descriptor. If ACK
lost/late or evaluator dies, broker FIRST marks session unusable and closes gate and
connection, THEN terminates its exact owned child with bounded TERM/KILL/wait outside
gate/ledger locks; durable intent remains visible to any intervening stop transaction;
evaluator intent/owned state remains unknown/recovery, never resumed or refunded.
No guest protocol IO, completion wait or abort teardown wait holds the gate in1–5;
only bounded spawn and tracking handoff do. Delayed COMMITTED cannot revive session.

Stop acquires separate gate FD before its durable transaction. If stop obtains it
first, epoch commits and later launch recheck rejects. If launch wins, stop cannot
commit until broker closes transferred FD, so physical child exists with durable
intent (and normally committed owned tracking) BEFORE stop; all intents are cancelled
or conservatively unknown. A queued descriptor retains the lock: it cannot launch
after a successful stop commit. Failed/lost send that leaves queued rights is bounded
by broker receive deadline, never assumed absent. Broker crash closes rights, but
possibly orphaned child remains represented by durable intent. Stop can commit fence
then return cancellation-pending/recovery, never claim cessation from broker death.
On lock deadline exhaustion: NO durable stop ACK; dedicated best-effort cancel,
durable recovery marker where possible, fence service and report RecoveryRequired.
Never forcibly unlock/recreate gate or let delayed broker launch bypass it. A hung
holder can deny ACK, not authorize work after ACK. Timing qualification must bound
this path; unavailable/unmeasured bound blocks real execution, not a fabricated default.
Fresh broker/evaluator startup validates all intents/session closures; unresolved
intent/owned/pending state fences all new work, no bare PID adoption, no resend, no
automatic recovery. Even late evidence does not automatically release that fence.
Broker signals ONLY its exact unreaped owned child under its owner-map lock; finish
identity/signal actions before wait reaps to prevent PID reuse. No ps/name/killpg path
in backend mode. Existing legacy control_worker implementation is NOT this guarantee.
Dedicated launchd job AbandonProcessGroup=false/no child setsid is the proposed
OS teardown boundary for broker death; actual launchd crash-teardown qualification
and pinned launcher policy REQUIRED before production execution, not inferred from
source process tests or a caller-provided qualification JSON. Failure leaves holds.

## 7. Current authority, explicit v5 accounting and real replay
BaselineEndorsementV1 (`capstone-baseline-endorsement-v1`)={schema,binding_sha256:H,
store_identity:H,schema_sha256:H,baseline_raw_sha256:H,ledger_anchor:H,package_sha256:H,
quiescence_receipt:H,provenance_receipt:H,completeness_receipt:H,independent_review:H,
decision_sha256:H,valid_from_ns:N,expires_ns:N}. References resolve independently
accepted immutable bytes, not bools. Validate current schema/rows/BLOBs, custody,
writer exclusion, complete lineage/side stores/pending/unknowns and subsequent deltas.
Unknown writer/history, unexplained delta, empty unproven DB or stopped store blocks.
Historical validators are not current authority; reuse validate_evidence arithmetic
only after current validation, never rewrite execution_authorized=False/private builders.
For EACH r: R[r]=min(POC.ceiling[r]-known[r]-unknown_bound[r],milestone.ceiling[r]
-known[r]-unknown_bound[r]); preserve positivity checks, compare remaining finite maxima
componentwise. No scalar unit mixing, duplicated charges or deduction of unknown holds.
Retained `unissued-independent-replay-v4` stays mode=ro even if stop bit changes.
Operational successor=`capstone-operational-accounting-v5`; V5Binding schema=
`capstone-v5-binding-v1`, exact fields {schema,version:5,campaign:H,store_id:H,
directory:fixed-derived-path,profiles:[independent-replay],device:N,inode:N,
prior_history_receipt:H,predecessor_binding:H,activation_receipt:H,baseline_endorsement:H,
authority_schema:capstone-operational-authority-v1}. campaign is complete spec hash.
Separate future authorization/installation must carry forward COMPLETE v4 lineage,
known liabilities, all unresolved full-max holds, bounded unknowns and POC/milestone
caps losslessly, with exact identity and stop disposition. No implicit migration,
activation, reconciliation, stop release or reset. v5 same accounting table layout;
legacy v1 guard unchanged; no Budget constructor/inheritance bypass. SQL allowlist
only reserve/meter/settle/stop=1/disclosed overhead, never DDL/attach/delete/stop=0.
Cross-process writer-exclusion lease covers accounting effects; gate protects final
control checks. claim -> ledger reserve-intent -> v5 BEGIN IMMEDIATE revalidate and
deterministic reserve -> commit -> journal record_reserved; intent includes before/
after digests/exact rows. Cross-DB crash preserves hold and fences, never auto-repairs.
Trusted measurements -> meter intent -> v5 meter/settle -> ledger completion, only
after verified cessation+integrity. Uncertainty holds maximum; every liability once.
Pre-reserved replay context never constructs ReplaySession or reserves again. Extract
material/reservation checks/observation/spec/verdict/meter logic once; legacy v1 intact.
Every baseline/candidate fresh separate guest/permit/send, no baseline cache or
candidate-authored logs as authority. Full profile maps ALL frozen seeds and clean
negatives with pinned authoritative spec and validated receipts; missing spec blocks
verification, never guessed from implementation. Source full-profile preparation/new
catalog/image definition included; building/provisioning/live qualification gated.

## 8. Gate phases, CLI and complete acceptance matrix
All11 unchanged: source_environment_identity, isolation, protected_asset_integrity,
baseline_correctness, trusted_observation, independent_replay, specification_traceability,
evidence_integrity_currency, budget_state, reviewer_outcome, action_specific_human_approval.
Prelaunch requires exact pins, approved isolation mechanism/live prerequisites,
current protected baseline, baseline input/spec, trusted observer, finite fresh-pair
plan, authoritative spec, current anchors, known budget+reservation, independent
source/plan review and bounded human execution approval. Postrun requires actual
isolation/cessation/integrity, fresh baseline/raw observations/pair verdict, exact spec
mapping, complete current export, measured accounting and independent result review.
Phase-tagged evidence prevents prelaunch proof impersonating runtime pass; postrun
not-run in Plan is allowed, no circular refusal or client waiver. Final verification
needs all11 fresh applicable gates; admission separate/blocked, promotion disabled.
Preserve ALL seven original6sso journeys, >=20 seeds, clean negatives, comparison/Jev,
stop/crash/admission races, tamper, accessibility and cost/report proof; backend alone
cannot close6sso or authorize Jev/admission. Historical milestone checklist unchanged.
Grammar ONLY `prepare --request BUNDLE --authorization AUTH --output PLAN` and
`run --plan PLAN --authorization AUTH --output MANIFEST`; reject extras. Prepare:
public lexical guards -> strict bytes -> installed peer -> issued campaign/current
history -> allowance -> floors -> phase gates. NO writes/nonce registration/DDL/VM.
Run revalidates before claim and every send; timeout queries known operation once,
no effect retry. Public output root bound to operator; no-follow dirfds and exclusive
O_CREAT|O_EXCL|O_NOFOLLOW0600, file+directory fsync, never overwrite. Unsafe/existing
output: stderr+nonzero, no sidefile. FailureRecord not fake Plan/Receipt; run nonzero
for partial/unknown/blocked verification even when execution completed.
| Acceptance scope | Required actual proof; not interchangeable |
|---|---|
| Source issuance | real temp SQLite, repeated same bytes byte-identical bundle, changed inputs deny, every intent/commit crash cut/concurrent issuer, no extra grants after reopen |
| Source control | real multiprocess Unix sendmsg/recvmsg+flock, queued/partial FD delivery, duplicate/invalid ancillary rejection, both stop orderings, lock deadlines, lost COMMITTED, broker/evaluator death; harmless owned children, no mocks for linearization |
| Source projection | preclaim binding crash, unclaimed-leaf stop, stop transaction rollback, subordinate journal latch gap, replay/cross-index corruption, no permits on reopen, unchanged journal replay/schema |
| Source backend | temp v4 ro refusal/positive v5 reserve-meter-settle, full historical caps/holds, all denial cuts, two grants/two sends, real wait/reap/PID ownership, runner hang, bounded control, full frozen coverage/phases, no prepare writes, immutable outputs |
| Source regressions | both interpreters, full regressions/pvg verify, exact source hashes, independent architecture/security+PM acceptance; zero protected metadata instrumentation; none run in this design task |
| Live only | authorized root install/schema/registry, real UIDs/ACL/inode/FD behavior, current complete independent baseline, separately approved v5 carry-forward/activation/stop disposition, measured bounds/floors, real launchd broker-death guest teardown, approved full-corpus image/build, fresh VM observations, trusted accounting/export, all7 journeys/result/human reviews |
Fixture UID topology is explicitly nonproduction; synthetic installation/qualification
records NEVER satisfy live launcher containment. Positive source execution must really
launch harmless children via installed-equivalent backend protocol, not refusal stubs.
Budget proposal remains20–28 files/~5,000–8,000 changed LOC including2,000–3,000 tests;
q3hp6–8 files/~800–1,200 LOC afterward. Re-estimate after design acceptance, not license
to weaken tests or broaden ecosystem. No source implementation until this passes.
