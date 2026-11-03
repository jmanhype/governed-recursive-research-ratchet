# GRRR-z3w9 Stage R independent source-issuance review request

## Exact scope

Review only the repository-retained v4 protected-source issuance package,
builder, emitter, tests, exact source-role files, generated bundle, retained
logs, and report. Do not access or mutate `/Library/GRRR`. Do not stage or
install protected records, amend the budget, reconcile, execute replay, admit,
promote, mutate production, merge, or push.

## Base state

- Story HEAD: `23fdac5fcdc9bcef5147314a8f3c8bcb6d458d3f`
- Stage P package:
  `ba7e8a45486a21ff399027821d3b0bd1d21c6577730597f900f3c21fb192c0b1`
- Stage Q package:
  `d953651c0bd635a1e80295376665fd2331b86ac9b5f25f726b945bcf9e41fb3e`

## Implementation identities

- `research/replay_successor_source_issuance.py`
  SHA-256 `9e8da12568235c3699bb218e81bc84e47bc395e939219196bd6996f77c9fa955`
- `scripts/prepare-replay-successor-v4-source-issuance`
  SHA-256 `d6d7a0bbf594c3fda3570eb149275ee5eafce67b7241fb436d10761c6b822e13`
- `tests/unit_replay_successor_source_issuance.py`
  SHA-256 `7e5d93760ac867549380ceb2eac7d5a420be82c7ebecbe31177d4e306c9ebade`
- `docs/evidence/replay-authority/stage-r/SOURCE-BUNDLE.json`
  SHA-256 `6d025533ab33c41490a154d947880adefb208b486a49314b365d5486eb7484f0`

## Exact role identities

- `source/install-replay-successor-v4`
  SHA-256 `94b37112fc3b3146078b6edd0cf80d5e845f1cc83543344d79e00d144d453dbc`
- `source/replay-successor-v4-v4_store_schema.py`
  SHA-256 `629c6a70936fb94ea4b4a89b4dc3c94095aa2586194c077e4c06258b2c7ce644`
- `source/replay-successor-v4-stage_n_contract.py`
  SHA-256 `d2105c6fbab6edd42ad9724e6ff2313d2531c11af14625bfb0cf8a81b9646fb5`
- `source/replay-successor-v4-stage_o_runtime_adapter.py`
  SHA-256 `f54f051684dd9be4ccf635d3029cb1f099ddb227e8d763efad2c8bf24e3478c4`
- `source/replay-successor-v4-protected_preflight.py`
  SHA-256 `bffc612b0e48bff8969fa463bbb57bd8edbdaf00962deb1de048662eff268221`
- `source/replay-successor-v4-atomic_publisher.py`
  SHA-256 `c448f4853e6bb9467c6994b64b3f04dfd9ee9c6d0718de69529eb24218e5a719`
- `source/replay-successor-v4-postflight_verifier.py`
  SHA-256 `f276c0bd84a4fe43d5661672600734120af1332c45c372fc6881a2913491ca46`
- `source/replay-successor-v4-failure_preservation.py`
  SHA-256 `8fb37a74e96c7fab7f96fed74ad1aea187fc306716ebb024a1cd0059ca9ded47`

## Logs

- `docs/evidence/replay-authority/stage-r/FOCUSED-HOMEBREW-3.14.log`
  SHA-256 `3a8b150d26a1e03efb91192a33647e4aa91956099d71cbac0d10193469c3cb52`
- `docs/evidence/replay-authority/stage-r/FOCUSED-MINICONDA-3.12.log`
  SHA-256 `b0e59b619fd378293155bbf13cc6f05bcb383fd3d2fd1d50dd0e22cc42816fb5`
- `docs/evidence/replay-authority/stage-r/FULL-HOMEBREW-3.14.log`
  SHA-256 `cf18b8820b0a5b048ac795b173534a7d0d2bffac16aa1fd6c3f823f7b9b7e81d`
- `docs/evidence/replay-authority/stage-r/FULL-MINICONDA-3.12.log`
  SHA-256 `13b97345a40cb3c964d14bd296de172402c323a080ec417c6e14b39f31e035be`

## Required commands

```sh
/opt/homebrew/bin/python3 -I -B -W error::ResourceWarning -m unittest discover -s tests -p 'unit_replay_successor_source_issuance.py' -v
/Users/speed/miniconda3/bin/python -I -B -W error::ResourceWarning -m unittest discover -s tests -p 'unit_replay_successor_source_issuance.py' -v
scripts/prepare-replay-successor-v4-source-issuance > /tmp/grrr-stage-r-review.json
cmp docs/evidence/replay-authority/stage-r/SOURCE-BUNDLE.json /tmp/grrr-stage-r-review.json
```

## Review questions

1. Does the builder read only the eight retained source-role files and remain
   free of protected filesystem access?
2. Does the package contain exactly the eight Stage P roles, exact destination
   paths, and eight distinct source hashes?
3. Are the pinned source bytes, canonical role identity digest, and generated
   bundle exact and deterministic?
4. Does tampering, removal, marker replacement, or issuance injection fail?
5. Does the Stage N role preserve unresolved spendability, encumbered ceilings,
   and all three exact predecessor holds?
6. Does the Stage O role remain unissued and block replay?
7. Does protected preflight reject `/Library`, `/Library/GRRR`, repeated
   leading roots, `..`, absolute escapes, and symlinks before metadata access?
8. Does store creation/publication/postflight/failure preservation work only in
   a temporary sandbox and preserve stopped/empty/uncertain semantics?
9. Does the entrypoint refuse even exact live-install grammar?
10. Does the package remain `prepared-not-issued`, with operator issuance,
    protected staging, and all operational authority explicitly not-run/false?

## Required verdict

Return exactly one:

- `STAGE_R_SOURCE_ISSUANCE_REVIEW: APPROVED`
- `STAGE_R_SOURCE_ISSUANCE_REVIEW: REJECTED`

Approval covers only this repository-retained prepared source package. It does
not approve protected issuance, staging, operator authorization, installation,
budget amendment, reconciliation, replay, admission, promotion, merge, or push.
