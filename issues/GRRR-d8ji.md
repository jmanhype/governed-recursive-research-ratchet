---
id: GRRR-d8ji
title: "Bug: registered independent-replay accounting lacks recovery implementation"
status: closed
priority: 0
type: bug
parent: GRRR-2t3h
created_at: 2026-10-24T20:19:06Z
created_by: speed
updated_at: 2026-10-25T16:58:24Z
content_hash: "sha256:94b7f3913c69a7112243867c4029d5f954f4f256d7a75413df42756543ece984"
blocked_by: [GRRR-43i8]
follows: [GRRR-43i8, GRRR-w1lt, GRRR-bnkf, GRRR-c875, GRRR-my5n, GRRR-gu87, GRRR-90te]
labels: [blocked, accepted]
assignee: dev-GRRR-d8ji
closed_at: 2026-10-25T16:58:05Z
close_reason: "Accepted: independent full re-review verifies AC1-7, exact-byte no-guest and parent stop-only integration proof, and corrected current/historical documentation. No replay, reconciliation, merge or production authority."
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


## nd_contract
status: accepted

### evidence
- PM closeout applied via pvg story accept on 2026-10-25.

### proof
- [x] Story closed after accepted label was applied.


## PM Decision
ACCEPTED [2026-10-25]: Independent full evidence-based re-review of 0fa26e4cf6f0c35b19fb6f1f75259932b00a086e closes both DOCS_STALE blockers and the documentation-freshness gate. Runtime-smoke documents phase-local TERM uncertainty reset only on entering KILL, fresh timely absence, persistent/invalid/deadline failures; architecture accurately distinguishes installed stop-only v3 from workflow approval and preserves unresolved/null uncertainty, history/holds and denied runtime writes. Eight-doc generalized historical scoping and links reviewed.

Reviewed full story/diff and unchanged implementation/authority/ancestry against all seven ACs. Fresh static ladder: no stub markers; public production APIs typed; no new config or cross-cutting bypass. Seven source/test hashes independently match prior exact-byte reviews. Fresh four documentation check runs PASS48/48, zero failures; git diff --check PASS and worktree clean. verify-delivery PASS9/9. Both external manifests rehashed9/9 OK; raw full/focused proof hash b2825f94a76a2d04969b993942c80b7e4b5906d19dddeae848219d25ad4eb433 retained and trustworthy: each required interpreter253 full,20 recovery,30 registration passed without skips/errors/warnings. No implementation test rerun needed for unchanged sources. Separately authorized real parent install/verify success, consumed-authority refusal and12/12 UID320 mutation refusals substantiate AC7; no protected operations repeated by PM. Diff overrun explained by bounded independently reviewed cessation prerequisite fix, docs and evidence, not replay wiring. Coverage percentage explicitly not measured.

## nd_contract
status: accepted

### evidence
- Independent PM reviewed exact delivery0fa26e4, unchanged source hashes, test raw evidence and protected success/refusal manifests.
- Fresh docs48/48, delivery9/9 and manifests9/9; both previous documentation contradictions corrected.

### proof
- [x] AC1: Exact independently reviewed transition/authority/lock/publication/crash contract and source.
- [x] AC2: Original identity/history/ceilings/three holds and unresolved/null uncertainty preserved.
- [x] AC3: Canonical immutable ancestry, append-only success/uncertain receipts.
- [x] AC4: No-guest negative cases and controlled real duplicate/API/SQL/BLOB refusals fail closed.
- [x] AC5: Separate parent authorization, no developer privileged effects, no downstream authority.
- [x] AC6: Both required interpreter full/focused raw passing proof verified against unchanged source.
- [x] AC7: Distinct separately authorized real success/refusal gate recorded; no replay or reconciliation approved.
- [x] Documentation freshness: both blockers and adjacent historical records reconciled.

## nd_contract
status: delivered

### evidence
- Transitioned via pvg story deliver on 2026-10-25.

### proof
- [ ] Developer evidence block must remain authoritative above this contract.


## nd_contract
status: rejected

### evidence
- PM rejection applied via pvg story reject on 2026-10-25.

### proof
- [ ] Story requires another developer delivery before it can be accepted.


## nd_contract
status: delivered

### evidence
- Transitioned via pvg story deliver on 2026-10-25.

### proof
- [ ] Developer evidence block must remain authoritative above this contract.


## Implementation Evidence (DELIVERED)

PROOF:

### Scope and commits
- Branch story/GRRR-d8ji; documentation delivery SHA 734554707374f10c3c17b1e788d6fa2c3678bdd4, parent implementation SHA 65bb7945299851c078f5b48e9083d3aee13a7c4a. Clean after commit. Exactly docs/ACCOUNTING-RECOVERY.md and docs/evidence/accounting-recovery/REPORT.md changed: 127 insertions, 18 deletions. No implementation/test/protected-state changes.
- Operator authorization permits documentation, story commit/delivery and independent PM review only. No merge, push, reconciliation, replay, promotion, admission or production mutation; no root/sudo or protected action in this delivery turn.

### CI/Test Results
- Fresh command on BOTH /usr/bin/python3 and /opt/homebrew/bin/python3: INTERPRETER /tmp/grrr-d8ji-doc-check.py. Each PASS 12 checks, 0 failures. Checks validate document fences/conflict markers/local link, exact current hashes/boundaries, all nine external manifest files and 12/12 refusal probe inventory. No skips.
- pvg verify docs/ACCOUNTING-RECOVERY.md docs/evidence/accounting-recovery/REPORT.md --format=text: exit0, VERIFY: PASSED (0 files scanned, 0 issues). Markdown is not scanned by that code verifier; the explicit documentation/evidence checks above supply substantive static validation.
- git diff --check and git diff --cached --check: exit0. shasum -a 256 -c protected-recovery-SHA256SUMS and shasum -a 256 -c refusal-proof-SHA256SUMS from external recovery-staging evidence directory: all 9 entries OK, 0 mismatches. Implementation/test source hashes independently unchanged.
- No unit-suite rerun for these two documentation-only changes. Preserved and hash-verified final implementation evidence: /Users/speed/Documents/Codex/2026-10-19/3e4m-b-4/outputs/grrr-d8ji-no-guest/cessation-final.txt SHA256 b2825f94a76a2d04969b993942c80b7e4b5906d19dddeae848219d25ad4eb433. At implementation SHA65bb794, both /usr/bin/python3 3.9.6 and /opt/homebrew/bin/python3 3.14.3 ran: -m unittest discover -s tests -p unit_replay_accounting_recovery.py (20/20); -m unittest discover -s tests -p unit_replay_accounting_registration.py (30/30); -m unittest discover -s tests -p 'unit_*.py' (253/253); cessation suite5/5, smoke12/12 and exact cessation case5/5 repetitions each. All final commands exit0, zero failures/errors/skips/warnings; all nine genesis tests executed. Compilation passed. These are recorded implementation results, not fresh reruns at docs commit.
- Coverage: instrumentation percentage not measured; AC verification 7/7 documented; no fabricated coverage score. Full unit suite had no omissions at implementation verification. Real replay/E2E deliberately not executed or authorized.

### Exact source and protected evidence
- recovery source88cf699236288ba989fcb2b21e5966720faadc13f420c83c0f64e99bade8760a; registration source db2d5965a78443fcd4205f8c73950ab0649876624fadfd79a17de086f3b1a038; persistent budget78f0e145d902dbeadbb1693055551dfdf59aee16d1bc2d5fd4bc4c403bcaaf32; recovery test ff52097fa7ba0002ea9df2600afbc388a46a48efa3c8c08718f011f135281d5e.
- Independent review recorded in story: final exact-byte follow-up READY_FOR_PROTECTED_RECOVERY_REVIEW and APPROVED_STOP_ONLY_RECOVERY_PLAN. Review bound baseline dfc4bfcfd56a2fe8cfbc4416f912829b35e2dced5c31b23f181cbed38f63b73f, plan478cbae360092c5b6a9659516be75b0a2c7e9d9741509bfbb8b4d6468f77307e, review94f9b8113b2b08595783d16223a2c10cdcde6b79de5c09076de1075de5fbec81; separate operator authorization9235640b58b973913e9b14f2ade420085daeed91a1e048ad5b2b09da41079a60.
- Raw parent evidence directory /Users/speed/Documents/Codex/2026-10-19/3e4m-b-4/outputs/grrr-d8ji-recovery-staging/: recovery-install.json and recovery-verify.json SHA25656476efca0fd6f379cca965eee5ebd0efe2ae1d0e97bc98f01a8a76c717df974; v3-protected-postflight.log18ba02d0e4044b2775abd09d6ddc06dd6834948ec6ff9d629a63f67dde5ce928; duplicate-install-refusal.log ccb69d1cf62fa6ec865b96b43dbf05bddc63ab2948292acbd7879b9ed34474ec; duplicate-install-refusal-summary.log22202128007a20adf323ab8c6b00917c5e578bed0741142aea0c6ebf3f4baf0b; v3-refusal-probe.json6caf3d9be0aacb175aa1cbc4d115f0cc646c61135ef7015970181641191efdb1; refusal-proof-postflight.log18ba02d0e4044b2775abd09d6ddc06dd6834948ec6ff9d629a63f67dde5ce928. Private rows remain external.
- Parent PINNED_PYTHON -I -S -B /Library/GRRR/bootstrap/recovery/accounting_recovery.py install PLAN REVIEW AUTHORIZATION AUTHORIZATION_SHA256 and verify: recorded success exit0 each, not rerun. Repeating install with consumed authorization: expected exit1 partial/unknown registration state. Controlled UID320 probe: 12/12 API/connection/cursor/BLOB mutations refused, protected_state_changed=false. These are expected denials, not unaddressed failures.
- Active v3 SHA2569c5194dd12ff7601917fcccc293c459db09a41da8bad9fa9983cbef618d453f8; recovery receipt6d3d5b092c0ee8273a657c83823d8465b215f2b1b66ec627dfde2d96b21fe587; DB9c6ff2561a364ed982cd5477dd4b200c995da6910c9a17aa3d3c411a962d64f3. Original inode682589447; state1|0; reservations11, metering8, overhead0, pending3; known encumbered [0,1108265788,0] both scopes; historical_unknowns unresolved, spendable null, allowed mutations empty, execution_authorized false. No unknown-zeroing or allowance.

### AC Verification
| AC | Requirement / location / evidence | Status |
|---|---|---|
| 1 | docs/ACCOUNTING-RECOVERY.md exact APIs/schemas/locks/publication/crash contract; research/accounting_recovery.py; independent exact-source/plan review and real stop-only result | PASS |
| 2 | research/accounting_recovery.py unchanged inventory checks; unit_replay_accounting_recovery.py and parent before/after postflights retain identity/history/ceilings/3 holds/unresolved uncertainty | PASS |
| 3 | canonical intent/receipt/complete ancestry, immutable v2 prior/registration; focused real-file transition tests and protected receipt/postflight | PASS |
| 4 | focused recovery20/registration30 cases each Python, inherited/raw SQL/BLOB/stale/tamper/lock guards; duplicate refusal and 12/12 controlled live refusals; no unlimited crash proof claimed | PASS |
| 5 | no-guest developer package/tests unprivileged; later protected effects separately reviewed, authorized and parent-mediated; no replay/production authority | PASS |
| 6 | final unchanged implementation full253/253 each required Python and focused gates; exact raw log/hash/commands above; zero errors/failures/skips/warnings | PASS |
| 7 | distinct authorized parent install/verify success plus duplicate/runtime refusal proof, ancestry/identity/inventory postflights; docs/evidence/accounting-recovery/REPORT.md current section; downstream replay remains independently gated | PASS |

LEARNINGS:
- Stop release and spendability are different: stopped=0 still means read-only v3, unresolved unknowns and null spendable; never infer execution permission.
- Label superseded pre-install/full-suite blocks as historical while preserving raw failures and their exact checkpoint provenance.
- pvg verify reports zero scanned files for Markdown; pair its structural pass with explicit document/evidence hash checks rather than claiming code scanning.
- Worktree vault notes search still fails due absent worktree .vault; no unrelated repair attempted. Existing relevant context was available from live shared nd story.

DISCOVERED_BUG:
  title: Worktree vault knowledge search resolves missing local .vault
  context: pvg notes search 'accounting recovery' exits1 with vlt vault directory not found at dev-GRRR-d8ji/.vault, while pvg nd correctly resolves shared git-common-dir vault. Existing known blocker reproduced; no unrelated vault changes.
  affected_files: Paivot notes/vlt worktree routing (external toolchain)
  discovered_during: GRRR-d8ji

## nd_contract
status: delivered

### evidence
- Docs commit734554707374f10c3c17b1e788d6fa2c3678bdd4; exact implementation/source evidence unchanged; static checks12/12 each Python and manifest9/9 pass. Implementation full253/253 each; protected stop-only success and refusal proof recorded separately.

### proof
- [x] AC #1: Reviewed exact conservative transition implemented and documented.
- [x] AC #2: Original cumulative identity/history/holds/unknowns preserved.
- [x] AC #3: Canonical append-only recovery ancestry recorded.
- [x] AC #4: Fail-closed unit and controlled live refusals verified.
- [x] AC #5: Separate authority boundaries retained; no unauthorized protected effects.
- [x] AC #6: Both required interpreter suites pass with measured artifacts.
- [x] AC #7: Separately authorized parent live stop-only success/refusal gates recorded; no replay authority.

## Post-reboot focused cessation fix — no-guest gates PASS

PROOF:
- Authorized focused commit: 65bb7945299851c078f5b48e9083d3aee13a7c4a on story/GRRR-d8ji, parent caf08f31e07138c8d49e29b916cbf6b67d3483a6. Clean worktree. Four files: research/replay_smoke.py (phase-scoped uncertainty and post-inventory deadline check), scripts/replay-root-prepare (one source hash pin), new tests/unit_replay_cessation.py and evidence REPORT.md.
- Actual historical host-specific trigger remains unproven: exact Python3.9 test passed 5/5 before editing; instrumented real run showed normal TERM/KILL/absence. Deterministic single TERM observation TimeoutExpired reproduced False!=True with the same unchanged real process-group helper. Global uncertainty poisoned a later valid KILL/absence proof; uncertainty now resets only on entering KILL. A second regression proves late inventory cannot claim success beyond deadline. Persistent unknown KILL observation still fails closed. No assertions, TERM5/KILL2/total7s/ps0.2s limits or disk floors changed.
- RED: /usr/bin/python3 -m unittest discover -s tests -p unit_replay_cessation.py ran5, failed2 before fix. GREEN same command ran5/pass both Pythons.
- Final commands run on BOTH /usr/bin/python3 (3.9.6) and /opt/homebrew/bin/python3 (3.14.3):
  - -m unittest tests.unit_replay_smoke.RuntimeSmoke.test_real_term_resistant_group_is_killed_within_deadline, five repetitions per interpreter: all5 pass.
  - -m unittest discover -s tests -p unit_replay_cessation.py: 5/5 pass.
  - -m unittest discover -s tests -p unit_replay_smoke.py: 12/12 pass.
  - -m unittest discover -s tests -p unit_replay_accounting_recovery.py: 20/20 pass.
  - -m unittest discover -s tests -p unit_replay_accounting_registration.py: 30/30 pass.
  - -m unittest discover -s tests -p 'unit_*.py': 253/253 pass, all nine ConservativeGenesis tests executed.
  - -m py_compile research/replay_smoke.py tests/unit_replay_cessation.py scripts/replay-root-prepare: exit0.
- All final runs: exit0, zero failures/errors/skips/warnings. Coverage instrumentation not measured.
- pvg verify research/replay_smoke.py tests/unit_replay_cessation.py scripts/replay-root-prepare docs/evidence/accounting-recovery/REPORT.md --format=text: PASS, 2 code/test files scanned, 0 issues. git diff --check and staged diff check PASS.
- Final raw evidence: /Users/speed/Documents/Codex/2026-10-19/3e4m-b-4/outputs/grrr-d8ji-no-guest/cessation-final.txt SHA256 b2825f94a76a2d04969b993942c80b7e4b5906d19dddeae848219d25ad4eb433. Initial diagnostics, RED and stale-pin failures retained beside it; exact hashes in committed docs/evidence/accounting-recovery/REPORT.md.
- Source hashes: replay_smoke.py 819ab8e37ebaf138eca6b69abee78bf356124809b64ca60c28ecd5b957749612; unit_replay_cessation.py d3ee8811a442d02936ee39c4eb16c608c12f4caeba8f163158841f461737bbd2; replay-root-prepare 5908b3134f2cc13bc6c10e046630c0e0bfe8742618acc36a75be855e6b645a8c.
- Live integration0 executed. No root/sudo, protected reads/writes, recovery, stop release, guest/replay, promotion, admission, production mutation, merge or push. Earlier independent package review is not claimed as review of this subsequent cessation fix.

LEARNINGS:
- Observation uncertainty is phase-local: a bad TERM observation requires KILL; fresh verified post-KILL absence can prove cessation, while unknown or late KILL observations cannot.
- Source hash pins must change with their source; unchanged closure tests correctly caught the stale pin before the final clean run.
- Keep deterministic failure reproduction distinct from an unproven intermittent host-specific cause.

## nd_contract
status: new

### evidence
- Focused fix committed at 65bb7945299851c078f5b48e9083d3aee13a7c4a; no-guest proof clean on both required interpreters. Claim released; no delivery/acceptance.

### proof
- [x] AC6: Focused/full no-guest suites pass on both Pythons, no unexecuted classes/skips.
- [x] Deadline exhaustion and persistent uncertain observation remain failures; real KILL/absence success proven.
- [ ] Independent review of later cessation fix is separate from the earlier package review.
- [ ] AC7: Separately authorized parent live integration remains pending; no recovery accepted.

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
- 2026-10-24T22:30:36Z status: blocked -> in_progress
- 2026-10-24T22:30:36Z auto-follows: linked to predecessor GRRR-bnkf
- 2026-10-24T22:30:36Z claimed by dev-GRRR-d8ji
- 2026-10-24T22:38:40Z status: in_progress -> open
- 2026-10-24T22:38:40Z released by speed
- 2026-10-24T22:39:53Z status: open -> blocked
- 2026-10-25T16:47:31Z status: blocked -> in_progress
- 2026-10-25T16:47:31Z auto-follows: linked to predecessor GRRR-c875
- 2026-10-25T16:47:31Z claimed by dev-GRRR-d8ji
- 2026-10-25T16:50:17Z status: in_progress -> in_progress
- 2026-10-25T16:50:17Z auto-follows: linked to predecessor GRRR-my5n
- 2026-10-25T16:53:57Z status: in_progress -> open
- 2026-10-25T16:53:57Z released by speed
- 2026-10-25T16:55:07Z status: open -> in_progress
- 2026-10-25T16:55:07Z auto-follows: linked to predecessor GRRR-gu87
- 2026-10-25T16:55:07Z claimed by dev-GRRR-d8ji
- 2026-10-25T16:56:40Z status: in_progress -> in_progress
- 2026-10-25T16:56:40Z auto-follows: linked to predecessor GRRR-90te
- 2026-10-25T16:58:06Z status: in_progress -> closed
- 2026-10-25T16:58:06Z dep_removed: no_longer_blocks GRRR-z3w9

## Links
- Parent: [[GRRR-2t3h]]
- Blocked by: [[GRRR-43i8]]
- Follows: [[GRRR-43i8]], [[GRRR-w1lt]], [[GRRR-bnkf]], [[GRRR-c875]], [[GRRR-my5n]], [[GRRR-gu87]], [[GRRR-90te]]

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

### 2026-10-24T20:47:01Z speed
## Authoritative Commit-Only Result

Operator authorization was exact: commit the independently reviewed stop-only recovery WIP package; do not deliver/accept, merge, recover protected state, release stop, replay, promote, admit, mutate production, or push.

Result:
- Story commit: caf08f31e07138c8d49e29b916cbf6b67d3483a6
- Subject: feat(GRRR-d8ji): preserve reviewed stop-only recovery WIP
- Six package files committed: 859 insertions, 11 deletions.
- Worktree clean. Story branch is not merged into epic/GRRR-2t3h.
- All seven independently reviewed source/test/contract hashes were verified unchanged after commit.
- Updated committed evidence REPORT.md records independent SECURITY_REVIEW: READY_FOR_COMMIT_REVIEW and the exact commit authorization; its SHA256 is 47f7521ee83b96d5435e605212b07aa09ac2e14d2512e6045f09fced49e68026.
- Complete raw no-guest logs remain external at outputs/grrr-d8ji-no-guest/no-guest.txt SHA256 aa41940ba6288b4a97642188a7b95ed67f32e2e3a26894dd872180034b99015d.
- Protected active/prior/receipt hashes remained unchanged; no privileged effect occurred.

Story remains BLOCKED and not delivered because:
1. both full suites have ConservativeGenesis disk-floor setup errors and nine unexecuted class tests;
2. Python 3.9 has a separate term-resistant process-group cessation failure;
3. separately authorized live recovery integration is 0 executed;
4. protected recovery/stop release/replay/promotion/admission remain denied.

## nd_contract
status: blocked

### evidence
- Commit-only authorization fulfilled; claim released.

### proof
- [x] Independently reviewed WIP preserved on story/GRRR-d8ji.
- [ ] AC6 clean full-suite proof remains unmet.
- [ ] AC7 protected live integration remains not-run.
- [ ] No delivery, acceptance, merge, recovery, replay, promotion, admission, production mutation, or push.

### 2026-10-24T21:35:19Z speed
## Operator-Authorized Host Reboot

The operator explicitly requested a host reboot after the authorized cache cleanup, Chrome/Spotify quit, and macOS purge failed to clear the fixed 15,350,000,000-byte preparation floor. Expected purpose is to release swap/transient memory and process/filesystem pressure without deleting more files or changing thresholds.

Pre-reboot state:
- epic/GRRR-2t3h clean at 6afd643df51a6a2f046512dfc3fbe7572dd8d67.
- story/GRRR-d8ji clean at caf08f31e07138c8d49e29b916cbf6b67d3483a6.
- GRRR-d8ji remains blocked/not delivered; GRRR-z3w9 remains blocked.
- No protected recovery, stop release, replay, promotion, admission, production mutation, merge, or push is authorized or performed.

## nd_contract
status: blocked

### evidence
- Reboot requested after recorded capacity failures.

### proof
- [ ] Post-reboot free space, swap, disk-floor suite, and Python 3.9 smoke test require remeasurement.

### 2026-10-24T22:30:36Z speed
## Post-Reboot Verification

The operator completed the authorized reboot. Live boot state was confirmed about 53 minutes after boot.

Capacity recovery:
- Free space rose from roughly 12.2 GB before reboot to 23,303,909,376 bytes after reboot.
- Swap usage fell from roughly 3.6 GiB to 0 bytes.
- Both required interpreters reran the exact ConservativeGenesis suite after reboot:
  - /usr/bin/python3: 9/9 passed, exit 0.
  - /opt/homebrew/bin/python3: 9/9 passed, exit 0.
- The disk/preparation-space blocker is cleared.

Remaining blocker:
- The exact Python 3.9 test `tests.unit_replay_smoke.RuntimeSmoke.test_real_term_resistant_group_is_killed_within_deadline` still fails in isolation with `False != True` at tests/unit_replay_smoke.py:153.
- Therefore the prior failure was not merely full-suite ordering or swap pressure.
- No threshold or assertion was weakened.

Evidence directory: outputs/grrr-reboot-verification/ with both ConservativeGenesis logs/exit codes and the isolated Python 3.9 smoke log/exit code.

## nd_contract
status: blocked

### evidence
- Reboot evidence captured; no protected effect.

### proof
- [x] Disk floor and swap blockers cleared.
- [ ] Python 3.9 term-resistant process-group cessation failure remains.
- [ ] Full clean suites and later protected integration remain pending.

### 2026-10-24T22:39:53Z speed
## Post-Reboot Cessation Fix Result

The reboot cleared capacity/swap. The remaining Python 3.9 cessation failure was then reproduced deterministically as a phase-global uncertainty bug: a transient TERM-phase observation timeout remained sticky even after SIGKILL and later verified absence. The focused implementation now resets uncertainty when entering the KILL phase, accepts success only after fresh valid group-absence evidence, rejects observations completed after the global deadline, and leaves persistent uncertainty/malformed inventory/deadline exhaustion as failures. TERM/KILL allowances and safety assertions were not weakened.

Final focused commit:
- 65bb7945299851c078f5b48e9083d3aee13a7c4a
- fix(GRRR-d8ji): verify cessation after transient TERM observation failure
- Four files changed: replay_smoke.py, unit_replay_cessation.py, replay-root-prepare hash pin, and evidence report.

Final no-guest proof on BOTH /usr/bin/python3 3.9.6 and /opt/homebrew/bin/python3 3.14.3:
- exact previously failing cessation test: 5/5 repetitions passed;
- cessation suite: 5/5;
- replay smoke suite: 12/12;
- recovery suite: 20/20;
- registration suite: 30/30;
- full unit suite: 253/253 each;
- zero failures, errors, skips, or warnings;
- compile, explicit-path pvg verify, and diff checks passed.

Exact final source hashes:
- research/replay_smoke.py 819ab8e37ebaf138eca6b69abee78bf356124809b64ca60c28ecd5b957749612
- tests/unit_replay_cessation.py d3ee8811a442d02936ee39c4eb16c608c12f4caeba8f163158841f461737bbd2
- scripts/replay-root-prepare 5908b3134f2cc13bc6c10e046630c0e0bfe8742618acc36a75be855e6b645a8c

Raw final evidence: outputs/grrr-d8ji-no-guest/cessation-final.txt SHA256 b2825f94a76a2d04969b993942c80b7e4b5906d19dddeae848219d25ad4eb433. RED evidence preserved in outputs/grrr-d8ji-no-guest/cessation-red.txt. The historical intermittent trigger itself was not reproduced after resume; deterministic injection supplies the tested defect class.

Independent focused review before the hash-only launcher pin update returned SECURITY_REVIEW: READY_FOR_COMMIT_REVIEW. Story/worktree clean, claim released, story remains blocked because separately authorized protected recovery integration is 0 executed and delivery/live acceptance are not claimed.

## nd_contract
status: blocked

### evidence
- Capacity, full-suite, and cessation no-guest blockers are cleared; branch clean at 65bb794.

### proof
- [x] Both full no-guest suites now pass 253/253.
- [ ] Final exact-byte review must include the launcher hash pin and protected integration package.
- [ ] Separately authorized live recovery integration remains not-run.
- [ ] No protected recovery, stop release, replay, promotion, admission, merge, production mutation, or push.

### 2026-10-24T22:40:53Z speed
## Final Exact-Byte Follow-up Review

SECURITY_REVIEW: READY_FOR_PROTECTED_RECOVERY_REVIEW

- Reviewed complete focused diff caf08f3..65bb7945299851c078f5b48e9083d3aee13a7c4a.
- Launcher change is exactly the replay_smoke.py source-pin update; no thresholds, assertions, deadlines, or gates weakened.
- Fresh post-KILL process-group absence remains mandatory after TERM uncertainty; late inventories fail closed.
- Recorded evidence reports 253/253 on both interpreters with zero failures/errors/skips and expressly withholds protected/live authority.
- Reviewer verified final hashes including replay_smoke.py 819ab8e37ebaf138eca6b69abee78bf356124809b64ca60c28ecd5b957749612, unit_replay_cessation.py d3ee8811a442d02936ee39c4eb16c608c12f4caeba8f163158841f461737bbd2, replay-root-prepare 5908b3134f2cc13bc6c10e046630c0e0bfe8742618acc36a75be855e6b645a8c, and evidence REPORT.md 18b3197c80fc7f1437ccd9e0b48f49c3b0b3cd8959e9ecfeed4a53f3b7f7daca.
- This authorizes progression to protected-recovery review only, not protected execution, live recovery, replay, admission, or production.

## nd_contract
status: blocked

### evidence
- Independent reviewer performed no edits or privileged operations.

### proof
- [x] Final no-guest implementation and focused fix reviewed.
- [ ] Protected recovery review/authorization/installation remains pending.
- [ ] Live integration remains not-run.

### 2026-10-25T14:33:32Z speed
## Operator Authorization — protected staging and recovery-plan review only

APPROVED [2026-10-25]: For exact GRRR-d8ji commit 65bb7945299851c078f5b48e9083d3aee13a7c4a, stage the reviewed two-file source closure and candidate plan/review inputs under /Library/GRRR/bootstrap/recovery, capture the exact read-only v2 baseline, and perform independent review.

Explicit denials: do not create /Library/GRRR/accounting-poc2/recovery, change active.json or budget.sqlite, release stop, recover, replay, promote, admit, mutate production, merge, or push.

## nd_contract
status: blocked

### evidence
- Live preflight before protected staging.

### proof
- [ ] Source staging pending.
- [ ] Read-only v2 baseline capture pending.
- [ ] Candidate plan/review staging and independent review pending.
- [ ] No runtime transition authorized.

### 2026-10-25T14:43:02Z speed
## Protected Staging and Independent Recovery-Plan Review

Operator authorization permitted staging and review only. Parent preflight verified clean story worktree HEAD 65bb7945299851c078f5b48e9083d3aee13a7c4a, exact source hashes, v2 protected binding, free space above floor, no QEMU/accounting runner, absent bootstrap/recovery staging path, and absent runtime recovery namespace.

Protected staging completed under /Library/GRRR/bootstrap/recovery:
- accounting_recovery.py SHA256 88cf699236288ba989fcb2b21e5966720faadc13f420c83c0f64e99bade8760a
- accounting_registration.py SHA256 db2d5965a78443fcd4205f8c73950ab0649876624fadfd79a17de086f3b1a038
- candidate-recovery-plan.json SHA256 478cbae360092c5b6a9659516be75b0a2c7e9d9741509bfbb8b4d6468f77307e
- candidate-recovery-review.json SHA256 94f9b8113b2b08595783d16223a2c10cdcde6b79de5c09076de1075de5fbec81
All four are root:wheel regular files mode 0444 with one link. No authorization record is staged.

Exact read-only v2 baseline was captured under launch-lock/idle-process controls:
- canonical baseline SHA256 dfc4bfcfd56a2fe8cfbc4416f912829b35e2dced5c31b23f181cbed38f63b73f
- version 2; stopped=1; pending=3; historical_unknowns=unresolved; spendable=null
- database SHA256 2347a548429cd8bf07048e15898de1432c960d7a08743e17dc31d39efdb5bbaf
- known encumbered POC/milestone [0,1108265788,0]
Baseline is exactly embedded in the plan; review hash and source closure are bound to it.

Independent security review verdict:
SECURITY_REVIEW: APPROVED_STOP_ONLY_RECOVERY_PLAN

Reviewer verified exact source/baseline/plan/review hashes, canonical schemas and cross-bindings, unchanged ceilings, empty allowed mutation list, unresolved/null uncertainty, v2 ancestry, protected staging metadata, and absence of runtime recovery/authorization artifacts. Reviewer limitation: protected database values were checked in the captured baseline rather than directly remeasured under unprivileged review; future authorized parent preflight must revalidate. Root parent postflight subsequently did directly revalidate DB hash/integrity/state/count and active/registration/prior hashes.

Boundaries preserved after staging and review:
- active.json remains v2 SHA256 97ad3cd38a90a71d412afccad5ed49fc73af73e5413edcc4e07a1e0d23f451c5
- budget.sqlite remains unchanged SHA256 2347a548429cd8bf07048e15898de1432c960d7a08743e17dc31d39efdb5bbaf
- /Library/GRRR/accounting-poc2/recovery remains absent
- no stop release, recovery execution, replay, promotion, admission, production mutation, merge, or push occurred
- authorization for protected execution was not created or consumed

Evidence: outputs/grrr-d8ji-recovery-staging/ with v2-baseline.json, candidate plan/review, protected-staging-postflight.log, and SHA256SUMS.

## nd_contract
status: blocked

### evidence
- Protected staging, baseline capture, root postflight, and independent review completed without runtime transition.

### proof
- [x] Exact reviewed source closure staged.
- [x] Exact v2 baseline captured and bound.
- [x] Candidate plan/review independently approved.
- [ ] Separate exact operator authorization and protected live install/verify remain pending.
- [ ] GRRR-d8ji remains blocked/not delivered.

### 2026-10-25T15:13:27Z speed
## Operator Authorization — protected stop-only recovery install and verify

APPROVED [2026-10-25]: The operator supplied an exact authorization binding GRRR-d8ji commit 65bb7945299851c078f5b48e9083d3aee13a7c4a, recovery source 88cf699236288ba989fcb2b21e5966720faadc13f420c83c0f64e99bade8760a, registration source db2d5965a78443fcd4205f8c73950ab0649876624fadfd79a17de086f3b1a038, baseline dfc4bfcfd56a2fe8cfbc4416f912829b35e2dced5c31b23f181cbed38f63b73f, review 94f9b8113b2b08595783d16223a2c10cdcde6b79de5c09076de1075de5fbec81, and plan 478cbae360092c5b6a9659516be75b0a2c7e9d9741509bfbb8b4d6468f77307e.

Authorized effects:
1. Stage the exact root-owned authorization record.
2. Run the reviewed stop-only recovery install.
3. Run protected verify under exclusive parent writer control.
4. Preserve original database inode/history/holds/unknowns and keep v3 read-only.

Explicit denials: no spendability reconciliation, replay, promotion, admission, production mutation, merge, or push.

## nd_contract
status: blocked

### evidence
- Authorization generated from the exact protected plan/review bytes; parent preflight still required immediately before effects.

### proof
- [ ] Authorization staging pending.
- [ ] Install and verify pending.
- [ ] Denials remain active.

### 2026-10-25T15:17:03Z speed
## Protected Authorization Staging

A first staging-script attempt failed before any authorization or protected runtime effect because its preflight used malformed nested command substitution for the database path. Revalidation confirmed authorization and runtime recovery namespace were absent and active/database hashes were unchanged. The script was corrected to the exact hardcoded store path.

The exact authorization record was then staged successfully at /Library/GRRR/bootstrap/recovery/candidate-recovery-authorization.json:
- SHA256 9235640b58b973913e9b14f2ade420085daeed91a1e048ad5b2b09da41079a60
- root:wheel mode 0444, one link, 602 bytes
- action release-stop-retain-unknowns-read-only
- principal operator-via-exclusive-root-parent
- exclusive_parent=true
- execution_authorized=false

No runtime recovery namespace was created; active.json and budget.sqlite remained unchanged.

## nd_contract
status: blocked

### evidence
- Authorization stage log and preflight evidence retained under outputs/grrr-d8ji-recovery-staging/.

### proof
- [x] Exact authorization staged.
- [ ] Install and verify remain pending.
- [ ] No replay, reconciliation, promotion, admission, production mutation, merge, or push.

### 2026-10-25T15:20:16Z speed
## Protected Stop-Only Recovery Install and Verify Result

Authorized parent execution completed successfully using the exact staged closure, plan, review, and authorization:
- source commit 65bb7945299851c078f5b48e9083d3aee13a7c4a
- accounting_recovery.py 88cf699236288ba989fcb2b21e5966720faadc13f420c83c0f64e99bade8760a
- accounting_registration.py db2d5965a78443fcd4205f8c73950ab0649876624fadfd79a17de086f3b1a038
- baseline dfc4bfcfd56a2fe8cfbc4416f912829b35e2dced5c31b23f181cbed38f63b73f
- review 94f9b8113b2b08595783d16223a2c10cdcde6b79de5c09076de1075de5fbec81
- plan 478cbae360092c5b6a9659516be75b0a2c7e9d9741509bfbb8b4d6468f77307e
- authorization 9235640b58b973913e9b14f2ade420085daeed91a1e048ad5b2b09da41079a60

Protected install exited 0. Protected verify exited 0. Published active binding is version 3, SHA256 9c5194dd12ff7601917fcccc293c459db09a41da8bad9fa9983cbef618d453f8, with recovery receipt SHA256 6d3d5b092c0ee8273a657c83823d8465b215f2b1b66ec627dfde2d96b21fe587. Original store/database inode 682589447 and evaluator ownership/mode remain unchanged; SQLite integrity is ok; state is 1|0; reservations=11, metering=8, overhead=0, pending holds=3. Historical unknowns remain unresolved and spendable remains null. Known encumbered remains [0,1108265788,0] in both scopes.

Recovery namespace has exactly root:wheel 0444 intent.json, prior-active.json, receipt.json, and complete.json; directory is 0555. No next-active or uncertain artifact remains. Prior v2 active bytes are preserved with SHA256 97ad3cd38a90a71d412afccad5ed49fc73af73e5413edcc4e07a1e0d23f451c5. Original registration ancestry remains unchanged.

The database SHA changed exactly as required for the stop transition, from 2347a548429cd8bf07048e15898de1432c960d7a08743e17dc31d39efdb5bbaf to 9c6ff2561a364ed982cd5477dd4b200c995da6910c9a17aa3d3c411a962d64f3. Allowed mutations remain empty and execution_authorized remains false. Source code and no-guest regressions enforce the read-only v3 mutation boundary; no protected write/refusal test was attempted.

No reconciliation, replay, promotion, admission, production mutation, merge, or push occurred.

Evidence: outputs/grrr-d8ji-recovery-staging/recovery-install.json, recovery-verify.json, v3-protected-postflight.log, and protected-recovery-SHA256SUMS.

## nd_contract
status: blocked

### evidence
- Protected live success install and verify completed; all ancestry/invariants verified.

### proof
- [x] Stop-only v3 transition installed and verified.
- [x] Original DB inode/history/holds/unknowns preserved.
- [x] v3 remains read-only by reviewed source contract.
- [ ] Separately authorized controlled refusal-path live proof remains not-run.
- [ ] Story remains blocked/not delivered pending that distinct gate and PM review.

### 2026-10-25T15:55:37Z speed
## Operator Authorization — controlled refusal-path proof only

APPROVED [2026-10-25]: attempt duplicate recovery with the already consumed authorization and attempt reviewed v3 reserve, meter, settle, overhead, halt, raw SQL, and writable BLOB mutations. Every attempt is expected to fail without changing active.json or budget.sqlite.

Explicit denials: no spendability reconciliation, replay, promotion, admission, production mutation, merge, or push.

## nd_contract
status: blocked

### evidence
- Current published state is v3 stop-only recovery; source and protected hashes require immediate preflight.

### proof
- [ ] Duplicate install refusal pending.
- [ ] Runtime mutation refusals pending.
- [ ] active.json and budget.sqlite byte-preservation checks pending.

### 2026-10-25T16:03:59Z speed
## Controlled Refusal-Path Proof — PASS

Operator authorization covered duplicate recovery and v3 mutation refusal attempts only.

Duplicate recovery with the already consumed authorization exited 1 as required:
- error: partial/unknown registration state
- execution_authorized=false
- active.json remained 9c5194dd12ff7601917fcccc293c459db09a41da8bad9fa9983cbef618d453f8
- budget.sqlite remained 9c6ff2561a364ed982cd5477dd4b200c995da6910c9a17aa3d3c411a962d64f3
- database inode remained 682589447
- state remained 1|0
- recovery intent/prior/receipt/complete hashes and inventory remained unchanged
- no uncertain.json or next-active.json was created

A parent-staged, hash-pinned temporary evaluator probe used the reviewed source closure at commit 65bb794 and ran as UID 320. It attempted 12 mutation surfaces:
- reserve: refused, Failure, Accounting registration is read-only; reviewed recovery required
- meter: refused with same read-only Failure
- settle: refused with same read-only Failure
- disclose_overhead: refused with same read-only Failure
- halt: refused with same read-only Failure
- raw connection execute: refused, DatabaseError/not authorized
- raw connection executemany: refused, DatabaseError/not authorized
- raw connection executescript: refused, DatabaseError/not authorized
- raw cursor execute: refused, DatabaseError/not authorized
- raw cursor executemany: refused, DatabaseError/not authorized
- raw cursor executescript: refused, DatabaseError/not authorized
- writable blobopen: refused, Failure, Writable accounting BLOB handles are forbidden

The probe checked active/database hashes and state/counts after every refusal. Final state remained:
- active SHA256 9c5194dd12ff7601917fcccc293c459db09a41da8bad9fa9983cbef618d453f8
- database SHA256 9c6ff2561a364ed982cd5477dd4b200c995da6910c9a17aa3d3c411a962d64f3
- database inode 682589447
- state 1|0; reservations 11; metering 8; overhead 0; pending 3
- all_refused=true; protected_state_changed=false; execution_authorized=false

A protected root postflight reverified complete v3 ancestry, unchanged registration/prior history, exact recovery artifacts, database integrity, and no evaluator/runner/QEMU process. The temporary probe workspace was removed after evidence capture.

No reconciliation, replay, promotion, admission, production mutation, merge, or push occurred.

Evidence: outputs/grrr-d8ji-recovery-staging/duplicate-install-refusal.log, duplicate-install-refusal-summary.log, v3-refusal-probe.json, refusal-proof-postflight.log, and refusal-proof-SHA256SUMS.

## nd_contract
status: blocked

### evidence
- All authorized refusal paths passed; protected bytes/inventory remained unchanged.

### proof
- [x] Duplicate recovery refused.
- [x] All reviewed v3 API/raw SQL/BLOB mutation attempts refused.
- [x] Successful protected install/verify and refusal-path proof are now both recorded.
- [ ] Story delivery/PM acceptance remain separate workflow actions not authorized by this proof-only operator request.

### 2026-10-25T16:51:22Z speed
## Implementation Evidence

PROOF:

### CI/Test Results
Commands run:
- /usr/bin/python3 /tmp/grrr-d8ji-doc-check.py
- /opt/homebrew/bin/python3 /tmp/grrr-d8ji-doc-check.py
- pvg verify docs/ACCOUNTING-RECOVERY.md docs/evidence/accounting-recovery/REPORT.md --format=text
- git diff --check; git diff --cached --check
- shasum -a 256 -c protected-recovery-SHA256SUMS; shasum -a 256 -c refusal-proof-SHA256SUMS (external recovery-staging directory)
Summary: documentation checks PASS 12/12 each interpreter, 0 failures; manifests PASS 9/9, 0 mismatches; pvg verify PASS 0 files scanned/0 issues (Markdown unsupported, substantive checks supplied separately); diff checks PASS. No new unit runs for docs-only change; unchanged implementation evidence records 253/253 full,20/20 recovery,30/30 registration each Python, zero failures/errors/skips/warnings. Coverage percentage not measured, AC coverage7/7.

### Commit
- Branch: story/GRRR-d8ji
- SHA: 734554707374f10c3c17b1e788d6fa2c3678bdd4
- Implementation/test evidence SHA: 65bb7945299851c078f5b48e9083d3aee13a7c4a; raw final log b2825f94a76a2d04969b993942c80b7e4b5906d19dddeae848219d25ad4eb433.
- Only two Markdown files changed; no implementation/test/protected effects. Full detailed proof, source/raw artifact hashes, AC table and limitations are in the appended delivery notes and committed docs/evidence/accounting-recovery/REPORT.md.

### AC Verification
| AC | Evidence | Status |
|---|---|---|
| 1 | Exact reviewed transition contract/source, final follow-up/plan review and authorized stop-only result | PASS |
| 2 | Original inode682589447/history/ceilings, reservations11/metering8/overhead0/pending3 and unresolved/null state preserved | PASS |
| 3 | Canonical intent/receipt/completion and original registration/v2 ancestry verified | PASS |
| 4 | Focused unit cases plus consumed-authority refusal and12/12 UID320 live API/rawSQL/BLOB denials, protected_state_changed=false | PASS |
| 5 | Developer no-guest effects unprivileged; parent effects separately reviewed and explicitly authorized, no downstream authority | PASS |
| 6 | Both required interpreter full253/253, recovery20/20, registration30/30 at unchanged implementation source, exact commands/log above | PASS |
| 7 | Separate live install/verify success and authorized refusal paths with before/after invariants, no reconciliation/replay | PASS |

LEARNINGS:
- Stop-only v3 is read-only with spendable null; successful recovery is not execution authority.
- Historical blocked contracts in Comments occur after Notes; final proof must be appended as a comment to retain append-only authoritative EOF contract.
- Markdown requires explicit checks beyond pvg verify's zero-scanned structural pass.

DISCOVERED_BUG:
  title: pvg deliver and nd append-notes leave historical Comments contract authoritative
  context: First verify-delivery passed4/9. pvg nd append-notes inserts under Notes; deliver inserts delivered contract there, before historical Comments containing blocked contracts. Latest global contract remained blocked. No raw vault edits or story rewrite; this comment appends complete proof/contract via nd API.
  affected_files: external pvg/nd delivery proof routing
  discovered_during: GRRR-d8ji

## nd_contract
status: delivered

### evidence
- Commit 734554707374f10c3c17b1e788d6fa2c3678bdd4; docs checks12/12 each Python; manifest9/9; static/diff checks pass. Detailed prior appended proof retained. No merge/push/protected operation.

### proof
- [x] AC #1: Exact reviewed transition contract and implementation.
- [x] AC #2: Original identity/history/holds/unknowns preserved.
- [x] AC #3: Canonical append-only ancestry and receipts.
- [x] AC #4: Fail-closed unit and controlled live refusals.
- [x] AC #5: Authority boundaries preserved.
- [x] AC #6: Both required interpreter suites pass with exact artifacts.
- [x] AC #7: Separately authorized stop-only success/refusal gates recorded; downstream replay gated.

### 2026-10-25T16:53:57Z speed
## PM Decision
REJECTED [2026-10-25]: DOCS_STALE; implementation/live proof is substantively present but mandatory documentation-freshness gate fails.

EXPECTED: Documentation Freshness requires updating documentation describing behavior changed by this story; no documentation scope-out exists.
DELIVERED: research/replay_smoke.py now resets observation uncertainty on entering SIGKILL and permits fresh timely post-KILL absence to establish success. docs/REPLAY-RUNTIME-SMOKE.md:158-160 still says uncertain cessation stays false even if a later observation finds no processes. docs/ARCHITECTURE.md:55 still describes current persistent accounting as registration-only and stopped, whereas the delivered documented/verified result is stop-only v3 with stopped=0 and runtime writes denied.
GAP: DOCS_STALE: docs/REPLAY-RUNTIME-SMOKE.md references the superseded phase-global uncertainty behavior but was not updated. DOCS_STALE: docs/ARCHITECTURE.md current-existence table references superseded stopped accounting state but was not updated. Readers receive contradictory current safety/state contracts despite the new recovery document being accurate.
FIX: Update both documents to the exact phase-local TERM/KILL semantics and bounded deadline failures; reconcile the architecture current-state row/checkpoint with the stop-only v3 result, unresolved history, spendable=null, empty allowed mutations and execution_authorized=false. Explicitly distinguish implemented/story/protected-installed closure state; retain no replay/reconciliation authority. Review related registration/current-state documentation for clear historical scoping or successor links. Redeliver docs-only with static/link/diff evidence; do not repeat protected actions or change implementation merely to resolve this finding.

Evidence reviewed: clean story HEAD 734554707374f10c3c17b1e788d6fa2c3678bdd4, full nine-file diff (1084 insertions/13 deletions; bounded cessation fix and evidence explain overrun), exact four implementation/test source hashes, raw cessation-final log b2825f94a76a2d04969b993942c80b7e4b5906d19dddeae848219d25ad4eb433 with both interpreter 253/20/30 passing counts, protected manifests 9/9 OK, actual install/verify records and duplicate/12 mutation refusals. No new test reruns needed for trustworthy unchanged evidence. No protected operations or code edits performed by PM.

## nd_contract
status: rejected

### evidence
- Independent PM review found two current documentation contradictions; source and protected evidence hashes verified.

### proof
- [ ] Mandatory documentation-freshness gate: exact current cessation and stop-only accounting behavior documented consistently.
- [x] AC1-7 substantive implementation/no-guest/live evidence reviewed; no downstream execution authority granted.

### 2026-10-25T16:56:41Z speed
## Implementation Evidence

PROOF:

### CI/Test Results
Commands run:
- /usr/bin/python3 /tmp/grrr-d8ji-doc-rework-check.py
- /opt/homebrew/bin/python3 /tmp/grrr-d8ji-doc-rework-check.py
- /usr/bin/python3 /tmp/grrr-d8ji-doc-check.py
- /opt/homebrew/bin/python3 /tmp/grrr-d8ji-doc-check.py
- pvg verify docs/ARCHITECTURE.md docs/REPLAY-RUNTIME-SMOKE.md docs/REPLAY-ACCOUNTING-REGISTRATION.md docs/REPLAY-ACCOUNTING-RECOVERY-PROPOSAL.md docs/evidence/replay-accounting-registration/no-guest.md docs/evidence/replay-accounting-registration/completed-install.md docs/evidence/replay-accounting-registration/frozen-runtime.md docs/evidence/replay-accounting-registration/blob-guard.md --format=text
- git diff --check; git diff --cached --check; git status --short; git rev-parse HEAD
Summary: rework documentation checks12/12 PASS per interpreter; original documentation/evidence checks12/12 PASS per interpreter; total48 checks,0 failures/skips/warnings; all commands exit0. Checks cover exactly8 Markdown changes, no implementation/tests changes, conflict/fence/local-link validation, precise KILL-phase semantics, precise current architecture row and historical provenance/current recovery pointers. Existing evidence checker also revalidates all9 manifest files and12/12 live refusals. pvg verify PASS0 issues,0 code files scanned (Markdown unsupported; explicit substantive checks supplied). Diff/staged diff PASS; committed worktree clean.
- No unit suites rerun for docs-only rework. Existing unchanged-source implementation proof remains: Python3.9.6 and3.14.3 each full253/253, recovery20/20, registration30/30, cessation5/5, smoke12/12, exact cessation test5/5 repetitions; zero failures/errors/skips/warnings. Raw evidence at /Users/speed/Documents/Codex/2026-10-19/3e4m-b-4/outputs/grrr-d8ji-no-guest/cessation-final.txt SHA256 b2825f94a76a2d04969b993942c80b7e4b5906d19dddeae848219d25ad4eb433. Exact commands, source hashes and raw protected artifacts remain in prior proof and docs/evidence/accounting-recovery/REPORT.md.
- Coverage percentage not instrumented/measured; AC coverage7/7, all PM DOCS_STALE targets corrected. No new implementation runtime/live test claim.

### Commit
- Branch: story/GRRR-d8ji
- SHA: 0fa26e4cf6f0c35b19fb6f1f75259932b00a086e
- Parent delivery SHA:734554707374f10c3c17b1e788d6fa2c3678bdd4; unchanged implementation SHA:65bb7945299851c078f5b48e9083d3aee13a7c4a.
- Eight docs-only files,46 insertions/13 deletions. No root/sudo/protected-state mutation, reconciliation, replay, promotion, admission, production mutation, merge or push. No PM acceptance.

### PM rework verification
- docs/REPLAY-RUNTIME-SMOKE.md now states uncertainty reset only on entering SIGKILL, fresh valid timely post-KILL absence required, persistent KILL uncertainty/malformed inventory/deadline exhaustion fail closed. No deadlines or implementation changed.
- docs/ARCHITECTURE.md current table/checkpoint now records stop-only v3 stopped=0, original inode/history/holds, unresolved unknowns/spendable=null/allowed_mutations=[]/execution_authorized=false and every runtime write denied. Also corrects GRRR-43i8 merged checkpoint at6afd643.
- Related registration narrative/proposal and four registration evidence records clearly label historical stopped-v2/recovery-not-run claims and link current recovery proof, retaining original measurements. No historical logs/scores rewritten.

### AC Verification
| AC | Evidence / location | Status |
|---|---|---|
| 1 | Exact implementation/review/transition unchanged; ACCOUNTING-RECOVERY contract and runtime-smoke semantics reconciled | PASS |
| 2 | Parent before/after evidence preserves inode682589447/history/ceilings/holds3; architecture matches stopped0, unresolved/null, empty mutations and no execution | PASS |
| 3 | Canonical intent/receipt/completion and original ancestry remain unchanged; registration records historical with current link | PASS |
| 4 | Prior recovery20/registration30 cases per Python and duplicate plus12/12 live refusals retained; no protected bytes changed by rework | PASS |
| 5 | Documentation-only unprivileged rework; separate exact parent authority remains bounded; no replay/production authority | PASS |
| 6 | Prior both-interpreter full253/253 and focused evidence unchanged, no errors/failures/skips; fresh docs checks48/48 | PASS |
| 7 | Prior separately authorized stop-only install/verify success and controlled refusals preserved; historical pending statements scoped; downstream gates remain separate | PASS |

LEARNINGS:
- Initial delivery updated the recovery pair but missed adjacent current-state architecture and runtime-smoke wording; rework searched related registration/proposal/evidence narratives rather than only the PM's two lines.
- Preserve old checkpoint hashes/state as historical evidence and link current proof instead of rewriting original measurements.
- TERM observation uncertainty is not globally sticky: only fresh timely valid post-KILL absence can resolve cessation; persistent uncertainty still fails closed.
- EOF proof must be appended as an nd comment after deliver because older Comments occur after the Notes section; prior proof remains append-only.

## nd_contract
status: delivered

### evidence
- Docs rework commit0fa26e4cf6f0c35b19fb6f1f75259932b00a086e;48/48 fresh documentation/evidence checks across both required interpreters; pvg verify/diff checks PASS. Implementation/tests and protected state unchanged.

### proof
- [x] AC #1: Exact reviewed contract and current cessation semantics documented.
- [x] AC #2: Original cumulative identity/history/holds/unknowns preserved and current v3 accurately described.
- [x] AC #3: Canonical recovery ancestry retained; historical registration records scoped.
- [x] AC #4: Fail-closed unit and controlled live refusal evidence unchanged.
- [x] AC #5: No unauthorized protected effects or broadened authority.
- [x] AC #6: Both required interpreter implementation suites green with exact artifacts; docs rework checks pass.
- [x] AC #7: Separately authorized stop-only live success/refusal gates recorded; no replay authority.

### 2026-10-25T16:58:24Z speed
## PM Decision — authoritative final contract
ACCEPTED [2026-10-25]: Independent full re-review of0fa26e4cf6f0c35b19fb6f1f75259932b00a086e verifies all seven ACs and documentation freshness. Both DOCS_STALE blockers are corrected and adjacent historical registration records link the current stop-only v3 evidence. Exact seven implementation/test hashes remain unchanged; raw both-interpreter full253/253 and focused20/20 plus30/30 passing evidence remains trustworthy. Fresh PM documentation checks48/48, delivery9/9, protected evidence manifests9/9 and diff checks passed. Real separately authorized parent success and duplicate/12 runtime refusals reviewed without repeating protected operations. Prior detailed PM notes preserved. Coverage percentage not measured. No replay, spendability reconciliation, merge, promotion, admission or production authority granted.

Transition independently verified: pvg story accept returned OK; nd status closed and accepted label present, delivered/rejected absent. The pre-existing blocked label remains as returned by the transition, not a rejection of this accepted stop-only slice. Epic auto-close checked: five children remain nonclosed, so epic not closed. This EOF comment repairs the known Notes-before-Comments contract placement without raw vault edits.

## nd_contract
status: accepted

### evidence
- Exact delivery0fa26e4 reviewed; source hashes unchanged; fresh docs48/48, delivery9/9, manifests9/9.
- pvg acceptance landed closed/accepted; parent epic retains five nonclosed children.

### proof
- [x] AC1: Exact independently reviewed stop-only contract/implementation.
- [x] AC2: Original identity/history/ceilings/holds and unresolved/null preserved.
- [x] AC3: Canonical immutable complete receipt ancestry and uncertain outcomes.
- [x] AC4: Fail-closed unit and real controlled duplicate/API/SQL/BLOB refusals.
- [x] AC5: Separate exact parent authority; no developer privileged effects or downstream authority.
- [x] AC6: Both interpreter full/focused evidence verified for unchanged source.
- [x] AC7: Separately authorized actual parent success/refusal integration verified.
- [x] Documentation-freshness gate: both exact blockers and adjacent records corrected.
