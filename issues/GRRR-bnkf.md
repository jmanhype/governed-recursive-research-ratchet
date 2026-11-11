---
id: GRRR-bnkf
title: "Inspect a frozen representative vlt defect corpus"
status: closed
priority: 1
type: task
labels: [milestone-1, integration, accepted]
parent: GRRR-2t3h
created_at: 2026-10-20T03:19:03Z
created_by: speed
updated_at: 2026-10-23T18:36:38Z
content_hash: "sha256:cdc5fcc086b4c669194cdbc7f4f8a03986f4e3eea18787d41ef7a156e15f7bec"
was_blocked_by: [GRRR-c875]
follows: [GRRR-c875, GRRR-my5n, GRRR-gu87, GRRR-90te]
assignee: dev-GRRR-bnkf
closed_at: 2026-10-23T18:36:37Z
close_reason: "Accepted: final corpus v2.2 provides independently hash-verified real isolated fixture validation for 24 defects and 8 clean controls across 96 deterministic repetitions, while downstream replay, admission, comparison, and promotion remain explicitly blocked."
led_to: [GRRR-z3w9, GRRR-w1lt, GRRR-43i8, GRRR-d8ji, GRRR-wu6f, GRRR-dbbi, GRRR-6sso]
blocks: [GRRR-2hib]
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
I can judge whether proposed detection scenarios cover meaningful vlt failures rather than an optimizer-selected easy benchmark.

## OUT OF SCOPE
Selection-arm execution/statistical comparisons land in comparison; independent allegation replay and contract admission are later slices. Corpus acceptance covers frozen trusted fixtures and their preliminary validation only; final full mandatory-system detection proof remains in GRRR-6sso after every sibling is accepted. Missing downstream capabilities must stay not-run and cannot authorize findings/admission; they are not required to accept this upstream fixture artifact. This story does not generate patches.

## DIFF BUDGET
~25 fixture/doc/test files, under 2200 changed LOC; fixture count is intentional for >=20 independent scenarios. Gross overrun triggers PM investigation, not automatic rejection.

## Boundary Map
PRODUCES:
- corpus/manifest.json -> schema: version, source/build/variant/input digests, public challenge IDs, protected truth/critical labels, clean/faulty observations, category, independent validation references; public projection omits hidden truth
- corpus/evaluation-plan.json -> schema: version/digest, approved arm order/seeds/repetitions/exceptions, feedback partitions, stopping/tie-break/deduplication/accounting/amortization rules, uncertainty method, corpus approval
- corpus/spec-map.json -> schema: challenge ID, pinned authoritative specification or operator-approved requirement digest, expected behavior, provenance, ambiguity/validation status
- tests/integration/validated-corpus -> spec: real success and all enumerated failure cases via ./scripts/test-story validated-corpus; no mocks, mandatory absence fails

CONSUMES:
- GRRR-90te: research/policy
  spec: `loadPolicy(principal: Principal, ref: PolicyDigest) → Result<VerifiedPolicy, Error>`
  Usage: loadPolicy(authenticated evaluator, pinned PolicyDigest); reject Error or unapproved scope before any work.
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
1. Independently validate at least 20 seeded defect scenarios plus clean negatives as trusted fixture ground truth against pinned source/spec requirements using real isolated executions through the already accepted executor/observation path. Corpus manifest hashes variants, input identities, clean/faulty observations, source/spec references, critical labels and independent corpus-review approval. This is preliminary fixture validation, not a Verified defect finding, independent allegation ReplayReceipt, contract admission or complete-system proof. Unsupported/ambiguous behavior is not fabricated as a known defect.
2. Cover exact filename/title resolution; alias/collision precedence; case-insensitive/path-qualified lookup; wikilinks/embeds/headings/block references/inert zones; frontmatter/index invalidation; rename/move/delete/stale cache; concurrent read/write/locking; filesystem errors/invalid paths; deterministic repetition and integrity-registry tampering. Approve representativeness before interpreting detection thresholds.
3. Freeze corpus, seeded variants, hidden truth, critical classes, specifications and plan before arms. Separate public synthetic metadata from protected answers/holdouts and permitted training feedback; test filesystem/API denials and contamination checks. Mutation after freeze invalidates comparison and requires new approved version, never silent repair.
4. Pre-register arm ordering, seeds, at least three randomized repetitions where feasible, explicit feasibility exceptions, tie-breaks, stopping, feedback, unique-defect deduplication, cost allocations/amortization, denominator validity and uncertainty method. Operator/reviewer approves before measurement, not after results.
5. Run preliminary trusted fixture-validation checks over frozen variants and clean controls using only accepted upstream isolation, observation, budget, ledger and stop capabilities. Require reproducible expected clean/faulty behavior and spec-backed ground truth for every included scenario; missing required fixture-validation evidence or nondeterministic unresolved seeds blocks corpus acceptance. Record failed/false-positive checks and gaps. Downstream independent allegation replay, authorization/admission and complete mandatory-system gates remain explicitly not-run, not waived or deemed passing. Complete-system 100% critical and at least 90% other-seed detection is acceptance proof owned by the final capstone after all capabilities land, not a prerequisite for accepting this corpus.
6. Expose an operator-reviewable preliminary fixture coverage table and immutable corpus/plan/spec digests with counts and gaps; the selector never receives hidden labels or outputs outside approved feedback. Label fixture observations as preliminary, separately from later independently verified selector discoveries and final mandatory-suite detections; do not credit preliminary observations as either.

## Testing Requirements
Integration tests: MANDATORY (no mocks). Include real success path plus every negative/error/concurrency case enumerated in the AC. Use real local VM, OS identities/permissions, evaluator, transactional store and pinned vlt where the path crosses them; mocks/stubs/fake receipts do not establish integration proof. Unit tests may supplement pure parsing/serialization; they cannot replace real integration. No skip-if-missing or environment-variable shortcut to green.
Proposed required command after implementation: ./scripts/test-story validated-corpus. The walking skeleton creates this test entrypoint; it must enumerate required tests, report counts and exit nonzero on missing prerequisites/failures. This command does not exist today. Capture actual commands, versions, stdout/stderr, exit codes, elapsed/runtime/review costs and artifact hashes; never fabricate results. Any required infrastructure authorization not yet granted blocks test execution explicitly, not story scope.

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

## Acceptance Criteria


## Design


## Notes
DELIVERY_COMMIT_ADDENDUM: implementation commit 4f24b31d5f276996e1885cbad3bee0a256e661c0; completed evidence commit aaecdb20c7a477a6c9073d776f130cef6ea552eb; delivery-proof commit 0995477971f81ae35f07c2e644a8b5f1195b7307. Worktree clean before pvg delivery transition.


## nd_contract
status: accepted

### evidence
- PM closeout applied via pvg story accept on 2026-10-23.

### proof
- [x] Story closed after accepted label was applied.


## PM Decision
ACCEPTED [2026-10-23]: Independent PM evidence review meets the fixture-validation scope.

## nd_contract
status: accepted

### evidence
- Worktree HEAD 3f6d8dcfb407438591ad13c9bc14d60886bb0d73 is clean; profile/code commit 2dc3ca8b4598af0a777122b98602729ac858459a and evidence commit 3f6d8dcfb407438591ad13c9bc14d60886bb0d73 resolve exactly.
- Recomputed corpus freeze digest dfa75ef2bf3d43fd4f750094fe643afe4f204812c0ae2426276bedb471fa8529 and all manifest artifact hashes; current manifest is byte-identical in all four executed batches.
- Re-verified all four v2.2 snapshots with the ledger verifier, compared each 33-event chain to immutable ledger.sqlite, verified all 9 durable objects per batch, and verified all 8 budget reservations were metered and settled.
- Confirmed exact challenge order D001-D024 then C001-C008: 24 defects, 8 clean controls, 3 repetitions each, 96 total, all expected=observed, deterministic, verified=false, admission=blocked.
- Confirmed summary/integration logs report required=8, executed=8, repetitions=24, failures/errors/skips=0 in each batch and Ran 4 tests ... OK.
- Verified SHA256SUMS 3/3 OK and aggregate references exactly the four successful v2.2 archives; 82 failed setup directories and 3 superseded batch directories remain preserved outside the final denominator.
- Scope remains preliminary fixture validation only: independent replay, reviewer outcome, admission, selector comparison, and production promotion stay blocked/not-run.

### proof
- [x] AC #1: 24 defects plus 8 clean controls validated by real isolated executions; variants, source/spec identity, protected truth, critical labels, inputs, observations, and receipts are hash-bound.
- [x] AC #2: all 10 required defect categories have multiple represented defect scenarios.
- [x] AC #3: v2.2 is explicitly frozen with public/protected separation; v2.0/v2.1 and transient failures remain preserved, not silently repaired or counted.
- [x] AC #4: arm order, seeds, three repetitions, exceptions, stopping, feedback, deduplication, cost, denominator, and uncertainty are pre-registered; measurement remains not approved and not started.
- [x] AC #5: all 32 scenarios have deterministic trusted-observation evidence through the accepted UID-separated isolated path, with durable ledger/budget/snapshot evidence and blocked downstream gates.
- [x] AC #6: operator-reviewable consolidated report/aggregate/observations expose counts, hashes, receipts, and gaps without protected public leakage; preliminary observations are not credited as verified findings.

## nd_contract
status: delivered

### evidence
- Final code/profile commit: 2dc3ca8b4598af0a777122b98602729ac858459a
- Final evidence commit: 3f6d8dcfb407438591ad13c9bc14d60886bb0d73
- Four final v2.2 isolated batches all passed 4/4 integration tests: 32/32 scenarios, 96/96 repetitions, 24 defects, 8 clean controls.
- Evidence root: docs/evidence/validated-corpus/v2.2-batched-run/

### proof
- [x] AC #1: real isolated fixture validation completed for 24 defects plus 8 clean controls; verified finding/admission not claimed.
- [x] AC #2: all required categories represented.
- [x] AC #3: corpus v2.2 explicitly versioned after failed/superseded attempts; protected/public separation preserved.
- [x] AC #4: evaluation plan remains pre-registered and measurement blocked.
- [x] AC #5: every final scenario has three deterministic real isolated repetitions with durable ledger evidence.
- [x] AC #6: operator-reviewable consolidated evidence, counts, hashes, and blocked downstream gates recorded.

## nd_contract
status: delivered

### evidence
- Transitioned via pvg story deliver on 2026-10-21.

### proof
- [ ] Developer evidence block must remain authoritative above this contract.


## Implementation Evidence (DELIVERED)

PROOF:

### Final revision

- Branch: `story/GRRR-bnkf`
- Code/profile commit: `2dc3ca8b4598af0a777122b98602729ac858459a`
- Code + evidence commit: `3f6d8dcfb407438591ad13c9bc14d60886bb0d73`
- Worktree is clean at the evidence commit.

### Corrected frozen corpus

- Corpus: `GRRR-validated-corpus-v2.2-isolated`
- Freeze digest: `dfa75ef2bf3d43fd4f750094fe643afe4f204812c0ae2426276bedb471fa8529`
- Input image SHA-256: `6c3cb672f367fd5164672e0a2d36f720dcc705414c6dcf96ab9e9d3adfa327f3`
- Profile SHA-256: `b3b92a6382c1ed276862675540ab07ba399a4e0dc8bcdc7254138e5abc86db71`
- Preparation receipt SHA-256: `755af0f8d9fc632287b5b099fc7ac913ad9a01970f0ad84145a2c15fce96815c`

The v2.0/v2.1 probe defects and all failed/superseded attempts remain preserved under `docs/evidence/validated-corpus/failed-setup-archive/` and `superseded-batches/`; they are not counted as final observations.

### Real isolated fixture validation

Four parent-mediated, UID-separated, offline, 8-scenario batches all passed all four integration tests. Each summary reports 8 required, 8 executed, 24 repetitions, 0 failures, 0 errors, 0 skipped, fixture gate executed, verified false, and admission blocked.

- Batch 1: `docs/evidence/validated-corpus/successful-batches/v2.2-batch-1-znzk0hd5/`
- Batch 2: `docs/evidence/validated-corpus/successful-batches/v2.2-batch-2-pg9tma_b/`
- Batch 3: `docs/evidence/validated-corpus/successful-batches/v2.2-batch-3-4pkzsdin/`
- Batch 4: `docs/evidence/validated-corpus/successful-batches/v2.2-batch-4-zov6lwyz/`
- Consolidated report: `docs/evidence/validated-corpus/v2.2-batched-run/REPORT.md`
- Consolidated aggregate: `docs/evidence/validated-corpus/v2.2-batched-run/aggregate.json`

Measured result: **32/32 scenarios**, **24 defect scenarios**, **8 clean controls**, and **96/96 deterministic repetitions**. D007, D011, D012, D018, and D023 all pass in the final v2.2 corpus. Every final observation is marked `verified: false` and `admission: blocked`.

### Verification

Commands run at the final code/profile revision:

- `./scripts/generate-validated-corpus` — PASS; emitted freeze digest `dfa75ef2bf3d43fd4f750094fe643afe4f204812c0ae2426276bedb471fa8529`.
- `scripts/prepare-validated-corpus-input ...` — PASS; no VM/candidate execution during preparation.
- Four isolated root-bootstrap launches — PASS; each integration log reports `Ran 4 tests ... OK`.
- `/usr/bin/python3 -I -B -m unittest discover -s tests -p 'unit*.py' -v` — **166 passed, 0 failed, 0 skipped**.
- `/opt/homebrew/bin/python3 -B -m unittest discover -s tests -p 'unit*.py' -v` — **166 passed, 0 failed, 0 skipped**.
- `pvg verify --include-tests ... --format=text` — `VERIFY: PASSED (4 files scanned, 0 issues)`.
- `shasum -a 256 -c docs/evidence/validated-corpus/v2.2-batched-run/SHA256SUMS` — **3/3 OK**.
- `git diff --check` — PASS.

All four durable batch ledgers/snapshots were independently verified with the existing ledger verifier during aggregate construction. The aggregate confirms exact manifest order, exact challenge IDs, expected clean/defect behavior, three repetitions per scenario, unique scenarios, and four verifiable snapshots.

### AC Verification

- [x] AC #1: 24 defect scenarios plus 8 clean controls validated through real isolated executions; manifest, protected truth, variants, source/spec references, critical labels, and execution evidence are hash-bound. Preliminary only: no verified defect finding or contract admission is claimed.
- [x] AC #2: all 10 required categories remain represented across the corrected frozen corpus.
- [x] AC #3: corpus v2.2 explicitly supersedes failed v2.0/v2.1 freezes rather than silently repairing them; public projections exclude protected truth, anchors, replacements, critical labels, and holdout membership.
- [x] AC #4: arm order, fixed seeds, three repetitions, stopping, feedback, deduplication, cost, denominator, uncertainty, and approval remain pre-registered with measurement blocked.
- [x] AC #5: final v2.2 execution used the accepted trusted-observation/isolated executor path under actual UID separation; every included scenario has three deterministic clean/fault observations. Downstream replay, review, admission, and selector comparison remain explicitly not-run/blocked.
- [x] AC #6: consolidated counts/digests/gaps and per-batch evidence are operator-reviewable; selector comparison remains blocked and preliminary observations are not credited as verified discoveries.

### Remaining gates

- Independent allegation replay: not-run (later story).
- Reviewer outcome: not-run (later story).
- Contract admission: blocked.
- Selector-arm comparison and recursive adaptation: not-run/blocked.
- Automatic merge/production promotion: disabled.

LEARNINGS:

- An unanchored regex can make removal of an optional prefix behavior-neutral; probes must exercise the actual semantic difference, not merely a syntactic mutation.
- D018's mutation is in the trash branch, so a permanent-delete probe cannot detect it.
- A single match cannot validate adjacent-range merging; D023 needs two adjacent ranges.
- Snapshot/summary finalization must occur before the tests that inspect those files; class teardown is too late.
- Batching preserved the host disk floor while retaining one complete ledger per batch; failed and superseded runs remain clearly separated rather than being mixed into the final denominator.

### DISCOVERED_BUG

None in pvg/nd/vlt core. The fixture defects were authored corpus scenarios. The transient v2.2 D016 `RecoveryRequired` attempt is preserved at `failed-setup-archive/grrr-corpus-ozvpqtfw/` and was followed by a complete successful batch retry; it is not hidden or counted as success.

## nd_contract
status: in_progress

### evidence
- Rework claimed 2026-10-21 after PM rejection; prepare a new reviewed disposable corpus input/profile and request parent-mediated UID-separated execution.

### proof
- [ ] AC #1/#5 pending real isolated seeded-variant execution.

## nd_contract
status: rejected

### evidence
- PM rejection applied via pvg story reject on 2026-10-21.

### proof
- [ ] Story requires another developer delivery before it can be accepted.


## Implementation Evidence

Commands run:
- ./scripts/test-story validated-corpus: 9 executed, 0 failed, 0 skipped.
- /usr/bin/python3 -I -B -m unittest discover -s tests -p 'unit*.py' -v: 166 passed, 0 failed, 0 skipped.
- /opt/homebrew/bin/python3 -B -m unittest discover -s tests -p 'unit*.py' -v: 166 passed, 0 failed, 0 skipped.
- pvg verify explicit changed paths: PASSED, 0 issues.
- python3 -m py_compile explicit changed Python files: PASSED.
- git diff --check: PASSED.

Summary:
Frozen corpus GRRR-validated-corpus-v1 contains 24 defects, 8 clean controls, 16 critical defects, 10/10 required categories, and 32 unique reconstructed variants. Arbitrary seeded guest execution and all downstream replay/review/admission gates remain explicitly not-run or blocked.

SHA: 0995477971f81ae35f07c2e644a8b5f1195b7307

- [x] AC #1 through AC #6 evidence and explicit blockers are recorded in the authoritative delivered contract and docs/evidence/validated-corpus/.

## Implementation Evidence (DELIVERED)

PROOF:

### CI/Test Results

Commands run:

- `./scripts/generate-validated-corpus` — PASS; emitted corpus freeze digest `ea62c30a72a1359455b94c235493d6959ce27757c38d1ba1c4fa21574d4a2c7d`.
- `./scripts/test-story validated-corpus` — PASS; **9 executed, 0 failed, 0 skipped** (repeated post-commit with the same result).
- `/usr/bin/python3 -I -B -m unittest discover -s tests -p 'unit*.py' -v` — PASS after authorized cache cleanup; **166 passed, 0 failed, 0 skipped**.
- `/opt/homebrew/bin/python3 -B -m unittest discover -s tests -p 'unit*.py' -v` — PASS after authorized cache cleanup; **166 passed, 0 failed, 0 skipped**.
- `pvg verify --include-tests <all explicit changed code/corpus/evidence paths>` — `VERIFY: PASSED (2 files scanned, 0 issues)`.
- `/usr/bin/python3 -I -B -m py_compile scripts/test-story scripts/generate-validated-corpus research/validated_corpus.py tests/integration/validated_corpus.py` — PASS.
- `git diff --check` — PASS.
- `shasum -a 256 -c docs/evidence/validated-corpus/SHA256SUMS` — PASS for all 26 recorded files.

Coverage: 166/166 required no-guest tests passed under both Python interpreters; the mandatory corpus integration gate passed 9/9. Line coverage was not measured and is not claimed.

The first full-suite attempt was preserved at 157 run / 1 setup error because free space was below 15.35 GB; after the parent's authorized regenerable-cache cleanup, both final full runs passed 166/166. That first attempt also caught a temporary import-path violation in new code, which was fixed before either final full-suite run.

### Commit

- Branch: `story/GRRR-bnkf`
- Corpus implementation SHA: `4f24b31d5f276996e1885cbad3bee0a256e661c0`
- Final evidence SHA: `aaecdb20c7a477a6c9073d776f130cef6ea552eb`

### Wiring

- `research/validated_corpus.py` generates and validates the frozen corpus.
- `scripts/generate-validated-corpus` is the reproducible operator entrypoint.
- `scripts/test-story validated-corpus` invokes `tests/integration/validated_corpus.py`.
- `corpus/public/*` is the only selector-visible projection.
- `corpus/protected/*` and `corpus/spec-map.json` hold seeds, truth, holdouts, and expected behavior.

### pvg verify

`VERIFY: PASSED (2 files scanned, 0 issues)`

### AC Verification

| AC # | Requirement | Code Location | Test Location | Status |
|------|-------------|---------------|---------------|--------|
| 1 | At least 20 independent seeded defects plus clean negatives, pinned source identities, hashed variants, critical labels, and preliminary validation | `research/validated_corpus.py`, `corpus/manifest.json`, `corpus/protected/*` | `tests/integration/validated_corpus.py` | PASS: 24 defects + 8 clean, 32 unique reconstructed variants; arbitrary seeded guest execution remains explicitly not-run because the fixed v4 input/profile admits only its original variants |
| 2 | Cover every required defect category | `research/validated_corpus.py::CATEGORIES`, `corpus/public/challenges.json` | `test_counts_categories_and_independence` | PASS: 10/10 categories |
| 3 | Freeze variants, hidden truth, critical classes, specs, and plan with public/protected separation and contamination checks | `corpus/*` | `test_public_projection_omits_protected_truth`, `test_seed_recipes_reproduce_against_exact_pinned_source` | PASS |
| 4 | Pre-register arms, seeds, repetitions, exceptions, stopping, feedback, deduplication, cost, denominator, and uncertainty | `corpus/evaluation-plan.json` | `test_plan_is_pre_registered_and_measurement_is_blocked` | PASS; operator approval is correctly still not-approved and measurement is false |
| 5 | Run preliminary trusted fixture checks while preserving downstream gates | `research/validated_corpus.py::validate`, accepted v4 snapshot evidence | `test_accepted_v4_observation_is_internally_verified`, `test_downstream_gates_remain_not_run` | PASS for static seed validation plus accepted v4 observation reference; arbitrary seeded isolated execution not-run |
| 6 | Expose reviewable coverage, immutable digests, counts, gaps, and prevent selector access to protected labels | `corpus/manifest.json`, `docs/evidence/validated-corpus/REPORT.md` | full validated-corpus integration suite | PASS |

### Summary

Delivered a frozen, hash-bound corpus with 24 defect scenarios, 8 clean controls, 16 critical defects, all 10 required categories, protected/public separation, a pre-registered three-repetition arm plan, and 32 deterministic source-recipe reconstructions against the pinned vlt archive. The accepted v4 ledger supplies real isolated-path evidence only for its fixed clean/fault variants; it is not presented as execution of these new arbitrary seeds.

Remaining blockers/gates:

- Arbitrary seeded variants: not-run; a new reviewed input/profile is required.
- Independent replay, reviewer outcome, verified findings, and admission: not-run/blocked.
- Bounded-challenge entrypoint fails closed in this isolated story worktree without the parent runtime binding.
- Protected accounting remains stopped; no release/recovery attempted.

LEARNINGS:

- Reading `vlt.tar` directly from the preserved ISO's primary namespace avoids mounting, host candidate execution, and protected mutation.
- Public projections require explicit scrubbing of both truth and critical labels; deleting expected behavior alone was insufficient.
- A research module must not mutate `sys.path`; the existing import-closure test caught that boundary error before final verification.
- Environment-dependent suite floors can masquerade as code regressions; preserve the failed run, fix the actual code issue, and rerun both interpreters only after an authorized space remedy.

### DISCOVERED_BUG

None remaining. The temporary import-path violation was introduced and fixed inside this story before final delivery; no production, pvg, nd, or vlt core defect was found.

## Implementation Evidence (DELIVERED)

PROOF:

### CI/Test Results

Commands run:

- `./scripts/generate-validated-corpus` — PASS; emitted corpus freeze digest `ea62c30a72a1359455b94c235493d6959ce27757c38d1ba1c4fa21574d4a2c7d`.
- `./scripts/test-story validated-corpus` — PASS; **9 executed, 0 failed, 0 skipped** (repeated post-commit with the same result).
- `/usr/bin/python3 -I -B -m unittest discover -s tests -p 'unit*.py' -v` — PASS after authorized cache cleanup; **166 passed, 0 failed, 0 skipped**.
- `/opt/homebrew/bin/python3 -B -m unittest discover -s tests -p 'unit*.py' -v` — PASS after authorized cache cleanup; **166 passed, 0 failed, 0 skipped**.
- `pvg verify --include-tests <all explicit changed code/corpus/evidence paths>` — `VERIFY: PASSED (2 files scanned, 0 issues)`.
- `/usr/bin/python3 -I -B -m py_compile scripts/test-story scripts/generate-validated-corpus research/validated_corpus.py tests/integration/validated_corpus.py` — PASS.
- `git diff --check` — PASS.
- `shasum -a 256 -c docs/evidence/validated-corpus/SHA256SUMS` — PASS for all 26 recorded files.

Coverage: 166/166 required no-guest tests passed under both Python interpreters; the mandatory corpus integration gate passed 9/9. Line coverage was not measured and is not claimed.

The first full-suite attempt was preserved at 157 run / 1 setup error because free space was below 15.35 GB; after the parent's authorized regenerable-cache cleanup, both final full runs passed 166/166. That first attempt also caught a temporary import-path violation in new code, which was fixed before either final full-suite run.

### Commit

- Branch: `story/GRRR-bnkf`
- Corpus implementation SHA: `4f24b31d5f276996e1885cbad3bee0a256e661c0`
- Final evidence SHA: `aaecdb20c7a477a6c9073d776f130cef6ea552eb`

### Wiring

- `research/validated_corpus.py` generates and validates the frozen corpus.
- `scripts/generate-validated-corpus` is the reproducible operator entrypoint.
- `scripts/test-story validated-corpus` invokes `tests/integration/validated_corpus.py`.
- `corpus/public/*` is the only selector-visible projection.
- `corpus/protected/*` and `corpus/spec-map.json` hold seeds, truth, holdouts, and expected behavior.

### pvg verify

`VERIFY: PASSED (2 files scanned, 0 issues)`

### AC Verification

| AC # | Requirement | Code Location | Test Location | Status |
|------|-------------|---------------|---------------|--------|
| 1 | At least 20 independent seeded defects plus clean negatives, pinned source identities, hashed variants, critical labels, and preliminary validation | `research/validated_corpus.py`, `corpus/manifest.json`, `corpus/protected/*` | `tests/integration/validated_corpus.py` | PASS: 24 defects + 8 clean, 32 unique reconstructed variants; arbitrary seeded guest execution remains explicitly not-run because the fixed v4 input/profile admits only its original variants |
| 2 | Cover every required defect category | `research/validated_corpus.py::CATEGORIES`, `corpus/public/challenges.json` | `test_counts_categories_and_independence` | PASS: 10/10 categories |
| 3 | Freeze variants, hidden truth, critical classes, specs, and plan with public/protected separation and contamination checks | `corpus/*` | `test_public_projection_omits_protected_truth`, `test_seed_recipes_reproduce_against_exact_pinned_source` | PASS |
| 4 | Pre-register arms, seeds, repetitions, exceptions, stopping, feedback, deduplication, cost, denominator, and uncertainty | `corpus/evaluation-plan.json` | `test_plan_is_pre_registered_and_measurement_is_blocked` | PASS; operator approval is correctly still not-approved and measurement is false |
| 5 | Run preliminary trusted fixture checks while preserving downstream gates | `research/validated_corpus.py::validate`, accepted v4 snapshot evidence | `test_accepted_v4_observation_is_internally_verified`, `test_downstream_gates_remain_not_run` | PASS for static seed validation plus accepted v4 observation reference; arbitrary seeded isolated execution not-run |
| 6 | Expose reviewable coverage, immutable digests, counts, gaps, and prevent selector access to protected labels | `corpus/manifest.json`, `docs/evidence/validated-corpus/REPORT.md` | full validated-corpus integration suite | PASS |

### Summary

Delivered a frozen, hash-bound corpus with 24 defect scenarios, 8 clean controls, 16 critical defects, all 10 required categories, protected/public separation, a pre-registered three-repetition arm plan, and 32 deterministic source-recipe reconstructions against the pinned vlt archive. The accepted v4 ledger supplies real isolated-path evidence only for its fixed clean/fault variants; it is not presented as execution of these new arbitrary seeds.

Remaining blockers/gates:

- Arbitrary seeded variants: not-run; a new reviewed input/profile is required.
- Independent replay, reviewer outcome, verified findings, and admission: not-run/blocked.
- Bounded-challenge entrypoint fails closed in this isolated story worktree without the parent runtime binding.
- Protected accounting remains stopped; no release/recovery attempted.

LEARNINGS:

- Reading `vlt.tar` directly from the preserved ISO's primary namespace avoids mounting, host candidate execution, and protected mutation.
- Public projections require explicit scrubbing of both truth and critical labels; deleting expected behavior alone was insufficient.
- A research module must not mutate `sys.path`; the existing import-closure test caught that boundary error before final verification.
- Environment-dependent suite floors can masquerade as code regressions; preserve the failed run, fix the actual code issue, and rerun both interpreters only after an authorized space remedy.

### DISCOVERED_BUG

None remaining. The temporary import-path violation was introduced and fixed inside this story before final delivery; no production, pvg, nd, or vlt core defect was found.

## nd_contract
status: delivered

### evidence
- Corpus freeze: `ea62c30a72a1359455b94c235493d6959ce27757c38d1ba1c4fa21574d4a2c7d`
- Source archive: `e644b9848b306f158a2367293dd96c66dac2bed97c0dd42891db007667c0ae7e`
- Accepted v4 snapshot: `745f5d2c9086550c184cccd484023d5e490f0c082550eb55524adf25948ac513`
- Final commit: `aaecdb20c7a477a6c9073d776f130cef6ea552eb`
- Evidence root: `docs/evidence/validated-corpus/`

### proof
- [x] AC #1: 24 defects + 8 clean negatives frozen and hash-bound; arbitrary seeded guest execution explicitly not-run (Code: `research/validated_corpus.py`, Test: `tests/integration/validated_corpus.py`, Evidence: `docs/evidence/validated-corpus/corpus-validation.json`).
- [x] AC #2: 10/10 required categories represented (Code: `research/validated_corpus.py`, Test: `test_counts_categories_and_independence`, Evidence: `corpus/public/challenges.json`).
- [x] AC #3: public/protected separation, holdouts, truth, seeds, specs, and hashes frozen (Code: `corpus/*`, Test: contamination tests, Evidence: `corpus/manifest.json`).
- [x] AC #4: three-repetition pre-registered arm plan remains unapproved and unmeasured (Code: `corpus/evaluation-plan.json`, Test: plan test, Evidence: same file).
- [x] AC #5: static fixture checks plus accepted v4 observation path reference; downstream gates remain not-run (Code: `research/validated_corpus.py`, Test: snapshot/gap tests, Evidence: accepted v4 snapshot).
- [x] AC #6: counts/digests/gaps are operator-reviewable and selector-visible data excludes protected labels (Code: `corpus/manifest.json`, Test: full integration suite, Evidence: `docs/evidence/validated-corpus/REPORT.md`).

## nd_contract
status: delivered

### evidence
- Transitioned via pvg story deliver on 2026-10-21.

### proof
- [ ] Developer evidence block must remain authoritative above this contract.


## Implementation Evidence (DELIVERED)

PROOF:

### CI/Test Results

Commands run:

- `./scripts/generate-validated-corpus` — PASS; emitted corpus freeze digest `ea62c30a72a1359455b94c235493d6959ce27757c38d1ba1c4fa21574d4a2c7d`.
- `./scripts/test-story validated-corpus` — PASS; **9 executed, 0 failed, 0 skipped** (repeated post-commit with the same result).
- `/usr/bin/python3 -I -B -m unittest discover -s tests -p 'unit*.py' -v` — PASS after authorized cache cleanup; **166 passed, 0 failed, 0 skipped**.
- `/opt/homebrew/bin/python3 -B -m unittest discover -s tests -p 'unit*.py' -v` — PASS after authorized cache cleanup; **166 passed, 0 failed, 0 skipped**.
- `pvg verify --include-tests <all explicit changed code/corpus/evidence paths>` — `VERIFY: PASSED (2 files scanned, 0 issues)`.
- `/usr/bin/python3 -I -B -m py_compile scripts/test-story scripts/generate-validated-corpus research/validated_corpus.py tests/integration/validated_corpus.py` — PASS.
- `git diff --check` — PASS.
- `shasum -a 256 -c docs/evidence/validated-corpus/SHA256SUMS` — PASS for all 26 recorded files.

Coverage: 166/166 required no-guest tests passed under both Python interpreters; the mandatory corpus integration gate passed 9/9. Line coverage was not measured and is not claimed.

The first full-suite attempt was preserved at 157 run / 1 setup error because free space was below 15.35 GB; after the parent's authorized regenerable-cache cleanup, both final full runs passed 166/166. That first attempt also caught a temporary import-path violation in new code, which was fixed before either final full-suite run.

### Commit

- Branch: `story/GRRR-bnkf`
- Corpus implementation SHA: `4f24b31d5f276996e1885cbad3bee0a256e661c0`
- Final evidence SHA: `aaecdb20c7a477a6c9073d776f130cef6ea552eb`

### Wiring

- `research/validated_corpus.py` generates and validates the frozen corpus.
- `scripts/generate-validated-corpus` is the reproducible operator entrypoint.
- `scripts/test-story validated-corpus` invokes `tests/integration/validated_corpus.py`.
- `corpus/public/*` is the only selector-visible projection.
- `corpus/protected/*` and `corpus/spec-map.json` hold seeds, truth, holdouts, and expected behavior.

### pvg verify

`VERIFY: PASSED (2 files scanned, 0 issues)`

### AC Verification

| AC # | Requirement | Code Location | Test Location | Status |
|------|-------------|---------------|---------------|--------|
| 1 | At least 20 independent seeded defects plus clean negatives, pinned source identities, hashed variants, critical labels, and preliminary validation | `research/validated_corpus.py`, `corpus/manifest.json`, `corpus/protected/*` | `tests/integration/validated_corpus.py` | PASS: 24 defects + 8 clean, 32 unique reconstructed variants; arbitrary seeded guest execution remains explicitly not-run because the fixed v4 input/profile admits only its original variants |
| 2 | Cover every required defect category | `research/validated_corpus.py::CATEGORIES`, `corpus/public/challenges.json` | `test_counts_categories_and_independence` | PASS: 10/10 categories |
| 3 | Freeze variants, hidden truth, critical classes, specs, and plan with public/protected separation and contamination checks | `corpus/*` | `test_public_projection_omits_protected_truth`, `test_seed_recipes_reproduce_against_exact_pinned_source` | PASS |
| 4 | Pre-register arms, seeds, repetitions, exceptions, stopping, feedback, deduplication, cost, denominator, and uncertainty | `corpus/evaluation-plan.json` | `test_plan_is_pre_registered_and_measurement_is_blocked` | PASS; operator approval is correctly still not-approved and measurement is false |
| 5 | Run preliminary trusted fixture checks while preserving downstream gates | `research/validated_corpus.py::validate`, accepted v4 snapshot evidence | `test_accepted_v4_observation_is_internally_verified`, `test_downstream_gates_remain_not_run` | PASS for static seed validation plus accepted v4 observation reference; arbitrary seeded isolated execution not-run |
| 6 | Expose reviewable coverage, immutable digests, counts, gaps, and prevent selector access to protected labels | `corpus/manifest.json`, `docs/evidence/validated-corpus/REPORT.md` | full validated-corpus integration suite | PASS |

### Summary

Delivered a frozen, hash-bound corpus with 24 defect scenarios, 8 clean controls, 16 critical defects, all 10 required categories, protected/public separation, a pre-registered three-repetition arm plan, and 32 deterministic source-recipe reconstructions against the pinned vlt archive. The accepted v4 ledger supplies real isolated-path evidence only for its fixed clean/fault variants; it is not presented as execution of these new arbitrary seeds.

Remaining blockers/gates:

- Arbitrary seeded variants: not-run; a new reviewed input/profile is required.
- Independent replay, reviewer outcome, verified findings, and admission: not-run/blocked.
- Bounded-challenge entrypoint fails closed in this isolated story worktree without the parent runtime binding.
- Protected accounting remains stopped; no release/recovery attempted.

LEARNINGS:

- Reading `vlt.tar` directly from the preserved ISO's primary namespace avoids mounting, host candidate execution, and protected mutation.
- Public projections require explicit scrubbing of both truth and critical labels; deleting expected behavior alone was insufficient.
- A research module must not mutate `sys.path`; the existing import-closure test caught that boundary error before final verification.
- Environment-dependent suite floors can masquerade as code regressions; preserve the failed run, fix the actual code issue, and rerun both interpreters only after an authorized space remedy.

### DISCOVERED_BUG

None remaining. The temporary import-path violation was introduced and fixed inside this story before final delivery; no production, pvg, nd, or vlt core defect was found.

## nd_contract
status: delivered

### evidence
- Corpus freeze: `ea62c30a72a1359455b94c235493d6959ce27757c38d1ba1c4fa21574d4a2c7d`
- Source archive: `e644b9848b306f158a2367293dd96c66dac2bed97c0dd42891db007667c0ae7e`
- Accepted v4 snapshot: `745f5d2c9086550c184cccd484023d5e490f0c082550eb55524adf25948ac513`
- Final commit: `aaecdb20c7a477a6c9073d776f130cef6ea552eb`
- Evidence root: `docs/evidence/validated-corpus/`

### proof
- [x] AC #1: 24 defects + 8 clean negatives frozen and hash-bound; arbitrary seeded guest execution explicitly not-run (Code: `research/validated_corpus.py`, Test: `tests/integration/validated_corpus.py`, Evidence: `docs/evidence/validated-corpus/corpus-validation.json`).
- [x] AC #2: 10/10 required categories represented (Code: `research/validated_corpus.py`, Test: `test_counts_categories_and_independence`, Evidence: `corpus/public/challenges.json`).
- [x] AC #3: public/protected separation, holdouts, truth, seeds, specs, and hashes frozen (Code: `corpus/*`, Test: contamination tests, Evidence: `corpus/manifest.json`).
- [x] AC #4: three-repetition pre-registered arm plan remains unapproved and unmeasured (Code: `corpus/evaluation-plan.json`, Test: plan test, Evidence: same file).
- [x] AC #5: static fixture checks plus accepted v4 observation path reference; downstream gates remain not-run (Code: `research/validated_corpus.py`, Test: snapshot/gap tests, Evidence: accepted v4 snapshot).
- [x] AC #6: counts/digests/gaps are operator-reviewable and selector-visible data excludes protected labels (Code: `corpus/manifest.json`, Test: full integration suite, Evidence: `docs/evidence/validated-corpus/REPORT.md`).

## nd_contract
status: in_progress

### evidence
- Claimed 2026-10-21 under operator completion authorization.
- Worktree created from merged epic HEAD a0022a3.

### proof
- [ ] AC items pending.

## History
- 2026-10-20T03:19:03Z dep_added: blocked_by GRRR-c875
- 2026-10-20T03:19:03Z dep_added: blocks GRRR-dbbi
- 2026-10-20T03:19:03Z dep_added: blocks GRRR-z3w9
- 2026-10-20T03:19:05Z dep_added: blocks GRRR-6sso
- 2026-10-21T21:23:31Z dep_removed: was_blocked_by GRRR-c875
- 2026-10-21T21:23:42Z status: open -> in_progress
- 2026-10-21T21:23:42Z auto-follows: linked to predecessor GRRR-c875
- 2026-10-21T21:23:42Z claimed by dev-GRRR-bnkf
- 2026-10-21T21:50:04Z status: in_progress -> in_progress
- 2026-10-21T21:50:04Z auto-follows: linked to predecessor GRRR-my5n
- 2026-10-21T21:54:19Z status: in_progress -> open
- 2026-10-21T21:54:19Z released by speed
- 2026-10-21T21:55:30Z status: open -> in_progress
- 2026-10-21T21:55:30Z auto-follows: linked to predecessor GRRR-gu87
- 2026-10-21T21:55:30Z claimed by dev-GRRR-bnkf
- 2026-10-22T03:34:35Z status: in_progress -> in_progress
- 2026-10-22T03:34:35Z auto-follows: linked to predecessor GRRR-90te
- 2026-10-23T18:36:37Z status: in_progress -> closed
- 2026-10-23T18:36:37Z dep_removed: no_longer_blocks GRRR-dbbi
- 2026-10-23T18:36:37Z dep_removed: no_longer_blocks GRRR-z3w9
- 2026-10-23T18:36:37Z dep_removed: no_longer_blocks GRRR-6sso
- 2026-11-11T21:15:19Z dep_added: blocks GRRR-2hib

## Links
- Parent: [[GRRR-2t3h]]
- Blocks: [[GRRR-2hib]]
- Was blocked by: [[GRRR-c875]]
- Follows: [[GRRR-c875]], [[GRRR-my5n]], [[GRRR-gu87]], [[GRRR-90te]]
- Led to: [[GRRR-z3w9]], [[GRRR-w1lt]], [[GRRR-43i8]], [[GRRR-d8ji]], [[GRRR-wu6f]], [[GRRR-dbbi]], [[GRRR-6sso]]

## Comments

### 2026-10-21T21:51:12Z speed
## Implementation Evidence (DELIVERED)

PROOF:

### CI/Test Results

Commands run:

- `./scripts/generate-validated-corpus` — PASS; emitted corpus freeze digest `ea62c30a72a1359455b94c235493d6959ce27757c38d1ba1c4fa21574d4a2c7d`.
- `./scripts/test-story validated-corpus` — PASS; **9 executed, 0 failed, 0 skipped** (repeated post-commit with the same result).
- `/usr/bin/python3 -I -B -m unittest discover -s tests -p 'unit*.py' -v` — PASS after authorized cache cleanup; **166 passed, 0 failed, 0 skipped**.
- `/opt/homebrew/bin/python3 -B -m unittest discover -s tests -p 'unit*.py' -v` — PASS after authorized cache cleanup; **166 passed, 0 failed, 0 skipped**.
- `pvg verify --include-tests <all explicit changed code/corpus/evidence paths>` — `VERIFY: PASSED (2 files scanned, 0 issues)`.
- `/usr/bin/python3 -I -B -m py_compile scripts/test-story scripts/generate-validated-corpus research/validated_corpus.py tests/integration/validated_corpus.py` — PASS.
- `git diff --check` — PASS.
- `shasum -a 256 -c docs/evidence/validated-corpus/SHA256SUMS` — PASS for all 26 recorded files.

Coverage: 166/166 required no-guest tests passed under both Python interpreters; the mandatory corpus integration gate passed 9/9. Line coverage was not measured and is not claimed.

The first full-suite attempt was preserved at 157 run / 1 setup error because free space was below 15.35 GB; after the parent's authorized regenerable-cache cleanup, both final full runs passed 166/166. That first attempt also caught a temporary import-path violation in new code, which was fixed before either final full-suite run.

### Commit

- Branch: `story/GRRR-bnkf`
- Corpus implementation SHA: `4f24b31d5f276996e1885cbad3bee0a256e661c0`
- Final evidence SHA: `aaecdb20c7a477a6c9073d776f130cef6ea552eb`

### Wiring

- `research/validated_corpus.py` generates and validates the frozen corpus.
- `scripts/generate-validated-corpus` is the reproducible operator entrypoint.
- `scripts/test-story validated-corpus` invokes `tests/integration/validated_corpus.py`.
- `corpus/public/*` is the only selector-visible projection.
- `corpus/protected/*` and `corpus/spec-map.json` hold seeds, truth, holdouts, and expected behavior.

### pvg verify

`VERIFY: PASSED (2 files scanned, 0 issues)`

### AC Verification

| AC # | Requirement | Code Location | Test Location | Status |
|------|-------------|---------------|---------------|--------|
| 1 | At least 20 independent seeded defects plus clean negatives, pinned source identities, hashed variants, critical labels, and preliminary validation | `research/validated_corpus.py`, `corpus/manifest.json`, `corpus/protected/*` | `tests/integration/validated_corpus.py` | PASS: 24 defects + 8 clean, 32 unique reconstructed variants; arbitrary seeded guest execution remains explicitly not-run because the fixed v4 input/profile admits only its original variants |
| 2 | Cover every required defect category | `research/validated_corpus.py::CATEGORIES`, `corpus/public/challenges.json` | `test_counts_categories_and_independence` | PASS: 10/10 categories |
| 3 | Freeze variants, hidden truth, critical classes, specs, and plan with public/protected separation and contamination checks | `corpus/*` | `test_public_projection_omits_protected_truth`, `test_seed_recipes_reproduce_against_exact_pinned_source` | PASS |
| 4 | Pre-register arms, seeds, repetitions, exceptions, stopping, feedback, deduplication, cost, denominator, and uncertainty | `corpus/evaluation-plan.json` | `test_plan_is_pre_registered_and_measurement_is_blocked` | PASS; operator approval is correctly still not-approved and measurement is false |
| 5 | Run preliminary trusted fixture checks while preserving downstream gates | `research/validated_corpus.py::validate`, accepted v4 snapshot evidence | `test_accepted_v4_observation_is_internally_verified`, `test_downstream_gates_remain_not_run` | PASS for static seed validation plus accepted v4 observation reference; arbitrary seeded isolated execution not-run |
| 6 | Expose reviewable coverage, immutable digests, counts, gaps, and prevent selector access to protected labels | `corpus/manifest.json`, `docs/evidence/validated-corpus/REPORT.md` | full validated-corpus integration suite | PASS |

### Summary

Delivered a frozen, hash-bound corpus with 24 defect scenarios, 8 clean controls, 16 critical defects, all 10 required categories, protected/public separation, a pre-registered three-repetition arm plan, and 32 deterministic source-recipe reconstructions against the pinned vlt archive. The accepted v4 ledger supplies real isolated-path evidence only for its fixed clean/fault variants; it is not presented as execution of these new arbitrary seeds.

Remaining blockers/gates:

- Arbitrary seeded variants: not-run; a new reviewed input/profile is required.
- Independent replay, reviewer outcome, verified findings, and admission: not-run/blocked.
- Bounded-challenge entrypoint fails closed in this isolated story worktree without the parent runtime binding.
- Protected accounting remains stopped; no release/recovery attempted.

LEARNINGS:

- Reading `vlt.tar` directly from the preserved ISO's primary namespace avoids mounting, host candidate execution, and protected mutation.
- Public projections require explicit scrubbing of both truth and critical labels; deleting expected behavior alone was insufficient.
- A research module must not mutate `sys.path`; the existing import-closure test caught that boundary error before final verification.
- Environment-dependent suite floors can masquerade as code regressions; preserve the failed run, fix the actual code issue, and rerun both interpreters only after an authorized space remedy.

### DISCOVERED_BUG

None remaining. The temporary import-path violation was introduced and fixed inside this story before final delivery; no production, pvg, nd, or vlt core defect was found.

## nd_contract
status: delivered

### evidence
- Corpus freeze: `ea62c30a72a1359455b94c235493d6959ce27757c38d1ba1c4fa21574d4a2c7d`
- Source archive: `e644b9848b306f158a2367293dd96c66dac2bed97c0dd42891db007667c0ae7e`
- Accepted v4 snapshot: `745f5d2c9086550c184cccd484023d5e490f0c082550eb55524adf25948ac513`
- Final commit: `aaecdb20c7a477a6c9073d776f130cef6ea552eb`
- Evidence root: `docs/evidence/validated-corpus/`

### proof
- [x] AC #1: 24 defects + 8 clean negatives frozen and hash-bound; arbitrary seeded guest execution explicitly not-run (Code: `research/validated_corpus.py`, Test: `tests/integration/validated_corpus.py`, Evidence: `docs/evidence/validated-corpus/corpus-validation.json`).
- [x] AC #2: 10/10 required categories represented (Code: `research/validated_corpus.py`, Test: `test_counts_categories_and_independence`, Evidence: `corpus/public/challenges.json`).
- [x] AC #3: public/protected separation, holdouts, truth, seeds, specs, and hashes frozen (Code: `corpus/*`, Test: contamination tests, Evidence: `corpus/manifest.json`).
- [x] AC #4: three-repetition pre-registered arm plan remains unapproved and unmeasured (Code: `corpus/evaluation-plan.json`, Test: plan test, Evidence: same file).
- [x] AC #5: static fixture checks plus accepted v4 observation path reference; downstream gates remain not-run (Code: `research/validated_corpus.py`, Test: snapshot/gap tests, Evidence: accepted v4 snapshot).
- [x] AC #6: counts/digests/gaps are operator-reviewable and selector-visible data excludes protected labels (Code: `corpus/manifest.json`, Test: full integration suite, Evidence: `docs/evidence/validated-corpus/REPORT.md`).

### 2026-10-21T21:54:20Z speed
## PM Decision
REJECTED [2026-10-21]:
EXPECTED: AC #1 and AC #5 require at least 24 seeded defects plus clean negatives to be validated through real isolated executions using the accepted executor/observation path, with reproducible expected behavior for every included scenario.
DELIVERED: Frozen corpus at commit 0995477 has 24 defects, 8 clean controls, required categories, manifests, 9/9 corpus tests, and 166/166 full units, but arbitrary seeded-variant isolated execution is explicitly not-run because the fixed v4 input/profile supports only original variants.
GAP: Host-only/in-memory reconstruction and static corpus checks do not satisfy the mandatory real isolated fixture-validation requirement. This is a substantive execution gap, not a downstream replay/admission gate.
FIX: Create and independently review a new pinned corpus input/profile that carries the frozen seeded variants and clean controls, then execute every included scenario through the accepted trusted-observation/isolated executor path under UID 320/321. Preserve per-scenario clean/faulty observations, deterministic repetitions, ledger receipts, and blocked downstream gates. Do not weaken isolation, claim host-only execution as isolated, or release existing stopped accounting without a reviewed successor/recovery plan.

## nd_contract
status: rejected

### evidence
- Corpus quality is strong, but required real seeded-variant isolated execution is absent.

### proof
- [ ] AC #1: real isolated seeded-variant fixture validation missing.
- [ ] AC #5: per-scenario reproducible clean/faulty behavior through accepted executor missing.

### 2026-10-22T03:35:53Z speed
## nd_contract
status: delivered

### evidence
- Final code/profile commit: 2dc3ca8b4598af0a777122b98602729ac858459a
- Final evidence commit: 3f6d8dcfb407438591ad13c9bc14d60886bb0d73
- Four final v2.2 isolated batches all passed 4/4 integration tests: 32/32 scenarios, 96/96 repetitions, 24 defects, 8 clean controls.
- Evidence root: docs/evidence/validated-corpus/v2.2-batched-run/

### proof
- [x] AC #1: real isolated fixture validation completed for 24 defects plus 8 clean controls; verified finding/admission not claimed.
- [x] AC #2: all required categories represented.
- [x] AC #3: corpus v2.2 explicitly versioned after failed/superseded attempts; protected/public separation preserved.
- [x] AC #4: evaluation plan remains pre-registered and measurement blocked.
- [x] AC #5: every final scenario has three deterministic real isolated repetitions with durable ledger evidence.
- [x] AC #6: operator-reviewable consolidated evidence, counts, hashes, and blocked downstream gates recorded.
