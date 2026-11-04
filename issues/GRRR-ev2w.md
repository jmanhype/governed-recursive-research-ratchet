---
id: GRRR-ev2w
title: "Bug: Fail closed on corrupt admission registry"
status: closed
priority: 0
type: bug
labels: [milestone-1, security, integration, discovered-by-developer, accepted]
parent: GRRR-2t3h
created_at: 2026-11-04T01:07:35Z
created_by: speed
updated_at: 2026-11-04T01:21:14Z
content_hash: "sha256:2045db589d072502c2d2ba4983b18979e99f14fc33786fd1d53ec1ccd56b618f"
assignee: dev-GRRR-ev2w
follows: [GRRR-888u, GRRR-gge0]
closed_at: 2026-11-04T01:21:13Z
close_reason: "Accepted: branch 710e6fb matches the delivered hashes; 9/9 delivery proof, 28 unit and 6 real-filesystem integration executions on Python 3.14/3.9 with 0 failures/skips, and the 3-file 197-line diff satisfy all six fail-closed/durability ACs within scope."
---
## Description
## Context
- Discovery base: `epic/GRRR-2t3h` at `845b47d221773eb4157491d35f57dce47ce8afe6`; the affected implementation exists at `research/admission.py`.
- GRRR-6sso reported that `pvg verify` flags `research/admission.py:60`. Current `_load_registry()` catches both `json.JSONDecodeError` and `OSError`, executes `pass`, and returns `{"consumed_authorizations": [], "admitted_contracts": {}}`.
- Failure scenario: a truncated/malformed/unreadable durable registry is indistinguishable from a legitimate first use. A later `_save_registry()` can replace the damaged evidence, while consumed-authorization and admitted-contract knowledge are silently lost. That can permit authorization replay or a duplicate contract admission and can make `recurrence_rejected()` falsely reject safe recurrence protection.
- This is a P0 durability/security bug in the accepted admission controller, not missing capstone evidence. It must be fixed independently before the capstone can claim complete mandatory authorization/admission capability.

## USER INTENT
I can trust permanent admission state: corruption or unreadable durable evidence must stop admission and preserve the audit trail, never reset duplicate protection to an empty registry.

## Root Cause
`_load_registry()` treats registry decoding/read failures as an empty registry. It does not distinguish legitimate initialization from integrity or availability failure, and the caller can then persist derived state over the unusable registry.

## Affected Components
- `research/admission.py`
  - `REGISTRY_PATH = Path(__file__).resolve().parent.parent / "docs/evidence/contract-admission/REGISTRY.json"`
  - `_load_registry()`
  - `consume_authorization(auth)`
  - `persist_admission(admission)`
  - `recurrence_rejected(admission, replay_receipt)`
- `tests/unit_admission.py` (current coverage resets/removes the registry and does not corrupt it)
- New real-filesystem integration coverage for durable registry failure behavior

## OUT OF SCOPE
- Do not “fix” the unrelated `AdmissionError`/`research/review_report.py` static-verification `pass` findings or hide `pvg verify` output; this story owns only silent registry reset.
- Do not redesign registry schema, add reversals, or implement a new registry version; preserve the existing version-1 shape unless a same-scope validation error requires rejecting an invalid shape.
- Do not execute protected admission, replay, promotion, production mutation, external/paid calls, merge, or push.
- Do not complete or weaken GRRR-6sso capstone journeys, Jev comparison, stop/recovery, adversarial matrix, accessibility, or final packet requirements; GRRR-6sso remains their owner.

## DIFF BUDGET
~3 files, under 250 changed LOC: admission implementation plus focused unit and real-filesystem integration regressions. Gross overrun triggers PM investigation, not automatic rejection.

## Boundary Map
PRODUCES:
- research/admission.py -> `_load_registry() -> registry dict`, raising `AdmissionError` for an existing registry that is malformed, structurally invalid, or unreadable
- tests/unit_admission.py -> focused real-file unit regressions for initialization, malformed JSON, invalid shape, and durable duplicate state
- tests/integration/admission_registry.py -> public admission-path integration regressions using a real temporary registry and no filesystem mocks

CONSUMES:
- GRRR-34ve: research/admission.py -> `consume_authorization(auth)`, `persist_admission(admission)`, `recurrence_rejected(admission, replay_receipt)`
  spec: existing Python admission state operations; preserve their call shape and ensure registry integrity failures fail closed rather than returning an empty registry
- GRRR-34ve: tests/integration/protected-admission -> real success/failure integration pattern
  source: accepted admission-controller story requires durable protected registry outcomes and no mocks

## Bug Acceptance Criteria
1. **State / legitimate initialization:** When `REGISTRY_PATH` does not exist, admission still begins with exactly an empty version-1 shape containing a `consumed_authorizations` list and `admitted_contracts` mapping, and the existing valid admission success path continues to work.
2. **Unwanted / corrupt bytes:** An existing registry containing malformed or truncated JSON makes `_load_registry()`, `consume_authorization()`, `persist_admission()`, and `recurrence_rejected()` fail closed with `AdmissionError`; none may return or persist an empty registry.
3. **Unwanted / wrong structure:** Parseable but invalid registry JSON (non-object, missing/unknown fields, `consumed_authorizations` not a list, or `admitted_contracts` not a mapping) also fails closed with `AdmissionError`; it must not be coerced or reset.
4. **Unwanted / unavailable evidence:** A real filesystem read failure makes the same public admission paths fail closed with `AdmissionError`; the failing load must not create `.tmp`, replace the registry, consume an authorization, or add an admitted contract.
5. **State / durable duplicates:** A valid registry containing an already consumed authorization and admitted contract retains that state across reload: replayed authorization and duplicate contract admission remain rejected, and the real admitted recurrence remains rejected.
6. **Integration proof:** Real temporary-file integration tests exercise success plus malformed JSON, invalid shape, unavailable read, and durable duplicate reload through the public admission path, with no mocks, no skip-if-missing, no protected repository evidence mutation, and nonzero exit on any mandatory case failure.

## Testing Requirements
- Unit tests: cover legitimate missing registry, malformed/truncated JSON, each structural-shape error, and preservation of consumed/admitted state. Redirect `REGISTRY_PATH` to a real temporary file rather than deleting `docs/evidence/contract-admission/REGISTRY.json`.
- Integration tests: MANDATORY (no mocks). Use a real temporary filesystem path and public admission operations; prove failures leave the original bytes/inode-appropriate file unchanged and no temporary replacement is committed. Do not mock `Path`, JSON, or admission functions.
- Required commands (all offline and repository-only): `python3 -B tests/unit_admission.py`; `python3 -B tests/integration/admission_registry.py`.
- Focused verification must show that the silent `research/admission.py:60` catch-and-reset finding is gone. Unrelated pre-existing static findings may remain visible and must not be suppressed.
- No protected path access, runtime admission authorization, replay, external call, credentials, merge, or push.

## Discovered During
Story GRRR-6sso: repository-only capstone rework identified the admission-controller defect as separate responsible security/admission scope.

## MANDATORY SKILLS
- developer: implement exactly this bug, preserve concurrent edits, deliver but do not close.
- nd and pvg: live tracker notes/transitions only; never edit issue files directly.
- pm_acceptor: independent acceptance after real test evidence.
- codebase-memory: verify existing admission source/test relationships before editing.

## Skills To Use
- `nd` and `pvg` for tracker operations.
- `codebase-memory` for structural source/test discovery.
- No protected-access or external-integration skill is authorized.

## Delivery Requirements
- Developer must append exact command output/exit counts, affected SHA, test paths, and an AC-by-AC proof table with `pvg nd update --append-notes`.
- Developer must run `pvg story verify-delivery` and `pvg story deliver`; PM-Acceptor independently closes or rejects.
- Preserve the capstone boundary: GRRR-6sso may not be delivered while this bug is open.

## nd_contract
status: new

### evidence
- Created: 2026-11-04
- Discovery source: GRRR-6sso DISCOVERED_BUG “Admission registry corruption silently resets durable state”.
- Repository evidence at base 845b47d221773eb4157491d35f57dce47ce8afe6: `research/admission.py:55-61` catches `json.JSONDecodeError`/`OSError`, executes `pass`, and returns empty state.

### proof
- [ ] Pending implementation

## Acceptance Criteria


## Design


## Notes


## nd_contract
status: accepted

### evidence
- PM closeout applied via pvg story accept on 2026-11-03.

### proof
- [x] Story closed after accepted label was applied.


## Implementation Evidence

PROOF: Formatting supplement to the complete evidence, AC table, and LEARNINGS above; all results refer to the same final commit. No code or claims changed.

### CI/Test Results
Commands run:
- python3 -B tests/unit_admission.py: 28 passed, exit 0.
- python3 -B tests/integration/admission_registry.py: 6 passed, exit 0.
- /usr/bin/python3 -B tests/unit_admission.py: 28 passed, exit 0.
- /usr/bin/python3 -B tests/integration/admission_registry.py: 6 passed, exit 0.
- python3 -B tests/unit_review_report.py and /usr/bin/python3 -B tests/unit_review_report.py: 6 passed each, exit 0 each.
- python3 -B tests/unit_safe_stop.py and /usr/bin/python3 -B tests/unit_safe_stop.py: 7 passed each, exit 0 each.
- pvg verify research/admission.py tests/unit_admission.py tests/integration/admission_registry.py --format=text: exit 1, only excluded unchanged AdmissionError class pass at line 84.
- pvg gates research/admission.py tests/unit_admission.py tests/integration/admission_registry.py --format text: exit 0, PASS with unchanged recurrence_rejected complexity warning.

Summary: 94 passed, 0 failures/errors/skips; extra coverage run 28 passed. Admission module line coverage 89.8%, loader executable lines fully exercised. Full command output and hashes are in the preceding evidence block.

Commit SHA: 710e6fb1affa366da6ca4c855f49805d3bdb944d
SHA: 710e6fb1affa366da6ca4c855f49805d3bdb944d

LEARNINGS:
- Delivery verification expects exact heading and label syntax; this append-only supplement normalizes it without replacing prior evidence.

## nd_contract
status: delivered

### evidence
- Commit 710e6fb1affa366da6ca4c855f49805d3bdb944d, branch story/GRRR-ev2w; complete AC table and artifact hashes above remain authoritative.
- 94 successful test executions on Python 3.14.3/3.9.6; no failures or skips. Explicit existing static exceptions remain visible.

### proof
- [x] AC #1: absent registry exact empty shape and valid success.
- [x] AC #2: malformed/truncated registry rejected by loader and public operations.
- [x] AC #3: all specified invalid shapes rejected.
- [x] AC #4: real filesystem failures preserve evidence and do not write temporary state.
- [x] AC #5: durable authorization/contract duplicates and recurrence protection survive fresh import.
- [x] AC #6: mandatory real temporary-filesystem integration tests pass on both interpreters without mocks or skips.

## nd_contract
status: delivered

### evidence
- Transitioned via pvg story deliver on 2026-11-03.

### proof
- [ ] Developer evidence block must remain authoritative above this contract.


## Implementation Evidence (DELIVERED)

PROOF:

### CI/Test Results
Commands run (cwd: dispatcher-owned `.claude/worktrees/dev-GRRR-ev2w`):
- `python3 -B tests/unit_admission.py` — 28 tests, OK, exit 0 (Python 3.14.3).
- `python3 -B tests/integration/admission_registry.py` — 6 tests, OK, exit 0.
- `/usr/bin/python3 -B tests/unit_admission.py` — 28 tests, OK, exit 0 (Python 3.9.6).
- `/usr/bin/python3 -B tests/integration/admission_registry.py` — 6 tests, OK, exit 0.
- `python3 -B tests/unit_review_report.py` — 6 tests, OK, exit 0.
- `python3 -B tests/unit_safe_stop.py` — 7 tests, OK, exit 0.
- `/usr/bin/python3 -B tests/unit_review_report.py` — 6 tests, OK, exit 0.
- `/usr/bin/python3 -B tests/unit_safe_stop.py` — 7 tests, OK, exit 0.
- `python3 -B -m trace --count --missing --summary --coverdir /tmp/GRRR-ev2w-evidence-v1/coverage-verified --module unittest discover -s tests -p unit_admission.py` — 28 tests, OK, exit 0; admission.py 89.8% line coverage, all executable loader lines 58–73 executed. No branch-coverage claim.
- `pvg verify research/admission.py tests/unit_admission.py tests/integration/admission_registry.py --format=text` — exit 1, 3 files scanned, one finding: `research/admission.py:84 [stub] bare pass statement` in unchanged AdmissionError. Original loader catch-and-reset finding is gone. This remaining finding is explicitly outside this story's scope and not suppressed.
- `pvg gates research/admission.py tests/unit_admission.py tests/integration/admission_registry.py --format text` — exit 0, `GATES: PASS (1 warn, 0 skipped)`; unchanged recurrence_rejected CCN 15 warning at line 223 remains visible.
- `git diff --check 845b47d221773eb4157491d35f57dce47ce8afe6 HEAD` — exit 0.
- `git status --short` — empty, exit 0.

Summary: 94 test executions passed, 0 failures, 0 errors, 0 skips; plus 28 successful coverage executions. Static verification has the one explicitly excluded existing class-pass finding; metric gates pass with one existing complexity warning. No full repository suite was run: assigned tests plus adjacent offline review/stop tests cover the bounded change; protected, replay, external, and capstone journeys remain outside this assignment. No runtime authorization, protected repository registry mutation, network/Jev, merge, or push performed.

Coverage: stdlib trace reports admission.py 89.8% line coverage (187 executable lines); changed loader executable lines all exercised. Initial `python3 -m coverage --version` found coverage uninstalled. An exploratory direct-file trace invocation incorrectly ran zero tests; that output is retained in verification.log and is NOT claimed as coverage proof. The corrected unittest-discovery invocation above ran 28 actual tests and is the authoritative coverage measurement.

RED evidence before implementation: the initial new 27-test unit suite failed with 21 subtest failures and one UnicodeDecodeError, demonstrating silent corrupt/invalid state acceptance. Final suite has 28 tests after adding metadata-access regression.

### Commit
- Branch: `story/GRRR-ev2w`
- SHA: `710e6fb1affa366da6ca4c855f49805d3bdb944d`
- Base: `845b47d221773eb4157491d35f57dce47ce8afe6`
- Diff: 3 files, 197 insertions, 10 deletions. Only loader behavior and focused unit/integration tests changed.
- Final complete command/output artifact: `/tmp/GRRR-ev2w-evidence-v1/verification-final.log`
- Artifact SHA256: `1c3517dafd88b9196134e66921c947ff7de53eedbe830366b2709f4886061dc9`
- research/admission.py SHA256: `d6f53e43ea4233e2a244ed4c5640739a3610dbee40bdad85e2bca6d90717a43f`
- tests/unit_admission.py SHA256: `ae8a648eb40efb75bf6082203996bc0fc67760537113631956212a81eddb84fd`
- tests/integration/admission_registry.py SHA256: `a633e088f6fc9f5e76babad2d64769155b670ef31977bb0bccfaae412e26d710`

### Wiring and boundaries
- Existing public consume_authorization/persist_admission/recurrence_rejected call `_load_registry`; their signatures, locks, persistence implementation, and valid registry-v1 shape are unchanged.
- Loader now uses lstat to distinguish a missing directory entry from unavailable metadata or a dangling link, raises AdmissionError for read/parse/encoding/depth failures, and rejects wrong top-level structure without writing.
- Tests redirect only the registry configuration to real TemporaryDirectory paths and restore it through cleanup; no filesystem/function mocks or skips.
- Integration asserts bytes or preserved directory evidence, inode/size/mtime, unchanged input objects, no `.tmp`, real permission denial, and duplicates across an independently imported module.
- Graph MCP tools were unavailable; bounded grep/read fallback covered admission.py and all test imports. No additional admission importers found within bin/scripts/tests. No docs/findings directory exists in this worktree. Epic HEAD checked before implementation.

### AC Verification
| AC # | Requirement | Code Location | Test Location | Status |
|------|-------------|---------------|---------------|--------|
| 1 | Only legitimate absence initializes exact empty v1 shape; valid success works | research/admission.py:58-61 | unit test_missing_registry_is_empty_without_writing; integration setUp and test_success_and_durable_duplicates_after_module_reload | PASS |
| 2 | Corrupt/truncated bytes fail closed across loader and public paths | research/admission.py:64-67 | unit test_corrupt_registry_rejects_without_reset; integration test_malformed_truncated_and_invalid_encoding and assert_closed | PASS |
| 3 | Non-object, missing/unknown fields, wrong collection types reject | research/admission.py:68-72 | unit test_invalid_registry_shapes_reject (19 cases); integration test_invalid_shapes (6 cases across 5 paths) | PASS |
| 4 | Real unavailable reads preserve evidence with no temp writes or mutations | research/admission.py:58-67 | unit test_unavailable_registry_metadata_rejects; integration unreadable-file, directory, dangling-link cases and assert_closed | PASS |
| 5 | Consumed/admitted state remains durable and recurrence protected | unchanged public operations plus validated loader | unit test_duplicate_state_survives_reload; integration independent-module reload test | PASS |
| 6 | Real temporary-file integration success and all mandatory failures, nonzero on failure | tests/integration/admission_registry.py | 6 integration tests pass on Python 3.14.3 and 3.9.6; unittest.main supplies failure exit status | PASS |

LEARNINGS:
- Path.exists is not a safe security-state initialization discriminator; lstat distinguishes missing entries from dangling registry links, and access errors must propagate as domain failure.
- Changing the unit fixture to isolated real temporary storage avoids deleting accepted evidence during ordinary regression runs.
- Fresh module imports prove durable duplicate behavior without invalidating exception-class identities held by other test modules.
- Stdlib trace must invoke unittest discovery here; direct tracing of a unittest.main script yielded zero tests and is not valid coverage evidence.

### OBSERVATIONS (not changed)
- `pvg notes search 'admission registry'` could not access a worktree-local .vault. Shared tracker operations through pvg nd succeeded; no vault configuration was changed. Context/evidence remain appended in this story.
- `tests/integration/protected-admission`, referenced as a historical pattern in the story, is absent at the base; the newly required Python integration entry point is self-contained and fully executes.
- Existing AdmissionError class-pass static finding and recurrence_rejected complexity warning remain reported above per the explicit scope boundary; GRRR-6sso capstone claims are unchanged.

## nd_contract
status: delivered

### evidence
- Commit 710e6fb1affa366da6ca4c855f49805d3bdb944d; exact commands and full count summaries above.
- 94/94 assigned/focused executions passed on two interpreters, plus 28 coverage executions. No tests skipped.
- Static verify retains only the excluded class-pass finding; gates pass with disclosed existing warning.

### proof
- [x] AC #1: exact empty initialization and valid success.
- [x] AC #2: corrupt/truncated/invalid-encoding/deep JSON rejected without reset.
- [x] AC #3: invalid top-level registry shapes rejected.
- [x] AC #4: real unreadable evidence preserved; no temporary write or admission/authorization mutation.
- [x] AC #5: durable duplicates and real recurrence remain rejected after independent module import.
- [x] AC #6: real-file integration success and mandatory failures pass without mocks/skips on both interpreters.

## History
- 2026-11-04T01:07:35Z dep_added: blocks GRRR-6sso
- 2026-11-04T01:11:27Z status: open -> in_progress
- 2026-11-04T01:11:27Z auto-follows: linked to predecessor GRRR-888u
- 2026-11-04T01:11:27Z claimed by dev-GRRR-ev2w
- 2026-11-04T01:17:37Z status: in_progress -> in_progress
- 2026-11-04T01:17:37Z auto-follows: linked to predecessor GRRR-gge0
- 2026-11-04T01:21:13Z status: in_progress -> closed
- 2026-11-04T01:21:13Z dep_removed: no_longer_blocks GRRR-6sso

## Links
- Parent: [[GRRR-2t3h]]
- Follows: [[GRRR-888u]], [[GRRR-gge0]]

## Comments

### 2026-11-04T01:07:35Z speed
RECOMMEND hard-tdd: corrupt durable security state has subtle failure-preservation cases. Adds RED/GREEN phases and roughly doubles agent passes, tokens, and wall-clock time; label not applied because no hard-TDD authorization exists for this story.
