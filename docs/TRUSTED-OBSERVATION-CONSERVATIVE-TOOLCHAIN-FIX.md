# Current conservative-genesis provisioning: canonical toolchain preflight

Supersedes v2 bootstrap/plan only; blocked accounting semantics are unchanged.
No installed file or Apple permission was changed. No root/QEMU invocation.
`/Library/GRRR/accounting` remains absent.

## Reviewed checks

Immutable bootstrap and plan: root:wheel, safe ancestors, no symlinks or ACLs,
single-link files, **no write bits**. No exception applies to payload bytes.

Toolchain owner-write exception applies ONLY to the two exact canonical paths:
- CLT Python `.../Python3.framework/Versions/3.9/bin/python3.9`, root:wheel 0755,
  SHA `5c5950c62eee5fd227a67e4bdfcde81c9add59799bba0949635f3d5ba9661c26`,
  version `Python 3.9.6`.
- CLT `.../Python3.framework/Versions/3.9/lib/python3.9/json/__init__.py`,
  root:wheel 0644,
  SHA `332fabb72a4a1ed02c9207a7619ab339dac8f0b6862e16f6499147121b302a27`.

Both retain safe root:wheel ancestors, no symlinks, no ACLs, no group/world writes
and exact hash checks. The interpreter version is independently checked through
its absolute canonical path with `-I -S -B` and minimal environment. Install
checks the loaded stdlib origin. Any other owner-write exception path is rejected.

Tests exercise the REAL canonical Python/stdlib read-back and immutable rejection
of their write bits, real user-owned path and symlink negatives, plus pure
metadata-predicate negatives for UID/GID, group/world writes and ACL indicators.
These are nonprivileged checks, not a claim of executed privileged installation.
Both Python suites passed 105/105; the explicit pvg scan passed (one `.py` file;
extensionless provisioner separately executed for build/verify).

## Current exact pins

- Bootstrap: `07484611331e38165dcf8d3cb872455806572ca5451289d7b30ea9a9ffccbc97`
- Plan: `7c46b634e367eb732aebef26c4a09504571f552ab6a09fdcb6095f721a580459`
  at `docs/evidence/trusted-observation/conservative-genesis/toolchain-fix/plan.json`.
- Database unchanged: `9fe4000c0c45b83cc818c29640e561167c34bd663abc26267e2a1b009f878234`,
  prepared at this worktree's `.tmp-sr_pm/conservative-genesis-v3/budget.sqlite`.
- Receipt unchanged: `9f64395bec815a6bb2281d3b5d96d2356899138b1929b0a9881c16483c486dde`.

259 original artifacts remain byte-bound; stopped=1, unknown historical campaign
stop, unresolved history, no fabricated settlements or fresh allowance. Full POC
encumbrance is included in milestone. Every profile/stage remains blocked.

## Parent authorization and command

Requested authorization:
“Provision ONLY conservative-genesis plan
`7c46b634e367eb732aebef26c4a09504571f552ab6a09fdcb6095f721a580459`
with bootstrap `07484611331e38165dcf8d3cb872455806572ca5451289d7b30ea9a9ffccbc97`.
Keep stopped=1 and unresolved history; no execution, hold release, stop clearing
or complete migration. Do not modify Apple toolchain permissions.”

After independent review/authorization and independent root-controlled placement
of exact bootstrap and plan as root:wheel 0444:

```sh
/usr/bin/env -i PATH=/usr/bin:/bin LC_ALL=C /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/bin/python3.9 -I -S -B /Library/GRRR/bootstrap/conservative-genesis install /Library/GRRR/bootstrap/conservative-genesis-plan.json 7c46b634e367eb732aebef26c4a09504571f552ab6a09fdcb6095f721a580459 INSTALL_BLOCKED_CONSERVATIVE_GENESIS:7c46b634e367eb732aebef26c4a09504571f552ab6a09fdcb6095f721a580459
```

AWAITING_PARENT_IDENTITY_RUN. Existing/partial-state refusal, 15 GB post-copy
floor, immutable hash-bound payload copy and inode/device read-back remain.
Earlier evidence manifests apply at their historical commits; the toolchain-fix
manifest binds current changed source/docs. No historical evidence is overwritten.
