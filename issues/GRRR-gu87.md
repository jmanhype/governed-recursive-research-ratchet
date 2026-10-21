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
updated_at: 2026-10-21T04:58:42Z
content_hash: "sha256:b2e655b7a7db67cca3dc84a356247d99ecc711fb24550a9b7cc1a966dfbb5c0b"
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
OPERATOR TRUSTED-OBSERVATION PROFILE DEVELOPMENT/REVIEW APPROVAL (2026-10-20):
- Approved development and review—but not execution—of the distinct trusted-observation supervisor profile bound to proposal SHA-256 1830a92ad2cbd91788051304ec8f6acaebf256b85065b2db2c07271b6906e3f6.
- Approved exact proposal limits: 1024 MiB RAM; 1 vCPU; 512 MiB guest /work; 30s boot; 240s command timeout; 300s total invocation; 2s stop acknowledgement target; 5s TERM grace; 2s force-kill wait; 1 MiB guest output cap; 3 MiB IPC wire cap; 15 GB minimum host free space; host evaluator UID 320; host executor UID 321; guest supervisor UID 0; candidate UID/GID 1000/1000; networking, host shares, and paid dispatch disabled.
- Existing synthetic and offline profiles remain unchanged.
- Authorized work: implement and pin the guest supervisor and detached input image, perform static/unit review, and present completed supervisor/image hashes for separate execution approval.
- Not authorized: guest execution of this new profile, resource expansion, paid calls, host fallback, production mutation, automatic admission, or treating proposal isolation properties as demonstrated.
- Before execution, operator must separately approve parent-mediated identity execution and guest negative controls after reviewing completed supervisor and detached input-image hashes.
DISPOSABLE OFFLINE RUNTIME CLEANUP (2026-10-21): removed only old root-owned /private/tmp/grrr-offline-jwxgpr6a (175M/121 files) and /private/tmp/grrr-offline-m5qlaapy (200M/127 files); durable evidence was already committed. Free space now 15,481,393,152 bytes. No project/model/output data touched.
REGENERABLE DEVELOPMENT CACHE CLEANUP (2026-10-21): removed only /Users/speed/.cache/opencode (190M, 11,996 files) and /Users/speed/.cache/codebase-memory-mcp (143M, 24 files); free space now 15,461,191,680 bytes. Manifest main checkout .tmp-sr_pm/development-cache-cleanup-manifest.txt. No model/project/output data touched.
REGENERABLE UPDATER CACHE CLEANUP (2026-10-21): removed only /Users/speed/Library/Caches/autoclaw-updater (1.2G, 3 files) and /Users/speed/Library/Caches/voyager-updater (1.0G, 5 files); free space now 16,972,693,504 bytes. Manifest main checkout .tmp-sr_pm/updater-cache-cleanup-manifest.txt. No application data, models, projects, credentials, or outputs touched.
INDEPENDENT SECURITY REVIEW (2026-10-21, commit d53deaf60290c5795a29ca279ec6919a15b44fb3): SECURITY_REVIEW: CHANGES_REQUIRED. Blocking findings: (1) fresh per-launch budget DB resets cross-run/profile ceilings; use one protected persistent accounting store and test restart/concurrency/cross-profile exhaustion; (2) mode-0666 service allows eight pre-auth slow readers for 310s and can starve stop/status; authenticate before payload reads, reserve control capacity, and add saturation tests; (3) mutable operator-owned Homebrew QEMU path is hashed then executed; use immutable root-controlled reviewed executable/deps or equivalent race-resistant binding and test replacement; (4) root imports/executes checkout code before validating approval inventory; use independently verified root-controlled bootstrap/source snapshot before privileged execution. Preparation pins/hashes matched and ten-scenario harness exists, but no execution approval should be requested until blockers are fixed and re-reviewed.
INDEPENDENT SECURITY RE-REVIEW (2026-10-21, commit 7fee2ba0fa456fc9edd1b9ce1bfdbc284cd338a1): SECURITY_REVIEW: CHANGES_REQUIRED. Original persistent accounting/control-availability designs substantially addressed, but two new high blockers remain: (1) staged trusted_observation.py derives /private/tmp/research and /private/tmp/tests paths ahead of isolated verified code, allowing host-writable modules to load as UID 320; preserve verified directory structure or remove unsafe path manipulation and add poisoned-path regression; (2) QEMU @rpath validation checks manifest membership but not actual loader selection/order, allowing unlisted earlier shadow libraries; validate all search directories/candidates and mutable ancestors or forbid @rpath, with shadow/symlink/ambiguity negatives. Immutable installation/accounting migration/bootstrap provisioning and composed execution digest remain pending; no execution approval.
INDEPENDENT SECURITY RE-REVIEW 2 (2026-10-21, current clean HEAD 8be2a19/source db53a47): SECURITY_REVIEW: READY_FOR_PROVISIONING. Staged import escape and @rpath shadowing blockers are closed. Host inventory 742625e1254dc50a41642508e3df1db6d7f1bf019079861bfbc77003dc50255a; bootstrap 615cbfab84ddce1d84b397da9b4e99d2a51c1404bfd637defcc313238512ed9f; evidence manifest 93d2c52eaccd267dc98eb56a6602df03f5b5118e0a006d5f8cb349bd81816f33. Required provisioning-only authorization before execution: independently install bootstrap/interpreter under /Library/GRRR/bootstrap; install immutable QEMU 11.1.2 closure with absolute deps/no LC_RPATH and provenance; reconcile persistent synthetic/offline/trusted accounting into one protected campaign DB with receipt/identity/inode binding/lock; independently review installed state and permission/import/accounting/replacement controls; compose final bindings/digest; then separately request exact local-use execution approval. All ten guest scenarios remain not-run.
OPERATOR TRUSTED-OBSERVATION PROVISIONING-ONLY APPROVAL (2026-10-21):
- Approved provisioning—not guest execution—of the reviewed trusted-observation host boundary.
- Approved installing the reviewed bootstrap/canonical interpreter under a root-controlled /Library/GRRR/bootstrap path and verifying installed hashes, ownership, modes, ACLs, ancestors, and isolated invocation.
- Approved installing an immutable root-controlled QEMU 11.1.2 closure with executable/library/data/firmware provenance, absolute dependencies, no LC_RPATH, disabled modules/plugins, and runtime-loading review. Mutable Homebrew QEMU must remain rejected for privileged execution.
- Approved creating/reconciling one protected persistent campaign accounting store across synthetic/offline/trusted profiles, including prior charges, unresolved holds, stops, migration receipt, store identity, inode/device binding, active state, and campaign lock. No fresh allowance or silent reset.
- Approved installed-state review and non-guest permission/import-origin/accounting restart/concurrency/replacement-denial checks, followed by composition of final installation/accounting/bootstrap/interpreter bindings and exact composed execution-profile digest.
- Not authorized: QEMU guest execution, ten trusted-observation controls, paid calls, resource expansion, host fallback, production mutation, automatic admission, or candidate-correctness certification. Separate execution approval remains mandatory.
REGENERABLE PROVISIONING CACHE CLEANUP (2026-10-21): removed Citro Labs cache 948M/11,155 files; Google cache 929M/12,978 files; partially regenerated Codex cache reduced to ~20K; com.spacefs.launcher 751M/487 files; dev.zcode.app.ShipIt 772M/779 files; @zcodedesktop-updater 476M/3 files. Current free space 18,042,109,952 bytes. Manifests: .tmp-sr_pm/provisioning-cache-cleanup-manifest.txt and .tmp-sr_pm/provisioning-cache-cleanup-round2-manifest.txt. No model/project/output/credential data touched.
REGENERABLE QEMU BUILD CACHE CLEANUP (2026-10-21): removed only now.typeless.desktop.ShipIt 529M/227 files; com.meta.endo 544M/748 files; antigravity-updater 349M/3 files; typeless-updater 349M/3 files. Current free space 18,674,339,840 bytes. Manifest .tmp-sr_pm/qemu-build-cache-cleanup-manifest.txt. No model/project/output/credential data touched.
REGENERABLE QEMU PACKAGING CACHE CLEANUP (2026-10-21): removed only /Users/speed/Library/Caches/ms-playwright (554M, 359 files). Current free space 17,356,939,264 bytes. Manifest .tmp-sr_pm/qemu-packaging-cache-cleanup-manifest.txt. No model/project/output data touched.
REGENERABLE QEMU PACKAGE ROUND 2 CACHE CLEANUP (2026-10-21): removed only /Users/speed/Library/Caches/loom-updater (209M, 2 files). Current free space after cleanup measured 17,199,886,336 bytes, about 199.9 MB above the 17 GB packaging gate. Manifest .tmp-sr_pm/qemu-package-round2-cache-cleanup-manifest.txt. No application data/models/projects/outputs touched.
INDEPENDENT QEMU INSTALLER/PACKAGE REVIEW (2026-10-21, HEAD dd4f6d3): SECURITY_REVIEW: READY_FOR_QEMU_INSTALL. Verified provisioner f6190845f01c4935759e03dcc1df0a04bb2ce56986ecf439c972fefd1dbbe1df; plan d1bf4b297c3d31f48e494abfb3c1bd9456d438b8f4e328d62787841e0aaf0fcd; installation manifest e40888d8d14bc9c2b8db38d8468bc53fdbf77421b284d9eacbbce1d37818b625; evidence manifest 5f87b465bea46d326d46076a2523d4e48484d95d0d7d372d66db565e050177fa; 191-file package readback; absolute dependencies/no LC_RPATH; four signatures; signed QEMU 352108bbc46171ed74ee3ef0b74ac1f32403c7e076ebac623ce2c265724699da. Parent must install exact root-owned bootstrap/plan, umask 022, verify hashes/ancestors/interpreter, enforce 15GB floor, retain failure state, and perform mandatory no-QEMU post-install checks. Accounting and guest execution remain blocked.
REGENERABLE INSTALL CACHE CLEANUP (2026-10-21): removed generated QEMU build/source trees and safe caches, preserving staged QEMU package; then removed .cache/codex-runtimes 3.2G/54,169 files plus GeminiMacOS 257M, deno 165M, ollama cache 190M, node-gyp 125M, electron 109M, Comet 103M, GeoServices 100M, go-build 97M. Current free space 16,862,380,032 bytes. Manifests .tmp-sr_pm/before-qemu-install-cleanup-manifest.txt and .tmp-sr_pm/install-cache-final-cleanup-manifest.txt. Hugging Face model cache, Ollama models, whisper cache, projects, outputs, downloads, credentials, and application data were not touched.
EXACT QEMU PROVISIONING PLAN d1bf4b29 INSTALLED AND INDEPENDENTLY CHECKED (2026-10-21): root-owned /Library/GRRR/bootstrap and /Library/GRRR/qemu installed without launching QEMU. Bootstrap provisioner f6190845f01c4935759e03dcc1df0a04bb2ce56986ecf439c972fefd1dbbe1df, trusted-root-bootstrap 615cbfab84ddce1d84b397da9b4e99d2a51c1404bfd637defcc313238512ed9f, plan d1bf4b297c3d31f48e494abfb3c1bd9456d438b8f4e328d62787841e0aaf0fcd. Readback SHA e434e72e02d4b0ac71b76d948a632cec53f3514e9f7599265ee12c0d0a13048b; fields accounting_touched=false, execution_authorized=false, guest_executed=false, runtime_loading_tested=false; host inventory 7e887f77bfc1a57f1a4fa26cb95c72e5567836ce98fb08553ae02e6a19744a97 and QEMU installation manifest e40888d8d14bc9c2b8db38d8468bc53fdbf77421b284d9eacbbce1d37818b625. Independent plan check verified 218 entries; installed tree exactly 221 files/19 directories, no symlinks, root:wheel, dirs 0755, QEMU executable 0555, other files 0444. QEMU SHA 352108bbc46171ed74ee3ef0b74ac1f32403c7e076ebac623ce2c265724699da. Four Mach-O images verify strict codesign and contain no LC_RPATH; non-system deps absolute /Library/GRRR/qemu paths; QEMU entitlement is Hypervisor-only. OS build 27.0/26A428. UID 320 and 321 can read/execute installed QEMU/snapshot but writes/links denied. /Library/GRRR/accounting absent and no unauthorized artifacts created. Free space after install 16,730,546,176 bytes.
## nd_contract
status: in_progress

### evidence
- WIP commit 0b538c5: independent non-root installed QEMU audit, 221 files / 20 directories including root / no symlinks; no QEMU execution. Parent identity-denial checks recorded distinctly from worker read-back.
- Installed read-back audit SHA256 39163533253709e3a255704f62f439d474f028bed87fd79b5f7e2b84ddb8f784. Installed host inventory remains 7e887f77bfc1a57f1a4fa26cb95c72e5567836ce98fb08553ae02e6a19744a97.
- Accepted synthetic 12/12 and offline 6/6 evidence independently verified; reconciliation report SHA256 f7b38efb3d096f7803555f648475390d3ea8661f423aefcf98a03b6c1306921c. Five identified reservations, five observations, four stop events, six unmapped legacy reservations, ten earlier attempt manifests. Not complete campaign totals.
- System and Homebrew Python: 93/93 unit tests each. pvg verify explicit paths: passed, two Python files scanned; extensionless audit scripts separately executed. Evidence SHA256SUMS a5c018e1706361b349d341ea3206cdf8bba1e31ce5bf1e0cf3c506300f57a58b verified 14/14.
- Accounting remains absent. Reconciliation always blocked: unknown cumulative review/replay, earlier failures, selector/preparation separation, holds/receipts, stop scope and cross-profile POC carry-forward. No fresh allowance, inferred zero, database creation, root run, or guest execution.

### proof
- [ ] AC #1-#6: mandatory trusted-observation guest controls remain not-run; provisioning and static evidence do not demonstrate candidate isolation/correctness.
- Claim retained; no delivery or execution approval requested.

## nd_contract
status: in_progress

### evidence
- Non-root package completed, QEMU never executed. Independent staged readback both Pythons: 191 files, 185 data; all non-system dependencies absolute under /Library/GRRR/qemu, LC_RPATH removed, signatures verified. Installation manifest e40888d8d14bc9c2b8db38d8468bc53fdbf77421b284d9eacbbce1d37818b625; signed QEMU 352108bbc46171ed74ee3ef0b74ac1f32403c7e076ebac623ce2c265724699da.
- Exact QEMU-only parent provisioning plan d1bf4b297c3d31f48e494abfb3c1bd9456d438b8f4e328d62787841e0aaf0fcd; installer f6190845f01c4935759e03dcc1df0a04bb2ce56986ecf439c972fefd1dbbe1df. Plan excludes accounting fields and installer returns before accounting. All current plan inputs read back.
- Both unit suites 85/85; both Python syntax checks and pvg pass. docs/TRUSTED-OBSERVATION-QEMU-PACKAGED.md records exact AWAITING_PARENT_IDENTITY_RUN command, independent bootstrap setup, data/config boundary and remaining gates. Host inventory 7e887f77bfc1a57f1a4fa26cb95c72e5567836ce98fb08553ae02e6a19744a97; v3 guest/bootstrap unchanged.
- No root/install/QEMU/guest execution performed. Independent security review and parent provisioning pending. Accounting unreconciled; composed execution binding absent. Claim retained, no execution approval request.

### proof
- [ ] AC #1-#6: Mandatory guest controls remain unauthorized/not-run; packaged closure is not candidate correctness or admission proof.

## nd_contract
status: in_progress

### evidence
- Prefix-only fresh dynamic build completed and signed; binary 616b0284fbaba079be4e2701061741eb9e9bae44e55af3980730f89497bd14f2. Compiled fallbacks now /Library/GRRR/qemu. No QEMU executed.
- Packaging script independently refused before staging because free space fell below 17 GB after brief near-threshold pass. No dependency rewrite/copy/signing yet. Exact logs in qemu-source-build/retry-8; stable packaging margin required.
- Staged package/readback tools; exact-prefix/full-tree validator; no-user-config and C locale host hardening. New host inventory 7e887f77bfc1a57f1a4fa26cb95c72e5567836ce98fb08553ae02e6a19744a97; provisioner 206df1f4aead529be79dc2f89fd3089f0f0b616422797a7f3e8e4054ec913c49. Independent review required. v3/bootstrap unchanged.
- Both Python suites 84/84; py_compile both pass; explicit pvg 3 files zero issues. Claim retained; no root/install/guest execution or execution approval request.

### proof
- [ ] AC #1-#6: Mandatory suite unauthorized/not-run; package incomplete and accounting unreconciled.

## nd_contract
status: in_progress

### evidence
- Authorized FDT-only unified diff applied: meson.build before 7d45b715ca8e740d787eee6d4a1e8ae4a7456aecfe16dda2a7d32a0f2cc10591 after 7222d581694f1022ba6ab661907af6abf552243e80c9725cc4a7a064d70df4e0. dtc hashes reverified.
- Fresh configure succeeded; exact static libfdt.a selected, no FDT subproject/download. Static/minimal/no-modules/no-plugins retained. Compilation reached final link 2022/2023, failed ld library crt0.o not found with -static. Exit 2; stopped with no fallback.
- Complete logs, build configuration, static dependency formula/archive/license provenance retained in qemu-source-build/retry-6. No binary/closure/QEMU execution/root install. Host/v3 pins unchanged; claim retained.

### proof
- [ ] AC #1-#6: Mandatory guest suite unauthorized/not-run; build blocked at macOS fully-static link.

## nd_contract
status: in_progress

### evidence
- Authorized minimal Meson static FDT environment probe exited 1: C static library fdt not found. Exact LIBRARY_PATH/CPATH supplied. No QEMU configure retry followed because prerequisite failed.
- Pinned Meson source shows static lookup enumerates explicit dirs plus compiler --print-search-dirs; Apple clang output ignores LIBRARY_PATH there. Full real probe logs/source hashes retained in qemu-source-build/retry-5. Proposed explicit dirs/static source patch requires separate review; none applied.
- No QEMU/root/install/guest execution or execution request. Claim retained; v3 and host pins unchanged.

### proof
- [ ] AC #1-#6: Mandatory trusted guest suite unauthorized/not-run; build blocked at isolated FDT search probe.

## nd_contract
status: in_progress

### evidence
- Ninja 1.13.2 executable/formula/receipt/SBOM/license provenance recorded. Genuine configure first failed because required FDT disabled. Parent-authorized fresh system-FDT retry failed at Meson 2048 prefer_static fdt not found. Further parent-authorized fresh retry with exact dtc 1.8.1 include/link paths also failed at same library-search gate.
- Exact libfdt.a/header/formula/receipt/SBOM hashes retained; no successful static archive selection claimed. Full configure/Meson logs and status docs preserved in qemu-source-build/retry-2, retry-3, retry-4. No prior directory overwritten.
- Static/minimal/no-module/no-plugin flags unchanged; no target build, QEMU execution, root installation or execution request. Claim retained. Next work is library-search diagnosis, not repeated linker-flag retries.

### proof
- [ ] AC #1-#6: Mandatory trusted guest suite remains unauthorized/not-run; source build blocked at FDT selection.

## nd_contract
status: in_progress

### evidence
- Genuine QEMU 11.1.2 release archive fetched/extracted, SHA256 731b5681e4bb18be313231579b8efd0296c5b015fa36dc533874b639ba838016. Upstream tag peeled commit 4fc49f46dc95d4a27de2509e7fceb2931e91faeb. VERSION/license/configure hashes preserved in docs/evidence/trusted-observation/qemu-source-build/retry-1.
- Staged minimal static aarch64 build flags verified against configure help. Actual configure/build not run: preconfigure free 16987373568 bytes, above 15 GB floor but 12626432 bytes short of conservative 2 GB preparation headroom. Gate exit 1, stopped per instruction. Headroom is not a VM resource limit; no silent reduction.
- Ninja absent on PATH; bundled Meson present. No QEMU/root/install/guest execution, no paid calls, no execution request. Shell syntax passed; pvg recognized zero files, not substantive coverage. Host inventory/v3 media unchanged. Claim retained.

### proof
- [ ] AC #1-#6: Mandatory trusted guest suite remains unauthorized and not-run; build incomplete.

## nd_contract
status: in_progress

### evidence
- Upstream QEMU 11.1.2 build assignment stopped at first read-only gate: scripts/qemu-build-preflight exit 1; available 13738397696 bytes versus mandatory 15000000000 floor. Receipt docs/evidence/trusted-observation/qemu-source-build/preflight.json.
- No source fetch/configure/build/sign/package/root/QEMU execution, no cleanup. Source commit/archive/binary/closure hashes null. Both Python py_compile checks pass; pvg verify recognized 0 files (not substantive coverage). Application and pinned v3 artifacts unchanged.
- Claim retained. Await independently authorized parent space recovery; no executable provisioning command or execution request.

### proof
- [ ] AC #1-#6: Mandatory guest controls remain unauthorized and not-run; upstream build blocked before fetch.

## nd_contract
status: in_progress

### evidence
- Provisioning-only WIP staged: scripts/provision-trusted-host and scripts/review-provisioning-inputs. Independently installed root-controlled plan/hash boundary; no mutable checkout root entry; no overwrite/reset; complete source read-back before imports; exact reviewed DB migration only.
- Both Python unit suites 84/84; explicit py_compile and pvg verify pass. No root/sudo/install/QEMU/guest execution. Host inventory 742625e1254dc50a41642508e3df1db6d7f1bf019079861bfbc77003dc50255a and v3 guest artifacts unchanged. Provisioner e34bd0bc92af433bba6757f66c892ea9983c778cd9096b8da6108b6a41e32d36.
- docs/TRUSTED-OBSERVATION-PROVISIONING-WIP.md records paths and parent-only command template. Installed Homebrew bottle formula does not prove disabled/pinned module/plugin loading; immutable closure not fabricated. Accepted synthetic/offline source evidence hashed with known observations; cumulative review and earlier attempt/hold/stop reconciliation incomplete. No fresh allowance/database invented.
- AWAITING_PARENT_IDENTITY_RUN remains conditional on genuine reviewed plan, QEMU closure and reconciled prior database. Final composed execution-profile digest unavailable. No execution approval requested. Claim retained.

### proof
- [ ] AC #1: Mandatory guest suite not-run.
- [ ] AC #2: Unit negatives pass; mandatory identity suite not-run.
- [ ] AC #3: Race/locking guest proof not-run.
- [ ] AC #4: Genesis reconciliation blocked; no allowance reset.
- [ ] AC #5: Trusted guest receipt proof not-run.
- [ ] AC #6: Ten mandatory controls unauthorized and not-run.

## nd_contract
status: in_progress

### evidence
- Security re-review source db53a47: removed flattened import-path escapes; isolated subprocess poisoned-neighbor regression passes. Absolute-only Mach-O dependencies; every LC_RPATH rejected. Prior persistent accounting/control/bootstrap fixes retained.
- Both Python unit suites 81/81; pvg verify explicit paths 12 recognized files, 0 issues; both py_compile checks pass. Go protocol coverage 90.6%; Python trace installation 49%, transport 88%, persistent budget 72%.
- Host inventory 742625e1254dc50a41642508e3df1db6d7f1bf019079861bfbc77003dc50255a; bootstrap unchanged 615cbfab84ddce1d84b397da9b4e99d2a51c1404bfd637defcc313238512ed9f. Evidence docs/evidence/trusted-observation/security-rereview/SHA256SUMS and docs/TRUSTED-OBSERVATION-IMPORT-CLOSURE-WIP.md.
- v3 guest read-back unchanged. No provisioning/install/root/sudo/QEMU/guest execution. No execution authorization requested. Independent re-review pending; installation/accounting/composed execution bindings remain absent. Claim retained.

### proof
- [ ] AC #1: Mandatory isolated guest execution not-run.
- [ ] AC #2: Unit negatives pass; mandatory service/guest suite not-run.
- [ ] AC #3: Race/locking guest gate not-run.
- [ ] AC #4: Accounting unit controls pass; protected persistent store not provisioned.
- [ ] AC #5: Receipt/unit checks pass; trusted guest receipts not-run.
- [ ] AC #6: Ten mandatory scenarios remain not-run.

## nd_contract
status: in_progress

### evidence
- Parent independent review: SECURITY_REVIEW: CHANGES_REQUIRED. Four findings:
  persistent accounting lifecycle, pre-auth control availability, immutable QEMU
  execution binding, root bootstrap trust.
- Response source WIP `66f4ba1f7e7750dfe91c0eaa8b9dc10940617a7b`;
  final source/evidence WIP `7fee2ba0fa456fc9edd1b9ce1bfdbc284cd338a1`.
- Protected pre-existing campaign store now required across synthetic/offline/
  trusted-observation evaluator reservation paths. No automatic initialization
  or missing-state repair. Identity/history/inode/stop/meter integrity checks;
  missing migration binding blocks work. Profile resources unchanged.
- Dedicated pre-auth data/control sockets, bounded initial reads; actual
  socket-saturation tests and separate-process flock rejection pass.
- Trusted path rejects Homebrew execution; requires reviewed root-owned QEMU/
  dependency/data closure and disabled-module/plugin build provenance.
- Independently installed standalone bootstrap required; no checkout application
  import before approval-bound snapshot verification; isolated canonical Python.
- Host source inventory SHA-256:
  `f5170737b386d3f80039b40f70a6ec878ec0144d4db518d680479045498ff9e9`.
- Bootstrap source (not installed):
  `615cbfab84ddce1d84b397da9b4e99d2a51c1404bfd637defcc313238512ed9f`.
- System and Homebrew Python: 76/76 unit tests each. Actual UID-320/root/guest
  proof remains not-run; unit identity substitution is explicitly disclosed.
- Go protocol tests pass, 90.6% statements. pvg explicit paths: 15 recognized
  files, 0 issues. py_compile/diff checks pass.
- Python trace line coverage: transport 88%, persistent accounting 72%,
  installation validator 38%, executor 41%, evaluator 48%, bootstrap 23%.
- v3 supervisor/ISO/source unchanged; independent readback 7 ISO/52 source
  members succeeds. No guest binary rebuild or execution.
- Mandatory suite: 10 required, 0 executed, 0 skipped, 1 identity prerequisite
  error. Nonroot bootstrap rejected; dry-run blocked by absent root installation.
- Evidence manifest:
  `6116186b4cec078928b330e8037ea754fc9999bf02115f5cd9faa24de829e8a9`.
  All entries rehashed successfully. Worktree clean after commit.
- Full response, immutable-bootstrap design, profile transition, missing
  prerequisites and exact next request: docs/TRUSTED-OBSERVATION-SECURITY-WIP.md.

### proof
- [ ] AC #1: actual approved composed-profile invocation remains not-run.
- [ ] AC #2: privileged service/guest adversarial suite remains not-run.
- [ ] AC #3: actual isolation/race/locking proof remains not-run.
- [ ] AC #4: protected prior-cost migration and real cross-profile identity proof pending.
- [ ] AC #5: actual metering/lost-receipt/recovery proof pending.
- [ ] AC #6: actual root/guest watchdog/tamper/store controls pending.

### AC Verification
All six ACs remain incomplete. No security approval or delivery is claimed.
Claim retained; no root/sudo/QEMU/guest run, paid call, push, deliver or close.

The prior direct checkout root command and host pin are withdrawn. Prepared-v3
still pins historical Homebrew QEMU, so the hardened path requires a NEW composed
execution-profile digest binding the unchanged media plus immutable installation,
accounting, bootstrap/interpreter, host code and unchanged limits. That digest,
installation approval, and accounting binding are null/absent, not fabricated.

Exact next request: independently re-review these four security changes. Do not
request or authorize guest execution. If design review clears them, identify the
separate provisioning-only authorization needed for immutable QEMU/runtime closure,
independently installed bootstrap and migration of prior campaign costs/holds/stops.
Return verified hashes and composed profile for a later decision.

## nd_contract
status: in_progress

### evidence
- WIP implementation commit `87a8766`; development/review evidence commit `d53deaf`.
- Dedicated profile-specific executor, evaluator receipt adapter, root launcher,
  and ten real mandatory scenarios staged; no root/sudo/QEMU/guest execution.
- Exact host-code inventory SHA-256:
  `8f4c4aec14549d3d0f458e4cf0fc3837d19586e539ed38716d8fcdb7db423fc8`.
- Pinned v3 supervisor/image/profile unchanged. Independent preparation readback:
  7 ISO entries and 52 source entries verified; exit 0.
- Unit suite 59/59 pass. Corrected Python trace line coverage: trusted executor
  41.8%, evaluator adapter 50.0%, root launcher 18.5%; not branch/integration proof.
- pvg verify explicit paths: 5 recognized files, 0 issues. py_compile and diff check pass.
- Nonroot --run fails Unauthorized before staging. --dry-run fails BudgetExceeded
  at unchanged 15 GB floor. Latest free-space binding: 14,683,729,920 bytes.
- Mandatory suite: 10 required, 0 executed, 0 skipped, 1 actual-identity setup
  error. Mandatory guest gate not-run. No mocked service/identity used in it.
- Evidence manifest SHA-256:
  `e722138ce3ca14c6b15147d0047462f3f03249d526be2404de36ad76c3f404ce`;
  all manifest entries independently rehashed successfully.
- Exact limits, authorization request, record schemas, parent command, test
  mapping and remaining review gaps: `docs/TRUSTED-OBSERVATION-HOST-WIP.md`.
- Claim retained. No deliver/accept/close/push. Existing synthetic/offline
  profile resources and launchers unchanged by this checkpoint.

### proof
- [ ] AC #1: actual approved isolated invocation remains not-run.
- [ ] AC #2: real service/guest adversarial cases staged, unexecuted.
- [ ] AC #3: candidate-inaccessible supervisor behavior/race observation unproven.
- [ ] AC #4: actual identity and cross-profile persistent accounting review pending.
- [ ] AC #5: real metering, overlap/review, epoch and lost-receipt controls pending.
- [ ] AC #6: real watchdog/store exhaustion/no-retry controls pending.

### AC Verification
All six ACs remain incomplete; static/unit pass is not behavioral proof.
Independent security/PM review must address expanded diff, cross-profile budget
lifecycle and restart/recovery before delivery.

AWAITING_PARENT_IDENTITY_RUN

After separate operator execution/local-use approval AND restored 15 GB floor,
from the story worktree, parent authorized root identity only:
`python3 scripts/trusted-identity-integration --run ../../../.tmp-sr_pm/vm .tmp-sr_pm/trusted-observation/prepared-v3 /private/tmp/grrr-trusted-execution-approval.json /private/tmp/grrr-trusted-license-review.json`

Those two approval files do not exist from this checkpoint; the development-only
approval does not authorize this command. No credentials requested or stored.

## nd_contract
status: in_progress

### evidence
- Development implementation 98c8af1; complete evidence checkpoint 91a7ad5. Worktree clean. No guest execution, privileged launcher, paid call or push.
- 50/50 Python tests; 2/2 Go protocol tests with 90.6% parser coverage. Python research coverage 37%; Linux supervisor runtime coverage 0%. Cross-Go-vet and explicit pvg verify pass (12 files, zero issues).
- Actual nonexecuting ISO read-back verified all 7 files and all 52 archived source files. Receipt anchor 775a767ca74f9c18678fc998111b0c9870df1a68db68e453b6af0c50ae9d6c0c.
- Final supervisor a9a0fd9a8471bc1859e5ab91c3746a139942562f719784fec51b8254eb8307d6; ISO 799ec744f27e7329686e5acb8a3e1f663c82a321f7bc1d4bc940ea5c97068233; prepared profile 3edebcd4b85ae7ce666d953bd3c5527606a7043c42294a0f60000875f8d2eec0. Dispatch remains disabled.
- docs/TRUSTED-OBSERVATION-PREPARED.md SHA256 fcd27424ad8f50c15d13cb01f07673be558c709fad4d5957e88925f97acfba04.
- Story diff guideline overrun explicitly referred to PM investigation. Claim retained. Not delivered or accepted.

### proof
- [ ] AC #1: guest adapter and execution proof pending separate approval.
- [ ] AC #2: full real adversarial guest/service observations pending.
- [ ] AC #3: supervisor and image pinned but actual separation/race proof not-run.
- [ ] AC #4: real evaluator identity and offline accounting integration pending.
- [ ] AC #5: real cross-service metering/review/overlap proof pending.
- [ ] AC #6: real watchdog/store/lost-response integration pending.

# Trusted-observation development checkpoint — execution not authorized

Implementation basis: `98c8af1` on `story/GRRR-gu87`. This supersedes the
preliminary v2 binary/image pins, **not** the original approved development
proposal. The v2 evidence and assets remain preserved.

## Prepared pins

| Artifact | SHA-256 |
|---|---|
| Original development proposal | `1830a92ad2cbd91788051304ec8f6acaebf256b85065b2db2c07271b6906e3f6` |
| Supervisor executable, static Linux/arm64 ELF, 3,991,473 bytes | `a9a0fd9a8471bc1859e5ab91c3746a139942562f719784fec51b8254eb8307d6` |
| Supervisor Linux source | `b5382ea1a87a76401b7ec68961991405578603e68dcd204f8ad1930ee17ed259` |
| Separate candidate helper executable | `14603a520a8a7d6f460aaa6057097da78e0cdba97a3e620ee8d4fcd3c5b62d2e` |
| Guest bootstrap | `8738b78aed326c02ce95640765b103618565b5e8f90f97442b54ebc79c73b6eb` |
| Detached input ISO | `799ec744f27e7329686e5acb8a3e1f663c82a321f7bc1d4bc940ea5c97068233` |
| Prepared profile, still dispatch-disabled | `3edebcd4b85ae7ce666d953bd3c5527606a7043c42294a0f60000875f8d2eec0` |
| Development-only binding | `9fd432900036552fcdeb95ed1433937e01fbc45b73250aba91f6ed87a0efc209` |
| Independently retained preparation receipt | `775a767ca74f9c18678fc998111b0c9870df1a68db68e453b6af0c50ae9d6c0c` |

Bulk assets remain **ignored and local**, in
`.tmp-sr_pm/trusted-observation/prepared-v3/`. Do not remove this worktree before
the dispatcher preserves them. Committed JSON evidence is in
`docs/evidence/trusted-observation/prepared-v3/`; it is not a substitute for the
actual ISO/binaries.

## Resource and identity boundaries

The original profile remains byte-identical. Limits: 1024 MiB RAM, 1 vCPU,
512 MiB `/work`, 30s boot, 240s command, 300s invocation, 2s stop-ack target,
5s TERM grace, 2s force-kill/cessation wait, 1 MiB guest output, 3 MiB IPC,
15 GB host free-space floor. Network, host shares and paid calls remain disabled.
The existing synthetic 512 MiB and offline 1024/512 MiB profiles are unchanged.

Host evaluator/executor remain UID 320/321. Guest supervisor is UID 0;
candidate UID/GID is 1000/1000, empty supplementary groups. The locked launching
thread sets no-new-privileges and drops the capability bounding set; credential
drop removes effective/permitted capabilities. Supervisor checks the candidate's
actual `/proc/PID/status`, not candidate-provided role metadata.

The original read-only input mount moves under root-only `/root` before candidate
launch. Supervisor/expectations live in root-only `/work/control`; candidate
receives `/dev/null` stdin, captured data pipes, a detached session, and no extra
control descriptors. Console and input block devices are root-only. The separate
helper attempts read/write/replacement/signal and control impersonation; its
bytes are data and do not become verdicts.

Supervisor owns the flock, sticky root-owned vault lock inode, hold/release
schedule, `/proc/locks` observation and no-follow artifact read. This is a bounded
schedule observation, **not exhaustive race freedom**. No permission, capability,
race, stop or isolation assertion is considered demonstrated until real guest
execution and independent evaluation.

## Restored inputs and compiler provenance

- vlt commit: `129e0b3f15a3bd6af949ee47d76f6855c582ab73`; 52 source files verified
  against Git and tar read-back. License blob:
  `c004659349c7a1f6c55e5107b53a0766085e8d2e`.
- Pinned guest Go archive:
  `3f4227ce7b206a513e794f1393adb473a07b46e94d18bd15d1c684bbb7319797`.
  Archive transport uses APFS clonefile, with no fallback full copy.
- Existing Alpine/kernel/initramfs/QEMU inputs were rehashed; exact values are
  in the preparation receipt and match the proposal.
- **Trusted supervisor/helper only** were cross-compiled using host Go 1.26.7,
  compiler SHA `e670dfa79b080bad7f7d6b1d7131145c8c49068096650ebf0ac6292f098db60d`.
  Compiler license text/hash is retained. This new compiler provenance needs
  independent local-use compliance/security review before execution approval.
- Target vlt was **not** built or executed on host. Its build remains guest-only
  with pinned Go 1.26.10. Generated Linux binaries were never executed here.
- Free space after v3 preparation: **15,132,168,192 bytes**. Subsequent shared-host
  changes can reduce this; launch must measure again.

## Verification performed

Commands were synchronous; full logs are committed in the v3 evidence directory.

1. `python3 scripts/prepare-trusted-observation
   .tmp-sr_pm/trusted-observation/source
   .tmp-sr_pm/trusted-observation/go1.26.10.linux-arm64.tar.gz
   ../../../.tmp-sr_pm/vm .tmp-sr_pm/trusted-observation/prepared-v3`
   — exit 0. Actual ELF headers verified static AArch64; all **7 ISO files**
   read back through the primary ISO9660 namespace and byte-hashed.
2. `python3 scripts/verify-trusted-preparation
   .tmp-sr_pm/trusted-observation/prepared-v3
   775a767ca74f9c18678fc998111b0c9870df1a68db68e453b6af0c50ae9d6c0c`
   — exit 0. Reverified binaries/image/profile/source against retained receipt.
3. `go test -count=1 -v -coverprofile=... protocol.go protocol_test.go` —
   **2 passed, 0 failed**, protocol statement coverage **90.6%**. This runs only
   the pure protocol parser on host, not supervisor/helper/candidate code.
4. Linux/arm64 `go vet` on supervisor+protocol and separately helper — both exit 0.
5. `python3 -m unittest discover -s tests -p 'unit*.py' -v` —
   **50 passed, 0 failed, 0 skipped**.
6. Python `coverage --source=research`: **37% overall**, budget 99%,
   observation 98%, evaluator 0%. Linux supervisor guest execution coverage is
   **0%**; parser coverage must not be presented as supervisor coverage.
7. Explicit-path `pvg verify --include-tests --format=text` —
   **12 recognized files, 0 issues**. `sh -n`, gofmt and `git diff --check` pass.
8. `./scripts/test-story trusted-observation` — **exit 1**:
   10 required, 1 executed, 2 prerequisite errors, 0 skips. No integrated pass.

Earlier preparation failures are preserved: insufficient reserved disk headroom,
then v1's incorrect Homebrew license location. v2 completed; v3 superseded it to
honor TERM grace rather than immediate timeout kill. No failed attempt was
rewritten as success.

## Remaining mandatory work and approval

No dedicated trusted-profile host dispatch adapter/root identity launcher exists
yet. Existing synthetic/offline launchers **must not** be repurposed to run this
image. They are not a valid `AWAITING_PARENT_IDENTITY_RUN` command for this profile.
Finish and independently review that adapter, strict evaluator schema/expected
results, root-controlled execution-approval binding, and real integration cases.
All six story ACs remain incomplete end to end; claim remains in progress.

Recommended operator authorization, **after** adapter/security/license review:

> I approve parent-mediated restricted-identity execution, for evidence review
> only, of prepared profile
> `3edebcd4b85ae7ce666d953bd3c5527606a7043c42294a0f60000875f8d2eec0`,
> supervisor
> `a9a0fd9a8471bc1859e5ab91c3746a139942562f719784fec51b8254eb8307d6`,
> helper
> `14603a520a8a7d6f460aaa6057097da78e0cdba97a3e620ee8d4fcd3c5b62d2e`,
> and input image
> `799ec744f27e7329686e5acb8a3e1f663c82a321f7bc1d4bc940ea5c97068233`,
> with the exact original proposal limits and reviewed compiler provenance.
> Run only fixed registered controls through the reviewed trusted-profile
> adapter. Stop on missing prerequisites, unknown outcomes or exceeded limits.
> No resource increase, paid call, host fallback, production mutation or
> automatic admission is authorized. This approval does not certify candidate
> correctness, isolation, race freedom or any resulting finding.

The diff now exceeds the story's approximate 7-file/1,400-line guideline because
the separate supervisor, preparation/verifier and evidence were added. This is
explicitly referred to PM investigation; it is not hidden as a completed story.

## nd_contract
status: in_progress

### evidence
- WIP implementation: 7286815d88cc752bb58f5a9e692278027a61a79e; evidence commit: 96e612d.
- 45 unit tests passed; required integration exit 1 with two prerequisite errors and zero skips. Full research coverage 37%; pvg verify 0 issues.
- Claim retained by dispatcher instruction. No delivery, acceptance, profile execution or remote push.
- docs/evidence/trusted-observation/wip-7286815/STATUS.md SHA256 8f0b5ed981dd9c5e8201e171f189110eb2d2cbdcd47fb6f843c37770a4e855b4.

### proof
- [ ] AC #1: approved guest supervisor challenge remains blocked.
- [ ] AC #2: real guest/service hostile observations remain incomplete.
- [ ] AC #3: supervisor implementation, pinning and profile approval absent.
- [ ] AC #4: actual identity and shared offline accounting proof pending.
- [ ] AC #5: actual service metering, overlap and review proof pending.
- [ ] AC #6: actual store/lost-response/watchdog integration proof pending.

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
