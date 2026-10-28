# GRRR-z3w9 Stage G independent review request

## Exact scope

Review only the local evidence-search implementation, generated candidate index,
validation record, focused logs, and operator handoff. Do not access or mutate
protected accounting paths. Do not reconcile, write spendability, replay, admit,
promote, mutate production, merge, or push.

## Base state

- Story branch: `story/GRRR-z3w9`
- Stage F commit under review: `5ea8afca67fb980f69ed3a97a19c0b2a356c5a8b`
- Stage F request SHA-256:
  `6c59851d15fa44afccc3907e0aa0bedd7eb629095898d50b51a53079183cf919`
- Stage F package SHA-256:
  `388b0022adfba2a2e60ca436239178fa07589b4ffbe724bae6b5f847a2e4be23`
- Stage A baseline SHA-256:
  `7608cbe6fc5f671b88573eca8b642ebfbc172f0cb920f75d60ca34cfa60c730a`

## Files for review

- `research/spendability_search.py`
  SHA-256 `99e12225a660573cac060bdbadb6ac435d82b8bbf36a5c62dcef4142a17252e3`
- `scripts/search-spendability-evidence`
  SHA-256 `799fefeb821fe3ae7a2a7342b63fb290a7c392878595de19cd83c1651c486518`
- `tests/unit_spendability_search.py`
  SHA-256 `8710be30838004fd0ee942aa5e43e8dc85366200b86179bd267eee69ad3e44c3`
- `docs/evidence/spendability/stage-g/CANDIDATE-INDEX.json`
  SHA-256 `31466b133af19110cd80323ff4499642307bd2c74bff055079ec13738203c7bc`
- `docs/evidence/spendability/stage-g/VALIDATION.json`
  SHA-256 `ff4b465e9111ff14e74c42914f994bb3e8695caa0503e22df959539bdc86459a`
- `docs/evidence/spendability/stage-g/HANDOFF.md`
  SHA-256 `439592c0f12ccf675843135070bad4b4d9fadcc1baa03ec63bcb8202da7ad07a`
- `docs/evidence/spendability/stage-g/FOCUSED-HOMEBREW-3.14.log`
  SHA-256 `baeec883ba6561f79e6ff3755e41f9da1b4feb8c59383184e2e2a46896caa4fc`
- `docs/evidence/spendability/stage-g/FOCUSED-MINICONDA-3.12.log`
  SHA-256 `ee750d69eecddd2e2101cfff88e652c7cebe4d91efdc9a2a0db111c8df649054`
- `docs/evidence/spendability/stage-g/FULL-HOMEBREW-3.14.log`
- `docs/evidence/spendability/stage-g/FULL-MINICONDA-3.12.log`
- `docs/evidence/spendability/stage-g/REPLAY-SMOKE-RETRY-HOMEBREW-3.14.log`
- `docs/evidence/spendability/stage-g/REPLAY-SMOKE-RETRY-MINICONDA-3.12.log`

## Review questions

1. Does validation bind the exact approved Stage F request/package and Stage A
   baseline rather than trusting mutable metadata?
2. Does it verify the trusted export's readback, ledger, snapshot identity,
   event hash chain, projection, object bytes, and observation raw digests?
3. Does it correctly join all 11 request events to Stage A runs and maxima?
4. Does it correctly join the eight settled reservations' meter receipt, actual
   usage, and observation object?
5. Does it retain all three pending reservations as partial rather than
   inferring non-dispatch, zero cost, or final unavailability?
6. Does it refuse to convert lineage hash references, agent/session matches,
   partial operation history, or empty overhead into final absence or spendability?
7. Does the candidate index contain all 30 Stage F item IDs exactly once with
   no final classification and independent review required?
8. Does any code path access protected paths, grant authority, or claim
   spendability?
9. Is the full-suite process-table timeout correctly recorded as an unresolved
   host-pressure gate rather than hidden or converted into success?
10. Are manual negative discovery observations explicitly demoted to
    `search-completeness-not-established` rather than falsely presented as
    exhaustive search proof?

## Recorded validation

- Homebrew Python 3.14.3: 13/13 passed.
- Miniconda Python 3.12.7: 13/13 passed.
- Generator output across those interpreters: byte-identical.
- System Python 3.9 was not run because Xcode 27.1 reports that its license has
  not been accepted; no license action was taken.
- Latest full no-guest suite: 407 tests on each interpreter with one existing
  process-table timing failure on each under host load.
- Isolated replay-smoke retry: 12/12 passed on each interpreter.
- `pvg verify --include-tests`: PASS.
- `git diff --check`: PASS.

## Required verdict

Return exactly one:

- `STAGE_G_SEARCH_NARROW_REWORK_REVIEW: APPROVED`
- `STAGE_G_SEARCH_NARROW_REWORK_REVIEW: REJECTED`

Approval covers only the local search/index validation. It does not classify
the eight candidates as accepted spendability evidence, establish historical
completeness, or grant reconciliation/replay authority.
