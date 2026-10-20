---
id: GRRR-90te
title: "Block unsafe baselines before an operator starts research"
status: closed
priority: 1
type: task
labels: [milestone-1, integration, delivered]
parent: GRRR-2t3h
created_at: 2026-10-20T03:19:01Z
created_by: speed
updated_at: 2026-10-20T23:46:09Z
content_hash: "sha256:8aa0a3d2511467dc4835d031242327a4567932c55a0e13ebe304a0b23119e12c"
was_blocked_by: [GRRR-0g4n]
assignee: dev-GRRR-90te
follows: [GRRR-0g4n]
closed_at: 2026-10-20T23:46:09Z
close_reason: "Accepted: independently verified pinned offline baseline, real identity/isolation/cancellation controls, exact local-use license scope, and justified evidence/diff growth; admission remains blocked."
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
I can start only with a verified offline baseline and a tested permission boundary, rather than trusting configuration intent.

## OUT OF SCOPE
Full observation-protocol attack matrix belongs to trusted-observation; stop/admission linearization belongs to stop/recovery; no VM provisioning without explicit approval. No security certification against host administrator compromise is promised.

## DIFF BUDGET
~7 files, under 1200 changed LOC. Gross overrun triggers PM investigation, not automatic rejection.

## Boundary Map
PRODUCES:
- research/execution -> `dispatch(principal: Principal, request: ApprovedInvocation, reservation: ReservationId, fence: RunEpoch, key: IdempotencyKey) → Result<DispatchReceipt, Error>`
- research/policy -> `loadPolicy(principal: Principal, ref: PolicyDigest) → Result<VerifiedPolicy, Error>`
- tests/integration/offline-preflight -> spec: real success and all enumerated failure cases via ./scripts/test-story offline-preflight; no mocks, mandatory absence fails

CONSUMES:
- GRRR-0g4n: research/execution
  spec: `dispatch(principal: Principal, request: ApprovedInvocation, reservation: ReservationId, fence: RunEpoch, key: IdempotencyKey) → Result<DispatchReceipt, Error>`
  Usage: dispatch(authenticated evaluator, allowlisted ApprovedInvocation, reservation.id, current RunEpoch, key); reject any Error, stale fence or unknown outcome.
- GRRR-0g4n: research/policy
  spec: `loadPolicy(principal: Principal, ref: PolicyDigest) → Result<VerifiedPolicy, Error>`
  Usage: loadPolicy(authenticated evaluator, pinned PolicyDigest); reject Error or unapproved scope before any work.
- GRRR-0g4n: scripts/test-story
  spec: `./scripts/test-story <story-slug>` → exit 0 only when every required test passes; nonzero for missing infrastructure, skipped mandatory tests or failures (proposed test entrypoint, not installed)
  Usage: Read the versioned artifact or invoke the proposed test entrypoint exactly; validate identity and completeness before use; unknown/missing values block dependent authority.

## Story Acceptance Criteria
1. Operator receives a pinned-baseline preflight receipt identifying source commit 129e0b3f15a3bd6af949ee47d76f6855c582ab73, source/build/image/toolchain hashes, authoritative behavior references and independent clean-baseline tests; verify exact source bytes and license blob rather than trusting supplied metadata.
2. Repeat builds from evaluator-controlled pinned inputs with networking disconnected; record build byte identities and explain/reject unexplained differences. Missing dependencies or a non-clean baseline blocks execution. Inventory direct/transitive dependencies, VM images, tools, models and reused assets with version/hash/origin/license/notices and obligations.
3. MIT, Apache-2.0, BSD-2/3 and ISC require compliance verification; GPL/AGPL/BSL, noncommercial, source-available and unclear licenses require separate review. Record provenance and known-risk inspection; a lockfile or public availability is not clearance.
4. Probe actual guest routes/mounts/devices, host-home shares, clipboard/integration channels and forwarded agents. Candidate cannot reach network, host home/credentials, protected corpus/specs/evaluator, production paths or host writes; approved synthetic input/output works without shared writable storage. Read-only host mounts are not presumed safe.
5. Verify separate OS identities/ACLs, clean reset per invocation, evaluator-owned expectations and resource caps on the chosen VM. Provision only after separate operator approval; absence of virtualization or trusted observation support blocks start, never falls back to host/container execution.
6. Measure watchdog, acknowledgement and graceful/forced cancellation capabilities; obtain numeric policy approval and document host-level emergency VM-stop procedure before execution. Test deliberately misconfigured network/share/identity/image/dependency cases and observe nonpassing preflight with preserved evidence.

## Testing Requirements
Integration tests: MANDATORY (no mocks). Include real success path plus every negative/error/concurrency case enumerated in the AC. Use real local VM, OS identities/permissions, evaluator, transactional store and pinned vlt where the path crosses them; mocks/stubs/fake receipts do not establish integration proof. Unit tests may supplement pure parsing/serialization; they cannot replace real integration. No skip-if-missing or environment-variable shortcut to green.
Proposed required command after implementation: ./scripts/test-story offline-preflight. The walking skeleton creates this test entrypoint; it must enumerate required tests, report counts and exit nonzero on missing prerequisites/failures. This command does not exist today. Capture actual commands, versions, stdout/stderr, exit codes, elapsed/runtime/review costs and artifact hashes; never fabricate results. Any required infrastructure authorization not yet granted blocks test execution explicitly, not story scope.

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

## Historical nd_contract 1
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
OPERATOR OFFLINE BUILD PREFLIGHT PROFILE APPROVAL (2026-10-20):
- Approved two independent fresh disposable VM invocations for pinned vlt source 129e0b3f15a3bd6af949ee47d76f6855c582ab73 using Go 1.26.10 linux-arm64 archive SHA-256 3f4227ce7b206a513e794f1393adb473a07b46e94d18bd15d1c684bbb7319797.
- Per invocation: 512 MiB RAM, 1 vCPU, 300-second total hard ceiling. Cumulative build/test runtime before other probes/replays: maximum 600 seconds.
- Initial command timeout is 240 seconds and explicitly unmeasured; replace with measured result while retaining the 300-second hard ceiling.
- Preserve approved controls: 30-second boot deadline, 2-second stop acknowledgement target, 5-second SIGTERM grace plus mandatory forced kill, 1 MiB output cap, and 15 GB minimum host free space.
- Required isolation: no guest networking, host shares, clipboard integration, or forwarded agents; evaluator-controlled read-only detached asset input; no host build fallback, paid service, production access, automatic main merge, or promotion.
- Unexplained build differences, missing dependencies, license ambiguity, isolation failure, or non-clean baseline must fail closed. Resource exhaustion at 512 MiB is a measured blocker, not permission to increase limits.
OPERATOR LOCAL-USE LICENSE, MACOS TERMS, CLEANUP, AND PREFLIGHT APPROVAL (2026-10-20):
- Operator approved the reviewed 159-component inventory for bounded local offline use only: no source/binary redistribution, no new project linking or copying, notices/source references preserved, GPL/LGPL components confined to local execution under the approved isolation boundary.
- Operator confirmed installed macOS build 26A428 terms permit local execution of installed system frameworks and QEMU for this non-redistributable preflight.
- Operator approved deletion of only /Users/speed/.gradle/caches, a regenerable build cache.
- Operator approved parent-mediated root identity execution for GRRR-90te after the disk gate passes and the exact license-review artifact is bound.
- Runtime offline dependency closure, reproducibility, isolation, cancellation, and license checks remain mandatory and must fail closed on ambiguity or mismatch.
- Review basis: license-review-draft.json SHA-256 4d3e93ebb6ac205225e7521c951a93baa64335a899710619ae3f593f7b3cf0c6; provenance addendum SHA-256 3be01e90783d6cfeb928585691c86d7413a37c02c8d5e0bc93135cb4cc36bc67.
AUTHORIZED GRADLE CLEANUP RESULT (2026-10-20): removed only /Users/speed/.gradle/caches (1.7 GiB, 19,865 files); df rose from 13 GB to 15 GB; manifest .tmp-sr_pm/gradle-cleanup-manifest.txt. No model/project/output cache touched.
AUTHORIZATION ARTIFACT FINALIZATION: documentation/evidence-only commit fa0949766a836af84a0247ccf189b4dbda5f86bd. Final ignored private license-review.json SHA256 4ce0bb6c8533eb9036b28d0145f6856a80a8f66a0cb93cee0fe6124b5acc8aaf; owner UID 501 mode 0600; exact 159 components and four risk dispositions; classification counts preserved 54 permissive / 80 boundary-controlled / 25 Apple-system. Authorization reference 033330e01fda00835902bdd7cb0016338fe7891146d4501ef3e6fa1d2d00b8d5 binds four operator/license evidence artifacts. Both parent Gradle cleanup files copied byte-identically (SHA256 de0617ffa519fa284b03e03f13e0eec0ab8620c12887d14df43cd44ee1577851). Unit tests 24/24 passed; pvg verify six files passed; py_compile and sh -n passed. Free bytes at final verification 16530137088; root launcher must recheck 15000000000 floor. No root/sudo/VM invocation performed. Ready for parent-mediated root run; not delivered or accepted.
REGENERABLE HOMEBREW CACHE CLEANUP (2026-10-20): removed only /Users/speed/Library/Caches/Homebrew (208M, 1,576 files); free space now 15,260,770,304 bytes. Manifest preserved in main checkout .tmp-sr_pm/homebrew-cache-cleanup-manifest.txt. No project/model/output data touched.
REGENERABLE CARGO CACHE CLEANUP (2026-10-20): removed only /Users/speed/.cargo/registry/src (410M, 21,720 files) and /Users/speed/.cargo/registry/cache (57M, 477 files); free space now 15,551,619,072 bytes. Manifest main checkout .tmp-sr_pm/cargo-cache-cleanup-manifest.txt. No project/model/output data touched.
OPERATOR 1024 MiB OFFLINE VM APPROVAL (2026-10-20):
- Operator explicitly increased offline-build VM memory from 512 MiB to 1024 MiB and authorized rerunning GRRR-90te parent identity integration.
- All other limits remain unchanged: 1 vCPU; 300-second total hard ceiling per invocation; 240-second initial command timeout replaced by measured result; two fresh VMs; maximum 600 seconds cumulative build/test runtime before other probes; no guest networking/host shares/clipboard/forwarded agents; no host build fallback, paid service, production access, automatic main merge, or promotion; 1 MiB output cap; 15 GB host-free-space gate; existing stop and force-kill controls.
- If compilation still fails at 1024 MiB, stop again; do not automatically increase resources.
OPERATOR 512 MiB WORKFS APPROVAL (2026-10-20):
- Operator explicitly increased the offline-build guest ephemeral /work tmpfs cap from 350 MiB to 512 MiB and authorized rerunning GRRR-90te parent identity integration.
- VM RAM remains 1024 MiB. All other limits remain unchanged: 1 vCPU; 300-second total hard ceiling per invocation; 240-second initial command timeout replaced by measured result; two fresh VMs; 600-second cumulative build/test runtime before other probes; no guest networking, host shares, clipboard, or forwarded agents; no host build fallback, paid service, production access, automatic main merge, or promotion; 1 MiB output cap; 15 GB host-free-space gate; existing stop and force-kill controls.
- If linking still fails at 512 MiB /work, stop again; do not automatically increase resources.
## PM Decision
ACCEPTED [2026-10-20]: Independent bounded review of delivery a1d2148d8a8216e4db964b1a4fc76ee10f48c564 against epic e841545dedef472ffc2c74414a3a425d7bf27acf. Runtime source at 403c907 is unchanged by the final documentation commit. No privileged integration rerun, source edit, branch checkout, merge, or push performed.

## nd_contract
status: accepted

### evidence
- Reviewed full changed implementation/test diff and exact source files, final-audit/AUDIT.md, canonical successful attempt, approval amendments, license review and provenance addendum.
- Ran pvg verify on research/offline.py research/offline_execution.py research/policy.py tests/unit_offline.py tests/unit_offline_runtime.py tests/integration/offline_preflight.py tests/integration/offline_probe.py: 7 files, 0 issues. git diff --check and guest sh -n passed. No incomplete stubs/thin files; three bare pass statements are intentional process-cleanup exception handlers. New public functions carry type annotations.
- Ran python3 scripts/verify-offline-evidence docs/evidence/offline-preflight/attempt-20261020T233115Z-6e1e938c: PASS, six evaluator snapshots; 6 required/executed, 0 skipped/errors/failures. Independently hashed manifest 85fbaadbae832ebb67110bbdfe980025fc011d6adb720866054acb4c690b1c16 and license review 4ce0bb6c8533eb9036b28d0145f6856a80a8f66a0cb93cee0fe6124b5acc8aaf.
- Inspected recorded 31/31 unit output and unit-only 24.0761478163% coverage; no integration coverage inferred. Successful integration output is clean; deliberate negative-service errors and prior failed attempts are expected preserved evidence, not dismissed defects.
- Diff-budget investigation: 329 files / 3921 additions / 2 deletions total; implementation/tests 13 files / 1525 additions / 2 deletions. Growth is attributable to distinct preparation, guest, identity launcher, runtime adapter, independent verifier and real negative tests plus preserved attempts/license/authorization evidence. No unrelated core changes or excluded admission/observation-attack implementation found. Separation of trust roles justifies overrun.
- Canonical current result is final-audit/AUDIT.md and successful attempt; STATUS.md and earlier draft/blocked artifacts are historical checkpoints, not current authorization or baseline results. Approval docs retain original limits and explicit later amendments rather than silently rewriting history.
- Graph-tool discovery unavailable in this worker; bounded source/diff fallback used. pvg notes search could not resolve a worktree-local notes vault; live story/children operations resolved shared git-common-dir nd vault correctly. No issue files read directly.

### proof
- [x] AC #1: exact 52 source blobs and LICENSE blob verified; pinned source/toolchain/VM identities bound through inventory/profile/assets; actual full upstream tests and synthetic create/read observed.
- [x] AC #2: two fresh offline VMs produced identical ae21fbda8127e7560c30bbd1026d79dffafefe4a32a78728521228a1162af5ea binaries; total 92.563880959s; source checks before/after; actual dependency output and full inventory retained.
- [x] AC #3: exact 159-component operator-approved local-use review, 54 permissive / 80 boundary-controlled / 25 Apple-system classifications, notice/provenance exceptions retained. No redistribution, new project linking, Apple extraction or additional rights inferred; dyld per-image hash limitation explicit.
- [x] AC #4: actual guest routes/mounts/devices show loopback-only and detached read-only input; fixed QEMU arguments omit network/shares/integration/agents; protected path and write denial probes plus guest synthetic IO pass.
- [x] AC #5: separate OS identities, protected evaluator policy/expectations, root-readonly inputs, fresh reset, one active VM and approved RAM/workspace limits verified in code and real evidence; no host/container fallback.
- [x] AC #6: real bad network/share/identity/image/dependency controls, concurrency rejection, acknowledgement, graceful/forced stop, watchdog and output cap pass. Numeric original profile and narrow 1024 MiB RAM / 512 MiB work amendments are recorded; emergency exact-PID stop procedure documented.

Residual boundaries: baseline only; admission and promotion remain blocked. Full observation attack matrix, stop/admission linearization, general budget lifecycle and adversarial runner/administrator certification are not granted by this acceptance. The registered test-story wrapper was inspected and delegates to the tested launcher; it was not separately rerun. No DISCOVERED_BUG blocks raised by this bounded review.

## Implementation Evidence
PROOF: See committed final audit a1d2148d8a8216e4db964b1a4fc76ee10f48c564 and complete AC Verification table above. Independent verifier PASS; integration 6/6 no skips/failures; units31/31; unit-only coverage24.0761478163%; pvg verify7files0issues.
LEARNINGS: Exact ISO namespace and resource-boundary evidence are mandatory.

## Historical nd_contract 2
status: delivered

### evidence
- Commit a1d2148d8a8216e4db964b1a4fc76ee10f48c564. Canonical successful attempt attempt-20261020T233115Z-6e1e938c; offline verifier PASS.

### proof
- [x] AC #1: pinned source/license/toolchain/image and full baseline tests verified.
- [x] AC #2: two clean independent offline builds byte-identical; dependencies inventoried.
- [x] AC #3: complete scope-limited operator license/provenance review bound.
- [x] AC #4: actual guest isolation and synthetic IO plus host permission probes pass.
- [x] AC #5: independent identities/ACLs/reset and approved resource caps pass.
- [x] AC #6: actual negative configs, watchdog, acknowledgement and graceful/forced cancellation pass; emergency procedure approved.

## Historical nd_contract 3
status: delivered

### evidence
- Transitioned via pvg story deliver on 2026-10-20.

### proof
- [ ] Developer evidence block must remain authoritative above this contract.


## Implementation Evidence

PROOF:

### CI/Test Results
Commands run:
- Parent: /opt/homebrew/bin/python3 scripts/offline-identity-integration <main .tmp-sr_pm/vm> <story .tmp-sr_pm/offline-preflight/assets-20261020-1> <same assets/license-review.json>, at runtime code commit 403c907e66095ee9d860158e069e0d963d8a9b48. Exact absolute command in dispatcher handoff. Same launcher used by ./scripts/test-story offline-preflight; entrypoint not separately rerun.
- python3 scripts/verify-offline-evidence docs/evidence/offline-preflight/attempt-20261020T233115Z-6e1e938c
- PYTHONPATH=.tmp-sr_pm/final-coverage-tools COVERAGE_FILE=.tmp-sr_pm/final.coverage python3 -m coverage run --source=research -m unittest discover -s tests -p 'unit*.py' -v
- Same environment: python3 -m coverage json -o docs/evidence/offline-preflight/final-audit/unit-coverage.json; python3 -m coverage report
- pvg verify research/offline.py research/offline_execution.py research/policy.py tests/unit_offline.py tests/unit_offline_runtime.py tests/integration/offline_preflight.py tests/integration/offline_probe.py
- python3 -m py_compile scripts/prepare-offline-assets scripts/prepare-offline-preflight scripts/offline-identity-integration scripts/test-story scripts/verify-offline-evidence
- sh -n research/offline-guest.sh

Summary: integration 6/6 PASS, zero skipped/errors/failures, launcher exit 0, 348.058 seconds. Independent evidence verifier PASS, six snapshots, baseline_verified=true. Unit 31/31 PASS, zero skipped; Python/shell static checks PASS. pvg verify PASSED, 7 files scanned, 0 issues.
Coverage: unit-only research line coverage 24.0761478163% (215/893), coverage.py 7.13.4. No integration coverage inferred.

### Commit
Branch: story/GRRR-90te
SHA: a1d2148d8a8216e4db964b1a4fc76ee10f48c564
Runtime implementation SHA: 403c907e66095ee9d860158e069e0d963d8a9b48

### Evidence identities
- Canonical attempt docs/evidence/offline-preflight/attempt-20261020T233115Z-6e1e938c; audit docs/evidence/offline-preflight/final-audit/AUDIT.md.
- Manifest SHA256 85fbaadbae832ebb67110bbdfe980025fc011d6adb720866054acb4c690b1c16.
- Test-output SHA256 1a88076a5222ac0217f6eb59d642049d1bb3138c3d457d657dbcadcdd7246946.
- Baseline receipt SHA256 cd26c3022ac378d726136079b0989eed5ff8842b6afaf613fdfa2420256ebd50.
- Both build SHA256 ae21fbda8127e7560c30bbd1026d79dffafefe4a32a78728521228a1162af5ea.
- Profile SHA256 2e08f0288355a64eba22b75fdeb1e62ac14dfaea3be26cbee38ece6eb4051d47.
- License review SHA256 4ce0bb6c8533eb9036b28d0145f6856a80a8f66a0cb93cee0fe6124b5acc8aaf.
- Measured command maximum 44.959017792s; invocation maximum 46.332908917s; two builds total 92.563880959s. Measured observations replace unmeasured assumption, not approved 240/300 second ceilings.

### AC Verification
| AC | Evidence | Status |
|---|---|---|
| 1 | research/offline.py verifies pinned commit, all 52 source blobs, correct LICENSE blob, authoritative behavior references; inventory/receipt bind source/toolchain/image; baseline receipt and independent full tests. | PASS |
| 2 | offline_execution.py and offline_preflight.py test_06 use two independent clean offline VM runs, identical binary hashes, printed real dependency closure, full inventoried tools/assets. Missing dependency negative blocks. | PASS |
| 3 | 159-component exact-inventory operator review, license/provenance addendum, all risk resolutions; GPL/LGPL local-use boundaries and macOS terms explicit. No redistribution/new-linking clearance inferred. | PASS |
| 4 | Guest actual routes/mounts/devices, no host/credential/protected paths or channels, readonly detached inputs reject writes; synthetic vault IO works. Real host permission probes pass. | PASS |
| 5 | Separate service identities/ACLs, root-readonly assets/config, evaluator-private policy; test_06 clean reset and unchanged inputs, bounded 1024 MiB RAM/512 MiB work approved separately. Synthetic remains unchanged. | PASS |
| 6 | Real misconfiguration network/share/identity/image/dependency probes and tests_02–05 concurrency/stop/forced/watchdog/output-cap PASS. Approved numeric limits and emergency-stop procedure predate execution. All failures preserved. | PASS |

Boundary map: research/execution retains accepted synthetic Executor; offline specialization research/offline_execution.py extends it; research/policy.py loads exact protected offline profile; logical tests/integration/offline-preflight maps to offline_preflight.py plus offline_probe.py/root launcher. No pvg/nd/vlt core changes.

LEARNINGS:
- Verify base ISO9660 names, not just Joliet/macOS extension-aware listings.
- Archive source/toolchain to preserve exact hidden/case/long names.
- Persist failure diagnostics before assertions.
- Separate RAM, guest workspace, and host disk boundaries; changes require operator approval.
- Unit coverage is supplementary, never a substitute for real identity/VM tests.

Residual boundaries: baseline only, admission/promotion intentionally blocked; full observation attack matrix and stop/admission linearization remain other stories. Diff budget exceeded: 13 implementation/test files and 1525 additions/2 deletions relative to accepted epic base, excluding evidence. PM investigation required; no waiver or automatic acceptance claimed.


## Historical nd_contract 4
status: in_progress
### evidence
- Approved offline /work tmpfs increased only to 512 MiB, now explicit in profile and strict runtime config; guest uses size=512m. VM RAM remains 1024 MiB and synthetic policy unchanged.
- 31 unit tests, shell syntax/Python compilation and pvg verify 4 files pass. Old image/receipt retained; new ISO primary GO.TGZ extent hash verified.
- Profile 2e08f0288355a64eba22b75fdeb1e62ac14dfaea3be26cbee38ece6eb4051d47; approval ea54419888597cacde66c9a73efa86eacd52dde96bf0c098b0b7fd728277b3b2; receipt bfcb6b9f5fac29267ade2c50258f1b99106b69ae808c936062e442cc39191666; image 7e75d23870510175489ba818b7795dfbb9fde7cd1a69c00e36e735c76cbdb5ce.
- Parent root run pending; no privileged execution here. If /work fills at 512 MiB stop, no further increase authorized.
### proof
- [ ] AC #1-#6: mandatory real baseline proof remains pending; not delivered.

## Historical nd_contract 5
status: in_progress
### evidence
- BLOCKED: attempt-20261020T205833Z-60a4135e reached linking under approved 1024 MiB RAM; linker mapping output failed: no space left on device. Guest /work tmpfs 350 MiB cap, not host disk or compiler kill.
- Tests 1-5 passed; 6/6 executed, zero skips, one failure. Duration 18.121606208s; command 16.788934333s. All 24 manifest hashes verified.
- Manifest SHA256 0a0b4707b4c4f6a40d9dab62b2d4948cabf3e858fd47d8dad2e9db5aacb93ebb; build 362724662f774edefae58a42cbd2384105d72b4116418fa66ee08daccc9cdbef; test-output 7e2068f1d8654238bef8dcccae589fb6442c960cf461717988160aa6fff270c7.
- Operator decision requested: increase only guest ephemeral /work tmpfs from 350 MiB to fixed 512 MiB; RAM stays 1024 MiB, all other limits unchanged. Not applied; no VM rerun or delivery. Documentation/evidence-only checkpoint; code unchanged.
### proof
- [ ] AC #1-#6: baseline remains false; independent successful builds unproven.

## Historical nd_contract 6
status: in_progress
### evidence
- Explicit operator-approved 1024 MiB offline-only amendment implemented in profile, adapter validation/QEMU arguments, root launcher and preparation approval binding. Synthetic remains 512 MiB; every other limit unchanged.
- 31 unit tests pass including exact limits comparison and rejection of 512/2048 offline configs; Python compilation and pvg verify 4 files pass.
- New profile 6dc4ea9d4da104b22d9865edfa64487d817eb40aaa5425d37c565c4280f4dfd3; approval 2fa136998c51d4a0dc3d3ffc535345d4b1b815dc1c660ae6ceba064efe8c365c; receipt c55cbe8d5c1e13918efbd0cedaf8b7a15233626b57e3cf973a89d5f5a7ad5eba. Image unchanged ff523652e7f0073df3424732d924b5223dc719f1e373ad1cbe44f88194bac38a.
- Parent identity run required; no privileged run by worker. If compiler killed at 1024 MiB, stop with no further resource increase. Prior 512 MiB evidence preserved.
### proof
- [ ] AC #1-#6: awaiting mandatory successful real baseline evidence; not delivered.

## Historical nd_contract 7
status: in_progress
### evidence
- BLOCKED checkpoint: attempt-20261020T182702Z-768d552e, all 24 artifact hashes verified. Manifest SHA256 b4e19f303ae9cf644484de878014a9b51e142cc4989c0a5eb55c8174222ced0b; build SHA256 a0949547b9a7f7c4a700887e80ddda4d391ecda3c7d3bb5bd0ebfb41d9dc8017.
- Tests 1-5 passed; 6/6 executed, zero skipped, first build failed with runtime compiler signal: killed under approved 512 MiB. Total 193.6099525s, command 174.8244202s. Compiler kill directly proven; kernel OOM diagnostic not captured. Resource boundary is a blocker, not permission to raise limits.
- 31 unit tests and static checks pass; no VM rerun. Failure evidence and all inputs retained. See resource-blocked-checkpoint/BLOCKED.md.
- Operator decision required to approve higher memory or alternative isolated execution strategy; no automatic retry, host fallback, delivery or promotion. Dispatcher to release claim.
### proof
- [ ] AC #1-#6: baseline remains false; no successful independent builds or complete baseline proof. Not delivered.

## Historical nd_contract 8
status: in_progress
### evidence
- go.tgz primary ISO namespace repair: direct PVD/root directory read-back proves GO.TGZ contains exact pinned Go archive SHA, independent of Joliet. 31 unit tests/static checks pass.
- All failed attempts and prior images preserved. Only authorized Go duplicate removed with deterministic manifest; repack waited for parent Cargo cleanup. Free bytes after repack 15486951424.
- Image ff523652e7f0073df3424732d924b5223dc719f1e373ad1cbe44f88194bac38a; receipt 594cb1a07adc6134be81b05035c275562b558a9853eeb2b3ccb9ed39d512157a.
### proof
- [ ] AC #1-#6: real build proof outstanding; no developer root execution; not delivered.

## Historical nd_contract 9
status: in_progress
### evidence
- Go archive transport repair: pinned archive read back from new ISO and hash verified; guest verifies and extracts only inside /work. Prior fourth failure and old image retained.
- 30 unit tests, shell syntax, Python compilation and pvg verify pass.
- Image fb3a017ecf56fd3f9e211fcd7fefd468ace46e5914c25df35a0689f62e8a5cd9; receipt 7eaf64a4c309d10a5b94740e17c05d83c6ce1aba580c97783acd0ba1e501e090.
- Only about 65 MB disk headroom above hard floor; parent disk gate mandatory. All VM/work limits unchanged; exhaustion remains blocker.
### proof
- [ ] AC #1-#6: real build proof outstanding; no developer root run; not delivered.

## Historical nd_contract 10
status: in_progress
### evidence
- Exact 52-file source tar transport replaces loose ISO source tree; names, modes, hashes verified after reading archive back from generated ISO. Third failed attempt preserved unchanged.
- 29 unit tests, shell syntax, Python compilation and pvg verify pass.
- Image SHA256 797b99fad8534f2a49a7dc7954d0f008abd36941e361ef0e4167dd5698bd2220; receipt SHA256 024d7d3a2f56e5942c17494392c49625eb638a3deaa6189d9711fe938c312c9f. No root execution; parent rerun mandatory.
### proof
- [ ] AC #1-#6: real offline build proof outstanding; not delivered.

## Historical nd_contract 11
status: in_progress
### evidence
- Isolation repair: 28 unit tests pass, shell syntax and Python compilation pass, pvg verify passes.
- Preserved second failure attempt-20261020T174728Z-f95be96e unchanged: controls, stop, forced cancellation, watchdog and output cap passed; first build isolation failed. Empty IPv4 route table and boot snapshot/input distinction repaired with named diagnostics.
- New input image SHA256 1a5dc0e5c64fa107fd186196d88d0d138a71b2d0796b30766841e75fbbb4ad89; receipt 3f8fefed6a5b9b2c1569295d75df470fa0cb6107154e16c97c3607029d17b5d6. Prior assets retained; no root run by worker.
### proof
- [ ] AC #1-#6: parent real baseline rerun remains mandatory; not delivered.

## Historical nd_contract 12
status: in_progress

### evidence
- Repair commit f4f6e96c9bd965a6aad8bcf74b5aaf8c2c3b1067: detached read-only input discovery and failure receipt preservation.
- 26 unit tests passed; pvg verify 3 changed Python files passed, zero issues; py_compile passed.
- Parent attempt attempt-20261020T174216Z-4fb11b30 preserved unchanged: 2/6 executed, 1 failure, 0 skips. Readiness failure proven; exact guest device assignment unavailable in exported evidence.
- No root execution by developer; parent rerun required. Input image and private license review unchanged.

### proof
- [ ] AC #1-#6: mandatory real offline integration remains unproven; no delivery.

## Historical nd_contract 13
status: in_progress

### evidence
- Commit 6c7b93e165e141d8884f2318934cfe84763a244c implements approved offline profile, fixed guest adapter, root launcher, real mandatory suite and independent verifier. Worktree clean after commit; no delivery/acceptance.
- Operator profile approval versioned in docs/OFFLINE-PREFLIGHT-APPROVAL-2026-10-20.md. Synthetic behavior unchanged; separate root-bound offline loadPolicy branch.
- Preparation manifest SHA256 51b5f46f6fdde846096f711ec7c483aa858abf1ac4fa597d5fee6a0966ac0b05 under docs/evidence/offline-preflight/approved-preparation/. Independently verified 10 artifact hashes, source/image/bootstrap/inventory bindings.
- Inventory: 101 Alpine APKs, 16712 Go archive members, 41 notice matches, 56 host runtime components. GPL/mixed licenses and four explicit risks still require separate substantive review; no clearance fabricated.
- Authorized deletion only of regenerable media/go: 15045 files / 227769067 bytes; tree digest 777d4e351960e6e55c8bd521992ebf35afa3a740fa0037f0e2fc6b8aeb214b54. Both ISOs, source and pinned archive retained. Actual df pre-combined-repackage/cleanup and post recorded. Host space moving near 15-GB floor; gate unchanged.
- Root launcher uses clonefile(2) directly because cp -c silently falls back; rehashes root-owned ACL-stripped read-only clones. Actual independent clone test passed.
- Unit suite 24/24, zero skips; unit-only research coverage 22.46%. pvg verify passed six Python files; extensionless scripts py_compile and guest sh -n passed. git diff --cached --check passed.
- ./scripts/test-story offline-preflight run without privilege: exit 1, AWAITING_PARENT_IDENTITY_RUN. No new guest/build/test execution. Exact parent command and required review schema are in STATUS.md.
- Budget disclosure: total story diff exceeds approximate seven-file/1200-LOC guideline; distinct launcher/guest/bootstrap/inventory/verifier/test trust roles retained for PM investigation.

### proof
- [ ] AC #1: exact source/license/toolchain/image hashes present; real clean-baseline receipt pending root run.
- [ ] AC #2: two fresh builds implemented, not executed; dynamic Go dependency confirmation pending.
- [ ] AC #3: inventory metadata/notices preserved; separate license review and compliance proof unresolved.
- [ ] AC #4: actual guest isolation/synthetic I/O probes implemented, unexecuted.
- [ ] AC #5: root-controlled immutable staging and identity/ACL probes implemented, privileged execution pending.
- [ ] AC #6: explicit numeric profile approved; real watchdog/ack/TERM/KILL and five misconfiguration tests implemented, measurements pending.

### learnings
- cp -c is not a strict clone primitive on macOS. Use clonefile without copy fallback near hard disk gates.
- Preserve preparation-stage success separately from verified baseline status; a complete metadata inventory is not license clearance.


## Historical nd_contract 14
status: in_progress

### evidence
- Authorization-boundary WIP committed 90f4da212b3711d717d00d32f412d0681c6accd6; not delivered or accepted.
- Non-executing preparation verified pinned vlt commit/license/every tracked source byte and Go 1.26.10 archive; source/toolchain remain ignored preparation assets, not Git code imports.
- Final evidence: docs/evidence/offline-preflight/preparation-20261020T160545Z-bc3d6dc7; manifest SHA256 30a5624ef6f1321ca77ab1f2d78a38b8cd9a7432652e553bc85eb9afadb64033. Manifest artifacts and inventory/profile binding independently rechecked.
- python unittest discovery: 17/17 passed, zero skips. Coverage unit-only research 22.95%, offline module 41.76%. No VM/source/build/test execution of new profile.
- pvg verify explicit 3 code paths: passed (2 .py scanned; extensionless script independently py_compile checked). git diff --cached --check passed.
- Dispatcher requires operator approval before new offline Go profile execution. Proposal: 512 MiB, 1 CPU, 300 seconds per fresh VM, 2 independent builds (600 seconds cumulative max), 240-second command timeout UNMEASURED, no networking/shares/paid calls. Existing synthetic policy unchanged.
- Full inventory/license compliance, detached read-only input image, VM adapter/root launcher and mandatory offline-preflight integration suite still incomplete. No root command fabricated. See docs/evidence/offline-preflight/STATUS.md.

### proof
- [ ] AC #1: source identity verified; offline baseline receipt absent.
- [ ] AC #2: toolchain/source inputs pinned; independent VM builds not executed.
- [ ] AC #3: licenses/notices inventoried partially; separate review and full compliance incomplete.
- [ ] AC #4: new-profile actual isolation probes not executed.
- [ ] AC #5: no policy/identity/cap weakening; new-profile integration outstanding.
- [ ] AC #6: explicit approval absent; cancellation/misconfiguration measurements outstanding.

### learnings
- Preparation success must remain distinct from preflight success. Preserve binary notice-name matches as bytes. Synthetic-only approval does not authorize a Go build profile.


## History
- 2026-10-20T03:19:01Z dep_added: blocked_by GRRR-0g4n
- 2026-10-20T03:19:02Z dep_added: blocks GRRR-gu87
- 2026-10-20T03:19:04Z dep_added: blocks GRRR-6sso
- 2026-10-20T15:56:23Z dep_removed: was_blocked_by GRRR-0g4n
- 2026-10-20T15:59:07Z status: open -> in_progress
- 2026-10-20T15:59:07Z auto-follows: linked to predecessor GRRR-0g4n
- 2026-10-20T15:59:07Z claimed by dev-GRRR-90te
- 2026-10-20T23:40:54Z status: in_progress -> in_progress
- 2026-10-20T23:46:09Z status: in_progress -> closed
- 2026-10-20T23:46:09Z dep_removed: no_longer_blocks GRRR-gu87
- 2026-10-20T23:46:09Z dep_removed: no_longer_blocks GRRR-6sso

## Links
- Parent: [[GRRR-2t3h]]
- Was blocked by: [[GRRR-0g4n]]
- Follows: [[GRRR-0g4n]]

## Comments

## nd_contract
status: delivered

### evidence
SHA: a1d2148d8a8216e4db964b1a4fc76ee10f48c564
- Runtime code 403c907e66095ee9d860158e069e0d963d8a9b48.
- Successful attempt docs/evidence/offline-preflight/attempt-20261020T233115Z-6e1e938c.
- Independent python3 scripts/verify-offline-evidence verification PASS, six evaluator snapshots.
- Manifest SHA256 85fbaadbae832ebb67110bbdfe980025fc011d6adb720866054acb4c690b1c16.
- Integration 6/6 executed, 0 skipped/errors/failures; two builds byte-identical ae21fbda8127e7560c30bbd1026d79dffafefe4a32a78728521228a1162af5ea.
- Unit31/31 pass; unit-only research coverage24.0761478163% (215/893), not integration coverage. pvg verify7files0issues; shell/Python static pass.
- Measured command max44.959017792s, invocation max46.332908917s, two builds92.563880959s. Approved ceilings unchanged.
- Full PROOF/LEARNINGS and PM diff-budget investigation retained above and in committed final-audit/AUDIT.md. Baseline only; admission/promotion blocked.

### proof
[x] AC #1: exact pinned source and license blob, toolchain/image identities and clean-baseline tests verified.
[x] AC #2: independent offline fresh VM builds match; complete inputs/dependency inventory and runtime closure retained.
[x] AC #3: 159-component exact-inventory local-use license review and risk resolutions operator-approved.
[x] AC #4: actual guest routes/mounts/devices and protected-host denial pass; synthetic IO without writable shares.
[x] AC #5: separate OS identities/ACLs, evaluator protection, clean resets and approved resource caps pass.
[x] AC #6: numeric stop/watchdog/forced cancellation and misconfiguration probes pass; emergency procedure approved.
