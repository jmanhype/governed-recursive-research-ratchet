# GRRR-z3w9 Stage Q containment alias narrow review request

## Exact scope

This is the one permitted retry of the operator’s revised containment brief.
Review only the correction of the two revised-brief rejection findings:

1. repeated leading-root separators such as `//Library`;
2. unrelated `/Library/...` ancestors that would otherwise require
   `lstat("/Library")`.

Confirm they reject lexically before any stat/lstat call, without weakening:

- `..` and absolute-escape rejection;
- symlinked sandbox-root/ancestor rejection;
- exact SQLite inventory;
- uncertainty dominance;
- publication-failure preservation;
- checkout refusal.

Do not review unrelated architecture. Do not access or mutate `/Library/GRRR`.
Do not stage/install protected records, amend budget, reconcile, execute replay,
admit, promote, mutate production, merge, or push.

## Corrected identities

- `research/replay_successor_installer.py`
  SHA-256 `c1b846576f38a9344ed92f74f4bfdff3be34c6ed0a45bed57e0b76194cb334c6`
- `scripts/install-replay-successor-v4`
  SHA-256 `7ee2728f99408b2f83b6626fe61c187d91d3b6d04b386e026e68fdc7abcaaaa3`
- `tests/unit_replay_successor_installer.py`
  SHA-256 `26699b0839e2a7ebd0c6d20eb6aefb9d8c9ce4f26067af5ef8ae0958fadb138c`
- `docs/evidence/replay-authority/stage-q/FOCUSED-HOMEBREW-3.14.log`
  SHA-256 `4f541a542f4a64b4489c4f86226083daeb194077ec3ddd452dde81bad284c58d`
- `docs/evidence/replay-authority/stage-q/FOCUSED-MINICONDA-3.12.log`
  SHA-256 `d0edeba481a62f4b6412abfce3982079713ac40dddbf8942c82dd0f1f1e18c66`
- `docs/evidence/replay-authority/stage-q/FULL-HOMEBREW-3.14.log`
  SHA-256 `554a736a7dfe4210866b653dd94813b62c483aff2ec7b991a441c8ea5f816660`
- `docs/evidence/replay-authority/stage-q/FULL-MINICONDA-3.12.log`
  SHA-256 `6f9fef275ca2ed0b77f909ca9cca454dab7f45a7a6b8c33977bfa4a0a31e80cf`

## Required commands and probes

```sh
/opt/homebrew/bin/python3 -I -B -W error::ResourceWarning -m unittest discover -s tests -p 'unit_replay_successor_installer.py' -v
/Users/speed/miniconda3/bin/python -I -B -W error::ResourceWarning -m unittest discover -s tests -p 'unit_replay_successor_installer.py' -v
```

Independently probe, with all stat/lstat replaced by fail-closed mocks:

- `Path("//Library/GRRR/x")` with `Path("//Library")`;
- `Path("//Library/unrelated/x")` with `Path("//Library/unrelated")`;
- `Path("/Library/unrelated/x")` with `Path("/Library/unrelated")`;
- `Path("/Library/GRRR/x")` with `Path("/Library")`.

No real `/Library` or `/Library/GRRR` metadata access is permitted.

## Required verdict

Return exactly one:

- `STAGE_Q_CONTAINMENT_ALIAS_REVIEW: APPROVED`
- `STAGE_Q_CONTAINMENT_ALIAS_REVIEW: REJECTED`

Approval covers only this repository-retained containment correction. It does
not approve protected source issuance, staging, operator authorization,
installation, budget amendment, reconciliation, replay, admission, promotion,
merge, or push.
