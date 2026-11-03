# GRRR-z3w9 Stage Q containment rework — revised independent review request

## Exact revised brief

Review only whether the operator-authorized containment corrections close the
three narrow-review blockers without weakening the already corrected installer
behavior:

1. lexical canonicalization/validation occurs before every filesystem metadata
   call;
2. `..`, absolute escapes, symlinked sandbox roots, and symlinked ancestors are
   rejected;
3. every `/Library/GRRR` path—and a protected ancestor such as `/Library`—is
   rejected without stat/lstat access;
4. syscall guards prove zero protected metadata access;
5. exact SQLite inventory, uncertainty dominance, publication-failure
   preservation, and checkout refusal remain intact.

Do not review unrelated architecture. Do not access or mutate `/Library/GRRR`.
Do not stage or install protected records, amend the budget, reconcile, execute
replay, admit, promote, mutate production, merge, or push.

## Base state

- Story HEAD: `5c130a02958042975c8522f71e134f19627c999d`
- Prior narrow rejection:
  `STAGE_Q_NARROW_REWORK_REVIEW: REJECTED`
- Operator explicitly authorized this fresh revised-brief review.

## Files and identities

- `research/replay_successor_installer.py`
  SHA-256 `1902290a64247a8c60ec477c7fda230d33b50c8f491c7660c422c398e4fdd1b9`
- `scripts/install-replay-successor-v4`
  SHA-256 `7ee2728f99408b2f83b6626fe61c187d91d3b6d04b386e026e68fdc7abcaaaa3`
- `tests/unit_replay_successor_installer.py`
  SHA-256 `dc9b898f96f9247cb09d92d0a0a11b21aeae7743aab82c30f134c094de4002fa`
- `docs/evidence/replay-authority/stage-q/CONTAINMENT-REWORK-REPORT.md`
  SHA-256 `ba52a3f49ef66279164f50dd47af93d4f3f537f1d9d6b72a730d7a5ee74a5e44`
- `docs/evidence/replay-authority/stage-q/FOCUSED-HOMEBREW-3.14.log`
  SHA-256 `3c794984ed1d11e1cb11c3559d56be1af42f2729da77e7e67649959373c4d4d5`
- `docs/evidence/replay-authority/stage-q/FOCUSED-MINICONDA-3.12.log`
  SHA-256 `5242b5973c161e0fe22f863317027f44057083506386b89f6e93e26dd07df305`
- `docs/evidence/replay-authority/stage-q/FULL-HOMEBREW-3.14.log`
  SHA-256 `b37ea2220aba237b9d71eb6cbadfd1239b343b579801000549140c43fe9b811c`
- `docs/evidence/replay-authority/stage-q/FULL-MINICONDA-3.12.log`
  SHA-256 `4ec07c9ddf51068b4f0a086e25cdfed0a562bfe2c994a9d278c9342bf0237939`

## Required independent commands

```sh
/opt/homebrew/bin/python3 -I -B -W error::ResourceWarning -m unittest discover -s tests -p 'unit_replay_successor_installer.py' -v
/Users/speed/miniconda3/bin/python -I -B -W error::ResourceWarning -m unittest discover -s tests -p 'unit_replay_successor_installer.py' -v
```

Also inspect `_safe_sandbox_path` and independently probe, in temporary
directories only:

- `/Library` and `/Library/GRRR` lexical overlap cases with `os.stat` and
  `os.lstat` guarded to fail before real protected access;
- `sandbox/path/../outside`;
- a supplied sandbox root beneath a symlinked ancestor;
- a source/target ancestor symlink;
- a final symlink;
- an absolute escape;
- unexpected SQLite object/DDL injection;
- failure after receipt publication, active publication, directory sync, and
  postflight.

## Required verdict

Return exactly one:

- `STAGE_Q_CONTAINMENT_REWORK_REVIEW: APPROVED`
- `STAGE_Q_CONTAINMENT_REWORK_REVIEW: REJECTED`

Approval covers only this repository-retained containment rework. It does not
approve protected source issuance, protected staging, operator authorization,
protected installation, budget amendment, reconciliation, replay, admission,
promotion, merge, or push.
