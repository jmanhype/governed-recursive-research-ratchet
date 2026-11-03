# GRRR-z3w9 Stage E narrow rework review request

## Exact scope

Review only the correction for the Stage E review-1 byte-binding rejection:
approved Stage D capture/postcapture digests must be pinned inside the
validation trust boundary, independent of bundle basis fields. Do not access or
mutate protected accounting paths. Do not write spendability, reconcile, replay,
admit, promote, mutate production, merge, or push.

## Exact current identities

- Stage D evidence commit: `d431807ce24e6c7decf57d22ffe478309da98743`
- Assembler:
  `research/spendability_bundle.py`
  SHA-256 `08ef91d035ac5e82305f59152299a4222ef27bd88d86b1ec74c2a873ed92a914`
- Script:
  `scripts/assemble-spendability-bundle`
  SHA-256 `266cbea21ba3233ff050e4ebd5fc25d4c6d33dd14def371e16974112a55509f2`
- Tests:
  `tests/unit_spendability_bundle.py`
  SHA-256 `6c29a994462175be8263eb43ab38491ae34bd50df0a059a34e2a3bab257a918f`
- Bundle:
  SHA-256 `52f08fc740feee1e48de7fb79b83ccb684324339dab386c383805ec136956467`
- Validation:
  SHA-256 `28e322cb6e651962a6eb1e76974c8d99775181a4863c0db01c01f2e0b555cb05`

## Required correction evidence

- `APPROVED_STAGE_D_CAPTURE_SHA256` is pinned to:
  `d22bec465786840fc85a139ebe3781f68bd1663bde51649ac96d34e03e340de8`
- `APPROVED_STAGE_D_POSTCAPTURE_SHA256` is pinned to:
  `78eb1f69a30d161f3c2d8c67fbbf40e579cc3de5f53b6bb0f8e8fc395888574a`
- Both assembler and validator enforce these constants before trusting supplied
  hashes.
- Regression tests append a newline to capture/postcapture bytes, update the
  corresponding bundle basis hash, and require rejection.
- Bundle regeneration remains byte-identical.

## Current validation

- Focused bundle tests: **16/16 passed** on Python 3.9.6 and 3.14.3.
- Full no-guest suites: **379/379 passed** on both interpreters.
- `pvg verify` selected assembler/script/tests: PASS.
- `git diff --check`: PASS.

## Required verdict

Return exactly one:

- `STAGE_E_NARROW_REWORK_REVIEW: APPROVED`
- `STAGE_E_NARROW_REWORK_REVIEW: REJECTED`

Approval covers only the fail-closed Stage E bundle implementation and artifact.
It grants no spendability, reconciliation, replay, admission, promotion, merge,
or push authority.
