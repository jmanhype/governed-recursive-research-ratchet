---
id: GRRR-43i8
title: "Bug: independent replay accounting profile unavailable"
status: in_progress
priority: 0
type: task
labels: [milestone-1, integration, discovered-by-developer]
parent: GRRR-2t3h
created_at: 2026-10-23T22:09:12Z
created_by: speed
updated_at: 2026-10-23T22:30:26Z
content_hash: "sha256:e2a12fbee02564dd1a9f1f59e5ed3cfd0b25a8bda6199abf70f5691d2ab6d21a"
blocks: [GRRR-z3w9]
assignee: dev-GRRR-43i8
follows: [GRRR-w1lt]
---

## Description
## Context

GRRR-z3w9 requires independent replay to consume the existing cumulative accounting campaign, but the active successor store has no `independent-replay` profile and remains stopped. The current active binding is `/Library/GRRR/accounting-poc2/active.json`; its protected store directory is `901acaff42b5a42f667b1c435be7c9a9ae8312539cc36eb023c45584fd2e06d6`, state is stopped, and registered profiles are only `synthetic`, `offline`, and `trusted-observation`.

The implemented replay preflight intentionally fails before namespace creation. It must not create a fresh allowance, reset cumulative ceilings, or reinterpret corpus/runtime-smoke events as independent replay.

## Root Cause

The successor accounting slice preserved ambiguous prior history conservatively but did not include a reviewed independent-replay profile or recovery path. Independent replay now needs cumulative registration without fabricating missing historical usage or silently releasing the stop.

## Affected Components

- `research/persistent_budget.py`
- Protected active accounting binding
- Stopped successor budget store
- Independent replay preflight and evaluator reservations
- Evidence/history preservation

## Acceptance Criteria

1. Produce an independently reviewed migration/recovery plan that identifies the exact active binding, store identity, stop record, existing reservations/holds/settlements/events, usage totals, and unknowns without mutating protected state.
2. Register an `independent-replay` profile only through a reviewed, root-owned, exclusive, atomic, permission-restricted path that preserves all existing bytes/history and carries forward cumulative usage and every uncertain hold conservatively.
3. The profile must use approved explicit ceilings and deny fresh-allowance reset, recasting of corpus/smoke events as independent replay, stop release by installer side effect, and unknown-history zeroing.
4. Stop recovery must require separate operator authorization and independent review, prove baseline intact, preserve unresolved history, and leave promotion/admission disabled.
5. Read-only preflight and post-install verification must prove binding/device/inode identity, hashes, ownership/modes/ACLs, profile registration, cumulative balances, stopped-state disposition, and fail-closed behavior for tampered/partial state.
6. Actual independent replay remains blocked until registration/recovery is accepted and all replay gates pass; no fresh replay Budget database may substitute for the cumulative store.

## Testing Requirements

- No-guest unit tests for binding/profile validation, conservative history carry-forward, stop persistence, uncertain holds, partial-state refusal, and ceiling enforcement.
- Integration proof requires separately reviewed parent-mediated execution and read-only before/after protected-state verification.
- No skipped mandatory tests or fabricated receipts.

## Discovered During

Story GRRR-z3w9 at WIP commit `6079af60ea7d8dc3b5927d0d51748903230a2`.

## Skills To Use

- `pvg` and `nd`
- independent security/architecture review before privileged effects

## nd_contract
status: new

### evidence
- Created from GRRR-z3w9 DISCOVERED_BUG report on 2026-10-23.

### proof
- [ ] Pending reviewed migration, authorization, installation, and verification.

## Acceptance Criteria


## Design


## Notes
# GRRR-43i8 registration-only verification

Status: implementation WIP, BLOCKED for privileged ACs; not delivered.
Tested source tree: `8f90d35c9008478c4258f07c171442e84de11235`.
No protected installation/mutation, root/sudo, stop release, guest/VM/QEMU,
independent replay, promotion, admission or push was performed.

## PROOF

Commands ran from `.claude/worktrees/dev-GRRR-43i8` on 2026-10-23.

| Command | Result |
|---|---|
| `/usr/bin/python3 -m unittest discover -s tests -p unit_replay_accounting_registration.py` | Python 3.9.6: 23 tests, 0 failures, 0 errors, 0 skipped; 0.923s; OK |
| `/opt/homebrew/bin/python3 -m unittest discover -s tests -p unit_replay_accounting_registration.py` | Python 3.14.3: 23 tests, 0 failures, 0 errors, 0 skipped; 0.860s; OK |
| `/usr/bin/python3 -m unittest discover -s tests -p 'unit_*.py'` | 221 tests, 0 failures, 0 errors, 0 skipped; 20.915s; OK |
| `/opt/homebrew/bin/python3 -m unittest discover -s tests -p 'unit_*.py'` | 221 tests, 0 failures, 0 errors, 0 skipped; 20.461s; OK |
| `/usr/bin/python3 -m compileall -q research tests/unit_replay_accounting_registration.py scripts/replay-root-prepare` | exit 0 |
| `/opt/homebrew/bin/python3 -m compileall -q research tests/unit_replay_accounting_registration.py scripts/replay-root-prepare` | exit 0 |
| `pvg verify research/accounting_registration.py research/budget.py research/persistent_budget.py tests/unit_replay_accounting_registration.py scripts/replay-root-prepare docs/REPLAY-ACCOUNTING-REGISTRATION.md --format=text` | PASS: 4 files scanned, 0 issues; extensionless script and Markdown not scanned |
| `git diff --check` and `git diff --cached --check` | exit 0 |

Full test stdout/stderr captures: `/tmp/GRRR-43i8-final-full-py39.log` and
`/tmp/GRRR-43i8-final-full-homebrew.log`. Both end with `Ran 221 tests` / `OK`.
No final suite warnings. These are no-guest units, not protected integration.

Coverage command (stdlib trace; not branch coverage):

```sh
/usr/bin/python3 -m trace --count --missing --summary \
  --file /tmp/GRRR-43i8-trace-final \
  --coverdir /tmp/GRRR-43i8-coverage-final \
  --module unittest discover -s tests -p unit_replay_accounting_registration.py
```

23 tests passed in 1.285s. Reported executable-line coverage: registration module
90% (350 lines), Budget 86% (162 lines), PersistentBudget 97% (91 lines), tests
99% (383 lines). Coverage output `/tmp/GRRR-43i8-coverage-final.log`.
The Homebrew interpreter lacks third-party `coverage`; no dependency was installed.
An initial trace without `--missing` reports a misleading executed-only denominator;
that result is explicitly discarded and is not the coverage claim above.

Source SHA256 values:

```text
74975c0da25303f05a7701008d87a22be7d8e6ed029bdee619f626a0d6ee10ab  research/accounting_registration.py
576b77e2bcc1782ab5cdc8fad80ad7b550e110f2f617280982b93363e0974a23  research/budget.py
d658334fc35228cac1b70c8e9e0e1c173bff90ca51d5470dbfbfa6da463e606b  research/persistent_budget.py
1285f6bf5f1e1973c5539437e99021b85c872b7452aa93564037ba3f59a41183  scripts/replay-root-prepare
```

## AC disposition

| AC | Implementation/test support | Remaining blocker |
|---|---|---|
| 1 | Reviewed proposal; exact pinned parent-observed identities; read-only snapshot code captures all raw rows and unknowns | Actual protected inventory/provenance not collected by worker; implementation review pending |
| 2 | Root-only, exclusive, receipt-first/atomic binding source; temporary fixture byte/inode preservation tests | Protected registration NOT RUN; no integration proof |
| 3 | Exact existing shared ceilings; POC-only replay; no DB writes/new store/reset; full uncertain holds retained | Independent review of implementation remains required |
| 4 | No recovery command; stop preserved; changed stopped DB rejects verification; duplicate/zero requests refuse | Recovery NOT AUTHORIZED/NOT RUN; separate decision and review required |
| 5 | Read-only baseline/postflight source; ACL/mode/link/identity/tamper/partial tests, fault injection before/after activation | Protected before/after verification NOT RUN |
| 6 | Legacy denies replay; registered store remains frozen/stopped; no dispatch authority added | Actual replay remains blocked behind registration/recovery and all replay gates |

## LEARNINGS

- A profile registration need not migrate SQLite: only the root binding changes;
  the exact stopped database, original binding bytes and all unknown holds remain.
- Idempotent duplicate reservation lookup previously preceded stop checking;
  fail-closed ordering must deny it before returning an old reservation.
- Updating Budget requires refreshing the checkout smoke launcher's source pin;
  that does not update or approve its installed closure.
- Legacy `PROFILES` is consumed by fixtures/clients; retain that three-profile API
  and add explicit `REGISTERED_PROFILES` rather than changing legacy semantics.
- Unit root emulation must restore original directory modes, not assume 0555:
  Python 3.14 Path.replace uses the patched os.replace where Python 3.9 differs.

Initial fixture permission errors, source-pin/legacy export regression failures,
and the Python 3.14 fixture-mode mismatch were fixed before the final clean runs.
Future parent commands and remaining privileged-parent exclusion obligation are
in `docs/REPLAY-ACCOUNTING-REGISTRATION.md`. Story remains in_progress.

## Independent Security Review

SECURITY_REVIEW: READY_FOR_REGISTRATION_IMPLEMENTATION

- Reviewed documentation-only commit f16d4628d26a49fb344a2ecc935b2e6e4558a31c and proposal SHA256 b2a6bcf72d6b22f8bbf6e6ea1f82c79069811010053aafb5e206b35bafc36c5c.
- No blocking defect in the proposal-only basis. Mandatory prerequisites remain: exact protected inventory/provenance, explicit approved replay limits/stage, complete publication/receipt and writer-lock protocol, implementation, tests, and separate independent verification.
- This review does not satisfy GRRR-43i8 delivery and authorizes no installation, stop recovery, protected mutation, replay, admission, or promotion.

## nd_contract
status: in_progress

### evidence
- Security reviewer was read-only; no privileged execution.

### proof
- [ ] Registration-only implementation and all tests remain pending.
- [ ] Protected installation/recovery remain blocked and not-run.

## History
- 2026-10-23T22:09:12Z dep_added: blocks GRRR-z3w9
- 2026-10-23T22:09:24Z status: open -> in_progress
- 2026-10-23T22:09:24Z auto-follows: linked to predecessor GRRR-w1lt
- 2026-10-23T22:09:24Z claimed by dev-GRRR-43i8

## Links
- Parent: [[GRRR-2t3h]]
- Blocks: [[GRRR-z3w9]]
- Follows: [[GRRR-w1lt]]

## Comments

### 2026-10-23T22:16:52Z speed
BLOCKED: No independent-replay ceilings, privileged registration, or stop recovery authorized in this turn. Current AC2/5 and integration requirements cannot be met by a proposal. Draft docs/REPLAY-ACCOUNTING-RECOVERY-PROPOSAL.md preserves parent-observed identity, conservative semantics and exact decisions needed. No protected effects, no production code changes. Baseline focused tests 7/7 and full no-guest tests 198/198 pass on Python 3.9.6 and 3.12.7; these do not prove proposed migration. Await independent review and explicit operator decisions; not delivered.
