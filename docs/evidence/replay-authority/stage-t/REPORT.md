# Stage T parent-mediated staging script and operator authorization — prepared

## Scope

Stage T prepares the exact parent-mediated staging script and
operator-authorization record format for future v4 protected staging. It does
not access or mutate `/Library/GRRR`, execute protected staging, install
anything, amend a budget, reconcile, execute replay, promote, admit, mutate
production, merge, or push.

## Implementation

Added:

- `research/replay_successor_staging.py` — authorization/outcome validators
- `scripts/stage-replay-successor-v4-sources` — exact staging script
- `tests/unit_replay_successor_staging.py` — 26 tests

## Staging script behavior

Sandbox mode (`--sandbox-root`):
- verifies all 8 source files against pinned SHA-256 hashes
- refuses `/Library` destinations
- checks no symlinked ancestors
- creates staging root with mode `0750`
- writes each file with `O_EXCL`, mode `0440`, and `fsync`
- verifies post-copy hashes
- refuses existing destinations without reset

Protected mode (`--protected`):
- only targets `/Library/GRRR/bootstrap`
- same hash/symlink/atomic verification
- caller is responsible for root privilege
- not executed in this stage

## Operator authorization record

The authorization record binds:

- Stage S record SHA-256:
  `1d27da0d718ac7713f54bc73d4b87d5bcd1ea57f3eb55de1e74b0e2c933a75c9`
- Stage S package SHA-256:
  `4f81a932e0dc1ce58495d925a6c0a574653d897f6bea6c88b8ada1f3ce344ceb`
- Base commit: `19ec1da534174039105a9ceaa532d13c91d8f09c`
- Action: `install-fresh-v4-replay-successor-poc`
- Principal: `operator-via-exclusive-root-parent`

The authorization grants only `protected_staging=true`;
`protected_installation` remains `false` as a separate gate.

## Staging outcome record

Outcome status is `staged-not-installed`. It carries:
- the authorization digest
- all 8 staged file records with exact hashes and byte counts
- the staging root

## Sandbox smoke test

- Staged 8 files with correct hashes and modes (`0440` files, `0750` dir)
- Refused duplicate staging (exit 1)
- Refused `/Library` in sandbox mode (exit 1)

## Verification

- Stage T focused tests:
  - Homebrew Python 3.14.3: 26/26 passed.
  - Miniconda Python 3.12.7: 26/26 passed.
- Full no-guest suites:
  - Homebrew Python 3.14.3: 682/682 passed.
  - Miniconda Python 3.12.7: 682/682 passed.
- `git diff --check`: PASS.

## Remaining gates

- Independent review of this Stage T preparation.
- Operator authorization (fill and sign the authorization record).
- Protected staging execution (`--protected` under root).
- Post-staging verification.
- Installation.
- Budget amendment.
- Reconciliation.
- Replay authorization.
- PM acceptance.
- Merge.
- Push.
