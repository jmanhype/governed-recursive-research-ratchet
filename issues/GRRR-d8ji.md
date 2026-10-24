---
id: GRRR-d8ji
title: "Bug: registered independent-replay accounting lacks recovery implementation"
status: blocked
priority: 0
type: bug
parent: GRRR-2t3h
created_at: 2026-10-24T20:19:06Z
created_by: speed
updated_at: 2026-10-24T20:47:01Z
content_hash: "sha256:667a78cf17b63fda4b2379c5193c56e922fa8b0847ed4993fafe7b36d313ae1b"
blocked_by: [GRRR-43i8]
blocks: [GRRR-z3w9]
follows: [GRRR-43i8, GRRR-w1lt]
labels: [blocked]
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
## Authorized WIP Commit — NOT DELIVERED

- Operator explicitly authorized committing the independently reviewed GRRR-d8ji stop-only recovery WIP to story/GRRR-d8ji. Authorization expressly excludes delivery/acceptance, merge, protected recovery, stop release, replay, promotion, admission, production mutation and push.
- Independent review: SECURITY_REVIEW: READY_FOR_COMMIT_REVIEW. Reviewer found no blocking security/architecture defect and independently reran recovery 20/20 and registration 30/30 on both required Pythons. This is not execution approval; crash-durability testing is not exhaustive kill/power-loss/fsync proof.
- Verified all seven reviewed hashes before editing via shasum -a 256 -c /tmp/grrr-d8ji-reviewed.sha256: 7/7 OK. Only docs/evidence/accounting-recovery/REPORT.md was updated to record review/authorization; reviewed source/test/contract bytes and raw logs remain unchanged.
- Commit: caf08f31e07138c8d49e29b916cbf6b67d3483a6, branch story/GRRR-d8ji. Six intended files, 859 insertions and 11 deletions. Worktree clean after commit. No push.
- Updated REPORT.md SHA256: 71adb09aec066034c3fdeda7ea540a5c95d6103c972fe0183e77f8df1950404e.
- git diff --check and git diff --cached --check passed. Explicit-path pvg verify passed: 4 code/test files scanned, 0 issues. No source changes or test reruns in this commit-only turn; existing final test evidence applies to unchanged source hashes.
- Full-suite blockers remain unchanged: Python3.9 239 executed, 1 smoke-cessation failure and 1 ConservativeGenesis setup error; Python3.14 239 executed, 1 setup error. Nine class tests unexecuted per interpreter; fixed disk floor unchanged. Focused 20 recovery + 30 registration passed per interpreter. Live integration 0 executed. No protected effects.

## nd_contract
status: new

### evidence
- Authorized reviewed WIP commit caf08f31e07138c8d49e29b916cbf6b67d3483a6 preserved; exact source hashes and raw evidence recorded in committed REPORT.md.
- Claim released after evidence update; story remains open, not delivered or accepted.

### proof
- [x] Commit-only authorization fulfilled without changing reviewed implementation/test/contract bytes.
- [x] Independent review READY_FOR_COMMIT_REVIEW recorded with limitations.
- [ ] AC6: Full-suite blockers and unexecuted tests remain.
- [ ] AC7: Separate protected integration authorization and live proof remain pending.

## Implementation Evidence (BLOCKED WIP, not delivered)

PROOF:
- Base HEAD: 6afd643df51aa6a2f046512dfc3fbe7572dd8d67, branch story/GRRR-d8ji. No implementation commit: coordinator explicitly withheld commit authorization pending direct operator approval. No push, root/sudo, protected inspection/mutation, guest, replay, admission or promotion.
- Exact commands and hashes are in docs/evidence/accounting-recovery/REPORT.md (SHA256 47f7521ee83b96d5435e605212b07aa09ac2e14d2512e6045f09fced49e68026).
- Complete raw initial/final logs: /Users/speed/Documents/Codex/2026-10-19/3e4m-b-4/outputs/grrr-d8ji-no-guest/no-guest.txt, SHA256 aa41940ba6288b4a97642188a7b95ed67f32e2e3a26894dd872180034b99015d.
- Both /usr/bin/python3 (3.9.6) and /opt/homebrew/bin/python3 (3.14.3): -m unittest discover -s tests -p unit_replay_accounting_recovery.py -> 20 tests, 0 failures/errors/skips, exit0; registration pattern unit_replay_accounting_registration.py -> 30 tests, 0 failures/errors/skips, exit0.
- Full command for each: -m unittest discover -s tests -p 'unit_*.py'. Python3.9: 239 executed, 1 failure and 1 class-setup error, exit1. Python3.14: 239 executed, 0 failures and 1 class-setup error, exit1. Nine ConservativeGenesis tests unexecuted per interpreter; zero explicit skips. No warnings in final runs. Not a clean full-suite result.
- Both interpreters: -m py_compile research/accounting_recovery.py research/accounting_registration.py research/persistent_budget.py tests/unit_replay_accounting_recovery.py -> exit0.
- pvg verify research/accounting_recovery.py research/accounting_registration.py research/persistent_budget.py tests/unit_replay_accounting_recovery.py docs/ACCOUNTING-RECOVERY.md docs/evidence/accounting-recovery/REPORT.md --format=text -> PASSED, 4 files scanned, 0 issues, exit0. git diff --check -> exit0.
- Coverage instrumentation: not measured. Live integration: 0 executed. Independent exact-byte security/architecture review: pending coordinator reviewer.

AC verification:
1. Exact stop-only v3 contract and implementation drafted; independent review pending.
2. Same-inode/history, three pending holds at exact ceiling, unresolved/null uncertainty tested. All post-recovery runtime writes remain denied.
3. Append-only canonical intent/result/completion/uncertainty and original ancestry implemented and tested.
4. Fail-closed authority/baseline/source/receipt/identity/partial/concurrency/runtime-surface checks tested; independent review pending.
5. No privileged effects. No recovery/replay execution authorized or performed.
6. BLOCKED by failed full-suite prerequisites and smoke failure; no tests skipped or floors lowered.
7. PENDING separate operator-authorized parent live success/refusal integration. Package tests do not claim recovery acceptance.

DISCOVERED_BUG:
  title: Full no-guest verification blocked by conservative-genesis disk prerequisite
  context: Both full suites fail ConservativeGenesis.setUpClass with RuntimeError preparation space floor; fixed threshold is 15350000000 bytes, measured about 12GiB free. Nine class tests remain unexecuted per interpreter. No cleanup/floor changes authorized.
  affected_files: scripts/conservative-genesis:85; tests/unit_conservative_genesis.py:25
  discovered_during: GRRR-d8ji

DISCOVERED_BUG:
  title: Term-resistant smoke process group cessation fails under Python3.9 full suite
  context: test_real_term_resistant_group_is_killed_within_deadline fails at tests/unit_replay_smoke.py:153, False != True from cease_groups. Python3.14 full run does not reproduce. No replay/timing/assertion changes made.
  affected_files: tests/unit_replay_smoke.py; research/replay_smoke.py
  discovered_during: GRRR-d8ji

LEARNINGS:
- Stop release is not spendability; unresolved history requires v3 read-only behavior and empty allowed runtime mutation set.
- Fixed initial sys.path import-closure regression via fixed-file importlib loading, and Python3.14 test SQLite ResourceWarning via explicit closing. Initial failure logs retained, final source hashes are distinguished.
- Worktree pvg notes search failed because .vault is missing; no unrelated vault repair attempted. Graph only indexed stale downstream worktree, so accounting sources were read directly.
- Raw logs retained outside package to preserve approximate diff budget without deleting failed evidence.

## History
- 2026-10-24T20:19:06Z dep_added: blocked_by GRRR-43i8
- 2026-10-24T20:19:11Z dep_added: blocks GRRR-z3w9
- 2026-10-24T20:19:47Z status: open -> in_progress
- 2026-10-24T20:19:47Z auto-follows: linked to predecessor GRRR-43i8
- 2026-10-24T20:19:47Z claimed by dev-GRRR-d8ji
- 2026-10-24T20:36:35Z status: in_progress -> open
- 2026-10-24T20:36:35Z released by speed
- 2026-10-24T20:44:56Z status: open -> in_progress
- 2026-10-24T20:44:56Z auto-follows: linked to predecessor GRRR-w1lt
- 2026-10-24T20:44:56Z claimed by dev-GRRR-d8ji
- 2026-10-24T20:45:32Z status: in_progress -> open
- 2026-10-24T20:45:32Z released by speed
- 2026-10-24T20:47:01Z status: open -> blocked

## Links
- Parent: [[GRRR-2t3h]]
- Blocks: [[GRRR-z3w9]]
- Blocked by: [[GRRR-43i8]]
- Follows: [[GRRR-43i8]], [[GRRR-w1lt]]

## Comments

### 2026-10-24T20:33:42Z speed
BLOCKED: Final no-guest package verification is not clean: both full suites execute 239 tests with ConservativeGenesis disk-floor setup error and nine class tests unexecuted; Python 3.9 additionally fails term-resistant smoke process-group cessation. Independent exact-byte review and separate commit authorization are pending; live integration 0 executed. WIP and exact hashes/counts retained in docs/evidence/accounting-recovery/REPORT.md; complete raw logs at /Users/speed/Documents/Codex/2026-10-19/3e4m-b-4/outputs/grrr-d8ji-no-guest/no-guest.txt (SHA256 aa41940ba6288b4a97642188a7b95ed67f32e2e3a26894dd872180034b99015d). No delivery or privileged effects.

### 2026-10-24T20:40:28Z speed
## Independent Security/Architecture Review

SECURITY_REVIEW: READY_FOR_COMMIT_REVIEW

- Reviewed the current uncommitted package bytes in dev-GRRR-d8ji. No blocking security/architecture defect was found in the stop-only v3 design.
- Reviewer confirmed the SQL transition preserves original database inode/schema/history/holds; introduces no fresh allowance or reconciliation; binds exact canonical plan/review/operator records; keeps v3 runtime read-only; denies inherited mutators, SQL, writable BLOBs, and stale registered handles; and preserves v2 stopped-only verification.
- Reviewer independently reran focused recovery and registration suites: 20/20 and 30/30 on both required Pythons. git diff --check passed.
- This is not delivery acceptance, protected recovery approval, or replay authorization. Full-suite disk-floor errors/unexecuted tests and the Python 3.9 smoke cessation failure still block delivery. Crash-durability coverage is limited to tested publication stages, not exhaustive kill/power-loss/fsync failure.
- Exact reviewed SHA256 values include accounting_recovery.py 88cf699236288ba989fcb2b21e5966720faadc13f420c83c0f64e99bade8760a and ACCOUNTING-RECOVERY.md 88635272ae4f4b7d475f5832bcdb56b265cb2d512f97e3ca1faee6f962521e8c; the reviewer report in the thread lists the complete set.

## nd_contract
status: new

### evidence
- Independent reviewer performed no edits or privileged operations.

### proof
- [x] Current package is security-review ready for commit review.
- [ ] Commit authorization is explicitly withheld by the story and has not yet been supplied.
- [ ] Full-suite blockers remain.
- [ ] Protected integration remains separately authorized/not-run.
