---
id: GRRR-gzgq
title: "Bug: Fail closed on corrupt admission registry"
status: open
priority: 0
type: bug
labels: [milestone-1, security, integration, discovered-by-developer]
parent: GRRR-2t3h
created_at: 2026-11-04T01:03:31Z
created_by: speed
updated_at: 2026-11-04T01:05:43Z
content_hash: "sha256:97417bef742da6086e8d1c54cbdeb39eb2c922ef055098cb3a149e784a61bac0"
blocks: [GRRR-6sso]
---

## Description
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


## History
- 2026-11-04T01:03:31Z dep_added: blocks GRRR-6sso

## Links
- Parent: [[GRRR-2t3h]]
- Blocks: [[GRRR-6sso]]

## Comments

### 2026-11-04T01:03:32Z speed
RECOMMEND hard-tdd: corrupt durable security state has subtle failure-preservation cases. Adds RED/GREEN phases and roughly doubles agent passes, tokens, and wall-clock time; label not applied because no hard-TDD authorization exists for this story.

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

## Acceptance Criteria
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


## History
- 2026-11-04T01:03:31Z dep_added: blocks GRRR-6sso

## Links
- Parent: [[GRRR-2t3h]]
- Blocks: [[GRRR-6sso]]

## Comments

### 2026-11-04T01:03:32Z speed
RECOMMEND hard-tdd: corrupt durable security state has subtle failure-preservation cases. Adds RED/GREEN phases and roughly doubles agent passes, tokens, and wall-clock time; label not applied because no hard-TDD authorization exists for this story.
