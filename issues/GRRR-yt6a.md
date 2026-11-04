---
id: GRRR-yt6a
title: "Source-only durable capstone grant and operation journal"
status: closed
priority: 0
type: task
labels: [milestone-1, source-only, security-boundary, accepted]
parent: GRRR-2t3h
created_at: 2026-11-04T18:42:49Z
created_by: speed
updated_at: 2026-11-04T19:35:33Z
content_hash: "sha256:aa39682e7c07006ec8dd245ca77884dc23c0a751037fe9fec686d72198346973"
assignee: dev-GRRR-yt6a
follows: [GRRR-wcwy, GRRR-ev2w]
closed_at: 2026-11-04T19:32:00Z
close_reason: "Independent security/PM review approved exact 2dc0b3a: eight source-only ACs verified; raw hashes/tests and parent-filter false-positive checked. No runtime or full capstone authority."
---

## Description
## Context and approved source boundary
This is ONE source-only prerequisite to GRRR-q3hp, not the driver or capstone.
Current epic9a439a09161b7c62da8acc36a9cefef8f2924faf includes accepted wcwy.
Current bounded architecture mapping /tmp/grrr-q3hp-current-mapping-20261104.md
SHA256 b24eb7cc862d526b279afb618b08e95f1de8f792ac6f83241905877424653dc8
finds the complete driver still blocked. A refusing CLI alone fails original
q3hp AC2/3; do not weaken them. The mapping proposes the durable journal below.

Coordinator's independent review of that proposal accepts ONLY this source
journal design, with the transaction/identity constraints below. It does not
approve full q3hp mapping, an installed backend, allowance or execution. Existing
system architecture and v1/v4 guards are unchanged. Detailed SQL constants/checks
are implementation artifacts requiring independent security/PM review before any
epic integration or protected migration. There is no protected migration here.
Routing: CoS unavailable and recent GLM/Qwen bounded tasks returned no artifacts;
this scope is transcribed through the public tracker API as final routine fallback.

## USER INTENT
An evaluator-owned journal must durably consume one already issued grant for one
exact operation, preserve conservative pending/unknown state through a restart,
and never turn a duplicate request into a second dispatch permit. Real SQLite
source tests prove this without touching protected accounting or launching a VM.

## Boundary Map
PRODUCES (new source APIs):
- research/capstone_journal.py: open_existing(ledger) -> Journal; Journal.claim(start, authenticated_uid) -> local journal record; record_reserved(operation_id,reservation); mark_dispatch_pending(operation_id); request_stop(operation_id,authenticated_uid); status(operation_id,authenticated_uid). Document exact typed return shapes. Any dispatch permit must be opaque, one-use and process-local, never a serialized authority token.
- research/capstone_journal_schema.py: exact declared schema/check validation for two new ledger tables capstone_grants/capstone_operations and their necessary constraints/triggers. Explicit schema constants are not a production migration or issuance API.
- tests/unit_capstone_journal.py: real temporary SQLite state, crash/reopen and concurrency tests; optional separate source-suite runner if needed.
- scripts/test-story: explicit capstone-journal source-only mode, rejecting zero/skipped/failing tests.
- docs/CAPSTONE-EVALUATOR-PROTOCOL.md: append journal semantics and limitations without changing the embedded accepted contract bytes.
CONSUMES:
- research/capstone_contract.py: validate_record, decode_record, operation_id, start_request_digest, canonical/digest via common. Original Grant bytes stay separate from canonical Plan and human authorization hash.
- research/ledger.py: Ledger.db, Ledger.lock (RLock), Ledger.tip(), Ledger.append_atomic(principal,event,expectedTip,key,callback), same-file transaction only. _append checks tip/idempotency BEFORE BEGIN IMMEDIATE and skips callback for cached keys. The new component MUST account for both facts; do not modify this existing module.
- Existing real source suites: tests/unit_capstone_suite.py (19 tests) and tests/unit_durable_evidence.py. Legacy durable tests patch an identity constant: label them unit policy/storage regressions, NOT real UID320 evidence.

## Acceptance Criteria
1. Open only a supplied trusted existing Ledger; validate the exact preinstalled journal schema/objects, existing core chain and journal rows. Missing/corrupt/changed schema or state refuses without DDL, repair or fallback to an empty registry. No production issuance or automatic migration/open/create path. Production open requires actual UID320 before effectful I/O; no configurable production UID/path override.
2. Claim uses an existing issued Grant row retaining its exact raw bytes/digest, not caller issuance. Validate Plan/start structure, original Grant/authorization bindings and exact operator UID. Grant consumption, unique operation insertion and hash-linked ledger event commit atomically in this ONE ledger DB. No budget or other database transaction is claimed.
3. Identical claim returns existing recorded state only; changed payload/plan/Grant for a consumed grant refuses. One grant can own at most one operation. Cross-thread AND separate-connection/process races must preserve both uniqueness and linear ledger chain. Because existing Ledger tip checks are outside BEGIN, revalidate actual prior/current chain and all relevant row predicates INSIDE the callback/transaction before any state transition. A cached append that skipped callback can NEVER mint a fresh effect permit.
4. Actual SQLite rollback/crash-before-commit leaves no consumed grant/operation/event; crash-after-commit retains consumption. Persisted dispatch-pending/unknown never regains dispatch permission after reopen. Only a successful live reserved->dispatch-pending transaction may return an opaque in-process single-use permit. Duplicate calls/status/reopen cannot dispatch or renew it. No dispatcher/callback, VM or transport invocation is added. Do not claim that a process-local permit alone solves the later stop-vs-send seam.
5. request_stop atomically and monotonically latches stop_requested for the correct recorded operator; dispatch-pending transition checks that latch under the same serialization. Reservation references are immutable after their approved transition; status is SELECT-only and absent state fails rather than fabricates success. No reset, refund, reserve, meter, settle, overhead, reconciliation, stop-release, grant reuse or automatic recovery API.
6. All positive parser/transaction/concurrency/crash evidence uses real SQLite and public private-temp fixtures, not mocked storage. Explicit nonproduction fixture factory may use the actual unprivileged UID and unmodified Ledger transaction methods, but must never fake getpeereid/os.getuid or claim production identity/issuance. Production factory still refuses unprivileged caller. Test-only paths are lexically rejected before metadata and may never address /Library/GRRR. Run journal suite, unchanged wcwy suite and existing durable unit regressions on all available Python3.14/3.12/CLT3.9. Record counts, errors/skips, hashes and measured coverage (or explicitly unmeasured), no skipped-green. No VM/integration identity proof is inferred.
7. Existing Ledger, common, transport, PersistentBudget/replay/v4-schema and wcwy guards remain byte unchanged. Documentation must distinguish local journal records from full capstone Operation/Receipt authority; do not fabricate Anchor, allowance, gate passes or discovered history. Original exact contract remains an exact docs suffix (insert additions BEFORE it). No service wiring, new sockets/daemons, backend installation, live store/grant issuance or permission change.
8. Source-only commit/delivery are operator-authorized; independent security/PM review is mandatory before source merge. Do not close q3hp/6sso. No /Library/GRRR access including metadata, protected install/write/reconcile/stop release/VM/replay, paid research/network/secret use, admission/promotion/prod/main mutation or push. Commit only the assigned source/test/docs to this story; no autonomous epic merge by developer.

## Testing and failure requirements
Required adversaries include missing/extra/changed schema and corrupt rows, counterfeit/changed original bytes, unauthorized operator, unknown operation, same and different start replay, same-grant races, different-grant stale-tip races, before/after-commit cuts, reopen pending/unknown, immutable reservation, stop-before-pending and stop/pending races, status no-write, cached-callback no-permit and zero/skip suite rejection. Every full runtime/capstone gate remains NOT-RUN. No environment-variable shortcut or production identity simulation may count as integration proof.

## DIFF BUDGET
Target <=1200 changed LOC, about6-7 files including any runner. If safety tests need modest extra lines, report the actual overrun and rationale; never delete/weaken assertions or silently broaden scope. No entire-ecosystem implementation.

## OUT OF SCOPE / remaining gates
Actual v4 allowance/read-write adapter, historical cumulative reconciliation and stopped state, production descriptor/launcher, exclusive writer installation, replay pre-reserved execution seam, administrative schema/grant installation, fresh exact run grant and all mandatory live VM/ledger proof. Journal success alone cannot authorize a run.

## nd_contract
status: new

### evidence
- Created from current bounded architect mapping and coordinator source-only review; no implementation or runtime capability is inferred.
- Operator authorized local source workflow, not protected execution or deployment.

### proof
- [ ] AC1 exact existing schema/state validation.
- [ ] AC2 atomic raw-bound grant consumption and operation/event.
- [ ] AC3 idempotency and real cross-connection linear-chain races.
- [ ] AC4 real crash cuts and no renewed dispatch permit.
- [ ] AC5 monotonic stop/immutable reservation/read-only status.
- [ ] AC6 real source suites across3interpreters with raw evidence.
- [ ] AC7 existing guards/exact contract and authority limits preserved.
- [ ] AC8 reviewed source workflow only, no protected/runtime effects.

## Acceptance Criteria


## Design


## Notes
## Accepted local source integration
- Independent security+PM review approved exact source commit2dc0b3a8920135c578d0d5aaec6aaefbbb2b55d6. Live nd confirms closed+accepted. Review /tmp/grrr-yt6a-pm-security-review-20261104.md SHA256 b50ad66ecc84f79f7763b3c8fdf581451b682e3fbef8cba55352b03bec73143e; retained under .git/paivot/wip/GRRR-yt6a/parent-verify-20261104/.
- Authorized epic merge2b601462ba0ffb5aee6239aa22b06c26801dfaf9 has parents9a439a09161b7c62da8acc36a9cefef8f2924faf and2dc0b3a8920135c578d0d5aaec6aaefbbb2b55d6. Merged tree is byte-identical to accepted source tree and clean. Main remains c2970356436531565711fb3c2df24eb91c3ed510.
- Native pvg story merge again failed with missing origin (exit128). No remote was invented or tool changed. Exact pinned local-only fallback rechecked PM closure/acceptance, source/base/branch/clean state before no-ff merge, as explicitly operator-authorized. Raw native failure and exact integration receipt retained in .git/paivot/wip/GRRR-yt6a/merge-20261104/.
- Nine merged-tree suite runs passed: EACH of3interpreters journal25+protocol19+durable unit7,0fail/error/skip and exit0. This is51 source tests per interpreter, not live corpus observations. No VM/replay or full capstone gate executed.
- Journal source is now integrated, not installed or issued authority. q3hp/6sso remain unfinished; v4 allowance/history/stopped-state authority, production descriptor/transport, replay reservation/execution seam and full driver/live proof remain substantive gaps. No protected access/install/write/reconcile/stop release, new research/credential call, admission/promotion/prod/main mutation or push.

## nd_contract
status: accepted

### evidence
- PM closeout applied via pvg story accept on 2026-11-04.

### proof
- [x] Story closed after accepted label was applied.


## nd_contract
status: delivered

### evidence
- Transitioned via pvg story deliver on 2026-11-04.

### proof
- [ ] Developer evidence block must remain authoritative above this contract.


## nd_contract
status: in_progress

### evidence
- Selected by pvg loop next and claimed atomically. Isolated source worktree .claude/worktrees/dev-GRRR-yt6a on story/GRRR-yt6a, base9a439a09161b7c62da8acc36a9cefef8f2924faf.
- One bounded security/concurrency implementation delegated to /root/implement_capstone_journal. Exact source design/ACs in Description; no recursive delegation or protected/runtime authority.
- Operator authorized local source commits/PM delivery/PM-accepted epic integration. Existing three interpreters and stdlib SQLite only; tiny public fixtures, no VM or protected access.

### proof
- [ ] AC1-8 implementation, tests and independent review pending.
- [x] Scope: q3hp remains blocked; no capstone completion or live authority inferred.

## Implementation Evidence

PROOF:

### CI/Test Results
Commands run:
- /opt/homebrew/bin/python3 -B scripts/test-story capstone-journal
- /opt/homebrew/bin/python3 -B tests/unit_capstone_suite.py
- /opt/homebrew/bin/python3 -B -m unittest discover -s tests -p unit_durable_evidence.py -v
- Repeat those three exact commands with /Users/speed/miniconda3/bin/python3 and /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/bin/python3.9.
- pvg verify research/capstone_journal.py research/capstone_journal_schema.py tests/unit_capstone_journal.py tests/unit_capstone_journal_suite.py scripts/test-story docs/CAPSTONE-EVALUATOR-PROTOCOL.md --include-tests --format=text
Summary: EACH of Python3.14.3,3.12.7,3.9.6 passed journal25, unchanged wcwy19, durable unit7, failures0/errors0/skips0, exit0. Static PASS4eligible files0issues. Nine source suite invocations independently reproduced by parent; these are51 source tests per interpreter, not153 distinct scenarios or VM observations. No full VM/corpus/replay/build/CI or capstone gate was run or implied.
- Author raw evidence /tmp/grrr-yt6a-evidence-20261104/, preserved under .git/paivot/wip/GRRR-yt6a/parent-verify-20261104/author-evidence/. Parent exact command arrays/stdout/stderr/hash receipts in runs.json, run0..run10.stdout/stderr and source-hashes.json. validation-receipt.json SHA256 ffa1b6d164d311868d5465647e37b736ed5795aebd51ce449f83b5136ac776a8.
- Parent verification /tmp/grrr-yt6a-parent-verify-20261104.py executed all11 commands successfully (9 suites, static, extra trace). Its final unanchored diagnostics filter falsely matched the stdlib traceback MODULE NAME in trace stdout and exited1. Original harness/raw outputs retained, filter fixed to anchored stderr diagnostics, and /tmp/grrr-yt6a-finish-parent-validation-20261104.py revalidated every raw hash/count/exit plus exact source. This was a parent-only validation bug, not a skipped/failing source test; no test requirement/code/log was weakened or rewritten.

### Coverage
- Author accurately reported unmeasured coverage. Parent subsequently measured stdlib trace LINE coverage: capstone_journal98.9%, capstone_journal_schema100.0%, using /opt/homebrew/bin/python3 -B -m trace --count --summary --missing --coverdir <repo>/.git/paivot/wip/GRRR-yt6a/parent-verify-20261104/coverage tests/unit_capstone_journal_suite.py. Extra trace executed25 tests,0fail/error/skip, exit0. Raw summary run10.stdout.
- Branch coverage, subprocess-child line coverage and production/runtime coverage remain unmeasured. Percentages are not an aggregate capstone assurance score.

### Commit
- Branch: story/GRRR-yt6a
- SHA: 2dc0b3a8920135c578d0d5aaec6aaefbbb2b55d6
- Base: 9a439a09161b7c62da8acc36a9cefef8f2924faf
- Six scoped files,966insertions/2deletions, within1200line budget. Source manifest verified against working tree and commit; clean working tree. Preserved source patch SHA256 3c2c745f0f99d39c3af7b5fc37e04c24750cbaf6af790c7f2a5df39975ee33db.
- Local source commit/delivery authorized by operator; independent security/PM acceptance is still pending. No epic/main merge or push performed for this story.

### Source Wiring and Boundaries
- Explicit scripts/test-story capstone-journal invokes only the real source-suite runner, which rejects zero/skipped/failing/error results. No production service, migration, issuance, budget or dispatch wiring is added.
- Public APIs are typed. Production open_existing requires actual UID320 before effectful I/O; explicit private-temp factory requires actual unprivileged UID and rejects0/320/321. No getpeereid/os.getuid impersonation. Fixture transactions reuse unmodified Ledger methods with real SQLite; this is not production identity proof.
- Callback-time chain/state replay revalidates after BEGIN IMMEDIATE, preventing existing Ledger's pre-BEGIN tip check from permitting a stale fork. Cached callbacks cannot mint transition permits. Two tables plus declared constraints/triggers are SOURCE schema, not a protected migration/issuer.
- Legacy common/Ledger/transport/PersistentBudget/replay/v4 schema and wcwy modules byte unchanged. Accepted contract remains exact docs suffix SHA256 9b0f0f5639a1f2f07539a1b1e22d33bb67e88e2dc78fe58ecc9925f356aaf8ad; journal documentation is inserted before it.

### pvg verify
- Exact explicit-path command above: VERIFY: PASSED (4 files scanned,0issues), exit0. Four eligible Python files scanned; docs/script not falsely counted. Whitespace diff and working tree clean. Raw results retained.

### AC Verification
| AC # | Requirement | Code Location | Test Location | Status |
|---|---|---|---|---|
| 1 | exact existing schema/core history/corrupt-row refusal, no DDL/repair | journal_schema.validate_schema; journal._validate/open_existing | missing/extra/corrupt/settings/boolean-version tests | PASS source |
| 2 | original raw Grant/auth/operator and same-DB atomic consumption/op/event | _binding; claim; _change callback | exact-replay/counterfeit/atomic crash tests | PASS public SQLite |
| 3 | changed start refusal, unique consumption, in-transaction linear chain, cached no-permit | _change; _validate | same/different-grant real thread/connection/process races and cached-ledger tests | PASS source |
| 4 | before/after-COMMIT cuts, conservative reopen, one-use process-local permit | DispatchPermit; mark_dispatch_pending | actual process exits, pending/reopen/unknown/fork/serialization tests | PASS source, not VM |
| 5 | monotonic stop, immutable reservation, SELECT-only status, absent fails | request_stop; record_reserved; status | stop/pending race, immutable reservation/status/unknown tests | PASS local state |
| 6 | real SQLite and explicit nonproduction fixtures; three interpreters/raw artifacts | journal fixture factory and source suite | 25+19+7 on each,0fail/error/skip; source hashes and measured limits above | PASS source |
| 7 | legacy guards/exact contract unchanged; no fake Operation/Receipt/authority | six-file diff; protocol docs | hash/diff/contract-suffix verification, frozen local JournalRecord | PASS boundary |
| 8 | authorized local source workflow only; no protected/live closure | full scoped diff and documented limits | independent review pending; no effects beyond public source fixtures | PASS scope, PM pending |

LEARNINGS:
- Existing Ledger tip/idempotency checks happen before BEGIN; same-database callback revalidation is essential for multiple connections, not merely a thread lock.
- An append cache hit that skipped its callback must never mint a new effect permit. Reopened pending and unsupported unknown state fail closed, never renew or repair.
- Original grant bytes, canonical local records and full capstone authority are different things; a local journal record must not fabricate an Anchor or spendable allowance.
- Stop latching in the journal does not solve future stop-versus-real-send coupling; no dispatcher exists here. Local SQLite/identity-policy tests are not installed UID320 or VM proof.

## nd_contract
status: delivered

### evidence
- Commit2dc0b3a8920135c578d0d5aaec6aaefbbb2b55d6; exact6files/966insertions2deletions;9 source suite runs reproduced on3interpreters, each25+19+7 tests,0fail/error/skip; static4eligible files0issues.
- Parent trace LINE coverage journal98.9/schema100.0; not branch/subprocess/runtime. Raw source/test/coverage and resolved parent-harness filter issue preserved.
- Local source workflow authorized; independent security/PM review pending. No protected access/install/issuance/accounting/reconciliation/stop release/VM/replay/admit/promote/production/main effect, merge or push.

### proof
- [x] AC #1: exact existing schema/history corruption refusal without repair.
- [x] AC #2: original raw-bound atomic same-DB grant/op/event.
- [x] AC #3: idempotency and real multi-connection/process linear-chain races.
- [x] AC #4: actual crash cuts and no renewed opaque one-use permit.
- [x] AC #5: monotonic stop, immutable reservation, read-only/absent status.
- [x] AC #6: real source suites3interpreters/raw evidence and honest coverage.
- [x] AC #7: unchanged guarded modules and exact embedded contract; local records not authority.
- [x] AC #8: source-only scope, no q3hp/capstone closure or protected/runtime effects.

# GRRR-yt6a independent source review — 2026-11-04

PM_RESULT: ACCEPTED
SECURITY_REVIEW: APPROVED

Exact reviewed commit: 2dc0b3a8920135c578d0d5aaec6aaefbbb2b55d6.
Parent: 9a439a09161b7c62da8acc36a9cefef8f2924faf.
Patch SHA256: 3c2c745f0f99d39c3af7b5fc37e04c24750cbaf6af790c7f2a5df39975ee33db.
Six files, 966 insertions / 2 deletions; clean story worktree. No source edits.

## Findings and verification

No material within-scope security or acceptance defect found. Reviewed complete journal/schema, test bodies, source runner, documentation diff, and existing Ledger append/cache behavior. Trusted supplied Ledger and in-process caller are explicitly not an adversarial Python sandbox.

- AC1: Exact sqlite_master SQL/index inventory, no temp shadows/attached DBs, required durability settings, complete chain/idempotency/row replay; corrupt state refuses. Production open checks actual UID320 before ledger I/O. No production migration or grant issuer.
- AC2: Raw issued Grant bytes/digest and decoded grant, authorization hash, Start/Plan and exact integer operator bindings checked; consumption, unique operation and event updated inside real Ledger append_atomic callback, same connection/transaction.
- AC3: Entire actual chain and row state revalidated after BEGIN IMMEDIATE including tentative event. A stale pre-BEGIN tip cannot survive callback validation. Cached append cannot set applied marker. Same/different-grant process and thread races force interleaving at BEGIN and validate reopened chain/uniqueness; shared-connection repeats return status only.
- AC4: Actual child exits at traced COMMIT-before and after returned commit prove rollback/durability. Only applied live pending transition mints permit. Copy/pickle, repeated consume, fork and reopen tests refuse renewed authority. Persisted unsupported unknown state refuses rather than repairs. No send exists.
- AC5: Stop is authenticated, monotonic and serialized with pending; reservation immutable. Status transaction contains reads and rollback, no persisted writes. Absent operation and stopped invalid transitions refuse.
- AC6: Real SQLite fixtures use actual unprivileged UID and unmodified Ledger methods; production-negative identity test is not a production positive. Reviewed raw nine suite runs, each interpreter journal25/wcwy19/durable7, zero failures/errors/skips and exit0; no need to repeat complete trustworthy proof. Static rerun passed four eligible files/zero issues; delivery preflight9/9. Measured trace LINE coverage 98.9%/100%; branch, child and runtime coverage unmeasured.
- AC7: Exact six-file change list and manifest/commit bytes independently verified. Guarded legacy code unchanged. Accepted docs suffix SHA256 9b0f0f5639a1f2f07539a1b1e22d33bb67e88e2dc78fe58ecc9925f356aaf8ad remains byte exact. Local JournalRecord does not fabricate full Operation/Receipt/Anchor/allowance.
- AC8: Source-only approval, no protected access, runtime, service, network, accounting, installation, merge or push. q3hp and 6sso remain unfinished; epic must remain open.

## Commands and evidence

- git log --oneline -3; git diff --stat HEAD^ HEAD; source/test/docs reads.
- pvg nd show GRRR-yt6a; pvg verify <six delivered paths> --include-tests --format=text; pvg story verify-delivery GRRR-yt6a.
- /opt/homebrew/bin/python3 -B /tmp/grrr-yt6a-pm-verify-20261104.py: exit0, independently hashes source against commit, exact manifest/patch/contract/receipt, all11 raw stdout/stderr artifacts and test counts/OK results.
- Parent evidence: .git/paivot/wip/GRRR-yt6a/parent-verify-20261104/{runs.json,run0..run10.stdout/stderr,source-hashes.json,validation-receipt.json}.
- Receipt SHA256 independently confirmed ffa1b6d164d311868d5465647e37b736ed5795aebd51ce449f83b5136ac776a8.
- Explicitly investigated parent-only harness exit1: run10 stdout contains the stdlib coverage row `traceback` (1065 lines,43.0%), not an exception. All11 actual commands have exit0 and matching raw hashes; test stderr ends OK without traceback/warnings/errors. Anchored stderr filter fix is valid; no source/test/log weakening. Existing parent harness is now corrected; raw execution artifacts retain the original successful runs.
- pvg nd children GRRR-2t3h --json confirms 6sso deferred, q3hp open (and this story in_progress before decision).

## Limits

Approval is only for this journal prerequisite at the pinned commit, not q3hp completion or a live capstone. No production UID320/getpeereid, installed schema/issuance, allowance/budget, VM/replay/send, reconciliation, admission or promotion proof. Process-local permit does not solve future stop-versus-send coupling. No further claim, merge, epic closure or push authorized/performed by reviewer.

## nd_contract
status: accepted

### evidence
- Independent security and PM review at exact commit2dc0b3a; static4/0issues, delivery9/9; all11 raw commands/hash receipts verified, source suites25+19+7 on3interpreters, no failure/error/skip.
- Full review /tmp/grrr-yt6a-pm-security-review-20261104.md; independent verification script /tmp/grrr-yt6a-pm-verify-20261104.py. Source-only limitations and resolved parent harness false-positive recorded above.

### proof
- [x] AC #1: exact existing schema/state refusal and pre-I/O production UID gate.
- [x] AC #2: raw-bound grant/operator and atomic same-DB operation/event.
- [x] AC #3: transactional chain revalidation, unique consumption and no cached permit.
- [x] AC #4: real crash cuts, conservative reopen, one-use process-local permit.
- [x] AC #5: monotonic stop, immutable reservation, SELECT-only absent-refusing status.
- [x] AC #6: real SQLite source evidence across3interpreters with honest coverage.
- [x] AC #7: exact legacy/contract preservation and no fabricated runtime authority.
- [x] AC #8: independent source approval only; q3hp/6sso and live gates remain unfinished.

## History
- 2026-11-04T18:43:15Z dep_added: blocks GRRR-q3hp
- 2026-11-04T18:43:35Z status: open -> in_progress
- 2026-11-04T18:43:35Z auto-follows: linked to predecessor GRRR-wcwy
- 2026-11-04T18:43:35Z claimed by dev-GRRR-yt6a
- 2026-11-04T19:28:39Z status: in_progress -> in_progress
- 2026-11-04T19:28:39Z auto-follows: linked to predecessor GRRR-ev2w
- 2026-11-04T19:32:00Z status: in_progress -> closed
- 2026-11-04T19:32:00Z dep_removed: no_longer_blocks GRRR-q3hp

## Links
- Parent: [[GRRR-2t3h]]
- Follows: [[GRRR-wcwy]], [[GRRR-ev2w]]

## Comments
