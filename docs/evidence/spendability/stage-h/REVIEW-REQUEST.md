# GRRR-z3w9 Stage H independent review request

## Exact scope

Review only the Stage H response-readiness implementation, generated matrix,
validation record, focused logs, and operator handoff. Do not access or mutate
protected accounting paths. Do not reconcile, write spendability, replay, admit,
promote, mutate production, merge, or push.

## Base state

- Stage F commit base: `5ea8afca67fb980f69ed3a97a19c0b2a356c5a8b`
- Stage G commit under review:
  `a43e7413c3383d74578931620d212465441b1f3d`
- Stage G package SHA-256:
  `d00b35c07f2b482f3441a767d179c5e163a27f0f2db4ff8544c727a7da44f4ca`
- Stage G candidate index SHA-256:
  `31466b133af19110cd80323ff4499642307bd2c74bff055079ec13738203c7bc`

## Files and identities

- `research/spendability_response.py`
  SHA-256 `fda3bd5212b63e30db80e603d6a8e2931fd0e432b888cbd41bcddfa90176b230`
- `scripts/build-spendability-response-readiness`
  SHA-256 `9d96ba7a7cc9c775514e97efdf087942e0406d9450ac0d3092a53a4a2a12a834`
- `tests/unit_spendability_response.py`
  SHA-256 `4baf377dd1e07284b122c38205dd5ef517e45ee928a53dc34cffe1717798dce8`
- `docs/evidence/spendability/stage-h/RESPONSE-READINESS.json`
  SHA-256 `d4aefba5c2f391f130b0319be3723b368cdbe4d21b13650a2d2acfbdb23341cf`
- `docs/evidence/spendability/stage-h/VALIDATION.json`
  SHA-256 `5111dcda05555cd5eb680f1ad5ca40ca14851835d87316351fd1e1eb80a693c3`
- `docs/evidence/spendability/stage-h/HANDOFF.md`
  SHA-256 `fc60cc9c667f66edbaae803fcc014254efcfefada66625fc31c0f5653ace8b2b`
- `docs/evidence/spendability/stage-h/FOCUSED-HOMEBREW-3.14.log`
  SHA-256 `a79eda2c18f33cb23457850dcf415038dfe685a89e28cd673c2ade6ad2cbd2bc`
- `docs/evidence/spendability/stage-h/FOCUSED-MINICONDA-3.12.log`
  SHA-256 `b9fb18300fbe588c0a68875706a60dd6daab67ba9cbbe4390f02d15e4719ddbb`

## Review questions

1. Does Stage H bind the exact Stage F request/package, Stage A baseline,
   Stage G package, Stage G candidate index, and trusted export identities?
2. Does it map all 30 Stage F item IDs exactly once?
3. Does it recognize exactly eight candidate request/observation/meter record
   sets without marking them response-ready?
4. Does it preserve missing issuer identity, authorization, operation boundary,
   UTC measurement boundary, timestamps, custodian, custody, retrieval method,
   and independent review as blocking gaps?
5. Does it keep the three pending items, 15 search-completeness items, partial
   operation history, and all other domains non-final?
6. Does it make zero classifications and grant no spendability or operational
   authority?
7. Does regeneration reject modified inputs, injected classifications, and
   injected authority?

## Required verdict

Return exactly one:

- `STAGE_H_READINESS_REVIEW: APPROVED`
- `STAGE_H_READINESS_REVIEW: REJECTED`

Approval covers only the response-readiness matrix. It does not classify any
record as supplied, establish spendability, or authorize reconciliation/replay.
