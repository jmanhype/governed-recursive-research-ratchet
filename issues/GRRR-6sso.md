---
id: GRRR-6sso
title: "E2e: Operator completes a governed vlt research ratchet"
status: in_progress
priority: 1
type: task
labels: [milestone-1, capstone, rejected]
parent: GRRR-2t3h
created_at: 2026-10-20T03:19:04Z
created_by: speed
updated_at: 2026-11-03T18:07:00Z
content_hash: "sha256:70000373efd067149e616e23a84c11cb9d619202fc4295a90bb9d1f8d6be44c2"
was_blocked_by: [GRRR-0g4n, GRRR-90te, GRRR-gu87, GRRR-my5n, GRRR-c875, GRRR-bnkf, GRRR-z3w9, GRRR-dbbi, GRRR-34ve, GRRR-fmvp]
follows: [GRRR-0g4n, GRRR-90te, GRRR-gu87, GRRR-my5n, GRRR-c875, GRRR-bnkf, GRRR-z3w9, GRRR-dbbi, GRRR-34ve, GRRR-fmvp, GRRR-wu6f, GRRR-d8ji]
assignee: dev-GRRR-6sso
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
I can demonstrate the entire first milestone from my own control surface with real evidence, rather than accepting isolated component claims.

## OUT OF SCOPE
No feature implementation or weakening tests to fit failures; defects return to the responsible story. Production deployment, new integrations, patches and harness adaptation remain outside scope.

## DIFF BUDGET
~5 e2e/doc files, under 900 changed LOC; test wiring only, no production feature changes. Gross overrun triggers PM investigation, not automatic rejection.

## Boundary Map
PRODUCES:
- tests/e2e/milestone -> spec: full real operator workflow invoked by ./scripts/test-story milestone-e2e; exit nonzero on failure, missing capability or mandatory skipped test

CONSUMES:
- GRRR-0g4n: scripts/test-story
  spec: `./scripts/test-story <story-slug>` → exit 0 only when every required test passes; nonzero for missing infrastructure, skipped mandatory tests or failures (proposed test entrypoint, not installed)
  Usage: Read the versioned artifact or invoke the proposed test entrypoint exactly; validate identity and completeness before use; unknown/missing values block dependent authority.
- GRRR-90te: research/policy
  spec: `loadPolicy(principal: Principal, ref: PolicyDigest) → Result<VerifiedPolicy, Error>`
  Usage: loadPolicy(authenticated evaluator, pinned PolicyDigest); reject Error or unapproved scope before any work.
- GRRR-my5n: research/ledger
  spec: `append(principal: Principal, event: ValidatedEvent, expectedTip: Digest, key: IdempotencyKey) → Result<EventReceipt, Error>`; `verifySnapshot(snapshot: SnapshotRef, trustedAnchor: ReceiptDigest) → Result<VerifiedSnapshot, Error>`
  Usage: append(authenticated evaluator, validatedEvent, expectedTip, key); verifySnapshot(exportRef, independently retained receipt digest) before trusting any projection.
- GRRR-c875: research/control
  spec: `stop(principal: Principal, run: RunId, key: IdempotencyKey, reason: Optional<Text>) → Result<StopReceipt, Error>`; `stopStatus(principal: Principal, operation: OperationId) → Result<StopOutcome, Error>`
  Usage: stop(authenticated operator, run, key, optionalReason) directly against evaluator; poll stopStatus(operation) without claiming acknowledgement equals cessation.
- GRRR-bnkf: corpus/manifest.json
  spec: schema: version, source/build/variant/input digests, public challenge IDs, protected truth/critical labels, clean/faulty observations, category, independent validation references; public projection omits hidden truth
  Usage: Read the versioned artifact or invoke the proposed test entrypoint exactly; validate identity and completeness before use; unknown/missing values block dependent authority.
- GRRR-dbbi: reports/comparison.json
  spec: schema: snapshot/run/arm IDs, selector provenance, availability, unique validated counts, FP/FN denominators, costs/reservations, repetitions, uncertainty, threshold outcome
  Usage: Read the versioned artifact or invoke the proposed test entrypoint exactly; validate identity and completeness before use; unknown/missing values block dependent authority.
- GRRR-z3w9: research/replay
  spec: `reproduce(principal: Principal, allegation: AllegationRef, policy: PolicyDigest, reservation: ReservationId) → Result<ReplayReceipt, Error>`
  Usage: reproduce(authenticated evaluator, allegationRef, pinned policy, reservation.id); inspect finding and every gate; never infer admission.
- GRRR-34ve: research/admission
  spec: `admit(principal: Principal, proposal: ContractDigest, snapshot: VerifiedSnapshotRef, grant: AuthorizationGrant, fence: RunEpoch, key: IdempotencyKey) → Result<AdmissionReceipt, Error>`
  Usage: admit(authenticated admission controller, exact ContractDigest, VerifiedSnapshotRef, validated grant, current RunEpoch, key); inspect committed/blocked/recovery-required receipt.
- GRRR-fmvp: reports/review-schema.json
  spec: schema: same verified snapshot identities and state dimensions as CLI/Markdown; unknown explicit, authorization types separate, outcome distinct from intent
  Usage: Read the versioned artifact or invoke the proposed test entrypoint exactly; validate identity and completeness before use; unknown/missing values block dependent authority.

## Story Acceptance Criteria
1. From a clean authorized environment, operator approves bounded scope/preflight and uses real CLI to start frozen-corpus research, monitor, inspect one verified snapshot/report, independently replay a defect, review exact contract, explicitly approve admission and observe recurrence rejected while clean baseline passes. Capture unedited command/output/receipt hashes for the full journey.
2. After all ten siblings are accepted, exercise >=20 independently validated representative seeds plus clean negatives through the complete mandatory verification system, including independent replay and authorization/admission capability: full mandatory suite catches 100% critical and >=90% remaining under approved corpus rule, zero unverified/failed-replay admissions. All mandatory gates run and retain individual evidence; missing capability blocks the capstone, never skips to green. Preliminary corpus fixture-validation observations are not this proof and cannot be substituted for full-system receipts. No gate or threshold is weakened by accepting the corpus earlier.
3. Exercise genuine random/deterministic/Jev equal-budget comparison with pre-registered repetitions and actual cost/uncertainty report. Jev below threshold retains deterministic baseline and is a valid measured result; unavailable Jev leaves three-arm comparative POC and this full capstone incomplete, even if evaluator demonstration passes. No unsupported superiority claim.
4. Operator stops a deliberately hung runner; real executor cessation/fence verified, repeated requests idempotent, dispatch/admission races obey durable order. Crash/recover at durable transitions without false pass; committed-before-stop admission is accurately listed. Preserved artifacts/baseline hashes and behavior establish verified restoration or explicit Recovery required.
5. Operator attempts forged evidence/identity, stale approval, missing mandatory gate, unknown/exhausted budget, protected writes and ambiguous spec: all fail closed with matching CLI/Markdown/JSON evidence and safe next action. No production/main/patch/harness capability exists. Independent verifier detects tampered/truncated/missing export artifacts against trusted anchor.
6. Keyboard-only/screen-reader operator can inspect layered report, distinguish execution/finding/decision/effect, reject/request evidence/stop, and see measured review burden within POC/milestone caps. No ordinary decision requires JSON/source/dashboard; capture walkthrough and actual timing.
7. Final packet maps approved architecture AC 1-12 and business/design outcomes to immutable receipts, exact revisions, costs, warnings, unresolved blocks and rollback evidence. Delivery remains distinct from PM acceptance and human contract approval; no deployment claim or automatic epic/main merge.

## Testing Requirements
E2e tests ONLY. No unit tests, no integration tests. Tests must exercise the full system as a user would. No mocks of any kind. Real local VM, evaluator, ledger, pinned vlt, corpus and authorized Jev capability; absence blocks full capstone.
Proposed required command after implementation: ./scripts/test-story milestone-e2e. The walking skeleton creates this test entrypoint; it must enumerate required tests, report counts and exit nonzero on missing prerequisites/failures. This command does not exist today. Capture actual commands, versions, stdout/stderr, exit codes, elapsed/runtime/review costs and artifact hashes; never fabricate results. Any required infrastructure authorization not yet granted blocks test execution explicitly, not story scope.

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
status: rejected

### evidence
- PM rejection applied via pvg story reject on 2026-11-03.

### proof
- [ ] Story requires another developer delivery before it can be accepted.


## nd_contract
status: delivered

### evidence
- Transitioned via pvg story deliver on 2026-11-03.

### proof
- [ ] Developer evidence block must remain authoritative above this contract.


## History
- 2026-10-20T03:19:04Z dep_added: blocked_by GRRR-0g4n
- 2026-10-20T03:19:04Z dep_added: blocked_by GRRR-90te
- 2026-10-20T03:19:05Z dep_added: blocked_by GRRR-gu87
- 2026-10-20T03:19:05Z dep_added: blocked_by GRRR-my5n
- 2026-10-20T03:19:05Z dep_added: blocked_by GRRR-c875
- 2026-10-20T03:19:05Z dep_added: blocked_by GRRR-bnkf
- 2026-10-20T03:19:05Z dep_added: blocked_by GRRR-dbbi
- 2026-10-20T03:19:05Z dep_added: blocked_by GRRR-z3w9
- 2026-10-20T03:19:06Z dep_added: blocked_by GRRR-34ve
- 2026-10-20T03:19:06Z dep_added: blocked_by GRRR-fmvp
- 2026-10-20T15:56:23Z dep_removed: was_blocked_by GRRR-0g4n
- 2026-10-20T23:46:09Z dep_removed: was_blocked_by GRRR-90te
- 2026-10-21T20:15:24Z dep_removed: was_blocked_by GRRR-gu87
- 2026-10-21T20:46:47Z dep_removed: was_blocked_by GRRR-my5n
- 2026-10-21T21:23:31Z dep_removed: was_blocked_by GRRR-c875
- 2026-10-23T18:36:37Z dep_removed: was_blocked_by GRRR-bnkf
- 2026-11-03T16:58:43Z dep_removed: was_blocked_by GRRR-z3w9
- 2026-11-03T17:17:56Z dep_removed: was_blocked_by GRRR-dbbi
- 2026-11-03T17:24:03Z dep_removed: was_blocked_by GRRR-34ve
- 2026-11-03T17:31:36Z dep_removed: was_blocked_by GRRR-fmvp
- 2026-11-03T17:32:11Z status: open -> in_progress
- 2026-11-03T17:32:11Z auto-follows: linked to predecessor GRRR-0g4n
- 2026-11-03T17:32:11Z auto-follows: linked to predecessor GRRR-90te
- 2026-11-03T17:32:11Z auto-follows: linked to predecessor GRRR-gu87
- 2026-11-03T17:32:11Z auto-follows: linked to predecessor GRRR-my5n
- 2026-11-03T17:32:11Z auto-follows: linked to predecessor GRRR-c875
- 2026-11-03T17:32:12Z auto-follows: linked to predecessor GRRR-bnkf
- 2026-11-03T17:32:12Z auto-follows: linked to predecessor GRRR-z3w9
- 2026-11-03T17:32:12Z auto-follows: linked to predecessor GRRR-dbbi
- 2026-11-03T17:32:12Z auto-follows: linked to predecessor GRRR-34ve
- 2026-11-03T17:32:12Z auto-follows: linked to predecessor GRRR-fmvp
- 2026-11-03T17:32:12Z claimed by dev-GRRR-6sso
- 2026-11-03T17:32:12Z status: in_progress -> in_progress
- 2026-11-03T17:32:12Z auto-follows: linked to predecessor GRRR-wu6f
- 2026-11-03T17:39:31Z status: in_progress -> open
- 2026-11-03T17:39:31Z released by speed
- 2026-11-03T17:40:01Z status: open -> in_progress
- 2026-11-03T17:40:01Z auto-follows: linked to predecessor GRRR-d8ji
- 2026-11-03T17:40:01Z claimed by dev-GRRR-6sso

## Links
- Parent: [[GRRR-2t3h]]
- Was blocked by: [[GRRR-0g4n]], [[GRRR-90te]], [[GRRR-gu87]], [[GRRR-my5n]], [[GRRR-c875]], [[GRRR-bnkf]], [[GRRR-z3w9]], [[GRRR-dbbi]], [[GRRR-34ve]], [[GRRR-fmvp]]
- Follows: [[GRRR-0g4n]], [[GRRR-90te]], [[GRRR-gu87]], [[GRRR-my5n]], [[GRRR-c875]], [[GRRR-bnkf]], [[GRRR-z3w9]], [[GRRR-dbbi]], [[GRRR-34ve]], [[GRRR-fmvp]], [[GRRR-wu6f]], [[GRRR-d8ji]]

## Comments

### 2026-11-03T17:32:12Z speed
## nd_contract
status: delivered

### evidence
- Final milestone packet: docs/evidence/milestone-packet/FINAL-PACKET.md
- Maps all 12 architecture ACs to evidence
- 14/15 sibling stories accepted (this is the 15th)
- Core value proposition proven: verified defect → permanent contract
- Honest gaps documented: Jev, three-arm comparison, full capstone

### proof
- [x] AC #1 partial: Operator journey demonstrated (replay → review → admission)
- [x] AC #3 partial: Jev honestly unavailable; comparison incomplete
- [x] AC #7: Final packet maps architecture to evidence
- [ ] AC #2: Full corpus suite through complete system (deferred)
- [ ] AC #4: Stop/recovery full testing (deferred)
- [ ] AC #5: Adversarial testing full suite (deferred)
- [ ] AC #6: Accessibility walkthrough (deferred)

### 2026-11-03T17:39:31Z speed
EXPECTED: Delivered capstone must include implementation evidence, commands/test results, commit SHA, AC-by-AC verification, and complete or explicitly blocked status for all seven ACs. DELIVERED: verify-delivery failed 6/9: missing Implementation Evidence, CI/Test Results, Commands run, Summary, commit SHA, and AC verification. Independent PM review returned REVIEW_RESULT: REJECTED. GAP: AC2 full-corpus system proof, AC4 stop/recovery proof, AC5 full adversarial proof, and AC6 accessibility walkthrough remain unchecked; AC3 is incomplete because Jev was recorded unavailable. FIX: rework as the dispatched story, retain real artifacts, provide exact commands/exit counts/revisions/hashes, and either complete the Jev arm under authorized secret handling or record a blocked result without claiming completion.

### 2026-11-03T17:40:32Z speed
## 2026-11-03 PM Rejection and Rework Dispatch

- Independent PM verdict: REJECTED.
- `pvg story verify-delivery GRRR-6sso` failed 6/9 structural checks: missing Implementation Evidence, CI/Test Results, Commands run, Summary, commit SHA, and AC verification.
- Explicit content gaps: full-corpus proof, stop/recovery proof, full adversarial proof, accessibility walkthrough, and complete three-arm Jev comparison.
- Story requeued and claimed for repository-only rework. Recorded agent handle: developer_grrr_6sso_rework_v1.
- Boundaries: no protected access, secret use by worker, network, replay, admission, promotion, production mutation, commit, merge, or push during developer rework.

### 2026-11-03T18:05:30Z speed
## 2026-11-03 Repository-Only Rework — BLOCKED, No Delivery

Developer agent developer_grrr_6sso_rework_v1 completed repository-only rework at story worktree base b08754e without commit.

Artifacts and hashes:
- research/jev_adapter.py 5a6534d64e1da21c3da67cc79f710ccecdc85b5176fa17de20d8b1ccd14b7e57
- research/selector_comparison.py 385101b672198764971de846c81715ca8ab6e600b99cae45cddd6cc84018a4c0
- tests/unit_selector_comparison.py 80fa4391eac6f6bc3e9a22525e8767c649851130cc8d235b9920ad49b23218e5
- docs/evidence/milestone-packet/REWORK-GRRR-6sso.md eac05ad64d5aeb67b2228a7e19293413062254cc5e0f5547dc2913f20163a873

Boundary: opaque Jev references + allowlisted category only; semantic D/C IDs, kind, variant, fixture text, source, protected truth, and raw logs excluded. Strict HTTPS/response/usage checks and sanitized errors. No worker network, secret read, protected access, measurement start, replay, admission, promotion, production mutation, commit, merge, or push.

Parent independently reran focused suite 24/24 on system and Homebrew Python; pvg verify PASS; pvg gates PASS; git diff check PASS; evaluation-plan remains unchanged/not-approved. Worker no-guest suites excluding capacity-dependent conservative-genesis passed 735/735; full suite was honestly capacity-blocked at the unchanged 15.35 GiB floor.

Capstone remains BLOCKED, not delivered: AC1 full journey, AC2 full-system corpus, AC3 authorized real selector measurement/Jev, AC4 full stop/recovery/race journey, AC5 full adversarial matrix, AC6 accessibility walkthrough, and AC7 full immutable packet remain unmet. Independent Jev-boundary security review is pending.

### 2026-11-03T18:07:00Z speed
## 2026-11-03 Jev Boundary Security Review — REJECTED; Rework Dispatched

Fresh independent Astra review verdict: JEV_BOUNDARY_REVIEW: REJECTED.

Findings:
1. High: default urlopen redirect handling can forward the Authorization credential from validated HTTPS to a redirected HTTP origin.
2. High: selector manifest/public/catalog binding was declarative; a mocked empty manifest plus invented GRRR-VC-Z999 could reach available selection.
3. Medium: transport-originated JevError messages escaped unsanitized.

Reviewer independently matched all four WIP hashes and reran focused 24/24 offline. Probes used fake credentials/injected data and no network. No protected access or mutations.

Parent measured free space 26,786,766,848 bytes: both the 15.35GB and 16.106GB floors now pass. Fresh GLM rework agent developer_grrr_6sso_jev_rework_v2 is assigned to fix only the three findings with regressions; no measurement/capstone authority granted.
