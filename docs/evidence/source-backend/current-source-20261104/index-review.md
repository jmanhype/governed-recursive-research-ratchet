# Scoped source review — GRRR-k3j7 backend index WIP (2026-11-04)

REVIEW_RESULT: scoped APPROVED

## Boundary and inputs

- Worktree: `/Users/speed/Documents/Codex/2026-10-19/3e4m-b-4/outputs/governed-recursive-research-ratchet/.claude/worktrees/dev-GRRR-k3j7`
- HEAD: `2b601462ba0ffb5aee6239aa22b06c26801dfaf9`
- `docs/findings/` is absent in this worktree.
- Reviewed only the requested WIP files, with exact-source fallback into the consumed Ledger, Journal, contract, and StopCoordinator seams:
  - `research/capstone_backend_schema.py` SHA256 `2249d8b8a69baf6f88ba62934cfd9ba4fcf0f6cdaa12d400c3bae86e388001c8`
  - `research/capstone_backend_index.py` SHA256 `fe90fcd9fc80841030ad81c9ebdd9c5d0c0c788815c1c6f30825696894d96976`
  - `tests/unit_capstone_backend_index.py` SHA256 `15fff01697bd9ad0051ee64f5e476bb76cf59f22e3ffed3be65b0a120bcf796b`
- The three files are untracked WIP, consistent with the parent's bounded review boundary. No repository, tracker, credential, network, production, VM/replay, or protected-path mutation was performed.

## Findings

No concrete defect was found inside the actually implemented base-issuance/replay/stop-hook scope.

Evidence for the positive scoped approval:

1. **Data-only finite issuance and intent continuity**
   - `_spec` bounds the leaf list to 1..256, checks contiguous indices, exact request/run and leaf identities, predecessor bounds, typed nonnegative maxima, exact componentwise campaign/leaf maxima, authorization/spec hashes and windows, and exact leaf IDs (`research/capstone_backend_index.py:90-155`).
   - Intent is one exact issuance row and commits only from that prior intent, preserving all original identity/raw fields; commit cardinality binds spec leaves, bundle entries, and leaf rows, derives grant/control identities, and verifies original grant bytes and bindings before materializing rows (`research/capstone_backend_index.py:170-229`).
   - The issuer invocation marker is memory-only. A reopened index can obtain a cached intent receipt but cannot mint commits/grants; the implementation deliberately discards ownership only after a successful commit (`research/capstone_backend_index.py:366-421`).
   - This materializes finite data rows only. It does not validate or claim source/static approval authority, installation authority, allowance, or execution capability.

2. **Exact SQL inventory and full base replay/index equality**
   - The schema declares exact backend-v2 tables, constraints, delete/update guards, and receipt-derived mutable transitions (`research/capstone_backend_schema.py:32-128`).
   - `validate_schema` compares exact SQL and implicit-index inventory, rejects namespace additions/shadows via the journal schema preflight, and rejects foreign-key violations (`research/capstone_backend_schema.py:133-149`; `research/capstone_journal_schema.py:38-68`).
   - `_validate` checks the complete event chain and idempotency bodies, folds implemented events into state, compares every backend table row against SQLite, then validates the unchanged Journal and cross-checks issued grants and claims (`research/capstone_backend_index.py:267-322`; `research/capstone_journal.py:136-190`). Direct missing-row/blob/grant tampering is covered at `tests/unit_capstone_backend_index.py:235-275`.

3. **Cached retries and stale-tip exclusion**
   - A cached key is returned only after full validation and exact canonical body comparison; changed retries do not append (`research/capstone_backend_index.py:388-397`; test `tests/unit_capstone_backend_index.py:150-182`).
   - New transitions capture the tip only after validation and pass it to `Ledger.append_atomic`; the consumed Ledger API rejects a changed tip before append and rolls back event/row/grant changes on callback failure (`research/capstone_backend_index.py:406-416`; `research/ledger.py:72-107`; tests `tests/unit_capstone_backend_index.py:184-204`).
   - The real two-process `BEGIN IMMEDIATE` fixture leaves one committed event and one refusal (`tests/unit_capstone_backend_index.py:356-378`). This is the required source-race evidence, not an exhaustive OS scheduler proof.

4. **Subordinate stop hook**
   - `apply_backend_stop` requires the caller's transaction, binds the supplied extension to the final durable safe-stop/ref event and receipt, validates the pre-event prefix, computes the post-state in memory, and writes only SQL deltas; it performs no BEGIN/COMMIT, Ledger append, Journal call, object IO, or cancellation (`research/capstone_backend_index.py:234-264,325-363`).
   - First stop sets the campaign anchor and transitions a running campaign run to stop-pending with preserved active leaf and incremented revision. Missing runs are not invented, terminal/repeat runs remain unchanged, and any existing projection is explicitly refused because that reducer is unimplemented (`research/capstone_backend_index.py:234-264`).
   - Atomic rollback, repeat-anchor preservation, and wrong-linkage refusal are exercised at `tests/unit_capstone_backend_index.py:251-315`.

5. **Fail-closed factories and identifiers**
   - Production opening requires actual evaluator UID; public fixtures are restricted to private, directly parented `/private/tmp` directories, exact main DB path, no DB symlink, and explicit creation only (`research/capstone_backend_index.py:424-455`).
   - Receipt-derived and identity columns use strict digest validation where required by the backend contract (`research/capstone_backend_index.py:59-81`). A separate real SQLite probe changed `issuance_id` from 64-hex data to `issue-one`; result: `rejected:InvalidInput`, `EVENT_COUNT 0`.

## Verification actually run

Command (bounded by `timeout 30`):

```sh
/usr/bin/time -p timeout 30 /opt/homebrew/bin/python3 -B /tmp/grrr-k3j7-guarded-source-suite-20261104.py unit_capstone_backend_index
```

Measured result:

```text
Ran 29 tests in 1.064s
OK
PARENT_SOURCE_ONLY tests=29 failures=0 errors=0 skipped=0 protected_attempts=0; guard=parent-interpreter-only; no VM/UID/OS-isolation proof
real 1.24
user 0.74
sys 0.36
```

No mocks or tests were changed. The parent-interpreter guard reports zero protected-path attempts, but it is not an OS sandbox or production identity proof.

## Limitations / already-known gaps

This is **not** full backend, campaign, authority, scheduler, or PM acceptance. The following remain missing and are not treated as new findings:

- campaign start/select/leaf-bind/advance/finish/fence reducer and complete campaign replay;
- launch and projection reducers plus complete launch/review/control/accounting joins;
- complete source/static authority registry and current-capture validation;
- complete scheduling, capability lifetime, cessation verification, and production control integration;
- InstallationV2/UID322/live ACL or runtime qualification.

The current campaign format is intentionally refused (`research/capstone_backend_index.py:293-300`), and projection stop handling intentionally fails closed (`research/capstone_backend_index.py:264`). Therefore this approval is limited to the implemented finite issuance intent/commit mechanics, exact base schema/replay checks, cached/stale behavior, and subordinate SQL stop hook.
