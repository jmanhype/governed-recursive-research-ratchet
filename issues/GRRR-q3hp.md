---
id: GRRR-q3hp
title: "Bug: capstone lacks explicit executable driver wiring"
status: open
priority: 0
type: bug
labels: [milestone-1, integration, discovered-by-pm]
parent: GRRR-2t3h
created_at: 2026-11-04T13:37:38Z
created_by: speed
updated_at: 2026-11-04T13:50:12Z
content_hash: "sha256:7c42f00f76658279d19bfd46f1d02eaecd350e3e631ce371923dc14e352556be"
blocks: [GRRR-6sso]
---

## Description
## Context
At independently reviewed package `51ebc998e7c07018740ec53e389646a5b465cc75`, `tests/e2e/milestone.py` is deliberately a repository-only historical-provenance checklist with no pass mode; its `main() -> int` always returns `1`. `./scripts/test-story milestone-e2e` merely launches that file. This accurately fails closed, but no separately reviewed executable capstone prepare/run driver is wired to the accepted VM, evaluator, runtime, corpus, and accounting components. Historical hashes and public/no-guest regressions are not VM execution proof.

A parent later reported, without granting access authority: active accounting is live successor version 4 with profiles `['independent-replay']` and binding `/Library/GRRR/accounting-poc2/a142cabb5badd79b10b464d0198184caf218088f4c352c1624076b7207813530`; its directory is mode 0700 owned by `_grrr_evaluator`, and parent stat of `budget.sqlite` was denied. Treat that as context only: this story must not assume mutable/spendable budget, inspect the protected database, or bypass evaluator identity. The optimizer/driver may consume only authenticated evaluator allowance receipts.

## Root Cause
The capstone delivery bundled truthful blocked checklist evidence but deferred the actual command/runtime orchestration. No explicit prepare/run command exists to bind exact revisions and authorization, obtain evaluator-owned budget/capability evidence, and launch the already implemented isolated path while preserving per-gate truth.

## USER INTENT
I can issue one explicit, independently reviewed prepare command and one explicit run command for the exact capstone package; missing capability, budget uncertainty, authorization mismatch, or a floor breach stops before VM launch with truthful records, and no checklist result pretends to be execution.

## MANDATORY PREIMPLEMENTATION MAPPING
Before implementation, produce a bounded architect mapping against current reviewed source. If any item below cannot be resolved from concrete source, stop and request that architectural mapping rather than inventing an interface:
1. authenticated evaluator transport/client and exact allowance/spendability receipt API for the observed version-4 store;
2. exact revision set (driver package, runtime base, corpus freeze, VM/QEMU assets, active accounting binding, request/authorization bytes);
3. safe ownership/UID flow from operator-facing command to evaluator authority and runner `CorpusExecutor`;
4. exact prepare-plan/run-manifest schemas, receipt locations, retry/idempotency semantics, and launch refusal ordering;
5. which existing tests cover each refusal and which proof remains live-only.

## Boundary Map
PRODUCES:
- `research/capstone_driver.py` -> explicit driver API/CLI with separate `prepare` and `run` modes; signatures must be frozen by the architect mapping before implementation
- `scripts/capstone-driver` -> exact separately reviewed operator command (`prepare ...`, then `run ...`; grammar fixed by mapping)
- `scripts/test-story` -> explicit `capstone-driver` dispatch that never launches a VM during no-guest/public tests and reports each missing prerequisite as not-run
- focused driver tests/public documentation -> exact prepare refusal, run refusal, binding, idempotency, and historical-evidence-not-pass cases

CONSUMES:
- GRRR-0g4n: scripts/test-story -> current `milestone-e2e` behavior: run `python -I -S -B tests/e2e/milestone.py` and propagate its return code; preserve mandatory nonzero behavior for missing capability, skipped work, or failure
- GRRR-z3w9: research/replay_runtime.py -> `snapshot() -> dict`; `verify_runtime(current: bool = False) -> dict`; `verify_runtime(current=True)` requires `sys.executable == '/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/bin/python3.9'`, returns `runtime_identity`, `python`, and `root_launch_authorized: False`
- GRRR-w1lt: research/corpus_execution.py -> module functions `validate_preserved() -> dict`, `validate_config(config: dict) -> dict`, `validate_request(message: dict) -> None`; `CorpusExecutor(root: Path)` requires runner UID 321 and validates protected/approval records; `handle(uid: int, message: dict) -> dict` requires kernel-authenticated evaluator UID 320 and accepts `{'action':'status','run':...}` or validated dispatch/stop requests; `stop(run: str) -> dict`; `dispatch(message: dict) -> dict`. The mapping must establish the authenticated caller, not invoke this directly as optimizer
- GRRR-d8ji: research/persistent_budget.py -> `PersistentBudget(profile: str) -> None`; `totals(principal: int) -> dict`; `require_mutable() -> None`; `reserve(principal: int, run: str, maximum: dict, key: str, stage: str = 'poc', binding: str = None) -> dict`. Existing source also validates protected bindings; this story must not perform raw SQLite/database access from the driver
- GRRR-6sso: tests/e2e/milestone.py -> existing `checklist() -> dict` and `main() -> int`; observed package docstring/main are checklist-only and `main()` returns 1. Repair adds real driver wiring but must not reinterpret its historical provenance as a gate pass

## Acceptance Criteria
1. [State] A bounded, independently reviewable architecture mapping resolves every mandatory unknown above from concrete source and freezes exact command grammar, schemas, revisions, UID/transport boundaries, receipt APIs, and failure ordering. Implementation starts only after this mapping is accepted; unresolved mapping is a blocker, not permission to guess.
2. [Event] `prepare` performs no VM launch or protected mutation. It binds the exact driver/runtime/corpus/VM/accounting/request revisions and fresh external authorization, verifies authenticated evaluator capability and allowance/spendability receipts (never raw DB access), checks configured floors, and emits an immutable, individually truthful gate/plan record. Missing capability, unknown budget, non-spendable/insufficient budget, stale/mismatched authorization/revision, or floor breach stops with a precise per-gate `not-run/error/blocked` record before launch.
3. [Event] `run` is a separate command and refuses every prepare mismatch, replayed/stale authorization, unknown outcome, changed protected identity, or unmet gate before dispatch. It uses only the mapped authenticated evaluator path and existing isolated corpus/replay components; no source optimization or alternate host/container execution. A dispatch result and each mandatory gate remain separately recorded, with no aggregate code manufacturing a pass.
4. [Unwanted] Public/no-guest tests prove CLI parsing, exact revision/authorization binding, prepare/run separation, idempotent refusal, all enumerated prelaunch denials, truthful not-run records, and rejection of historical provenance as runtime proof. They explicitly do not prove VM execution. Real VM/evaluator/ledger integration remains mandatory live-only evidence requiring separate explicit authorization; this repair cannot close GRRR-6sso by itself.
5. [Unwanted] No contract admission, promotion, protected recovery/reset/stop-release, network/paid call, secret read, production mutation, merge, or push is added or performed. Existing capstone ACs remain unchanged. `milestone-e2e` continues to fail closed unless every mandatory runtime gate has fresh evidence; the explicit driver is the only route to attempt that later proof.

## Testing Requirements
- Unit/public no-guest tests: MANDATORY, no mocks for parsing/binding/refusal behavior; use synthetic receipts/plans only where protected inputs are intentionally denied, and label no-guest coverage as non-runtime proof.
- Integration/live tests: mandatory and distinct, real VM/evaluator/ledger only; absent authorization/prerequisite must leave tests not-run/blocked, never skipped-green. No environment-variable shortcut to green.
- Commands, both interpreters where applicable, exit codes, executed/failure/not-run counts, source hashes, and protected/non-protected scope must be captured. Run `./scripts/test-story capstone-driver` plus focused tests and `pvg verify`; true runtime command output belongs only to a separately authorized run.

## OUT OF SCOPE
- Changing GRRR-6sso ACs, thresholds, capstone semantics, or acceptance authority; this is blocker wiring only.
- New optimization strategy, source selector changes, admission/promotion capability, protected recovery/reset/stop release, VM provisioning changes, network access, secrets, merges, or pushes.
- Treating `PersistentBudget` construction, historical hashes, public tests, or parent observations as authenticated spendability or VM proof.

## DIFF BUDGET
Honest discovery result: mapping plus wiring is expected to touch ~8-12 files and stay under 1,200 changed LOC including tests/contract documentation. If architect mapping shows more surfaces, update this budget via pvg before implementation; gross overrun requires PM investigation.

## Skills To Use
- `architect` for the bounded mapping prerequisite
- `developer` only after mapping
- `pvg` and `nd`
- independent security/architecture review of exact driver bytes
- `pm_acceptor` for evidence-based acceptance

## Discovered During
GRRR-6sso review at reviewed package `51ebc998e7c07018740ec53e389646a5b465cc75`; parent source inspection confirmed checklist-only docstring/main. No protected run occurred.

## nd_contract
status: new

### evidence
- Created 2026-11-04 from bounded parent DISCOVERED_BUG and `git show 51ebc998...` API inspection; no VM/replay/protected accounting/network/source edit performed.
- Exact source commitments recorded in Boundary Map. Parent-reported live version-4 accounting is context only and was not accessed.

### proof
- [ ] AC #1: mapping complete and independently reviewed before implementation.
- [ ] AC #2: prepare binds exact identities and fails closed before launch.
- [ ] AC #3: run preserves separate execution/gate truth through authenticated path.
- [ ] AC #4: no-guest limits explicit; live-only runtime proof remains mandatory.
- [ ] AC #5: denied authority matrix and unchanged capstone ACs verified.

## Acceptance Criteria


## Design


## Notes
Dependency/evidence update: GRRR-6sso is now blocked by this repair. This blocker wiring does not change any capstone AC and does not constitute or authorize VM/replay execution. True capstone closure still requires separately authorized live runtime/evaluator/ledger proof plus all existing review and human gates.
## 2026-11-04 Source Mapping and Capacity Evidence - Implementation Blocked

Independent architecture mapping by `/root/grrr_q3hp_trust_boundary_mapping` returned `BLOCKED_BY_MISSING_CAPABILITY`. Parent verified the 196-line artifact exists at `/tmp/grrr-q3hp-architecture-mapping-20261104.md` with SHA-256 `631453fafb047f3a564ca8fc88813eb83f643d914a0d0f91b959c3b0242046bf`. The full mapping is appended separately for durable nd readback; it is source-only evidence, not implementation approval or deployed capability.

Concrete findings at reviewed package `51ebc998e7c07018740ec53e389646a5b465cc75` / runtime `c928791cdaa72df91e61002c40317457b543b032`:
- `PersistentBudget.validate_store` accepts versions 1/2/3, not v4; `require_mutable` and replay preflight require v1.
- No authenticated v4 allowance/spendability receipt API was identified in the bounded inspected interfaces.
- The retained Stage O adapter is hypothetical/uninstalled and grants no execution authority; a sandbox schema verifier is not a spendability or capability receipt.
- Operator-to-evaluator service wiring and cross-restart one-use authorization consumption are unresolved.
- Therefore a prepare/run wrapper alone cannot safely launch this capstone. Do not weaken version guards or instantiate the evaluator session during mutation-free prepare. Do not implement guessed schemas or claim a mapping pass.

Capacity audit artifact `/tmp/grrr-capacity-audit-20261104.txt` was independently checked on disk: 148,693 bytes, SHA-256 `f366259c07712e34ba32ebca3911ab424fe3b81320ded31c745fbc1b1c731de5`.

Measured cache-size ceilings (not guaranteed reclaimed bytes):
- Codex cache: 1,892,179,968 bytes; active runtime, not approved for cleanup.
- Go build cache: 1,366,118,400 bytes.
- Chrome Default Cache: 1,297,309,696 bytes; active browser.
- Chrome Default Code Cache: 606,470,144 bytes; active browser.
- pip cache: 8,232,960 bytes.
- Requested Homebrew cache path absent; no alternate-path search or inferred broader zero.
- Total measured ceiling: 5,170,311,168 bytes.

Parent's later `df -k /` observation reported 5,663,168 KiB available, or 5,799,084,032 bytes. Even an ideal recovery of every measured cache byte would yield only 10,969,395,200 bytes, still 5,136,732,160 bytes below the 16,106,127,360-byte replay floor, with no safety margin. Active Codex/Chrome caveats further reduce what could safely be considered. No cleanup, purge, quit, termination, reboot or deletion occurred.

Workflow writeback also exposed a tool failure: `pvg story reject GRRR-6sso` refused with `property "assignee" not found`. Live status/labels remained unchanged. A subsequent normal atomic `pvg nd claim ... --agent pm-rejection-writeback` without force was refused because GRRR-q3hp blocks the story. No force claim, manual label/status workaround, raw issue-file edit, or pvg-core change was used. The independent PM rejection is substantive but not a landed transition; do not claim otherwise.

Current result: GRRR-q3hp AC1 mapping is blocked by concrete missing trusted capability; no implementation has begun. Capstone runtime evidence and cumulative allowances remain unestablished. Source checkout remains untouched; no protected mutation, VM/replay, network/inference, credential, admission, promotion, merge or push occurred. The exact-old-revision conditional grant does not silently authorize new implementation or deployment.

## History
- 2026-11-04T13:37:44Z dep_added: blocks GRRR-6sso

## Links
- Parent: [[GRRR-2t3h]]
- Blocks: [[GRRR-6sso]]

## Comments
