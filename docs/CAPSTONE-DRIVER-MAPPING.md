# Capstone driver — bounded pre-implementation mapping (GRRR-q3hp AC1)

Status: **DECIDED** — operator delegated the three open decisions
(2026-11-05). Implementation proceeds against the decisions below.

## Decisions

1. **Transport:** the driver does not invent an evaluator transport. `prepare`
   and `run` are pure functions over caller-supplied authenticated receipts and
   an injected `dispatch` callable. The authenticated evaluator path stays
   where it already lives; the CLI supplies no dispatcher and therefore refuses
   `run` with `Unavailable`. This keeps the operator from ever wielding
   evaluator authority directly.
2. **Allowance:** for the v4 `independent-replay` profile, `prepare` records
   `budget_state = blocked` unless an evaluator-issued spendability receipt is
   supplied. No fresh allowance is issued or assumed. `run` therefore refuses
   for this profile, truthfully.
3. **Base:** stay on `story/GRRR-q3hp`. `tests/e2e/milestone.py` is not ported;
   the driver is standalone and `scripts/test-story capstone-driver` covers it.
   The GRRR-6sso dependency remains open and out of scope here.

Base: `story/GRRR-q3hp` at `0b2365e30ab5858cb419f4f4ce9b2ce001850541`.

Verified file digests:

| file | sha256 |
|---|---|
| `research/replay_runtime.py` | `f6c77cc8e3290ff0706134a1b107a320bf65d25a4fdf7a183dcc4b23d4fe665a` |
| `research/corpus_execution.py` | `46f0c03244af5191da6cc6c9e9d9a24ec36018f4c19c69fd2c662d3834d88fdd` |
| `research/persistent_budget.py` | `78f0e145d902dbeadbb1693055551dfdf59aee16d1bc2d5fd4bc4c403bcaaf32` |
| `scripts/test-story` | `3c70d0002e569a5638d0d2058b51deb1b074313b4765ebfd96d74e93e7c41180` |

## 1. Authenticated evaluator transport / allowance API — BLOCKED

`research/corpus_execution.py:161` `CorpusExecutor.__init__` requires
`os.getuid() == RUNNER` (321). `:177` `handle(uid, message)` requires
`uid == EVALUATOR` (320) and is an in-process call, not a wire protocol.

There is **no** transport, client, socket protocol or capability handoff in
`research/` that lets an operator-facing driver obtain evaluator authority:
grepping the tree for AF_UNIX/SCM_RIGHTS finds only the capstone launch broker
and review service, neither of which wraps `CorpusExecutor`.

Consequence: a driver running as the operator cannot reach `handle()` without
inventing both a transport and an authorization model. AC1 forbids inventing
that interface.

Likewise there is no authenticated allowance or spendability receipt API.
`PersistentBudget(profile)` (`research/persistent_budget.py:130`) requires the
evaluator UID through `Budget.__init__`, and `totals(principal)` is
evaluator-only. For the observed v4 binding and profile `independent-replay`
the class reports `historical_unknowns='unresolved', spendable=None`
(`:152-157`) and `reserve()` refuses anything but stage `poc` (`:184-191`).

## 2. Exact revision set — PARTIALLY RESOLVED

Resolved from source:

- runtime identity: `research/replay_runtime.py:65` `verify_runtime(current=True)`
  returns `runtime_identity`, `python`, `root_launch_authorized: False`; it
  requires the running interpreter to be the CommandLineTools Python 3.9 path.
- corpus validation surface: `research/corpus_execution.py:34/43/65`
  `validate_preserved`, `validate_config`, `validate_request`; config requires
  `qemu_installation`, `bootstrap_sha256`, `python_sha256`, `corpus_binding`,
  `accounting_binding`, `execution_profile` (`:43-63`).
- accounting binding must come from `record(ACTIVE)` inside
  `PersistentBudget`; no driver-side access is permitted by the story.

Unresolved: the driver cannot read the protected VM/QEMU asset digests or the
active accounting binding without an evaluator-owned receipt producer. The
story forbids raw protected access, and no receipt producer exists.

## 3. UID / ownership flow — BLOCKED

Operator → evaluator → runner is not expressible at this commit. The only
documented evaluator entry is the in-process `handle(uid, message)`, and the
only runner-side constructor is `CorpusExecutor(root)`. There is no kernel-
authenticated channel between them in source (see item 1).

## 4. Schemas, receipts, idempotency, refusal ordering — BLOCKED

`prepare` must emit an immutable gate/plan record and `run` must refuse every
prepare mismatch. No prepare-plan or run-manifest schema exists in `research/`
or `docs/`. Defining one is an architecture decision (it becomes a durable
record other components may later trust), not a wiring detail.

## 5. Existing test coverage — PARTIALLY RESOLVED

`tests/e2e/milestone.py` does **not** exist at this base commit. It exists only
on `story/GRRR-6sso` at package `51ebc998e7c07018740ec53e389646a5b465cc75`
(verified with `git branch --contains`). `scripts/test-story` at this commit
has no `milestone-e2e` dispatch.

Consequence: the story's CONSUMES entry for GRRR-6sso cannot be satisfied from
this branch without either rebasing onto 6sso or restating the dependency.

## Requested architecture decisions (blocking)

1. What is the authenticated operator→evaluator transport, and which component
   owns it? (New evaluator RPC, or an evaluator-owned launcher that accepts a
   signed request?)
2. What is the allowance/spendability receipt API for the v4
   `independent-replay` profile, given `spendable=None` and POC-only
   reservations? Is a fresh allowance even issuable, or must `prepare` record
   `blocked` permanently for this profile?
3. Which base should the driver land on — this branch, or `story/GRRR-6sso`
   where `tests/e2e/milestone.py` actually exists?

No implementation, no VM launch, no protected access and no accounting write
was performed while producing this mapping.
