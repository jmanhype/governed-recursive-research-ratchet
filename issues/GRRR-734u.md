---
id: GRRR-734u
title: "Replay: fresh execution namespace planner (source-only)"
status: in_progress
priority: 2
type: feature
parent: GRRR-2t3h
created_at: 2026-11-08T18:07:59Z
created_by: speed
updated_at: 2026-11-08T18:08:44Z
content_hash: "sha256:6eda21a551fdf7b7f63ca8404a1d86d990fa17230d4e92aa1aec4d21992259e8"
follows: [GRRR-hbc6, GRRR-q3hp]
assignee: dev-GRRR-734u
---

## Description
## USER INTENT

After merge `5f6ce4e` integrated accepted `GRRR-hbc6`, prepare—but do not issue—a distinct replay execution namespace. The source-only planner must bind all replay inputs to exact prior evidence and accounting while preserving every consumed-sequence and accounting invariant. The operator authorizes source work only.

## CONTEXT AND BINDINGS

- Predecessor `GRRR-hbc6` is accepted; source work at merge `5f6ce4e` had 307 tests pass on Python 3.14, 3.12, and 3.9.
- Existing `replay.py:440-442` rejects a consumed sequence by counting replay receipts. This guard must not be weakened, bypassed, or reset.
- `replay_runtime.py` identifies a Python runtime; it is not this execution namespace.
- Fixed predecessor execution target is `/Library/GRRR/independent-replay`, used only as provenance.
- Existing accounting v4 recovery receipt `8b7958e5be76f6b35c4bfafc1f17a2926badfdd813addbefd5d683e376e8eeeb` retains its unknowns and holds. No allowance or spendability may be created or inferred.

## PRODUCES / CONSUMES

**Produces (planned ownership, approximately 4 files and no more than 600 changed LOC):**

- `research/fresh_replay_runtime.py` — pure canonical versioned planner API and typed proposal result.
- `tests/unit_capstone_fresh_replay_runtime.py` — real temporary filesystem/SQLite integration coverage.
- `tests/unit_capstone_backend_suite.py` — registration-only change for the required backend runner.
- `docs/FRESH-REPLAY-RUNTIME-WIP.md` — source-only status and remaining authorization/provisioning gates.

**Consumes:**

- Caller-supplied archived or synthetic canonical source/input manifests, identity records, digests, prior evidence, and accounting receipt.
- Existing common canonical/digest helpers and approved isolation/authority policies.
- Predecessor target and accounting facts solely as immutable provenance bindings.

## OUT OF SCOPE

- No `/Library/GRRR` access, `stat`, `lstat`, `open`, provisioning, installation, VM action, replay, reconcile, promotion, admission, production action, commit, or push.
- No accounting creation, budget change, hold release, unknown zeroing, sequence reset, replay-state reset, ledger reset, or stale authorization inheritance.
- No runtime readiness claim: a valid source proposal is prepared, not issued or installed.

## ACCEPTANCE CRITERIA

1. The pure canonical versioned planner API validates an exact typed schema plus caller identities, digests, and immutable proposal hashes from archived/synthetic caller-supplied inputs. It never opens protected assets.
2. It proposes one distinct, non-reused execution namespace. The consumed predecessor is retained only as provenance. It rejects reused or consumed targets, pending/stopped/unknown target state, and invalid candidate roots. It never deletes or resets previous `replay_state`, sequence, or ledger state.
3. Every proposal binds the exact source, inputs, VM/policy, prior evidence, predecessor identity, and existing accounting v4 identity/recovery receipt `8b7958e5be76f6b35c4bfafc1f17a2926badfdd813addbefd5d683e376e8eeeb`. It creates no accounting entry, changes no budget, releases no holds, zeroes no unknowns, infers no spendability, and inherits no stale authorization.
4. Output is explicitly `prepared_not_issued`; review, installation, replay, promotion, and admission authorization are false; every mandatory live gate is recorded not-run; and no runtime readiness is asserted.
5. Invalid requests are rejected lexically before protected metadata is consulted, with no `/Library/GRRR` `stat`/`lstat`/`open`. Real temporary filesystem/SQLite fixtures cover collision/reuse, pending/stopped state, stale hash or identity, symlink/escape, and missing evidence, and prove preservation of old evidence/accounting. A valid new-target fixture can produce a nonauthorizing proposal even when the predecessor was consumed.
6. Filesystem/SQLite integration tests use real fixtures rather than mocks, contain no skips, and forbid a zero-test green run. Register the new tests in the required backend runner and run them on the three installed Pythons (3.14, 3.12, 3.9). The source-only artifact is not live execution proof.
7. Documentation records the remaining exact-parent review and provisioning gates and explicitly states that no root, VM, replay, promotion, admission, production, commit, or push action was performed.

## nd_contract

status: new

### evidence

- Create-only story from the operator brief; no implementation, claim, dispatch, test execution, protected access, commit, or push has occurred.
- Fresh `pvg loop next --json` before creation reported `Ready: 0` and `InProgress: 0`.

### proof

- [ ] AC #1: Exact typed canonical-input and immutable proposal-hash validation, with protected assets never opened.
- [ ] AC #2: Distinct namespace proposed while reused/consumed/invalid targets are rejected and prior replay state is preserved.
- [ ] AC #3: Exact replay and accounting identities bound with no accounting or authorization mutation.
- [ ] AC #4: Proposal is explicitly prepared-not-issued with all authorizations false and live gates not-run.
- [ ] AC #5: Lexical fail-closed behavior and preservation properties proven by real filesystem/SQLite fixtures.
- [ ] AC #6: Mock-free, skip-free nonzero tests pass through the required backend runner on Python 3.14, 3.12, and 3.9.
- [ ] AC #7: Remaining review/provisioning gates and source-only limits documented.

## Acceptance Criteria


## Design


## Notes


## History
- 2026-11-08T18:08:44Z status: open -> in_progress
- 2026-11-08T18:08:44Z auto-follows: linked to predecessor GRRR-q3hp
- 2026-11-08T18:08:44Z claimed by dev-GRRR-734u

## Links
- Parent: [[GRRR-2t3h]]
- Follows: [[GRRR-hbc6]], [[GRRR-q3hp]]

## Comments
