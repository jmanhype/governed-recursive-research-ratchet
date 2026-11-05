# Proposed normative JIT leaf-planning amendment

AMENDMENT_RESULT: READY_FOR_INDEPENDENT_REVIEW

Base design954a8578ca9354c0af2d1d19a25bff3dcd2f41b2ef98e62e5667254230239c56
resolves the three earlier review findings. One newly demonstrated integration
problem remains: preparing all executable leaf Plans against one ledger anchor
makes the second leaf stale after the first leaf's normal claim/reservation.
The strict existing bind_observation must NOT be relaxed or fed a fake current
anchor. Source-only counterexample /tmp/grrr-campaign-freshness-probe-20261104.py
uses real public SQLite and accepted journal/binding helpers: initial plans pass,
first claim advances actual tip, second original plan raises StaleBinding; a new
second-leaf observation/plan with IDENTICAL static Request/Grant succeeds. No VM,
production issuance, real UID320 or live accounting is demonstrated.

## Keep static approval separate from dynamic trusted observations
- Human AuthorizationV1 still binds exact CampaignSpecV1, finite leaves, total
  maxima, installation, baseline endorsement, window and review. No extra leaves,
  grants, attempts, scope, code/assets, resource maxima or authorization may change.
- GrantBundleV1 and each existing v1 Grant/Request/Invocation remain unchanged.
- Existing leaf Plan, Start, operation_id and strict nonce/epoch/age/anchor checks
  remain UNCHANGED. No permitted-delta freshness exception or portable receipt key.
- Replace ONLY the unimplemented root CampaignPlanV1 with CampaignPlanV2:
  {schema:"capstone-campaign-plan-v2",campaign_spec_raw:raw,grant_bundle_raw:raw,
   decision_json_raw:raw,decision_markdown_raw:raw,authorization_bytes_sha256:H,
   initial_anchor:Anchor,initial_observations:[{leaf_id:H,observation:Receipt}],
   gates:Gates,campaign_plan_sha256:H}.
  Selfhash omits only campaign_plan_sha256. Initial observations cover exact spec
  order/set, same initial_anchor, compatible service epoch and approved age/window;
  all original raw bindings match their exact preissued grants. They are inert
  readiness evidence, NOT executable leaf Plans or portable authority.
- Prepare remains read-only: no nonce registration, grant/run consumption, DDL,
  VM or protected write. Unavailable observation produces FailureRecord, no fake Plan.
- Run first revalidates exact static intent, live source/current baseline/allowance,
  first-step anchor and action-appropriate gates; server derives authority/gates
  from protected issuance and fresh live state, never from caller's gate booleans.
  Expired/stale initial readiness before beginning requires a new prepare.

## One trusted campaign owner, one bounded start
Installed service adds these exact request records (no new CLI commands):
- {action:"start-campaign",version:2,plan:CampaignPlanV2,campaign_operation_id:H}
- {action:"status",version:2,campaign_operation_id:H,nonce:H}
- {action:"stop",version:2,campaign_id:I,key:I}; may stop issued/unstarted campaign.
Campaign operation ID=D("campaign-operation-v2",{campaign_id,campaign_plan_sha256}).
Control requests retain action names status/stop, so legacy channel separation
still applies; new installed decoder is strict and separate from legacy v1 client.
Root start record must fit MAX_WIRE; local16MiB allowance is NOT permission to send
an oversized request. Refuse, do not silently partition/truncate/reduce coverage.

Add explicitly versioned backend index-v2 table backend_v2_campaign_run (other
base tables migrate their backend_v1_ prefix to backend_v2_ in this UNINSTALLED
successor specification, not any live database): campaign_id PK/FK campaign,
campaign_operation_id UNIQUE,plan_hash UNIQUE,plan_raw BLOB,auth_hash,owner_epoch,
state:running|completed|stopped|recovery-required,active_leaf ?INTEGER,
result_object ?H,intent_anchor. Identity columns immutable; only legal monotonic
progress/result updates, delete denied; exact schema and durable replay as base.
Campaign-start event atomically inserts it, derives intent_anchor from receipt
without a self-hash cycle. Original journal v1 namespace/schema is unchanged.
- One current owner-epoch/process may schedule it; server returns promptly with
  recorded status. Guest waits run outside control/ledger locks.
- Same root start returns status ONLY, never starts/continues another worker;
  changed root plan for that campaign fails StaleBinding. A restarted evaluator
  with unfinished campaign run fences all work/retains holds; no automatic resume.
- At most ONE active campaign; other campaigns are refused BEFORE claim/reserve.
  Qualified writer exclusion forbids unrelated operational writers; campaign
  total maxima and measured overhead bounds are checked before each new leaf.
- The trusted campaign worker builds each leaf Plan JUST IN TIME after earlier
  leaf completion/settlement, using its fresh internal observation and original
  exact Request/Grant/auth/static pins. It passes the unchanged strict v1 checks
  before claim. Known own claim/reserve transitions afterward are validated as
  intended state changes, not used to weaken another leaf's freshness check.
- Freeze/persist the actual leaf Plan bytes and deterministic operation ID BEFORE
  its first effectful request. One leaf grant/operation/permit per actual send.
- Public installed wire must not accept arbitrary v1 leaf Start to bypass this
  sequencer. Existing legacy refusal/test APIs remain intact; internal typed leaf
  execution requires the live campaign owner context, never a payload role/flag.
- Any uncertain leaf stops scheduling remaining leaves. Lost reply queries the
  known campaign/leaf operation, never re-observes/re-prepares that possibly
  consumed leaf or invents a new key. Stop remains authoritative at campaign level.

## Status, immutable evidence and final root manifest
CampaignStatusV2={schema:"capstone-campaign-status-v2",campaign_operation_id:H,
campaign_id:I,campaign_plan_sha256:H,state:running|completed|stopped|recovery-required,
active_leaf:?H,leaves:[{leaf_id:H,operation:?Operation,actual_plan_sha256:?H}],
gates:Gates,verification:blocked|verified,admission:blocked,promotion:disabled,
result_object:?H,failures:[FailureRecordV1]}.
Unclaimed leaves have null Operation/plan hash; never fabricate an Operation.
Stop of an unstarted campaign returns existing typed StopReceipt, not fake status.
All states/projections derive validated durable events plus live owner/control
state; source fixtures never imply production evidence. Separate execution state,
verification and human decision remain visible; completion alone is not verified.
CampaignManifestV2={schema:"capstone-campaign-manifest-v2",campaign_plan_sha256:H,
leaves:[{leaf_id:H,actual_plan_raw:?raw,manifest:?Manifest,failure:?FailureRecordV1}],
gates:Gates,execution:completed|partial|not-run|unknown,verification:blocked|verified,
admission:blocked,promotion:disabled,failures:[FailureRecordV1]}.
A non-null manifest requires actual_plan_raw; null manifest requires a non-null
failure, never a fictitious Manifest for an unstarted leaf. Every actual Plan raw
hash matches its leaf Manifest's plan_sha256 and unchanged static spec/grant
bindings; root hash stays the original CampaignPlanV2 hash. Initial readiness is
never substituted for actual execution.

Required tests: real accepted-source two-leaf anchor counterexample; JIT two-leaf
success without changing static approval; stale initial plan rejection; exact
static mismatch denial; duplicate root start status-only; crash before/after root
start and leaf-plan persistence; no resume/reprepare after unknown; stop-before-
unclaimed leaf; no direct wire leaf start; max-wire refusal without coverage loss;
manifest links actual dynamic plans and all mandatory gates truthfully. All other
base design guards, v4 read-only/v5 activation exclusions and live-only proof stand.
