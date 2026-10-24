# Governed Recursive Research Ratchet — Architecture

## Status and authority

Approved minimal executable architecture, with implementation in progress.
The trust boundaries below remain authoritative. This document itself grants no
additional experiment, provisioning, paid-service, replay, promotion, or merge
authority; exact authority and runtime proof remain bound to reviewed operator
records, story evidence, and protected receipts.

Inputs: accepted BUSINESS.md and DESIGN.md, operator architecture answers, and
dispatcher-reported source metadata dated 2026-10-19. Authoritative source:
https://github.com/paivot-ai/vlt at proposed pinned main commit
`129e0b3f15a3bd6af949ee47d76f6855c582ab73`. Relevant source surfaces are
`index.go`, `vault.go`, `wikilinks.go`, `frontmatter.go`, `inert.go` and tests.
Exact source bytes, build behavior, specifications and dependency closure require
preflight verification. The reported Apache-2.0 license blob is
`c004659349c7a1f6c55e5107b53a0766085e8d2e`; this is not dependency clearance.

## Architecture decisions and alternatives

1. A separate research runner integrates with PAIVOT without changing pvg core.
   Existing governance remains authoritative; a new orchestration platform would
   duplicate it. DESIGN.md's `pvg research ...` commands remain interface
   concepts, not installed commands. The approved implementation surface is the
   separate `bin/grrr` executable recorded in
   `docs/IMPLEMENTATION-APPROVAL-2026-10-20.md`; it does not modify pvg core.
2. Execute untrusted candidates in a dedicated local VM, with evaluator authority
   outside it under a restricted host identity. Worktrees and a second account
   alone cannot enforce this boundary. A container alternative needs separately
   approved, measured equivalent isolation; unavailable VM capability means stop,
   not an automatic container or unrestricted-host fallback.
3. Use an evaluator-owned local transactional event store with hash-linked events
   and immutable content-addressed evidence objects. A local hash chain detects
   alteration relative to trusted receipts; it does not defeat a privileged host
   administrator or guarantee survival of host destruction. A remote service is
   unnecessary for the POC and presently unavailable.
4. Evaluate frozen seeded variants and selector strategies, not generated patches.
   This isolates selection value and proves the verification ratchet before
   implementation or harness optimization expands scope.
5. Keep Jev optional and outside correctness authority. A deterministic selector
   is retained if Jev does not meet the business threshold. Extra Sean tools,
   Bend 2, ggen, wasm4pm and dteam are not architecture prerequisites.

## Components, ownership and current existence

| Component | Architecture / implementation state | Responsibility / forbidden authority |
|---|---|---|
| pvg / nd / vlt | Active governance and target stack | pvg governs workflow and authorizations; nd tracks references; vlt is the accepted frozen target/corpus domain. None implements `pvg research` commands |
| Operator / PM-Acceptor / adversarial reviewer | Existing roles | Human approves exact targets; reviewers inspect independent evidence, cannot substitute for execution isolation |
| Research runner | Approved separate `bin/grrr` executable; bounded lifecycle path implemented | Schedules bounded arms and translates lifecycle into CLI/report state; cannot certify defects, change policy, or write ledger directly |
| Selector adapters | Architecture retained; three-arm comparison not run | Random, deterministic risk-based, optional Jev return ranked public challenge IDs; no protected-fixture or verdict authority |
| Candidate executor | Isolated vlt corpus/trusted-observation execution proven; fresh independent replay not run | Runs pinned vlt variants in disposable offline VM instances; treats all output as untrusted |
| Trusted evaluator service | Protected policy/corpus/accounting/replay prerequisites progressively implemented | Owns policy, protected corpus, gate registry, measurements, replay, evidence store and ledger writes; never runs candidate code in its host process |
| Persistent accounting | Registration-only `independent-replay` profile installed and verified; store remains stopped and execution-unauthorized | Preserves cumulative usage, uncertain holds, history and stop state; cannot create a fresh allowance or release itself |
| Admission controller | Open operator-gated milestone capability | Validates exact approval and gate evidence, authorizes protected contract updates; has no main-merge or production capability |
| Jev broker | Optional future adapter; not started | Operator-controlled sanitized requests, authorization and spend receipts; not reachable by candidate |
| Export / report adapter | Partial projections implemented; accessible-surface capstone remains open | Read-only verified snapshots to Markdown/plain text/JSON and optional backups; no authority from report text |

### Implementation checkpoint

Accepted prerequisite work includes the bounded trusted-path challenge, unsafe
baseline blocking, forged-observation rejection, evidence recovery, independent
trusted stop, frozen isolated vlt corpus validation, replay runtime prerequisites,
and registration-only independent-replay accounting. GRRR-43i8 is accepted but
its story branch is not merged until separately authorized.

The next open capability is GRRR-z3w9: verify a defect from fresh trusted
inputs. Selector comparison, contract admission, report-surface parity, and the
operator end-to-end capstone remain downstream. No actual independent replay,
Jev-guided run, Harness²-style adaptation, contract admission, promotion, or
production mutation is claimed. Sean Chatman's Anti-Cheat Scorecard remains an
optional evaluator-side audit adapter to be evaluated first among his candidate
tools; it is not a trusted runtime prerequisite.

These are trust/responsibility boundaries, not a requirement for eight services.
A small runner and restricted evaluator service may house the logical modules.
Protected admission must be a distinct authorized operation even when implemented
inside the evaluator service. No model output is executable evaluator policy.

## Execution and permission boundaries

Run on the existing macOS host only after verified isolation. Use a dedicated
checkout/workspace, never active `/openjutsu-studio` or `/wangp-dspy` workspaces.
Provisioning and identity setup require explicit operator authorization.

| Principal | May read | May write | Must not possess |
|---|---|---|---|
| Selector / optimizer | Public synthetic descriptions and approved training feedback | Bounded proposals | Holdouts, hidden seed truth, protected specs/policy, evaluator implementation, admission capability |
| Candidate VM | Pinned executable/source as required and single delivered synthetic test input | Disposable guest workspace/output | Network, host home, credentials, production data, host/shared writable mounts, evaluator corpus/keys |
| Runner | Public manifest and validated receipt/status API | Scheduling state in its own workspace | Direct ledger/protected-policy writes, production or main-merge authority |
| Evaluator identity | Protected corpus/specs/policy and trusted artifacts | Ledger, evidence objects and admission-gated contract store | General operator credentials or production writes |
| Operator | Review packets and policy | Explicit authorization records through trusted endpoint | Implicit blanket approval from a completed run |

Candidate-visible test inputs are necessarily observable to that invocation;
denying protected fixtures means denying corpus access, expected outputs, hidden
labels and future/holdout inputs, not pretending the invoked input is invisible.
No input is reused across trust domains with writable shared storage. Start each
invocation/reproduction from a clean image or equivalent verified reset. Disable
guest networking, host-home sharing, clipboard/integration channels and forwarded
agents; verify actual routes/mounts/devices rather than configuration intent.
Read-only mounted host directories are not automatically acceptable: copy only
approved artifacts through a narrow transfer boundary.

Protected evaluation harnesses cannot be trusted merely because located in a VM
where candidate code can rewrite them. The evaluator retains assertions and
expected results outside candidate control, observes bounded outputs/state through
a trusted transport, and executes all candidate code only inside isolation.
Race/locking tests may require an in-guest supervisor isolated from candidate UID;
its build and permissions are part of preflight. If a trustworthy observation
path for a required test cannot be established, that mandatory gate is not run and
blocks execution acceptance. VM escape and host-admin compromise remain residual
risks; this POC is not a certification against them.

## Explicit interfaces and data flow

All interfaces use versioned, size-bounded structured records; reject unknown
actions, malformed identifiers, traversal paths, unexpected executable payloads,
oversized outputs, symlinks and missing required fields. Transport identity and
filesystem permissions bind the caller; a caller-supplied role string is not auth.

1. **Operator → governance/runner:** signed-in local human authorization records
   bind scope, source revision, policy/corpus/evaluator digests, budget ceilings
   and expiry/run identity. Provisioning, paid Jev use and each admission remain
   separate actions. Exact local authentication mechanism is implementation
   preflight, not an assumed pvg feature.
2. **Runner → selector:** approved public challenge catalog and remaining arm
   budget. Selector returns challenge IDs, ranking and provenance. No shell
   command field. Invalid/duplicate IDs are rejected deterministically.
3. **Runner → evaluator:** run ID, arm, challenge ID, pinned variant digest,
   idempotency key and reservation request. Evaluator resolves protected inputs
   itself; runner cannot supply an expected result or bypass mandatory gates.
4. **Evaluator → isolated executor:** allowlisted invocation descriptor, approved
   inputs, resource limits and clean-image identity. No arbitrary host commands.
5. **Executor → evaluator:** bounded raw observation, exit/signal, resource use
   and transport completion. Candidate logs are allegations, never trusted test
   verdicts. Output decoding cannot execute candidate instructions on the host.
6. **Evaluator → ledger/report:** verified measurements, gate outcomes, finding
   classification and object digests. Report generation reads a consistent
   receipt; plain text, JSON and Markdown share snapshot IDs and state dimensions.
7. **Reviewer/operator → admission:** exact receipt, contract diff digest, target,
   actor and decision. Recheck currency and all gates at commit time; reject
   replayed approvals and changed targets. Receipt records actual outcome, not
   merely authorization intent.
8. **Ledger → nd/export:** receipt ID and verified artifact location only; nd is
   not the experiment source of truth. Export supports a replaceable backup
   destination but no unconfirmed remote dependency.

Every interface needs an integration story and negative tests. Tool-version
capability discovery must precede wiring; do not invent pvg commands.

### Proposed module and public interface contracts

The following repository-relative paths and language-neutral signatures are
approval targets for a future dedicated runner repository, not existing files or
capabilities. Extensionless module paths deliberately leave language and VM
product undecided. `Result<T, Error>` is a tagged success/error union; no boolean
or empty result denotes success. IDs and digests are validated opaque types;
`Principal` is transport-authenticated, never trusted from request payloads.
`Error` contains a stable code, run/operation ID, retryability and optional durable
receipt ID. Codes include `Unauthorized`, `InvalidInput`, `StaleBinding`,
`GateBlocked`, `BudgetUnknown`, `BudgetExceeded`, `Stopped`, `IntegrityFailure`,
`Unavailable` and `RecoveryRequired`; unknown errors fail closed. Timeout means
unknown outcome until queried by operation ID, not permission to duplicate effects.

| Proposed path | Public signature → typed success | Principal / permission |
|---|---|---|
| `research/policy` | `loadPolicy(principal: Principal, ref: PolicyDigest) → Result<VerifiedPolicy, Error>` | Evaluator reads protected immutable policies; runner receives only redacted approved scope; optimizer cannot change policy |
| `research/authorization` | `validateAuthorization(principal: Principal, request: ActionBinding, approval: ApprovalRef) → Result<AuthorizationGrant, Error>` | Trusted evaluator/admission code validates human identity, exact action/target/digests/expiry and consumption state; callers cannot mint grants |
| `research/budget` | `reserve(principal: Principal, run: RunId, maximum: ResourceVector, key: IdempotencyKey) → Result<Reservation, Error>`; `settle(principal: Principal, reservation: ReservationId, actual: VerifiedUsage) → Result<SettlementReceipt, Error>` | Evaluator owns balances; runner requests reservations; only trusted metering settles; uncertain usage retains reservation |
| `research/execution` | `dispatch(principal: Principal, request: ApprovedInvocation, reservation: ReservationId, fence: RunEpoch, key: IdempotencyKey) → Result<DispatchReceipt, Error>` | Evaluator dispatches allowlisted guest work through narrow executor adapter; runner may request but cannot bypass policy, reservation or fence |
| `research/control` | `stop(principal: Principal, run: RunId, key: IdempotencyKey, reason: Optional<Text>) → Result<StopReceipt, Error>`; `stopStatus(principal: Principal, operation: OperationId) → Result<StopOutcome, Error>` | Authenticated operator uses evaluator-owned control endpoint directly, independent of runner; evaluator watchdog has bounded safety-stop authority |
| `research/ledger` | `append(principal: Principal, event: ValidatedEvent, expectedTip: Digest, key: IdempotencyKey) → Result<EventReceipt, Error>`; `verifySnapshot(snapshot: SnapshotRef, trustedAnchor: ReceiptDigest) → Result<VerifiedSnapshot, Error>` | Evaluator-only append; operator/reviewer/export verifier may read immutable snapshots; conflict rejects rather than overwrites |
| `research/replay` | `reproduce(principal: Principal, allegation: AllegationRef, policy: PolicyDigest, reservation: ReservationId) → Result<ReplayReceipt, Error>` | Evaluator reconstructs trusted inputs in fresh isolation; runner/claimant can request but cannot assert verdict or provide trusted expected results |
| `research/admission` | `admit(principal: Principal, proposal: ContractDigest, snapshot: VerifiedSnapshotRef, grant: AuthorizationGrant, fence: RunEpoch, key: IdempotencyKey) → Result<AdmissionReceipt, Error>` | Admission controller alone updates protected registry after human approval; operator grants permission, optimizer/runner have no direct registry write |

`ResourceVector` explicitly types money/currency, cumulative execution duration
and review duration, including unknown states. `ActionBinding` names authorization
type, target digest, run and policy/evidence versions. Receipts name exact effects
and durable state. `ReplayReceipt` contains a finding enum and individual gate
results, not an implied admission. `AdmissionReceipt` distinguishes committed,
blocked and recovery-required outcomes. `StopReceipt` acknowledges a durable stop
intent/fence only; `StopOutcome` distinguishes cancellation pending, stopped with
verified checks, and recovery required. These typed non-success domain outcomes
remain visible even when a request was successfully recorded.

### Independent trusted stop and cancellation path

The operator connects directly to the evaluator-owned local control endpoint,
without the runner process, its event loop or its credentials. Authenticate using
the approved local OS identity/peer-credential mechanism and an explicit operator
allowlist; enforce endpoint filesystem permissions. Exact transport is a
preflight choice. A guest, selector or unprivileged runner cannot impersonate the
operator. The watchdog can issue safety stops but cannot admit contracts. An
urgent stop needs no lengthy reason; the reason may be appended later.

For each run the evaluator owns a durable control state and monotonically
increasing fence epoch. In one serialized transaction, stop appends the request,
sets stopping state and increments the epoch. Return a durable acknowledgement
only after commit; include operation ID, epoch, receipt and cancellation status.
Repeated requests with the same key return the original receipt; new keys on an
already stopped/stopping run append or reference the existing stop without
restarting work or claiming a second cancellation. If durable recording fails,
return no durable acknowledgement, trigger best-effort safety cancellation, and
report recovery required. The service must reject further work until integrity
and control state are restored.

Dispatch and admission serialize their final authority checks against this same
run control state. A reservation or earlier approval is not a dispatch lease.
The executor validates the current epoch immediately before starting a guest;
queued stale-epoch requests are rejected. Work already launched before the stop
transaction is active work to cancel, never invisible to the stop receipt. The
trusted executor reports every launched guest to evaluator-owned tracking so
runner failure cannot orphan it from cancellation.

The admission commit linearization point is the durable protected-registry commit
record, serialized with stop. Contract objects may be staged beforehand but are
not admitted until that record commits. If stop commits first, admission is
blocked even with an earlier approval or staged object. If admission commits
first, the stop outcome explicitly lists the already-admitted contract/receipt;
stop prevents further admissions but does not undo that admission or claim a
rollback. Any later reversal requires its own human authorization. Crash recovery
uses durable intent/commit records to resolve ordering; ambiguous evidence remains
recovery-required and fences all new work.

After fencing, the evaluator control worker—not the runner—cancels all active
guests via the trusted VM adapter, escalates termination after the approved grace
bound, and verifies guest cessation and protected-baseline integrity. A hung
runner must not delay this worker. Numeric acknowledgement/cancellation/watchdog
bounds require measured preflight and operator approval before execution.
Until cessation and checks are verified report cancellation pending; failed
termination, unreachable executor or unknown state reports recovery required.
If the evaluator/control endpoint itself is unavailable, no success is asserted;
an approved host-level emergency VM-stop procedure must preserve evidence and
require recovery checks before resuming. This is not a guarantee against host loss.

Required negative tests: hang the runner while operator stop still records/fences
and cancels; repeat identical and distinct-key stop requests without duplicate
effects; race stop with queued and launching dispatches and verify no post-fence
start; race stop with staged and committing admissions and verify both legal
orderings and truthful committed-admission receipts; crash between acknowledgement,
cancellation and registry transitions; deny forged operator identities; simulate
unreachable executor and ensure pending/recovery is never labeled safely stopped.

## Ledger, evidence and recovery consistency

Use a transactional local store (SQLite is the proposed minimal option, subject
to runtime/dependency preflight), with one evaluator-owned writer and monotonic
event sequence. Logical updates append events; projections may be rebuilt.
Application deletion/update of historical events is forbidden. Filesystem access
denies the runner/guest direct mutation. Integrity links hash canonical event
bytes, prior event digest and referenced artifact digests. Define canonical
serialization and format version before producing receipts.

Each event binds: run/experiment/arm IDs, sequence and prior digest, event type,
actor, timestamps, candidate/base commit and built-artifact digest, evaluator and
VM/toolchain identities, policy/spec/corpus/input digests, selector version/seed,
mandatory gate inventory and individual results, measurements and units, costs
and reservations, findings/verdict, review/authorization target, object hashes,
and rollback/recovery outcome. Explicit unknown/not-run values never become zero
or pass. Record attempted and interrupted operations as well as successful ones.

Stage artifact objects, hash and durably publish them before transactionally
appending references. A crash may leave unreferenced staged objects, never a
passing receipt pointing to absent evidence. Recovery verifies chain and objects,
marks unresolved operations interrupted, conservatively retains spend
reservations, blocks promotion, and never silently retries non-idempotent actions.
Detect sequence gaps, truncated/modified records, missing objects and stale
snapshots. Admission and its event need one atomic or explicitly recoverable
protocol: write-ahead intent, immutable contract object, committed registry
version and outcome receipt; ambiguity remains recovery-required.

Evidence snapshots live outside disposable candidates and survive cleanup.
Read-only export includes manifest, chain tip, objects and verifier instructions;
an independent verifier checks integrity without trusting the report generator.
Backup/restore destination remains an operational choice; local exports satisfy
POC scope but do not promise disaster recovery.

## Evaluation, reproduction and protected admission

Allegation → independent fresh replay → authoritative-spec confirmation →
reviewed contract proposal → explicit human approval → protected admission →
demonstrated recurrence rejection. Evidence acceptance, contract admission and
software promotion are distinct authorization types; software promotion is
disabled in this POC, not implicitly granted by contract approval.

Independent replay starts from evaluator-controlled pinned source/build inputs
and fresh isolation. It must not consume candidate-created test harnesses, logs,
expected outputs or modified fixtures as trusted evidence. Rebuild when relevant;
record byte identities and environment differences. The challenger cannot
certify itself. A second physical host is not mandatory after isolation proof.

Authoritative behavior must be pinned to maintainer specification or explicitly
operator-approved requirement. Existing implementation behavior is not by itself
a specification. Ambiguity yields specification-review/inconclusive, not relaxed
criteria. PM-Acceptor and adversarial review support but do not replace human
approval of a contract. The contract proposal is inert data until reviewed;
new executable test code is reviewed for host-execution hazards before admission.
The admitted test must reject the faulty variant and pass the verified clean
baseline without changing the predeclared expected behavior.

The evaluator's mandatory gate registry includes source/environment identity,
isolation, protected-asset integrity, baseline correctness, trusted observation,
independent replay, specification traceability, evidence integrity/currency,
budget state, reviewer outcome and action-specific human approval. A gate is
pass/fail/not-run/error with evidence, never inferred from aggregate exit status.

## Corpus and equal-budget experiment design

Freeze and hash corpus, variants, hidden ground truth, critical classifications,
spec references and evaluation plan before running selection arms. Independent
corpus validation establishes each seed's observable failure and clean behavior.
At least 20 representative defect scenarios plus clean negatives must cover:

- Exact filename/title resolution; alias/collision precedence; case-insensitive
  and path-qualified lookup.
- Wikilinks, embeds, headings/block references and inert zones.
- Frontmatter updates/index invalidation; renames, moves, deletions/stale cache.
- Concurrent reads/writes/locking; filesystem errors and invalid paths.
- Deterministic repeated execution and integrity-registry tampering.

Map each category to source/spec references and identify critical cases before
measurement. Unsupported behavior is not fabricated as a known defect. Corpus
representativeness and ground-truth validation are independent review gates.
Selection sees only the same public metadata for all arms. Holdout truth, answers
and test outputs not approved for feedback remain protected; training/challenge
feedback and final evaluation partitions are explicit and contamination-checked.

Pre-register arm ordering, randomized seeds, repetitions (at least three where
feasible), tie-breaking, stopping rules, feedback allowance, deduplication and
accounting. Freeze deterministic heuristic and Jev configuration before runs.
Use identical eligible catalogs, resource ceilings and evaluation costs; include
selector overhead rather than giving Jev free inference. Shared setup cost and
arm-specific costs are disclosed separately with a predeclared amortization rule.
Report unique independently validated defects per arm, not repeated detections
as new defects. Faults detected by universal mandatory gates count separately
from selector discoveries, avoiding artificial selector credit.

The complete mandatory suite must detect 100% of designated critical seeds and
at least 90% of other seeds subject to corpus review. Report false positives,
false negatives, confidence intervals, variance, observed costs and sample limits.
Zero unverified claims and zero failed reproductions may be admitted. Claim Jev's
business target only at ≥20% validated defects/dollar over the strongest baseline;
do not infer statistical superiority from insufficient evidence. Zero-dollar or
unknown denominators make that metric undefined, not infinite: disclose this and
require an approved cost-accounting amendment before comparative acceptance.

Jev unavailability marks that arm unavailable; no heuristic is relabeled Jev.
The evaluator/verification demonstration may complete independently, but the
three-arm comparative POC remains incomplete. No autonomous patch generation,
recursive harness adaptation, main merge or production deployment is included.

## Offline operation, dependencies and licensing

Mandatory correctness, benchmarks, replay and admission gates operate offline.
Acquire pinned dependencies and image/toolchain artifacts through an authorized
preparation path; cache and verify them before disconnecting candidate execution.
Minimal standard-library/existing PAIVOT dependencies are preferred; reproducible
builds need documented inputs and repeat-build checks, not only a lockfile.

Inventory direct/transitive libraries, VM images, tools, models and reused test
assets with versions, hashes, origin, licenses/notices and required obligations.
MIT, Apache-2.0, BSD-2/3 and ISC are allowed subject to compliance verification.
GPL/AGPL/BSL, noncommercial, source-available or unclear licenses require separate
review. Public availability is not permission. Pinning does not establish
security; inspect dependency provenance and known risks before approval.

Jev's optional operator-controlled broker is the only proposed external inference
path. It accepts synthetic descriptions or explicitly approved sanitized metadata,
never proprietary source, raw logs, credentials or private holdouts. Use schema
allowlists, payload inspection, explicit authorization, provider-term review and
cost reservations. Candidate VM has no broker access. Credentials remain with
the broker and do not appear in evidence. Anti-Cheat Scorecard is only an optional
candidate after effectiveness, license and toolchain verification; applicable
Machinery obligations require capability/scope verification and separate explicit
enablement, not inferred availability or a new competing gate system.

## Budgets, observability, failure and rollback

Enforce POC ceilings $50 incremental spend, six cumulative experiment hours and
60 minutes operator review; milestone ceilings $150 including POC, 24 cumulative
hours and three review hours. Fourteen calendar days is a target, not a guarantee.
Define cumulative runtime as summed experiment execution time across arms and
replays, not elapsed wall time that hides concurrency. Report preparation and
review time separately. Track review sessions explicitly rather than assume zero.

Reserve worst-case bounded request cost/time before dispatch. Unknown maximum
cost blocks paid work; delayed receipts do not release reservations optimistically.
An independent evaluator-side deadline/watchdog stops work even if runner hangs.
No automatic budget increase. Ledger store exhaustion also stops new execution.

Hard-stop on exhausted budgets, unauthorized writes/attempts, isolation failure,
missing mandatory dependencies, evidence corruption, unrecoverable state or
protected-asset modification attempts. Proposed repeated-unreproducibility stop
threshold is two consecutive independent replay failures within a run; approve
this policy before execution. All failed attempts remain evidence, not discarded
outliers. Stop blocks scheduling and admission, terminates guest work with bounded
grace, preserves artifacts, and checks baseline/protected-store integrity.

Report execution, finding and decision separately using DESIGN.md vocabulary.
Expose run/snapshot ID, current phase, mandatory gates, reservations/spend/time,
blockers, fresh versus recorded evidence and safe next action. No color-only
meaning. Reports disclose cancellation pending and recovery required truthfully.

Rollback means a verified restoration, not a successful process exit. Candidates
are disposable and baseline is immutable; demonstrate baseline hashes and
behavior after stop. Preserve forensic evidence before candidate cleanup. An
approved contract is versioned: any later rollback is a new human-authorized
registry event pointing to the previous accepted set, never ledger deletion.
Persistent/external-state recovery requires separate authorization. Production
recovery is out of scope because production mutation is prohibited.

## Deployment/runtime preflight and unresolved risks

Before authorized experiments verify: macOS/virtualization support and resources;
dedicated VM lifecycle; separate identities/ACLs; absence of sharing/network/auth
leaks; trusted observation channel; dedicated source checkout and exact commit;
license/dependency inventory; offline builds; clean baseline; validated corpus;
ledger crash behavior; watchdog/resource limits; pvg integration capabilities;
Jev consent/accounting if used; and operator-approved policies/ACs.

These are verification tasks, not reasons to assume infrastructure already works.
Exact VM product, guest architecture, IPC transport, storage library and CLI syntax
remain implementation choices within these constraints and require approval if
they change trust, licenses, cost or permissions. Any missing capability fails
closed. Existing Podman host networking is not evidence of isolation.

Residual uncertainties: authoritative specs may be incomplete; 20 seeds may not
support broad claims; concurrency seeds may be nondeterministic; host-resource
contention may bias measurements; input/output parsing and VM escape remain attack
surfaces; local integrity is not privileged-attacker resistance; model pricing and
availability may prevent the Jev comparison. No remote backup is yet confirmed.

## Duplicate responsibilities deliberately avoided

- pvg owns governance; runner owns experiment scheduling, not a second backlog.
- nd owns work tracking; evaluator ledger owns experiment evidence, not vice versa.
- Evaluator owns correctness; Jev and scorecards can recommend, never grade or
  grant permission. Reviewers judge evidence without rewriting measured results.
- Existing mandatory gates and applicable Machinery obligations map into one
  registry; do not count duplicate checks as independent assurance.
- Hashes establish identity/integrity, not semantic correctness or human consent.
- CLI/reports are projections of receipts, not independent sources of verdicts.

## Architecture-to-Stories constraints

Do not create or execute stories until architecture and AC approval. Subsequent
stories must embed relevant trust constraints and proof, not merely link this doc.
Use atomic scopes with explicit wiring between: preflight/VM executor; evaluator
transport/observation; ledger/artifact recovery; corpus/spec validation; selectors
and budgets; independent replay; review/admission; report/state projections;
stop/rollback; and nd receipt references/export. Keep protected admission separate
from ordinary experiment execution. Each story specifies ownership, negative
tests, resource limits, evidence receipts and failure behavior. Delivery is not
acceptance; PM review and operator contract authorization remain distinct.

## Proposed testable architectural acceptance criteria

All criteria require captured commands/results, exact revisions and artifact
digests. They are proposed approval targets, not claims of passing tests.

1. **Isolation:** from candidate execution, attempts to access network, home,
   credentials, protected corpus/evaluator/specs, production paths and host writes
   fail; approved synthetic input/output still works. Misconfiguration blocks start.
2. **Identity/offline baseline:** exact pinned source/license and dependency
   manifest verify; offline repeat builds and independent clean-baseline checks
   produce recorded identities and results. Missing dependency blocks execution.
3. **Trusted observation:** forged candidate PASS logs, altered expected outputs,
   supervisor tampering and malformed transport cannot become passing verdicts;
   required race/locking observations are independently trustworthy or blocked.
4. **Ledger:** runner/guest writes are denied; mutation, missing objects, chain
   truncation relative to trusted receipt and interrupted transactions are detected.
   Crash-injection replay produces no false pass and preserves unresolved state.
5. **Replay/spec:** a valid seed reproduces in a clean environment from trusted
   inputs and pinned requirement; forged logs, failed replay and ambiguous specs
   cannot reach verified/admitted state.
6. **Admission:** human approval binds exact contract/snapshot/target. Wrong target,
   stale evidence, replayed approval, missing review or any nonpassing mandatory
   gate blocks admission. Demonstrate authorized admission and recurrence rejection
   while the clean baseline still passes.
7. **Corpus:** independently validate ≥20 representative defects plus negatives,
   category coverage and critical labels; full mandatory verification detects
   100% critical and ≥90% other seeds under the approved representative-set rule.
8. **Comparison:** same catalogs/budgets and frozen strategy definitions; ≥3
   randomized repetitions where feasible, with justified exceptions recorded.
   Costs include selection overhead; deduplication and uncertainty are visible.
   No unsupported superiority or substituted Jev arm is reported.
9. **Budget/stop:** forced exhausted/unknown reservations, runner hang, protected
   write attempts and dependency/evidence failure stop new work/admission within
   an approved measured cancellation bound; artifacts survive. Before execution,
   set numeric watchdog/grace limits from preflight capability, never leave unbounded.
    Prove direct authenticated control works with a hung runner, repeated stops
    are idempotent, and concurrent dispatch/admission obey the durable stop fence.
    A pre-stop committed admission remains explicitly committed, not rolled back.
10. **Recovery:** interrupt execution and admission at each durable transition;
    restoration is verified or explicitly recovery-required. Baseline remains
    intact; cleanup cannot remove evidence; external recovery requires new consent.
11. **Surface parity:** CLI/Markdown/JSON reference the same snapshot and distinguish
    execution, verification, decisions and effects. Stale/missing evidence blocks
    authority regardless of report wording; stop remains immediately accessible.
12. **Scope/security:** no capability for automatic main merge, production mutation,
    patch generation or harness adaptation. Dependency/metadata violations and
    unapproved paid calls fail closed. nd contains receipt references, not a rival
    evidence ledger. Verified isolation/replay/integrity/admission failure kills
    advancement rather than weakening the architecture.
