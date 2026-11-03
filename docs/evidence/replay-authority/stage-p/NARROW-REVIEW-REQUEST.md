# GRRR-z3w9 Stage P narrow re-review request

## Exact scope

Review only the correction for malformed schema-version types and regenerated
focused/full evidence. Do not repeat unrelated architecture review. Do not
access or mutate `/Library/GRRR`; do not edit files; do not build/install
runtime, stage protected records, amend budget, reconcile, execute replay,
admit, promote, mutate production, merge, or push.

## Corrected identities

- `research/replay_successor_installer_contract.py`
  SHA-256 `9e4d9bdf393cd219bfcf7ccc5d01917089cd67d51be40a0a571d03dcfcc90762`
- `tests/unit_replay_successor_installer_contract.py`
  SHA-256 `598eea1811e2791eab4dcf6045074d6110482653586774165b574dc48ba8480b`
- `docs/evidence/replay-authority/stage-p/FOCUSED-HOMEBREW-3.14.log`
  SHA-256 `1b196761b5de3aaeb4711df00ddadab7310f220d5cc7fb171f5590c76532c954`
- `docs/evidence/replay-authority/stage-p/FOCUSED-MINICONDA-3.12.log`
  SHA-256 `40cb8ca1f4dcdee8d9dc3022ec89760e4ade35458ee09ffe4550ea15b9f31971`
- `docs/evidence/replay-authority/stage-p/FULL-HOMEBREW-3.14.log`
  SHA-256 `6dffccf35486c84dbfb0b37b4d4e90b15c0bbeca43f4f4f4d81f23f67bc5a1f9`
- `docs/evidence/replay-authority/stage-p/FULL-MINICONDA-3.12.log`
  SHA-256 `6198fb346fa04f901d0317fc749bb973e61b401e28fd5aa431743542347672ab`

The generated `CONTRACT.json` remains byte-identical because the candidate itself
already used integer version `1`; only validators and tests changed.

## Required checks

1. Confirm both validators require `type(schema_version) is int`.
2. Confirm tests reject `True` and `1.0` for both contract and issued
   authorization validation.
3. Rerun both focused suites and expect 27/27 each.
4. Regenerate the contract emitter and confirm it remains byte-identical.
5. Confirm no other authority, basis, source-role, path, or gate semantics
   changed from the initially reviewed package.

## Required verdict

Return exactly one:

- `STAGE_P_NARROW_REWORK_REVIEW: APPROVED`
- `STAGE_P_NARROW_REWORK_REVIEW: REJECTED`

Approval covers only this corrected design-only WIP. It does not approve
installer implementation, exact protected bytes, protected access or staging,
budget amendment, reconciliation, replay, admission, promotion, merge, or push.
