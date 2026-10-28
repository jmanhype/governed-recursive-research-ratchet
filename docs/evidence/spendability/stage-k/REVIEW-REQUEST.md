# GRRR-z3w9 Stage K independent review request

## Exact scope

Review only the Stage K session search, per-record matrix implementation,
generated matrix, validation, focused logs, and handoff. Do not access or mutate
`/Library/GRRR`. Do not reconcile, write spendability, replay, admit, promote,
mutate production, merge, or push.

## Base state

- Stage I commit:
  `9b58eae0ba62d0d384a4743ea069bf3dde6c9f6d`
- Stage J WIP package SHA-256:
  `7a2251decd3073aaa268e2dabdeb16f4d9d8f9283536760c38ad4d6b5ab1c53e`
- Original session archive SHA-256:
  `a595ff5c996d5d673e005a3d55e0b82a3a8187ed5693b2c232a0f16e771fa80e`

## Files and identities

- `research/spendability_per_record.py`
  SHA-256 `4b96c4765469d6c4c3dfb7c5e448b3ebdb24a53149d6a4f8a9d136b1b73cefce`
- `scripts/build-spendability-per-record-matrix`
  SHA-256 `ae0678a63185df65b1b563e11fe2e85df01f0c589a4e5703b79aa4856b677d9f`
- `tests/unit_spendability_per_record.py`
  SHA-256 `f718e98b71a86a06eb3074828d9383aedd48e21e3755e516a12706d00a6df265`
- `docs/evidence/spendability/stage-k/SESSION-SEARCH.json`
  SHA-256 `84b6f0ebfb76d2adcd359274a167d2b77becd76cda6b3f265ce1845197c182cc`
- `docs/evidence/spendability/stage-k/PER-RECORD-MATRIX.json`
  SHA-256 `d71139015cd3b27683503984947ba692800e407aecd6f45d1ccf6e3c18ecd4d1`
- `docs/evidence/spendability/stage-k/VALIDATION.json`
  SHA-256 `492b6c56d728fb0dd5335adc7e863d75c6ae1a690bb4433f66322fe426286d9a`
- `docs/evidence/spendability/stage-k/HANDOFF.md`
  SHA-256 `a9059acf3ab559c55f32ab7fb7f52ffc0ec219791f6db2f45df0d935f58aed3d`
- `docs/evidence/spendability/stage-k/FOCUSED-HOMEBREW-3.14.log`
  SHA-256 `b8d44bfe5111f293d9830fa230ffaf8bdf6c73a4cfed9f4f537452aa99ea1d4e`
- `docs/evidence/spendability/stage-k/FOCUSED-MINICONDA-3.12.log`
  SHA-256 `310eeacb393fdfefbdf6958873397f16218bac56746cd785eca724894e4b69d3`

## Review questions

1. Does Stage K bind the exact Stage J package/validation and Stage I commit?
2. Does it hash the full original operator session archive and independently
   reproduce exact identifier counts?
3. Does it bind the line-11533 hash and common readback start/end boundary?
4. Does it validate the reviewed numeric evaluator/runner identity mapping?
5. Does it verify pinned source identity constants and evaluator-only ledger
   enforcement, plus the Stage A database owner UID/GID 320?
6. Does it preserve all eight reservation/run/request/event/object/meter chains?
7. Does it retain duration values without fabricating per-reservation UTC
   intervals, dispatch operation IDs, or authenticated principal receipts?
8. Does it keep all eight records unclassified and response-not-ready?
9. Does it grant no spendability or operational authority?

## Required verdict

Return exactly one:

- `STAGE_K_PER_RECORD_NARROW_REWORK_REVIEW: APPROVED`
- `STAGE_K_PER_RECORD_NARROW_REWORK_REVIEW: REJECTED`

Approval covers only the per-record matrix. It does not classify records as
supplied, establish spendability, or authorize reconciliation/replay.
