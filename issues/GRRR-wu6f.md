---
id: GRRR-wu6f
title: "Validate spendability evidence fail-closed"
status: open
priority: 1
type: task
parent: GRRR-2t3h
created_at: 2026-10-26T02:20:26Z
created_by: speed
updated_at: 2026-10-26T03:15:30Z
content_hash: "sha256:d01cca853d3c7119ed23bbd7baf8db584033bac103dcad356366d87b82c2e2e3"
labels: [milestone-1, integration, spendability-validator, delivered]
blocks: [GRRR-z3w9]
follows: [GRRR-d8ji, GRRR-43i8]
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
Implementation SHA: 2522a8ea95068527bba8db85180c4b38c239a1a0

## Implementation Evidence

Commands run:
- `/usr/bin/python3 -B -m unittest discover -s tests -p 'unit_spendability_evidence.py'` — Ran 28 tests, OK, exit 0.
- `/opt/homebrew/bin/python3 -B -m unittest discover -s tests -p 'unit_spendability_evidence.py'` — Ran 28 tests, OK, exit 0.
- Both required interpreters compiled the two changed files with bytecode confined under `/tmp` — exit 0.
- `pvg verify research/spendability_evidence.py tests/unit_spendability_evidence.py --include-tests --format=text` — VERIFY: PASSED (2 files scanned, 0 issues).
- `git diff --check`, `git diff --cached --check`, and range diff check — PASS.
- Static forbidden API/path scan — PASS; exactly 28 contiguous test-case methods.

Summary:
Implementation SHA: `2522a8ea95068527bba8db85180c4b38c239a1a0`
Parent: `820469226032761ca1335fe58ef674a3219e8d07`
Implementation file SHA256: `50f18fd77137d0a0519527ce631f4fac7012197fa96aefed2947a0293601d5f7`
Test file SHA256: `baa2923927d8a65cb71b5e7dc28cc8ccd12df9d8354323e2e26c97e159280e21`
Exactly two files changed, 996 inserted LOC. Both interpreters passed all 28 focused adversarial tests with no skips. The validator is pure/in-memory, returns `spendable=null` for incomplete evidence, retains pending maxima, and exposes no mutation or execution authority. No `/Library/GRRR` access, reconciliation execution, replay, VM/QEMU action, promotion, admission, production mutation, merge, or push occurred.

## nd_contract
status: delivered

### evidence
- Transitioned via pvg story deliver on 2026-10-25.

### proof
- [ ] Developer evidence block must remain authoritative above this contract.


## Implementation Evidence (DELIVERED)

PROOF:

### CI/Test Results
- Commands run:
  - `/usr/bin/python3 -B -m unittest discover -s tests -p 'unit_spendability_evidence.py'`
  - `/opt/homebrew/bin/python3 -B -m unittest discover -s tests -p 'unit_spendability_evidence.py'`
  - `PYTHONPYCACHEPREFIX=/tmp/grrr-wu6f-pycache/system /usr/bin/python3 -B -m py_compile research/spendability_evidence.py tests/unit_spendability_evidence.py`
  - `PYTHONPYCACHEPREFIX=/tmp/grrr-wu6f-pycache/homebrew /opt/homebrew/bin/python3 -B -m py_compile research/spendability_evidence.py tests/unit_spendability_evidence.py`
  - `pvg verify research/spendability_evidence.py tests/unit_spendability_evidence.py --format=text`
  - `git diff --check`
  - `git diff --cached --check`
  - Static scan for file/network/subprocess/SQLite/environment/`/Library/GRRR` operations in the two changed files.
- Summary:
  - System Python focused unit: PASS, Ran 28 tests, 0 failures, 0 errors, 0 skipped, exit 0.
  - Homebrew Python focused unit: PASS, Ran 28 tests, 0 failures, 0 errors, 0 skipped, exit 0.
  - System Python compile: PASS, exit 0; cache confined to `/tmp/grrr-wu6f-pycache/system`.
  - Homebrew Python compile: PASS, exit 0; cache confined to `/tmp/grrr-wu6f-pycache/homebrew`.
  - Explicit-path pvg verify: `VERIFY: PASSED (2 files scanned, 0 issues)`, exit 0.
  - `git diff --check`: PASS, exit 0.
  - `git diff --cached --check`: PASS, exit 0.
  - Forbidden-operation scan: PASS, no matches; 28 discoverable `test_case_` methods.
- Coverage: 28/28 approved contract adversarial cases mapped 1:1 (100% case mapping). Statement coverage was not measured because this story requires focused unit/static verification, not a full coverage run.

### Commit
- Branch: `story/GRRR-wu6f`
- SHA: `2522a8ea95068527bba8db85180c4b38c239a1a0`
- Subject: `feat(GRRR-wu6f): validate spendability evidence fail-closed`
- Files and hashes:
  - `research/spendability_evidence.py`: 624 lines, SHA256 `50f18fd77137d0a0519527ce631f4fac7012197fa96aefed2947a0293601d5f7`
  - `tests/unit_spendability_evidence.py`: 372 lines, SHA256 `baa2923927d8a65cb71b5e7dc28cc8ccd12df9d8354323e2e26c97e159280e21`
- Diff budget: 996 inserted LOC across exactly the two bounded files, under the ~1000-LOC budget.

### pvg verify
- `VERIFY: PASSED (2 files scanned, 0 issues)`

### AC Verification
| AC | Requirement | Code Location | Test/Check Location | Status |
|---|---|---|---|---|
| 1 | All 28 contract adversarial cases map 1:1 and pass on both required interpreters | `research/spendability_evidence.py:119-624` | `tests/unit_spendability_evidence.py:229-366` (28 methods); both required focused commands above | PASS |
| 2 | Current-like incomplete package returns unresolved/null spendability and retains pending maxima | `research/spendability_evidence.py:205-218,530-624` | `tests/unit_spendability_evidence.py:319-324,339-344`; totals remain 900,000,000 execution-us | PASS |
| 3 | Validation is pure/in-memory with no protected access, reconciliation execution, staging, production mutation, or external side effect | `research/spendability_evidence.py:1-624`; result pins `allowed_mutations=()` and `execution_authorized=False` at 623-624 | Static forbidden-operation scan PASS; no full suite, replay, VM, protected read, or integration action run | PASS |
| 4 | Explicit-path compile/static verify and diff checks pass | Changed files named above | Both compile exits 0; `pvg verify` PASS; both diff checks exit 0 | PASS |

LEARNINGS:
- Compacting the candidate to 996 total LOC preserved all 28 contract cases and the current-like 8-settled/3-pending shape while staying below budget.
- `pvg verify` usefully flagged the original overflow sentinel `return {}` as a stub; the final API returns `None` for an unrepresentable pending total instead of fabricating a clamped value.
- Both required interpreters produced identical 28-test, zero-skip results with bytecode writes confined to `/tmp`.

### OBSERVATIONS (unrelated)
- None.

## nd_contract
status: delivered

### evidence
- Commit `2522a8ea95068527bba8db85180c4b38c239a1a0` on `story/GRRR-wu6f`.
- Both required interpreters: Ran 28 tests, OK, exit 0.
- Both compile commands: exit 0 with cache confined under `/tmp/grrr-wu6f-pycache`.
- `pvg verify`: PASSED, 2 files, 0 issues.
- `git diff --check` and `git diff --cached --check`: PASS.
- Static forbidden I/O/path scan: PASS.

### proof
- [x] AC #1: 28/28 contract cases map 1:1 and pass on both interpreters with no skips.
- [x] AC #2: incomplete evidence remains `spendable=null`; all three pending maxima and their 900,000,000 execution-us total are retained.
- [x] AC #3: validation is synthetic/in-memory only and exposes no mutation or execution authority.
- [x] AC #4: focused compile/static verify and both diff checks pass.

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
- 2026-10-26T02:58:59Z status: in_progress -> in_progress
- 2026-10-26T02:58:59Z auto-follows: linked to predecessor GRRR-43i8
- 2026-10-26T03:15:30Z status: in_progress -> open
- 2026-10-26T03:15:30Z released by speed

## Links
- Parent: [[GRRR-2t3h]]
- Blocks: [[GRRR-z3w9]]
- Follows: [[GRRR-d8ji]], [[GRRR-43i8]]

## Comments

### 2026-10-26T03:02:29Z speed
## Implementation Evidence (DELIVERED — authoritative parent verification)

PROOF:

### CI/Test Results
Commands run:
- `/usr/bin/python3 -B -m unittest discover -s tests -p 'unit_spendability_evidence.py'`
- `/opt/homebrew/bin/python3 -B -m unittest discover -s tests -p 'unit_spendability_evidence.py'`
- `PYTHONPYCACHEPREFIX=/tmp/grrr-wu6f-parent-system /usr/bin/python3 -m py_compile research/spendability_evidence.py tests/unit_spendability_evidence.py`
- `PYTHONPYCACHEPREFIX=/tmp/grrr-wu6f-parent-homebrew /opt/homebrew/bin/python3 -m py_compile research/spendability_evidence.py tests/unit_spendability_evidence.py`
- `pvg verify research/spendability_evidence.py tests/unit_spendability_evidence.py --include-tests --format=text`
- `git diff --check`
- `git diff --cached --check`
- `git diff --check 820469226032761ca1335fe58ef674a3219e8d07..story/GRRR-wu6f`
- Static scan for `/Library/GRRR`, subprocess, socket, urllib, requests, SQLite, or file-open operations in the two changed files.

Summary:
- System Python focused test: PASS; Ran 28 tests in 0.056s; 0 failures, 0 errors, 0 skipped; exit 0.
- Homebrew Python focused test: PASS; Ran 28 tests in 0.042s; 0 failures, 0 errors, 0 skipped; exit 0.
- Both compile commands: PASS, exit 0; bytecode confined under `/tmp`.
- Explicit-path pvg verify: `VERIFY: PASSED (2 files scanned, 0 issues)`.
- All diff checks: PASS.
- Forbidden API/path scan: PASS, no matches.
- Exactly 28 discoverable `test_case_` methods map 1:1 through contract cases 1–28.
- Worktree clean; no full suite, replay, VM/QEMU, protected access, reconciliation execution, production mutation, merge, or push occurred.

### Commit
- Branch: `story/GRRR-wu6f`
- SHA: `2522a8ea95068527bba8db85180c4b38c239a1a0`
- Parent: `820469226032761ca1335fe58ef674a3219e8d07`
- Subject: `feat(GRRR-wu6f): validate spendability evidence fail-closed`
- Exact changed paths:
  - `research/spendability_evidence.py` — 624 lines, SHA256 `50f18fd77137d0a0519527ce631f4fac7012197fa96aefed2947a0293601d5f7`
  - `tests/unit_spendability_evidence.py` — 372 lines, SHA256 `baa2923927d8a65cb71b5e7dc28cc8ccd12df9d8354323e2e26c97e159280e21`
- Total diff: 996 inserted LOC across exactly two files, within the ~1000-LOC budget.

### AC Verification
| AC | Requirement | Evidence | Status |
|---|---|---|---|
| 1 | Implement pure fail-closed validator for approved contract | `research/spendability_evidence.py`; no file/network/subprocess/SQLite/protected-path API | PASS |
| 2 | Implement all 28 adversarial cases as focused tests | Exactly 28 `test_case_N` methods, contiguous 1–28; both interpreters 28/28 PASS | PASS |
| 3 | Current-like incomplete evidence remains null and retains pending holds | Case 21 and validator result preserve `spendable=null`, three pending maxima, and 900,000,000 execution-us total | PASS |
| 4 | Canonical/join/provenance/arithmetic/scope/stale rules fail closed | Cases 1–28 and validator gate order | PASS |
| 5 | No reconciliation/replay/protected/production authority or execution | Static scan PASS; result pins `allowed_mutations=()` and `execution_authorized=False`; no prohibited action run | PASS |
| 6 | Both required interpreters and static checks pass | Commands and summaries above | PASS |

### Coverage
- Contract adversarial-case mapping: 28/28 (100%).
- Statement/branch coverage percentage not measured; no coverage claim is made.
- Full suite intentionally not run because this authorized slice is focused unit validation only and current capacity is below the separate full-suite floors.

## nd_contract
status: delivered

### evidence
- Commit `2522a8ea95068527bba8db85180c4b38c239a1a0` adds exactly the two bounded validator/test files.
- Both required interpreters independently reran the focused suite: 28/28 OK, exit 0, no skips.
- Compile, explicit-path pvg verify, diff checks, forbidden-API scan, and clean-worktree checks pass.

### proof
- [x] AC #1: pure in-memory fail-closed validator implemented.
- [x] AC #2: all 28 adversarial cases map 1:1 and pass on both interpreters.
- [x] AC #3: incomplete current-like evidence returns `spendable=null` and retains pending maxima.
- [x] AC #4: canonical, ancestry, provenance, joins, arithmetic, scope, pending, and stale rules fail closed.
- [x] AC #5: no protected access, reconciliation, replay, promotion, admission, production mutation, merge, or push.
- [x] AC #6: focused both-interpreter and static verification pass.

### 2026-10-26T03:04:13Z speed
## Parent Dispatch Verification

Operator scope was one bounded spendability evidence-validator implementation story from approved contract commit 820469226032761ca1335fe58ef674a3219e8d07. The created story is GRRR-wu6f, parent GRRR-2t3h, blocking GRRR-z3w9.

Parent independently verified:
- Story branch base and contract commit: 820469226032761ca1335fe58ef674a3219e8d07.
- Implementation commit: 2522a8ea95068527bba8db85180c4b38c239a1a0.
- Exact changed paths: research/spendability_evidence.py and tests/unit_spendability_evidence.py.
- Total diff: 996 inserted LOC across two files.
- Implementation SHA256: 50f18fd77137d0a0519527ce631f4fac7012197fa96aefed2947a0293601d5f7.
- Test SHA256: baa2923927d8a65cb71b5e7dc28cc8ccd12df9d8354323e2e26c97e159280e21.
- Exactly 28 contiguous test_case methods map to contract cases 1–28.
- System Python focused suite: 28/28 OK, exit 0.
- Homebrew Python focused suite: 28/28 OK, exit 0.
- Both compile checks, explicit-path pvg verify, diff checks, and forbidden API/path scan passed.
- Delivery verification passes 9/9.
- Worktree clean.

The story is delivered and awaits independent PM review. No /Library/GRRR access or mutation, reconciliation decision/execution, unknown-zeroing, replay/live/integration execution, VM/QEMU/UID-GID action, promotion, admission, production mutation, full-suite execution, cache cleanup, merge, or push occurred.

### 2026-10-26T03:07:53Z speed
## Delivery Contract EOF Correction

The delivered implementation remains commit 2522a8ea95068527bba8db85180c4b38c239a1a0. The prior parent dispatch note was informational and was not intended to replace developer proof.

## nd_contract
status: delivered

### evidence
- Implementation SHA: 2522a8ea95068527bba8db85180c4b38c239a1a0.
- Implementation SHA256: 50f18fd77137d0a0519527ce631f4fac7012197fa96aefed2947a0293601d5f7.
- Test SHA256: baa2923927d8a65cb71b5e7dc28cc8ccd12df9d8354323e2e26c97e159280e21.
- Both interpreters: 28/28 focused tests passed with zero failures, errors, or skips.
- Compile, explicit-path pvg verify, diff checks, and forbidden API/path scan passed.

### proof
- [x] Pure fail-closed evidence validator implemented.
- [x] All 28 contract adversarial cases map 1:1 and pass.
- [x] Incomplete evidence remains spendable=null with pending maxima retained.
- [x] No protected access, reconciliation, replay, promotion, admission, production mutation, merge, or push occurred.
