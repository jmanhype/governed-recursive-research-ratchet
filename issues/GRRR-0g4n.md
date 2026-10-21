---
id: GRRR-0g4n
title: "Observe one bounded challenge through the trusted research path"
status: closed
priority: 1
type: task
labels: [milestone-1, integration, walking-skeleton, accepted]
parent: GRRR-2t3h
created_at: 2026-10-20T03:19:01Z
created_by: speed
updated_at: 2026-10-20T15:56:23Z
content_hash: "sha256:d132927e961096cdee6d427ebd8997bbdef492f85e7f3acb7acbbf249f3f94bd"
assignee: dev-GRRR-0g4n
closed_at: 2026-10-20T15:56:23Z
close_reason: "Accepted: independently verified bounded synthetic VM path, all seven ACs, 12/12 real integration tests, preserved hash-bound evidence and explicitly scoped unit coverage."
led_to: [GRRR-90te, GRRR-gu87]
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
I can see one real bounded challenge travel end to end and know exactly what has and has not been proven before investing in the full milestone.

## OUT OF SCOPE
Full baseline/dependency validation lands in the preflight story; transport adversarial matrix, durable recovery, full corpus, comparative statistics, admission and accessible review each have separate child slices. These are substantive extensions, not permission to omit minimum isolation, bounds or fail-closed behavior here.

## DIFF BUDGET
~10 files, under 1800 changed LOC; the cross-layer skeleton is intentional and PM must investigate overruns. Gross overrun triggers PM investigation, not automatic rejection.

## Boundary Map
PRODUCES:
- research/policy -> `loadPolicy(principal: Principal, ref: PolicyDigest) → Result<VerifiedPolicy, Error>`
- research/execution -> `dispatch(principal: Principal, request: ApprovedInvocation, reservation: ReservationId, fence: RunEpoch, key: IdempotencyKey) → Result<DispatchReceipt, Error>`
- research/ledger -> `append(principal: Principal, event: ValidatedEvent, expectedTip: Digest, key: IdempotencyKey) → Result<EventReceipt, Error>`; `verifySnapshot(snapshot: SnapshotRef, trustedAnchor: ReceiptDigest) → Result<VerifiedSnapshot, Error>`
- scripts/test-story -> `./scripts/test-story <story-slug>` → exit 0 only when every required test passes; nonzero for missing infrastructure, skipped mandatory tests or failures (proposed test entrypoint, not installed)
- docs/runner-cli.md -> schema: operator-approved standalone runner grammar mapping start/status/review/evidence/decide/stop/recover intentions; version, action, flags, output, exit status; no invented pvg extension
- research/runner -> fields: run ID, arm, challenge ID, pinned variant digest, idempotency key and reservation request; approved CLI grammar routes requests, never expected results or bypass flags
- research/evaluator -> fields: bounded raw observation, exit/signal, resource use, transport completion; evaluator-owned assertions produce measurements, individual gates, finding classification and object digests
- tests/integration/bounded-challenge -> spec: real success and all enumerated failure cases via ./scripts/test-story bounded-challenge; no mocks, mandatory absence fails

CONSUMES:
- (none — root walking skeleton; contracts are proposed, not existing APIs)

## Story Acceptance Criteria
1. Before implementation of the CLI or any experiment, capture operator approval of a standalone runner grammar, scope, policy, VM/identity setup and measured numeric limits. Discover existing pvg capabilities without changing pvg core. Approval absence blocks execution; help explains how to inspect and stop.
2. An operator submits one approved synthetic clean challenge and one deliberately faulty frozen variant. A real runner invokes a real evaluator and isolated executor; trusted assertions produce distinct observed results, durable hash-bound event receipts and readable reports naming run, candidate, evaluator, policy and snapshot. Candidate PASS text never substitutes for assertions. This is a bounded path demonstration, not defect verification/admission.
3. Establish public API type signatures (@spec/typespecs or language equivalent), validated config registration, DLP-style metadata allowlisting, budget/rate limiting, audit logging and structured error handling in the actual path. Integration tests: MANDATORY (no mocks). Tests fail closed on missing dependencies or skipped mandatory gates; CI uses the same entrypoint and cannot green a skipped suite.
4. Establish no automatic main merge, no production mutation, no autonomous patch generation, no harness adaptation and no unapproved paid calls as denied capabilities, with negative tests and visible blocked outcomes, not comments only.
5. The minimal policy contains the full mandatory gate inventory and reports unimplemented replay/review/admission as not-run; missing/failed/error gates block verified findings and admission. No success-looking exit or report hides a blocked requested effect. Full comparison, admission and recovery stay explicitly unavailable until their stories land.
6. Demonstrate a real VM clean reset, disabled guest networking/sharing, distinct evaluator permissions, bounded output, a finite reservation, evaluator-side deadline and direct emergency stop before the first synthetic execution. Reject missing policy, unauthorized caller, malformed input, duplicate mismatched key, stale epoch, absent VM and forged PASS output. Do not defer minimum safe execution to a later story.
7. Provide an independently checkable receipt plus preserved artifacts outside disposable candidates. A failing challenge leaves an inspectable report and no protected mutation. Plain-text/Markdown/JSON minimal outputs share snapshot ID; execution completion does not imply Verified defect, Approve or admission.

## Testing Requirements
Integration tests: MANDATORY (no mocks). Include real success path plus every negative/error/concurrency case enumerated in the AC. Use real local VM, OS identities/permissions, evaluator, transactional store and pinned vlt where the path crosses them; mocks/stubs/fake receipts do not establish integration proof. Unit tests may supplement pure parsing/serialization; they cannot replace real integration. No skip-if-missing or environment-variable shortcut to green.
Proposed required command after implementation: ./scripts/test-story bounded-challenge. The walking skeleton creates this test entrypoint; it must enumerate required tests, report counts and exit nonzero on missing prerequisites/failures. This command does not exist today. Capture actual commands, versions, stdout/stderr, exit codes, elapsed/runtime/review costs and artifact hashes; never fabricate results. Any required infrastructure authorization not yet granted blocks test execution explicitly, not story scope.

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

## Historical contract (superseded)
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
BLOCKED BEFORE DEVELOPER DISPATCH:
- AC #1 requires separate operator approval of standalone runner grammar, scope, policy, VM/identity setup, and measured numeric limits; those approvals are not yet recorded.
- AC #6 requires a real local VM with clean reset, disabled networking/sharing, distinct evaluator permissions, bounded output, finite reservation, evaluator deadline, and direct emergency stop.
- Measured host preflight on 2026-10-19: macOS 27.0, Apple M2 Pro, 32 GB RAM, 10 cores, Hypervisor support=1, only 8 GB free; limactl/QEMU/UTM/Parallels/VirtualBox/vmrun/colima/podman unavailable; Docker CLI exists but daemon is unreachable.
- Architecture forbids silent downgrade to unrestricted host/container execution. No implementation, experiment, commit, or push occurred.
- Next required operator decision: authorize a verified VM provisioning path and safe space plan, or provide another approved isolated execution host.
VM PREFLIGHT AUDIT (read-only, 2026-10-20):
- Data volume has approximately 3 GB free (100% capacity); initial earlier reading was 8 GB.
- Hypervisor support is present on macOS 27.0 / Apple M2 Pro / 32 GB RAM.
- No local VM tool is installed: limactl, QEMU, UTM, Parallels, VirtualBox, vmrun, Colima, and Podman unavailable. Docker CLI exists but daemon is unreachable.
- Read-only audit found safe/regenerable candidates requiring explicit cleanup authorization: Codex Sparkle update staging ~9.1 GiB; old pnpm v3 store ~7.2 GiB; CoreSimulator dyld cache ~3.5 GiB; Gradle caches ~1.7 GiB; additional updater caches are available under Library/Caches.
- Running app check: ChatGPT executes from /Applications, not the Sparkle Installation cache. No active pnpm/Gradle/CoreSimulator/Sparkle process was observed.
- Candidate provisioning path under review: direct QEMU with -net none, disposable snapshot disk, no host sharing, bounded process/output/deadline, and evaluator-owned control. QEMU is GPL-2.0-only and therefore requires separate license-boundary approval even as an external tool.
- No cache deletion, package installation, VM creation, source implementation, commit, or push occurred.
VM PREFLIGHT ADDENDUM: pnpm 10.28.2 reports its active store as /Users/speed/Library/pnpm/store/v10; the 7.2 GiB v3 store is stale relative to the current CLI. No deletion occurred.
AUTHORIZED CACHE CLEANUP RESULT (2026-10-20):
- Removed only Codex Sparkle Installation staging: 9.1 GiB, 19,900 files.
- Removed only obsolete pnpm v3 store: 7.3 GiB, 419,743 files.
- Recorded manifest at .tmp-sr_pm/vm-cleanup-manifest.txt.
- Active pnpm 10.28.2 store remains /Users/speed/Library/pnpm/store/v10.
- Free space increased from 4 GB to 14 GB, short of the preflight requirement of at least 15 GB.
- QEMU installation intentionally did not start because the authorized sequence required the 15 GB check first. No additional cache was deleted.
QEMU NO-NETWORK VM PREFLIGHT PASS (2026-10-20):
- Operator authorized additional CoreSimulator dyld cleanup; 3.5 GiB removed, free space reached 17 GB, then QEMU was installed.
- QEMU executable/version: /opt/homebrew/bin/qemu-system-aarch64 11.1.2; external GPL-2.0-only tool boundary recorded in VM-PREFLIGHT-2026-10-20.md.
- Alpine virt 3.22.6 aarch64 ISO SHA-256 09d601858d72484c89d576fb735215cccf54a92a03e67ca4a7fa7e4b8ec4a7a2; kernel and initramfs hashes are recorded in the preflight report.
- Two independent boots used -net none, -snapshot, -monitor none, -no-reboot, 512 MiB, one vCPU, and no host-share device. Both reached localhost login, preserved the ISO hash, stayed below 1 MiB output, and terminated on SIGTERM within grace.
- Run 1: marker 6422.769 ms; stop 63.655 ms. Run 2: marker 6545.848 ms; stop 59.223 ms. No eth0 text observed; QEMU -net none is the controlling isolation evidence.
- Report: VM-PREFLIGHT-2026-10-20.md. Machine evidence: .tmp-sr_pm/vm/qemu-no-network-preflight.json plus two run logs.
- Still not proven: standalone runner grammar, restricted OS identities/ACLs, authenticated evaluator control transport, durable ledger, trusted arbitrary-output observation, vlt challenge, independent replay/admission. No story implementation or experiment occurred.
VM PREFLIGHT EVIDENCE DURABILITY NOTE: durable copies of cleanup manifests, audit output, QEMU JSON result, and both boot logs now live under docs/evidence/vm-preflight/. VM-PREFLIGHT-2026-10-20.md references those durable paths. The files are not yet committed; commit requires separate operator authorization.
OPERATOR IMPLEMENTATION APPROVAL (2026-10-20):
- Approved standalone bin/grrr grammar, dedicated _grrr_evaluator and _grrr_runner identities, measured limits, local evidence commit, and dispatch of this story.
- Approved limits: QEMU 512 MiB / 1 vCPU; 30s boot deadline; 2s stop acknowledgement target; 5s SIGTERM grace then forced kill; 1 MiB guest output cap; 5-minute single-challenge deadline; 15 GB minimum free space; networking/host shares disabled.
- Approved record: docs/IMPLEMENTATION-APPROVAL-2026-10-20.md.
- Evidence/approval commit on main and fast-forwarded story/epic branches: c2970356436531565711fb3c2df24eb91c3ed510.
- Dispatch worktree: .claude/worktrees/dev-GRRR-0g4n on story/GRRR-0g4n.
- Authorization remains limited to this story. No production access, automatic main merge, autonomous patch generation, harness adaptation, or unapproved paid calls.
IDENTITY PROVISIONING BLOCKER (2026-10-20):
- Operator approved creating _grrr_evaluator (UID/GID 320) and _grrr_runner (UID/GID 321), both hidden, non-login, non-admin.
- Noninteractive sudo is unavailable ( reports a password is required).
- An AppleScript administrator-authorization attempt was cancelled after the prompt was not approved/visible for over three minutes. No account was created.
- Idempotent root provisioning script is staged at .tmp-sr_pm/provision-grrr-identities-root.sh; it fails if either account or UID/GID already exists.
- Developer dispatch is intentionally withheld until identities exist, because GRRR-0g4n AC #6 requires distinct evaluator permissions and must fail closed.
IDENTITY PROVISIONING COMPLETE (2026-10-20):
- _grrr_evaluator: UID/GID 320, hidden, UserShell /usr/bin/false, NFSHomeDirectory /var/empty, password disabled, no admin membership.
- _grrr_runner: UID/GID 321, hidden, UserShell /usr/bin/false, NFSHomeDirectory /var/empty, password disabled, no admin membership.
- Operator supplied administrator authorization interactively; the credential was not stored, echoed to artifacts, or passed to any worker.
- Noninteractive sudo remains unavailable to ordinary shell commands. Identity-launched integration commands must use an explicitly approved parent-mediated path; do not give credentials to the developer.
IMPLEMENTATION CHECKPOINT (not delivery): commit d136f7d1c086f3966d6ba2bf50079bea75df20af on story/GRRR-0g4n. Added 14 files/1085 lines: typed standard-library CLI, peer-authenticated restricted evaluator and executor, fixed synthetic packet hashes, QEMU isolation and stop adapter, SQLite hash-linked event/object snapshots, projections, and synchronous parent identity launcher. Parent clarified grrr-walk-001 CLEAN newline versus forged PASS newline semantics; no vlt defect claim. python3 tests/unit_contracts.py: 5/5 pass. pvg verify on explicit source/test/script paths: PASSED, 9 recognized files scanned, 0 issues. git diff --check: exit 0. Mandatory ./scripts/test-story bounded-challenge: exit 1, required 8, executed 0, skipped 0, errors 1 because evaluator endpoint absent. This is expected fail-closed infrastructure evidence, not integration proof. Requires parent-mediated root scripts/identity-integration with approved asset directory; no sudo or credentials used. No delivery/acceptance asserted. Remaining proof includes real identity/VM execution, missing asset/policy negative controls and full AC audit; current tests do not establish all required ACs. pvg notes search failed because worktree .vault missing; parent identified known local discovery issue, no global notes queried.
IDENTITY RUNTIME FIX CHECKPOINT (not delivery): commit 3c93078d3e9e2c73d1196a24e5414af6b7f9864b. Parent run at d136f7d failed exit 1 before evaluator start: runner Python could not open Documents-path execution.py (EACCES). TCC remains suspected, not proven. Original runner.log SHA256 2ee7b8a6d8e8118399c7747c12addc6a71e996933dd6d2e07bba7eab39775917 and manifest SHA256 6389da8faf46dad72095e74493645d6925ae8124e64e31307364d65f4934c4fa verified unchanged and committed; old .runtime untouched. Parent launcher now creates fresh root-owned mode0711 /private/tmp/grrr-* runtime, copies only approved code/assets, keeps service dirs mode0700, runs services/probe from temporary path, and records each attempt separately. Operator binding is mode0600 and peer authentication remains kernel-based in both directions. Runtime/protected-artifact denied-read and impersonation probes remain mandatory. Unit tests: 7/7 pass. py_compile and git diff --check exit 0. pvg verify explicit modified paths: 5 recognized files, 0 findings. Mandatory suite remains fail-closed before privilege run: required8/executed0/skipped0/errors1, absent runtime binding. Non-root identity launcher exits1 without creating runtime. Awaiting parent-mediated identity integration; no delivery/acceptance claim.
PREFLIGHT REPAIR CHECKPOINT (not delivery): commit 8f85947bfdac01ade6ced151afa8a847b768421a. Parent-exported read-only protected diagnostic proves event4 finished at1.298718459s with GateBlocked Guest isolation/reset check failed; ANSI-colored lo from interactive ls did not satisfy exact newline-lo-newline check. Operator stop occurred later at event5, so historical error is not relabeled as a stop race. Replaced ls with exact shell interface-name printing, retained strict isolation checks, added authenticated bootstrap readiness and stop-test readiness polling. Concurrent EOF checks recheck stop fence; preflight true requires Stopped error, verified isolation, cessation and unchanged assets. Validated request keys bind before preflight gate, including denied requests. Test saved ID renamed to saved_run_id. Unit tests9/9 pass, py_compile and diff-check pass, pvg verify4 recognized files/0 findings. Original attempt permissions/test-output/manifest hashes remain parent-reported values and are now committed with read-only diagnostic. Fresh parent identity run still required; no integration success or delivery claimed. Evidence preservation increases total diff beyond original approximate line/file budget; code remains a small Python-standard-library slice, added bulk is captured diagnostic/attempt evidence.
MANDATORY NEGATIVE CONTROL CHECKPOINT (not delivery): commit dee02e80f6a99c3c8a21f79bd0e15390ff85a4b9. Preserved successful 8-test attempt at integration commit8f85947 and independently verified12 manifest artifact hashes, receipt chains/anchors, raw CLEAN/PASS bytes, completed clean/faulty assertions,11 gates, stopped preflight, unchanged assets and output bounds; final-audit.json records measurements. Parent correctly required actual absence/overflow/deadline proof before delivery. Added separate restricted missing-policy and absent-QEMU runtimes using same source hashes; root-owned read-only executor config points only to approved QEMU or dedicated absent path, never modifies installed QEMU. Added evaluator-authored output flood and five-second command-deadline safety probes, distinct from candidate semantics. Full mandatory entrypoint now enumerates12 test methods and requires root-generated absence receipts plus active probe evidence. Raw console bytes stored separately as content objects to avoid nested-hex wire growth. Unit9/9 pass; pvg verify explicit paths10 recognized files0 findings; py_compile and diff-check pass. New12-test attempt requires parent identity launcher; no delivery or new integration-success claim.
DELIVERY COMMIT: 83bab97b3f5edea53005f4cb18374a24faaa12b6 on story/GRRR-0g4n; clean worktree, no push. Exact parent integration source commit dee02e80f6a99c3c8a21f79bd0e15390ff85a4b9. Evidence and independent audit committed at83bab97. Final scripts/verify-evidence check exit0,20 manifest artifacts verified;12/12 integration tests and9/9 unit tests; pvg verify10 recognized files0 issues. PM review required; developer is not accepting or closing.
UNIT-ONLY COVERAGE ADDENDUM. SHA: 10c0862f3e1c82b449d76f9342f2f89703e3dbaa. Executed /Users/speed/.pyenv/shims/coverage run --data-file=.tmp-sr_pm/unit.coverage --source=research --context=unit-only-research tests/unit_contracts.py, then coverage report --data-file=.tmp-sr_pm/unit.coverage --precision=2 -m and coverage json --data-file=.tmp-sr_pm/unit.coverage --pretty-print --show-contexts -o docs/evidence/bounded-challenge/unit-coverage.json; all exit0. Python3.10.14 and Coverage.py7.9.1. Nine unit tests passed. UNIT-ONLY line coverage for research/:112/567 statements=19.75%; common46.36%, evaluator0.00%, execution14.37%, ledger0.00%, policy47.06%, runner55.77%. Raw transcript unit-coverage.txt SHA2567ef31a3871d35dec5683a46ca409a25b4cf070d7dc8ceb0fda2c91b397ffa25c; JSON SHA2564560925e18f0ec1213efd44b15c32b5ec5104990626f595b81bf0fc8a47ba3d7. No identity/VM integration coverage is measured or inferred. No privileged VM integration rerun or implementation behavior change.


## nd_contract
status: accepted

### evidence
- PM closeout applied via pvg story accept on 2026-10-20.

### proof
- [x] Story closed after accepted label was applied.


## PM Decision
ACCEPTED [2026-10-20]: Independent review of delivery 10c0862f3e1c82b449d76f9342f2f89703e3dbaa meets the bounded synthetic walking-skeleton bar, not vlt verification, admission or production readiness.

Reviewed changed-file diff, public type annotations, actual policy/authentication/budget/audit wiring, approved grammar, documentation freshness, stub markers and trust boundaries. No incomplete stubs, missing public return types, credentials, or out-of-scope production capabilities found. UID320/321 permission and forged-peer probes, root-owned read-only executor config, QEMU network/snapshot/no-share settings and protected assets are backed by source and preserved real-run evidence. All five denied capabilities are exercised. No new DISCOVERED_BUG identified.

Diff-budget investigation: original 68 files/2670 additions includes approximately 1507 lines of source/scripts/tests and substantial preserved failure/success artifacts. New delivery adds only two coverage artifacts (7586 lines, mostly detailed Coverage.py JSON). The resulting 70 files/10256 additions are evidence-driven, not expanded implementation scope; preserving audit evidence justifies the overrun.

Coverage proof gap repaired before decision: 19.75% unit-only research coverage (112/567 statements), nine passing supplementary tests, Python 3.10.14/Coverage.py 7.9.1. Evaluator/ledger are 0% in this unit-only measurement. Privileged integration coverage is unknown, not inferred; the separate actual integration transcript proves 12/12 required tests executed with zero skips/failures/errors. No story coverage threshold exists. This is adequate for this bounded slice, not comprehensive security testing.

Mandatory-skill applicability: shared pvg nd/story transitions recorded; bounded developer delivery and independent PM review observed. Existing-source structural discovery is conditional in this greenfield slice; no existing API wiring was assumed. No vlt invocation is part of this synthetic path. Local vault discovery failure is explicitly disclosed, not treated as successful discovery.

## nd_contract
status: accepted

### evidence
- Reviewed HEAD 10c0862f3e1c82b449d76f9342f2f89703e3dbaa; git status --short empty; git diff --check epic/GRRR-2t3h...HEAD exit 0.
- pvg story verify-delivery GRRR-0g4n: 9 passed, 0 failed.
- pvg verify explicit research modules, CLI, scripts and tests --format=text: 10 recognized files, 0 issues. Extensionless files inspected separately.
- git diff --quiet dee02e80f6a99c3c8a21f79bd0e15390ff85a4b9 HEAD -- research scripts/identity-integration tests bin/grrr: exit 0; integrated source unchanged.
- ./scripts/verify-evidence docs/evidence/bounded-challenge/attempt-20261020T153803Z-4d13bc7b: exit 0; 20 artifact hashes, event chains/anchors/objects, real absence and active safety controls checked. No privileged integration rerun.
- shasum -a 256 matched manifest 5758264cf727dd9abd1c84e9b3b3c0d7b28575f2919271c5a105ebc26e9def54, test transcript 3a4fa144133976f27014091dfd3dec95e72dca767df28b2907a7eb36ae396bfe and negative controls 7b6ad2252dd79ac23c68feea7dff93704e525c4d1e23c1bfd3764c89a0271442.
- Coverage hashes matched transcript 7ef31a3871d35dec5683a46ca409a25b4cf070d7dc8ceb0fda2c91b397ffa25c and JSON 4560925e18f0ec1213efd44b15c32b5ec5104990626f595b81bf0fc8a47ba3d7; JSON totals reconcile 112 covered/567 statements.

### proof
- [x] AC #1: Prior approved standalone grammar, identities and numeric limits; pvg core unchanged; help and inspection/stop documented.
- [x] AC #2: Real runner/evaluator/VM/ledger path produces CLEAN pass and forged-PASS fail with receipts and identity-bound reports.
- [x] AC #3: Typed APIs, strict registration/allowlists, peer credentials, finite reservation/rate limit, audit and errors wired; real mandatory entrypoint cannot skip green.
- [x] AC #4: All five denied capabilities return tested GateBlocked outcomes.
- [x] AC #5: Eleven gates present; replay/specification/review/approval not-run; Verified and admission blocked without false aggregate success.
- [x] AC #6: Reset/offline/no-share VM, separated identities, direct stop before candidate, active output/deadline probes and all enumerated negative controls supported by artifacts.
- [x] AC #7: Independent hash/chain/anchor audit and report snapshot parity; faulty report retained, assets unchanged, no defect/admission claim.

Residual boundaries remain explicit: five-second command deadline actively tested, 300-second watchdog configured but not expired; hosted CI, full vlt baseline, replay, recovery, review/admission and comprehensive preparation/review accounting are not established. Host/root compromise is outside this isolation claim. No merge or epic close authorized by this decision.

## Historical contract (superseded)
status: delivered

### evidence
- Transitioned via pvg story deliver on 2026-10-20.

### proof
- [ ] Developer evidence block must remain authoritative above this contract.


## Implementation Evidence

Commit: 83bab97b3f5edea53005f4cb18374a24faaa12b6
Integration commit: dee02e80f6a99c3c8a21f79bd0e15390ff85a4b9
Branch: story/GRRR-0g4n. No push, acceptance or close performed.

### CI/Test Results

Commands run:
- Parent root: ./scripts/identity-integration /Users/speed/Documents/Codex/2026-10-19/3e4m-b-4/outputs/governed-recursive-research-ratchet/.tmp-sr_pm/vm — exit 0; launches restricted services and ./scripts/test-story bounded-challenge synchronously.
- ./scripts/test-story bounded-challenge — exit 0; 12 required, 12 executed, 0 skipped, 0 failures, 0 errors; 17.875 seconds.
- python3 tests/unit_contracts.py — exit 0; 9/9 passed.
- ./scripts/verify-evidence docs/evidence/bounded-challenge/attempt-20261020T153803Z-4d13bc7b — exit 0; 20 artifact hashes plus chains/anchors/raw objects and all four safety controls verified.
- pvg verify research/common.py research/policy.py research/ledger.py research/execution.py research/evaluator.py research/runner.py bin/grrr scripts/test-story scripts/identity-integration scripts/inspect-attempt scripts/verify-evidence tests/integration/bounded_challenge.py tests/integration/permission_probe.py tests/integration/absent_vm_probe.py tests/unit_contracts.py --format=text — exit 0; 10 recognized files scanned, 0 issues.
- git diff --check — exit 0.

Summary: 12/12 real integration tests and 9/9 supplementary unit tests pass; no skipped tests. Missing policy, absent QEMU, output cap and command deadline were actively tested. Clean execution passes its assertion; forged-PASS execution fails. Both remain blocked for Verified/admission. No hosted CI execution is claimed.

### PROOF

- [x] AC 1: Approved grammar, identity setup and numeric limits recorded; help exposes inspection and stop; pvg core unchanged.
- [x] AC 2: Real CLI/evaluator/QEMU/ledger/report path produced exact CLEAN versus PASS results and durable receipts.
- [x] AC 3: Typed validation/authentication/metadata/budget/rate/audit/error mechanisms wired; mandatory real integration entrypoint fails closed.
- [x] AC 4: Five denied capabilities tested against real evaluator transport, each GateBlocked.
- [x] AC 5: All 11 gates visible; replay/spec/review/approval remain not-run; verified/admitted states blocked.
- [x] AC 6: VM reset/network/sharing/identity/output/deadline/reservation/stop and malformed/unauthorized/stale/duplicate/absent-policy/absent-VM/forged-PASS negative controls passed.
- [x] AC 7: Independent chain/object/anchor verifier and CLI text/Markdown/JSON parity; preserved faulty evidence and unchanged assets.

Evidence: docs/evidence/bounded-challenge/DELIVERY-GRRR-0g4n.md contains the detailed AC table, wiring, measurements, all residual boundaries and histories. Final audit: docs/evidence/bounded-challenge/final-audit-12-tests.json. Final manifest SHA256: 5758264cf727dd9abd1c84e9b3b3c0d7b28575f2919271c5a105ebc26e9def54. Test log SHA256: 3a4fa144133976f27014091dfd3dec95e72dca767df28b2907a7eb36ae396bfe.

### LEARNINGS

- Preserve failed attempts: Documents-path EACCES required narrowly deployed temporary runtimes, not broad permission grants.
- Interactive ls colors caused a legitimate isolation assertion failure; exact shell inventory and observed readiness repaired it without loosening gates.
- Avoid TestCase.run attribute collision; bind idempotency keys even for denied requests.
- Absence and limit branches need real active controls; large raw output needs separate bounded content objects.
- The full 300-second outer watchdog was not allowed to expire; five-second command deadline was actively proven. Recovery/replay/admission, vlt validation and hosted CI execution remain outside these claims. PM must review evidence-driven file/line budget overrun.

# Implementation Evidence — GRRR-0g4n

## PROOF

Integration source commit: `dee02e80f6a99c3c8a21f79bd0e15390ff85a4b9`.
Final attempt: `attempt-20261020T153803Z-4d13bc7b` in this directory.
Parent-mediated root launcher exit **0**; same mandatory entrypoint
`./scripts/test-story bounded-challenge` executed **12/12**, skipped **0**,
failures **0**, errors **0**, wall time **17.875 seconds**.

Final independent checks (ordinary operator identity, no VM restart):

- `./scripts/verify-evidence docs/evidence/bounded-challenge/attempt-20261020T153803Z-4d13bc7b`: exit 0; verified 20 manifest artifacts, event chains, separately retained anchors, raw objects, clean/faulty assertions, probe ordering and four real negative controls. Results: `final-audit-12-tests.json`.
- `python3 tests/unit_contracts.py`: exit 0, 9/9 passed; `final-unit-tests.txt`.
- `pvg verify` with every explicit research module, executable script and test path: exit 0, 10 recognized files scanned, 0 findings; `final-pvg-verify.txt`. The scanner does not recognize extensionless scripts; Python syntax checks and actual launcher/CLI execution cover those paths.
- `git diff --check`: exit 0.

The root launcher copies only approved code/assets into fresh restricted temporary
runtimes; no sudo/password collection occurs in worker code. Prior failed and
successful attempts are preserved. The installed QEMU was never renamed or changed
by the negative controls.

### AC table

| AC | Implementation and measured proof |
|---|---|
| 1 | Approved grammar/limits/identities in `docs/IMPLEMENTATION-APPROVAL-2026-10-20.md`; `pvg help/version` discovered without core changes. `bin/grrr --help` exposes inspection/stop and unavailable recovery. |
| 2 | `bin/grrr` → `research/runner.py` → kernel-authenticated evaluator → isolated `research/execution.py` → assertions → `research/ledger.py` → reports. Real `CLEAN\n` passes; frozen `PASS\n` fails. Both are execution-completed, neither verified/admitted. |
| 3 | Typed public functions, registered policy/config, strict field allowlists, kernel peer identities, one-active-guest rate bound, conservative finite reservations, deny audit events and structured errors are on the actual path. 12 mandatory integration tests and 9 supplementary unit tests passed. Missing setup fails the same documented CI entrypoint rather than skipping; no hosted CI execution is claimed. |
| 4 | All five denied actions exercised through real evaluator transport in `test_03_all_denied_capabilities`; each returns GateBlocked. There is no merge, production, patch-generation, harness-adaptation or paid-dispatch implementation. |
| 5 | All 11 gates visible. Independent replay, specification traceability, reviewer outcome and action-specific approval remain not-run. Review/decide/recover return blocked; reports explicitly keep Verified/admission blocked. |
| 6 | Separate UID320/321 read/write and impersonation denial; real fresh-VM reset/network/mount checks; direct authenticated stop before candidates; exact output cap and five-second command deadline actively triggered; 300-second outer watchdog remains configured. Missing policy and absent QEMU really fail in separate restricted runtimes. Malformed metadata, wrong/missing policy binding, mismatched duplicate key, stale epoch, concurrency and forged PASS all exercised. |
| 7 | Independent verifier checks receipts/anchors and retained objects outside candidates. Text/Markdown/JSON snapshot parity is tested through the actual CLI. Faulty report remains inspectable; asset hashes unchanged; no Verified defect, approval or admission effect. |

### Measured results

| Item | Result |
|---|---|
| Clean run | `2c91e5b6d3844deab31d7f7c7c36ad24`; 1.292396s; 24,691 captured bytes; assertion pass |
| Faulty run | `824221898a5b4ccf960a462624105562`; 1.294578s; 24,690 captured bytes; assertion fail |
| Output safety probe | GateBlocked; 1,048,576 captured bytes; 4.467509s; cessation/unchanged assets verified |
| Deadline safety probe | GateBlocked; 6.300878s including boot; 24,603 bytes; cessation/unchanged assets verified |
| Missing policy | Same evaluator source; actual absent protected policy; exit 3, Unavailable; no service socket |
| Absent QEMU | Same executor source; root-owned read-only absent path; authenticated dispatch returns Unavailable; installed executable untouched |
| Reservations | 300s each, retained conservatively; 1,500s cumulative reserved by faulty snapshot (later concurrency test also reserves separately) |
| Review/cost | Review time unknown/not-run, not zero; no paid services invoked; no complete preparation-time accounting claimed |

### Durable identities and hashes

- Final manifest SHA-256: `5758264cf727dd9abd1c84e9b3b3c0d7b28575f2919271c5a105ebc26e9def54`.
- Test transcript SHA-256: `3a4fa144133976f27014091dfd3dec95e72dca767df28b2907a7eb36ae396bfe`.
- Negative-control receipt SHA-256: `7b6ad2252dd79ac23c68feea7dff93704e525c4d1e23c1bfd3764c89a0271442`.
- Clean snapshot file SHA-256: `762913430f973eb6b1c158d69fea4a3206c8fa91e4aa7b6e89112771d7a5f92c`.
- Faulty snapshot file SHA-256: `2b21d7e5b4b20d9e50e23df7b7e1c20af69a79b10974bc4d9f00a6473e9893bd`.
- Clean snapshot ID: `82926d2902291ceb8d934fcf3141629a67f32118f484e25dfd693b80bfaa7753`.
- Faulty snapshot ID: `f8f8c723d20288919cfc1e5191ebcc20daf1f8c2d58f635ef834c8b80390cb3e`.
- Clean event anchor: `77df06051ed13bce52777165f7ac3cc8fed88dd2e88c55ee1e8f95887cc8d273`.
- Faulty event anchor: `bdae7dbe080a3492525fa68b7fec5e07c8620368471f947680f0b7cddbdc5470`.
- Every other artifact hash is in the verified manifest; anchor-file hashes are distinct from event anchor values above.

## LEARNINGS

1. The first service launch from Documents returned EACCES. TCC was suspected,
   not proven. Moving narrowly copied code/assets to fresh restricted temp
   runtimes fixed execution without broadening service access to Documents.
2. Alpine's interactive `ls` emitted ANSI colors. The original strict isolation
   check correctly rejected them before the later stop request. Emit exact
   interface names without aliases; preserve original failed evidence.
3. Wait for observed bootstrap readiness before exercising direct stop, and
   recheck the fence when EOF races cancellation. Stopping an already failed
   run must never authorize execution.
4. Never use `run` as a saved unittest attribute; it collides with TestCase.run.
5. A passing happy path is not proof of absence/overflow/deadline branches. The
   final attempt actively exercises all four missing controls, without deleting
   successful policy or mutating the installed VM tool.
6. Keep large raw bytes as separate content objects; nested hex doubles twice
   and can exceed bounded transport even when guest capture itself is bounded.

## Residual boundaries for PM review

- Synthetic walkthrough only, not a vlt defect or validated vlt baseline. Full
  dependency/license preflight, replay, corpus, comparison, recovery, reviewed
  contracts and admission remain downstream. No automatic promotion exists.
- The five-second command safety deadline is actively tested; the full
  300-second outer watchdog is configured but not allowed to expire in this run.
- Services are stopped after the synchronous launcher. Temporary journals are
  retained but not a persistent deployment or disaster-recovery guarantee;
  exported snapshots survive temp-runtime cleanup.
- No hosted CI infrastructure was supplied; the same mandatory entrypoint fails
  closed without its real identity/runtime prerequisites.
- Root/host compromise is outside this boundary; hashes provide integrity
  relative to retained anchors, not administrator-resistant signing.
- Source/test/launcher code is approximately 1,500 lines. File/total-diff budget
  overrun is dominated by preserved evidence and requires PM review, not omission.
- Local `pvg notes search` discovery failed because worktree `.vault` is absent;
  live story operations used shared `pvg nd`. No global notes were consulted.

## Historical contract (superseded)
status: in_progress

### evidence
- Integration commit dee02e80f6a99c3c8a21f79bd0e15390ff85a4b9; 12/12 mandatory tests passed, zero skipped/failures/errors.
- 9/9 unit tests passed; pvg verify 10 recognized files, zero findings; independent manifest/chain/object audit exit 0.

### proof
- [x] AC #1: Approved grammar, identities and numeric execution policy discovered and implemented without modifying pvg core.
- [x] AC #2: Real clean/faulty VM path, trusted assertions, durable receipts and distinct readable outcomes.
- [x] AC #3: Typed/validated/authenticated/bounded/audited path; mandatory integration entrypoint fails closed.
- [x] AC #4: Five denied capabilities produce tested blocked outcomes.
- [x] AC #5: Full gate inventory with downstream not-run and no verified/admitted result.
- [x] AC #6: Real isolation/reset/permissions/stop and mandatory negative controls, including active cap/deadline probes.
- [x] AC #7: Independently checked receipts and preserved reports with shared snapshot identity and unchanged assets.

## nd_contract
status: delivered

### evidence
- Story branch: story/GRRR-0g4n
- Commit SHA: 10c0862f3e1c82b449d76f9342f2f89703e3dbaa
- Integration source commit: dee02e80f6a99c3c8a21f79bd0e15390ff85a4b9
- Required integration: 12 executed, 0 skipped, 0 failures, 0 errors
- Unit tests: 9 executed, 0 failures
- pvg verify: 0 findings
- Evidence: docs/evidence/bounded-challenge/attempt-20261020T153803Z-4d13bc7b
- Manifest SHA256: 5758264cf727dd9abd1c84e9b3b3c0d7b28575f2919271c5a105ebc26e9def54
- Test output SHA256: 3a4fa144133976f27014091dfd3dec95e72dca767df28b2907a7eb36ae396bfe
- Independent audit: docs/evidence/bounded-challenge/final-audit-12-tests.json; 20 artifact hashes plus chains, anchors and objects checked.
- Full PROOF/LEARNINGS and limitations: docs/evidence/bounded-challenge/DELIVERY-GRRR-0g4n.md

- UNIT-ONLY research/ line coverage: 19.75% (112/567 statements); 9 unit tests; Python 3.10.14, Coverage.py 7.9.1.
- Module line coverage: common 46.36%; evaluator 0.00%; execution 14.37%; ledger 0.00%; policy 47.06%; runner 55.77%.
- No parent-run identity/VM integration coverage is measured or inferred; no privileged integration rerun occurred.
- Coverage transcript: docs/evidence/bounded-challenge/unit-coverage.txt; SHA256 7ef31a3871d35dec5683a46ca409a25b4cf070d7dc8ceb0fda2c91b397ffa25c.
- Coverage JSON: docs/evidence/bounded-challenge/unit-coverage.json; SHA256 4560925e18f0ec1213efd44b15c32b5ec5104990626f595b81bf0fc8a47ba3d7.

### proof
### AC Verification
- [x] AC #1: Approved CLI/identities/numeric policy; docs/IMPLEMENTATION-APPROVAL-2026-10-20.md and CLI help.
- [x] AC #2: Real clean/faulty VM assertions and receipts; final attempt clean.json and faulty.json.
- [x] AC #3: Typed validated authenticated bounded audited path; 12 integration tests and 9 unit tests.
- [x] AC #4: Five denied capabilities; test_03_all_denied_capabilities passed.
- [x] AC #5: Full 11-gate inventory; downstream not-run and Verified/admission blocked in both reports.
- [x] AC #6: Real identity/isolation/reset/stop and active missing-policy/absent-VM/output/deadline controls; final attempt negative-controls.json and probe snapshots.
- [x] AC #7: Independent manifest/chain/object/anchor audit and CLI projection parity; final-audit-12-tests.json.


## History
- 2026-10-20T03:19:02Z dep_added: blocks GRRR-90te
- 2026-10-20T03:19:04Z dep_added: blocks GRRR-6sso
- 2026-10-20T03:34:35Z status: open -> in_progress
- 2026-10-20T03:34:35Z claimed by dev-GRRR-0g4n
- 2026-10-20T03:37:21Z status: in_progress -> open
- 2026-10-20T03:37:21Z released by speed
- 2026-10-20T14:48:29Z status: open -> in_progress
- 2026-10-20T14:48:29Z claimed by dev-GRRR-0g4n
- 2026-10-20T14:55:55Z status: in_progress -> open
- 2026-10-20T14:55:55Z released by speed
- 2026-10-20T14:58:36Z status: open -> in_progress
- 2026-10-20T14:58:36Z claimed by dev-GRRR-0g4n
- 2026-10-20T15:43:06Z status: in_progress -> in_progress
- 2026-10-20T15:56:23Z status: in_progress -> closed
- 2026-10-20T15:56:23Z dep_removed: no_longer_blocks GRRR-90te
- 2026-10-20T15:56:23Z dep_removed: no_longer_blocks GRRR-6sso

## Links
- Parent: [[GRRR-2t3h]]
- Led to: [[GRRR-90te]], [[GRRR-gu87]]

## Comments
