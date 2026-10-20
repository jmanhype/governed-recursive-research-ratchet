---
id: GRRR-0g4n
title: "Observe one bounded challenge through the trusted research path"
status: in_progress
priority: 1
type: task
labels: [milestone-1, integration, walking-skeleton]
parent: GRRR-2t3h
created_at: 2026-10-20T03:19:01Z
created_by: speed
updated_at: 2026-10-20T15:36:54Z
content_hash: "sha256:b40f0347a3ac5f42502822f82b35ed3bc03f0d894f690f72cca538a29e1388ca"
blocks: [GRRR-90te, GRRR-6sso]
assignee: dev-GRRR-0g4n
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

## Links
- Parent: [[GRRR-2t3h]]
- Blocks: [[GRRR-90te]], [[GRRR-6sso]]

## Comments
