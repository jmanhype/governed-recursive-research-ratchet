---
id: GRRR-c875
title: "Stop a hung research run through independent trusted control"
status: in_progress
priority: 1
type: task
labels: [milestone-1, integration]
parent: GRRR-2t3h
created_at: 2026-10-20T03:19:02Z
created_by: speed
updated_at: 2026-10-21T20:53:17Z
content_hash: "sha256:5c2cb242d29ec6247798e81cad5d96fd9d5f92e3116f5a5f55f3824a3a357f3c"
blocks: [GRRR-bnkf, GRRR-6sso]
was_blocked_by: [GRRR-my5n]
assignee: dev-GRRR-c875
follows: [GRRR-my5n]
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
I can stop work even when the scheduling process hangs and see whether cessation and recovery are actually verified.

## OUT OF SCOPE
Actual protected-admission races and rollback registry events land in admission after this fence exists. Do not manufacture a stub admission as proof. Host failure and disaster recovery are not guaranteed.

## DIFF BUDGET
~7 files, under 1400 changed LOC. Gross overrun triggers PM investigation, not automatic rejection.

## Boundary Map
PRODUCES:
- research/control -> `stop(principal: Principal, run: RunId, key: IdempotencyKey, reason: Optional<Text>) → Result<StopReceipt, Error>`; `stopStatus(principal: Principal, operation: OperationId) → Result<StopOutcome, Error>`
- research/execution -> `dispatch(principal: Principal, request: ApprovedInvocation, reservation: ReservationId, fence: RunEpoch, key: IdempotencyKey) → Result<DispatchReceipt, Error>`
- tests/integration/safe-stop -> spec: real success and all enumerated failure cases via ./scripts/test-story safe-stop; no mocks, mandatory absence fails

CONSUMES:
- GRRR-my5n: research/ledger
  spec: `append(principal: Principal, event: ValidatedEvent, expectedTip: Digest, key: IdempotencyKey) → Result<EventReceipt, Error>`; `verifySnapshot(snapshot: SnapshotRef, trustedAnchor: ReceiptDigest) → Result<VerifiedSnapshot, Error>`
  Usage: append(authenticated evaluator, validatedEvent, expectedTip, key); verifySnapshot(exportRef, independently retained receipt digest) before trusting any projection.
- GRRR-gu87: research/execution
  spec: `dispatch(principal: Principal, request: ApprovedInvocation, reservation: ReservationId, fence: RunEpoch, key: IdempotencyKey) → Result<DispatchReceipt, Error>`
  Usage: dispatch(authenticated evaluator, allowlisted ApprovedInvocation, reservation.id, current RunEpoch, key); reject any Error, stale fence or unknown outcome.
- GRRR-gu87: research/budget
  spec: `reserve(principal: Principal, run: RunId, maximum: ResourceVector, key: IdempotencyKey) → Result<Reservation, Error>`; `settle(principal: Principal, reservation: ReservationId, actual: VerifiedUsage) → Result<SettlementReceipt, Error>`
  Usage: reserve(authenticated evaluator, run, worstCaseResourceVector, key) before dispatch; settle only trusted VerifiedUsage; retain unknown reservation.
- GRRR-90te: research/policy
  spec: `loadPolicy(principal: Principal, ref: PolicyDigest) → Result<VerifiedPolicy, Error>`
  Usage: loadPolicy(authenticated evaluator, pinned PolicyDigest); reject Error or unapproved scope before any work.
- GRRR-0g4n: scripts/test-story
  spec: `./scripts/test-story <story-slug>` → exit 0 only when every required test passes; nonzero for missing infrastructure, skipped mandatory tests or failures (proposed test entrypoint, not installed)
  Usage: Read the versioned artifact or invoke the proposed test entrypoint exactly; validate identity and completeness before use; unknown/missing values block dependent authority.

## Story Acceptance Criteria
1. Authenticated operator reaches evaluator-owned endpoint directly, independent of runner event loop/credentials. Approved local OS peer identity/allowlist and filesystem permissions deny guest/selector/runner impersonation. Urgent stop accepts an absent reason for later append; watchdog has safety-stop authority but no admission authority.
2. One serialized durable transaction appends stop, sets stopping and increments RunEpoch. Acknowledge only after commit with operation ID/epoch/receipt/cancellation state. Same-key repeat returns original receipt; distinct-key repeat references/appends existing stop without duplicate cancellation or restart.
3. dispatch final check serializes with stop; executor validates current epoch immediately before guest launch and reports every launched guest to evaluator tracking. Race queued/launching work with stop: no post-fence start; pre-fence launches remain tracked and canceled even if runner dies.
4. Evaluator control worker cancels/forces termination within approved measured numeric grace/watchdog bounds without runner cooperation; prove hung runner cannot delay it. Until cessation and protected-baseline checks verify, report cancellation pending, never Stopped safely. Unreachable executor or unknown state is Recovery required.
5. Crash before/after stop record, acknowledgement, cancellation and cessation checks. Failed durable recording returns no durable acknowledgement, attempts best-effort safety cancellation and fences work until recovery. Repeated status queries are safe and truthful.
6. Keep admission serialized on the same run state: document and test control-side fence rejection with actual durable records, not mocks. Full actual admission race tests are owned by admission once its module exists; no registry effect is claimed here.
7. On budget/protected-write/isolation/dependency/evidence/repeated-unreproducibility triggers, stop scheduling/admission and preserve all evidence. Operator emergency VM-stop procedure handles unreachable control endpoint without false success. Baseline hashes and behavior verify cessation/restoration; persistent/external recovery or reversal needs new explicit authorization.

## Testing Requirements
Integration tests: MANDATORY (no mocks). Include real success path plus every negative/error/concurrency case enumerated in the AC. Use real local VM, OS identities/permissions, evaluator, transactional store and pinned vlt where the path crosses them; mocks/stubs/fake receipts do not establish integration proof. Unit tests may supplement pure parsing/serialization; they cannot replace real integration. No skip-if-missing or environment-variable shortcut to green.
Proposed required command after implementation: ./scripts/test-story safe-stop. The walking skeleton creates this test entrypoint; it must enumerate required tests, report counts and exit nonzero on missing prerequisites/failures. This command does not exist today. Capture actual commands, versions, stdout/stderr, exit codes, elapsed/runtime/review costs and artifact hashes; never fabricate results. Any required infrastructure authorization not yet granted blocks test execution explicitly, not story scope.

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
status: in_progress

### evidence
- Claimed 2026-10-21 from operator continuation authorization.
- Preserved local WIP commit 459b3c3 on story/GRRR-c875; worktree renamed to dev-GRRR-c875.

### proof
- [ ] AC #1 through AC #7 pending completion and real integration evidence.

## History
- 2026-10-20T03:19:02Z dep_added: blocked_by GRRR-my5n
- 2026-10-20T03:19:03Z dep_added: blocks GRRR-bnkf
- 2026-10-20T03:19:05Z dep_added: blocks GRRR-6sso
- 2026-10-21T20:46:47Z dep_removed: was_blocked_by GRRR-my5n
- 2026-10-21T20:53:17Z status: open -> in_progress
- 2026-10-21T20:53:17Z auto-follows: linked to predecessor GRRR-my5n
- 2026-10-21T20:53:17Z claimed by dev-GRRR-c875

## Links
- Parent: [[GRRR-2t3h]]
- Blocks: [[GRRR-bnkf]], [[GRRR-6sso]]
- Was blocked by: [[GRRR-my5n]]
- Follows: [[GRRR-my5n]]

## Comments
