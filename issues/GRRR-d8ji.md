---
id: GRRR-d8ji
title: "Bug: registered independent-replay accounting lacks recovery implementation"
status: open
priority: 0
type: bug
parent: GRRR-2t3h
created_at: 2026-10-24T20:19:06Z
created_by: speed
updated_at: 2026-10-24T20:19:06Z
content_hash: "sha256:1d80a9ce31bec4c1d71174039e91ad733d9a745e37cca2735ad93257e8d77f15"
blocked_by: [GRRR-43i8]
blocks: [GRRR-z3w9]
---

## Description
## Context (Embedded)
Registered independent-replay accounting intentionally freezes every mutation, but there is no reviewed recovery implementation. GRRR-43i8 is accepted for registration only; it did not authorize recovery or replay. GRRR-z3w9 remains blocked at clean WIP 3869e0ff223bae5d4ae75080f33d4b6ba33efacc after merging epic 6afd643. This bug owns one no-privileged-effects recovery implementation package, not an execution approval.

Accepted registration evidence (not a fresh protected-state observation by this author): active version-2 binding SHA256 97ad3cd38a90a71d412afccad5ed49fc73af73e5413edcc4e07a1e0d23f451c5; registration receipt fb2132f1dce4867d0a28895215ef9d5f9ad1ea947b3a373de5efd7ddad04f397; unchanged database SHA256 2347a548429cd8bf07048e15898de1432c960d7a08743e17dc31d39efdb5bbaf. Active binding is /Library/GRRR/accounting-poc2/active.json; store_id 901acaff42b5a42f667b1c435beba9a9ae8312539cc36eb023c45584fd2e06d6. stopped=1, pending=3, historical_unknowns=unresolved, spendable=null, 11 reservations, 8 metering rows, 0 overhead rows. Known encumbered vector is [0,1108265788,0] in each cumulative scope; order is money_cents, execution_us, review_us. POC ceilings [5000,21600000000,3600000000]; milestone ceilings [15000,86400000000,10800000000]. Currency USD; integer dimensions only. Profiles synthetic, offline, trusted-observation, independent-replay share the original campaign/store; independent-replay is POC-only.

## USER INTENT
The operator needs a reviewable, conservative route out of registered frozen accounting without resetting cumulative budgets, erasing uncertainty, or accidentally authorizing research execution.

## Root Cause / Current Behavior
research/persistent_budget.py opens v2 read-only, validates registration, and require_mutable permits only unchanged v1 without registration artifacts. Accepted registration verify intentionally requires exact original stopped DB bytes/metadata/inventory. Merely clearing stopped, modifying SQL, removing registration, or changing version would violate this contract. No recovery command exists. Implement an explicitly reviewed successor transition, not an installer bypass or weakening of v2 validation.

## Affected Components and Boundary Map
PRODUCES:
- research/accounting_recovery.py -> NEW proposed recovery implementation with exact public API, schema, errors, authority checks and transition table documented and independently reviewed before any protected execution; no existing API is claimed here.
- research/persistent_budget.py -> PersistentBudget.require_mutable(self) -> None and validate_store(binding: dict, path: Path) -> None: recognize only the reviewed successor recovery state, retaining v1/v2 protections and conservative unknown/hold accounting.
- tests/unit_replay_accounting_recovery.py -> NEW no-guest regression suite for recovery transitions and mutation surfaces.
- docs/ACCOUNTING-RECOVERY.md -> NEW exact recovery contract, reviewed command grammar, authorization boundaries, before/after proof checklist and not-run live integration gate.

CONSUMES:
- GRRR-43i8: research/accounting_registration.py -> validate_binding(binding: dict, version: int = 1) -> None; validate_receipt(binding: dict, receipt: dict, old_raw: bytes, database: Path) -> None; verify() -> dict; inventory(path: Path, binding: dict) -> dict. verify returns {'binding': binding, 'receipt': receipt}; inventory requires stopped=1 and returns raw schema/rows, stopped, pending, known_encumbered, historical_unknowns, spendable, database_sha256. These are registration-only validators, not recovery permissions. Preserve original registration/prior-active bytes as immutable ancestry; do not call protected bootstrap in developer tests.
- GRRR-43i8: research/persistent_budget.py -> PersistentBudget(profile: str) -> None; reserve(self, principal: int, run: str, maximum: dict, key: str, stage: str = 'poc', binding: str = None) -> dict; require_mutable(self) -> None; authorize_sql(self, action: int, first: str, second: str, database: str, source: str) -> int. Existing usage PersistentBudget('independent-replay') must remain denied for mutations until valid separately authorized recovery; reservations never confer launch authority.
- Existing accepted accounting: research/budget.py -> Budget.meter(self, principal: int, reservation: str, usage: dict, evidence: str) -> dict; settle(self, principal: int, reservation: str, actual: dict) -> dict; disclose_overhead(self, principal: int, category: str, duration_us: int, key: str) -> None; totals(self, principal: int) -> dict. Recovering must enumerate these inherited mutation surfaces as well as reserve/halt and SQLite entrypoints.

Downstream integration context (not an upstream dependency): GRRR-z3w9 WIP research/replay.py preflight() -> None rejects version 2 and unknown versions before input access/namespace creation; this bug must not change replay preflight to accept an unreviewed successor. Downstream owns later integration with the reviewed contract. Existing WIP docs/INDEPENDENT-REPLAY-V3-REVIEW.md and docs/evidence/independent-replay/v3-no-guest/REPORT.md record 91 focused tests passing on both Pythons, full suites 248 executed with one class setup error each, nine conservative-genesis tests not executed, and live integration 0 executed due dedicated UID/GID setup. These are not passing full/live proof.

## Acceptance Criteria
1. [State/Event] Deliver the exact reviewed recovery transition contract and matching no-guest implementation: enumerate source/target binding schemas, authorized principal, exact action/source/plan/review/baseline hashes, stop disposition, allowed post-recovery mutations, lock order/writer quiescence, atomic publication/durability ordering, retry/idempotency, crash states and errors. No implicit recovery, automatic retry of uncertain effects, or automatic restart. Independent security/architecture review must cover the exact implementation bytes before requesting protected execution.
2. [Ubiquitous] Preserve original campaign/store/database device+inode, cumulative POC/milestone ceilings, usage, reservations/holds, settlements, metering/overhead, prior history and registration evidence. Keep all three pending holds encumbered and historical_unknowns=unresolved/spendable=null unless separately authenticated evidence permits a specifically reviewed reconciliation; this story grants no reconciliation or unknown-zeroing authority. No fresh DB/allowance, reset, history recast, implicit hold release, or blanket mutation exemption. Any proposed DB change is confined to the precisely authorized transition, never historical row rewriting.
3. [Event] Recovery produces an append-only, canonical, hash-bound recovery receipt linking the exact prior active binding, registration receipt, baseline inventory/identity, plan, independent review, explicit operator authorization and exact transition result. Retain immutable original registration/prior-active records and complete ancestry. Define receipts for uncertain/partial outcomes without pretending success; never overwrite an existing receipt or re-use a stale authorization.
4. [Unwanted] Missing/changed/duplicate/noncanonical receipt fields; stale active binding/plan/review/source; replaced inode/device; unsafe owner/mode/ACL/link; malformed schema/usage; unknown journal/partial artifacts; concurrent writer; interrupted publication; replayed authorization; stale handles and tampering must fail closed without unauthorized writes or allowance. Preserve v2 read-only behavior and legacy protections. Test inherited reserve/meter/settle/disclose_overhead/halt, raw connection/cursor execute/executemany/executescript, cached statements, PRAGMA/DDL/ATTACH, writable BLOB and stale handles. Unknown versions never become mutable by fallback.
5. [Authority] The package and no-guest tests have zero privileged effects. Any later protected staging/install/recovery/stop release requires a new explicit operator authorization bound to independently reviewed exact bytes/action and parent mediation. Registration authorization is not reusable. Recovery receipts/registration/reservations grant no replay, launch, promotion, admission, merge or production authority. No developer root/sudo/QEMU/VM or /Library/GRRR mutation is permitted.
6. Focused and full no-guest unit suites pass on BOTH /usr/bin/python3 and /opt/homebrew/bin/python3 with exact commands, versions, exit codes, executed counts, failures/errors/skips and source hashes recorded. Include success transitions, denied transitions, conservative holds/unknowns, ceiling boundaries, repeated recovery/idempotency and negative cases in AC4. Never skip mandatory tests or lower fixed disk floors; any setup error, unmet prerequisite or unexecuted class remains blocked, not green.
7. Later separately reviewed parent integration proof is a mandatory distinct live gate: only after exact separate authorization, independently verify protected before/after identities, hashes, owners/modes/ACLs, locks/quiescence, receipt ancestry, allowed transition, unchanged historical accounting/holds/unknowns and fail-closed behavior. Integration tests: MANDATORY (no mocks), including a real permitted recovery success path and refusal paths using authorized controlled state. This story's no-guest delivery cannot claim live acceptance or unblock actual replay by itself. If authorization/prerequisites are absent, leave live proof pending and do not accept the story as fully recovered; GRRR-z3w9 remains gated on all its separate capacity, identity, review and replay approvals.

## Testing Requirements
- Run each interpreter with -m unittest discover -s tests -p 'unit_replay_accounting_recovery.py'; -m unittest discover -s tests -p 'unit_replay_accounting_registration.py'; -m unittest discover -s tests -p 'unit_*.py'. Retain current registration regressions unchanged in intent. Extend existing tests only where the independently reviewed successor contract requires it; never weaken frozen-v2 assertions.
- No-guest tests may use temporary local SQLite/filesystem state; no protected paths or privilege changes. Test actual transition/file/SQLite behavior rather than mocking away integrity or authority checks. Integration evidence cannot be substituted with mocks or unit results.
- Parent integration command grammar and test command are deliverables of the exact reviewed implementation; none exists or is authorized by this story. Real replay/E2E remain GRRR-z3w9 and epic GRRR-6sso gates, not recovery test substitutes.

## OUT OF SCOPE
- Protected staging/install/recovery/stop release execution: separate exact operator authorization and parent integration gate above; never developer execution.
- Independent replay, VM/QEMU, promotion/admission/production mutation: GRRR-z3w9 and downstream/epic gates; recovery does not grant these capabilities.
- Disk cleanup/floor changes, dedicated UID/GID provisioning, unrelated vault fixes: separate operator-governed prerequisites; no scope bundling or bypass here.
- New allowance, historical reconstruction without evidence, unknown-zeroing, raw SQL workaround, deleting registration, commit/push: never authorized by this story.

## DIFF BUDGET
- Approximately 4-6 files, under 900 changed LOC including implementation, focused tests and exact contract documentation. Gross overrun requires PM investigation, not silent scope expansion. Preserve concurrent edits; downstream replay wiring is not this package.

## MANDATORY SKILLS
- developer, pvg, nd; codebase-memory for structural exploration with source fallback on stale coverage; independent security/architecture review before any protected effects; pm_acceptor for evidence-based acceptance.

## Delivery Requirements
- Deliver exact diff/source hashes, independent review artifact, transition/receipt contract, both-interpreter raw test outputs and AC verification table; use pvg story deliver, never self-accept. Record package readiness separately from protected integration status. No skipped tests, fabricated proof or claims of recovery from registration success.

## Discovered During
GRRR-z3w9 at WIP 3869e0ff223bae5d4ae75080f33d4b6ba33efacc, consuming accepted GRRR-43i8 registration-only implementation.

## nd_contract
status: new

### evidence
- Created 2026-10-24 from verified tracker/source context. Scope: exactly one P0 recovery implementation package; no protected action authorized or performed.

### proof
- [ ] AC1-5: Exact reviewed implementation/receipt/authority contract and conservative failure semantics.
- [ ] AC6: Focused and full tests pass on both required Pythons with measured evidence.
- [ ] AC7: Later separately reviewed and authorized parent live integration proof; currently NOT RUN.

## Acceptance Criteria


## Design


## Notes


## History
- 2026-10-24T20:19:06Z dep_added: blocked_by GRRR-43i8
- 2026-10-24T20:19:11Z dep_added: blocks GRRR-z3w9

## Links
- Parent: [[GRRR-2t3h]]
- Blocks: [[GRRR-z3w9]]
- Blocked by: [[GRRR-43i8]]

## Comments
