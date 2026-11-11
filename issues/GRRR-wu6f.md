---
id: GRRR-wu6f
title: "Validate spendability evidence fail-closed"
status: closed
priority: 1
type: task
parent: GRRR-2t3h
created_at: 2026-10-26T02:20:26Z
created_by: speed
updated_at: 2026-10-26T04:04:40Z
content_hash: "sha256:4c7156a9c62253a5838d8c81c147a857d9150320e5785a909f8a7e981a23bd08"
labels: [milestone-1, integration, spendability-validator, accepted]
follows: [GRRR-d8ji, GRRR-43i8, GRRR-w1lt, GRRR-bnkf, GRRR-c875]
assignee: dev-GRRR-wu6f
closed_at: 2026-10-26T03:53:35Z
close_reason: "Accepted: strict type-first enum validation closes the malformed-value fail-closed gap while preserving all 28 cases and boundaries"
led_to: [GRRR-z3w9, GRRR-6sso]
blocks: [GRRR-6sso, GRRR-2hib]
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


## nd_contract
status: accepted

### evidence
- PM closeout applied via pvg story accept on 2026-10-25.

### proof
- [x] Story closed after accepted label was applied.


## PM Decision
ACCEPTED [2026-10-25]: Full re-review of rework commit a1664df3ae43cbfb5aaa2128ebc0a29641c626fd closes the prior malformed-enum rejection.

Reviewed evidence:
- Exact parent/commit ancestry: rejected 2522a8ea95068527bba8db85180c4b38c239a1a0 -> rework a1664df3ae43cbfb5aaa2128ebc0a29641c626fd; story base remains 820469226032761ca1335fe58ef674a3219e8d07.
- Exact rework diff is bounded to research/spendability_evidence.py (11 insertions/6 deletions) and tests/unit_spendability_evidence.py (47 insertions/1 deletion); hashes match 73c644b90952b9dd449d2fecb98286b5e3b5c02974b25c267e4f5fe6c3efb449 and 47030e903277ad66fed8056b198e7cba0a6564c330149924d78cd3a819747ba4.
- research/spendability_evidence.py:119-120 now type-checks enum values before membership; all enum-like row/arithmetic surfaces at 289, 293, 301, 322, 461-462, and 486-487 use it. No raw untrusted enum membership remains.
- tests/unit_spendability_evidence.py:277-324 now covers unknown stage, unhashable stage, wrong-type disposition, wrong-type pending dispatch outcome, and wrong-type overhead category. Each subTest asserts the affected first gate, null spendability, retained pending maxima and 900,000,000 execution-us total, no authority, and preserved observed evidence.
- Exactly 28 contiguous test methods remain (test_case_01 through test_case_28); no skip, expected-failure, or test-weakening marker was found.
- PM reran delivery proof (9/9), explicit-path pvg verify (2 files, 0 issues), rework diff whitespace check, hash/line-count checks, stub/secret/forbidden-I/O/protected-path scans, and raw-enum scan: all PASS.
- Trusted complete recorded focused evidence and parent behavioral confirmation rather than rerunning tests: both interpreters each ran exactly 28 tests with OK and zero failures/errors/skips.
- Diff budget note: final story-to-base addition is 1,047 lines across two files, a small explained increase above the nominal 1000 caused by the required malformed-type safety rework; not a gross or unexplained overrun.
- Boundary preserved: review-only; no /Library/GRRR access or mutation, reconciliation/replay/promotion/admission/production action, merge, or push.

## nd_contract
status: accepted

### evidence
- Reviewed rework commit a1664df3ae43cbfb5aaa2128ebc0a29641c626fd and the full evidence-based PM ladder.

### proof
- [x] AC #1: exactly 28 contiguous cases are preserved and recorded as passing on both required interpreters.
- [x] AC #2: unresolved spendability remains null and all pending maxima are retained.
- [x] AC #3: validation remains pure/in-memory with no protected access, external side effect, or authority grant.
- [x] AC #4: compile/static/diff evidence is complete; delivery proof passes 9/9.
- [x] Rework: malformed enum-shaped values now return structured ValidationResult output instead of raising TypeError.

## nd_contract
status: delivered

### evidence
- Rework commit `a1664df3ae43cbfb5aaa2128ebc0a29641c626fd` on `story/GRRR-wu6f`; parent `2522a8ea95068527bba8db85180c4b38c239a1a0`.
- System Python focused command: Ran 28 tests, OK, 0 failures/errors/skips.
- Homebrew Python focused command: Ran 28 tests, OK, 0 failures/errors/skips.
- Both `py_compile` commands: exit 0 with bytecode under `/tmp/grrr-wu6f-rework-*`.
- `pvg verify ... --include-tests`: `VERIFY: PASSED (2 files scanned, 0 issues)`.
- `git diff --check`, `git diff --cached --check`, and `git diff --check HEAD~1..HEAD`: PASS.
- AST authorization scan: PASS; 0 raw enum findings; 0 forbidden API/path findings.
- Implementation SHA256 `73c644b90952b9dd449d2fecb98286b5e3b5c02974b25c267e4f5fe6c3efb449`; test SHA256 `47030e903277ad66fed8056b198e7cba0a6564c330149924d78cd3a819747ba4`.

### proof
- [x] AC #1: exactly 28 contiguous cases pass 28/28 on both required interpreters.
- [x] AC #2: unresolved spendability remains null and pending maxima are retained.
- [x] AC #3: validation remains pure/in-memory with no protected access or external side effect.
- [x] AC #4: compile, explicit-path `pvg verify`, and all required diff checks pass.
- [x] Rework: malformed enum values return structured fail-closed evidence with affected first gate, preserved observed evidence, null spendability, and retained pending maxima.

## nd_contract
status: delivered

### evidence
- Transitioned via pvg story deliver on 2026-10-25.

### proof
- [ ] Developer evidence block must remain authoritative above this contract.


## Implementation Evidence (DELIVERED — REWORK 1)

PROOF:

### CI/Test Results
- Commands run at commit `a1664df3ae43cbfb5aaa2128ebc0a29641c626fd`:
  - `/usr/bin/python3 -B -m unittest discover -s tests -p 'unit_spendability_evidence.py'`
  - `/opt/homebrew/bin/python3 -B -m unittest discover -s tests -p 'unit_spendability_evidence.py'`
- System Python: PASS — Ran 28 tests in 0.072s; OK; 0 failures, 0 errors, 0 skips.
- Homebrew Python: PASS — Ran 28 tests in 0.052s; OK; 0 failures, 0 errors, 0 skips.
- Test discovery count: exactly 28 contiguous `test_case_01` through `test_case_28` methods; no method 29 was added.

### Compile/Static/Diff Results
- Commands run:
  - `PYTHONPYCACHEPREFIX=/tmp/grrr-wu6f-rework-system /usr/bin/python3 -B -m py_compile research/spendability_evidence.py tests/unit_spendability_evidence.py`
  - `PYTHONPYCACHEPREFIX=/tmp/grrr-wu6f-rework-homebrew /opt/homebrew/bin/python3 -B -m py_compile research/spendability_evidence.py tests/unit_spendability_evidence.py`
  - `pvg verify research/spendability_evidence.py tests/unit_spendability_evidence.py --include-tests --format=text`
  - `git diff --check`
  - `git diff --cached --check`
  - `git diff --check HEAD~1..HEAD`
  - AST authorization scan over exactly the two changed files.
- Both interpreter compiles: PASS, exit 0; bytecode prefixes confined under `/tmp/grrr-wu6f-rework-system` and `/tmp/grrr-wu6f-rework-homebrew`.
- `pvg verify`: `VERIFY: PASSED (2 files scanned, 0 issues)`.
- All diff checks: PASS, exit 0, no whitespace findings.
- AST authorization scan: `AUTHORIZATION: PASS`; `RAW_ENUM_FINDINGS: 0`; `FORBIDDEN_API_PATH_FINDINGS: 0`.
- Static import/call/string scan found no file, network, subprocess, SQLite, or `/Library/GRRR` API/path.

### Commit
- Branch: `story/GRRR-wu6f`
- Rework commit: `a1664df3ae43cbfb5aaa2128ebc0a29641c626fd`
- Parent (original rejected implementation): `2522a8ea95068527bba8db85180c4b38c239a1a0`
- Subject: `fix(GRRR-wu6f): type-check enum evidence values`
- New commit diff: exactly 2 files, 58 insertions, 7 deletions.
  - `research/spendability_evidence.py`: 11 insertions, 6 deletions; 629 lines; SHA256 `73c644b90952b9dd449d2fecb98286b5e3b5c02974b25c267e4f5fe6c3efb449`
  - `tests/unit_spendability_evidence.py`: 47 insertions, 1 deletion; 418 lines; SHA256 `47030e903277ad66fed8056b198e7cba0a6564c330149924d78cd3a819747ba4`
- Worktree clean after commit.

### AC Verification
| AC | Requirement | Code Location | Test/Check Location | Status |
|---|---|---|---|---|
| 1 | All 28 contract adversarial cases map 1:1 and pass on both required interpreters | Existing validator behavior retained | Exactly 28 methods at `tests/unit_spendability_evidence.py:236-416`; both commands above | PASS |
| 2 | Incomplete evidence remains unresolved and retains pending maxima | Pending derivation/result preservation unchanged | Existing cases 20, 21, 23, 24; malformed variants also assert 3 maxima and 900,000,000 execution-us total | PASS |
| 3 | Validation remains pure/in-memory with no protected access, reconciliation execution, staging, production mutation, or external side effect | Only enum predicate and membership uses changed | AST forbidden API/path scan PASS; result still pins `allowed_mutations=()` and `execution_authorized=False` | PASS |
| 4 | Explicit-path compile/static verify and diff checks pass | Two authorized changed files | Both compile PASS; `pvg verify` PASS; all diff checks PASS | PASS |
| Rework blocker | Malformed enum-shaped values return structured fail-closed results rather than raising `TypeError` | `_enum` strict-string predicate at `research/spendability_evidence.py:119-120`; reservation stage/disposition at 289/293; pending outcome at 301; overhead category at 322; arithmetic-side category at 484-487 | Case 10 sweeps unknown-string stage, unhashable `[]` stage, wrong-type disposition, wrong-type pending outcome, and wrong-type overhead category with `subTest` at `tests/unit_spendability_evidence.py:277-323` | PASS |

Case 10 asserts each malformed result has `valid=False`, `spendable=None`, the affected first gate (`row_schema` or `pending_evidence`), all 3 pending maxima, the 900,000,000 execution-us pending total, and an `observed_evidence` deep copy equal to the submitted package. The 28 original case mappings remain contiguous and no other case was weakened.

LEARNINGS:
- Raw `not in frozenset` validation is not safe for JSON-shaped values because unhashable arrays raise before the structured result boundary.
- A strict-string `_enum(value, allowed)` predicate gives one type-first boundary for every enum-like membership surface.
- Keeping malformed-type coverage inside case 10 preserves the contract's exact 28-method mapping while making the failure mode visible under `subTest`.
- The affected gate can legitimately differ: malformed `dispatch_outcome` belongs to `pending_evidence`, while the other four malformed enum fields fail `row_schema`.

## nd_contract
status: rejected

### evidence
- PM rejection applied via pvg story reject on 2026-10-25.

### proof
- [ ] Story requires another developer delivery before it can be accepted.


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
- 2026-10-26T03:34:17Z status: open -> in_progress
- 2026-10-26T03:34:17Z auto-follows: linked to predecessor GRRR-w1lt
- 2026-10-26T03:34:17Z claimed by dev-GRRR-wu6f
- 2026-10-26T03:41:11Z status: in_progress -> in_progress
- 2026-10-26T03:41:11Z auto-follows: linked to predecessor GRRR-bnkf
- 2026-10-26T03:41:29Z status: in_progress -> in_progress
- 2026-10-26T03:41:29Z auto-follows: linked to predecessor GRRR-c875
- 2026-10-26T03:53:35Z status: in_progress -> closed
- 2026-10-26T03:53:35Z dep_removed: no_longer_blocks GRRR-z3w9
- 2026-11-04T01:05:04Z dep_added: blocks GRRR-6sso
- 2026-11-11T21:15:21Z dep_added: blocks GRRR-2hib

## Links
- Parent: [[GRRR-2t3h]]
- Blocks: [[GRRR-6sso]], [[GRRR-2hib]]
- Follows: [[GRRR-d8ji]], [[GRRR-43i8]], [[GRRR-w1lt]], [[GRRR-bnkf]], [[GRRR-c875]]
- Led to: [[GRRR-z3w9]], [[GRRR-6sso]]

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

### 2026-10-26T03:15:30Z speed
## PM Decision
REJECTED [2026-10-25]
EXPECTED: The approved contract says missing, malformed, stale, duplicate, ambiguous, late, unauthenticated, or partial evidence must fail the affected gate, and error output must name the first failed mandatory gate and preserve observed source evidence. The delivered public API is validate_evidence returning ValidationResult for this purpose.
DELIVERED: At commit 2522a8ea95068527bba8db85180c4b38c239a1a0, research/spendability_evidence.py:284-290 tests row stage and disposition membership directly in frozensets. A JSON-shaped exact-schema reservation with stage set to an unhashable array raises TypeError at row["stage"] not in STAGES before a ValidationResult is returned. The equivalent category membership at lines 318-319 and 481-482 has the same malformed-type hazard. The 28 tests exercise only the hashable unknown string production.
GAP: Malformed field values can escape the structured fail-closed API instead of producing first_failed_gate, gate_results, retained observed_evidence, pending maxima, and null spendability. This violates the contract malformed-evidence/first-failure requirement and AC coverage for fail-closed validation.
FIX: Normalize membership checks to safe exact-type predicates or equivalent type-first validation for all enum-like fields. Ensure every JSON-shaped malformed package returns a ValidationResult naming the first failed gate and retaining evidence. Strengthen an existing case, while preserving exactly 28 test methods, with a wrong-type stage or category and assert the structured result rather than an exception.
## nd_contract
status: rejected

### evidence
- Reviewed commit 2522a8ea95068527bba8db85180c4b38c239a1a0 against contract commit 820469226032761ca1335fe58ef674a3219e8d07.
- Trusted complete recorded both-interpreter 28-test and static proof; no tests rerun.
- Static exact-diff, hashes, line counts, delivery-proof shape, stub/secret/forbidden-API scans, and boundary review passed; malformed-type API behavior is the rejection gap.

### proof
- [ ] AC #1: the 28 recorded cases pass, but the validator does not structurally fail closed for malformed enum-shaped field values outside those representative inputs.
- [ ] AC #2/#3: pending and authority behavior is otherwise retained, but the public validator contract is incomplete for malformed evidence.

### 2026-10-26T03:42:56Z speed
## nd_contract
status: delivered

### evidence
- Rework commit `a1664df3ae43cbfb5aaa2128ebc0a29641c626fd` on `story/GRRR-wu6f`; parent `2522a8ea95068527bba8db85180c4b38c239a1a0`.
- Both required focused commands ran 28 tests with 0 failures, 0 errors, and 0 skips.
- Both compile commands, `pvg verify ... --include-tests`, all diff checks, and AST authorization scan passed.
- Full rework evidence, hashes, and AC proof are in the appended Implementation Evidence note.

### proof
- [x] AC #1: exactly 28 contiguous cases pass on both interpreters.
- [x] AC #2: unresolved spendability remains null and pending maxima are retained.
- [x] AC #3: validation remains pure/in-memory with no protected access or external side effect.
- [x] AC #4: compile, static verify, and diff checks pass.
- [x] Rework: malformed enum-shaped values return structured fail-closed evidence without TypeError.

### 2026-10-26T04:03:02Z speed
## Operator Merge Authorization and Contamination Preflight

APPROVED [2026-10-26]: merge accepted GRRR-wu6f into epic/GRRR-2t3h. Denied: /Library/GRRR access or mutation, reconciliation, replay, promotion, admission, production mutation, and push.

Live preflight:
- Story is closed/accepted at a1664df3ae43cbfb5aaa2128ebc0a29641c626fd.
- Epic HEAD 38f33c936b8249a57be81aebd639aa40c2f9de55 is the merge base.
- Story worktree is clean.
- A normal full branch merge would introduce 65 files and 4,243 insertions because story/GRRR-wu6f descends through unaccepted GRRR-z3w9 WIP.

Governance decision for this merge:
- Preserve the accepted commit as the second merge parent.
- Include only the independently approved spendability evidence contract plus the accepted GRRR-wu6f validator/test paths in the epic tree.
- Exclude unaccepted GRRR-z3w9 replay implementation/evidence changes from the resulting tree.
- Verify the resulting diff, focused tests, and ancestry before deleting the story branch.

### 2026-10-26T04:04:40Z speed
## Authoritative Merge Result

Accepted story GRRR-wu6f was merged into epic/GRRR-2t3h at curated two-parent merge commit 36671bc467286404b9dfddcf487fc9358aa2b643.

Canonical `pvg story merge GRRR-wu6f --base epic/GRRR-2t3h` could not fetch because this local-only repository has no origin remote. After verifying the story was closed/accepted and both repository/worktree states were clean, the orchestrator used the local accepted+closed merge fallback.

Merge parents:
- Previous epic: 38f33c936b8249a57be81aebd639aa40c2f9de55
- Accepted story: a1664df3ae43cbfb5aaa2128ebc0a29641c626fd

Governance-safe tree curation:
- The accepted story branch descends through unaccepted GRRR-z3w9 WIP; a normal merge would have introduced 65 files and 4,243 insertions.
- The merge preserves the accepted story commit as the second parent but stages only the independently approved evidence contract and the accepted validator/test deliverables.
- The resulting first-parent diff changes exactly 3 paths / 1,514 insertions:
  1. docs/SPENDABILITY-RECONCILIATION-EVIDENCE-CONTRACT.md
  2. research/spendability_evidence.py
  3. tests/unit_spendability_evidence.py
- Unaccepted replay implementation/evidence ancestry is not present in the resulting epic tree.

Artifact hashes:
- Contract: c179b6c9640a5d848f70bb9b7e6ac3833223a6c55ddf9bfa0b2dbe68a6c82b37
- Validator: 73c644b90952b9dd449d2fecb98286b5e3b5c02974b25c267e4f5fe6c3efb449
- Tests: 47030e903277ad66fed8056b198e7cba0a6564c330149924d78cd3a819747ba4

Verification:
- Accepted story commit is an ancestor of epic HEAD.
- Previous epic commit is an ancestor of epic HEAD.
- System Python focused suite: 28/28 OK, 0 failures/errors/skips.
- Homebrew Python focused suite: 28/28 OK, 0 failures/errors/skips.
- Explicit-path pvg verify: PASSED, 2 files, 0 issues.
- git diff --check and staged diff check: PASS.
- Forbidden API/path scan on validator/test: PASS.
- Clean story worktree was removed before merge.
- story/GRRR-wu6f branch was deleted only after ancestry verification.
- Epic worktree remains clean.

No /Library/GRRR access or mutation, reconciliation, replay, promotion, admission, production mutation, or push occurred.
