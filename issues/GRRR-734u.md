---
id: GRRR-734u
title: "Replay: fresh execution namespace planner (source-only)"
status: in_progress
priority: 2
type: feature
parent: GRRR-2t3h
created_at: 2026-11-08T18:07:59Z
created_by: speed
updated_at: 2026-11-09T15:14:42Z
content_hash: "sha256:6aaa703c06626a5f9706901303a6f66cd7c912fc7c463f11ba7ba660a106f2d3"
follows: [GRRR-hbc6, GRRR-q3hp]
assignee: dev-GRRR-734u
---

## Description
## USER INTENT

After merge `5f6ce4e` integrated accepted `GRRR-hbc6`, prepare—but do not issue—a distinct replay execution namespace. The source-only planner must bind all replay inputs to exact prior evidence and accounting while preserving every consumed-sequence and accounting invariant. The operator authorizes source work only.

## CONTEXT AND BINDINGS

- Predecessor `GRRR-hbc6` is accepted; source work at merge `5f6ce4e` had 307 tests pass on Python 3.14, 3.12, and 3.9.
- Existing `replay.py:440-442` rejects a consumed sequence by counting replay receipts. This guard must not be weakened, bypassed, or reset.
- `replay_runtime.py` identifies a Python runtime; it is not this execution namespace.
- Fixed predecessor execution target is `/Library/GRRR/independent-replay`, used only as provenance.
- Existing accounting v4 recovery receipt `8b7958e5be76f6b35c4bfafc1f17a2926badfdd813addbefd5d683e376e8eeeb` retains its unknowns and holds. No allowance or spendability may be created or inferred.

## PRODUCES / CONSUMES

**Produces (planned ownership, approximately 4 files and no more than 600 changed LOC):**

- `research/fresh_replay_runtime.py` — pure canonical versioned planner API and typed proposal result.
- `tests/unit_capstone_fresh_replay_runtime.py` — real temporary filesystem/SQLite integration coverage.
- `tests/unit_capstone_backend_suite.py` — registration-only change for the required backend runner.
- `docs/FRESH-REPLAY-RUNTIME-WIP.md` — source-only status and remaining authorization/provisioning gates.

**Consumes:**

- Caller-supplied archived or synthetic canonical source/input manifests, identity records, digests, prior evidence, and accounting receipt.
- Existing common canonical/digest helpers and approved isolation/authority policies.
- Predecessor target and accounting facts solely as immutable provenance bindings.

## OUT OF SCOPE

- No `/Library/GRRR` access, `stat`, `lstat`, `open`, provisioning, installation, VM action, replay, reconcile, promotion, admission, production action, commit, or push.
- No accounting creation, budget change, hold release, unknown zeroing, sequence reset, replay-state reset, ledger reset, or stale authorization inheritance.
- No runtime readiness claim: a valid source proposal is prepared, not issued or installed.

## ACCEPTANCE CRITERIA

1. The pure canonical versioned planner API validates an exact typed schema plus caller identities, digests, and immutable proposal hashes from archived/synthetic caller-supplied inputs. It never opens protected assets.
2. It proposes one distinct, non-reused execution namespace. The consumed predecessor is retained only as provenance. It rejects reused or consumed targets, pending/stopped/unknown target state, and invalid candidate roots. It never deletes or resets previous `replay_state`, sequence, or ledger state.
3. Every proposal binds the exact source, inputs, VM/policy, prior evidence, predecessor identity, and existing accounting v4 identity/recovery receipt `8b7958e5be76f6b35c4bfafc1f17a2926badfdd813addbefd5d683e376e8eeeb`. It creates no accounting entry, changes no budget, releases no holds, zeroes no unknowns, infers no spendability, and inherits no stale authorization.
4. Output is explicitly `prepared_not_issued`; review, installation, replay, promotion, and admission authorization are false; every mandatory live gate is recorded not-run; and no runtime readiness is asserted.
5. Invalid requests are rejected lexically before protected metadata is consulted, with no `/Library/GRRR` `stat`/`lstat`/`open`. Real temporary filesystem/SQLite fixtures cover collision/reuse, pending/stopped state, stale hash or identity, symlink/escape, and missing evidence, and prove preservation of old evidence/accounting. A valid new-target fixture can produce a nonauthorizing proposal even when the predecessor was consumed.
6. Filesystem/SQLite integration tests use real fixtures rather than mocks, contain no skips, and forbid a zero-test green run. Register the new tests in the required backend runner and run them on the three installed Pythons (3.14, 3.12, 3.9). The source-only artifact is not live execution proof.
7. Documentation records the remaining exact-parent review and provisioning gates and explicitly states that no root, VM, replay, promotion, admission, production, commit, or push action was performed.

## nd_contract

status: new

### evidence

- Create-only story from the operator brief; no implementation, claim, dispatch, test execution, protected access, commit, or push has occurred.
- Fresh `pvg loop next --json` before creation reported `Ready: 0` and `InProgress: 0`.

### proof

- [ ] AC #1: Exact typed canonical-input and immutable proposal-hash validation, with protected assets never opened.
- [ ] AC #2: Distinct namespace proposed while reused/consumed/invalid targets are rejected and prior replay state is preserved.
- [ ] AC #3: Exact replay and accounting identities bound with no accounting or authorization mutation.
- [ ] AC #4: Proposal is explicitly prepared-not-issued with all authorizations false and live gates not-run.
- [ ] AC #5: Lexical fail-closed behavior and preservation properties proven by real filesystem/SQLite fixtures.
- [ ] AC #6: Mock-free, skip-free nonzero tests pass through the required backend runner on Python 3.14, 3.12, and 3.9.
- [ ] AC #7: Remaining review/provisioning gates and source-only limits documented.

## Acceptance Criteria


## Design


## Notes
Implementation kickoff: selected by fresh pvg loop next developer_new action and atomically claimed by dev-GRRR-734u. Retained worktree .claude/worktrees/dev-GRRR-734u on story/GRRR-734u from authorized merge 5f6ce4e83e2426e859127af568aa730c19dc6a9b. Worker /root/dev_grrr_734u dispatched via exact zai-coding/glm-5.3; no delegation permitted. CoS native dispatch connection failed; initial broad framing turn was bounded/interrupted without a created issue, then create-only Sr-PM produced this story. Source-only WIP: four assigned functional files, no commits/delivery/acceptance, no protected access or provision/reconcile/replay/promote/admit/production/merge/push. Existing accounting authority and consumed predecessor evidence must be preserved. Source test results not yet claimed.
Bounded worker replacement: GLM first source pass was interrupted after no source artifacts or commits appeared; no throttle/outage verdict is inferred. Worktree and branch reverified clean at 5f6ce4e. Canonical pvg worktree remove refused a missing ownership marker (the parent had used git worktree add); no force/marker/tooling override was attempted, and the clean checkout is preserved. Escalated exactly the protected-path/authority-sensitive four-file source WIP to fresh Astra task /root/grrr734u_security_wip, with no orchestration or delegation, no commit or protected effects. Existing tested OS denial profile is required for fixture/backend runs. Source results still pending; no approval/readiness claimed.
## Authorized independent source review and bounded rework

Operator authorization: independently review GRRR-734u, fix findings, then commit approved source WIP. No provisioning, reconciliation, replay, promotion, admission, production mutation, merge or push. This later authorization permits a reviewed local source-WIP commit; it does not issue runtime authority.

Live base remains 5f6ce4e83e2426e859127af568aa730c19dc6a9b. All four source-WIP hashes matched the retained checkpoint. Fresh baseline backend tests: 319 on each Python 3.14.3, 3.12.9 and 3.9.6; zero failures/errors/skips under process-local /Library/GRRR read/write denial.

Independent security review R1 rejected F1: string-subclass equality could bypass external expected-request and fixture digest comparisons. Report docs/evidence/fresh-replay-runtime/r1-review.md SHA256 575a0889134228046d091c4d654cefa9c28cad710a119155a719bf19c226ced5 retained. Exact GLM Coding Plan worker assigned minimal boundary validation/regressions and documentation lifecycle wording; new independent review is required before commit. CoS native worker path was unavailable.

Canonical pvg loop recover preserved dirty GRRR-734u as a foreign worktree, but cleaned two already-merged orphan checkouts (hbc6/q3hp). Their exact accepted branch tips and clean checkouts were restored using canonical pvg worktree add; no code/evidence was lost, no forced cleanup or invented marker. The loop's stalled advisory is a parked-WIP scheduling observation, not a source-test failure or permission for live actions.

The operator additionally requested an app-wide implicit-state-machine audit. It is a separate read-only source audit, not authorization for state migration or broad production refactoring. Results are being retained outside the source WIP at outputs/grrr-state-machine-audit-20261109.

## nd_contract
status: in_progress

### evidence
- R1 REVIEW_RESULT: REJECTED; minimal source rework and a new independent review pending.
- No source-WIP commit, delivery, PM acceptance, protected access or live action asserted at this checkpoint.

### proof
- [ ] Source-WIP commit: only after independent approval of corrected exact bytes and fresh required suites.
- [ ] Story acceptance and any protected runtime provisioning: not performed.

## Source WIP checkpoint — GRRR-734u

Parent verified the requested kickoff progressed beyond framing. The exact four scoped files exist in `.claude/worktrees/dev-GRRR-734u` on `story/GRRR-734u`, base commit `5f6ce4e83e2426e859127af568aa730c19dc6a9b`. No new commit, delivery, acceptance, or merge of this WIP.

### Implemented source, not runtime proof
- Pure versioned canonical `prepare`/`validate_proposal` API with a frozen byte/hash proposal and detached record copies.
- Exact source/input/VM/policy/prior-evidence/predecessor/accounting identity bindings; v4 recovery reference pinned. Caller-provided archival hashes are not authentication or proof of live currency.
- Distinct opaque future namespace; consumed predecessor retained as provenance. Existing/reused/consumed/pending/stopped/unknown target cases refuse. No old ledger, sequence, accounting store or allowance is created/reset/changed.
- All five authorization flags false, all eleven common mandatory live gates not-run, status prepared_not_issued, runtime readiness not_asserted.
- Explicit temporary-fixture preflight validates all filesystem-bound paths lexically before metadata and uses descriptor-relative no-follow reads. It does not probe the generated protected target and assumes caller-owned quiescent fixtures, not hostile concurrent renames.
- Twelve focused real filesystem/SQLite regressions, including preservation of prior bytes/inodes and zero protected metadata attempt guards. Public production functions now have type annotations.
- Documentation: docs/FRESH-REPLAY-RUNTIME-WIP.md states uncommitted/unapproved/unprovisioned and lists remaining exact-parent review/provisioning gates.

### Exact WIP hashes
- research/fresh_replay_runtime.py: 04e6dd9922de9e136dd0ad1b46ee114168c9fb509dd66df36a8711343f84eb55
- tests/unit_capstone_fresh_replay_runtime.py: de3616752ab0d19e4d4888ba73b9e00c758140c5dc18f6fb913640e115455da5
- tests/unit_capstone_backend_suite.py (registration only): 07e3d0521cdd631c9111da63a054fac579cb90f05da3e6f24c6af6d07bb1f6f4
- docs/FRESH-REPLAY-RUNTIME-WIP.md: bfd60c10cf14376d0d918901deecc0dbc42b185bb5535cebcb9634448eb85cf7
- Functional scope: four files, 471 insertions/1 deletion including new additions; under the 600-LOC budget. No other repo changes observed.

### Parent-measured source verification
Commands: `/usr/bin/sandbox-exec -p '(version 1)(allow default)(deny file-read* file-write* (subpath "/Library/GRRR"))' <python> -B tests/unit_capstone_backend_suite.py`, once per installed interpreter. Parent checked source SHA256 before and after each run.
- Python3.14.3: 319 tests, zero failures/errors/skips. /private/tmp/grrr-734u-parent-Python-3.14.3.log SHA256 134eaebfb1384bb4d990761adeb6577a4748d7b8411145317c7933ca088f1876.
- Python3.12.9: 319 tests, zero failures/errors/skips. /private/tmp/grrr-734u-parent-Python-3.12.9.log SHA256 53d63c6cb38d6d7246a04481b4f7b8159c14a9b48df62e9689382445f2565b40.
- Python3.9.6: 319 tests, zero failures/errors/skips. /private/tmp/grrr-734u-parent-Python-3.9.6.log SHA256 f9cd95b619d5692c8fed39dd09251bfc9d0735368d35b59baa333a24d3873734.
- Worker focused suites: 12 tests passed per interpreter under the same denial profile. Parent verified raw artifacts, source diff, public type hints, and git diff --check; no independent reviewer approval is asserted.

### Routing and lifecycle
CoS native dispatch was unavailable. Initial GLM coding pass produced no artifacts within its bounded window and was interrupted; no provider throttle/outage is inferred. The protected-path/authority-sensitive implementation was escalated once to fresh Astra, then a tiny GLM signature-only pass. All those child tasks are stopped; parent verification processes completed.
Canonical worktree cleanup refused a missing ownership marker because this checkout was originally created by git worktree add. The safety refusal was respected: no force removal or marker fabrication. The dirty WIP is deliberately preserved, not discarded or presented as committed.

## nd_contract
status: in_progress

### evidence
- Authorized hbc6 merge 5f6ce4e is committed on epic/GRRR-2t3h and freshly verified 307 tests on all three interpreters.
- GRRR-734u source-only WIP exists with hashes above and parent-measured 319-test results on all three interpreters under protected-path OS denial.
- No protected access/provisioning, reconciliation, VM/replay execution, promotion, admission, production mutation, new source commit, WIP merge, or push.

### proof
- [x] Kickoff: authoritative queue selection, atomic claim, isolated story worktree, implemented source WIP and measured fixture tests.
- [ ] AC #1-7: Independent review and canonical delivery/PM acceptance remain pending; source tests are not acceptance or live capstone evidence.
- [ ] Any protected provisioning or replay: not authorized or performed by this source-only checkpoint.

## nd_contract
status: in_progress

### evidence
- Authoritative queue selected developer_new GRRR-734u; canonical atomic claim verified in_progress / dev-GRRR-734u under GRRR-2t3h.
- Story worktree .claude/worktrees/dev-GRRR-734u on story/GRRR-734u from merge 5f6ce4e83e2426e859127af568aa730c19dc6a9b. Epic remains on the authorized merge; no source changes on epic.
- Developer /root/dev_grrr_734u dispatched for the exact four-file source-only WIP. CoS unavailable; exact GLM Coding Plan fallback. No source/test completion claimed yet.
- Accepted hbc6 merge freshly passed 307 required backend tests on each installed Python3.14/3.12/3.9, zero failures/errors/skips. These are baseline results, not results for new code.
- Optional process-local protected-path denial profile syntax accepted by /usr/bin/sandbox-exec running /usr/bin/true; no protected path was probed. This is not proof that a new planner passes containment.
- No protected access/provisioning, reconciliation, VM/replay execution, admission, promotion, production mutation, new source commit, merge of this new story, or push.

### proof
- [ ] AC #1: Exact typed canonical candidate API and hash bindings.
- [ ] AC #2: Fresh target validation and predecessor preservation.
- [ ] AC #3: Existing accounting authority only; no new allowance.
- [ ] AC #4: Prepared-not-issued output and false authorizations.
- [ ] AC #5: Real filesystem/SQLite fixtures plus zero protected metadata guards.
- [ ] AC #6: New tests and required suite measured on three interpreters.
- [ ] AC #7: Honest source-only documentation and remaining protected gates.

## History
- 2026-11-08T18:08:44Z status: open -> in_progress
- 2026-11-08T18:08:44Z auto-follows: linked to predecessor GRRR-q3hp
- 2026-11-08T18:08:44Z claimed by dev-GRRR-734u

## Links
- Parent: [[GRRR-2t3h]]
- Follows: [[GRRR-hbc6]], [[GRRR-q3hp]]

## Comments

### 2026-11-08T18:26:48Z speed
## Source WIP checkpoint — GRRR-734u

Parent verified the requested kickoff progressed beyond framing. The exact four scoped files exist in `.claude/worktrees/dev-GRRR-734u` on `story/GRRR-734u`, base commit `5f6ce4e83e2426e859127af568aa730c19dc6a9b`. No new commit, delivery, acceptance, or merge of this WIP.

### Implemented source, not runtime proof
- Pure versioned canonical `prepare`/`validate_proposal` API with a frozen byte/hash proposal and detached record copies.
- Exact source/input/VM/policy/prior-evidence/predecessor/accounting identity bindings; v4 recovery reference pinned. Caller-provided archival hashes are not authentication or proof of live currency.
- Distinct opaque future namespace; consumed predecessor retained as provenance. Existing/reused/consumed/pending/stopped/unknown target cases refuse. No old ledger, sequence, accounting store or allowance is created/reset/changed.
- All five authorization flags false, all eleven common mandatory live gates not-run, status prepared_not_issued, runtime readiness not_asserted.
- Explicit temporary-fixture preflight validates all filesystem-bound paths lexically before metadata and uses descriptor-relative no-follow reads. It does not probe the generated protected target and assumes caller-owned quiescent fixtures, not hostile concurrent renames.
- Twelve focused real filesystem/SQLite regressions, including preservation of prior bytes/inodes and zero protected metadata attempt guards. Public production functions now have type annotations.
- Documentation: docs/FRESH-REPLAY-RUNTIME-WIP.md states uncommitted/unapproved/unprovisioned and lists remaining exact-parent review/provisioning gates.

### Exact WIP hashes
- research/fresh_replay_runtime.py: 04e6dd9922de9e136dd0ad1b46ee114168c9fb509dd66df36a8711343f84eb55
- tests/unit_capstone_fresh_replay_runtime.py: de3616752ab0d19e4d4888ba73b9e00c758140c5dc18f6fb913640e115455da5
- tests/unit_capstone_backend_suite.py (registration only): 07e3d0521cdd631c9111da63a054fac579cb90f05da3e6f24c6af6d07bb1f6f4
- docs/FRESH-REPLAY-RUNTIME-WIP.md: bfd60c10cf14376d0d918901deecc0dbc42b185bb5535cebcb9634448eb85cf7
- Functional scope: four files, 471 insertions/1 deletion including new additions; under the 600-LOC budget. No other repo changes observed.

### Parent-measured source verification
Commands: `/usr/bin/sandbox-exec -p '(version 1)(allow default)(deny file-read* file-write* (subpath "/Library/GRRR"))' <python> -B tests/unit_capstone_backend_suite.py`, once per installed interpreter. Parent checked source SHA256 before and after each run.
- Python3.14.3: 319 tests, zero failures/errors/skips. /private/tmp/grrr-734u-parent-Python-3.14.3.log SHA256 134eaebfb1384bb4d990761adeb6577a4748d7b8411145317c7933ca088f1876.
- Python3.12.9: 319 tests, zero failures/errors/skips. /private/tmp/grrr-734u-parent-Python-3.12.9.log SHA256 53d63c6cb38d6d7246a04481b4f7b8159c14a9b48df62e9689382445f2565b40.
- Python3.9.6: 319 tests, zero failures/errors/skips. /private/tmp/grrr-734u-parent-Python-3.9.6.log SHA256 f9cd95b619d5692c8fed39dd09251bfc9d0735368d35b59baa333a24d3873734.
- Worker focused suites: 12 tests passed per interpreter under the same denial profile. Parent verified raw artifacts, source diff, public type hints, and git diff --check; no independent reviewer approval is asserted.

### Routing and lifecycle
CoS native dispatch was unavailable. Initial GLM coding pass produced no artifacts within its bounded window and was interrupted; no provider throttle/outage is inferred. The protected-path/authority-sensitive implementation was escalated once to fresh Astra, then a tiny GLM signature-only pass. All those child tasks are stopped; parent verification processes completed.
Canonical worktree cleanup refused a missing ownership marker because this checkout was originally created by git worktree add. The safety refusal was respected: no force removal or marker fabrication. The dirty WIP is deliberately preserved, not discarded or presented as committed.

## nd_contract
status: in_progress

### evidence
- Authorized hbc6 merge 5f6ce4e is committed on epic/GRRR-2t3h and freshly verified 307 tests on all three interpreters.
- GRRR-734u source-only WIP exists with hashes above and parent-measured 319-test results on all three interpreters under protected-path OS denial.
- No protected access/provisioning, reconciliation, VM/replay execution, promotion, admission, production mutation, new source commit, WIP merge, or push.

### proof
- [x] Kickoff: authoritative queue selection, atomic claim, isolated story worktree, implemented source WIP and measured fixture tests.
- [ ] AC #1-7: Independent review and canonical delivery/PM acceptance remain pending; source tests are not acceptance or live capstone evidence.
- [ ] Any protected provisioning or replay: not authorized or performed by this source-only checkpoint.
