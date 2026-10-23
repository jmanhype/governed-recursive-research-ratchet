---
id: GRRR-c875
title: "Stop a hung research run through independent trusted control"
status: closed
priority: 1
type: task
labels: [milestone-1, integration, accepted]
parent: GRRR-2t3h
created_at: 2026-10-20T03:19:02Z
created_by: speed
updated_at: 2026-10-21T21:23:31Z
content_hash: "sha256:5d9135c53581d4e5aed233968fb54faee82b5e82bb86ffe0a99f1503975e2278"
was_blocked_by: [GRRR-my5n]
assignee: dev-GRRR-c875
follows: [GRRR-my5n, GRRR-gu87, GRRR-90te, GRRR-0g4n]
closed_at: 2026-10-21T21:23:30Z
close_reason: "Accepted: real independent UID-separated safe-stop, durable fence/recovery, and admission gate evidence"
led_to: [GRRR-bnkf, GRRR-w1lt]
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
DELIVERY CORRECTION: The preceding Implementation Evidence and delivered proof are authoritative for commit 3f4a9cf2c52ae5992f76ff5350e63518ba1fad83; this note exists to let pvg story deliver append the final authoritative contract.


## nd_contract
status: accepted

### evidence
- PM closeout applied via pvg story accept on 2026-10-21.

### proof
- [x] Story closed after accepted label was applied.


## PM Decision
ACCEPTED [2026-10-21]: Delivery proof passed 9/9. PM independently verified all 18 final-evidence checksums, actual UID 320/321/501 integration 8/8 with zero skips/failures/errors, no mocks or environment gates, operator/runner/watchdog denial probes, bounded forced cessation, baseline preservation, durable recovery/admission fence evidence, clean static scan, and no remaining process. Scope remains host-control only; no guest, admission, promotion, accounting release, paid dispatch, or production mutation is claimed.

## nd_contract
status: accepted

### evidence
- Commit 3f4a9cf2c52ae5992f76ff5350e63518ba1fad83.
- Final evidence docs/evidence/safe-stop/attempt-20261021T211422Z-9f4ee3e0.

### proof
- [x] AC #1 through AC #7 reviewed against real identity evidence.
- [ ] Guest behavior, admission, promotion, and accounting release remain intentionally out of scope/blocked.

## nd_contract
status: delivered

### evidence
- Transitioned via pvg story deliver on 2026-10-21.

### proof
- [ ] Developer evidence block must remain authoritative above this contract.


## nd_contract
status: delivered

### evidence
- Transitioned via pvg story deliver on 2026-10-21.

### proof
- [ ] Developer evidence block must remain authoritative above this contract.


## Implementation Evidence (DELIVERED)

### Commit
- Branch: `story/GRRR-c875`
- Commit: `3f4a9cf2c52ae5992f76ff5350e63518ba1fad83`
- Subject: `feat(GRRR-c875): prove independent safe stop`
- Worktree was clean after commit; no push was performed.

### Summary
- Implemented evaluator-owned durable stop state, epoch/admission fencing, launch tracking, recovery markers, dual operator/watchdog Unix-socket endpoints, and evaluator-to-UID-321 trusted cancellation RPC.
- Added a UID-321 control worker that independently TERM/KILLs a real TERM-resistant sibling process and verifies the protected baseline hash.
- Added a parent-mediated real-identity launcher and mandatory `./scripts/test-story safe-stop` entrypoint. It stages root-controlled code, launches actual evaluator UID 320, hung runner/control-worker UID 321, and operator UID 501, preserves all attempts, and refuses nonroot execution.
- No QEMU, guest, paid call, protected admission, production mutation, accounting-stop release, or VM-behavior claim is made.

### CI/Test Results
Commands run:
- `sudo ./scripts/test-story safe-stop` (parent-mediated final exact-code run)
- `/usr/bin/python3 -I -B -m unittest discover -s tests -p unit_safe_stop.py -v`
- `/usr/bin/python3 -I -B -m unittest discover -s tests -p 'unit*.py'`
- `/opt/homebrew/bin/python3 -B -W error::ResourceWarning -m unittest discover -s tests -p 'unit*.py'`
- `/usr/bin/python3 -I -B -m py_compile research/control.py research/ledger.py research/control_worker.py research/isolated_entry.py research/trusted_transport.py tests/integration/hung_runner.py tests/integration/safe_stop.py tests/integration/safe_stop_probe.py tests/unit_safe_stop.py tests/unit_conservative_genesis.py scripts/safe-stop-identity-integration scripts/test-story scripts/conservative-genesis scripts/reconcile-installed-accounting`
- `pvg verify --include-tests --format=text <all explicit changed implementation/test/script paths>`
- `git diff --check`
- `PYTHONPATH=research /Users/speed/miniconda3/bin/coverage run --branch --source=control,trusted_transport -m unittest discover -s tests -p unit_safe_stop.py`, followed by `coverage report -m`

Summary:
- Real safe-stop integration: **8 required / 8 executed / 0 skipped / 0 failures / 0 errors**, elapsed 6.793 s, actual UIDs 320/321/501.
- Focused safe-stop unit tests: **7/7 passed**.
- Full no-guest unit suite: **166/166 passed** under system Python.
- Full no-guest unit suite: **166/166 passed** under Homebrew Python with `ResourceWarning` promoted to error.
- `py_compile`: exit 0.
- `pvg verify`: **10 recognized files scanned, 0 issues**.
- `git diff --check`: exit 0.
- Unit-only branch coverage: `research/control.py` **92%**; `trusted_transport.py` **15%**; combined measured sources **65%**. The UID-separated server/worker paths are exercised by the real integration but not instrumented by this unit coverage run.

Final real-identity evidence: `docs/evidence/safe-stop/attempt-20261021T211422Z-9f4ee3e0`.
- Private retained runtime: `/private/tmp/grrr-safe-stop-v39aekoq`.
- Manifest: exit 0, no cleanup error, identities evaluator 320 / runner 321 / operator 501, guest executed false, paid dispatch false, admission blocked.
- Authorized UID-501 stop returned operation `b40e7a8718a6d20c8cab5a689a2ddcc1294ce4586e63f734e9e0bf0a5bdfdc11`, durable receipt `01a21eee090376e8bbb3625a3af5dfe5c92944d6d2f73ca903afe79fd930c95b`, epoch 1, forced cessation true, baseline true, measured cancellation 1.013065625 s.
- UID-321 forged operator and UID-501 forged watchdog requests were both denied before payload reading.
- After service shutdown, UID-501 unavailable-control probe returned `Unavailable`, not success.
- Durable ledger SHA-256 in final evidence: `bccf3becf831e9c5ffb618490ca643c27f30c27af1339a6459d9339734b32b21`; full artifact inventory is in `SHA256SUMS`.

All failed/intermediate attempts are intentionally preserved:
- `attempt-20261021T210324Z-d2cead20`: nonroot fail-closed refusal.
- `attempt-20261021T210346Z-5d2f09dc`: tests passed but launcher cleanup failed for `run-crash`.
- `attempt-20261021T210508Z-9e752d4a`: first clean end-to-end launcher, before final isolated-entry routing.
- `attempt-20261021T210807Z-c2919925`: clean isolated-entry run, before all six hard-trigger records.
- `attempt-20261021T211329Z-82bb0bd2`: trigger-event assertion failure.
- `attempt-20261021T211422Z-9f4ee3e0`: final authoritative pass.

Operator-authorized regenerable cache cleanup:
- Initial full-suite setup failed the fixed 15.35 GiB preparation floor at about 11 GiB free.
- Safe `pnpm store prune` removed 1,153 unreferenced packages.
- Operator then authorized only HuggingFace xet, whisper-large-v3-turbo, and duplicate whisper-small caches. Exact-path inventory/hashes and result are in `docs/evidence/safe-stop/cache-cleanup-20261021`.
- Free space moved from 12,637,286,400 to 15,818,838,016 bytes (3,181,551,616 bytes freed by the three authorized entries); all named entries were absent afterward.

### pvg verify
- `VERIFY: PASSED (10 files scanned, 0 issues)`

### AC Verification
| AC | Requirement | Code Location | Test/Evidence Location | Status |
|---|---|---|---|---|
| 1 | Operator reaches independent evaluator control endpoint; runner/watchdog impersonation denied; urgent reason optional | `research/control.py:StopService`; `research/trusted_transport.py:AuthenticatedServer/control_call` | Final evidence `external-probes.json`; integration test 1 | PASS |
| 2 | Stop event, stopping state, and epoch commit atomically; same/distinct keys are idempotent without duplicate cancellation | `research/control.py:stop`; `research/ledger.py:append_atomic` | Unit idempotency/concurrency tests; integration test 3 and durable ledger | PASS |
| 3 | Final launch check serializes with stop, tracks pre-fence launches, and prevents post-fence starts | `research/control.py:register_launch/can_launch` | Integration race test 4; one legal ordering wins and the run stays fenced | PASS |
| 4 | Evaluator-directed trusted worker bounds TERM/KILL and verifies cessation/baseline without runner cooperation | `research/control_worker.py`; `control.py:terminate` | Final authorized/watchdog results; forced KILL in 1.013 s; baseline hash unchanged | PASS |
| 5 | Recording/cancellation failures never claim safe stop; recovery fences work and status remains truthful | `control.py:_record_recovery/_failed_stop/_write_recovery_marker` | Integration test 5 (worker unavailable) and test 8 (transaction crash/best-effort kill/marker) | PASS |
| 6 | Admission checks serialize on durable control state and record rejection without registry effects | `control.py:admission_fence`; `admission_fences` table | Unit admission test; integration test 7; every result has `registry_effect: false` | PASS |
| 7 | All hard triggers stop scheduling/admission and preserve evidence/baseline; unavailable control never reports success | `control.py:stop/admission_fence`; final operator unavailable probe | Integration test 6 records all six trigger reasons with one cancellation; post-integration UID-501 probe returns `Unavailable` | PASS |

### Remaining gates and residual scope
- None blocking this host-control story.
- Guest/VM cancellation behavior is intentionally not claimed because no guest was launched.
- Admission and promotion remain blocked; actual protected-registry admission races belong to the downstream admission story.
- Existing GRRR-POC-2 persistent accounting remains stopped and untouched.

LEARNINGS:
- macOS `with sqlite3.connect(...)` commits but does not close the connection; Homebrew Python exposes this as deferred `ResourceWarning`s. Explicit `contextlib.closing` plus an explicit commit where writes occur is required.
- A killed child can remain a zombie until the parent reaps it; cleanup must call `poll()`/`wait()` even when process-group signaling reports no live member.
- UID 320 cannot signal UID 321 directly. A separate UID-321 control worker, authenticated by peer UID and isolated from the hung runner process/session, provides the required independent sibling cancellation authority.
- Staged application modules must not mutate `sys.path`; extending the sole root-controlled `isolated_entry` allowlist preserves the existing import-closure invariant.
- Real identity launchers should preserve every intermediate failure, including a logically passing test run with failed cleanup, because process reaping is part of the safety guarantee.

DISCOVERED_BUG:
  title: Homebrew SQLite test cleanup emitted unclosed-connection warnings
  context: Full Homebrew unit execution passed but emitted 15 deferred SQLite ResourceWarnings. Tracemalloc identified `scripts/conservative-genesis`, `scripts/reconcile-installed-accounting`, and `tests/unit_conservative_genesis.py`. They used `with sqlite3.connect(...)` without `closing`. The conservative-genesis build path also needed an explicit commit after replacing transaction context semantics. All were fixed and the final Homebrew run passes 166/166 with ResourceWarning promoted to error.
  affected_files: scripts/conservative-genesis, scripts/reconcile-installed-accounting, tests/unit_conservative_genesis.py
  discovered_during: GRRR-c875

## nd_contract
status: delivered

### evidence
- Commit `3f4a9cf2c52ae5992f76ff5350e63518ba1fad83` on `story/GRRR-c875`.
- Final real-identity evidence `docs/evidence/safe-stop/attempt-20261021T211422Z-9f4ee3e0`: 8/8, 0 skipped, UIDs 320/321/501.
- Full units 166/166 under both interpreters; pvg verify 0 issues; py_compile and git diff --check passed.

### proof
- [x] AC #1: independent authenticated operator path and identity denials proven with real UIDs.
- [x] AC #2: atomic durable stop transaction, epoch, receipts, and idempotency proven.
- [x] AC #3: serialized launch/stop race, tracking, and post-stop fence proven.
- [x] AC #4: independent bounded TERM/KILL cancellation and baseline verification proven.
- [x] AC #5: unavailable cancellation and failed recording remain recovery-required/fenced, never safe-stopped.
- [x] AC #6: durable control-side admission-fence rejection proven without registry effects.
- [x] AC #7: all six hard triggers preserve evidence/baseline and unavailable control reports no false success.


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
- 2026-10-21T21:18:05Z status: in_progress -> in_progress
- 2026-10-21T21:18:06Z auto-follows: linked to predecessor GRRR-gu87
- 2026-10-21T21:18:24Z status: in_progress -> in_progress
- 2026-10-21T21:18:24Z auto-follows: linked to predecessor GRRR-90te
- 2026-10-21T21:18:45Z status: in_progress -> in_progress
- 2026-10-21T21:18:45Z auto-follows: linked to predecessor GRRR-0g4n
- 2026-10-21T21:23:30Z status: in_progress -> closed
- 2026-10-21T21:23:31Z dep_removed: no_longer_blocks GRRR-bnkf
- 2026-10-21T21:23:31Z dep_removed: no_longer_blocks GRRR-6sso

## Links
- Parent: [[GRRR-2t3h]]
- Was blocked by: [[GRRR-my5n]]
- Follows: [[GRRR-my5n]], [[GRRR-gu87]], [[GRRR-90te]], [[GRRR-0g4n]]
- Led to: [[GRRR-bnkf]], [[GRRR-w1lt]]

## Comments

### 2026-10-21T21:21:49Z speed
## Implementation Evidence

### CI/Test Results
Commands run:
- sudo ./scripts/test-story safe-stop
- /usr/bin/python3 -I -B -m unittest discover -s tests -p unit_safe_stop.py -v
- /usr/bin/python3 -I -B -m unittest discover -s tests -p 'unit*.py'
- /opt/homebrew/bin/python3 -B -W error::ResourceWarning -m unittest discover -s tests -p 'unit*.py'
- pvg verify --include-tests --format=text on explicit changed implementation/test/script paths
- git diff --check

Summary:
- Real UID-320/321/501 safe-stop integration: 8/8 executed, 0 skipped, 0 failures, 0 errors.
- Focused unit suite: 7/7. Full no-guest unit suites: 166/166 under system Python and 166/166 under Homebrew Python.
- pvg verify: 10 recognized files, 0 issues. py_compile: exit 0. git diff --check: exit 0.
- Final evidence: docs/evidence/safe-stop/attempt-20261021T211422Z-9f4ee3e0.

SHA: 3f4a9cf2c52ae5992f76ff5350e63518ba1fad83

### AC Verification
- [x] AC #1: real UID-501 operator path, UID-321/UID-501 denial probes, and optional urgent reason proven.
- [x] AC #2: atomic durable stop/epoch transaction, same-key receipt, distinct-key reference, and one cancellation proven.
- [x] AC #3: real launch/stop race serializes, tracks pre-fence work, and rejects post-fence launch proven.
- [x] AC #4: separate UID-321 worker forced KILL in 1.013065625 s and verified baseline proven.
- [x] AC #5: unavailable cancellation and failed recording remain recovery-required/fenced, never safe-stopped.
- [x] AC #6: durable admission-fence rejection with no registry effect proven.
- [x] AC #7: all six hard triggers preserve evidence/baseline; unavailable control returns Unavailable, never success.

LEARNINGS:
- Explicit SQLite closing/reaping and root-controlled import routing were required for a clean exact-identity run.
- Complete failure history and operator-authorized cache inventory are preserved in docs/evidence/safe-stop.

DISCOVERED_BUG:
  title: Homebrew SQLite test cleanup emitted unclosed-connection warnings
  context: Existing with sqlite3.connect(...) paths did not close connections. They were fixed with contextlib.closing and an explicit commit where needed; the final warning-as-error suite passes.
  affected_files: scripts/conservative-genesis, scripts/reconcile-installed-accounting, tests/unit_conservative_genesis.py
  discovered_during: GRRR-c875

## nd_contract
status: delivered

### evidence
- Commit SHA: 3f4a9cf2c52ae5992f76ff5350e63518ba1fad83.
- Final real-identity evidence docs/evidence/safe-stop/attempt-20261021T211422Z-9f4ee3e0 passed 8/8 with zero skips.

### proof
- [x] AC #1 through AC #7 verified by real integration, full units, pvg verify, py_compile, and git diff --check.

