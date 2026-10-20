---
id: GRRR-fmvp
title: "Review the same governed decision across accessible surfaces"
status: open
priority: 1
type: task
labels: [milestone-1, integration]
parent: GRRR-2t3h
created_at: 2026-10-20T03:19:04Z
created_by: speed
updated_at: 2026-10-20T03:19:04Z
content_hash: "sha256:1561203859e4bb4f68b4a4165b383b3514d45e7ea3b1fe2f3bc48197e72da530"
blocked_by: [GRRR-dbbi]
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
I can make a safe informed decision quickly without reading source code, and get the same truthful answer in every surface.

## OUT OF SCOPE
No dashboard or notification-channel commitment; these are deferred unless evidence shows CLI/report needs unmet. Reports are projections, never a second verdict authority.

## DIFF BUDGET
~8 files, under 1300 changed LOC. Gross overrun triggers PM investigation, not automatic rejection.

## Boundary Map
PRODUCES:
- docs/runner-cli.md -> schema: operator-approved standalone runner grammar mapping start/status/review/evidence/decide/stop/recover intentions; version, action, flags, output, exit status; no invented pvg extension
- reports/review-template.md -> schema: summary, technical verification, full audit; exact action/target, separate execution/finding/decision/effect, snapshot currency/gates/budget/recovery
- reports/review-schema.json -> schema: same verified snapshot identities and state dimensions as CLI/Markdown; unknown explicit, authorization types separate, outcome distinct from intent

CONSUMES:
- GRRR-0g4n: docs/runner-cli.md
  spec: schema: operator-approved standalone runner grammar mapping start/status/review/evidence/decide/stop/recover intentions; version, action, flags, output, exit status; no invented pvg extension
  Usage: Read the versioned artifact or invoke the proposed test entrypoint exactly; validate identity and completeness before use; unknown/missing values block dependent authority.
- GRRR-my5n: research/ledger
  spec: `append(principal: Principal, event: ValidatedEvent, expectedTip: Digest, key: IdempotencyKey) → Result<EventReceipt, Error>`; `verifySnapshot(snapshot: SnapshotRef, trustedAnchor: ReceiptDigest) → Result<VerifiedSnapshot, Error>`
  Usage: append(authenticated evaluator, validatedEvent, expectedTip, key); verifySnapshot(exportRef, independently retained receipt digest) before trusting any projection.
- GRRR-c875: research/control
  spec: `stop(principal: Principal, run: RunId, key: IdempotencyKey, reason: Optional<Text>) → Result<StopReceipt, Error>`; `stopStatus(principal: Principal, operation: OperationId) → Result<StopOutcome, Error>`
  Usage: stop(authenticated operator, run, key, optionalReason) directly against evaluator; poll stopStatus(operation) without claiming acknowledgement equals cessation.
- GRRR-z3w9: research/replay
  spec: `reproduce(principal: Principal, allegation: AllegationRef, policy: PolicyDigest, reservation: ReservationId) → Result<ReplayReceipt, Error>`
  Usage: reproduce(authenticated evaluator, allegationRef, pinned policy, reservation.id); inspect finding and every gate; never infer admission.
- GRRR-34ve: research/authorization
  spec: `validateAuthorization(principal: Principal, request: ActionBinding, approval: ApprovalRef) → Result<AuthorizationGrant, Error>`
  Usage: validateAuthorization(authenticated human principal, exact ActionBinding, approvalRef); Error blocks; a grant is action-specific and consumed at commit.
- GRRR-34ve: research/admission
  spec: `admit(principal: Principal, proposal: ContractDigest, snapshot: VerifiedSnapshotRef, grant: AuthorizationGrant, fence: RunEpoch, key: IdempotencyKey) → Result<AdmissionReceipt, Error>`
  Usage: admit(authenticated admission controller, exact ContractDigest, VerifiedSnapshotRef, validated grant, current RunEpoch, key); inspect committed/blocked/recovery-required receipt.
- GRRR-dbbi: reports/comparison.json
  spec: schema: snapshot/run/arm IDs, selector provenance, availability, unique validated counts, FP/FN denominators, costs/reservations, repetitions, uncertainty, threshold outcome
  Usage: Read the versioned artifact or invoke the proposed test entrypoint exactly; validate identity and completeness before use; unknown/missing values block dependent authority.
- GRRR-0g4n: scripts/test-story
  spec: `./scripts/test-story <story-slug>` → exit 0 only when every required test passes; nonzero for missing infrastructure, skipped mandatory tests or failures (proposed test entrypoint, not installed)
  Usage: Read the versioned artifact or invoke the proposed test entrypoint exactly; validate identity and completeness before use; unknown/missing values block dependent authority.

## Acceptance Criteria
1. Approved standalone CLI help exposes start/status/review/evidence/decide/stop/recover intentions without claiming pvg research exists. Start preview names scope/baseline/limits/authorization; status shows phase/blockers/consumed/remaining budgets/report. Errors identify run, effect/non-effect and next safe step with failure status.
2. Plain text, Markdown and JSON read one integrity-verified consistent snapshot and agree on run/candidate/evaluator/snapshot, gate inventory, costs/reservations, finding, decision, outcome and recovery. Explicit unknown values never zero/pass; historical snapshots label currency and cannot authorize action.
3. Use exact separate vocabulary: Execution Queued/Running/Awaiting verification/Ready for review/Stopped/Failed/Completed; Finding Verified defect/Not reproduced/Specification ambiguity/Inconclusive/Invalid claim; Decision Approve/Reject/Needs more evidence/Request change/Stop. proposed/observed/verified/approved/deployed remain distinct; deployed is out of scope.
4. Markdown orders decision summary then technical replay then full audit. Summary includes claim/requirement/actual behavior, replay and gate state, action target, blockers, snapshot/currency, budget and recommendation reason. Technical evidence has minimal input, expected/actual, replay command/output, byte IDs and spec; audit retains all failures, revisions and costs. Recorded output is visibly not fresh replay.
5. Preview three authorization types separately with actor/reason/time/exact target/effect and explicit high-impact confirmation; Approve is never default. Needs more evidence/Request change/Reject cannot admit. Show decision recorded separately from pending/failed/committed effect. Missing/stale gates remain BLOCKER on all surfaces, not just warning text.
6. Stop is directly accessible during running/review without a lengthy form. Display cancellation pending, Stopped safely, Rollback completed and verified, or Recovery required only with respective evidence. List preserved/interrupted artifacts, changed resources and exact safe recovery choices; separate consent for persistent/external effects.
7. Keyboard-only and screen-reader walkthroughs cover inspect/decision/stop/recovery with ordered headings, readable link labels, textual BLOCKER/WARNING/INFO and no color-only meaning. Approximately 80-column prose does not truncate critical IDs. Ordinary decision needs neither raw JSON nor source reading/dashboard.
8. Record actual operator review-session time against 60-minute POC/three-hour milestone ceilings; concise unchanged progress demands no repeated review. Tests show complete-but-unapproved, failed replay, stale snapshot, integrity failure, unknown budget, pending cancellation and committed-before-stop parity. Qualified comparison includes sample limits and unavailable Jev truthfully.
9. Optional nd integration stores receipt ID and verified artifact location only through supported discovered pvg nd operations; it is not a second evidence ledger. Export/verifier links remain valid after disposable cleanup and do not grant authority from report wording.

## Testing Requirements
Integration tests: MANDATORY (no mocks). Include real success path plus every negative/error/concurrency case enumerated in the AC. Use real local VM, OS identities/permissions, evaluator, transactional store and pinned vlt where the path crosses them; mocks/stubs/fake receipts do not establish integration proof. Unit tests may supplement pure parsing/serialization; they cannot replace real integration. No skip-if-missing or environment-variable shortcut to green.
Proposed required command after implementation: ./scripts/test-story review-surfaces. The walking skeleton creates this test entrypoint; it must enumerate required tests, report counts and exit nonzero on missing prerequisites/failures. This command does not exist today. Capture actual commands, versions, stdout/stderr, exit codes, elapsed/runtime/review costs and artifact hashes; never fabricate results. Any required infrastructure authorization not yet granted blocks test execution explicitly, not story scope.

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
- [ ] AC #8: pending implementation and independent proof.
- [ ] AC #9: pending implementation and independent proof.

## Acceptance Criteria


## Design


## Notes


## History
- 2026-10-20T03:19:04Z dep_added: blocked_by GRRR-dbbi

## Links
- Parent: [[GRRR-2t3h]]
- Blocked by: [[GRRR-dbbi]]

## Comments
