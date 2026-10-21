# Trusted-observation v4 preservation and composed-profile plan — planning only

Basis: clean `story/GRRR-gu87` worktree at
`cab53ad70f43187275b06223d195147c27dd81fb`.

This document approves no root installation, source implementation, accounting
migration, QEMU/guest execution, runtime claim, delivery, or push. The current
executor remains v3-only and cannot consume the live v4 candidate.

## Live input basis

The exact live bytes, sizes, hashes, sqlite integrity result, stop state,
reservation count, v3 rejection results, profile comparison, and free-space
reading are recorded in `INPUT-READBACK.json`. Every digest in that file and in
`PLAN.json` was generated from the referenced live or committed files, not
transcribed by hand.

The actual ISO, receipt, profile, development binding, supervisor, helper, and
all other binaries remain outside Git beneath the main checkout's ignored
`.tmp-sr_pm` tree.

## Future root-controlled preservation

A later, separately authorized root-only operation may create a complete
`/Library/GRRR/trusted-observation/v4/` namespace containing the exact v4 input
ISO, preparation receipt, prepared profile, development binding, supervisor,
and helper identities listed in `PLAN.json`.

Before creating anything, it must verify that every ancestor directory is
root:wheel, non-symlink, ACL-free, and free of group/world write bits. It must
not change system-directory permissions. It must build and verify a complete
private staging namespace first, then expose the final namespace only by an
exclusive atomic operation. If the destination or any expected member exists, the
operation must refuse. Every regular file must be `root:wheel`, mode `0444`,
non-symlink, ACL-free, hard-link count one, and byte-verified against its live
source. Partial state must never be exposed; diagnostics must be retained for
review and automatic retry is prohibited.

Rollback, if separately authorized, may affect only this newly created v4
namespace. It must not alter committed v3 evidence, the immutable QEMU
installation, or conservative accounting history.

## Required source revision before any runtime claim

`research/trusted_execution.py` still hardcodes the v3 profile, ISO, receipt,
and legacy Homebrew QEMU digest. Its current `validate_config` and
`validate_approval` reject the live v4 identities. Before any v4 runtime claim,
a separately reviewed source revision and no-guest tests must:

1. bind profile, ISO, receipt, supervisor, and explicit helper identities to
   the exact live v4 values in `INPUT-READBACK.json`;
2. replace the legacy QEMU digest with the installed immutable manifest digest;
3. reject v3 constants and any partial, mutated, linked, ACL-bearing, or
   incorrectly owned/mode asset;
4. bind all launch inputs to v4 and the installed QEMU closure with no v3 or
   Homebrew fallback;
5. retain dispatch-disabled behavior until every mandatory gate passes.

The current planning evidence does not implement those changes.

## Dispatch-disabled composed v4 record

`PLAN.json` contains a proposed composed v4 record binding:

- exact v4 ISO, receipt, profile, development binding, supervisor, and helper;
- installed immutable QEMU manifest and executable identities;
- conservative accounting active record, database, receipt, stopped state,
  blocked execution gate, and zero reservations;
- unchanged resource, timeout, output, IPC, workspace, networking, sharing,
  paid-dispatch, and dispatch-disable limits.

The conservative accounting state is an explicit blocker and unresolved-history
record, not an allowance, release, or reset. The composed record has
`execution_authorized=false` and `dispatch_enabled=false`.

## Mandatory later gates

1. Independent review of this plan and any subsequent source revision.
2. Separate root-controlled v4 preservation authorization and installed readback.
3. Conservative accounting-history resolution or reviewed migration to the
   evaluator-owned persistent schema.
4. Separate exact execution approval after all preceding gates pass.

Every unknown, timeout, hash mismatch, permission/ACL/link failure, partial
preservation state, accounting incompatibility, or free-space shortfall remains
blocked. Free space must remain at least 15,000,000,000 bytes and must be
measured before and after preservation. Missing cost or unknown outcome must
never convert to zero or trigger an automatic retry.
