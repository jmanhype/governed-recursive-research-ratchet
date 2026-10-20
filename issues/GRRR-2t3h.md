---
id: GRRR-2t3h
title: "Milestone 1: Governed vlt research ratchet"
status: open
priority: 1
type: epic
labels: [milestone-1]
created_at: 2026-10-20T03:08:52Z
created_by: speed
updated_at: 2026-10-20T03:08:52Z
content_hash: "sha256:9caa9e388ece980cd6441fb8b653a1853abf1208d746690b15992814433d1a15"
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


## History


## Links


## Comments
