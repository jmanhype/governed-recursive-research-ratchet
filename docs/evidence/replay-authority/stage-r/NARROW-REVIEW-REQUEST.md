# GRRR-z3w9 Stage R narrow re-review request

## Exact scope

Review only the correction for the initial Stage R rejection:

1. an existing leaf symlink must reject even with `exists=False`;
2. the sandbox root must reject as a file target;
3. all refreshed identities must match.

Confirm the already reviewed package properties remain unchanged:

- eight exact roles and destinations;
- distinct pinned hashes;
- deterministic bundle regeneration;
- Stage N unresolved holds/ceilings;
- Stage O unissued replay block;
- exact stopped/empty SQLite behavior;
- uncertainty preservation;
- entrypoint refusal;
- `prepared-not-issued` status and false authority.

Do not access or mutate `/Library/GRRR`; do not edit files; do not stage/install
protected records, amend budget, reconcile, execute replay, admit, promote,
mutate production, merge, or push.

## Corrected identities

- `research/replay_successor_source_issuance.py`
  SHA-256 `b6ac85b0cbc8a9ef4a6678b76cd81cc77e8a9a35196720898fef423b2fd98dc3`
- `scripts/prepare-replay-successor-v4-source-issuance`
  SHA-256 `d6d7a0bbf594c3fda3570eb149275ee5eafce67b7241fb436d10761c6b822e13`
- `tests/unit_replay_successor_source_issuance.py`
  SHA-256 `fcee7a5bac0325754a39482b44578948b0451124c0b7dcb2d93a56b03d8ee534`
- `docs/evidence/replay-authority/stage-r/SOURCE-BUNDLE.json`
  SHA-256 `38cc6f7904cf130e616772c98d1b526785763871dd6f498d1f02bb8af916e4e4`
- `docs/evidence/replay-authority/stage-r/source/replay-successor-v4-protected_preflight.py`
  SHA-256 `8a288bf13c2ccfffb695fdc350b28b1d99e5a368e8ceb070fcd1c69b82983171`
- `docs/evidence/replay-authority/stage-r/FOCUSED-HOMEBREW-3.14.log`
  SHA-256 `d12d98bf33405c1fda40957aa0e23e05e14edccbcaf0b3c5f6d9724b98aefade`
- `docs/evidence/replay-authority/stage-r/FOCUSED-MINICONDA-3.12.log`
  SHA-256 `a813efe3a541f351015a038bb4a4204886e5ad96a104fad75935c463e69ebaa6`
- `docs/evidence/replay-authority/stage-r/FULL-HOMEBREW-3.14.log`
  SHA-256 `5021b8e4e37f6a1c0ee764be64dc46860a7fcaf6051b8076128ec3ad0b56540f`
- `docs/evidence/replay-authority/stage-r/FULL-MINICONDA-3.12.log`
  SHA-256 `04ca1386cde34d7946013685a9fdfb7c81e98ee0bc815cde4d097ee61cbc363f`

Canonical role identity:

`2fc2821d0301718e94072f46094b959131598c7233b158dead64fb7a0b46cbff`

The installer-entrypoint hash is exactly:

`94b37112fc3b3146078b6edd0cf80d5e845f1cc83543344d79400d144d453dbc`

## Required commands

```sh
/opt/homebrew/bin/python3 -I -B -W error::ResourceWarning -m unittest discover -s tests -p 'unit_replay_successor_source_issuance.py' -v
/Users/speed/miniconda3/bin/python -I -B -W error::ResourceWarning -m unittest discover -s tests -p 'unit_replay_successor_source_issuance.py' -v
scripts/prepare-replay-successor-v4-source-issuance > /tmp/grrr-stage-r-narrow.json
cmp docs/evidence/replay-authority/stage-r/SOURCE-BUNDLE.json /tmp/grrr-stage-r-narrow.json
```

## Required verdict

Return exactly one:

- `STAGE_R_NARROW_REWORK_REVIEW: APPROVED`
- `STAGE_R_NARROW_REWORK_REVIEW: REJECTED`

Approval covers only this corrected repository-retained prepared source package.
It does not approve protected issuance, staging, operator authorization,
installation, budget amendment, reconciliation, replay, admission, promotion,
merge, or push.
