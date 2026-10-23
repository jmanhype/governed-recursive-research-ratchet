---
id: GRRR-z3w9
title: "Verify a defect from fresh trusted inputs"
status: in_progress
priority: 1
type: task
labels: [milestone-1, integration]
parent: GRRR-2t3h
created_at: 2026-10-20T03:19:03Z
created_by: speed
updated_at: 2026-10-23T21:52:12Z
content_hash: "sha256:a18d541e2667176718673bb9105491446f48baf8eed0ff041290ac49014e550e"
blocks: [GRRR-34ve, GRRR-6sso, GRRR-dbbi]
was_blocked_by: [GRRR-bnkf, GRRR-w1lt]
follows: [GRRR-bnkf, GRRR-w1lt]
assignee: dev-GRRR-z3w9
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
I can separate plausible allegations from independently reproduced specification violations before granting any authority.

## OUT OF SCOPE
Human contract approval and registry commits belong to admission; selector ranking belongs to comparison. Reproduction never grants software promotion or modifies specifications.

## DIFF BUDGET
~6 files, under 1000 changed LOC. Gross overrun triggers PM investigation, not automatic rejection.

## Boundary Map
PRODUCES:
- research/replay -> `reproduce(principal: Principal, allegation: AllegationRef, policy: PolicyDigest, reservation: ReservationId) → Result<ReplayReceipt, Error>`
- tests/integration/independent-replay -> spec: real success and all enumerated failure cases via ./scripts/test-story independent-replay; no mocks, mandatory absence fails

CONSUMES:
- GRRR-bnkf: corpus/spec-map.json
  spec: schema: challenge ID, pinned authoritative specification or operator-approved requirement digest, expected behavior, provenance, ambiguity/validation status
  Usage: Read the versioned artifact or invoke the proposed test entrypoint exactly; validate identity and completeness before use; unknown/missing values block dependent authority.
- GRRR-bnkf: corpus/manifest.json
  spec: schema: version, source/build/variant/input digests, public challenge IDs, protected truth/critical labels, clean/faulty observations, category, independent validation references; public projection omits hidden truth
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
- GRRR-0g4n: scripts/test-story
  spec: `./scripts/test-story <story-slug>` → exit 0 only when every required test passes; nonzero for missing infrastructure, skipped mandatory tests or failures (proposed test entrypoint, not installed)
  Usage: Read the versioned artifact or invoke the proposed test entrypoint exactly; validate identity and completeness before use; unknown/missing values block dependent authority.

## Story Acceptance Criteria
1. An operator requests replay of a recorded allegation; evaluator reconstructs pinned source/build/test inputs and fresh VM isolation from protected trusted artifacts, reserves budget and records new observation. Do not trust challenger-created harness/logs/expected outputs/fixtures as evidence. Record candidate/evaluator/toolchain byte identities and environment differences.
2. Confirm behavior against pinned maintainer specification or explicit operator-approved requirement; implementation behavior alone is not specification. Verified defect requires independently reproduced failure plus spec confirmation, never claimant self-certification. Second physical host is not required after isolation proof.
3. ReplayReceipt carries Finding and each mandatory gate with evidence: Verified defect, Not reproduced, Specification ambiguity, Inconclusive, Invalid claim. Execution completion is separate and cannot imply admission. Clean negative remains non-defect; reproduction failure/ambiguous specification cannot be verified or admitted.
4. Real integration tests use valid seed, clean baseline, forged PASS/logs, candidate-modified harness/fixture, stale candidate/evaluator binding, missing objects, failed rebuild, interrupted replay and ambiguous requirement. Gate failures are visible and block admission; no skip-if-missing.
5. Two consecutive independent replay failures within a run trigger stop only after that numeric policy is approved; all failures retained, reservations conservative and evidence exported. A successful fresh replay records its own receipt rather than overwriting prior failed/recorded evidence.

## Testing Requirements
Integration tests: MANDATORY (no mocks). Include real success path plus every negative/error/concurrency case enumerated in the AC. Use real local VM, OS identities/permissions, evaluator, transactional store and pinned vlt where the path crosses them; mocks/stubs/fake receipts do not establish integration proof. Unit tests may supplement pure parsing/serialization; they cannot replace real integration. No skip-if-missing or environment-variable shortcut to green.
Proposed required command after implementation: ./scripts/test-story independent-replay. The walking skeleton creates this test entrypoint; it must enumerate required tests, report counts and exit nonzero on missing prerequisites/failures. This command does not exist today. Capture actual commands, versions, stdout/stderr, exit codes, elapsed/runtime/review costs and artifact hashes; never fabricate results. Any required infrastructure authorization not yet granted blocks test execution explicitly, not story scope.

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

## Acceptance Criteria


## Design


## Notes


## History
- 2026-10-20T03:19:03Z dep_added: blocked_by GRRR-bnkf
- 2026-10-20T03:19:04Z dep_added: blocks GRRR-34ve
- 2026-10-20T03:19:05Z dep_added: blocks GRRR-6sso
- 2026-10-20T03:20:00Z dep_added: blocks GRRR-dbbi
- 2026-10-23T18:36:37Z dep_removed: was_blocked_by GRRR-bnkf
- 2026-10-23T18:42:50Z status: open -> in_progress
- 2026-10-23T18:42:50Z auto-follows: linked to predecessor GRRR-bnkf
- 2026-10-23T18:42:50Z claimed by dev-GRRR-z3w9
- 2026-10-23T18:51:31Z status: in_progress -> open
- 2026-10-23T18:51:31Z released by speed
- 2026-10-23T18:55:10Z dep_added: blocked_by GRRR-w1lt
- 2026-10-23T21:29:29Z dep_removed: was_blocked_by GRRR-w1lt
- 2026-10-23T21:30:42Z status: open -> in_progress
- 2026-10-23T21:30:42Z auto-follows: linked to predecessor GRRR-w1lt
- 2026-10-23T21:30:43Z claimed by dev-GRRR-z3w9

## Links
- Parent: [[GRRR-2t3h]]
- Blocks: [[GRRR-34ve]], [[GRRR-6sso]], [[GRRR-dbbi]]
- Was blocked by: [[GRRR-bnkf]], [[GRRR-w1lt]]
- Follows: [[GRRR-bnkf]], [[GRRR-w1lt]]

## Comments

### 2026-10-23T18:51:22Z speed
BLOCKED: Mandatory independent-replay execution prerequisites are unavailable, and no source changes were made.

Exact preflight at worktree story/GRRR-z3w9, HEAD 663a6b4 (clean):
- Current worker UID is 501; the accepted evaluator path requires actual UID 320 and runner UID 321.
- No fresh replay runtime exists: find /private/tmp -maxdepth 1 -type d -name 'grrr-replay-*' returned 0.
- No active corpus runtime exists: find /private/tmp -maxdepth 1 -type d -name 'grrr-corpus-*' returned 0.
- The replay-capable preserved executor is root-owned under /Library/GRRR and invokes QEMU; this worker is explicitly prohibited from sudo, QEMU, or mutating /Library/GRRR.
- Corpus v2.2 identity checks passed: version GRRR-validated-corpus-v2.2-isolated, freeze dfa75ef2bf3d43fd4f750094fe643afe4f204812c0ae2426276bedb471fa8529, source commit 129e0b3f15a3bd6af949ee47d76f6855c582ab73; all 7 manifest-listed artifacts matched SHA-256.
- No operator-approved numeric replay-stop policy was found. docs/ARCHITECTURE.md contains only the proposed threshold of two consecutive independent replay failures; execution must not infer approval.
- ./scripts/test-story independent-replay is not wired because implementation without a real success/failure execution path would create an unverifiable/gated suite, contrary to the story.

Required parent-mediated request:
1. Approve an explicit replay policy record binding run scope, two consecutive independent replay failures, watchdog/grace limits, and the corpus/source identities above.
2. Prepare a fresh root-owned disposable replay runtime with UID 320 evaluator, UID 321 runner, preserved QEMU/assets, evaluator-owned budget/ledger/expectations, and a protected replay policy/spec projection.
3. Only then dispatch this story again. The parent must provide/execute the approved launcher; do not reuse or mutate /Library/GRRR as this worker.

DISCOVERED_BUG:
  title: Independent replay lacks approved privileged execution prerequisites
  context: GRRR-z3w9 requires a fresh evaluator-controlled VM replay and an approved numeric consecutive-failure stop policy. The accepted corpus inputs are intact, but no fresh runtime or approval record exists, and the worker cannot create the required UID-separated QEMU environment without violating its explicit privileges.
  affected_files: research/replay.py (proposed); tests/integration/independent_replay.py (proposed); scripts/test-story
  discovered_during: GRRR-z3w9

### 2026-10-23T21:52:12Z speed
BLOCKED: Partial WIP only. PersistentBudget has no independent-replay profile; parent reports active cumulative store stopped. Fresh allowance is forbidden. Real replay-specific failed-rebuild, interruption and consecutive-failure guest fixtures/modes remain unfinished and require continuation plus independent review. No guest or protected mutation performed. See docs/INDEPENDENT-REPLAY-WIP.md; story will not be delivered.
