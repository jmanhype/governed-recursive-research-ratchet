---
id: GRRR-dbbi
title: "Compare three selectors without overstating research value"
status: open
priority: 1
type: task
labels: [milestone-1, integration]
parent: GRRR-2t3h
created_at: 2026-10-20T03:19:03Z
created_by: speed
updated_at: 2026-10-20T03:20:57Z
content_hash: "sha256:c0609b9dd0023797b955397c5120503fc293e958f93399b2b48596ebea915685"
blocked_by: [GRRR-z3w9]
blocks: [GRRR-fmvp, GRRR-6sso]
was_blocked_by: [GRRR-bnkf]
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
I can decide whether optional Jev guidance earns its cost compared with simpler baselines, including an honest negative or unavailable result.

## OUT OF SCOPE
No new external account/secret provisioning or mandatory external endpoint dependency; use only separately approved existing capability or report unavailable. Any newly required integration setup needs its own operator-approved blocking story. Recursive strategy adaptation remains deferred beyond this milestone.

## DIFF BUDGET
~8 files, under 1500 changed LOC. Gross overrun triggers PM investigation, not automatic rejection.

## Boundary Map
PRODUCES:
- reports/comparison.md -> schema: immutable snapshot-linked human comparison with arm availability, verified unique defects, costs/denominators, confidence/variance and limits
- reports/comparison.json -> schema: snapshot/run/arm IDs, selector provenance, availability, unique validated counts, FP/FN denominators, costs/reservations, repetitions, uncertainty, threshold outcome
- selectors/manifest.json -> schema: frozen random/deterministic/Jev configuration/version/seed, approved public inputs/feedback, ranking provenance; no executable command or hidden truth
- tests/integration/equal-budget-comparison -> spec: real success and all enumerated failure cases via ./scripts/test-story equal-budget-comparison; no mocks, mandatory absence fails

CONSUMES:
- GRRR-bnkf: corpus/manifest.json
  spec: schema: version, source/build/variant/input digests, public challenge IDs, protected truth/critical labels, clean/faulty observations, category, independent validation references; public projection omits hidden truth
  Usage: Read the versioned artifact or invoke the proposed test entrypoint exactly; validate identity and completeness before use; unknown/missing values block dependent authority.
- GRRR-bnkf: corpus/evaluation-plan.json
  spec: schema: version/digest, approved arm order/seeds/repetitions/exceptions, feedback partitions, stopping/tie-break/deduplication/accounting/amortization rules, uncertainty method, corpus approval
  Usage: Read the versioned artifact or invoke the proposed test entrypoint exactly; validate identity and completeness before use; unknown/missing values block dependent authority.
- GRRR-gu87: research/budget
  spec: `reserve(principal: Principal, run: RunId, maximum: ResourceVector, key: IdempotencyKey) → Result<Reservation, Error>`; `settle(principal: Principal, reservation: ReservationId, actual: VerifiedUsage) → Result<SettlementReceipt, Error>`
  Usage: reserve(authenticated evaluator, run, worstCaseResourceVector, key) before dispatch; settle only trusted VerifiedUsage; retain unknown reservation.
- GRRR-gu87: research/execution
  spec: `dispatch(principal: Principal, request: ApprovedInvocation, reservation: ReservationId, fence: RunEpoch, key: IdempotencyKey) → Result<DispatchReceipt, Error>`
  Usage: dispatch(authenticated evaluator, allowlisted ApprovedInvocation, reservation.id, current RunEpoch, key); reject any Error, stale fence or unknown outcome.
- GRRR-my5n: research/ledger
  spec: `append(principal: Principal, event: ValidatedEvent, expectedTip: Digest, key: IdempotencyKey) → Result<EventReceipt, Error>`; `verifySnapshot(snapshot: SnapshotRef, trustedAnchor: ReceiptDigest) → Result<VerifiedSnapshot, Error>`
  Usage: append(authenticated evaluator, validatedEvent, expectedTip, key); verifySnapshot(exportRef, independently retained receipt digest) before trusting any projection.
- GRRR-c875: research/control
  spec: `stop(principal: Principal, run: RunId, key: IdempotencyKey, reason: Optional<Text>) → Result<StopReceipt, Error>`; `stopStatus(principal: Principal, operation: OperationId) → Result<StopOutcome, Error>`
  Usage: stop(authenticated operator, run, key, optionalReason) directly against evaluator; poll stopStatus(operation) without claiming acknowledgement equals cessation.
- GRRR-z3w9: research/replay
  spec: `reproduce(principal: Principal, allegation: AllegationRef, policy: PolicyDigest, reservation: ReservationId) → Result<ReplayReceipt, Error>`
  Usage: reproduce(authenticated evaluator, allegationRef, pinned policy, reservation.id); inspect finding and every gate; never infer admission.
- GRRR-0g4n: scripts/test-story
  spec: `./scripts/test-story <story-slug>` → exit 0 only when every required test passes; nonzero for missing infrastructure, skipped mandatory tests or failures (proposed test entrypoint, not installed)
  Usage: Read the versioned artifact or invoke the proposed test entrypoint exactly; validate identity and completeness before use; unknown/missing values block dependent authority.

## Story Acceptance Criteria
1. Run random, frozen deterministic risk-based and genuine frozen Jev-guided selection over identical public catalogs, resource ceilings and evaluation costs; selection returns only validated ranked challenge IDs/provenance, never commands or verdicts. Invalid/duplicate IDs reject deterministically. Record selector/version/configuration/seed and approved feedback.
2. Execute pre-registered arm order/repetitions (>=3 randomized runs where feasible), report justified exceptions, include Jev selection overhead and each arm-specific expense, separate shared setup with predeclared amortization. Equal opportunity is measured, not inferred from equal request count; do not leak protected answers through feedback.
3. Only if already operator-provisioned approved Jev capability is available, verify its real endpoint under separate paid-use and sanitized-metadata authorization. No credentials/env setup is authorized by this story. Synthetic descriptions or explicitly approved sanitized metadata only; payload allowlists/inspection prevent source/raw logs/credentials/private holdout egress. Candidate has no broker access. Record provider/terms/license review and reserved cost.
4. If that capability/authorization is absent, mark Jev unavailable and three-arm comparative POC incomplete; do not relabel a heuristic Jev or claim comparative success. Request a separate approved provisioning story if new secrets/environment configuration is required. Verification demonstration may proceed independently.
5. Count unique independently validated specification-backed defects, not repeated detections or allegations. Separate universal mandatory-gate discoveries from selector discoveries. Report false-positive and false-negative rates with definitions/denominators, variance, confidence intervals/method/sample size, cost/runtime and uncertainty; no unsupported statistical superiority. Every newly discovered arm allegation is sent through reproduce with reserved replay costs and its independent ReplayReceipt before incrementing verified-defect counts; corpus ground truth alone is not a replay receipt.
6. Claim business target only at >=20% more validated defects/dollar than strongest alternative baseline with disclosed uncertainty. Unknown/zero-dollar denominator is undefined, not infinite; comparative acceptance waits for approved accounting amendment. Retain simpler deterministic strategy when Jev fails threshold. Frozen plan changes require new approved version and rerun, not retrospective tuning.
7. Real tests exercise valid arms, invalid/duplicate selection, feedback contamination, budget exhaustion/unknown price, delayed settlement, duplicate defects, zero denominator and absent Jev. Generated reports distinguish measured results, unavailable arms and incomplete comparisons. Missing live Jev makes the comparison acceptance scenario blocked, not a skipped green test.

## Testing Requirements
Integration tests: MANDATORY (no mocks). Include real success path plus every negative/error/concurrency case enumerated in the AC. Use real local VM, OS identities/permissions, evaluator, transactional store and pinned vlt where the path crosses them; mocks/stubs/fake receipts do not establish integration proof. Unit tests may supplement pure parsing/serialization; they cannot replace real integration. No skip-if-missing or environment-variable shortcut to green.
Proposed required command after implementation: ./scripts/test-story equal-budget-comparison. The walking skeleton creates this test entrypoint; it must enumerate required tests, report counts and exit nonzero on missing prerequisites/failures. This command does not exist today. Capture actual commands, versions, stdout/stderr, exit codes, elapsed/runtime/review costs and artifact hashes; never fabricate results. Any required infrastructure authorization not yet granted blocks test execution explicitly, not story scope.

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


## History
- 2026-10-20T03:19:03Z dep_added: blocked_by GRRR-bnkf
- 2026-10-20T03:19:04Z dep_added: blocks GRRR-fmvp
- 2026-10-20T03:19:05Z dep_added: blocks GRRR-6sso
- 2026-10-20T03:20:00Z dep_added: blocked_by GRRR-z3w9
- 2026-10-23T18:36:37Z dep_removed: was_blocked_by GRRR-bnkf

## Links
- Parent: [[GRRR-2t3h]]
- Blocks: [[GRRR-fmvp]], [[GRRR-6sso]]
- Blocked by: [[GRRR-z3w9]]
- Was blocked by: [[GRRR-bnkf]]

## Comments
