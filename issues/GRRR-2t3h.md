---
id: GRRR-2t3h
title: "Milestone 1: Governed vlt research ratchet"
status: open
priority: 1
type: epic
labels: [milestone-1]
created_at: 2026-10-20T03:08:52Z
created_by: speed
updated_at: 2026-10-20T03:28:13Z
content_hash: "sha256:43e6f45eeea8e96f520c72c5a5832f33ae1e78103b3c4699e19d27aafd52ce51"
---

## Description
## Context (Embedded)
- Authorized first milestone for the Governed Recursive Research Ratchet.
- Target subsystem: PAIVOT `vlt` indexing at proposed pinned commit `129e0b3f15a3bd6af949ee47d76f6855c582ab73`.
- Operator authorization dated 2026-10-19 approves the frozen BUSINESS.md, DESIGN.md, ARCHITECTURE.md and the twelve testable architectural acceptance criteria.
- Goal: prove governed isolation, trusted evidence, replay, human admission, equal-budget comparison, stop/recovery, and CLI/Markdown/JSON parity without implementation promotion.

## Milestone Boundary
- Evaluate frozen seeded variants and selector strategies; do not generate patches.
- Keep proposer, evaluator, promotion authority and operator authorization separate.
- Use a disposable offline local VM and an evaluator-owned local ledger.
- Enforce POC/milestone budgets and every BUSINESS.md hard-stop condition.
- Keep nd receipt references subordinate to the evaluator evidence ledger.

## Explicit Non-Goals
- No autonomous patch generation.
- No harness adaptation.
- No pvg/vlt/nd internals changes.
- No production access or mutation.
- No automatic merge to `main`.
- No unapproved paid calls.

## MANDATORY SKILLS
- sr_pm — author and repair the milestone backlog.
- developer — implement exactly one contained child story.
- pm_acceptor — independently verify delivered evidence and proof.

## nd_contract
status: new

### evidence
- Created: 2026-10-19
- Approved basis hashes: BUSINESS 7d56b562c4b3c194e2ee76ccdd4be68aa22ff0f8b749bdefacbd03e868a5dd82; DESIGN 97f0e36febd2ad4dce43cc2912db477735f82349d9d3f965d22216d6a566b252; ARCHITECTURE 1625922ac97e9fde0f9b492d96b748485fc0697837632e6814bef78dd25d8f75

### proof
- [ ] Pending child delivery and independent acceptance.

## Acceptance Criteria


## Design


## Notes
## ANCHOR REVIEW (backlog_review)
REVIEW_RESULT: APPROVED

Round 2 of 3. Reviewed GRRR-2t3h and all 11 children. Approval is for backlog quality only, not implementation completion, runtime feasibility or authorization of provisioning, experiments, paid calls, commits/pushes or promotion.

### Gaps
None blocking. Round 1's critical semantic dependency is resolved and the rule was generalized across the backlog.

### Summary
- GRRR-bnkf now accepts only independently validated frozen fixture artifacts and preliminary observations using accepted upstream execution/observation capabilities. Its intent, scope and ACs 1, 5 and 6 consistently distinguish these from verified findings, ReplayReceipts, admission and full-system proof. Missing downstream gates remain not-run and confer no authority.
- GRRR-6sso AC 2 explicitly owns complete-system 100% critical / >=90% other-seed detection after all ten siblings are accepted. Preliminary corpus observations cannot substitute; no final gate or threshold is weakened.
- Re-swept the other nine children: root minimum safety remains substantive; stop story explicitly defers actual admission races; replay is upstream of comparison; admission owns its true registry/stop races; surfaces consume both completed paths. No equivalent acceptance inversion or new critical/major issue found.
- All twelve approved architectural ACs retain substantive story/capstone coverage. Real integration evidence, separate authenticated authority, conservative costs, durable stop/admission ordering, recovery truth, accessible surface parity and no-mock capstone remain required.
- All capabilities remain proposed. Unavailable live Jev still blocks complete comparison/capstone acceptance rather than producing a substitute or skipped green result. Empty RTM tag extraction is not treated as coverage proof.

### Evidence
- First command: `pvg lint --backlog`: 12 issues scanned; PASSED, 0 errors, 0 review findings.
- `pvg nd show GRRR-bnkf` and `pvg nd show GRRR-6sso`: full repaired bodies inspected; remaining nine child AC sets re-read through `pvg nd show`; epic inspected through `pvg issues show`.
- `pvg nd dep cycles`: No dependency cycles found.
- `shasum -a 256 docs/BUSINESS.md docs/DESIGN.md docs/ARCHITECTURE.md BACKLOG-REVIEW.md`: accepted D&F hashes unchanged; updated report is de28985b2a1fa1966d2d60b87ba85f238714cac60be50c16d5b74e21a6edd32f.
- Updated Sr PM repair/generalization report read and checked against live story criteria, not accepted on narration alone.
- No story body/status edits, implementation, runtime tests, upstream clone, explicit source commit or push performed by this review.

## ANCHOR REVIEW (backlog_review)
REVIEW_RESULT: REJECTED

Round 1 of 3. Scope: GRRR-2t3h and all 11 children. Backlog review only; no implementation or runtime proof claimed.

### Gaps
1. **Critical — downstream capability required for upstream acceptance.**
   ISSUE: GRRR-bnkf AC 5 requires the complete mandatory verification suite and says a missing gate blocks acceptance, while its embedded inventory includes independent replay and action-specific approval. Its OUT OF SCOPE explicitly assigns independent allegation replay and contract admission to later slices. GRRR-z3w9 (the replay producer) is blocked by GRRR-bnkf, and GRRR-34ve (authorization/admission) follows GRRR-z3w9. The corpus developer therefore cannot meet the literal complete-suite acceptance condition without implementing downstream scope or treating missing gates as passing. GRRR-6sso AC 2 already owns the full-system threshold proof at the correct late boundary.
   RULE: Each story must be acceptable using its own authorized scope and already-available upstream capabilities. A partial slice must explicitly distinguish preliminary checks from complete mandatory-system proof; it must not require a downstream capability that it blocks, or relax final mandatory gates to escape that dependency.
   SCOPE: Swept all 11 children and epic for semantic availability versus declared scope. Repair GRRR-bnkf AC 5 and its coverage claims; sweep all 11 children for equivalent early full-suite claims. GRRR-c875 already explicitly defers actual admission races to GRRR-34ve, which is the correct pattern.
   Impact: Execution-breaking semantic dependency despite a mechanically acyclic graph.
   Fix: Keep independent corpus validation, representativeness and frozen ground truth in GRRR-bnkf. Explicitly label its available-path detection checks preliminary and leave downstream gates not-run/blocked without requiring their implementation to accept the corpus artifact. Retain the unchanged 100% critical / >=90% other complete-system threshold as mandatory downstream proof in GRRR-6sso (or another correctly ordered owner). Alternatively restructure dependencies and scope without introducing a cycle or weakening final criteria.

### Summary
- All twelve approved architecture ACs have named story coverage, but AC 7's early complete-suite claim has the scope/order conflict above.
- Walking skeleton contains a real isolated path, trusted assertions, bounded authority, retained evidence and substantive quality-gate tests; unavailable replay/admission remains explicitly blocked there.
- Stop fencing, authenticated direct control, admission linearization, conservative budgets, replay/spec provenance and truthful recovery are represented with concrete negative cases.
- Capstone covers the full operator journey, all ten siblings, genuine three-arm comparison, accessible surfaces and AC 1-12 evidence. Unavailable Jev correctly prevents full comparative/capstone success.
- Proposed files/APIs are honestly labeled greenfield contracts. Approval does not imply provisioning, paid-use, experiment, commit/push or promotion authorization.
- No additional missing story type identified. No fabricated implementation evidence accepted.

### Evidence
- First command: `pvg lint --backlog`: 12 issues scanned; PASSED, 0 errors, 0 review findings.
- `pvg nd show` for GRRR-2t3h and all 11 child IDs; `pvg issues show GRRR-2t3h --json` for canonical body.
- `shasum -a 256 docs/BUSINESS.md docs/DESIGN.md docs/ARCHITECTURE.md BACKLOG-REVIEW.md`: all four match dispatcher-provided accepted hashes.
- Read accepted D&F documents and manual 12-AC mapping; empty RTM extraction is not semantic coverage proof.
- Three prescribed `pvg notes search` pattern/convention queries returned no results.
- `git log --oneline -3`: unborn main, no commits. `docs/findings` is absent. No runtime experiments, upstream clone, implementation, commit or push performed.

## History


## Links


## Comments
