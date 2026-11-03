# GRRR-z3w9 Stage R absent-leaf rework — fresh differently scoped review request

## Exact scope

Review only the revised absent-leaf/symlink/root-type behavior and refreshed
identities. This is a new review brief, not a retry of the prior package review.

Required behavior:

1. a genuinely absent final leaf succeeds only when `exists=False`;
2. an existing final symlink always rejects, including a dangling symlink;
3. intermediate absence rejects;
4. sandbox-root-as-file rejects;
5. sandbox-root-as-absent rejects;
6. all already reviewed Stage R package semantics remain unchanged.

Do not review unrelated architecture. Do not access or mutate `/Library/GRRR`.
Do not stage or install protected records, amend the budget, reconcile, execute
replay, admit, promote, mutate production, merge, or push.

## Corrected identities

- `research/replay_successor_source_issuance.py`
  SHA-256 `8a71e1d5020bafb75236d81abdf0bc79a2c236422a6c3c11ed43900fe7d755b4`
- `scripts/prepare-replay-successor-v4-source-issuance`
  SHA-256 `d6d7a0bbf594c3fda3570eb149275ee5eafce67b7241fb436d10761c6b822e13`
- `tests/unit_replay_successor_source_issuance.py`
  SHA-256 `e9aac58ccf0d0ad0f2e483cb0335d4eadaa1ffebefc929df17a1adb19f08b759`
- `docs/evidence/replay-authority/stage-r/source/replay-successor-v4-protected_preflight.py`
  SHA-256 `0e09ccc6f995e24ab983489755df6a14028c154a99b84811b95d6ea95bf0946f`
- `docs/evidence/replay-authority/stage-r/SOURCE-BUNDLE.json`
  SHA-256 `31cb9b8ee538ac22553927fe5f8006c47461073578f9d025f3ddb892ed3ca84c`

Canonical role identity:

`b6354127a7552b628506c25dc7eee27c8ecb371f56bf565a63dd247b31445084`

## Logs

- `docs/evidence/replay-authority/stage-r/FOCUSED-HOMEBREW-3.14.log`
  SHA-256 `b643cccc6a5dd2734ed0468779c19313ff5c6033d59e76284553ecf13ee54337`
- `docs/evidence/replay-authority/stage-r/FOCUSED-MINICONDA-3.12.log`
  SHA-256 `4f9fa21b6c8760b5e30815798a8f51d289da02861eb37f1a053521ffa68c04e3`
- `docs/evidence/replay-authority/stage-r/FULL-HOMEBREW-3.14.log`
  SHA-256 `3e986d1e0febab3cdb779ecdb88dd773e0208e7eff1709528e0b1f08da51cddc`
- `docs/evidence/replay-authority/stage-r/FULL-MINICONDA-3.12.log`
  SHA-256 `7d18fcc243432d81ade5b5c1d00f2322f1953dadf53df29646fb57c64d2f70f8`

## Required commands

```sh
/opt/homebrew/bin/python3 -I -B -W error::ResourceWarning -m unittest discover -s tests -p 'unit_replay_successor_source_issuance.py' -v
/Users/speed/miniconda3/bin/python -I -B -W error::ResourceWarning -m unittest discover -s tests -p 'unit_replay_successor_source_issuance.py' -v
scripts/prepare-replay-successor-v4-source-issuance > /tmp/grrr-stage-r-absent-review.json
cmp docs/evidence/replay-authority/stage-r/SOURCE-BUNDLE.json /tmp/grrr-stage-r-absent-review.json
```

Independently probe, in a temporary sandbox:

- truly absent file/directory target with `exists=False`;
- existing directory symlink with `exists=False`;
- dangling final symlink with `exists=False`;
- absent intermediate directory;
- root as file;
- root as absent.

## Required verdict

Return exactly one:

- `STAGE_R_ABSENT_LEAF_REVIEW: APPROVED`
- `STAGE_R_ABSENT_LEAF_REVIEW: REJECTED`

Approval covers only this corrected repository-retained prepared source package.
It does not approve protected issuance, staging, operator authorization,
installation, budget amendment, reconciliation, replay, admission, promotion,
merge, or push.
