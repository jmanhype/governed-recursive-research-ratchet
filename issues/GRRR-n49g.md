---
id: GRRR-n49g
title: "Report: fail-closed recommendations and read-only status view"
status: in_progress
priority: 0
type: bug
parent: GRRR-2t3h
created_at: 2026-11-09T17:44:55Z
created_by: speed
updated_at: 2026-11-09T19:05:30Z
content_hash: "sha256:6c236513bc2b5f2650846f91bd080a44961b014edf922c380bea18083db1d50e"
assignee: dev-GRRR-n49g
follows: [GRRR-hbc6]
---

## Description
## USER INTENT
Fix the operator report's zero-gate admission recommendation and fabricated zero cost; build one pure, read-only, versioned status view shared by text/Markdown/JSON, with tests and independent review. Preserve every mandatory gate, independent authority, and approval boundary.

## SOURCE BASE AND SCOPE
Use accepted epic/GRRR-2t3h at 5f6ce4e83e2426e859127af568aa730c19dc6a9b, not unmerged story/GRRR-734u. That source checkpoint remains preserved at 4e09c6b; it is not a dependency or approved runtime. Parent audit: outputs/grrr-state-machine-audit-20261109/STATE-MACHINES.md.

The legacy replay admission inventory has exactly nine required gates (research/admission.py:GATE_INVENTORY); the newer capstone/common inventory has eleven. Do not conflate gate profiles, mutate admission/common, accept empty/all([]) as passing, or infer action-specific authority from either inventory or a finding string. This slice is an archived replay/report projection, not a live accounting or campaign monitor.

## PRODUCES / OWNERSHIP (7 functional files, stdlib only)
- research/status_view.py: typed pure read-only versioned status projection and explicit legacy-replay gate profile.
- research/review_report.py: build_report and text/Markdown/JSON share that projection, unknown costs and states stay unknown.
- scripts/grrr-review: expose status view using existing --format and a small --view review|status option; label the existing fixed evidence snapshot historical, not live. No new mutation commands.
- tests/unit_status_view.py: source-only positive/adversarial/purity tests, including real temporary evidence files and CLI journeys.
- tests/unit_review_report.py: preserve existing coverage; repair unsafe expectations, remove silent missing-fixture skips in favor of real self-contained fixtures.
- tests/unit_capstone_backend_suite.py: registration-only, require both report/status modules with nonzero skip-free counts.
- docs/READ-ONLY-STATUS-VIEW.md: API, version/compatibility, evidence scope and limits; no readiness/authority claims.

## CONSUMES
research/review_report.py: load_replay_data(Path)->dict, build_report(dict)->dict, to_plain_text(dict)->str, to_markdown(dict)->str, to_json(dict)->str; currently hardcodes cost0 and snapshot export, and recommends approval from finding alone. research/admission.py:GATE_INVENTORY/check_gates defines legacy nine required gates; READ ONLY, never call admission writers. Canonical/hash helpers may be reused where appropriate; hashes identify bytes, not trusted origin or live currency.

## ACCEPTANCE CRITERIA
1. Missing/empty/partial gates never yield an approval recommendation or Ready-for-action claim. Enumerate all nine required legacy gates; missing = not-run, failed/error/unknown stay blocking. Extra gates cannot mask missing required gates. Verified must be exact bool True plus exact Verified defect and all required gates pass before even eligibility for evidence review. Eligibility is not human approval or contract admission. Inconclusive/ambiguity/missing evidence requests more evidence, not automatic rejection or approval.
2. Missing/unknown/malformed/non-finite/negative/bool-as-number cost is never displayed as $0. JSON uses null and explicit knowledge/reason for unknown. Genuine explicit nonnegative finite zero/nonzero observations can be displayed with provenance/scope; reported cost is not settled spendability or verified accounting. Do not invent totals, currencies, usage, elapsed time or evidence identities. No false stale hardcoded snapshot identity for arbitrary data.
3. Pure typed versioned status separates execution, finding/verification, source review, human decision, action-specific authorization, installation, budget knowledge/cost, stop/cessation, admission and promotion. Unsupported/missing axes remain unknown/not-established or explicitly disabled; never fabricate live state from archive/source tests. Include stable reason_codes, next_action and next_owner plus evidence/scope markers. Projection grants NO authorities; no current/freshness assertion without independently established evidence. Return detached data, do not mutate caller input.
4. The existing report surface and new --view status use the SAME projection and consistent facts in text/Markdown/JSON. Clearly label historical/unverified evidence in every format including compact text. Keep existing public function signatures and vocabulary exports; version changed JSON explicitly. Full keyboard/plain text, no color reliance, readable approximately 80-column summary, technical detail optional. No raw JSON required for ordinary review.
5. Tests cover all gates absent, each missing/fail/error/not-run/malformed, extras, verified False/truthy wrong type, ambiguities, malformed data, unknown vs actual zero/nonzero cost, non-finite/bool/negative values, detached input/output, no I/O/network in pure projection, no implied approval/install/replay/promotion, and format/CLI consistency. Real temporary filesystem fixtures, no skipped tests or mocked-success I/O; syscall guards only for negative purity assertions. Required suite nonzero and skip-free on installed Python3.14/3.12/3.9. Preserve every preexisting mandatory backend suite module.
6. Retain independent read-only review verdict, exact file hashes, actual test logs/counts and source-only evidence. Do not self-accept. User authorized source work/review only, NOT a new source commit, delivery/acceptance, protected staging or runtime actions.

## FORBIDDEN
No /Library/GRRR access incl metadata, protected state, credentials/network/provider calls, VM/provisioning/install, reconciliation/accounting writes, actual replay, admission, promotion, production mutation, merge, push or new source commit. Do not alter admission.py/common.py/evaluator/ledger/budgets, benchmark inputs, acceptance gates or protected fixtures. No new dependency/framework, schema migration, default approvals, retry/reset or automatic cleanup. Preserve concurrent branches and files.

## nd_contract
status: new
### evidence
- Operator-authorized report/status source work only; no implementation or acceptance claimed.
### proof
- [ ] AC #1: Mandatory gate inventory and review eligibility fail closed.
- [ ] AC #2: Unknown cost never becomes fabricated zero; evidence scope explicit.
- [ ] AC #3: Pure typed detached versioned projection, separate axes and no authority.
- [ ] AC #4: One projection across three formats and CLI, accessible historical labels.
- [ ] AC #5: Real fixture/purity/adversarial tests, three Python suites, no skips.
- [ ] AC #6: Independent review and retained evidence, no prohibited effects/commit.

## Acceptance Criteria


## Design


## Notes
## Measured gate-profile clarification (operator's preserve-all-gates requirement)

The compatibility checker read selected fields of the actual archived ReplayReceipt: it contains common.GATES' full eleven records, with nine pass and reviewer_outcome/action_specific_human_approval not-run. admission.GATE_INVENTORY is only a nine-gate subset. The initial wording about displaying nine required legacy gates was ambiguous and could obscure those two records; it is superseded for presentation by this clarification.

Required report/status gate inventory: retain all eleven common.GATES, missing entries explicitly not-run; actual archived output must show 9/11, NOT a fully passed9/9. An optional admission-only9/9 subset is separately labeled and grants no approval. Evidence-inspection eligibility requires all eleven plus exact verified=True and Verified defect; source-code review is always separately not-established here. No mandatory gate or authority implementation is changed.

Source-only integration also removes the unrequested arbitrary --evidence CLI input, retaining only --view review|status with existing --format. CLI fixture tests create a real temporary app/evidence copy, not mocked I/O. Exact JSON-type checks prevent in-process equality/lookup hooks; control characters are not projected as labels/status. Parent verification and independent review of the final seven-file diff are pending. Initial worker338-test results apply only to its initial bytes, not the corrected final package.

## nd_contract
status: in_progress
### evidence
- Source patch exists; parent corrected full eleven-gate presentation and tested focused fixtures. Source WIP uncommitted, no runtime/protected effects.
### proof
- [ ] Final cross-version counts and independent review required before reporting review-approved source WIP.

## History
- 2026-11-09T17:45:04Z status: open -> in_progress
- 2026-11-09T17:45:04Z auto-follows: linked to predecessor GRRR-hbc6
- 2026-11-09T17:45:04Z claimed by dev-GRRR-n49g

## Links
- Parent: [[GRRR-2t3h]]
- Follows: [[GRRR-hbc6]]

## Comments

### 2026-11-09T17:48:00Z speed
Source kickoff selected by pvg loop next and atomically claimed; isolated pvg-owned story/GRRR-n49g worktree from accepted epic 5f6ce4e. CoS worker unavailable; exact GLM Coding Plan implementation worker assigned seven files; separate read-only compatibility check. Parent baseline307 required backend tests passed on Python3.14.3/3.12.9/3.9.6, zero failures/errors/skips under /Library/GRRR OS denial. New status/report implementation, independent review and final counts pending; no readiness/acceptance/runtime assertion.

### 2026-11-09T19:05:30Z speed
## Measured gate-profile clarification (operator's preserve-all-gates requirement)

The compatibility checker read selected fields of the actual archived ReplayReceipt: it contains common.GATES' full eleven records, with nine pass and reviewer_outcome/action_specific_human_approval not-run. admission.GATE_INVENTORY is only a nine-gate subset. The initial wording about displaying nine required legacy gates was ambiguous and could obscure those two records; it is superseded for presentation by this clarification.

Required report/status gate inventory: retain all eleven common.GATES, missing entries explicitly not-run; actual archived output must show 9/11, NOT a fully passed9/9. An optional admission-only9/9 subset is separately labeled and grants no approval. Evidence-inspection eligibility requires all eleven plus exact verified=True and Verified defect; source-code review is always separately not-established here. No mandatory gate or authority implementation is changed.

Source-only integration also removes the unrequested arbitrary --evidence CLI input, retaining only --view review|status with existing --format. CLI fixture tests create a real temporary app/evidence copy, not mocked I/O. Exact JSON-type checks prevent in-process equality/lookup hooks; control characters are not projected as labels/status. Parent verification and independent review of the final seven-file diff are pending. Initial worker338-test results apply only to its initial bytes, not the corrected final package.

## nd_contract
status: in_progress
### evidence
- Source patch exists; parent corrected full eleven-gate presentation and tested focused fixtures. Source WIP uncommitted, no runtime/protected effects.
### proof
- [ ] Final cross-version counts and independent review required before reporting review-approved source WIP.
