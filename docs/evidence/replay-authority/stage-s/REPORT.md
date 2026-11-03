# Stage S v4 operator-authorization preparation — prepared, not authorized

## Scope

Stage S prepares the exact v4 protected-staging plan and
operator-authorization requirement record, binding the independently
approved Stage R source package to a future protected-staging action. It does
not access or mutate `/Library/GRRR`, stage or install protected records,
amend the budget, reconcile, execute replay, promote, admit, mutate
production, merge, or push.

## Implementation

Added:

- `research/replay_successor_authorization.py`
- `scripts/prepare-replay-successor-v4-authorization`
- `tests/unit_replay_successor_authorization.py`
- `docs/evidence/replay-authority/stage-s/AUTHORIZATION-PREPARED.json`

## Authorization preparation record

The record binds:

- Stage R source bundle role identity:
  `b6354127a7552b628506c25dc7eee27c8ecb371f56bf565a63dd247b31445084`
- Stage R SOURCE-BUNDLE.json file SHA-256:
  `31cb9b8ee538ac22553927fe5f8006c47461073578f9d025f3ddb892ed3ca84c`
- Stage R PACKAGE.json SHA-256:
  `c1b70a4fc1279e48c25a6004d93bc6b6055981524c1f5acd0ff9885fe28a5a9c`
- Stage R absent-leaf review approval SHA-256:
  `e84d5abc30aea4d1e7885f5ebe8df3217d7c35d206b0fa3c5d5b95b986f1cf61`
- Story base commit: `b43f1fa483c8a281246f425d6c5b66606d867bff`

## Exact staging plan

Eight roles, each with source SHA-256 and protected destination:

| Role | Destination |
|---|---|
| installer-entrypoint | `/Library/GRRR/bootstrap/install-replay-successor-v4` |
| v4-store-schema | `/Library/GRRR/bootstrap/replay-successor-v4-v4_store_schema.py` |
| stage-n-contract | `/Library/GRRR/bootstrap/replay-successor-v4-stage_n_contract.py` |
| stage-o-runtime-adapter | `/Library/GRRR/bootstrap/replay-successor-v4-stage_o_runtime_adapter.py` |
| protected-preflight | `/Library/GRRR/bootstrap/replay-successor-v4-protected_preflight.py` |
| atomic-publisher | `/Library/GRRR/bootstrap/replay-successor-v4-atomic_publisher.py` |
| postflight-verifier | `/Library/GRRR/bootstrap/replay-successor-v4-postflight_verifier.py` |
| failure-preservation | `/Library/GRRR/bootstrap/replay-successor-v4-failure_preservation.py` |

Installation target (sibling, not predecessor replacement):
`/Library/GRRR/accounting-poc2/unissued-independent-replay-v4`

Predecessor mutation: **forbidden**.

## Operator authorization requirement

Status: `prepared-not-authorized`.

The operator authorization hash, authorized_by, and authorized_at are all
`null`. Explicit human approval is required **before** any protected staging.
The record is immutable after authorization.

## Denied authorities

- budget amendment
- reconciliation
- replay execution
- admission
- promotion
- merge
- push
- production mutation

All authority flags are `false`.

## Verification

- Initial independent review rejected six validator bypasses:
  empty authority dict, missing authorization_hash field, extra
  predecessor-binding field, missing/incorrect base_commit, extra staging
  item field with recomputed digest, and `prepared_at=None`.

- Correction enforces exact nested key sets for basis, staging items,
  predecessor binding, authorization requirement, and authority; validates
  `base_commit` and `prepared_at` exactly; and adds 13 regressions covering
  every reviewer probe.

- Stage S focused tests:
  - Homebrew Python 3.14.3: 42/42 passed.
  - Miniconda Python 3.12.7: 42/42 passed.
- Full no-guest suites:
  - Homebrew Python 3.14.3: 656/656 passed.
  - Miniconda Python 3.12.7: 656/656 passed.
- All five initial reviewer mutation probes independently reject.
- Deterministic record emission: byte-identical.
- `git diff --check`: PASS.

## Remaining gates

- Independent review of this Stage S authorization preparation record.
- Operator authorization (explicit human approval).
- Protected staging.
- Installation.
- Postflight verification.
- Budget amendment.
- Reconciliation.
- Replay authorization.
- Live four-mode replay.
- PM acceptance.
- Merge.
- Push.
