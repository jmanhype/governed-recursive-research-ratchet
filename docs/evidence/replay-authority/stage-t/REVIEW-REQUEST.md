# Stage T staging preparation — independent review request

## Scope

Review the Stage T parent-mediated staging script and
operator-authorization record format for:

1. Correct binding to Stage S record and package hashes.
2. Authorization grants only protected_staging; installation remains separate.
3. Authorization hash, authorized_by, and authorized_at are validated.
4. All eight source roles and hashes are enforced.
5. Staging script verifies source hashes before copy.
6. Staging script uses O_EXCL, correct modes, and fsync.
7. Staging script refuses existing destinations, symlinks, and /Library in
   sandbox mode.
8. Outcome record binds authorization digest and all 8 staged files.
9. Validator rejects empty authority, missing flags, wrong hashes, duplicates,
   wrong roots, and installed outcome.
10. No `/Library/GRRR` access or mutation in this stage.

## Files to review

- `research/replay_successor_staging.py`
- `scripts/stage-replay-successor-v4-sources`
- `tests/unit_replay_successor_staging.py`

## Commands to independently rerun

```bash
/opt/homebrew/bin/python3 -I -B -m unittest discover -s tests -p 'unit_replay_successor_staging.py' -v
/Users/speed/miniconda3/bin/python -I -B -m unittest discover -s tests -p 'unit_replay_successor_staging.py' -v
```

Sandbox smoke:
```bash
SB=$(mktemp -d)
./scripts/stage-replay-successor-v4-sources --sandbox-root "$SB/bootstrap"
./scripts/stage-replay-successor-v4-sources --sandbox-root "$SB/bootstrap"  # must fail
./scripts/stage-replay-successor-v4-sources --sandbox-root /Library/test  # must fail
```

## Expected hashes

- Validator SHA-256:
  `504020a015e7f273154f0a1cbacd948f19e2a8791c054db67ecb84d0d76e66cf`
- Script SHA-256:
  `332bae97c8f4d8797154a95e30988958c52b9b83898f822b11add5e01a2e44ed`
- Tests SHA-256:
  `f936e0e4168992d1be5e857b322c5593e9ece21b36eec2871908f5bb51af68b5`

## Boundary

This review covers only the repository-retained Stage T preparation. It does
not approve protected staging execution, installation, budget amendment,
reconciliation, replay, admission, promotion, merge, or push.
