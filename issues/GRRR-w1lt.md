---
id: GRRR-w1lt
title: "Bug: independent replay lacks approved privileged prerequisites"
status: open
priority: 0
type: task
labels: [milestone-1, integration, discovered-by-developer]
parent: GRRR-2t3h
created_at: 2026-10-23T18:55:10Z
created_by: speed
updated_at: 2026-10-23T18:55:10Z
content_hash: "sha256:8dfd8e855f5706266071c73c1792d858d27507e75e18e8340a03cc8cda304558"
---

## Description
## Context

GRRR-z3w9 requires a fresh, evaluator-controlled, UID-separated, offline VM replay of an allegation from the accepted corpus v2.2. A developer verified the repository corpus artifacts, but no replay-specific operator policy record, replay launcher, fresh runtime, protected replay assets, or privileged parent execution path exists. A UID-501 developer must not create the required evaluator/runner identities, invoke QEMU, or mutate `/Library/GRRR`.

## Root Cause

The milestone supplied the trusted corpus execution path but deferred independent replay infrastructure and action-specific authority. The proposed two-consecutive-failure stop rule and resource limits have not been converted into an approved replay policy binding. As a result, GRRR-z3w9 is structurally ready in the dependency graph but cannot execute its mandatory no-mock integration path.

## Affected Components

- Proposed `research/replay` / replay receipt path
- Proposed `tests/integration/independent-replay`
- `scripts/test-story independent-replay`
- Evaluator UID 320 policy/expectation/budget/ledger ownership
- Runner UID 321 approved executor ownership
- Root-owned immutable QEMU, VM, source/build, corpus, and specification inputs

## Acceptance Criteria

1. An operator explicitly approves a replay-specific policy record binding corpus `GRRR-validated-corpus-v2.2-isolated`, freeze digest `dfa75ef2bf3d43fd4f750094fe643afe4f204812c0ae2426276bedb471fa8529`, source commit `129e0b3f15a3bd6af949ee47d76f6855c582ab73`, exactly two consecutive independent replay failures, and explicit numeric watchdog/termination/grace/kill/output/runtime/cost limits. The record must deny network, paid dispatch, host shares, contract admission, and promotion.
2. A reviewed, root-owned provisioning path creates a fresh disposable replay runtime with evaluator UID 320 owning policy, expectations, budget, reservations, and ledger; runner UID 321 owning only the approved executor; immutable installed QEMU/VM/source/corpus/spec identities; and verified safe ancestors, ownership, modes, and ACL-free paths.
3. Read-only preflight proves exact protected asset hashes, corpus/spec binding, disk headroom, process/lock absence, isolation controls, and identity separation before any replay dispatch.
4. The parent-mediated launcher can execute a replay without exposing credentials, protected truth, raw private logs, or host shares, and preserves all failure/recovery evidence outside candidate control.
5. GRRR-z3w9 remains blocked until this prerequisite bug is accepted; no corpus fixture ledger may be relabeled as an independent ReplayReceipt.

## Testing Requirements

- Integration tests: MANDATORY (no mocks) for provisioning/preflight/launcher behavior where authorized.
- Privileged operations require a separately recorded operator authorization and parent-mediated execution.
- Missing approval or failed preflight must produce explicit blocked/not-run evidence, never a skipped green test.

## Discovered During

Story GRRR-z3w9: developer preflight found corpus artifacts valid but replay policy/runtime prerequisites absent.

## Skills To Use

- `pvg` and `nd` for tracker state
- `architect` or security review for provisioning/runtime changes
- `vlt` only if vault tooling itself is used

## nd_contract
status: new

### evidence
- Created from the GRRR-z3w9 DISCOVERED_BUG report on 2026-10-23.

### proof
- [ ] Pending operator approval and reviewed provisioning.

## Acceptance Criteria


## Design


## Notes


## History


## Links
- Parent: [[GRRR-2t3h]]

## Comments
