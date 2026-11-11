---
id: GRRR-my5n
title: "Recover a verifiable experiment snapshot after interruption"
status: closed
priority: 1
type: task
labels: [milestone-1, integration, accepted]
parent: GRRR-2t3h
created_at: 2026-10-20T03:19:02Z
created_by: speed
updated_at: 2026-10-21T20:46:48Z
content_hash: "sha256:298f3b6f4c3a330c4b6cd6ade46c416213c92b2397224190487fc02c508a3047"
was_blocked_by: [GRRR-gu87]
assignee: dev-GRRR-my5n
follows: [GRRR-gu87, GRRR-90te]
closed_at: 2026-10-21T20:46:47Z
close_reason: "Accepted: durable UID-320 ledger, crash recovery, trusted export, and identity denials proven"
led_to: [GRRR-c875, GRRR-bnkf, GRRR-w1lt, GRRR-43i8, GRRR-d8ji, GRRR-z3w9, GRRR-6sso]
blocks: [GRRR-0kb3]
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
I can inspect or replay the same trusted evidence after a crash without relying on a runner narrative.

## OUT OF SCOPE
Protected-registry admission intent/commit protocol lands in admission; this story supplies durable primitives and crash semantics, not registry authorization. Remote backup is optional later and not assumed.

## DIFF BUDGET
~6 files, under 1300 changed LOC. Gross overrun triggers PM investigation, not automatic rejection.

## Boundary Map
PRODUCES:
- research/ledger -> `append(principal: Principal, event: ValidatedEvent, expectedTip: Digest, key: IdempotencyKey) → Result<EventReceipt, Error>`; `verifySnapshot(snapshot: SnapshotRef, trustedAnchor: ReceiptDigest) → Result<VerifiedSnapshot, Error>`
- tests/integration/durable-evidence -> spec: real success and all enumerated failure cases via ./scripts/test-story durable-evidence; no mocks, mandatory absence fails

CONSUMES:
- GRRR-0g4n: research/ledger
  spec: `append(principal: Principal, event: ValidatedEvent, expectedTip: Digest, key: IdempotencyKey) → Result<EventReceipt, Error>`; `verifySnapshot(snapshot: SnapshotRef, trustedAnchor: ReceiptDigest) → Result<VerifiedSnapshot, Error>`
  Usage: append(authenticated evaluator, validatedEvent, expectedTip, key); verifySnapshot(exportRef, independently retained receipt digest) before trusting any projection.
- GRRR-gu87: research/budget
  spec: `reserve(principal: Principal, run: RunId, maximum: ResourceVector, key: IdempotencyKey) → Result<Reservation, Error>`; `settle(principal: Principal, reservation: ReservationId, actual: VerifiedUsage) → Result<SettlementReceipt, Error>`
  Usage: reserve(authenticated evaluator, run, worstCaseResourceVector, key) before dispatch; settle only trusted VerifiedUsage; retain unknown reservation.
- GRRR-0g4n: scripts/test-story
  spec: `./scripts/test-story <story-slug>` → exit 0 only when every required test passes; nonzero for missing infrastructure, skipped mandatory tests or failures (proposed test entrypoint, not installed)
  Usage: Read the versioned artifact or invoke the proposed test entrypoint exactly; validate identity and completeness before use; unknown/missing values block dependent authority.

## Story Acceptance Criteria
1. Evaluator-owned single writer appends canonical format-versioned hash-linked events with monotonic sequence and expectedTip compare-and-append. Runner/guest filesystem and API attempts to mutate history are denied. Updates/deletes of historical events are forbidden; rebuildable projections are separate.
2. Every event binds run/experiment/arm, sequence/prior digest, type/actor/times, base/candidate commits and built digests, evaluator/VM/toolchain, policy/spec/corpus/input, selector version/seed, complete gate inventory/results, measurements/units, usage/reservations, finding, review/action target, object hashes and recovery outcome. Unknown/not-run stays explicit, never zero/pass.
3. Stage/hash/durably publish immutable content-addressed objects before appending references. Crash at each publish/transaction boundary yields unreferenced objects or explicit interrupted work, never a passing receipt referencing absent data. Duplicate idempotency key returns original effect; conflicting payload or tip rejects.
4. Independent verifySnapshot checks chain/object hashes against a separately retained trusted receipt anchor and detects modified/truncated records, gaps, missing objects and stale snapshots. A self-consistent truncated chain without trusted comparison is not claimed detected.
5. Export manifest, chain tip, objects and verifier instructions outside disposable workspaces. A reviewer verifies an exported snapshot without trusting report generation; cleanup cannot remove forensic evidence. Local export is not host-loss/disaster-recovery assurance.
6. Recovery preserves reservations, marks unresolved work interrupted/recovery-required, blocks promotion and avoids silent retry of non-idempotent effects. Fault injection covers storage exhaustion, interrupted append, altered object and missing anchor; outputs retain failures and never manufacture pass.

## Testing Requirements
Integration tests: MANDATORY (no mocks). Include real success path plus every negative/error/concurrency case enumerated in the AC. Use real local VM, OS identities/permissions, evaluator, transactional store and pinned vlt where the path crosses them; mocks/stubs/fake receipts do not establish integration proof. Unit tests may supplement pure parsing/serialization; they cannot replace real integration. No skip-if-missing or environment-variable shortcut to green.
Proposed required command after implementation: ./scripts/test-story durable-evidence. The walking skeleton creates this test entrypoint; it must enumerate required tests, report counts and exit nonzero on missing prerequisites/failures. This command does not exist today. Capture actual commands, versions, stdout/stderr, exit codes, elapsed/runtime/review costs and artifact hashes; never fabricate results. Any required infrastructure authorization not yet granted blocks test execution explicitly, not story scope.

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


## nd_contract
status: accepted

### evidence
- PM closeout applied via pvg story accept on 2026-10-21.

### proof
- [x] Story closed after accepted label was applied.


## PM Decision
ACCEPTED [2026-10-21]: Delivery proof passed 9/9. PM independently verified the trusted export against anchor 0955178e5c5d47e512ebdd2505b7f31cb7bcbb60cd6b3503c493dfc1f5cf0a37, recovery retry/promotion denial, UID-321 and UID-501 filesystem denial probes, clean static scan, clean story branch, and no remaining process. The 61-file commit count is primarily preserved failed and successful integration evidence; implementation is six files and 913 insertions, explained by mandatory crash/recovery/export controls. The disclosed Homebrew ResourceWarning remains test cleanup debt and does not affect this acceptance path.

## nd_contract
status: accepted

### evidence
- Implementation/evidence commit 1c2a1c595703abf6a94e96792c5f1deb60841ca8.
- Real integration 4/4, no skips; full no-guest 159/159 under both interpreters; pvg verify 0 issues.

### proof
- [x] AC #1 through AC #6 independently rechecked against durable evidence.
- [ ] Admission and promotion remain intentionally blocked.

## nd_contract
status: delivered

### evidence
- Transitioned via pvg story deliver on 2026-10-21.

### proof
- [ ] Developer evidence block must remain authoritative above this contract.


## Implementation Evidence (DELIVERED)

Implementation commit: 1c2a1c595703abf6a94e96792c5f1deb60841ca8 on story/GRRR-my5n. Changed implementation paths: research/ledger.py, scripts/test-story, scripts/durable-identity-integration, tests/unit_durable_evidence.py, tests/integration/durable_evidence.py, and tests/integration/durable_probe.py. Durable evidence and all failed launcher attempts are preserved under docs/evidence/durable-evidence.

Final successful real-identity evidence: docs/evidence/durable-evidence/attempt-20261021T204415Z-c360927f. Private runtime: /private/tmp/grrr-durable-pbc2gjg6. External local export: /Users/Shared/GRRR/durable-evidence/durable-e9bf620ac3a3438d9aef883d9d7c02ee/export. Reviewer-readable copy: the export subtree in the evidence attempt. Snapshot ID: 83567fa3aaeb646ac040454f49070767b1a758bbecb650d462570833b51a11c2. Independently retained anchor: 0955178e5c5d47e512ebdd2505b7f31cb7bcbb60cd6b3503c493dfc1f5cf0a37.

### CI/Test Results

Commands run:
- /usr/bin/python3 -I -B -W error -m unittest discover -s tests -p unit_durable_evidence.py -v
- /usr/bin/python3 -I -B -m unittest discover -s tests -p "unit*.py"
- /opt/homebrew/bin/python3 -B -m unittest discover -s tests -p "unit*.py"
- ./scripts/test-story durable-evidence as UID 501 (expected fail-closed refusal)
- sudo ./scripts/test-story durable-evidence (parent-mediated UID-320/UID-321/UID-501 integration)
- PYTHONPATH=research /Users/speed/miniconda3/bin/coverage run ... unit_durable_evidence.py
- pvg verify --include-tests --format=text research/ledger.py tests/unit_durable_evidence.py tests/integration/durable_evidence.py tests/integration/durable_probe.py scripts/durable-identity-integration scripts/test-story
- git diff --check

Summary: focused durable units 7/7 passed; full no-guest units 159/159 passed under system Python and 159/159 under Homebrew Python. Required real integration: 4 required / 4 executed / 0 skipped / 0 failures / 0 errors. Actual UID-321 and UID-501 filesystem/API probes were denied. Coverage of research/ledger.py: 98% (228 statements, 4 missed). pvg verify: 4 recognized files, 0 issues. git diff --check passed. No QEMU/guest or paid dispatch was executed.

AC Verification:
| AC | Requirement | Evidence | Status |
|---|---|---|---|
| 1 | Evaluator-owned immutable hash-linked history | Real UID-320 test 1; SQL update/delete triggers denied; UID 321 API principal denied | PASS |
| 2 | Full explicit experiment/gate/usage/recovery schema | validate_durable_event and unit schema negatives; all eleven gates remain explicit pass/fail/not-run/error | PASS |
| 3 | Objects precede references; transaction/idempotency crash semantics | Real fault trigger left object unreferenced and rolled back event/idempotency; duplicate key behavior tested | PASS |
| 4 | Trusted-anchor snapshot verification | verifySnapshot detects altered, truncated, missing-object and wrong-anchor snapshots | PASS |
| 5 | Durable export outside runtime | export_snapshot wrote manifest, snapshot, object and verifier instructions to /Users/Shared and reviewer copy; verify_export passed | PASS |
| 6 | Recovery and fault behavior | Real interrupted event, recovery-required record, preserved reservations, no retry/promotion, altered-object and store-exhaustion controls passed | PASS |

LEARNINGS:
- Isolated Python does not implicitly make a staged script directory importable; the staged entrypoint must add its own root-controlled directory.
- macOS can surface a denied traverse as FileNotFoundError rather than PermissionError; denial probes must accept the OS-specific denial without accepting missing protected evidence.
- A public identity probe cannot live inside the UID-320 private code directory; it must be separately root-owned while the ledger stays private.
- Final export bytes can remain evaluator-private externally while a reviewer-readable copy is preserved in durable evidence.

DISCOVERED_BUG:
  title: Homebrew Python suite still emits SQLite ResourceWarnings
  context: The final full Homebrew run passed 159/159 but emitted 36 SQLite ResourceWarning lines during trusted-import AST/database work. System Python and real integration are clean; this is test-resource cleanup debt already disclosed on GRRR-gu87, not durable-ledger behavior.
  affected_files: tests/unit_trusted_import_closure.py, research/trusted_install.py
  discovered_during: GRRR-my5n

## nd_contract
status: delivered

### evidence
- Commit 1c2a1c595703abf6a94e96792c5f1deb60841ca8; story worktree clean; no push.
- Final real-identity evidence attempt 20261021T204415Z-c360927f passed 4/4 with zero skips and preserved all prior failed attempts.

### proof
- [x] AC #1 through AC #6 verified by real UID-320 integration and no-skip unit negatives.
- [ ] Admission/promotion remains blocked and downstream independent review is intentionally not claimed.

## nd_contract
status: in_progress

### evidence
- Claimed: 2026-10-21
- Epic integration includes accepted GRRR-gu87 at merge commit 0f04e11; durable v4 run evidence is available as a real recovery input.

### proof
- [ ] AC #1 through AC #6 pending.

## History
- 2026-10-20T03:19:02Z dep_added: blocked_by GRRR-gu87
- 2026-10-20T03:19:02Z dep_added: blocks GRRR-c875
- 2026-10-20T03:19:05Z dep_added: blocks GRRR-6sso
- 2026-10-21T20:15:24Z dep_removed: was_blocked_by GRRR-gu87
- 2026-10-21T20:27:05Z status: open -> in_progress
- 2026-10-21T20:27:05Z auto-follows: linked to predecessor GRRR-gu87
- 2026-10-21T20:27:05Z claimed by dev-GRRR-my5n
- 2026-10-21T20:45:40Z status: in_progress -> in_progress
- 2026-10-21T20:45:40Z auto-follows: linked to predecessor GRRR-90te
- 2026-10-21T20:46:47Z status: in_progress -> closed
- 2026-10-21T20:46:47Z dep_removed: no_longer_blocks GRRR-c875
- 2026-10-21T20:46:47Z dep_removed: no_longer_blocks GRRR-6sso
- 2026-11-11T21:15:21Z dep_added: blocks GRRR-2hib
- 2026-11-11T21:17:49Z dep_removed: no_longer_blocks GRRR-2hib
- 2026-11-11T21:17:56Z dep_added: blocks GRRR-0kb3

## Links
- Parent: [[GRRR-2t3h]]
- Blocks: [[GRRR-0kb3]]
- Was blocked by: [[GRRR-gu87]]
- Follows: [[GRRR-gu87]], [[GRRR-90te]]
- Led to: [[GRRR-c875]], [[GRRR-bnkf]], [[GRRR-w1lt]], [[GRRR-43i8]], [[GRRR-d8ji]], [[GRRR-z3w9]], [[GRRR-6sso]]

## Comments

### 2026-10-21T20:46:06Z speed
## Implementation Evidence

Implementation commit: 1c2a1c595703abf6a94e96792c5f1deb60841ca8. Final real-identity evidence is docs/evidence/durable-evidence/attempt-20261021T204415Z-c360927f. It contains a 4/4 no-skip integration log, trusted-anchor summary, UID-321/UID-501 denial probes, and a reviewer-readable snapshot/export copy. External export: /Users/Shared/GRRR/durable-evidence/durable-e9bf620ac3a3438d9aef883d9d7c02ee/export. Snapshot: 83567fa3aaeb646ac040454f49070767b1a758bbecb650d462570833b51a11c2. Anchor: 0955178e5c5d47e512ebdd2505b7f31cb7bcbb60cd6b3503c493dfc1f5cf0a37.

### CI/Test Results

Commands run:
- /usr/bin/python3 -I -B -W error -m unittest discover -s tests -p unit_durable_evidence.py -v
- /usr/bin/python3 -I -B -m unittest discover -s tests -p "unit*.py"
- /opt/homebrew/bin/python3 -B -m unittest discover -s tests -p "unit*.py"
- ./scripts/test-story durable-evidence as UID 501, then through the root parent launcher
- pvg verify --include-tests on all six changed implementation/test/script paths
- git diff --check

Summary: focused units 7/7; full units 159/159 under system Python and 159/159 under Homebrew; real integration 4/4, 0 skipped, 0 failures, 0 errors; ledger coverage 98%; pvg verify 4 recognized files, 0 issues. The Homebrew run disclosed 36 existing SQLite ResourceWarnings.

Commit SHA: 1c2a1c595703abf6a94e96792c5f1deb60841ca8

### AC Verification
- [x] AC #1: evaluator-only immutable hash-linked history and API/filesystem denial proven.
- [x] AC #2: full explicit event/gate/usage/recovery schema proven.
- [x] AC #3: object-first publication, transaction rollback, and idempotency crash semantics proven.
- [x] AC #4: modified/truncated/missing-object/wrong-anchor snapshots rejected against retained anchor.
- [x] AC #5: external manifest/snapshot/object/verifier export independently verified.
- [x] AC #6: interrupted work, preserved reservations, no retry/promotion, altered object, missing anchor, and store exhaustion handled.
- [ ] Admission and promotion intentionally remain blocked.

## nd_contract
status: delivered

### evidence
- Story commit 1c2a1c595703abf6a94e96792c5f1deb60841ca8; no push; worktree clean.

### proof
- [x] AC #1 through AC #6 delivered with real UID-320 evidence.
- [ ] Downstream admission/promotion remains intentionally blocked.
