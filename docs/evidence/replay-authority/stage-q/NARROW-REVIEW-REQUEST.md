# GRRR-z3w9 Stage Q narrow re-review request

## Exact scope

Review only the corrections for the three initial blockers and regenerated
installer evidence. Do not repeat unrelated architecture review. Do not access
or mutate `/Library/GRRR`; do not edit files; do not stage/install protected
records, amend budget, reconcile, execute replay, admit, promote, mutate
production, merge, or push.

## Corrected identities

- `research/replay_successor_installer.py`
  SHA-256 `53aab09e067a07629df9b41b72e759d331c96dd84520a6ba36a4e2fc2c95e161`
- `tests/unit_replay_successor_installer.py`
  SHA-256 `6bb1a92925afeeb290b7849c51261e28371e2406a4ebdda71f63eb3c1e0476f6`
- `docs/evidence/replay-authority/stage-q/FOCUSED-HOMEBREW-3.14.log`
  SHA-256 `8b71c40c22d6785a96a24c175d4d5e8161104bf7191f948de8eca71d506de1a6`
- `docs/evidence/replay-authority/stage-q/FOCUSED-MINICONDA-3.12.log`
  SHA-256 `afa057206ed1986ebfc7f641864f574a287e8194b81ee2038bb8137073811edd`
- `docs/evidence/replay-authority/stage-q/FULL-HOMEBREW-3.14.log`
  SHA-256 `ca6c3bccae090d689c59ed360bc9cbb155d7653fc34961825ff8809ae80a9865`
- `docs/evidence/replay-authority/stage-q/FULL-MINICONDA-3.12.log`
  SHA-256 `b630500b2b6a157b5706c2b22539dc16773ccb0047435cf105f83056af4ab481`

`scripts/install-replay-successor-v4` is intentionally unchanged:
`7ee2728f99408b2f83b6626fe61c187d91d3b6d04b386e026e68fdc7abcaaaa3`.

## Required checks

1. Confirm explicit sandbox-root containment rejects `/Library/GRRR` lexically
   before source-file access and rejects symlinked ancestors/final components.
2. Confirm exact SQLite object inventory and table DDL are verified, including
   rejection of an injected extra table.
3. Confirm `uncertain.json` dominates verification even when a success receipt
   and active binding were already published.
4. Confirm injected failures at receipt write, active write, directory sync,
   and postflight each retain uncertainty and never verify as success.
5. Rerun both focused installer suites and expect 34/34 each.
6. Confirm no unrelated Stage Q or durability semantics changed from the
   initially reviewed package.

## Required verdict

Return exactly one:

- `STAGE_Q_NARROW_REWORK_REVIEW: APPROVED`
- `STAGE_Q_NARROW_REWORK_REVIEW: REJECTED`

Approval covers only this corrected repository-retained WIP. It does not
approve exact protected source issuance, protected staging, operator
authorization, protected installation, budget amendment, reconciliation,
replay, admission, promotion, merge, or push.
