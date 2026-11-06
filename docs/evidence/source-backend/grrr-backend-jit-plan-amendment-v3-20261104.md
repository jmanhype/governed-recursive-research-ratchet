# JIT campaign amendment v3 — exact delta contract (2026-11-04)
AMENDMENT_RESULT: READY_FOR_INDEPENDENT_REVIEW
Design only: no implementation, acceptance, installation or execution authority.
Base SHA256 `954a8578ca9354c0af2d1d19a25bff3dcd2f41b2ef98e62e5667254230239c56`;
JIT amendment `3f2c661bf93b8513440f3a31daed2f3d2f37cd312137c3181304195402ebb488`;
review `ae447e94efdbfcbf7480f0e7756734d1f202eeab9425adeb48a8bc8e603b76c5`.
This delta supersedes conflicting JIT run/status/manifest rules ONLY; otherwise both
inputs stand. Resolves the three NEW findings, not a re-review of resolved base work.
HEAD verified `2b601462ba0ffb5aee6239aa22b06c26801dfaf9`; docs/findings absent.
Bounded source fallback: capstone_contract.py observation/Plan/hash definitions and
capstone_journal.py claim/pending. Graph unavailable; no exhaustive claim. Public
freshness probe read, not rerun here. No repo/tracker/protected-path/network changes.
InstallationV1.schema is literal `capstone-installation-v1`; only fields OTHER THAN
schema and operator_uid are H. The local 16MiB limit does not override MAX_WIRE:
some valid approved bundles are unstartable; refuse without partial coverage.

## 1. Exact durable run reducer (finding 1)
Use the proposed, uninstalled backend-v2 namespace; journal v1 is unchanged.
Replace run row with exact columns:
backend_v2_campaign_run(campaign_id PK/FK campaign, campaign_operation_id UNIQUE,
plan_hash UNIQUE, plan_raw BLOB, auth_hash, owner_epoch H, state, active_leaf ?INTEGER,
result_object ?H, intent_anchor H, revision N, last_event H).
state=running|completed|stop-pending|stopped|recovery-required. Identity columns
through owner_epoch and intent_anchor immutable. revision starts 0, increases by 1
on each update; last_event is that update receipt.digest. No delete; only reducer
updates. No other columns, indices beyond declared constraints, or owner reassignment.
owner_epoch is fresh evaluator boot nonce, never loaded/reused as a scheduling token.
The in-memory owner capability is minted ONLY by the invocation committing start;
it is neither reconstructed from rows nor returned to caller. Duplicate/concurrent
start returns status only. Worker exit/loss destroys capability; cannot restart it
even in the same process. Restart with unfinished run fences service immediately;
append campaign-fence when possible, never resume. Read-only status overlays this
fence if persistence fails, reports RecoveryRequired, and never claims durable update.

Add exact envelope {format:"capstone-campaign-event-v2",version:2,action,record,
idempotency_key}; Ledger supplies version/idempotency_key as in base. action allowlist:
campaign-start, campaign-select, campaign-leaf-bind, campaign-advance,
campaign-finish, campaign-fence, campaign-stop-outcome. record has EXACT fields
{campaign_id:I,previous_revision:?N,run:<complete new row>,binding:?<base binding row>,
leaf_plan:?<row in section 2>,evidence:[H]}. Every nullable field must be present.
Run row omits last_event, plus intent_anchor ONLY for start; binding omits bind_anchor
ONLY for leaf-bind. Reducer fills these from current receipt.digest after hashing.
All other row fields required; BLOB raw encoding and base canonical rules apply.
Evidence hashes sorted unique, resolving durable typed objects before append.
Key=D("campaign-event-v2",{campaign_id,action,revision:run.revision}); no append on
cached retry: validate stored event and return status. Mismatched retry fails.
New envelopes coexist with base backend-event-v1 actions targeting backend_v2_ tables;
base bind is forbidden for campaign leaves: campaign-leaf-bind is its atomic replacement.

Reducer transition table (all rows require validated full static joins):
* start: previous_revision=null, no prior run; issued/unstopped campaign, no other
  running/stop-pending/recovery-required campaign, fresh root readiness and all base
  gates. Insert running/active_leaf=null/result_object=null/revision=0; binding and
  leaf_plan null. Exact original plan/auth/root operation IDs verified; evidence is
  exactly the source/static review hashes resolved from approved policy/review_anchor.
* select: running/null -> running/i, result stays null; i is FIRST unfinished leaf
  in spec order, all earlier leaves completed with verified cessation/integrity and
  committed settlement (finding verification may remain blocked); predecessor met.
  No existing leaf_plan for i. Evidence contains prior completion refs (empty at i=0).
* leaf-bind: running/i -> same running/i; atomically insert EXACT base binding and
  section 2 leaf_plan, no prior binding/plan/grant consumption; evidence=[review_hash].
  Owner/gate/window/live-anchor checks below required; never replace either row.
* advance: running/i -> running/null; exact valid claimed Operation and leaf result
  prove normal exit/cessation/integrity/meter/settlement; evidence=[leaf result hash].
* finish: running/null -> completed/null; every leaf has advanced once; evidence
  contains exactly the final manifest hash; set result_object to that hash.
* fence: running|stop-pending -> recovery-required, preserve active_leaf; evidence
  is exactly FailureRecord, FenceSnapshotV2 and final manifest hashes; result_object
  becomes that manifest hash. No work resumes.
* stop-outcome: stop-pending -> stopped iff base StopOutcome verifies ALL intents
  and baseline; otherwise -> recovery-required. Clear active_leaf only for stopped;
  set result_object=final manifest hash. evidence exactly StopOutcome and manifest.
Except leaf-bind, binding/leaf_plan null. Except finish/fence/stop-outcome, result
stays null. Other mutations, backwards steps, missing/extra rows/evidence are invalid.
Events select/bind/advance/finish require the original live capability; fence and
stop handling require authenticated controller, not a resurrected worker capability.
FenceSnapshotV2={schema:"capstone-campaign-fence-v2",campaign_operation_id:H,
owner_epoch:H,observed_owner:present|absent,active_leaf:?N,cut:owner-lost|binding-gap|
claim-gap|accounting-gap|dispatch-unknown|evidence-failure,anchor:Anchor,evidence:[H]}.
Its evidence is sorted unique, includes every available binding/journal/accounting/
launch diagnostic object for the failed cut, and never asserts absent evidence as safe.

Extend base safe-stop.backend_stop to literal schema `capstone-campaign-stop-v2`,
same base fields plus run_before_revision:?N and run_after:?<complete run row>.
These are null iff no run exists. First stop commits base campaign/control changes
AND run running -> stop-pending in the SAME SQL-only hook; active_leaf preserved,
result null, revision+1; run_after omits last_event supplied by stop receipt. No IO.
Completed/stopped/recovery-required run is unchanged (run_after is exact existing
row, including last_event); new-key repeat stop likewise leaves run unchanged.
Stop is still authoritative for every finite leaf, including unplanned/unclaimed.
Unstarted stop returns typed StopReceipt, no fabricated run. Durable ACK means
stop-pending, not cessation. Cancel outside locks; unresolved outcome requires recovery.
If stopped/completed evidence later fails validation, status fails closed with
RecoveryRequired; no transition back to running or reinterpretation as valid completion.

Replay folds ledger in sequence from empty backend state: validate envelope/receipt,
prior revision, transition preconditions, object hashes, base control/journal/accounting
joins at that event prefix; compute rows, never accept supplied rows as truth. Recompute
each advance's completed-prefix from events (no hidden mutable cursor). At end compare
ALL columns/rows/BLOB bytes of run/binding/leaf_plan and all base tables with reducer
output; exact cardinality, no missing/extra rows. Receipt-derived fields must equal
their particular receipt. Future evidence cannot justify an earlier send. SQL guards
mirror transitions; replay remains mandatory. A journal claim without preceding
leaf-bind, or launch without review/owner/control joins, is invalid, not repaired.
Late leaf projection/stop diagnostics may append truthful evidence after terminal
run state but cannot replace result_object, restart owner, or mutate frozen manifest.

## 2. Actual bytes and preclaim provenance (finding 2)
New immutable table backend_v2_leaf_plan(campaign_id FK campaign_run, leaf_index N,
operation_id UNIQUE FK binding, plan_hash H, plan_bytes_sha256 H, plan_raw BLOB,
review_hash H, PRIMARY KEY(campaign_id,leaf_index)); no update/delete, no other indices.
Inserted with binding at leaf-bind; original Start in binding decodes to EXACT plan_raw
canonical Plan bytes; operation_id uses UNCHANGED v1 plan_sha256 and grant_id.
plan_hash = Plan.plan_sha256 (existing selfhash omitting its selfhash field);
plan_bytes_sha256 = SHA256(plan_raw bytes INCLUDING plan_sha256). They are NOT equal
by definition. Actual raw bytes, review and prerequisite objects fsynced before event.
Crash before event leaves unreferenced inert objects, not authority or a new attempt;
crash after event retains immutable binding/Plan even when no journal claim exists.
No discard/replan/rebind after this commit; even known no-send cut fences the campaign.
Before commit a stale prospective Plan can be discarded without consuming a leaf;
after abandonment/restart the run still cannot resume. Never turn an object into a
claim, Operation, reservation, permit or success.

Replace each CampaignStatusV2 leaf entry with EXACT
{leaf_id:H,preclaim:not-planned|binding-only|claimed,operation_id:?H,
actual_plan_sha256:?H,actual_plan_bytes_sha256:?H,review_sha256:?H,operation:?Operation}.
not-planned: all nullable fields null, no durable leaf_plan/binding.
binding-only: IDs/hashes nonnull from joined leaf_plan/binding; Operation null because
no valid journal claim. It is never called claimed/reserved. Active uninterrupted
bind->claim gap is pending preparation; after crash/abandonment it implies recovery.
claimed: same nonnull immutable provenance, plus valid full v1 Operation projected
from journal/base joins. Missing/corrupt claim joins are validation failure, not a
downgrade to not-planned. Stop does not erase any of these provenance states.
Root state enum includes stop-pending; active_leaf is leaf_id for row index or null.
Add root revision:N,last_event:H,live_owner:present|absent to status; live_owner is
authenticated observation only, never persisted authority. Base gate/failure rules hold.

Replace each CampaignManifestV2 leaf entry with EXACT
{leaf_id:H,preclaim:<same enum>,operation_id:?H,actual_plan_raw:?raw,
actual_plan_sha256:?H,actual_plan_bytes_sha256:?H,review_sha256:?H,
manifest:?Manifest,failure:?FailureRecordV1}. Null rules follow status. binding-only
retains raw/hash/review/ID and null Manifest plus concrete FailureRecord. not-planned
has null provenance/Manifest and concrete failure. claimed requires actual raw;
when leaf Manifest unavailable, explicit failure records the unknown, not fake data.
Non-null Manifest links its plan_sha256 to embedded selfhash, its operation_id to
v1 derived ID, and SHA256(decoded raw) to bytes hash. Root original plan, static spec,
grant bytes, finite leaf order/cardinality and auth all join exactly; no omitted leaves.
Terminal result is SHA256(C(CampaignManifestV2)); never include its own digest inside
that manifest. Status can report later evidence/failures without rewriting the object.

## 3. Independent phase-tagged actual-Plan review (finding 3)
Static review/approval must explicitly approve the deterministic JIT review procedure
and verifier identity/inventory under existing pinned policy and review_anchor. It
approves finite intent, NOT unknown future Plan bytes. Missing procedure approval
blocks source/live execution; no fresh per-leaf human authorization is invented.
The independent reviewer is a separate trusted principal from campaign owner/worker,
with an authenticated local interface and own append-only, durable review object store.
Evaluator may read, never write/impersonate that principal's accepted records. Policy
pins allowed reviewer identity, verifier inventory and checks; source fixtures cannot
qualify live provenance. It may be an independently reviewed deterministic verifier,
not an owner-generated boolean or repeated human grant. Actual reviewer time is metered
within approved bounds. Failure/timeout/stale review blocks send, never bypasses review.

Exact ReviewV2 object (canonical bytes, no selfhash):
{schema:"capstone-jit-review-v2",phase:actual-plan-prelaunch,verdict:pass|fail,
reviewer_identity:H,verifier_inventory:H,policy_sha256:H,source_review_sha256:H,
static_review_sha256:H,authorization_bytes_sha256:H,campaign_spec_sha256:H,
campaign_plan_sha256:H,leaf_id:H,grant_bytes_sha256:H,operation_id:H,
actual_plan_sha256:H,actual_plan_bytes_sha256:H,observation_sha256:H,
service_epoch:H,anchor:Anchor,reviewed_ns:N,expires_ns:N,evidence:[H],blockers:Codes}.
Review hash is SHA256(object bytes). Independently authenticated retrieval must return
these same original bytes; hash possession alone is not reviewer identity. Evidence
sorted unique resolves source/static reviews and all required prelaunch gate evidence;
pass requires empty blockers. Reviewer recomputes both hashes/operation and checks
EXACT immutable leaf/Request/Invocation/Grant/auth/window/maxima/pins, genuine retained
observation, phase gates and approved JIT algorithm. Reject readiness or result-phase
objects presented as actual-plan-prelaunch. Review expires no later than auth/grant
expiry and observation observed_ns+receipt_max_age_ns; no extended freshness window.

Construction order avoids self-reference and an artificial ledger freshness failure:
select -> fresh authenticated observation -> freeze strict v1 Plan -> independent
review/store -> final prebind strict bind_observation against CURRENT live anchor,
retained nonce/service_epoch/clock/UID -> atomic leaf-bind -> unchanged journal claim.
Review storage/object writes do not advance ledger/accounting/registry snapshots.
Plan.gates holds only evidence available BEFORE freeze (static/phase prerequisite
reviews, postrun not-run); never inject actual review hash into its own reviewed Plan.
The separately stored review is joined by leaf_plan.review_hash and drives authoritative
Operation reviewer_outcome evidence; action_specific_human_approval continues to refer
to ORIGINAL AuthorizationV1 via static review, not ReviewV2 as a substitute grant.
Retain base gate->ledger lock order/writer exclusion across final check/bind/claim;
no ledger lock during independent review. Recheck stop/window/review expiry before
claim/send. Only exact recorded own bind/claim/reserve transitions may follow the
validated prebind anchor; no second bind_observation with a fabricated current anchor,
no tolerance delta and no unrelated write permitted. Fresh observation for next leaf
includes ALL preceding durable events; initial readiness never substitutes for it.
Lost capability or uncertain send remains query-only; no repeated Plan/permit/send.

## 4. Required source acceptance deltas (not tests performed here)
Integrated real temp backend tests must cover every event rollback/crash boundary,
full-row tamper/replay equality, revision/action/extra-row denial, both stop orderings,
stop-pending before cancellation, failed cancellation, duplicate root status-only,
same-process worker death and evaluator restart with NO owner reuse/new scheduling.
Exercise select->review->bind->claim cuts: retained binding-only bytes/ID/review with
null Operation, unplanned stop, raw-hash versus selfhash linkage, immutable manifests.
Independent review store/identity substitution, wrong phase/leaf/bytes/source/static
approval, missing evidence and expired review MUST deny before claim/first send;
an intervening unrelated anchor change must fail unchanged bind_observation.
Positive two-leaf JIT path must use real accepted journal/accounting/backend protocol,
distinct dynamic Plans and independent review records, same finite human approval,
one permit/send each, real harmless children and truthful final joined manifests.
Preserve complete base source/live matrix, all11 phase gates, no public leaf bypass,
q3hp independent mapping acceptance, v4 read-only/v5 activation exclusions. Source
proof is not live qualification; no admission, promotion, recovery or unstop authority.
