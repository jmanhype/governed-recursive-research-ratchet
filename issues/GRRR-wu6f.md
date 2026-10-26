---
id: GRRR-wu6f
title: "Validate spendability evidence fail-closed"
status: in_progress
priority: 1
type: task
parent: GRRR-2t3h
created_at: 2026-10-26T02:20:26Z
created_by: speed
updated_at: 2026-10-26T02:26:11Z
content_hash: "sha256:655363bb64b49436e48af90db21bdc2ac1e069024411b609b5f34a80621caccf"
labels: [milestone-1, integration, spendability-validator]
blocks: [GRRR-z3w9]
assignee: dev-GRRR-wu6f
follows: [GRRR-d8ji]
---

## Description
## USER INTENT
Determine exactly why spendability remains `null` before any reconciliation authority is granted.

## Context (Embedded)
- Approved spendability reconciliation evidence contract: `story/GRRR-z3w9` commit `820469226032761ca1335fe58ef674a3219e8d07`, `docs/SPENDABILITY-RECONCILIATION-EVIDENCE-CONTRACT.md`, SHA256 `c179b6c9640a5d848f70bb9b7e6ac3833223a6c55ddf9bfa0b2dbe68a6c82b37`, `CONTRACT_REVIEW: APPROVED`.
- The contract contains 28 contiguous adversarial cases. This story validates packages against that approved schema and explains the first failed gate; it does not grant reconciliation authority.
- Validation is pure and in-memory, using synthetic packages only.

## Scope
- Implement `validate_evidence(package: Mapping[str, object]) -> ValidationResult`.
- Implement exactly the 28 contract adversarial cases as focused unit tests.
- Cover canonical JSON, exact schema/joins/uniqueness, bounded integer arithmetic, baseline/ancestry identity, provenance, pending full-maximum holds, POC-in-milestone, one-time/stale resistance, field-level nullability, unresolved `spendability=null`, and first failed gate.

## OUT OF SCOPE
- `/Library/GRRR` access: no protected-state authority is granted by this story.
- Reconciliation decision or execution: remains downstream after validated evidence and explicit authorization.
- Replay, VM, QEMU, and UID/GID work: unrelated protected execution surfaces.
- Staging or installation: no protected or machine mutation is authorized.
- Promotion, admission, or production mutation: remains governed by later gates.
- Merge, push, cache cleanup, and full-suite execution: this is a pure focused unit slice.

## DIFF BUDGET
- ~3-5 files, under 1000 LOC.

## Boundary Map
PRODUCES:
- `research/spendability_evidence.py` -> `validate_evidence(package: Mapping[str, object]) -> ValidationResult`
- `tests/unit_spendability_evidence.py` -> exactly the 28 approved contract adversarial cases

CONSUMES:
- GRRR-z3w9: `docs/SPENDABILITY-RECONCILIATION-EVIDENCE-CONTRACT.md` -> schema/source for `validate_evidence(package: Mapping[str, object]) -> ValidationResult` and its 28 adversarial cases; approved at commit `820469226032761ca1335fe58ef674a3219e8d07`, SHA256 `c179b6c9640a5d848f70bb9b7e6ac3833223a6c55ddf9bfa0b2dbe68a6c82b37`.

## Acceptance Criteria
1. All 28 contract adversarial cases map 1:1 to focused unit tests and pass on both `/usr/bin/python3` and `/opt/homebrew/bin/python3`.
2. A current-like incomplete synthetic package returns `spendable=null` and retains pending maxima rather than coercing unresolved data to a spendable decision.
3. Validation has no protected access, reconciliation authority, staging, production mutation, or external side effect.
4. Explicit-path compile/static `pvg verify` checks and diff checks pass; full-suite and protected integration execution remain out of scope.

## Testing Requirements
- Unit: focused `tests/unit_spendability_evidence.py`, exactly the 28 contract adversarial cases, using only in-memory synthetic packages.
- Run that focused test file with both `/usr/bin/python3` and `/opt/homebrew/bin/python3`.
- Run explicit-path compile/static `pvg verify` and diff checks.
- Full suite and protected integration are out of scope.

## MANDATORY SKILLS
- developer
- pvg
- nd
- codebase-memory or direct-source fallback

## Delivery Requirements
- Developer must paste focused test, compile/static, and diff-check output into notes.
- Developer must include an AC verification table.
- Developer must update `nd_contract` to delivered and add label delivered.

## nd_contract
status: new

### evidence
- Created: 2026-10-25

### proof
- [ ] Pending implementation


## Acceptance Criteria


## Design


## Notes
## nd_contract
status: in_progress

### evidence
- Claim verified: dev-GRRR-wu6f; implementation started from 820469226032761ca1335fe58ef674a3219e8d07.

### proof
- [ ] Pending focused implementation and verification

## History
- 2026-10-26T02:20:59Z dep_added: blocks GRRR-z3w9
- 2026-10-26T02:22:25Z status: open -> in_progress
- 2026-10-26T02:22:25Z auto-follows: linked to predecessor GRRR-d8ji
- 2026-10-26T02:22:25Z claimed by dev-GRRR-wu6f

## Links
- Parent: [[GRRR-2t3h]]
- Blocks: [[GRRR-z3w9]]
- Follows: [[GRRR-d8ji]]

## Comments
