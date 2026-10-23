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
updated_at: 2026-10-23T22:19:17Z
content_hash: "sha256:7ce7d1950dd609e7583aefedc36bc5592af6a58f284594c5e436cf17c3cfaec5"
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
