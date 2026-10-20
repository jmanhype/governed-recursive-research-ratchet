# Implementation Approval — 2026-10-20

## Operator decision

The operator approved:

1. Committing the verified VM preflight evidence to the local `main` baseline.
2. The standalone runner grammar below.
3. Creating and using restricted evaluator/runner identities after access-control verification.
4. The measured numeric execution limits below.
5. Dispatching `GRRR-0g4n` to a developer in its dispatcher-managed story worktree.

This approval does **not** authorize production access, production mutation, automatic merge to `main`, autonomous patch generation, harness adaptation, unapproved paid calls, or weakening any mandatory gate.

## Approved standalone runner grammar

The runner is a separate `bin/grrr` executable. It is not implemented as a `pvg research` command and does not modify pvg core.

```text
bin/grrr start --policy <digest> --challenge <id> --variant <digest>
bin/grrr status <run-id>
bin/grrr review <run-id>
bin/grrr evidence <run-id> --level decision|technical|audit --format text|markdown|json
bin/grrr decide <run-id> --action approve-evidence|admit-contract|reject|needs-evidence|request-change --target <digest>
bin/grrr stop <run-id> [--key <id>] [--reason <text>]
bin/grrr recover <run-id> [--plan <id>] [--execute]
```

For `GRRR-0g4n`, commands for capabilities owned by downstream stories must report an explicit blocked/not-run outcome. They must not fake review, admission, recovery, verified-defect, or promotion capability.

## Approved identity boundary

Create two dedicated local service identities with no administrator capability:

- `_grrr_evaluator`: owns protected policy, fixtures, evidence, ledger, and control state.
- `_grrr_runner`: owns only the disposable execution workspace/output and may launch QEMU; it cannot read operator credentials, protected holdouts, or evaluator internals.

The operator remains the separate approval authority. Endpoint ACLs and negative impersonation tests must pass before synthetic execution.

## Approved numeric limits

- VM memory: 512 MiB.
- Virtual CPUs: 1.
- Boot/login deadline: 30 seconds.
- Stop acknowledgement target: 2 seconds.
- SIGTERM grace: 5 seconds.
- Forced kill after grace: mandatory.
- Guest output cap: 1 MiB.
- Single bounded challenge deadline: 5 minutes.
- Minimum host free space: 15 GB.
- Guest networking and host shares: disabled.

These limits are enforced in addition to the POC and milestone budget ceilings in `BUSINESS.md` and `ARCHITECTURE.md`.

## Approved VM basis

- QEMU: `/opt/homebrew/bin/qemu-system-aarch64`, version 11.1.2.
- Guest: Alpine `virt` 3.22.6, aarch64.
- ISO SHA-256: `09d601858d72484c89d576fb735215cccf54a92a03e67ca4a7fa7e4b8ec4a7a2`.
- Kernel SHA-256: `dd37c4460f933ec909ff022c34944ff7e1a5300aff99750e3bdc02cd4074c332`.
- Initramfs SHA-256: `899b8023e92db85345375b3ad10c2c9e5b977dc35a0429489ab2476ebad507ec`.

QEMU is GPL-2.0-only and is approved only as an independent external executable. Do not copy, link, or redistribute QEMU source or binaries.

## Dispatch boundary

Dispatch is limited to `GRRR-0g4n` in:

`/Users/speed/Documents/Codex/2026-10-19/3e4m-b-4/outputs/governed-recursive-research-ratchet/.claude/worktrees/dev-GRRR-0g4n`

The developer must implement exactly the story acceptance criteria, run its mandatory tests, commit only to `story/GRRR-0g4n`, append evidence through `pvg nd`, and mark the story delivered without closing it.
