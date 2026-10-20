---
id: GRRR-gu87
title: "Reject forged observations before spending evaluation authority"
status: in_progress
priority: 1
type: task
labels: [milestone-1, integration]
parent: GRRR-2t3h
created_at: 2026-10-20T03:19:02Z
created_by: speed
updated_at: 2026-10-20T23:57:21Z
content_hash: "sha256:3935d1b218f015e572f10add041526f6d904b4c01133cc99a54462e0f3c6123e"
blocks: [GRRR-my5n, GRRR-6sso]
was_blocked_by: [GRRR-90te]
assignee: dev-GRRR-gu87
follows: [GRRR-90te]
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
I can rely on measurements and spending limits even when a candidate lies or a runner retries.

## OUT OF SCOPE
Durable ledger crash matrix is a separate evidence slice; operator fence/admission races belong to stop/recovery and admission. This story must still enforce finite reservations and immediate launch checks.

## DIFF BUDGET
~7 files, under 1400 changed LOC. Gross overrun triggers PM investigation, not automatic rejection.

## Boundary Map
PRODUCES:
- research/budget -> `reserve(principal: Principal, run: RunId, maximum: ResourceVector, key: IdempotencyKey) → Result<Reservation, Error>`; `settle(principal: Principal, reservation: ReservationId, actual: VerifiedUsage) → Result<SettlementReceipt, Error>`
- research/execution -> `dispatch(principal: Principal, request: ApprovedInvocation, reservation: ReservationId, fence: RunEpoch, key: IdempotencyKey) → Result<DispatchReceipt, Error>`
- tests/integration/trusted-observation -> spec: real success and all enumerated failure cases via ./scripts/test-story trusted-observation; no mocks, mandatory absence fails

CONSUMES:
- GRRR-90te: research/execution
  spec: `dispatch(principal: Principal, request: ApprovedInvocation, reservation: ReservationId, fence: RunEpoch, key: IdempotencyKey) → Result<DispatchReceipt, Error>`
  Usage: dispatch(authenticated evaluator, allowlisted ApprovedInvocation, reservation.id, current RunEpoch, key); reject any Error, stale fence or unknown outcome.
- GRRR-90te: research/policy
  spec: `loadPolicy(principal: Principal, ref: PolicyDigest) → Result<VerifiedPolicy, Error>`
  Usage: loadPolicy(authenticated evaluator, pinned PolicyDigest); reject Error or unapproved scope before any work.
- GRRR-0g4n: research/ledger
  spec: `append(principal: Principal, event: ValidatedEvent, expectedTip: Digest, key: IdempotencyKey) → Result<EventReceipt, Error>`; `verifySnapshot(snapshot: SnapshotRef, trustedAnchor: ReceiptDigest) → Result<VerifiedSnapshot, Error>`
  Usage: append(authenticated evaluator, validatedEvent, expectedTip, key); verifySnapshot(exportRef, independently retained receipt digest) before trusting any projection.
- GRRR-0g4n: scripts/test-story
  spec: `./scripts/test-story <story-slug>` → exit 0 only when every required test passes; nonzero for missing infrastructure, skipped mandatory tests or failures (proposed test entrypoint, not installed)
  Usage: Read the versioned artifact or invoke the proposed test entrypoint exactly; validate identity and completeness before use; unknown/missing values block dependent authority.

## Story Acceptance Criteria
1. Run a real isolated challenge through versioned size-bounded structured IPC. Evaluator resolves protected inputs/expected results itself; runner sends only run/arm/challenge/variant/idempotency/reservation metadata. Decode raw outputs as data, never host instructions.
2. Reject unknown actions, role spoofing, malformed IDs, traversal/symlink artifacts, missing fields, oversized/truncated outputs, executable payloads and transport incompletion; candidate PASS logs or altered expected outputs cannot produce passing gates. Report explicit trusted-observation failure/not-run with evidence.
3. Demonstrate required race/locking observation using a pinned supervisor inaccessible to candidate UID, or block that mandatory gate. Attempt supervisor mutation and control-channel impersonation in the real guest. Host evaluator never runs candidate code or candidate-supplied harnesses.
4. Reserve worst-case ResourceVector money/currency, cumulative execution duration and review duration before dispatch. Atomically reject exhausted ceilings, unknown maxima and duplicate key with changed request. Test concurrent reservations cannot overspend POC $50/6h/60m or milestone $150/24h/3h, including POC carry-forward.
5. Only trusted metering settles usage; delayed/missing receipts retain conservative reservations. Sum overlapping execution and replay time, disclose selector overhead and preparation separately, track review sessions. Reservation alone is not a dispatch lease; validate current epoch at launch.
6. Force deadline, evaluator store exhaustion, malformed observation and lost executor response; watchdog stops new work and preserves unknown outcomes rather than retrying effects or counting missing cost as zero. Successful control-path receipt does not imply candidate correctness.

## Testing Requirements
Integration tests: MANDATORY (no mocks). Include real success path plus every negative/error/concurrency case enumerated in the AC. Use real local VM, OS identities/permissions, evaluator, transactional store and pinned vlt where the path crosses them; mocks/stubs/fake receipts do not establish integration proof. Unit tests may supplement pure parsing/serialization; they cannot replace real integration. No skip-if-missing or environment-variable shortcut to green.
Proposed required command after implementation: ./scripts/test-story trusted-observation. The walking skeleton creates this test entrypoint; it must enumerate required tests, report counts and exit nonzero on missing prerequisites/failures. This command does not exist today. Capture actual commands, versions, stdout/stderr, exit codes, elapsed/runtime/review costs and artifact hashes; never fabricate results. Any required infrastructure authorization not yet granted blocks test execution explicitly, not story scope.

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
# GRRR-gu87 WIP checkpoint — not delivered

Implementation SHA: `7286815d88cc752bb58f5a9e692278027a61a79e`.
Branch: `story/GRRR-gu87`; base: `b13022c55f78a4a5b14ed0198b42d9476aae9610`.
No privileged launcher, new VM profile, paid call or remote push was executed.

PROOF:

- `python3 -m unittest discover -s tests -p 'unit*.py' -v`: exit 0,
  **45 passed / 0 failed / 0 skipped**. Unit budget identity substitution is not
  OS permission evidence; SQLite concurrency/page-exhaustion is actual SQLite.
- `./scripts/test-story trusted-observation`: exit 1. Required 10, executed 1,
  skipped 0, failures 0, errors 2. Actual UID-320 prerequisite failure prevents
  nine accounting tests; proposal-only supervisor blocks the guest test.
  This is an explicit failed mandatory suite, not integration success.
- `python3 -m coverage run
  --data-file=/private/tmp/grrr-gu87-wip-7286815.coverage --source=research
  -m unittest discover -s tests -p 'unit*.py'`, then `coverage report`:
  **37% total research statement coverage**; budget 99%, observation 98%,
  evaluator 0%. Identity/VM paths are unproven, not discounted from coverage.
- `pvg verify research/budget.py research/observation.py research/common.py
  research/evaluator.py research/execution.py scripts/identity-integration
  scripts/test-story tests/unit_trusted_observation.py
  tests/integration/trusted_observation.py
  docs/TRUSTED-OBSERVATION-AUTHORIZATION.md
  docs/TRUSTED-OBSERVATION-PROFILE-PROPOSAL.json --include-tests --format=text`:
  exit 0, 7 recognized files scanned, 0 issues. This is static scanning, not proof
  of runtime behavior.
- `git diff --check`: exit 0. `git diff b13022c -- research/policy.py
  research/offline.py research/offline_execution.py research/offline-guest.sh`:
  empty. Existing resource/command profiles were not changed.
- Proposal file SHA-256:
  `1830a92ad2cbd91788051304ec8f6acaebf256b85065b2db2c07271b6906e3f6`.
  Supervisor/image hashes are **null**, so this proposal is not launchable.
- Evidence byte hashes: `SHA256SUMS` alongside this document.

### AC Verification

| AC | Implemented/tested WIP | Remaining mandatory proof | Status |
|---|---|---|---|
| 1 | Strict executor envelope and evaluator-owned exact synthetic assertion | Distinct approved supervisor, real structured guest challenge | BLOCKED |
| 2 | Strict fields, types, wire duplicates, bounds, malformed data, digest artifacts; legacy logs cannot pass trusted-observation | Real adversarial guest/service cases, artifact validator production wiring | INCOMPLETE |
| 3 | Mandatory gate explicitly not-run; separate profile staged disabled | Implement/pin/review supervisor and execute guest mutation/impersonation/race controls after approval | BLOCKED |
| 4 | Atomic vector reservations, ceilings, carry-forward and concurrent SQLite tests | Actual evaluator UID tests; offline shared-accounting integration | INCOMPLETE |
| 5 | Stored trusted meter receipts, held unknowns, additive time/review, overhead separation, typed launch epoch | Real metering/overlap/review/launch proof across service boundaries | INCOMPLETE |
| 6 | Accounting store page-exhaustion test and evaluator fail-closed paths | Actual evaluator store exhaustion, lost response and watchdog no-repeat evidence | INCOMPLETE |

LEARNINGS:

- Existing guest-root serial markers cannot establish a candidate-inaccessible
  supervisor; resource approval does not imply command-profile approval.
- POC and milestone must share one transactional accounting store. Pending
  receipts remain worst-case charges; no absence-to-zero conversion is valid.
- Explicit integer units and request binding make concurrency/ceiling tests
  deterministic without claiming that unit tests prove OS identity.
- Mandatory missing capabilities remain suite failures and blocked authority.
  No mock, skip, relabeled proposal or control receipt can manufacture success.

DISCOVERED_BUG:
  title: Trusted-observation supervisor capability and authorization missing
  context: Accepted synthetic/offline guest profiles execute as root; neither provides a candidate-inaccessible race/locking supervisor. A distinct profile requires explicit approval, implementation and parent identity execution.
  affected_files: research/execution.py, research/offline-guest.sh, docs/TRUSTED-OBSERVATION-PROFILE-PROPOSAL.json
  discovered_during: GRRR-gu87

Operator approval requested: approve development/review of the distinct profile
under the draft's exact limits, then separately approve final supervisor/input
image hashes and parent-mediated guest negative-control execution. Null hashes
cannot be approved for execution. See `docs/TRUSTED-OBSERVATION-AUTHORIZATION.md`.

AWAITING_PARENT_IDENTITY_RUN

## History
- 2026-10-20T03:19:02Z dep_added: blocked_by GRRR-90te
- 2026-10-20T03:19:02Z dep_added: blocks GRRR-my5n
- 2026-10-20T03:19:05Z dep_added: blocks GRRR-6sso
- 2026-10-20T23:46:09Z dep_removed: was_blocked_by GRRR-90te
- 2026-10-20T23:47:21Z status: open -> in_progress
- 2026-10-20T23:47:21Z auto-follows: linked to predecessor GRRR-90te
- 2026-10-20T23:47:21Z claimed by dev-GRRR-gu87

## Links
- Parent: [[GRRR-2t3h]]
- Blocks: [[GRRR-my5n]], [[GRRR-6sso]]
- Was blocked by: [[GRRR-90te]]
- Follows: [[GRRR-90te]]

## Comments
