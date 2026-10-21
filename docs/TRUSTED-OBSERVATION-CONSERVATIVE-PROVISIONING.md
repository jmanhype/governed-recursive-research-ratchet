# Conservative-genesis provisioning proposal — no execution authority

Prepared only; `/Library/GRRR/accounting` has NOT been created. Installed QEMU,
bootstrap, runtime inventory and guest v3 artifacts are unchanged.

## Exact prepared objects

- Standalone `scripts/conservative-genesis`:
  `c411ab2a67ae924eca90889b60306a4a9582b9edc69e029e31770bb321474635`
- Canonical plan `docs/evidence/trusted-observation/conservative-genesis/plan.json`:
  `0fe2d1cb4e989c75640497194e3efe0bb9a365a3d755a619eaae1c94685f306a`
- Receipt: `9f64395bec815a6bb2281d3b5d96d2356899138b1929b0a9881c16483c486dde`
- SQLite bytes: `9fe4000c0c45b83cc818c29640e561167c34bd663abc26267e2a1b009f878234`
  at this worktree's `.tmp-sr_pm/conservative-genesis-v2/budget.sqlite`.

The database contains 259 original hash-bound artifacts, including original
snapshots/events and all twelve attempt manifests. Nine report nonzero exit,
three zero; ten are earlier/nonaccepted, NOT ten failed exits.

## Schema and authority

Canonical receipt schema is the committed `receipt.json`: version 1,
`schema=conservative-genesis`, campaign/store/proposal hashes, all three profiles,
`unresolved_history=true`, `complete_migration=false`, `release_authorized=false`,
`reset_allowance=false`, `execution_gate=blocked`,
`historical_campaign_stop=null`, `migration_safety_stopped=1`,
POC/milestone encumbrances and `milestone_includes_poc=true`.
Campaign/store identities are deterministic proposal-derived digests, not
fabricated historical identities.

`state` enforces stopped=1; triggers deny inserts into `reservations`, updates
and deletion of stop state. Reservations remain empty: legacy event/run/fallback
keys exist only as evidence keys. `artifacts` retains bytes and hashes;
`legacy_events` retains metadata and source references; `metadata` retains the
exact proposal and receipt. Original measurements, including fractional
microseconds, remain non-settlement evidence. No meter receipt, charge or epoch
is invented. POC is INCLUDED in the cumulative milestone encumbrance; the two
full-ceiling admission barriers are not independent additive historical charges.

All new reservations, including zero-cost requests, fail. The installed
`active.json` intentionally uses a distinct incompatible conservative schema:
the existing complete-migration runtime rejects it before dispatch for every
profile/stage. This is a quarantine baseline, not a usable runtime allowance.
The existing complete-migration installer is untouched and cannot accept this
receipt. No stop-clear, hold-release or conversion command exists.

## Installation / failure boundaries

Parent must independently install and hash the standalone bootstrap at
`/Library/GRRR/bootstrap/conservative-genesis`, root:wheel 0444, and the exact
plan at `/Library/GRRR/bootstrap/conservative-genesis-plan.json`, root:wheel 0444.
Use the pinned canonical CLT interpreter, not mutable checkout imports.
Installer checks absolute bootstrap identity, isolated/no-site/no-bytecode
invocation, interpreter hash, root-owned safe ancestors and absence of ACLs;
it validates the stdlib JSON origin. It imports no repository code.

The plan has no approval to execute. Install mode additionally requires an
exact digest-bound provisioning-only authorization string. It locks the existing
root-controlled `/Library/GRRR` directory using nonblocking flock, checks the
15 GB post-copy free-space floor, rejects any existing accounting path (including
partial state or symlink), hashes the SAME opened source bytes it copies,
and verifies SQLite integrity, raw artifact inventory, receipt and event bindings.
Prepared input size is capped at 128 MiB; receipt/plan at 64 KiB.

Proposed output: root:wheel `/Library/GRRR/accounting` 0755, database/receipt/active
files 0444, no symlinks, no evaluator write permission. Active binds exact
database device/inode/hash, receipt hash, plan hash and campaign/store IDs.
Files are fsynced; active is written last; parent directory is fsynced. A failure
leaves a partial inactive or conservatively blocked store; retry refuses all
existing state. No destructive rollback, repair or silent reset is performed.
Future recovery requires independent review and explicit authorization.

Nonprivileged tests use real SQLite connections, concurrent access and reopen
cycles across three profiles and two stages. They prove rejection including
zero-cost, SQL stop-change denial, actual existing runtime schema rejection,
hash read-back and existing-preparation refusal. They do not claim privileged
installation or service-identity behavior has been exercised.

## Exact authorization requested

“Authorize provisioning ONLY of conservative-genesis plan
`0fe2d1cb4e989c75640497194e3efe0bb9a365a3d755a619eaae1c94685f306a`,
using bootstrap `c411ab2a67ae924eca90889b60306a4a9582b9edc69e029e31770bb321474635`,
to install the immutable blocked evidence baseline. Keep unresolved history,
stopped=1, and all profiles/stages blocked. Do not execute QEMU, clear stops,
release holds, create fresh allowance or approve complete migration.”

After independent review, authorization and bootstrap installation, parent-only:

```sh
/usr/bin/env -i PATH=/usr/bin:/bin LC_ALL=C /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/bin/python3.9 -I -S -B /Library/GRRR/bootstrap/conservative-genesis install /Library/GRRR/bootstrap/conservative-genesis-plan.json 0fe2d1cb4e989c75640497194e3efe0bb9a365a3d755a619eaae1c94685f306a INSTALL_BLOCKED_CONSERVATIVE_GENESIS:0fe2d1cb4e989c75640497194e3efe0bb9a365a3d755a619eaae1c94685f306a
```

AWAITING_PARENT_IDENTITY_RUN — staged only, not invoked.
Historical reconciliation gaps and all ten guest controls remain blocked.
