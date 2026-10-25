---
id: GRRR-z3w9
title: "Verify a defect from fresh trusted inputs"
status: open
priority: 1
type: task
labels: [milestone-1, integration, blocked]
parent: GRRR-2t3h
created_at: 2026-10-20T03:19:03Z
created_by: speed
updated_at: 2026-10-25T21:13:37Z
content_hash: "sha256:00e23b9411565fb982fde28d3b59ba4c68393435e80ace46ea7c589cb5762855"
blocks: [GRRR-34ve, GRRR-6sso, GRRR-dbbi]
was_blocked_by: [GRRR-bnkf, GRRR-w1lt, GRRR-43i8, GRRR-d8ji]
follows: [GRRR-bnkf, GRRR-w1lt, GRRR-c875, GRRR-43i8, GRRR-d8ji]
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
COMMIT: 6079af6 (story/GRRR-z3w9), v2 partial WIP, clean worktree; exact tested source hashes checked against source-SHA256SUMS after commit. Full suites 225/225 on both Pythons; focused suites 59/59 both; mandatory live gate 0 run and 1 UID/GID setup error. No delivery, acceptance, push, protected mutation or live proof. Review map: docs/INDEPENDENT-REPLAY-V2-REVIEW.md. Prepared ISO remains /private/tmp/grrr-independent-replay-input-v1/input.iso, SHA256 977783b9bae0b76e7288afbf31e9018b86a7345072b5729257f8392d45e256cf. Independent review/accounting recovery/live proof still blocked; releasing claim for parent triage.
WIP COMMIT: 3869e0ff223bae5d4ae75080f33d4b6ba33efacc on story/GRRR-z3w9. Merge parents preserve 6079af6 replay WIP and 6afd643 accepted epic. Worktree clean. All seven source-SHA256SUMS entries verified after commit. Focused 91/91 both interpreters; full 248 executed, one setup error each; live 0 executed, one UID/GID setup error each. No delivery, acceptance, push, protected mutation, replay or authorization claimed. Exact future command inventory is unapproved and requires recovery implementation plus independent review. Releasing claim under BLOCKED protocol.
FINAL BLOCKED HANDOFF: source merge/WIP c2c19ae92f4d318d0892bc77272b599043c0019f; evidence commit f94f306f94172f6dbf7ca6aa893f93d2e8376ed9. Clean story worktree; claim released. Evidence and source SHA256SUMS independently verified after commit; diff checks pass. Story remains open with blocked label, not delivered or accepted. No push, privileged effects, reconciliation or replay.

# V4 no-guest verification — BLOCKED, NOT DELIVERED

PROOF:

Source merge/WIP commit: `c2c19ae92f4d318d0892bc77272b599043c0019f`,
parents `3869e0ff223bae5d4ae75080f33d4b6ba33efacc` and
`38f33c936b8249a57be81aebd639aa40c2f9de55`. Branch story/GRRR-z3w9.
The launcher hash-map conflict was resolved with the exact merged import closure;
accepted accounting recovery/security implementation and cessation tests remain
unchanged. The new replay boundary refuses v3 explicitly because it is read-only,
not because recovery is still missing. No authority was broadened.

Tests ran on `/usr/bin/python3` (3.9.6) and `/opt/homebrew/bin/python3` (3.14.3):

| Command (each interpreter) | System | Homebrew |
|---|---|---|
| `-m unittest discover -s tests -p 'unit_*replay*.py'` | 117 pass, 0 failures/errors/skips; 20.988s; exit 0 | 117 pass, 0 failures/errors/skips; 20.534s; exit 0 |
| `-m unittest discover -s tests -p 'unit_*.py'` | 274 executed/pass, 0 failures/skips; 1 class setup error; 25.063s; exit 1 | 274 executed/pass, 0 failures/skips; 1 class setup error; 23.909s; exit 1 |
| `scripts/test-story independent-replay` | 0 executed, 1 class setup error; exit 1 | 0 executed, 1 class setup error; exit 1 |
| `-m compileall -q research scripts tests` | exit 0 | exit 0 |
| `-m py_compile scripts/replay-root-prepare scripts/prepare-independent-replay-input scripts/test-story` | exit 0 | exit 0 |

The full suites are NOT passing: nine conservative-genesis tests never executed
because setUpClass raises `RuntimeError: preparation space floor`, requiring
15,350,000,000 bytes. The recorded filesystem available space was 10,358,388 KiB,
below that floor and the replay floor. No deletion or floor relaxation occurred.
The live read-only suite fails at `Dedicated UID/GID required`; no guest is run
or guest receipt produced. No tests are gated/skipped to manufacture green.
Coverage was not measured in this continuation; no percentage or live coverage
claim is made. Mocked preflight tests prove decision ordering only, not integration.

`pvg verify research/replay.py research/replay_smoke.py research/persistent_budget.py research/accounting_registration.py research/accounting_recovery.py scripts/replay-root-prepare tests/unit_replay_registration_boundary.py tests/unit_replay_smoke.py tests/unit_replay_accounting_recovery.py tests/unit_replay_cessation.py docs/INDEPENDENT-REPLAY-V4-REVIEW.md --include-tests --format=text`
returned `VERIFY: PASSED (9 files scanned, 0 issues)`, exit 0. Both
`git diff --check` and `git diff --cached --check` returned exit 0.
Logs are adjacent; source-SHA256SUMS binds exact relevant source bytes and
SHA256SUMS binds the evidence package. Compile/metadata checks are in checks.log.

## AC verification

| AC | Evidence | Status |
|---|---|---|
| 1 fresh trusted reconstruction/reservation/VM | preflight and exact import closure; focused tests | Partial; actual fresh VM and writable/spendable reservation unavailable |
| 2 specification-confirmed independent defect | existing pinned D011 maintainer mapping | Partial; no live independent reproduction |
| 3 receipt/findings/mandatory gates | pure helpers and conservative refusal | Partial; no actual ReplayReceipt |
| 4 required real success and fault modes | no-guest tests and explicit identity failure | Unmet; all live tests unexecuted |
| 5 retained failures/two-failure stop | existing pure transitions; inherited cessation tests | Partial; actual durable live sequence unproven |

LEARNINGS:
- Accepted v3 recovery releases only stop; null spendability and denied mutations
  are still hard blockers. Reconciliation is separate and prohibited here.
- Transitive recovery imports must be pinned after merging accepted code; hash
  assertions remain strict and accepted cessation behavior remains intact.
- Passing focused tests cannot conceal capacity-blocked full-suite setup or an
  identity-blocked live suite. Earlier documents are historical, not authorization.
- Knowledge search failed because this worktree has no `.vault` knowledge path;
  no raw issue files were read. Code graph coverage was stale/untracked/excluded
  for the exact changed paths; direct source review supplied the fallback.

DISCOVERED_BUG:
  title: Independent replay remains blocked by spendability, capacity and live identity gates
  context: The reviewed v3 accounting successor is stop-only read-only, preserves unknown usage/holds and denies every runtime mutation. Replay needs reservation/settlement writes but reconciliation and replay are expressly unauthorized. Both full suites also have a disk-floor class setup error; read-only live tests fail dedicated UID/GID setup. No safeguards were relaxed.
  affected_files: research/replay.py; research/persistent_budget.py; scripts/conservative-genesis; tests/integration/independent_replay.py
  discovered_during: GRRR-z3w9

Remaining parent gates: separately reviewed and explicitly authorized reconciliation
if writes/spendability are required; capacity above fixed floors; actual identities;
independent exact-byte replay review and immutable installation; separate replay
authorization; fresh four-mode VM execution and retained complete evidence; PM
acceptance. No reconciliation, replay, promotion, admission, production mutation,
push, privileged command, UID/GID setup or /Library/GRRR mutation occurred.

## nd_contract
status: blocked

### evidence
- Safe no-guest WIP integrated with accepted epic; exact source commit and counts above.
- Full suite capacity error and live identity error retained, not skipped success.

### proof
- [x] No-guest v3 refusal and merged import closure verified.
- [ ] AC #1: actual fresh replay and authorized budget unavailable.
- [ ] AC #2: live independent reproduction unproven.
- [ ] AC #3: actual complete receipt unavailable.
- [ ] AC #4: required live modes unexecuted.
- [ ] AC #5: actual durable failure sequence unproven.

# V3 no-guest verification — BLOCKED, NOT DELIVERED

PROOF:

Source bytes are bound by source-SHA256SUMS in this directory. WIP commit SHA
is appended to the live GRRR-z3w9 story after commit. Starting WIP 6079af6;
merged epic 6afd643 without conflicts. No accounting/security source or test
diff remains relative to that epic (persistent_budget.py, accounting_registration.py,
budget.py, unit_replay_accounting_registration.py).

From the dev-GRRR-z3w9 worktree, with Python 3.9.6 and 3.14.3 respectively:

| Command (each interpreter) | System | Homebrew |
|---|---|---|
| `-m unittest discover -s tests -p 'unit_*replay*.py'` | 91 pass, 0 errors/failures/skips; 17.419s | 91 pass, 0 errors/failures/skips; 16.784s |
| `-m unittest discover -s tests -p 'unit_*.py'` | 248 executed/pass, 0 test failures; 1 class setup error; 21.231s; exit 1 | 248 executed/pass, 0 test failures; 1 class setup error; 20.033s; exit 1 |
| `scripts/test-story independent-replay` | 0 executed, 1 class setup error, 0 skips; exit 1 | 0 executed, 1 class setup error, 0 skips; exit 1 |
| `-m compileall -q research scripts tests` | exit 0 | exit 0 |
| `-m py_compile scripts/replay-root-prepare scripts/prepare-independent-replay-input scripts/test-story` | exit 0 | exit 0 |

The exact interpreters were `/usr/bin/python3` and `/opt/homebrew/bin/python3`.
The nine conservative-genesis tests did not execute because their class setup
requires 15,350,000,000 bytes free. The measured 13,212,716 KiB free is below
that threshold and the replay 15-GiB floor. This is not a passing full suite.
The live suite only reads existing evidence; its actual UID/GID prerequisite
rejected this operator process before tests. No guest was attempted.

Initial runs are retained separately: focused 91 with 3 failed hash assertions;
full 248 with those same 3 failures plus the disk setup error. The merge had
retained a stale persistent_budget.py launcher pin. The pin was corrected to
the accepted epic bytes, not by weakening the hash assertions.

`pvg verify research/replay.py research/replay_fixtures.py research/replay_profile.py research/replay_smoke.py research/corpus_execution.py research/corpus_evaluation.py research/persistent_budget.py research/accounting_registration.py scripts/replay-root-prepare scripts/prepare-independent-replay-input tests/unit_replay_inputs.py tests/unit_replay_smoke.py tests/unit_replay_registration_boundary.py tests/integration/independent_replay.py docs/INDEPENDENT-REPLAY-V3-REVIEW.md --include-tests --format=text`
returned `VERIFY: PASSED (12 files scanned, 0 issues)`, exit 0.
Both `git diff --check` and `git diff --cached --check` returned exit 0.

`/usr/bin/python3 -m trace --count --missing --summary --coverdir /private/tmp/grrr-replay-v3-coverage --module unittest discover -s tests -p 'unit_replay_registration_boundary.py'`
passed 2 tests. Boundary-only coverage: replay.py 20% of 480 executable lines,
new test module 96% of 33 lines. This is not full-suite or live coverage.
Focused suites include real non-privileged SQLite/filesystem/authorization
tests inherited from accepted registration; new mocks test only pure preflight
decisions and never establish integration evidence.

## AC verification

| AC | Package evidence | Actual status |
|---|---|---|
| 1 | Replay profile/fixtures, cumulative-binding preflight, exact import closure | Partial; fresh VM and authorized reservation unproven |
| 2 | Pinned D011 maintainer assertion mapping | Partial; no independent live reproduction |
| 3 | Pure finding/gate helpers and four-mode result validation | Partial; no actual ReplayReceipt |
| 4 | Four-mode read-only integration suite and no-guest tests | Unmet; all live integration unexecuted |
| 5 | Pure failure transition tests, retained-mode draft | Partial; durable live sequence unproven |

LEARNINGS:
- Registration v2 deliberately freezes every mutation; successful registration
  is neither an executable budget profile nor stop-recovery authorization.
- Import closures need transitive dependencies and updated pins after merges.
- A passing focused suite does not conceal a disk-blocked full-suite class.
- Future commands need a new recovery implementation and independent review;
  presenting exact grammar does not authorize or validate execution.

DISCOVERED_BUG:
  title: Independent replay remains blocked by recovery and capacity prerequisites
  context: Registered v2 accounting is intentionally frozen. No approved recovery implementation exists; free disk also blocks conservative-genesis setup and replay floor. Live tests reject the operator UID/GID. No safeguards were relaxed.
  affected_files: research/replay.py; research/persistent_budget.py; scripts/conservative-genesis; tests/integration/independent_replay.py
  discovered_during: GRRR-z3w9

DISCOVERED_BUG:
  title: Story worktree knowledge search cannot resolve vault
  context: pvg notes search independent-replay returned vault directory not found for dev-GRRR-z3w9/.vault. Live pvg nd worked using the git-common shared vault. No raw issue data was accessed or vault routing modified.
  affected_files: worktree knowledge vault configuration
  discovered_during: GRRR-z3w9

## nd_contract
status: new

### evidence
- No-guest WIP only; independent review and live gates remain blocked.

### proof
- [ ] AC #1: real fresh replay unproven.
- [ ] AC #2: independent live specification violation unproven.
- [ ] AC #3: actual complete receipt unproven.
- [ ] AC #4: mandatory live integrations unexecuted.
- [ ] AC #5: durable failure/stop sequence unproven.

# V2 no-guest proof — partial WIP only

## PROOF

Source identity is recorded in `source-SHA256SUMS`; commit identity is appended
to the story after committing these exact source bytes. No guest, QEMU, sudo,
root execution, protected mutation, push or paid call occurred.

Commands from the GRRR-z3w9 worktree:

- `/usr/bin/python3 scripts/prepare-independent-replay-input /private/tmp/grrr-independent-replay-input-v1`
  — exit 0; 9 primary-ISO members verified; 71,954,432-byte image, no execution.
- `/usr/bin/python3 -m unittest discover -s tests -p 'unit_*.py'`
  — 225 passed, 0 failed/errors/skipped, 20.399 seconds (`full-system.txt`).
- `/opt/homebrew/bin/python3 -m unittest discover -s tests -p 'unit_*.py'`
  — 225 passed, 0 failed/errors/skipped, 19.489 seconds (`full-homebrew.txt`).
- `/usr/bin/python3 -m unittest discover -s tests -p 'unit_*replay*.py'`
  and the same command with `/opt/homebrew/bin/python3`
  — 59 passed each, 0 failed/errors/skipped (`focused-*.txt`).
- `/usr/bin/python3 -m trace --count --missing --summary --coverdir /private/tmp/grrr-replay-v2-coverage --module unittest discover -s tests -p 'unit_*replay*.py'`
  — 59 passed; replay.py 41% of 476 executable lines, replay_fixtures.py 100%
  of 31, replay_profile.py 45% of 44 (`coverage-system.txt`). Protected/live
  branches remain unexecuted; this is not execution coverage of the required VMs.
- `pvg verify research/replay.py research/replay_fixtures.py research/replay_profile.py research/replay_smoke.py research/corpus_execution.py research/corpus_evaluation.py scripts/replay-root-prepare scripts/prepare-independent-replay-input tests/unit_replay_inputs.py tests/unit_replay_smoke.py tests/integration/independent_replay.py docs/INDEPENDENT-REPLAY-WIP.md docs/INDEPENDENT-REPLAY-V2-REVIEW.md --include-tests --format=text`
  — exit 0, reported 9 files scanned, 0 issues. This is not security approval.
- Both interpreters: `-m py_compile research/replay.py research/replay_profile.py research/replay_fixtures.py research/corpus_execution.py research/corpus_evaluation.py research/replay_smoke.py scripts/prepare-independent-replay-input scripts/replay-root-prepare tests/integration/independent_replay.py tests/unit_replay_inputs.py`
  — exit 0. Both also passed `-m compileall -q research scripts tests`.
- `git diff --check` — exit 0. `git diff --name-only -- corpus` — empty.
- `/usr/bin/python3 scripts/test-story independent-replay` — exit 1,
  0 tests run, 1 setup error, 0 skipped: actual dedicated UID/GID unavailable.
  This is a blocking live gate, not a passing integration result.

An earlier verify run identified the no-op result hook as a stub. It was replaced
by explicit run-binding validation preserving the corpus receipt shape; the
final verify and both final suites above passed. No RED tests were weakened.

## AC status

| AC | Evidence | Status |
|---|---|---|
| 1 fresh evaluator reconstruction/reservation/VM | New byte-pinned replay profile, source reconstructions, fixed executor hooks | Draft only; cumulative registration/recovery and actual execution blocked |
| 2 authoritative specification | Existing pinned upstream D011 assertion plus matching replay clean/seed probes | Byte/spec mapping tested; live reproduction unproven |
| 3 Finding and mandatory gates | Explicit mode checks and existing receipt/gate rules | Draft; no actual independent ReplayReceipt |
| 4 real success/failure integration | Separate clean, seed, syntax-error and bounded-interruption inputs; four one-shot modes; post-run integration | Required live suite blocked, 0 tests executed |
| 5 durable two-failure stop | Fixed success/negative/negative mode, shared cumulative store, retained ledger objects/holds | Pure state tests pass; real durable sequence unproven |

## LEARNINGS

- The generic supervisor can consume a separate replay catalog unchanged; D/C
  identifier syntax is not a license to relabel frozen corpus evidence.
- Reusing verified primary-ISO source/toolchain/supervisor bytes avoided host
  candidate execution and preserved corpus v2.2 completely.
- Negative fixture modes need distinct immutable namespaces, but not distinct
  accounting allowances. Stop recovery is separate from profile registration.
- A timed command interruption proves dispatched guest interruption, not that a
  slow build reached the sleeping probe. The limitation is explicit in review.
- Source/fixture preparation and unit success do not satisfy live ACs. Read-only
  post-run integration cannot manufacture missing evaluator evidence.

## nd_contract
status: new

### evidence
- Partial v2 preparation and implementation only; exact source hashes and logs here.
- Independent review, protected accounting migration/recovery and live gates blocked.

### proof
- [ ] AC #1: actual fresh cumulative-budget-bound replay unproven.
- [ ] AC #2: independent live specification violation unproven.
- [ ] AC #3: actual complete ReplayReceipt unproven.
- [ ] AC #4: actual four-mode integration unproven.
- [ ] AC #5: actual durable two-failure stop unproven.

## Partial implementation evidence — BLOCKED, NOT DELIVERED

PROOF:
- Branch story/GRRR-z3w9; WIP commit 40f851e37804cc3b853d20e17744ec770792c95f.
- Python versions: /usr/bin/python3 = 3.9.6; /opt/homebrew/bin/python3 = 3.14.3.
- `/usr/bin/python3 tests/unit_independent_replay.py`: 17 tests, 0 failures/errors/skips; exit 0.
- `/opt/homebrew/bin/python3 tests/unit_independent_replay.py`: 17 tests, 0 failures/errors/skips; exit 0.
- `/usr/bin/python3 -m unittest discover -s tests -p 'unit_*.py'`: final 215 tests, 0 failures/errors/skips, 20.174s; exit 0.
- `/opt/homebrew/bin/python3 -m unittest discover -s tests -p 'unit_*.py'`: final 215 tests, 0 failures/errors/skips, 19.408s; exit 0.
- Initial system full run: 205 tests, 1 error, 19.237s, conservative-genesis preparation-space-floor refusal. Preserved separately in initial-full-failure.txt. Parent reported safe staging cleanup; both final suites subsequently passed. No cleanup by this worker.
- Both interpreters ran `scripts/test-story independent-replay`: exit 1, 0 integration tests executed, 1 setUpClass error, 0 skips, actual Dedicated UID/GID required. This is a blocked integration run, not success.
- Both interpreters ran `-m py_compile research/replay.py research/replay_smoke.py scripts/replay-root-prepare scripts/test-story tests/unit_independent_replay.py tests/unit_replay_smoke.py tests/integration/independent_replay.py`: exit 0.
- `git diff --check`: exit 0.
- `pvg verify research/replay.py research/replay_smoke.py scripts/replay-root-prepare scripts/test-story tests/unit_independent_replay.py tests/unit_replay_smoke.py tests/integration/independent_replay.py docs/INDEPENDENT-REPLAY-WIP.md --format=text`: VERIFY PASSED, 5 files scanned, 0 issues. This is not security approval.
- Coverage command: `/usr/bin/python3 -m trace --count --missing --summary --coverdir /private/tmp/grrr-z3w9-no-guest-coverage --module unittest discover -s tests -p unit_independent_replay.py`: 17 tests pass; replay.py 42% of 362 executable lines; unit_independent_replay.py 99% of 124 lines. Privileged/live branches intentionally remain unexecuted.
- Evidence directory: docs/evidence/independent-replay/no-guest/ (committed logs). No VM, QEMU, sudo, root execution, /Library/GRRR mutation or paid call performed.
- research/replay.py SHA256 bd60de46037c23b99f17eaaeca105d280c5dac1531758cc62ebb03a738961323.
- scripts/replay-root-prepare SHA256 e6b3140f5ffaee1f620763eaeff05c2eecd537356bcc267cb486d096420e6a59.
- Direct D011 maintainer specification: source archive e644b9848b306f158a2367293dd96c66dac2bed97c0dd42891db007667c0ae7e, wikilinks_test.go member 218eebc6314ce14c555c579db24b85ccc4ccb425e3cd51f93d1c52a9049da570, TestParseWikilinks/link with display text and g.Display comparison loop.

### AC verification
| AC | Implementation and test locations | Status |
| 1 fresh evaluator-controlled reconstruction | research/replay.py; root mode/shared lifecycle; tests/unit_independent_replay.py | PARTIAL draft. No live execution; cumulative replay profile absent; replay-specific guest profile unfinished. |
| 2 pinned specification confirmation | maintainer_specification and finding in research/replay.py; exact archived maintainer case checked by unit tests | No-guest byte/spec mapping PASS for D011 only; no verified live defect claimed. |
| 3 Finding plus mandatory gates | finding, gate_inventory, reproduce; invalid-claim receipt draft; baseline/seed result draft | PARTIAL. Pure contracts tested, actual evaluator receipts unproven. Admission always blocked. |
| 4 all real integration paths | tests/integration/independent_replay.py; scripts/test-story independent-replay | UNMET. Actual identity blocks operator execution; failed-build/interruption/failure-sequence expectations remain red and need real guest fixtures. |
| 5 approved two-failure stop and retained evidence | failure_transition and ledger atomic callback/export in research/replay.py | PARTIAL. Pure transition tests pass; actual persistent replay sequence not executed. |

### Unresolved gates / continuation
Independent security review, registered cumulative replay accounting with preserved prior usage/holds and explicit stop recovery, new versioned replay guest profile, full real fault-mode implementation, fresh parent installation, actual UID-separated live integration, reviewer outcome and all admission/comparison/promotion gates remain blocked/not-run. Existing C001 smoke is not reused or relabeled. The current root command is a future candidate only, NOT approved for installation/execution. docs/INDEPENDENT-REPLAY-WIP.md contains exact continuation map and parent-command candidate.

LEARNINGS:
- corpus specification_digest is a commit/filename label hash, not specification content; exact upstream table/assertion bytes provide a valid D011 mapping without inventing human approval.
- Failed rebuild must be Inconclusive, not the corpus fixture verdict's defect classification.
- The lifecycle smoke's separate Budget database cannot become independent replay accounting; cumulative store registration/history must be preserved.
- Current corpus transport hard-codes media/profile identities and variant==challenge. Real clean-D011/rebuild/interruption fixtures require a separate reviewed replay profile, not frozen-corpus mutation or synthetic receipts.
- Graph coverage was stale for corpus_execution and untracked for replay prerequisites; exact source reads supplied the missing evidence. pvg notes search failed because the story worktree has no .vault knowledge directory; no raw issue files were read.

DISCOVERED_BUG:
  title: Independent replay has no registered cumulative campaign accounting profile
  context: PersistentBudget.PROFILES excludes independent-replay; parent reports the active successor store stopped. A fresh replay allowance would reset campaign usage. Draft preflight refuses before namespace creation. Requires independently reviewed registration/history/stop-recovery decision, not a new empty database.
  affected_files: research/persistent_budget.py; research/replay.py
  discovered_during: GRRR-z3w9

## nd_contract
status: new

### evidence
- Partial WIP 40f851e37804cc3b853d20e17744ec770792c95f; no delivery or acceptance claimed.
- Final no-guest full suites 215/215 on both Python interpreters; live integration blocked.

### proof
- [ ] AC #1: fresh live replay/cumulative accounting unproven.
- [ ] AC #2: byte-pinned D011 mapping exists; independent reproduction unproven.
- [ ] AC #3: actual complete ReplayReceipt unproven.
- [ ] AC #4: required real guest fault modes incomplete.
- [ ] AC #5: actual durable two-failure sequence unproven.


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
- 2026-10-23T21:52:57Z status: in_progress -> open
- 2026-10-23T21:52:57Z released by speed
- 2026-10-23T21:54:21Z status: open -> in_progress
- 2026-10-23T21:54:21Z auto-follows: linked to predecessor GRRR-c875
- 2026-10-23T21:54:21Z claimed by dev-GRRR-z3w9
- 2026-10-23T22:08:06Z status: in_progress -> open
- 2026-10-23T22:08:06Z released by speed
- 2026-10-23T22:09:12Z dep_added: blocked_by GRRR-43i8
- 2026-10-24T13:58:45Z dep_removed: was_blocked_by GRRR-43i8
- 2026-10-24T15:39:30Z status: open -> in_progress
- 2026-10-24T15:39:30Z auto-follows: linked to predecessor GRRR-43i8
- 2026-10-24T15:39:30Z claimed by dev-GRRR-z3w9
- 2026-10-24T15:45:58Z status: in_progress -> open
- 2026-10-24T15:45:58Z released by speed
- 2026-10-24T15:47:31Z status: open -> blocked
- 2026-10-24T20:19:11Z dep_added: blocked_by GRRR-d8ji
- 2026-10-25T16:58:06Z dep_removed: was_blocked_by GRRR-d8ji
- 2026-10-25T20:41:44Z status: blocked -> in_progress
- 2026-10-25T20:41:44Z auto-follows: linked to predecessor GRRR-d8ji
- 2026-10-25T20:41:44Z claimed by dev-GRRR-z3w9
- 2026-10-25T20:45:27Z status: in_progress -> open
- 2026-10-25T20:45:27Z released by speed

## Links
- Parent: [[GRRR-2t3h]]
- Blocks: [[GRRR-34ve]], [[GRRR-6sso]], [[GRRR-dbbi]]
- Was blocked by: [[GRRR-bnkf]], [[GRRR-w1lt]], [[GRRR-43i8]], [[GRRR-d8ji]]
- Follows: [[GRRR-bnkf]], [[GRRR-w1lt]], [[GRRR-c875]], [[GRRR-43i8]], [[GRRR-d8ji]]

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

### 2026-10-23T21:53:28Z speed
Partial handoff: verify-delivery returned 1 passed / 8 failed, as expected for an undelivered partial story. It is NOT delivery proof. Claim released; story remains open. Source WIP 40f851e; integration evidence refreshed against that source. Full PROOF/AC/LEARNINGS and unresolved gates are appended in nd. No push or protected execution.

### 2026-10-23T22:06:21Z speed
BLOCKED: V2 replay-only preparation and four fixed-mode source drafts exist, but cumulative independent-replay accounting is unregistered and the existing campaign store is stopped. No protected mutation or live guest execution is authorized for this worker. Independent security review, protected registration/stop-recovery preserving all prior usage and holds, immutable parent installation, and actual UID-separated live proof remain required. See docs/INDEPENDENT-REPLAY-V2-REVIEW.md for exact candidate commands and blockers. This is WIP, not delivery.

### 2026-10-24T15:45:25Z speed
BLOCKED: Merged accepted epic 6afd643 into replay WIP. Registered v2 accounting remains frozen with no separately approved recovery implementation or execution authorization. Disk below preparation/replay floors; full no-guest suites execute 248 tests but have one class setup error on both interpreters. Focused suites pass 91/91 each. Live read-only integration executes 0 tests with dedicated UID/GID setup error. No privileged action performed. See docs/INDEPENDENT-REPLAY-V3-REVIEW.md and docs/evidence/independent-replay/v3-no-guest/REPORT.md. WIP only; do not deliver.

### 2026-10-24T15:47:31Z speed
## Parent Dispatch Result

GRRR-z3w9 was dispatched as authorized and completed safe no-guest continuation at story commit 3869e0ff223bae5d4ae75080f33d4b6ba33efacc, integrating epic 6afd643 without privileged effects.

Verified no-guest evidence:
- Focused registration/replay suites: 91/91 on both required Pythons.
- Full suites: 248 executed on each with one disk-floor setup error; nine conservative-genesis preparations did not execute.
- Compile, explicit-path pvg verify, diff checks, and seven source hashes passed.
- Live integration: 0 executed due dedicated UID/GID setup boundary.
- docs/INDEPENDENT-REPLAY-V3-REVIEW.md and docs/evidence/independent-replay/v3-no-guest/REPORT.md record the exact state.

Blocking conditions:
1. Registered accounting v2 intentionally freezes every mutation; no independently reviewed recovery implementation exists.
2. Actual replay remains explicitly unauthorized by the operator.
3. Host free space is about 13.21 GB, below the required preparation/replay floor.
4. Dedicated evaluator/runner UID/GID live integration is parent-mediated and not runnable by the developer.

No stop release, recovery, replay, promotion, admission, production mutation, push, QEMU/VM, or /Library/GRRR mutation occurred.

## nd_contract
status: blocked

### evidence
- Developer claim released and worktree left on clean WIP branch 3869e0f.

### proof
- [x] Safe no-guest integration and documentation completed.
- [ ] Recovery implementation/review remains separately required.
- [ ] Disk capacity must be restored above the fixed floor.
- [ ] Actual independent replay remains not-run and separately authorized.

### 2026-10-24T16:12:45Z speed
## Read-only Capacity/Recovery Preflight

Live reinspection measured root free space at 12,924,252,160 bytes, below the 15 GiB replay/preparation floor. Protected accounting remains version 2 with independent-replay registered, stopped, and execution-unauthorized; active binding hash 97ad3cd38a90a71d412afccad5ed49fc73af73e5413edcc4e07a1e0d23f451c5; no partial next-active artifact exists.

Identified regenerable cache targets, subject to explicit operator cleanup authorization:
- 1.82 GiB Codex Sparkle installation cache at /Users/speed/Library/Caches/com.openai.codex/org.sparkle-project.Sparkle/Installation (not the active Codex runtime under /Users/speed/.cache/codex-runtimes).
- 0.76 GiB Chrome cache under /Users/speed/Library/Caches/Google/Chrome/Default; Chrome is currently running, so cleanup should either skip it or use a safe shutdown/app-controlled path.
- 0.198 GiB pip cache.
- Smaller regenerable Homebrew/go-build caches.
Potential non-runtime cleanup excluding active Codex runtimes and protected GRRR evidence is approximately 3.1 GiB, sufficient to clear the reported 15.35 GB preparation threshold if Chrome cache is included or otherwise combined with purgeable/system recovery. No deletion occurred.

Recovery gap remains unchanged: registration deliberately has no recovery command; a separate reviewed recovery design/implementation and exact operator authorization are required before stop release. Actual replay remains denied/not-run.

## nd_contract
status: blocked

### evidence
- Read-only disk and cache inventory completed; no protected or cache state mutated.

### proof
- [ ] Explicit disk-cleanup authorization pending.
- [ ] Recovery implementation/review pending.
- [ ] Replay remains separately unauthorized.

### 2026-10-24T16:21:55Z speed
## Operator Authorization — regenerable cache cleanup only

APPROVED [2026-10-24]: remove only the Codex Sparkle Installation cache, Chrome Default Cache/Code Cache, pip cache, Homebrew cache, and go-build cache for GRRR-z3w9 capacity recovery.

Preserve all GRRR evidence, protected accounting, replay inputs, active Codex runtimes, repositories, and production data.

Denied: recovery, stop release, replay, promotion, admission, production mutation, and push.

## nd_contract
status: blocked

### evidence
- Cleanup has not started; exact target inventory and protected-state hash recorded by parent.

### proof
- [ ] Authorized cache cleanup pending.
- [ ] Recovery/replay remain denied.

### 2026-10-24T16:24:02Z speed
## Authorized Cache Cleanup Result

Operator authorized cleanup of only Codex Sparkle Installation, Chrome Default Cache/Code Cache, pip, Homebrew, and go-build caches. Parent removed contents of exactly those targets and preserved their parent directories.

Measured target bytes before:
- Codex Sparkle Installation 1,953,968,128
- Chrome Default Cache 730,193,920
- Chrome Code Cache 88,477,696
- pip 207,474,688
- Homebrew 50,655,136
- go-build 43,900,928

Immediate cleanup result: free space rose from 11,745,353,728 to 14,629,060,608 bytes, reclaiming 2,883,706,880 bytes. All six target directories were empty immediately afterward. Protected active/prior/receipt hashes were identical before/after; active Codex runtime, replay input, repositories, and GRRR evidence remained present. No recovery, stop release, replay, promotion, admission, production mutation, or push occurred.

Post-cleanup verification still failed the conservative-genesis preparation floor. Free space then measured 13,825,343,488 bytes and continued drifting down to about 13,244,039,168 bytes under host activity. The system-Python unit_conservative_genesis run exited nonzero in setUpClass with RuntimeError: preparation space floor; 0 tests ran. Chrome had recreated only small cache entries, so the larger loss was other host/purgeable activity rather than the authorized target regenerating.

Evidence: outputs/grrr-z3w9-cache-cleanup/ including before.tsv, after.tsv, protected hashes, run.log, post-cleanup test log/exit code, and SHA256SUMS.

## nd_contract
status: blocked

### evidence
- Authorized cleanup completed, but capacity still below the 15,350,000,000-byte preparation floor.

### proof
- [x] Exact authorized regenerable caches removed.
- [x] Protected records and preserved artifacts verified unchanged/present.
- [ ] Disk remains below fixed floor.
- [ ] Recovery implementation/review remains pending.
- [ ] Replay remains denied/not-run.

### 2026-10-24T20:16:14Z speed
## Operator-Authorized Capacity Reset Result

The operator authorized quitting Chrome and Spotify, running macOS purge, remeasuring free space, and rerunning the disk-floor test. Spotify exited gracefully. Chrome AppleScript quit returned user-canceled, so the parent used the operator-authorized SIGTERM fallback; both Chrome and Spotify were then absent. macOS purge completed.

Measured state:
- Before reset: 12,956,143,616 bytes free; swap used 3,748.88 MiB.
- After Chrome/Spotify exit: 12,740,812,800 bytes free; swap used 3,668.81 MiB.
- After purge: 12,927,787,008 bytes free; swap used remained 3,668.81 MiB.
- After tests: 12,927,635,456 bytes free.

Both required interpreters reran tests/unit_conservative_genesis.py. Each exited 1 in setUpClass with ; zero tests ran. The fixed 15,350,000,000-byte preparation floor remains unmet by 2,422,365,544 bytes at the after-purge measurement.

No additional files were deleted. No recovery, stop release, replay, promotion, admission, production mutation, or push occurred.

Evidence: outputs/grrr-z3w9-capacity-reset/ with states.txt, both interpreter logs/exit codes, and SHA256SUMS.

## nd_contract
status: blocked

### evidence
- Authorized capacity reset completed but did not clear the floor.

### proof
- [x] Chrome and Spotify quit; purge run; both interpreter floor tests rerun.
- [ ] Disk remains below 15,350,000,000 bytes.
- [ ] Recovery implementation/review remains required.
- [ ] Replay remains separately unauthorized.

### 2026-10-24T20:16:23Z speed
## Capacity Reset Contract Correction

The previous shell quoting removed the text `RuntimeError: preparation space floor` from the narrative by treating backticks as command substitution. The pvg update otherwise landed. Correct exact result: both required interpreters exited 1 in setUpClass with RuntimeError: preparation space floor, and zero tests ran. Evidence files remain unchanged.

## nd_contract
status: blocked

### evidence
- Corrected narrative only; no state or protected effect changed.

### proof
- [x] Capacity reset evidence remains in outputs/grrr-z3w9-capacity-reset/.
- [ ] Disk remains below the preparation floor.

### 2026-10-25T20:45:26Z speed
BLOCKED: V3 stop-only recovery is accepted but remains read-only with unknown historical usage, spendable=null, allowed_mutations=[] and execution_authorized=false. Reconciliation and replay are prohibited. Source WIP c2c19ae92f4d318d0892bc77272b599043c0019f merges epic 38f33c9 without weakening accounting/cessation tests. Focused no-guest suites 117/117 each; full suites 274 executed/pass with one capacity class setup error each; read-only live suite 0 tests with one UID/GID setup error each. See docs/INDEPENDENT-REPLAY-V4-REVIEW.md and docs/evidence/independent-replay/v4-no-guest/REPORT.md. Not delivered.

### 2026-10-25T21:00:44Z speed
## Authorized Capacity Preflight and Regenerable Cache Cleanup

Scope honored: read-only capacity preflight and regeneration-safe cache cleanup only. No spendability reconciliation, replay, promotion, admission, production mutation, protected accounting mutation, merge, or push.

Measured results:
- Before cleanup: 10,748,387,328 bytes available on /System/Volumes/Data.
- Removed only: Codex Sparkle Installation cache (1.9G), pip cache (259M), Chrome Default Cache (3.7M), and Chrome Default Code Cache (2.2M).
- Process/open-file preflight found Chrome, brew, go, pip3, and Sparkle updater inactive before cache removal.
- After cleanup: 12,952,973,312 bytes available.
- Reclaimed: 2,204,585,984 bytes.
- Homebrew and go-build caches were already 0B and were left untouched.
- Exact quarantined cache tree was deleted; no grrr-z3w9 cache quarantine residue remains.

Gate result:
- Preparation floor 15,350,000,000 bytes: FAIL (shortfall 2,397,026,688 bytes).
- Replay floor 16,106,127,360 bytes: FAIL (shortfall 3,153,300,048 bytes).
- Floors were not relaxed. GRRR-z3w9 remains open/blocked and capacity remains a mandatory gate.

Protected hashes after cleanup:
- /Library/GRRR/accounting/active.json cc45b70fed84bae583959379559e8fc8336a0da3b4bca1750fc20c2848619f1b
- /Library/GRRR/accounting/budget.sqlite 9fe4000c0c45b83cc818c29640e561167c34bd663abc26267e2a1b009f878234
- /Library/GRRR/accounting/receipt.json 9f64395bec815a6bb2281d3b5d96d2356819138b1929b0a9881c16483c486dde
- /Library/GRRR/accounting-poc2/active.json 9c5194dd12ff7601917fcccc293c459db09a41da8bad9fa9983cbef618d453f8
- /Library/GRRR/accounting-poc2/recovery/receipt.json 6d3d5b092c0ee8273a657c83823d8465b215f2b1b66ec627dfde2d96b21fe587

Repository remained clean at epic 38f33c936b8249a57be81aebd639aa40c2f9de55 and story tip f94f306f94172f6dbf7ca6aa893f93d2e8376ed9.

### 2026-10-25T21:13:37Z speed
## Authorized Safe Capacity Reset — macOS Purge Only

Scope honored: ran macOS `/usr/sbin/purge` through the standard administrator authorization prompt, then remeasured capacity and reran both fixed floors. No additional files were deleted, and no spendability reconciliation, replay, promotion, admission, protected mutation, production mutation, merge, or push occurred.

Execution details:
- `/usr/bin/purge` was absent on this host; no state changed from that lookup.
- Unprivileged `/usr/sbin/purge` was refused with `Operation not permitted`.
- `sudo -n` found no cached credential; no password was embedded or logged.
- macOS administrator authorization then ran exactly `/usr/sbin/purge` successfully with exit 0.

Measured result:
- Before purge: 12,722,626,560 bytes available; swap usage 0 MiB.
- After purge: 12,726,525,952 bytes available; swap usage 0 MiB.
- Nominal reclaimed accounting: 3,899,392 bytes.
- Preparation floor 15,350,000,000 bytes: FAIL; shortfall 2,623,474,048 bytes.
- Replay floor 16,106,127,360 bytes: FAIL; shortfall 3,379,601,408 bytes.

The floors were not relaxed. GRRR-z3w9 remains open/blocked; capacity remains a mandatory gate.

Post-reset invariants:
- Epic HEAD unchanged: 38f33c936b8249a57be81aebd639aa40c2f9de55.
- Story tip unchanged: f94f306f94172f6dbf7ca6aa893f93d2e8376ed9.
- Repository clean.
- No GRRR-z3w9 cache-quarantine residue.
- Protected accounting hashes unchanged:
  - /Library/GRRR/accounting/active.json cc45b70fed84bae583959379559e8fc8336a0da3b4bca1750fc20c2848619f1b
  - /Library/GRRR/accounting/budget.sqlite 9fe4000c0c45b83cc818c29640e561167c34bd663abc26267e2a1b009f878234
  - /Library/GRRR/accounting/receipt.json 9f64395bec815a6bb2281d3b5d96d2356819138b1929b0a9881c16483c486dde
  - /Library/GRRR/accounting-poc2/active.json 9c5194dd12ff7601917fcccc293c459db09a41da8bad9fa9983cbef618d453f8
  - /Library/GRRR/accounting-poc2/recovery/receipt.json 6d3d5b092c0ee8273a657c83823d8465b215f2b1b66ec627dfde2d96b21fe587
