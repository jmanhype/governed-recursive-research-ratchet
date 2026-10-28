# GRRR-z3w9 Stage N narrow re-review request

## Exact scope

Review only the correction for the initial rejection: the corrected predecessor
hold ID, the retained-Stage-A derivation regression, regenerated contract and
summary, updated focused/full logs, and updated report. Do not repeat unrelated
architecture review. Do not access or mutate `/Library/GRRR`. Do not edit files,
implement/install runtime, reconcile, execute replay, admit, promote, mutate
production, merge, or push.

## Corrected identities

- `research/replay_successor_contract.py`
  SHA-256 `30a78a0733fb826cf02f83dddf54696dc0dd3fd456d189f77e96fed72714382f`
- `tests/unit_replay_successor_contract.py`
  SHA-256 `9def6292e95387dc9cacfe4c18e26e8b041da260866869a895d708ea79808b20`
- `docs/evidence/replay-authority/stage-n/CONTRACT.json`
  SHA-256 `20a79ab0121454e43c98328641a3c8fd0b84efa7298a52a158a728efe5bce135`
- `docs/evidence/replay-authority/stage-n/SUMMARY.json`
  SHA-256 `ed2790014f2610f90c2957024ba90191f42c85a89d4724a302941519e5a575e7`
- `docs/evidence/replay-authority/stage-n/FOCUSED-HOMEBREW-3.14.log`
  SHA-256 `f9ed80c32923ba9e1faaeb4461ba5823dda364bc33e436d13902c1344a9719d0`
- `docs/evidence/replay-authority/stage-n/FOCUSED-MINICONDA-3.12.log`
  SHA-256 `ec7add9cf6aba06677aa36e4963b7418431440c434b946963b93b0cc6c2dbde3`
- `docs/evidence/replay-authority/stage-n/FULL-HOMEBREW-3.14.log`
  SHA-256 `89836a1bf59068efbac2c67cddadef73e2c365ee90161bdbd000154061070924`
- `docs/evidence/replay-authority/stage-n/FULL-MINICONDA-3.12.log`
  SHA-256 `d56d5881cb378d848f0b174802b99cadcc203c30da4d31f18a2d285cc08d5c31`

The retained Stage A baseline remains:

- path: `docs/evidence/spendability/stage-a/BASELINE.json`;
- SHA-256:
  `7608cbe6fc5f671b88573eca8b642ebfbc172f0cb920f75d60ca34cfa60c730a`.

## Required checks

1. Confirm the corrected ID is exactly
   `b34d8b9d106e42eab3a3e43daac98ddd`.
2. Independently hash Stage A and derive pending IDs from reservation rows with
   null actual/receipt values and the exact 300,000,000-microsecond maximum.
3. Rerun both focused Stage N suites and expect 28/28 each.
4. Regenerate the contract and confirm it is byte-identical to `CONTRACT.json`.
5. Confirm no other authority or gate semantics changed from the initially
   reviewed design.

## Required verdict

Return exactly one:

- `STAGE_N_NARROW_REWORK_REVIEW: APPROVED`
- `STAGE_N_NARROW_REWORK_REVIEW: REJECTED`

Approval covers only this corrected design-only WIP. It does not approve runtime
implementation, protected access or installation, spendability reconciliation,
budget amendment, replay, admission, promotion, merge, or push.
