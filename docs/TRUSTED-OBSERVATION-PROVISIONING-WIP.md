# Provisioning-only staging — GRRR-gu87

No installation, root invocation, QEMU invocation, guest execution, or ten-control
run occurred. This checkpoint is incomplete and requires independent review.
The operator authorized provisioning, not execution.

## Staged implementation

`scripts/provision-trusted-host` is stdlib-only until it has copied and read back
the complete approved source inventory. It must first be independently installed
and verified at `/Library/GRRR/bootstrap/provision-trusted-host`; invoking the
checkout copy as root is rejected. It validates a root-owned read-only plan
against a caller-supplied, independently reviewed SHA-256. Every input is bounded
and hashed from opened regular no-follow files; every output is exclusive-create
or identical read-back, never destructive overwrite. Partial accounting installs
require explicit recovery, not automatic reset.

Canonical interpreter remains:
`/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/bin/python3.9`.
It is Python 3.9.6, SHA-256
`5c5950c62eee5fd227a67e4bdfcde81c9add59799bba0949635f3d5ba9661c26`.
It is not relocated. Python 3.9 does not support the newer `-P` switch; `-I`
already excludes current/script paths, and `-S -B` excludes site initialization
and bytecode writes. Installer checks exact version/path/hash, root ownership,
ancestors, ACLs and initial stdlib search origins. Invocation must use an empty
environment with only fixed PATH/locale.

Expected paths:
- `/Library/GRRR/bootstrap/{provision-trusted-host,trusted-root-bootstrap}`
- `/Library/GRRR/bootstrap/provisioning-plan.json` (independently reviewed input)
- `/Library/GRRR/bootstrap/provisioning-readback.json` (output, never execution approval)
- `/Library/GRRR/snapshots/provisioned/` (complete source tree)
- `/Library/GRRR/qemu-reviewed/{installation.json,build-record.json,bin/,lib/,data/}`
- `/Library/GRRR/accounting/{active.json,migration.json,launch.lock,<store-id>/budget.sqlite}`

QEMU validation uses the existing immutable absolute-dependency verifier.
Accounting migration copies only a hash-bound, already reconciled database,
preserving reservations, meter receipts, unresolved holds and stops. It creates
no tables/allowances or guessed usage. The supplied database must already contain
the reviewed campaign/store/history identity. It validates that identity before
publishing active.json with actual device/inode. Existing campaigns are validated,
never replaced. The genesis/history receipt excludes its containing database
hash to avoid a self-referential hash cycle; the separately approved plan binds
both receipt and database bytes. Campaign flock excludes concurrent migration
and launch. Execution and runtime-loading flags remain false.

## Current blockers — do not fill with guessed values

`scripts/review-provisioning-inputs` inventories exact accepted synthetic/offline
JSON evidence and retains discovered timing/usage values with JSON locations;
it does not sum potentially overlapping values or infer absent costs as zero.
The output in `docs/evidence/trusted-observation/provisioning-wip/` marks cumulative
review duration, earlier failed attempts, unresolved holds/stops and settlement
reconciliation incomplete. No migrated database or allowance was manufactured.

The same receipt hashes installed QEMU executable, formula, Homebrew receipt and
SBOM. This is a **poured Homebrew bottle**, not a new upstream build. Formula
inspection does not establish `--disable-modules` or `--disable-plugins`.
Rewriting LC_LOAD paths and signing alone does not prove GIO/plugin/module
runtime loading safe. Therefore no absolute closure/build-record provenance was
fabricated; current verifier correctly rejects this unproven installation.
An independent reviewed method to disable/pin all such paths remains necessary.
No QEMU invocation was used to inspect it.

Installed-state UID/restart/concurrency/replacement-denial hooks and final composed
execution-profile digest remain blocked until genuine installation and accounting
inputs exist. Existing nonprivileged tests are not substituted for these proofs.
The ten guest controls remain unauthorized and not-run.

## Parent command boundary

AWAITING_PARENT_IDENTITY_RUN

After independent installer review/installation **and only once a complete plan
has its own reviewed digest**, the provisioning-only invocation template is:

```text
/usr/bin/env -i PATH=/usr/bin:/bin LC_ALL=C /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/bin/python3.9 -I -S -B /Library/GRRR/bootstrap/provision-trusted-host /Library/GRRR/bootstrap/provisioning-plan.json <REVIEWED_PLAN_SHA256>
```

This is intentionally not represented as currently runnable: the plan digest,
immutable QEMU closure, and reconciled accounting database are absent. Do not
substitute an automatically computed unreviewed plan hash. No execution
authorization is requested.

## Verification

Both Python unit suites: 84/84. Explicit py_compile checks passed under both.
`pvg verify` explicit paths passed. Source host inventory and v3 guest artifacts
are unchanged; new provisioning code is separately pinned and not added to the
runtime execution inventory. Provisioner digest:
`e34bd0bc92af433bba6757f66c892ea9983c778cd9096b8da6108b6a41e32d36`.
