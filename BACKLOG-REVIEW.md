# First-milestone backlog review

Date: 2026-10-19 operator-local date. Authoring only; no implementation, experiment, runtime test, provisioning or promotion performed.

## Result

Existing epic **GRRR-2t3h — Milestone 1: Governed vlt research ratchet** retained. Created 11 children through `pvg issues create`; all remain open, P1, with initial `nd_contract: new`. No hard-tdd labels. No Anchor invocation or recursive delegation.

| ID | Title | Direct blockers |
|---|---|---|
| GRRR-0g4n | Observe one bounded challenge through the trusted research path | None |
| GRRR-90te | Block unsafe baselines before an operator starts research | GRRR-0g4n |
| GRRR-gu87 | Reject forged observations before spending evaluation authority | GRRR-90te |
| GRRR-my5n | Recover a verifiable experiment snapshot after interruption | GRRR-gu87 |
| GRRR-c875 | Stop a hung research run through independent trusted control | GRRR-my5n |
| GRRR-bnkf | Inspect a frozen representative vlt defect corpus | GRRR-c875 |
| GRRR-z3w9 | Verify a defect from fresh trusted inputs | GRRR-bnkf |
| GRRR-dbbi | Compare three selectors without overstating research value | GRRR-bnkf, GRRR-z3w9 |
| GRRR-34ve | Admit one human-approved contract that rejects recurrence | GRRR-z3w9 |
| GRRR-fmvp | Review the same governed decision across accessible surfaces | GRRR-dbbi, GRRR-34ve |
| GRRR-6sso | E2e: Operator completes a governed vlt research ratchet | All ten siblings above |

All children have `milestone-1`; the first ten have `integration`; GRRR-0g4n has `walking-skeleton`; GRRR-6sso has `capstone`. Provider default issue type is `task` (the Paivot role is still a story); IDs were not recreated.

## Measured mechanical gates

Full commands, exit codes and outputs: `.tmp-sr_pm/gate-results.txt` and `.tmp-sr_pm/gate-results.json`.

| Command | Exit | Observed result |
|---|---:|---|
| `pvg rtm check` | 0 | 0 requirements extracted, 0 covered, 0 uncovered; 12 issues checked. This is NOT proof of semantic coverage. |
| `pvg lint --backlog` | 0 | 12 issues scanned, **0 errors, 0 review findings** |
| `pvg nd dep cycles` | 0 | No dependency cycles |
| `pvg nd epic close-eligible` | 0 | No close-eligible epics, correctly: all children remain open |
| `pvg nd graph GRRR-0g4n` | 0 | Reachable dependency graph inspected; repeats of shared descendants are graph rendering, not duplicate IDs |
| `pvg nd epic tree GRRR-2t3h` | 0 | Existing epic plus exactly 11 children |
| `pvg nd stale --days=14` | 0 | No stale issues |
| `pvg nd stats` | 0 | 12 total/open, 10 blocked, 0 in progress/closed; 11 tasks plus one epic |

The additional audit script checked all 11 live canonical bodies, single authored-body occurrence, parent/status, exact dependency edges, matching upstream PRODUCES for every CONSUMES, no hard-tdd, all ten capstone blockers and unchanged D&F hashes. Result: passed. Evidence: `.tmp-sr_pm/audit-checks.json`, `.tmp-sr_pm/backlog-final.json`, `.tmp-sr_pm/children-final.json`.

## Manual requirement coverage (RTM lacks tagged inputs)

The approved twelve architectural ACs are mapped explicitly rather than claiming the empty RTM extraction proves coverage.

| Approved architecture AC | Primary child proof | Full-workflow confirmation |
|---|---|---|
| 1 Isolation | GRRR-90te AC 4-6; minimum real isolation GRRR-0g4n AC 6 | GRRR-6sso AC 1, 5 |
| 2 Identity/offline baseline | GRRR-90te AC 1-3 | GRRR-6sso AC 1 |
| 3 Trusted observation | GRRR-gu87 AC 1-3 | GRRR-6sso AC 5 |
| 4 Ledger | GRRR-my5n AC 1-6 | GRRR-6sso AC 4-5 |
| 5 Replay/spec | GRRR-z3w9 AC 1-5 | GRRR-6sso AC 1-2, 5 |
| 6 Admission | GRRR-34ve AC 1-7 | GRRR-6sso AC 1-2, 4 |
| 7 Corpus | GRRR-bnkf AC 1-6: preliminary trusted fixture validation/freeze only | GRRR-6sso AC 2: complete mandatory-system 100% critical/>=90% other detection proof |
| 8 Comparison | GRRR-dbbi AC 1-7 | GRRR-6sso AC 3 |
| 9 Budget/stop | GRRR-gu87 AC 4-6; GRRR-c875 AC 1-7; GRRR-34ve AC 5 | GRRR-6sso AC 4-5 |
| 10 Recovery | GRRR-my5n AC 3-6; GRRR-c875 AC 5-7; GRRR-34ve AC 4-7 | GRRR-6sso AC 4 |
| 11 Surface parity | GRRR-fmvp AC 1-9 | GRRR-6sso AC 5-6 |
| 12 Scope/security | Embedded constraints in every child; GRRR-0g4n AC 3-6; GRRR-90te AC 2-6; GRRR-dbbi AC 3-4; GRRR-fmvp AC 9 | GRRR-6sso AC 5, 7 |

Business coverage: protected baseline/evaluator, representativeness and >=20 scenarios, clean negatives, 100% critical/>=90% other seeds, equal budgets, >=3 randomized repetitions where feasible, >=20% defects/dollar target, uncertainty/FP/FN/variance/confidence/costs, zero unverified or failed-replay admission, complete Counterexample-to-Contract recurrence proof, POC/milestone limits and every hard-stop trigger are explicit. Negative Jev performance is valid evidence; unavailable Jev is incomplete comparison, not manufactured success.

Design coverage: all seven CLI intentions, progressive three-level report, separate execution/finding/decision/effect, three authorization types, exact-target confirmation, actual effect receipts, stale/missing evidence blockers, recorded-versus-fresh replay, accessible keyboard/screen-reader journeys, stop/recovery truth and measured review burden are embedded in GRRR-fmvp and exercised by GRRR-6sso. Minimal parity and discoverability begin in the skeleton.

## Terminology and interface audit

- All eight approved `research/*` function contracts were extracted verbatim from the architecture table; Error codes and Principal semantics retained. Shared API signatures match upstream producers byte-for-byte.
- `ResourceVector`, `RunEpoch`, `ActionBinding`, `ReplayReceipt`, `AdmissionReceipt`, `StopReceipt`, `StopOutcome`, gate values and state vocabulary retain approved meanings. No approval-to-deployment or stop-acknowledgement-to-cessation collapse.
- Candidate source pin `129e0b3f15a3bd6af949ee47d76f6855c582ab73` and license blob `c004659349c7a1f6c55e5107b53a0766085e8d2e` copied, explicitly requiring live preflight verification.
- All implementation paths/signatures are explicitly **proposed**, not claimed to exist. `research/runner`/`research/evaluator` wire-field contracts reuse approved data flow; proposed corpus/report/test paths declare concrete artifacts without pretending a library/API is installed.
- CLI grammar, language, VM product and exact OS transport remain implementation choices inside approved boundaries; changes to trust/license/cost/permissions and provisioning require operator approval. No invented `pvg research` command.
- No source implementation existed to verify; greenfield contracts are approved design targets, not fabricated source signatures. Actual implementation mapping must be recorded on delivery.

## Adversarial per-story self-review

Each line covers reality/existence claims, nontrivial outcome, scope honesty, enumerated negative coverage and hard-rule compliance.

- **GRRR-0g4n — fixed:** Added explicit runner/evaluator and test ownership. Real isolated clean/faulty path, trusted verdict, receipt and report—not stubs. Minimum safety is required before executing; later stories extend attack/crash coverage rather than deferring safe basics. Wider file count is intentional for one walking vertical slice, not a production-readiness claim.
- **GRRR-90te — clean:** Concrete operator-blocked preflight outcome; pinned identity/licenses/offline rebuilds and actual ACL/network/share probes. No provision-without-consent or container fallback. Runtime and identity assumptions remain unproven until tested.
- **GRRR-gu87 — clean:** Observation-to-budget-to-dispatch outcome includes forgery, parser, supervisor, concurrent reservation and lost-response cases. No free inference, unknown cost as zero, or reservation-as-launch-lease loophole.
- **GRRR-my5n — clean:** Reviewer independently verifies restored snapshot. Hash-chain truncation detection is correctly relative to trusted anchor, not a claim against privileged host compromise. All storage boundaries have negative/crash cases.
- **GRRR-c875 — clean:** Hung-runner stop is independent, authenticated, durable and idempotent. Actual admission race tests explicitly land after admission exists; control-side tests do not pretend a stub registry is proof. Pending cancellation is not safe-stop success.
- **GRRR-bnkf — clean:** Independent corpus validation has category/spec/critical/negative coverage and frozen plan. Larger fixture count justified by >=20 required scenarios. Truth and public metadata separated; unsupported semantics stay ambiguous.
- **GRRR-z3w9 — clean:** Fresh trusted-input replay rejects claimant harnesses and ambiguous specs; no implicit admission. Failure streak policy requires approval and retains failed attempts.
- **GRRR-dbbi — fixed:** Added direct blocker/CONSUMES for GRRR-z3w9 and explicit per-arm replay receipts/costs before verified counts. Equal-budget/denominator/absence cases prevent optimistic scoring. Optional existing Jev endpoint is conditional on separate authorization; no new credential provisioning hidden in scope.
- **GRRR-34ve — clean:** Exact authorization, gate recheck, atomic/recoverable protected commit, both stop/admission orderings, recurrence rejection and versioned human-authorized reversal are enumerated. Evidence acceptance never grants registry or software authority.
- **GRRR-fmvp — clean:** Human-observable accessible surfaces reflect one snapshot, not their own verdicts. Full vocabulary, ordinary decision without JSON/source, actual review time and stale/pending outcomes included; dashboard is a genuine deferred surface.
- **GRRR-6sso — clean:** E2e-only, real-system user journey, all ten direct blockers. No mocks, skipped unavailable Jev or missing-gate green. Feature repair returns to responsible slice rather than capstone scope creep.

## Tooling incidents and bounded corrections

1. `pvg issues create --help` advertises `--type story`, but nd rejects that type. First attempt failed before child creation. Reported and stopped; dispatcher explicitly authorized removing the flag. Omission created provider-default `task` records. No semantics changed.
2. Initial `## Acceptance Criteria` conflicted with nd-managed headings. Attempting supported `pvg nd update --body-file` retained the old nested body. Reported and stopped. Dispatcher authorized supported `pvg nd edit` with deterministic EDITOR normalization. Frontmatter and nd-managed Acceptance Criteria/Design/Notes/History/Links/Comments tail were preserved; canonical authored body replaced only through that command. Count **12 before -> 12 after**, same IDs; per-child preservation evidence and counts saved. Final lint has zero advisories.

## Residual advisories / execution prerequisites

- RTM extracted zero tags; rely on the explicit manual coverage matrix above, not the superficial zero-uncovered count. D&F was not modified to insert tags.
- Conditional Jev use does not authorize account creation, new secret/env configuration or paid calls. If existing approved capability is unavailable, comparator is incomplete. New setup requires a separate explicitly approved blocking story; no external-integration label was used to imply configured capability.
- Full security, race, crash and accessibility proof is future work. These are executable backlog requirements, not passing tests. Some slices have >3 files because verified vertical trust-boundary behavior cannot be represented honestly as independent horizontal layers; stated budgets trigger PM scrutiny.
- Runtime choice, CLI grammar, operator identity/VM provisioning, numeric watchdog/grace/ack bounds, two-failure policy and corpus/accounting approval are explicit execution gates. Backlog approval is not blanket authorization for them.
- No global/Obsidian vault search or `pvg seed` was run, per bounded assignment. No remote is configured; no sync/push attempted.
- No explicit `git commit`, `git push` or source implementation was performed. `main` remains unborn. **nd-native mutation autosnapshots did create/update `refs/heads/nd/backlog`**, as the tracker contract specifies; observed final tracker ref at inspection: `0484717967289cea9098e95ea05ae40f9d20fed6`. This is not a source commit and is disclosed rather than claiming no Git object was written.

## Frozen D&F identities

- BUSINESS.md: `7d56b562c4b3c194e2ee76ccdd4be68aa22ff0f8b749bdefacbd03e868a5dd82`
- DESIGN.md: `97f0e36febd2ad4dce43cc2912db477735f82349d9d3f965d22216d6a566b252`
- ARCHITECTURE.md: `1625922ac97e9fde0f9b492d96b748485fc0697837632e6814bef78dd25d8f75`

All three match assigned hashes after authoring and normalization.

## Anchor Round 1 repair — 2026-10-19

**Finding accepted:** the prior GRRR-bnkf AC 5 required complete mandatory verification even though allegation replay and protected authorization/admission were downstream of corpus acceptance. This was a semantic dependency cycle not detected by the DAG linter. The earlier corpus self-review verdict is superseded by this correction; mechanical success was insufficient.

**General rule swept:** an upstream artifact may require trusted validation available from its own/upstream capabilities, but cannot require excluded downstream capabilities for acceptance. Preliminary observations, independently verified findings, admission and full-system proof must remain distinct. A future gate stays not-run and cannot grant its downstream authority; that does not force acceptance of an upstream fixture artifact to wait for the downstream system.

### Exact changes

- **GRRR-bnkf, USER INTENT:** proposed scenario coverage, rather than suggesting completed system detection.
- **GRRR-bnkf, OUT OF SCOPE:** corpus acceptance explicitly covers frozen trusted fixtures/preliminary validation only. Final complete-system detection proof is GRRR-6sso's responsibility; not-run downstream gates cannot authorize findings/admission.
- **GRRR-bnkf, Story Acceptance Criteria 1:** independently validated seeded ground truth is explicitly preliminary fixture validation via accepted executor/observation capabilities—not a Verified defect, independent allegation ReplayReceipt, admission or full-system proof.
- **GRRR-bnkf, Story Acceptance Criteria 5:** replace premature complete-suite threshold with real preliminary trusted fixture checks using accepted isolation/observation/budget/ledger/stop. Every included scenario still needs reproducible clean/faulty behavior and spec-backed ground truth; missing required fixture evidence and unresolved nondeterminism block corpus acceptance. Downstream gates remain not-run. Full 100% critical/>=90% other thresholds are deferred to the final capstone, not relaxed.
- **GRRR-bnkf, Story Acceptance Criteria 6:** label preliminary observations separately from later selector and mandatory-suite discoveries; no transferred discovery credit.
- **GRRR-6sso, Story Acceptance Criteria 2:** after all ten siblings are accepted, require complete mandatory-system proof including independent replay and authorization/admission capability, retaining 100% critical/>=90% remaining detection, zero unverified/failed-replay admissions, every mandatory gate and no missing-capability skip. Preliminary fixture observations cannot substitute for these receipts.

Only these two live story bodies changed through supported `pvg nd edit`; no ID, parent, labels, priority, status or dependency changed. Other nine child bodies and the epic body were verified byte-identical. Issue count remains 12. Metadata and managed history tail preserved by the deterministic editor. Evidence: `.tmp-sr_pm/round1-repair-checks.json`.

### Generalized all-child sweep

| Child | Semantic prerequisite result |
|---|---|
| GRRR-0g4n | Clear: root implements minimum real execution, isolation, bounded reservation/deadline and receipts itself; replay/review/admission remain not-run and no verified/admitted result is claimed. Full downstream attack/recovery matrices are not skeleton acceptance prerequisites. |
| GRRR-90te | Clear: verifies baseline/permission/preflight capabilities built here or in skeleton; no full comparison/replay/admission required. Numeric measured policy approval is an operator precondition, not a downstream story dependency. |
| GRRR-gu87 | Clear: implements trusted transport/budget reservations here; consumes existing executor/policy/ledger. Unknown observation/cost blocks work without demanding future corpus or replay. |
| GRRR-my5n | Clear: current append/snapshot crash proof does not require future registry commit protocol; admission-specific recovery remains downstream. |
| GRRR-c875 | Clear: actual control/dispatch fencing proved here; AC 6 explicitly reserves real admission races for admission and rejects stub-registry proof. Future admissions remain unavailable, not implicitly passed. |
| GRRR-bnkf | **Fixed:** fixture validation/freeze can now be accepted upstream without downstream replay/admission; complete-system thresholds are capstone-only proof. |
| GRRR-z3w9 | Clear: fresh allegation replay consumes accepted frozen fixture/spec artifacts and creates ReplayReceipt here. Admission remains unavailable; preventing inadmissible claims does not require proving future registry commits. |
| GRRR-dbbi | Clear: directly blocked by independent replay; per-arm verified counts require actual ReplayReceipt and costs. Contract admission is not a selector-comparison prerequisite. Optional live Jev authorization remains an explicit external precondition, never fabricated. |
| GRRR-34ve | Clear: implements authorization/admission now, depends transitively on control/ledger/replay, and owns actual stop/admission race proof. No polished review surface required for its minimal exact-target confirmation. |
| GRRR-fmvp | Clear: both comparison and admission are blockers; all required surface data/authority capabilities precede acceptance. |
| GRRR-6sso | **Clarified:** all ten direct blockers; complete-system detection and recurrence/admission proof happen only here after full capability delivery. No downstream capability exists beyond this gate. |

No other equivalent upstream/downstream acceptance inversion found in the 11-child sweep. Boundary signatures/paths and all dependency edges remain unchanged.

### Re-run evidence

- `pvg lint --backlog`: exit 0; **0 errors, 0 review findings**, 12 issues scanned.
- `pvg rtm check`: exit 0; still **0 tagged requirements extracted**, so the manual coverage matrix remains necessary.
- `pvg nd dep cycles`: exit 0; none.
- `pvg nd epic close-eligible`: exit 0; none, correctly while children are open.
- Dependency graph/tree/stale/stats: exit 0; 12 total/open, 10 blocked, no stale issues.
- Canonical-body/boundary/dependency verification: 11/11 passed, capstone still blocked by all ten siblings, all three D&F hashes unchanged.

No implementation, runtime experiment, explicit Git commit or push was performed. nd's normal native backlog autosnapshots may advance the tracker branch; no source commit was made. No new Anchor invocation by this worker.
