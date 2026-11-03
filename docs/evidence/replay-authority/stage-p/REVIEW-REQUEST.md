# GRRR-z3w9 Stage P independent review request

## Exact scope

Review only the design-only future v4 installer/authorization contract source,
emitter, tests, generated contract, focused/full logs, and report. Do not access
or mutate `/Library/GRRR`. Do not build or execute an installer, stage protected
records, amend a budget, reconcile, execute replay, admit, promote, mutate
production, merge, or push.

## Base state

- Story HEAD: `2051e7dd5378db6ed4c2057dd50aa3287bfe3525`
- Stage N package SHA-256:
  `e349cc8349f62072af94f8b82ee1aafa1648db22270a77b9dba278469d305a48`
- Stage O package SHA-256:
  `283918e2c1df4b9b25b79a26be90de9e5d20ea8c195b058a5b827c474872553b`

## Files and identities

- `research/replay_successor_installer_contract.py`
  SHA-256 `9aa834c18846a99290713cdf80cc20b917eddfb2bcd2c5d502d0a4afc742efea`
- `scripts/show-replay-successor-installer-contract`
  SHA-256 `dfa14c0e15869b8e2a508aad5d5b5ffea04719869fe4a586f37fe95a00029ea7`
- `tests/unit_replay_successor_installer_contract.py`
  SHA-256 `f4b6614e432bc3d83ee7fd50c3d19a4b9e14fc49343149c38dbbdc4535201038`
- `docs/evidence/replay-authority/stage-p/CONTRACT.json`
  SHA-256 `0c4f800bb4b1efd7f831094123e4afd082fa1d18eb8f32bf3a1c8b1649ec8267`
- `docs/evidence/replay-authority/stage-p/FOCUSED-HOMEBREW-3.14.log`
  SHA-256 `cb83677cac883dc8b14d5f3e8975e86747ce22e5bdc261ebf21891cff13c394d`
- `docs/evidence/replay-authority/stage-p/FOCUSED-MINICONDA-3.12.log`
  SHA-256 `c2f4795fd3916f39ff31ab85c4ae10c3b31ea93a1ba1843aded9170d74eee514`
- `docs/evidence/replay-authority/stage-p/FULL-HOMEBREW-3.14.log`
  SHA-256 `fa536d8a38f292694d32477d6830cb1b15b9e8071914ab62bf5421b2a57922fb`
- `docs/evidence/replay-authority/stage-p/FULL-MINICONDA-3.12.log`
  SHA-256 `c0fb077741ab9f4a6540f77cb6d3612d0fe917252e88506f3eeda378c9b30013`

## Independent commands to rerun

From the story worktree:

```sh
/opt/homebrew/bin/python3 -I -B -m unittest discover -s tests -p 'unit_replay_successor_installer_contract.py' -v
/Users/speed/miniconda3/bin/python -I -B -m unittest discover -s tests -p 'unit_replay_successor_installer_contract.py' -v
scripts/show-replay-successor-installer-contract > /tmp/grrr-stage-p-review.json
cmp docs/evidence/replay-authority/stage-p/CONTRACT.json /tmp/grrr-stage-p-review.json
```

## Review questions

1. Does the module use only in-memory/repository data and avoid filesystem,
   SQLite, process, VM, credential, network, and protected-path access?
2. Does it bind the exact committed Stage N/Stage O packages and predecessor
   identities rather than mutable or alternate state?
3. Are installer, plan, review, authorization, and source-role hashes correctly
   unissued rather than fabricated?
4. Are the eight source roles and exact future protected artifact paths complete
   and unambiguous for a later implementation/review slice?
5. Does the design require an exclusive parent, one-shot install, read-only
   predecessor, fresh sibling target, refuse-no-retry failure handling, new-store-only
   rollback, and postflight?
6. Does operator authorization remain external and distinct from plan/review
   receipts?
7. Does a valid future authorization shape still authenticate nothing and grant
   no installation authority in this design?
8. Does the contract require a separate budget amendment while denying budget,
   reconciliation, replay, execution, admission, promotion, merge, and push
   authority?
9. Do tests reject basis tampering, fabricated hashes, missing/extra closure
   roles, unsafe failure/rollback modes, authority injection, gate
   self-certification, reused receipts, and malformed authorization fields?
10. Does implementation avoid weakening any existing accounting/replay gate?

## Required verdict

Return exactly one:

- `STAGE_P_INSTALLER_CONTRACT_REVIEW: APPROVED`
- `STAGE_P_INSTALLER_CONTRACT_REVIEW: REJECTED`

Approval covers only this design-only WIP contract. It does not approve
installer implementation, exact protected bytes, protected access or staging,
budget amendment, reconciliation, replay, admission, promotion, merge, or push.
