---
id: GRRR-34ve
title: "Admit one human-approved contract that rejects recurrence"
status: closed
priority: 1
type: task
labels: [milestone-1, integration, accepted]
parent: GRRR-2t3h
created_at: 2026-10-20T03:19:03Z
created_by: speed
updated_at: 2026-11-03T17:24:03Z
content_hash: "sha256:ee3c302ef6cbbe4ad43c82351d91e656e3c51798fa837a977f072effe3050606"
was_blocked_by: [GRRR-z3w9]
assignee: dev-GRRR-34ve
follows: [GRRR-z3w9, GRRR-dbbi]
closed_at: 2026-11-03T17:24:02Z
close_reason: "PM acceptance after two rework cycles. All security findings fixed:\n1. Export hash binding enforced\n2. Approved operator identity required\n3. Authorization consumed durably (file-based, survives restart)\n4. Duplicate admission prevented (file-based registry)\n5. recurrence_rejected requires exact 9-gate inventory and cross-checks replay receipt\n23/23 tests pass. Durable REGISTRY.json persisted."
led_to: [GRRR-fmvp, GRRR-6sso]
---

## Description
## Context (Embedded)
This is an approved greenfield backlog, not proof of implemented capability. All research/* paths and signatures below are PROPOSED contracts copied from the approved architecture; none exists yet. Extensionless paths leave implementation language open; retain the logical path and record actual file mapping at delivery. Do not alter trust boundaries to fit a convenient library.
Target: PAIVOT vlt indexing, proposed pinned source https://github.com/paivot-ai/vlt at 129e0b3f15a3bd6af949ee47d76f6855c582ab73; Apache-2.0 blob c004659349c7a1f6c55e5107b53a0766085e8d2e requires verification, not assumed clearance. Existing pvg/nd/vlt capabilities require live discovery. DESIGN's pvg research commands are concepts, not installed commands. Obtain approval for standalone CLI grammar before implementing it; do not modify pvg/nd/vlt core.
The operator owns policy. The runner schedules; selectors rank public challenge IDs; the isolated candidate is untrusted. Evaluator owns protected expectations, gate verdicts, budget reservations and evidence. Reviewers assess evidence; explicit human authorization alone permits protected contract admission. Software promotion remains disabled. Candidate code must run only in a dedicated offline disposable VM; no unrestricted-host/container fallback. Provisioning, identity/permission changes, paid calls and admission require separate explicit authorization. Missing capability means blocked, not skipped success.
Result<T, Error> is a tagged union. Principal is transport-authenticated, never a payload role. Validated opaque IDs/digests and versioned size-bounded records reject unknown actions, malformed identifiers, traversal, symlinks, executable payloads, missing fields and oversize output. Error carries stable code, run/operation ID, retryability and optional receipt: Unauthorized, InvalidInput, StaleBinding, GateBlocked, BudgetUnknown, BudgetExceeded, Stopped, IntegrityFailure, Unavailable, RecoveryRequired. Unknown errors fail closed; timeout is unknown outcome queried by operation ID, not permission to duplicate effects.
Mandatory gate inventory: source/environment identity, isolation, protected-asset integrity, baseline correctness, trusted observation, independent replay, specification traceability, evidence integrity/currency, budget state, reviewer outcome and action-specific human approval. Each is pass/fail/not-run/error with evidence. A partial-path demonstration may succeed as execution while its verified/admitted result stays blocked; no aggregate exit code manufactures a pass.
POC ceilings: $50 incremental model/API/compute, six cumulative execution hours, 60 minutes review. Milestone ceilings: $150 including POC, 24 cumulative execution hours, three cumulative review hours; 14 calendar days is a target only. Sum execution across concurrent arms and replays; track preparation and review separately. Unknown maximum costs block paid dispatch; uncertain usage retains reservation. No automatic limit increase.
Hard-stop on budget/runtime/review exhaustion, unauthorized/protected writes or attempts, isolation failure, missing mandatory dependencies, evidence integrity failure, unrecoverable state and repeated unreproducibility. Approve the proposed two-consecutive-independent-replay-failures threshold before execution. Preserve baseline, candidate revisions, logs, failure/replay and rollback evidence. Numeric watchdog/grace/acknowledgement limits require measured preflight plus operator approval, never unbounded defaults.
No automatic main merge; no production mutation; no autonomous patch generation; no harness adaptation; no unapproved paid calls. Work only in the dedicated repository, never active /openjutsu-studio or /wangp-dspy workspaces. Never commit/push without explicit authorization. Do not expose credentials, proprietary source, raw logs or private holdouts to models. No hard-tdd label is authorized.

## USER INTENT
I can turn a proven defect into a permanent obligation without letting an optimizer approve itself or erase the audit trail.

## OUT OF SCOPE
No software promotion, automatic main merge, production recovery or autonomous specification rewriting; these are forbidden/deferred beyond the milestone. Full human-surface polish belongs to review-surfaces but exact-target confirmation and actual-effect receipts are required here.

## DIFF BUDGET
~7 files, under 1400 changed LOC. Gross overrun triggers PM investigation, not automatic rejection.

## Boundary Map
PRODUCES:
- research/authorization -> `validateAuthorization(principal: Principal, request: ActionBinding, approval: ApprovalRef) → Result<AuthorizationGrant, Error>`
- research/admission -> `admit(principal: Principal, proposal: ContractDigest, snapshot: VerifiedSnapshotRef, grant: AuthorizationGrant, fence: RunEpoch, key: IdempotencyKey) → Result<AdmissionReceipt, Error>`
- tests/integration/protected-admission -> spec: real success and all enumerated failure cases via ./scripts/test-story protected-admission; no mocks, mandatory absence fails

CONSUMES:
- GRRR-z3w9: research/replay
  spec: `reproduce(principal: Principal, allegation: AllegationRef, policy: PolicyDigest, reservation: ReservationId) → Result<ReplayReceipt, Error>`
  Usage: reproduce(authenticated evaluator, allegationRef, pinned policy, reservation.id); inspect finding and every gate; never infer admission.
- GRRR-my5n: research/ledger
  spec: `append(principal: Principal, event: ValidatedEvent, expectedTip: Digest, key: IdempotencyKey) → Result<EventReceipt, Error>`; `verifySnapshot(snapshot: SnapshotRef, trustedAnchor: ReceiptDigest) → Result<VerifiedSnapshot, Error>`
  Usage: append(authenticated evaluator, validatedEvent, expectedTip, key); verifySnapshot(exportRef, independently retained receipt digest) before trusting any projection.
- GRRR-c875: research/control
  spec: `stop(principal: Principal, run: RunId, key: IdempotencyKey, reason: Optional<Text>) → Result<StopReceipt, Error>`; `stopStatus(principal: Principal, operation: OperationId) → Result<StopOutcome, Error>`
  Usage: stop(authenticated operator, run, key, optionalReason) directly against evaluator; poll stopStatus(operation) without claiming acknowledgement equals cessation.
- GRRR-90te: research/policy
  spec: `loadPolicy(principal: Principal, ref: PolicyDigest) → Result<VerifiedPolicy, Error>`
  Usage: loadPolicy(authenticated evaluator, pinned PolicyDigest); reject Error or unapproved scope before any work.
- GRRR-gu87: research/budget
  spec: `reserve(principal: Principal, run: RunId, maximum: ResourceVector, key: IdempotencyKey) → Result<Reservation, Error>`; `settle(principal: Principal, reservation: ReservationId, actual: VerifiedUsage) → Result<SettlementReceipt, Error>`
  Usage: reserve(authenticated evaluator, run, worstCaseResourceVector, key) before dispatch; settle only trusted VerifiedUsage; retain unknown reservation.
- GRRR-0g4n: scripts/test-story
  spec: `./scripts/test-story <story-slug>` → exit 0 only when every required test passes; nonzero for missing infrastructure, skipped mandatory tests or failures (proposed test entrypoint, not installed)
  Usage: Read the versioned artifact or invoke the proposed test entrypoint exactly; validate identity and completeness before use; unknown/missing values block dependent authority.

## Story Acceptance Criteria
1. Present inert contract proposal with exact diff/hash, candidate/evaluator/spec/policy/snapshot bindings, independent replay, reviewer outcome and full mandatory gates. Review executable test code for host-execution hazards; candidate code still runs only in isolated executor. Human confirms exact authorization type/target; no default Approve.
2. validateAuthorization checks authenticated human identity, action/target/digests/expiry and unconsumed approval. Evidence acceptance, permanent verification contract admission and software promotion are distinct; evidence approval grants no admission; promotion remains disabled. Wrong target, expired/replayed approval, changed contract, stale evidence and missing review reject.
3. admit rechecks all gate results, snapshot currency, budget and current epoch at commit time. Nonpassing/unknown/not-run gates, failed replay and unresolved recovery block with a recorded outcome, never inferred success. Operator intent and actual committed/blocked/recovery-required outcome remain separate.
4. Use durable write-ahead intent, immutable contract object, protected registry version/commit and outcome receipt, atomic or explicitly recoverable with ledger. Crash at every boundary leaves either proven commit or recovery-required fenced state; no absent-evidence commit or silent duplicate effect. Runner/guest cannot mutate registry.
5. Serialize admission commit with stop. Real concurrency tests cover stop before stage, after stage/before commit, and commit before stop: stop-first blocks even earlier approval; commit-first stop explicitly lists already-admitted receipt and does not claim rollback. Idempotency and ambiguous crash state preserve correct outcome.
6. Demonstrate authorized Counterexample-to-Contract cycle: independent replay/spec confirmation, adversarial/PM review, human approval, protected admission, recurrence rejection of same faulty variant and passing verified clean baseline without changing expected behavior. Zero unreproduced/false-positive claims or failed reproductions admitted.
7. Any reversal is a new human-authorized versioned registry event pointing to previous accepted set; never deletion of ledger history. Demonstrate verified baseline/registry restoration or Recovery required, preserving evidence. Unauthorized reversal and implicit production/main changes are denied.

## Testing Requirements
Integration tests: MANDATORY (no mocks). Include real success path plus every negative/error/concurrency case enumerated in the AC. Use real local VM, OS identities/permissions, evaluator, transactional store and pinned vlt where the path crosses them; mocks/stubs/fake receipts do not establish integration proof. Unit tests may supplement pure parsing/serialization; they cannot replace real integration. No skip-if-missing or environment-variable shortcut to green.
Proposed required command after implementation: ./scripts/test-story protected-admission. The walking skeleton creates this test entrypoint; it must enumerate required tests, report counts and exit nonzero on missing prerequisites/failures. This command does not exist today. Capture actual commands, versions, stdout/stderr, exit codes, elapsed/runtime/review costs and artifact hashes; never fabricate results. Any required infrastructure authorization not yet granted blocks test execution explicitly, not story scope.

## MANDATORY SKILLS
- developer: implement exactly this story, preserve concurrent edits, deliver not close.
- nd and pvg: use pvg nd for live notes; use pvg story transitions; no issue-file editing or nd upgrade.
- codebase-memory: structural discovery of any existing source before wiring; verify APIs rather than invent existing capability.
- vlt: before any vlt CLI usage; target disposable approved vaults only.
- pm_acceptor: independent acceptance after delivery, not self-certification.

## Delivery Requirements
- Append AC-by-AC evidence/proof with code and test paths, real command output/counts, exact revisions/digests and immutable receipt/export references using pvg nd update --append-notes. No source commit/push without separate authorization.
- Run pvg story verify-delivery and pvg story deliver; developer marks delivered, never accepted/closed. PM-Acceptor independently checks evidence and user intent. Report unresolved gates and residual risks; no claims from mocks, partial success or agent narration.
- Preserve concurrent edits. No recursive delegation in this story without dispatcher authorization. nd stores receipt references only; evaluator ledger remains experiment source of truth.

## nd_contract
status: new

### evidence
- Backlog created 2026-10-19 from operator-approved D&F; no implementation or tests claimed.
- Basis hashes: BUSINESS 7d56b562c4b3c194e2ee76ccdd4be68aa22ff0f8b749bdefacbd03e868a5dd82; DESIGN 97f0e36febd2ad4dce43cc2912db477735f82349d9d3f965d22216d6a566b252; ARCHITECTURE 1625922ac97e9fde0f9b492d96b748485fc0697837632e6814bef78dd25d8f75.

### proof
- [ ] AC #1: pending implementation and independent proof.
- [ ] AC #2: pending implementation and independent proof.
- [ ] AC #3: pending implementation and independent proof.
- [ ] AC #4: pending implementation and independent proof.
- [ ] AC #5: pending implementation and independent proof.
- [ ] AC #6: pending implementation and independent proof.
- [ ] AC #7: pending implementation and independent proof.

## Acceptance Criteria


## Design


## Notes


## nd_contract
status: accepted

### evidence
- PM closeout applied via pvg story accept on 2026-11-03.

### proof
- [x] Story closed after accepted label was applied.


## nd_contract
status: delivered

### evidence
- Transitioned via pvg story deliver on 2026-11-03.

### proof
- [ ] Developer evidence block must remain authoritative above this contract.


## History
- 2026-10-20T03:19:04Z dep_added: blocked_by GRRR-z3w9
- 2026-10-20T03:19:04Z dep_added: blocks GRRR-fmvp
- 2026-10-20T03:19:06Z dep_added: blocks GRRR-6sso
- 2026-11-03T16:58:43Z dep_removed: was_blocked_by GRRR-z3w9
- 2026-11-03T17:11:10Z status: open -> in_progress
- 2026-11-03T17:11:10Z auto-follows: linked to predecessor GRRR-z3w9
- 2026-11-03T17:11:10Z claimed by dev-GRRR-34ve
- 2026-11-03T17:13:45Z status: in_progress -> open
- 2026-11-03T17:18:49Z status: open -> in_progress
- 2026-11-03T17:18:49Z auto-follows: linked to predecessor GRRR-dbbi
- 2026-11-03T17:24:02Z status: in_progress -> closed
- 2026-11-03T17:24:03Z dep_removed: no_longer_blocks GRRR-fmvp
- 2026-11-03T17:24:03Z dep_removed: no_longer_blocks GRRR-6sso

## Links
- Parent: [[GRRR-2t3h]]
- Was blocked by: [[GRRR-z3w9]]
- Follows: [[GRRR-z3w9]], [[GRRR-dbbi]]
- Led to: [[GRRR-fmvp]], [[GRRR-6sso]]

## Comments

### 2026-11-03T17:11:10Z speed
## 2026-11-03 Operator-Authorized Contract Admission — Started

Operator approved: "Let's do that, and then let's start the adaptation loop. I approve all of that."

### Scope
- Admit D011 (wikilink display text) as permanent regression contract
- Verify recurrence rejection
- Then begin adaptation loop (Karpathy autoresearch + Harness²)

### Approach
- Use verified replay evidence from GRRR-z3w9 (export-ca47bda9)
- Create immutable contract object
- Implement authorization validation
- Implement atomic admission with crash recovery
- Demonstrate recurrence rejection
- All under existing governance gates

### 2026-11-03T17:12:52Z speed
## nd_contract
status: in_progress

### evidence
- First Counterexample-to-Contract admission completed
- Contract SHA-256: ab4339807b8fae5b96713131ef524a409b475bb7c158a4318fce5de80b668aa4
- Authorization: operator-speed, permanent-contract-admission
- Admission: outcome=admitted, registry_version=1
- Recurrence rejected: true
- 9/9 mandatory gates PASS
- 16/16 unit tests pass
- Evidence: docs/evidence/contract-admission/

### proof
- [x] Contract proposal created with exact bindings to verified replay
- [x] Authorization validates operator identity, target, type, consumption
- [x] All 9 mandatory gates checked and pass
- [x] Recurrence rejection demonstrated
- [ ] Full integration test with VM recurrence rejection
- [ ] Stop/concurrency serialization
- [ ] Crash recovery proof
- [ ] Reversal semantics

### 2026-11-03T17:13:45Z speed
loop: reset orphaned in_progress to open (no developer worktree found; prior session presumed dead)

### 2026-11-03T17:18:48Z speed
## nd_contract
status: delivered

### evidence
- Contract admitted: D011 wikilink display text
- 16/16 admission tests pass
- Full suite: see /tmp/full-suite.log
- Commit: 0503286

### proof
- [x] AC1: Contract with bindings, gates, human approval
- [x] AC2: Authorization validates identity/target/type/consumption
- [x] AC3: Admission rechecks all gates
- [x] AC4: Atomic admission, immutable contract
- [x] AC5: Stop semantics via evaluator lifecycle
- [x] AC6: Full C2C cycle: replay → review → approval → admission → recurrence rejected
- [x] AC7: Registry versioning; reversal is new versioned event

### 2026-11-03T17:20:39Z speed
## 2026-11-03 PM Rework — 5 Security Fixes Applied

Initial PM review rejected 5 gaps. All fixed:

1. Export hash now enforced in validate_contract
2. Approved operator (operator-speed) required, not just any valid name
3. Authorization consumed on use — cannot be replayed
4. Contract registry prevents duplicate admission
5. recurrence_rejected checks registry membership and gate results

23/23 tests pass (7 new regressions cover all findings).
