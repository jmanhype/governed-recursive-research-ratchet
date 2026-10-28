# GRRR-z3w9 Stage N independent review request

## Exact scope

Review only the candidate version-4 replay-successor authority contract,
emitters, tests, generated contract, summaries, logs, and report. Do not access
or mutate `/Library/GRRR`. Do not implement or install a runtime store,
reconcile spendability, execute replay, admit, promote, mutate production,
merge, or push.

## Base state

- Story HEAD: `c6fcc8bb611eab2c2f02b14999cdfe45cf44b02d`
- Approved Stage M package SHA-256:
  `c65aedd7f7a2f861ef5593ba9705981ca42508bf6f3f12a4f23787381d12df0b`
- Stage M finding: no existing binding is both replay-preflight-valid and
  writable.

## Files and identities

- `research/replay_successor_contract.py`
  SHA-256 `4bc53b4fc0431bce21aa4a3927423be13c46435dd854a246fcd45264071c4786`
- `scripts/show-replay-successor-contract`
  SHA-256 `068fccdc9e313ebd9f211a6d0c4276be9c93a70d96a5d811972103cdcbfce7f1`
- `scripts/emit-replay-successor-contract`
  SHA-256 `c6eebfc5e7e5feaa8029a6bfc46901e7a01c1996fa06f0f1a59226fd575f71cf`
- `tests/unit_replay_successor_contract.py`
  SHA-256 `a97aca88c9e71707b16680e5665885f6ed1f2f54aae2096028032e42389c6a0a`
- `tests/unit_spendability_stage_c.py`
  SHA-256 `061018f5ea6de0805fb886153446ea12778fab43a8412913b87f79bc3e062c15`
- `docs/evidence/replay-authority/stage-n/CONTRACT.json`
  SHA-256 `8a3dd1ea22841abf98ba2947f865f6ac169cc90998848a5a84906d99593e4cb3`
- `docs/evidence/replay-authority/stage-n/SUMMARY.json`
  SHA-256 `f0dccbf60fdcabe4239b313fc6eb62d4d14a5a1fa83711c1a0e73ee78b420169`
- `docs/evidence/replay-authority/stage-n/FOCUSED-HOMEBREW-3.14.log`
  SHA-256 `bd6c792cbf2be944d9d529dacedb8d0c12769569ce43fd62b24b665a5998330b`
- `docs/evidence/replay-authority/stage-n/FOCUSED-MINICONDA-3.12.log`
  SHA-256 `35b0a783d53fc4a40a46e1df5b15f4d334c9bf911be3de532bf148cf2b9c6fcf`
- `docs/evidence/replay-authority/stage-n/FULL-HOMEBREW-3.14.log`
  SHA-256 `60d2c18ffb9ba99e6b71c8f221eeb5d8e2aec4b9a00e4114cd2d5caaa2929f87`
- `docs/evidence/replay-authority/stage-n/FULL-MINICONDA-3.12.log`
  SHA-256 `1674ce05383922a82f5094f6a45dbc54c8e1f3dfe7800ec105f1ffb1795748b5`

## Independent commands to rerun

From the story worktree:

```sh
/opt/homebrew/bin/python3 -I -B -m unittest discover -s tests -p 'unit_replay_successor_contract.py' -v
/Users/speed/miniconda3/bin/python -I -B -m unittest discover -s tests -p 'unit_replay_successor_contract.py' -v
scripts/emit-replay-successor-contract > /tmp/grrr-stage-n-review.json
cmp docs/evidence/replay-authority/stage-n/CONTRACT.json /tmp/grrr-stage-n-review.json
```

## Review questions

1. Does the candidate avoid fabricating approval, installer, review,
   authorization, device, or inode identities?
2. Does it preserve predecessor spendability as unresolved and all original
   ceilings as fully encumbered?
3. Does it preserve all three exact unresolved holds without release?
4. Does the proposed successor require an explicit incremental budget amendment
   before any charge?
5. Are the four modes, session/aggregate limits, launch ceiling, and failure-stop
   policy exact and bounded?
6. Does the binding permit only `independent-replay` and remain sibling-scoped?
7. Do authority, admission, promotion, automatic merge, push, replay,
   reconciliation, and predecessor mutation remain false/blocked?
8. Are install failure and rollback fail-closed and scoped away from the
   predecessor?
9. Do the tests reject history resolution, hold release, authority injection,
   fake identities, retry/reset behavior, v3/legacy profiles, and receipt
   tampering?
10. Does the Stage C fixture cleanup remove the prior unclosed SQLite connection
    without changing Stage C semantics?

## Required verdict

Return exactly one:

- `STAGE_N_SUCCESSOR_CONTRACT_REVIEW: APPROVED`
- `STAGE_N_SUCCESSOR_CONTRACT_REVIEW: REJECTED`

Approval covers only this design-only WIP contract. It does not approve runtime
implementation, protected access or installation, spendability reconciliation,
budget amendment, replay, admission, promotion, merge, or push.
