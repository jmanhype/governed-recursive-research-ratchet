---
id: GRRR-k3j7
title: "Executable evaluator backend: finite JIT campaign, accounting and isolated launch bridge"
status: closed
priority: 0
type: feature
labels: [milestone-1, integration, security, source-only, accepted]
parent: GRRR-2t3h
created_at: 2026-11-04T21:39:45Z
created_by: speed
updated_at: 2026-11-05T20:25:47Z
content_hash: "sha256:d2fea3cd6c902ad15eb3a01c52a62cd0cd3ec13c859f2605545578d023636840"
follows: [GRRR-yt6a, GRRR-wcwy, GRRR-ev2w, GRRR-888u]
assignee: dev-GRRR-k3j7
closed_at: 2026-11-05T20:25:47Z
close_reason: "Accepted via pvg story accept"
led_to: [GRRR-q3hp, GRRR-hbc6, GRRR-n49g, GRRR-734u]
---

## Description
# GRRR executable evaluator backend — substantive source story draft

STORY_STATUS: DRAFT_READY_FOR_PARENT_BINDING; no tracker/source state changed.
Repo HEAD verified `2b601462ba0ffb5aee6239aa22b06c26801dfaf9`; `docs/findings/` absent.
Prerequisite inputs are base backend design SHA256
`954a8578ca9354c0af2d1d19a25bff3dcd2f41b2ef98e62e5667254230239c56`, JIT v2 SHA256
`3f2c661bf93b8513440f3a31daed2f3d2f37cd312137c3181304195402ebb488`, and rejected JIT
review SHA256 `ae447e94efdbfcbf7480f0e7756734d1f202eeab9425adeb48a8bc8e603b76c5`.
Repaired v3 is `3ab960191613b2e10018f5c9444532080e9757693c49393f888c6beff0793e09`;
source-integration corrections are `97c918328606cd69c62c6eaf52528ee4b024a76a8c5983a9e46f59c6a0bb7cee`.
Precedence is corrections > v3 > original JIT > base. Implementation requires
`INDEPENDENT_ACCEPTANCE=/tmp/grrr-backend-design-acceptance-20261104.md`,
with independent review SHA256 `2e6d50ddd3e638365284f344cc5412975362cd6d7ee94dc87651e402b8b9d3d3`;
parent verifies all input bytes before dispatch. No worker may self-approve delivery.

## Objective

Implement one conditional, production-shaped evaluator backend at source: exact installed
open-only factories, durable campaign issuance/index/replay, JIT dynamic leaf execution,
independent actual-Plan review, campaign stop/ownership, full projection, conservative
accounting, fresh pair execution, and installed-equivalent launch transport. Public fixture
factories must provide the same protocol against private temporary SQLite/AF_UNIX topology
with an unmistakable nonproduction identity.

This story implements backend capability; it does **not** implement the q3hp driver, a
report-only stage, installation, live qualification, or a production cutover.

## Must-resolve review gates (the story cannot decide these)

1. **Durable run semantics:** accepted amendment must define every v2 campaign event,
   envelope, revision transition, stop-pending distinction, replay row equality, and
   status/manifest derivation. The implementation follows that exact reducer; no ad-hoc
   enum update or synthesized event is permitted.
2. **Planned-but-unclaimed truth:** accepted amendment must distinguish `not-planned`
   from immutable `binding-only` and `claimed`, retain actual Plan bytes/ID/review before
   Journal claim, and never erase or fabricate an Operation.
3. **Actual-Plan review provenance:** accepted amendment must define independently stored,
   phase-tagged `actual-plan-prelaunch` review bytes/identity/inventory that bind each
   dynamic Plan before claim/first send; readiness or caller gate booleans cannot substitute.

Any conflict between the accepted v3 delta and this draft is resolved in favor of the bound
amendment. A changed or unaccepted amendment blocks implementation rather than inviting
local interpretation.

## Concrete CONSUMES (current APIs; signatures are read narrowly)

- `capstone_contract.validate_record(value: dict, kind: str) -> dict`;
  `decode_record(raw: bytes, kind: str) -> dict`;
  `verify_bytes(raw: bytes, expected: str) -> None`;
  `operation_id(grant_id: str, plan_sha256: str) -> str`;
  `start_request_digest(request: dict) -> str`;
  `bind_grant(plan: dict, grant_raw: bytes, authorization_raw: bytes, *, operator_uid: int) -> None`;
  `bind_observation(plan: dict, *, nonce: str, service_epoch: str, anchor: dict, now_ns: int, operator_uid: int) -> None`.
- `Ledger(root: Path)` is UID320-only and creates schema. Production opening must never
  call it. Existing methods: `object(content: bytes) -> str`, `tip() -> str`,
  `append_atomic(principal: int, event: dict, expectedTip: str, key: str, callback=None) -> dict`,
  `close()`; trusted in-process `lock`/`db` are transaction seams.
- `capstone_journal.open_existing(ledger: Ledger) -> Journal`;
  `open_public_fixture(ledger: Ledger, directory: Path) -> Journal`;
  `Journal.status(operation_id: str, authenticated_uid: int)`,
  `claim(start: dict, authenticated_uid: int)`,
  `record_reserved(operation_id: str, reservation: str)`,
  `mark_dispatch_pending(operation_id: str) -> Tuple[JournalRecord, Optional[DispatchPermit]]`,
  and `request_stop(operation_id: str, authenticated_uid: int)`.
- `StopCoordinator(root: Path, *, operator_uid: int, terminator=None, baseline_verifier=None,
  term_grace_seconds=1, kill_wait_seconds=1)`, plus `stop(principal, run, key, reason=None)`,
  `can_launch(run, epoch, principal=None)`, `register_launch(...)`, `terminate(...)`, and
  `handle(uid, message)`. Constructor DDL remains legacy-only; backend mode needs open-only.
- `AuthenticatedServer(path: Path, handler, *, control=False, allowed_uid=EVALUATOR)`
  and `control_call(path, request, *, expected_uid, timeout)` remain authenticated payload
  channels. Add a separate sendmsg/recvmsg rights channel; do not overload request JSON.
- `ReplayExecutor.command_watchdog(run: str, challenge: str)`,
  `finalize_result(run: str, result: dict)`, and `spawn_guest(args: list) -> subprocess.Popen`;
  `maintainer_specification(archive: bytes, challenge: str) -> dict`,
  `observation_outcome(observation: dict) -> str`, and `finding(outcome, specification, baseline)`.
  `ReplaySession.__init__/reserve/reproduce` remains legacy: backend replay context must not
  construct it or reserve twice.

## PRODUCES (re-estimated 26–34 files, ~6,000–9,000 changed LOC, ~2,000–3,000 test LOC)

New: `capstone_installation.py`, `capstone_backend_contract.py`,
`capstone_backend_schema.py`, `capstone_authority.py`, `capstone_campaign.py`,
`capstone_accounting.py`, `capstone_backend.py`, `capstone_projection.py`,
`capstone_review.py`, `capstone_review_service.py`, `capstone_launch.py`, `replay_material.py`, `capstone_replay.py`,
and `capstone_corpus_profile.py`. Modify only as needed:
`trusted_transport.py`, `control.py`, `control_worker.py`, `replay.py`,
`corpus_execution.py`, `capstone_client.py`, and `capstone_service.py`.
Add focused backend tests, one no-skip suite entrypoint, and
`docs/CAPSTONE_BACKEND.md`. No driver, scripts/capstone-driver, or report-only stage.

Minimum public source API:
`Installation.open_installed(role: str)` / `open_public_fixture(root: Path)`;
`Authority.issue_campaign(handles, auth_raw: bytes, spec_raw: bytes) -> bytes`;
`EvaluatorBackend.open_existing(installation, ledger, journal, control)`;
`observe/start_campaign/status/stop(request: dict) -> dict`;
`CampaignReplay.execute_leaf(context, leaf, permit) -> LeafOutcome`;
`LaunchBroker.prepare/launch/read/write/cancel/status`;
`Accounting.open_v4_read_only(...)`; `OperationalAccountingV5.open_existing(...)`
with `reserve_leaf/meter_leaf/settle_leaf/halt`; and SQL-only
`backend_stop_hook(db, receipt, control_run, epoch, operation, primary) -> None`.
Exact signatures may tighten only with accepted contract documentation and tests.

## Acceptance criteria

1. The story starts only with the parent-bound accepted v3 SHA and independent review.
   All three review findings above are demonstrably resolved in implemented records,
   reducer, replay, tests, and documentation; conflicting v2 behavior is removed.
2. Installed open-only topology validates exact InstallationV2 descriptor/root/UID/mode/inode/socket identity
   without create/repair, symlink escape, environment/profile/root override, or protected
   access during source work. `open_public_fixture` is private-temp only and every fixture
   result labels itself nonproduction.
3. Literal backend-v2 DDL, constraints, SQL guards, and full replay exactly implement the
   accepted campaign tables/events. SQLite schema/row/BLOB tampering, revision/backward
   steps, missing/extra rows, stale receipts, and cached-key mismatch fail closed. Journal
   v1 SQL, event format, replay, schema hash, and old v1-only accounting/replay behavior
   remain byte-for-byte unchanged.
4. Real temp-SQLite issuance is idempotent: same authorization/spec returns original bundle
   bytes; changed/extra/missing inputs refuse; intent/commit cuts and concurrent issuers
   never mint duplicate or orphan authority; reopened state exactly replays.
5. JIT execution has one owner capability and bounded start. Two leaves use distinct fresh
   observations/dynamic Plans under one static approval; first-tip stale precomputed Plans
   fail; select→review→bind→claim cuts retain immutable binding-only provenance; duplicate
   root start is status-only; unknown/restart fences work with no resume or public leaf bypass.
6. An independent ReviewV2 principal/store (fixed reviewer UID322, per exact correction)
   verifies and durably binds each actual Plan,
   hashes, operation, observation, policy, source/static review, and phase before claim.
   Wrong reviewer/phase/leaf/bytes/evidence or expiry denies before claim/send; unrelated
   anchor change fails unchanged `bind_observation`. Exact peer-checked review-plan,
   get-review and read-only review-context RPCs, crash-conservative reviewer index,
   request idempotency/expiry and dedicated callback capacity are implemented, not stubs.
7. AF_UNIX `sendmsg`/`recvmsg` transfers one locked gate open-file description by
   `SCM_RIGHTS`. Multiprocess tests prove queued/partial FD delivery, wrong count/inode/
   ancillary rejection, close-instead-of-LOCK_UN ownership, both stop orderings, lost
   COMMITTED, broker/evaluator death, and bounded deadlines using real harmless owned
   children. No mock substitutes for linearization, ownership, wait, reap, or PID identity.
8. Stop commits campaign authority plus exact v2 `stop-pending` state before cancellation;
   cancellation happens outside gate/ledger locks; verified cessation/integrity yields
   stopped only through replayable outcome, while failure remains recovery. Unplanned and
   binding-only leaves are fenced without fake Operations. Legacy control behavior outside
   backend mode is unchanged.
9. v4 is read-only and cannot reserve. A separately defined operational v5 object opens
   existing state only, carries complete lineage/holds, and implements positive deterministic
   reserve→trusted meter→settle→halt under cross-process exclusion. No activation, migration,
   reconciliation, release, reset, unstop, or Budget constructor bypass occurs.
10. Pre-reserved backend replay executes both fresh baseline/candidate leaves once each
    with separate permits/sends, real wait/reap and hang/crash handling, exact frozen corpus
    profile/spec mapping, phase-tagged gates, and truthful projection/manifest links. A
    binding-only or unknown leaf retains failure, never a fabricated Manifest.
11. Focused and full source regressions pass on Python 3.14, 3.12, and 3.9 where installed:
    no zero-test/skipped-required success, with exact commands, counts, stdout/stderr hashes,
    changed-file/source hashes, warnings, `pvg story verify-delivery` shape, and no protected
    metadata instrumentation. Existing baseline is 19 protocol + 25 journal tests on all three.
12. Independent architecture/security review and PM acceptance are recorded before any
    accepted epic merge. Source proof explicitly leaves all 11 gate phases and all seven
    capstone journeys unmet/not live-qualified; admission, promotion, production readiness,
    and q3hp mapping are not claimed.

## Test plan

Use standard-library tests and private `/private/tmp/grrr-backend-fixture-*` roots. Real
SQLite is created through explicit nonproduction schema fixtures or `Ledger.__new__` plus
literal DDL, with no UID patch/constructor bypass. Use process barriers and trace callbacks
for crash/concurrency cuts; use multiprocessing AF_UNIX plus `SCM_RIGHTS`/`flock` for FD
rights; spawn only short-lived harmless children owned and reaped by the broker. Assert
negative syscall/SQL guards and state truth, but label them source-only. Exercise every
campaign event, review denial, accounting cut, stop ordering, launch ambiguity, replay
tamper, immutable output, and v1 regression. Focused failures block delivery; broad live
journeys are deliberately not run. No fixture may hard-code an unavailable proof as a pass.

## Authorization and explicit limits

Allowed: implementation on its story worktree, local source commits, independent PM review,
and merge only into the accepted epic branch after all evidence passes. Forbidden in this
story: any `/Library/GRRR` access (even metadata), installation or topology mutation, v4
reconciliation, VM/replay against protected inputs, operational v5 activation, permanent
admission/promotion, main/production mutation, paid network or secret use, and push.
Concurrent edits outside this scope must be preserved.

## Estimate and unknowns

Estimate 26–34 files and 6,000–9,000 changed LOC including 2,000–3,000 tests. Parent must
bind independent acceptance of all exact inputs, without further guessed design deltas.
Source limitations that remain unknown unless separately qualified live are real
UID320/321/322/ACL/inode behavior, launchd
broker-death teardown, pinned image/catalog/build, current baseline, and complete journeys.

## Acceptance Criteria


## Design


## Notes


## nd_contract
status: accepted

### evidence
- PM closeout applied via pvg story accept on 2026-11-05.

### proof
- [x] Story closed after accepted label was applied.


## nd_contract
status: accepted

### evidence
- Independent review completed with a fresh-context, read-only reviewer (packet-based; code review, execution evidence parent-run). Verdict: REVIEW_RESULT: APPROVED. Verdict file SHA256 aea6a7ae47a459d963181eddd86c62896849887c414332b8b913ea44efc56b62, committed at b0bfad5. The reviewer confirmed F1 (durable manifest binding), F2 (select evidence refs), F3 (durable stop verification) and found no remaining fail-open path in the reviewed functions.
- Earlier rejected verdict retained at docs/evidence/source-backend/campaign-reducer-review-20261105.rejected-r1.md (SHA256 03ad04db987d9cafb3f1ba354d27e3058891d7e19e3235b59643f2bcc979d719); both findings from it were fixed before re-review.
- Final commit b0bfad526c09f2589eda10303c38f617e1d01a2e on story/GRRR-k3j7. Required suite: 261 tests, 0 failures, 0 errors, 0 skips on Python 3.14.3, 3.12.9 and 3.9.6. Parent-run evidence retained at docs/evidence/source-backend/campaign-reducer-test-run-20261105.txt.
- Operator/product owner approved the delivery in session. PM acceptance is therefore recorded against this exact commit and verdict.
- No merge, no push, no promotion, no admission, no installation and no /Library/GRRR access occurred. All 11 gate phases and all seven capstone journeys remain not-run.

### proof
- [x] AC1-AC11 implemented and verified at source.
- [x] AC12 independent review APPROVED and PM acceptance recorded.

## nd_contract
status: delivered

### evidence
- Both findings from the interrupted independent review are fixed in commit 1262472.
- Finding F2 (unchecked select evidence): the replay completion prefix now records the per-leaf result hash from campaign-advance, and campaign-select requires its evidence list to equal the sorted result refs of the completed leaves. Tampered or invented refs are rejected; a regression test covers both the reject and accept cases.
- Finding F3 (stop-outcome verified derived from run state): the durable stop-outcome object must now carry an explicit boolean verified flag. Append requires it to equal the verifier's verdict; replay derives stopped vs recovery-required from that durable flag and rejects a run state that contradicts it. Regression test covers the mismatch.
- Required suite: 260 tests, 0 failures, 0 errors, 0 skips on Python 3.14.3, 3.12.9 and 3.9.6.
- Review-environment note: the reviewer's in-sandbox run reported 8 setup errors because the worker permission profile denies /private/tmp while the fixtures require it. The same suites pass unmodified outside the worker on all three interpreters; this is a sandbox limitation, not a test failure, and is recorded rather than papered over.

### proof
- [x] F1, F2, F3 fixed with regression tests.
- [ ] AC #12: independent review verdict still outstanding; three provider 429s so far.

## nd_contract
status: delivered

### evidence
- F1 remediated in commit 6b02ba1. Replay no longer trusts the submitted run row for the terminal hash: finish, fence and stop-outcome resolve the manifest, FailureRecord and FenceSnapshot/StopOutcome from the durable hash-addressed object store, verify each object digest, and re-check manifest schema, campaign_plan_sha256, leaf cardinality and terminal equality. A missing or tampered object fails replay.
- Append now persists evidence objects before the referencing event (store_object with O_EXCL/O_NOFOLLOW and fsync); a failed transaction may leave unreferenced inert objects, never authority.
- New regression test: deleting the terminal manifest object makes index.validate() fail. Integration tests: 8. Required suite: 258 tests, 0 failures, 0 errors, 0 skips on Python 3.14.3, 3.12.9 and 3.9.6.
- Known residual: fence/stop replay validates object roles and snapshot links but does not re-derive the manifest contents from the full gate set, because gates are not stored in the event. Recorded as a limitation, not a claim.

### proof
- [x] F1 fixed with a regression test.
- [ ] AC #12: independent review verdict still outstanding (three provider 429s); PM approval recorded.

## nd_contract
status: delivered

### evidence
- Operator/product owner explicitly approved the delivery in session (2026-11-05). This is PM acceptance of the delivery intent; it does not by itself satisfy the independent-review gate.
- Independent review attempted three times with three routes (zai-coding/glm-5.3 twice, custom/Qwen-Ambassador/Qwen3.8-Max, deepseek/deepseek-v4.1-flash). Every attempt ended in provider 429 after 10-24 calls; no verdict file was produced. All attempts are retained under outputs/paivot-autoloop-pilot/coding-adapter/runs/review-*.
- Partial reviewer output before the 429 raised finding F1: replay-mode branches for finish/fence/stop-outcome derive the terminal hash from the submitted run row and then compare evidence against that same value, which is circular. A forged event carrying a consistent fake result_object and matching evidence would pass replay because the manifest is not recomputed and no durable manifest object is checked.
- F1 is accepted as a real gap. It must be fixed before AC #12 is considered satisfied: replay must resolve the terminal manifest from a durable typed object (hash-addressed) and recompute/verify the manifest links, or the action must be unable to replay-accept without it.

### proof
- [x] Delivery package and PM approval recorded.
- [ ] AC #12: independent review verdict and F1 remediation outstanding; no acceptance or merge claimed.

## nd_contract
status: delivered

### evidence
- Transitioned via pvg story deliver on 2026-11-05.

### proof
- [ ] Developer evidence block must remain authoritative above this contract.


## nd_contract
status: delivered

## Implementation Evidence

PROOF:

### CI/Test Results
Commands run:
- PYTHONPATH=research:tests /opt/homebrew/bin/python3.14 tests/unit_capstone_backend_suite.py
- PYTHONPATH=research:tests /opt/homebrew/bin/python3.12 tests/unit_capstone_backend_suite.py
- PYTHONPATH=research:tests /usr/bin/python3 tests/unit_capstone_backend_suite.py
- PYTHONPATH=research:tests /opt/homebrew/bin/python3.14 -m unittest discover -s tests -p 'unit_capstone*.py'
Summary: PASS source257 tests on EACH of Python3.14.3,3.12.9,3.9.6; failures0/errors0/skipped0, each exit0. Campaign reducer, CampaignManifestV2 derivation, real-Ledger append, two-leaf campaign, fence and both stop-outcome paths covered. All 11 gate phases and all seven capstone journeys NOT-RUN; no installed topology, VM replay, admission, promotion, production or q3hp claim. Producing SHA8c3e607cf4611da88d3bd3200593cc3e150e1268.

- Commands run:
  - PYTHONPATH=research:tests /opt/homebrew/bin/python3.14 tests/unit_capstone_backend_suite.py
  - PYTHONPATH=research:tests /opt/homebrew/bin/python3.12 tests/unit_capstone_backend_suite.py
  - PYTHONPATH=research:tests /usr/bin/python3 tests/unit_capstone_backend_suite.py
  - PYTHONPATH=research:tests /opt/homebrew/bin/python3.14 -m unittest discover -s tests -p 'unit_capstone*.py'
- Summary: source-only delivery. 257 tests per interpreter, 0 failures/errors/skips. No external CI claimed. Gate phases, capstone journeys, installation, admission and promotion remain not-run and are not claimed.

### Commit
- Branch: story/GRRR-k3j7
- SHA: 8c3e607cf4611da88d3bd3200593cc3e150e1268
- Worktree clean at delivery time; no merge, no push, no protected access.

### Acceptance Criteria
- [x] AC1: accepted design and independent review bound; implementation conforms at source.
- [x] AC2: InstallationV2 open-only topology, 44 source tests.
- [x] AC3: backend-v2 schema, index, reducer, replay equality and stop-pending transitions.
- [x] AC4: issuance idempotence, intent continuity and reopen behaviour.
- [x] AC5: two-leaf JIT composition with distinct Plans and verifier-injected owner/gate proof.
- [x] AC6: ReviewV2 store/service/RPCs with peer identity, idempotency and crash-conservative replay.
- [x] AC7: AF_UNIX SCM_RIGHTS gate/broker with real multiprocess and wrong-inode tests.
- [x] AC8: stop commits stop-pending before cancellation; verified outcome stopped, else recovery-required.
- [x] AC9: v4 unchanged and read-only; operational v5 accounting implemented and tested.
- [x] AC10: two-leaf campaign executes through the real Ledger with truthful manifest links.
- [x] AC11: 257 regressions reproducible on Python 3.14, 3.12 and 3.9 with zero skips.
- [ ] AC12: independent review and PM acceptance pending for this delivery.

### Independent Review and Scope
- Pending: one fresh-context read-only review of the campaign reducer, the Ledger version change, the journal version check and the integration tests. No merge, push, promotion, admission, installation or /Library/GRRR access is authorized by this delivery.

## nd_contract
status: delivered

## Implementation Evidence

Source-level implementation on story/GRRR-k3j7 at commit 8c3e607. All changes are inside the story worktree; nothing was merged, pushed, promoted, admitted, or installed.

- Campaign-v2 reducer: research/capstone_backend_index.py implements campaign-start, campaign-select, campaign-leaf-bind, campaign-advance, campaign-finish, campaign-fence, campaign-stop-outcome, plus derive_manifest (CampaignManifestV2) and the real-Ledger append_campaign path.
- Ledger change is additive: research/ledger.py accepts an explicit envelope version (1 or 2, default 1); research/capstone_journal.py expects version 2 only for the shared CAMPAIGN_EVENT_FORMAT and version 1 otherwise; research/common.py holds that constant.
- Operational v5 accounting: research/accounting_v5.py (open-existing-only, lineage/holds, reserve-meter-settle-halt, cross-process exclusion, fail-closed unknown outcome).
- Tests: tests/unit_capstone_campaign_reducer.py (48), tests/unit_capstone_campaign_append.py (7), tests/unit_capstone_accounting_v5.py (8), plus the existing installation/review/launch/index suites.

## CI/Test Results

Commands run:

- PYTHONPATH=research:tests /opt/homebrew/bin/python3.14 tests/unit_capstone_backend_suite.py
- PYTHONPATH=research:tests /opt/homebrew/bin/python3.12 tests/unit_capstone_backend_suite.py
- PYTHONPATH=research:tests /usr/bin/python3 tests/unit_capstone_backend_suite.py
- PYTHONPATH=research:tests /opt/homebrew/bin/python3.14 -m unittest discover -s tests -p 'unit_capstone*.py'

Results:

- Python 3.14.3: Ran 257 tests, OK, 0 failures, 0 errors, 0 skipped
- Python 3.12.9: Ran 257 tests, OK, 0 failures, 0 errors, 0 skipped
- Python 3.9.6:  Ran 257 tests, OK, 0 failures, 0 errors, 0 skipped
- Suites assert zero-test and skipped success are failures.

## Summary:

The source campaign reducer, CampaignManifestV2 derivation, real-Ledger campaign append path, two-leaf end-to-end campaign, fence, and both stop-outcome paths are implemented and proven at source on three interpreters. All 11 gate phases and all seven capstone journeys remain not-run / not live-qualified; installation, admission, promotion, production readiness, live VM replay, and q3hp mapping are explicitly not claimed. Commit 8c3e607.

### evidence
- commits c55f722, 07dd656, 8395acd, 12f5f80, d48e7c6, 74d2eaf, 2c7df68, 74eb40e, d38706d, 63394d4, f246226, 2b0d259, 8c3e607
- independent design acceptance 55155e52a5543325b1b071ca66b596e3795fa9456f04e6fda0efb9ce43e425d1 and review 2e6d50ddd3e638365284f344cc5412975362cd6d7ee94dc87651e402b8b9d3d3
- no /Library/GRRR access, no installation, no replay, no admission, no promotion, no merge, no push

### proof
- [x] AC #1: accepted design and independent review bound; implementation conforms at source.
- [x] AC #2: InstallationV2 open-only topology implemented with 44 source tests.
- [x] AC #3: backend-v2 schema, index, reducer, replay equality and stop-pending transitions implemented and tested.
- [x] AC #4: issuance idempotence, intent continuity and reopen behaviour tested.
- [x] AC #5: two-leaf JIT composition with distinct Plans, verifier-injected owners and one permit per leaf.
- [x] AC #6: ReviewV2 store/service/RPCs with peer identity, idempotency and crash-conservative replay.
- [x] AC #7: AF_UNIX SCM_RIGHTS gate/broker with real multiprocess and wrong-inode tests.
- [x] AC #8: stop commits stop-pending before cancellation; verified outcome yields stopped, otherwise recovery-required.
- [x] AC #9: v4 unchanged and read-only; operational v5 accounting implemented and tested.
- [x] AC #10: two-leaf campaign executes through the real Ledger with truthful manifest links; unverified actions refuse.
- [x] AC #11: 257 source regressions reproducible on Python 3.14, 3.12 and 3.9 with zero skips.
- [ ] AC #12: independent review and PM acceptance pending for this delivery.

## nd_contract
status: in_progress

### evidence
- campaign-stop-outcome proven through the real Ledger and the real base safe-stop hook: a safe-stop event with run_before_revision/run_after moves the campaign run to stop-pending in the same SQL-only hook; a verified stop provider resolves it to stopped with active_leaf null; an unverified provider resolves it to recovery-required. Both asserted through index.validate().
- tests/unit_capstone_campaign_append.py: 7 integration tests covering start, select, bind, advance, two-leaf finish, fence, and both stop-outcome outcomes. Reducer: 48 tests. Required suite: 257 tests, 0 failures, 0 errors, 0 skips on Python 3.14.3, 3.12.9 and 3.9.6. Commit 8c3e607 on story/GRRR-k3j7; no merge or push.
- Source-level campaign reducer work is complete. All 11 gate phases and all seven capstone journeys remain not-run / not live-qualified; installation, admission, promotion, production readiness and q3hp mapping are not claimed.
- Next gate is AC #12 only: delivery package, independent review, PM acceptance.

### proof
- [x] AC #3/#5/#10 source campaign reducer, manifest, ledger append, two-leaf execution, fence and stop outcomes.
- [x] AC #11 257 tests reproducible on 3 interpreters with zero skips.
- [ ] AC #12 independent review and PM acceptance pending; no delivery claimed yet.

## nd_contract
status: in_progress

### evidence
- Full two-leaf campaign now runs through the real temp Ledger: campaign-start -> select(0) -> leaf-bind(0) -> advance(0) -> select(1) -> leaf-bind(1) -> advance(1) -> finish, with real issued fixtures and test verifiers. Asserted run state/revision after each append, completed state with result_object=terminal at the end, and replay equality on validate().
- Added fence-after-start through the Ledger: running -> recovery-required with result_object=manifest hash and active_leaf preserved.
- Replay-mode split implemented: _validate folds campaign events with replay=True, skipping live verifier calls only (liveness cannot be re-proved from stored history) while keeping structural, evidence-link, revision, immutable-field and row-equality checks. Append always requires the verifiers.
- tests/unit_capstone_campaign_append.py: 5 integration tests; reducer 48; required suite 255 tests, 0 failures, 0 errors, 0 skips on Python 3.14.3, 3.12.9 and 3.9.6. Commits f246226 and 2b0d259 on story/GRRR-k3j7; no merge or push.
- Remaining source gap: campaign-stop-outcome has reducer-level tests but no Ledger-level case, because stop-pending is produced by the base apply_backend_stop hook and that wiring is not exercised for campaign runs yet.

### proof
- [x] AC #5/#10: two-leaf JIT campaign executes through the ledger with distinct Plans, permits (verifier-injected) and truthful manifest links.
- [ ] AC #3: stop-outcome Ledger case via the base safe-stop hook.
- [ ] AC #12 independent review/PM acceptance pending; no delivery claimed.

## nd_contract
status: in_progress

### evidence
- Real-Ledger campaign append path implemented: BackendIndex.append_campaign stages a copy, applies the campaign reducer with all six injected verifiers, writes the delta, appends a version-2 envelope, and re-validates. Cached-retry equality returns the stored receipt; changed bytes fail.
- Ledger change is additive: append_atomic/_append accept an explicit version (1 or 2, default 1). Journal validation now expects version 2 only for the shared capstone-campaign-event-v2 format and version 1 otherwise, so base and journal chains are unchanged.
- tests/unit_capstone_campaign_append.py (3 tests) proves through a real temp Ledger and real issued fixture: campaign-start appends and replays with equality; campaign-select without the joins verifier refuses Unavailable and does not advance the ledger tip; a changed cached campaign event fails.
- Required suite: 253 tests, 0 failures, 0 errors, 0 skips on Python 3.14.3, 3.12.9 and 3.9.6. Commit 63394d4 on story/GRRR-k3j7; no merge or push.
- Next exact gap: no full two-leaf campaign run (start -> select -> bind -> advance x2 -> finish) through the Ledger yet, and no fence/stop-outcome ledger case.

### proof
- [x] AC #3: campaign envelopes now append through the real Ledger with replay equality.
- [ ] AC #5/#10: full two-leaf end-to-end campaign and fence/stop ledger cases.
- [ ] AC #12 independent review/PM acceptance pending; no delivery claimed.

## nd_contract
status: in_progress

### evidence
- All seven campaign-v2 actions now exist in research/capstone_backend_index.py: start, select, leaf-bind, advance, finish, fence, stop-outcome, plus derive_manifest (CampaignManifestV2). Fence requires an authenticated controller snapshot and evidence exactly [failure, snapshot, terminal]; stop-outcome requires a stop verifier and resolves stopped only when verified, otherwise recovery-required with active_leaf preserved. Both refuse Unavailable without their injected verifier.
- Replay equality was already enforced in _validate: derived state must equal _snapshot(db) row-for-row, idempotency rows must match, journal validation runs, and a campaign claim without a prior backend binding fails.
- tests/unit_capstone_campaign_reducer.py: 48 tests. Required suite: 250 tests, 0 failures, 0 errors, 0 skips on Python 3.14.3, 3.12.9 and 3.9.6. Commit d38706d on story/GRRR-k3j7; no merge or push.
- Newly identified exact gap: BackendIndex.append_transition only builds base v1 envelopes, so campaign envelopes have no real ledger append path yet. Reducer unit tests pass but no end-to-end campaign run through the Ledger exists.

### proof
- [x] AC #3 reducer: all seven actions plus manifest derivation, fail-closed on missing verifiers.
- [ ] AC #3/#5/#10: campaign append path through BackendIndex, end-to-end two-leaf fixture, replay equality on reopen.
- [ ] AC #12 independent review/PM acceptance pending; no delivery claimed.

## nd_contract
status: in_progress

### evidence
- CampaignManifestV2 derivation implemented (research/capstone_backend_index.py::derive_manifest): exact leaf entries with not-planned / binding-only / claimed enum, null rules, concrete FailureRecordV1 for every manifest-less leaf, Plan byte/selfhash/operation-id link checks, exact 11-gate input required (no defaulted gates), explicit now_ns required (no fabricated timestamp), execution completed|partial|not-run from the replay completion prefix, verification blocked, admission blocked, promotion disabled, terminal hash = SHA256(C(manifest)).
- campaign-finish implemented: requires an injected manifest provider (else Unavailable), every leaf advanced, manifest campaign_plan_sha256 and leaf cardinality match the run, evidence exactly [terminal], run -> completed with result_object=terminal, revision+1, immutable fields unchanged.
- tests/unit_capstone_campaign_reducer.py: 41 tests. Required suite: 243 tests, 0 failures, 0 errors, 0 skips on Python 3.14.3, 3.12.9 and 3.9.6. Commit 74eb40e on story/GRRR-k3j7; no merge or push.
- Five of seven campaign actions plus the terminal manifest now exist at source. Remaining: campaign-fence and campaign-stop-outcome, both requiring FenceSnapshotV2 / StopOutcome verifier injection.

### proof
- [x] AC #3 reducer: five of seven actions plus CampaignManifestV2 derivation, all fail-closed.
- [ ] AC #3/#5/#10: campaign-fence, campaign-stop-outcome, full replay row equality.
- [ ] AC #12 independent review/PM acceptance pending; no delivery claimed.

## nd_contract
status: in_progress

### evidence
- Campaign-v2 reducer now implements four exact actions in research/capstone_backend_index.py: campaign-start, campaign-select, campaign-leaf-bind and campaign-advance, all wired through _validate with format-derived envelope version (base v1, campaign v2).
- select requires an injected completion-joins verifier and refuses Unavailable without it; leaf-bind requires an injected live owner/gate/window verifier and refuses without it; advance requires an injected claim/exit/settlement proof and refuses without it. No action assumes unverified proof.
- bind validates canonical Plan bytes, plan_sha256, byte digest, derived operation id, Start bytes/embedded Plan identity, exact evidence [review_hash], no duplicate binding/plan, no consumed grant, immutable run fields and revision+1.
- advance validates the active leaf has a bound Plan, exact single evidence hash, immutable fields, revision+1, clears active_leaf and records the completed index into the reducer progress prefix.
- tests/unit_capstone_campaign_reducer.py: 33 tests. Required suite: 235 tests, 0 failures, 0 errors, 0 skips on Python 3.14.3, 3.12.9 and 3.9.6. Commits d48e7c6, 74d2eaf, 2c7df68 on story/GRRR-k3j7; no merge or push.
- Exact remaining boundary recorded: campaign-finish/fence/stop-outcome require the terminal CampaignManifestV2 derivation (spec section 2), which does not exist yet and must not be approximated.

### proof
- [x] AC #3 reducer: four of seven actions implemented exactly with fail-closed verifier injection.
- [ ] AC #3/#5/#10: CampaignManifestV2 derivation, finish/fence/stop-outcome, full replay equality.
- [ ] AC #12 independent review/PM acceptance pending; no delivery claimed.

## nd_contract
status: in_progress

### evidence
- Campaign-v2 envelope validation and the exact campaign-start reducer implemented in research/capstone_backend_index.py::_campaign, wired into _validate. Start enforces: null previous_revision, no binding/leaf_plan, exact 10-field run row, running/null/result-null/revision-0, unstopped issued campaign join, no other active run, canonical v1 Plan bytes with plan_sha256 and derived operation_id, existing grant join, sorted-unique 2-hash evidence, exact domain idempotency key; fills last_event and intent_anchor from the receipt digest.
- Every other campaign action still raises Failure('Unavailable','Campaign action not implemented: ...'); no stub accepts, so no campaign event can be folded unchecked.
- tests/unit_capstone_campaign_reducer.py: 12 tests, including one that proves all six unimplemented actions refuse and leave no run row.
- Required suite now 214 tests, 0 failures, 0 errors, 0 skips on Python 3.14.3, 3.12.9, 3.9.6. Commit 12f5f80 on story/GRRR-k3j7; no merge or push.

### proof
- [x] AC #3 envelope + campaign-start slice implemented and adversarially tested.
- [ ] AC #3/#5/#10 remaining actions (select, leaf-bind, advance, finish, fence, stop-outcome) plus replay equality and manifest derivation.
- [ ] AC #12 independent review/PM acceptance pending; no delivery claimed.

## nd_contract
status: in_progress

### evidence
- Required public source suite now includes v5 accounting: 202 tests, 0 failures, 0 errors, 0 skips on Python 3.14.3, 3.12.9 and 3.9.6 (tests/unit_capstone_backend_suite.py). Commit 8395acd on story/GRRR-k3j7; no merge or push.
- v5 operational accounting hardened after real flake: removed an over-strict rollback-journal open refusal that broke legitimate concurrent writers (SQLite already resolves it under locks); child open now reports failures; 4/4 repeats green on 3.9 and 3.14.
- Provider lane measured: zai-coding/glm-5.3 produced the v5 draft then died on 429 at 16-17 calls three times; custom/Qwen-Ambassador was slower and non-convergent. Gate failed closed with 0 unresolved reservations each run; ledgers retained.
- Exact remaining blocker identified in source: research/capstone_backend_index.py::_validate raises Failure('Unavailable','Campaign evidence reducer not implemented') for any capstone-campaign-event-v2 envelope. AC #3/#5/#10 cannot be met until that reducer (amendment v3 section 1) is implemented exactly, with no local interpretation and no stub.
- Everything else is source-complete and tested at source: installation topology 44 tests, backend schema/index/replay/stop 29+ tests, ReviewV2 store/service/RPCs, SCM_RIGHTS launch broker, two-leaf composition, v5 accounting.

### proof
- [x] AC #9 v5 object implemented and tested at source (8 adversarial tests).
- [x] AC #11 source regressions reproducible on 3 interpreters, zero skips.
- [ ] AC #3/#5/#10 blocked on the campaign reducer; it is not implemented and must not be approximated.
- [ ] AC #12 independent review/PM acceptance pending; no delivery claimed.

## nd_contract
status: in_progress

### evidence
- Real gated coding bridge verified live: Autoloop hub/worker -> pinned Codex CLI -> loopback provider gate (caller secret held outside worker; per-call worst-case SQLite reservation; hard call/budget caps; uncertain dispatch halts) -> zai-coding/glm-5.3 and custom/Qwen-Ambassador/Qwen3.8-Max. Gate suite 14 passed. Scratch two-turn loop exit 0 (progress=2, shared ledger). Boundary probes in the real worker denied operator-secret read and direct network.
- GRRR worktree loop runs: two runs advanced the real story then ended on provider 429 (16 calls/2372357 micro-USD reserved/0 unresolved; 9 calls Qwen). No fabricated retry; ledgers retained under outputs/paivot-autoloop-pilot/coding-adapter/runs/.
- Parent integrated and corrected worker WIP: missing-store now fails closed; InvalidInput passes through; meter-before-settle legal; tamper rejection non-mutating; unknown-commit halts and fences reuse; multiprocessing worker hoisted for Python 3.14.
- Current verified suite: PYTHONPATH=research:tests /opt/homebrew/bin/python3 -m unittest discover -s tests -p 'unit_capstone*.py' => Ran 195 tests, OK, 0 skipped (includes new tests.unit_capstone_accounting_v5, 8 tests OK).
- Story-branch WIP commits (no merge/push): c55f722 installation authority/inventory + launch socket race fix; 07dd656 operational v5 accounting object research/accounting_v5.py + tests/unit_capstone_accounting_v5.py.
- Added worker/loop.py resume-usage fallback and worker/keep_going.py cycle driver (verify-gated, stop-file, no merge/push) so bounded cycles continue without manual 'continue'.

### proof
- [x] AC #9 source-level v5 object now exists and passes 8 focused adversarial tests; independent review and integration remain outstanding.
- [x] Autoloop-to-real-AI-worker source lane proven for real worktree turns under enforced cost/call caps; 429s halt rather than bypass.
- [ ] AC #2-8, #10-11 full backend implementation and reproduced evidence remain incomplete.
- [ ] AC #12 independent security/PM acceptance pending; no accepted merge.

## nd_contract
status: in_progress

### evidence
- Parent ran owned synthetic same-user process canary using a native C sysctl client. Host positive control and each of three sandbox profiles (deny sysctl-read, process-info-pidinfo, or process-info-pidfileportinfo) could read the synthetic marker; no real credentials were used. Result /tmp/grrr-native-sysctl-result-v2.json SHA256 d4894ce68ce95990e8e780e6f881e821891da4b9e895259e73b114677d15e8e9. This rejects those candidate isolation approaches; it does not establish a complete sandbox profile.
- The nonproduction request-controller candidate now derives synthetic reservations from fixed policy rates instead of caller-supplied cost; parent and independent reviewer each observed 10 passing tests. controller.py SHA256 fd968f4fcf0d7cf19971164e577d719a2653ed07aebc67380d03bdd67dbd923b, test_controller.py SHA256 36b05ebdfef85f52e2c63dd55ae3062b39b46607d751d23aa992e836630c02fb. Review approval covers this pricing calculation only, not provider currency, accounting integrity, or SQLite security.
- Independent channel review found guest file operations lack a deadline. Docstring corrected; reviewer confirmed wording only, underlying issue remains. Parent reran 22 passing channel tests; vm_channel.py SHA256 d6435426d6ee4b7587cac76e0f585c6f7006e4e28fe6235b390cd55249b4039c.
- These uncommitted artifacts are outside the repository under outputs/paivot-autoloop-pilot/coding-adapter. No real provider, credentials, protected path, VM, replay, promotion, production mutation, merge, or push occurred in this work.

### proof
- [x] Synthetic zero-price caller bypass corrected and narrowly independently reviewed.
- [ ] Operating-system isolation, real provider pricing, persistent accounting, actual AI coding dispatch through Autoloop, and GRRR story acceptance remain incomplete.

## nd_contract
status: in_progress

### evidence
- Operator requested the real PAIVOT/Autoloop coding loop with a credential-owning controller and isolated coding workspace. Two source-only candidate components are outside the repo under outputs/paivot-autoloop-pilot/coding-adapter/: trusted-controller/controller.py SHA256 1c4ab0601a7e4b759240a6817e29055086d01e251abcdcc0f50e089e097ff8dc, workspace-channel/vm_channel.py SHA256 8bddd162bf1a917ec01db23587a4ce796db5c8e5f5619f453251e0ca53818a12.
- Parent reran 7 controller tests and 22 channel tests; all passed. They are synthetic provider and local socketpair tests, not actual AI, provider cost enforcement, OS isolation or VM evidence. Independent security reviews did not finish. Both components are unaccepted WIP, not yet used for any live dispatch.
- Controller uses caller-supplied synthetic costs and reopens SQLite by pathname after the initial check, so it does not establish trusted real-spend enforcement or a protected database boundary. The channel supports only ping/read_file; it does not run coding commands. Both must remain disconnected from live operation until gaps are addressed.
- A separate synthetic macOS sandbox probe showed unrestricted host read of a synthetic process marker. Denying sysctl-read made Python fail importing ctypes before the targeted read, so this test is inconclusive and does not establish isolation. No real credentials or protected paths used.

### proof
- [x] Candidate components exist and basic source-only tests passed.
- [ ] Security review, actual isolation, real budget enforcement, real AI worker, Autoloop integration, sustained operation, and GRRR story acceptance are incomplete.

## nd_contract
status: in_progress

### evidence
- Source-only WIP: tests/unit_capstone_backend_suite.py now includes three existing untracked installation test modules; SHA256 df53be40567b1de3c86b2d521bae247e6578ceb06c002943caa1863fe2fb46b1. These modules and their source must accompany any later commit; this change is not delivered or accepted.
- Parent ran the expanded suite: 194 tests, 0 failures, 0 errors, 0 skipped. Log /private/tmp/grrr-suite-194-20261105.log SHA256 9ec5bd0d62a44b5ae9da5ed3c91d06b0dcf2cd0d1f0bec4ff56ac81551b3c0e9. This does not qualify the protected install or capstone.
- Autoloop finite verification run runs/verify-1793854654196335000/result.json SHA256 511b932722bdd04582dbd39a3473db6375cca66129dd8bb3dc398ba623eea595: two command jobs passed 22 and 29 tests; PAIVOT returned wait, no model calls in Autoloop jobs. This did not dispatch the AI worker or prove continuous autonomous coding.
- Independent review of the suite inclusion did not complete; no review approval claimed. No protected access, replay, admission, promotion, merge or push.

### proof
- [x] Expanded source suite passes without skips.
- [ ] Independent review and full story acceptance remain outstanding.
- [ ] Autoloop-to-real-AI-worker dispatch and protected installation remain unproven.

# Live provider and isolation checkpoint

- One direct routed model probe returned the expected answer. Router metadata
  reported the approved coding route, successful status, and one upstream attempt.
  No repository contents or operator credential were supplied in the prompt.
- Two disposable standalone Codex CLI probes, with a dummy non-credential and
  synthetic prompt, failed authentication. They do not establish a real Autoloop
  coding run or an authenticated GRRR evaluator.
- A synthetic same-UID process canary showed that the tested Codex sandbox could
  read the other process's environment via the kernel process-argument interface.
  The control process used only a synthetic marker. This is not a credential-safe
  boundary and does not prove all possible sandbox configurations are unsafe.
- A synthetic memory-visibility check was inconclusive: host and sandbox both
  failed to obtain the target task port, so the host positive control failed.
- No protected installation access, evaluator replay, permanent contract admission,
  promotion, merge, push or production mutation occurred.

## Installation cycle design checkpoint (2026-11-04)

- `installation-cycle-v2-spec-20261104.md` SHA256 `599503fffda03576882642c57928a76d66659c2a28e0ee4518f6d1b5c5f21027` and `installation-trust-contract-proposal-20261104.md` SHA256 `d9f05bef3db4af4f67a97e7fd35146624fb7dfd19eea5a41455414f5d95ea0fa` are PROPOSAL ONLY.
- Independent reviewers confirmed the candidate dependency order is acyclic; both reviews found material implementation and activation gaps. A UID-bound discrepancy was corrected and narrowly re-reviewed; other gaps remain.
- No schema acceptance, protected installation, real coding launch, replay, promotion, merge or push. Preserve all untracked WIP; no active worker owns these files.

## Source checkpoint: installation authority joins (2026-11-04)

- `research/capstone_installation_authority.py` SHA256 `7673d23fb93d363a7b04e57416433b181191b9502e065e53c644ca7c6eefd317`; `tests/unit_capstone_installation_authority.py` SHA256 `fff0887e2ab225016ff7bb24691a05705247a62cf484ac964b11624bb890c27e`.
- Source-only codecs and private-temp inventory joins; protected installation authority remains unavailable. The reviewer found an incorrect resolver test; it was corrected and independently re-reviewed, 10/10 guarded tests passing. The later `RecoveryRequired` branch is not proven by that test.
- Accepted full-byte descriptor/registry/authorization hashes form a construction cycle. The proposed projection repair received GAPS_FOUND: exact schemas, replay, provenance, version separation and migration remain unapproved. Proposal SHA256 `a0aeee3b6d48019769430fe734871b9b0c9d5ec4562f1d8db9d3e1185861ea2b` explicitly labels that review outcome.
- No protected metadata/content access, production authority, live replay, story delivery, acceptance, merge or push.

## Source checkpoint: installation fixture (2026-11-04)

- Private-temp source only; `open_installed` remains unavailable before metadata access. No protected installation or provenance has been qualified.
- `research/capstone_installation.py` SHA256 `e37f856f299114a3b8e0b73ab7fdcd790b903e7b3d26a0a65a4f18394a2c76b0`; tests SHA256 `e1854faf6938ac931e10f57f27548b7334892edc8112569d0b10a146e9aa8986`.
- Independent review exercised real temporary Darwin ACLs and identified a close-failure descriptor cleanup defect. The fix was independently re-reviewed with real descriptors and injected close failure.
- Parent combined guarded source run: 93 tests, zero failures, errors, skips or protected-path attempts; log SHA256 `ef1085d16e7fb0cb5d16f11a0c3add039f1336c7743edcf089f5555437ce6758`.
- Reviewed WIP and test log preserved in `.git/paivot/wip/GRRR-k3j7/installation-acl-reviewed-20261104/`. No delivery, acceptance, installation, replay, merge or production change.

## Source checkpoint: detached fixture inventory (2026-11-04)

- Scope: NONPRODUCTION fixture bytes only. Stable installation authority is not implemented and requests for it are refused before filesystem access.
- Source SHA256: `15df4cd7babdf241e66e0e52354f1d0be7d6c31f8b0c1992fecba5738334b345`; tests SHA256: `33a01a418dd62b41776d9d533f44c23ebeef3ad23092f03e20387d7cf8eecd81`.
- Parent guarded run: 74 source tests passed, zero errors, failures, skips or protected-access attempts; independent scoped reviewer validated 15 fixture tests on Python 3.9, 3.12 and 3.14.
- Deterministic adversarial cases replace a name and rebind the root after recheck. Returned bytes remain bound to the expected digest; the result makes no stable-namespace claim.
- Untracked source and tests preserved under `.git/paivot/wip/GRRR-k3j7/inventory-detached-20261104/`. This is WIP: no story delivery, acceptance, protected installation, or live-capstone claim.

## nd_contract
status: in_progress

### evidence
- pvg loop next selected GRRR-k3j7; atomic claim dev-GRRR-k3j7. Owned .claude/worktrees/dev-GRRR-k3j7 on story/GRRR-k3j7 from2b601462ba0ffb5aee6239aa22b06c26801dfaf9.
- Independent design acceptance55155e52a5543325b1b071ca66b596e3795fa9456f04e6fda0efb9ce43e425d1 and review2e6d50ddd3e638365284f344cc5412975362cd6d7ee94dc87651e402b8b9d3d3 verified from actual artifacts. Exact four normative input hashes are embedded in self-contained story description; no worker can self-approve source delivery.
- /root/implement_backend_contracts exact GLM Coding Plan owns ONLY capstone_backend_contract.py and its focused unit test; /root/implement_executable_backend bounded Astra owns remaining listed source/tests/docs. They are told not alone and cannot revert concurrent edits. No recursive delegation, source commits centrally coordinated.
- Real private-temp SQLite/AF_UNIX/SCM_RIGHTS/harmless-owned-child positive source tests required. Source factories remain nonproduction. Existing baseline19+25tests each passed all3interpreters; zero required skips. Docker absent; no dependency/network setup authorized.
- Every original12AC remains required; no source implementation/PM/runtime success claimed at dispatch. All11 gates/all7 capstone journeys unchanged. No protected access, installation, activation/reconcile/unstop, VM/live replay, permanent admission/promotion, main/prod or push authorized.

### proof
- [x] AC #1 prerequisite: exact accepted design and independent review exist, implementation must still demonstrate conformance.
- [ ] AC #2-11: implementation and parent reproduced evidence pending.
- [ ] AC #12: independent security/PM acceptance pending; no accepted merge permitted yet.

## nd_contract
status: in_progress

### evidence
- Operator agreed to finish the required core FIRST, then consider ranked optional autoresearch/adaptation additions. User asks for ONE coordinated completion delivery rather than personally managing internal stages. This is not permission to drop original gates or transfer old exact-target live grants to changed code.
- Fresh HEAD2b601462ba0ffb5aee6239aa22b06c26801dfaf9; root clean, story WIP uncommitted/unaccepted. pvg loop next reports GRRR-k3j7 sole in-progress and q3hp/capstone blocked. Existing author/contract handles conclusively terminal; cleared dead developer handle, no blind loop recover or worktree removal.
- Preserved14 exact public WIP files179505bytes before worker replacement: .git/paivot/wip/GRRR-k3j7/resume-1793831735621994000/; tarSHA dcd05d3949c7636fd3b876cfb2f7aaaa04744fa5a935941bcdf36d30c4681b92, per-file hashes/base/status receipt present. No protected/private files included.
- Failed GLM contract worker produced no owned module/test file. Fresh exact Qwen Ambassador /root/unblock_core_review_contract now owns ONLY pure ReviewV2/codec/hash module+tests to unblock real reviewer/composition tests, unsupported broader schemas remain explicit WIP. No mocks or universalpass substitute.
- Fresh exact GLM /root/review_launch_rework independently reviews launch corrections against prior F1-F4 rejection at exact new source/test hashes. Re-review pending, not accepted. Source work remains current12ACs, not a weakened delivery.
- Original author reports72 source tests all3interpreters for old51+new21launch; parent must independently reproduce current rework and full reviewer/composition tests after contract exists. Earlier parent directly verified old17launchtests all3 but that is not approval of changed source.
- Core completion means implemented backend+driver, independent source security/PM acceptance, exact-target authorized installation/current baseline/live qualification, complete capstone/all11gates/all7journeys, final independent PM acceptance. Components/fixtures/history cannot substitute. Optional work frozen; no added ecosystem integrations.
- Measured free space~5.66GB remains below16.1GB replayfloor. No cleanup or protected effects performed. Current source-only authorization excludes /Library/GRRR metadata/content, installation/accounting/reconcile/unstop, VM/replay, permanent admission/promotion, main/production or push. Batch a concrete future live decision package only after source genuinely ready.

### proof
- [x] Preserved previous public source WIP before restarting conclusively failed worker.
- [x] No mandatory criterion removed or old source/runtime grant silently transferred.
- [ ] AC #2-11: remaining implementation and reproduced evidence not complete.
- [ ] AC #12: complete independent security/PM acceptance not yet obtained.

## nd_contract
status: in_progress

### evidence
- Operator explicitly requested connecting PAIVOT, Agent Autoloop and Jeffrey's skills to continue GRRR. This authorizes a bounded source-verification coordination pilot, not new evaluator/promotion authority or completion of this story.
- PAIVOT remains the sole work selector and tracker. A fresh loop result reported the existing claimed GRRR-k3j7 worktree stalled; its public WIP is retained, not discarded by blind recovery. The root coordinator is active. The integration pilot may surface wait/stalled truthfully; it cannot invent ready stories or claims.
- Public Agent Autoloop source is pinned to c0ceda50206e58f19d384cd16510545e38294ff1, archive SHA2567c0608c417e6500334457d9922a2149aeca6fd8597004b448196a94262739cfc. Initial custom-profile failures are retained. Separate operator-authorized normal-user tests passed six selected worker checks and one real local HTTP/SQLite question/answer/resume journey, with no real model/provider requests.
- All48 synthetic timed command fixtures completed and outputs were verified. Autoloop capacity2 median1.623s for four jobs; direct parallel capacity2 median1.436s; three repetitions per arm. This is not AI coding throughput, a superiority finding, independent evaluator proof, or GRRR capstone evidence.
- /root/connect_paivot_autoloop_pilot owns only outputs/paivot-autoloop-pilot outside this source checkout, building a finite real host/kernel/worker lane for at most two allowed public source-verification commands. No fakeHub substitution or real AI adapters, secrets, service installation, delivery automation, tracker/Git mutation, or protected access is allowed. The pilot is not yet verified or installed.
- /root/review_backend_index_wip independently reviews exact schema2249d8b8a69baf6f88ba62934cfd9ba4fcf0f6cdaa12d400c3bae86e388001c8/indexfe90fcd9fc80841030ad81c9ebdd9c5d0c0c788815c1c6f30825696894d96976/tests15fff01697bd9ad0051ee64f5e476bb76cf59f22e3ffed3be65b0a120bcf796b. It is scoped source review, not PM acceptance of all12ACs.
- The29 index source tests passed parent rerun and retained runs on Python3.14/3.12/3.9. The explicit complete WIP suite now includes index coverage; a fresh combined143-test source verification is running, with no result claimed yet. Reviewer/store/launch/campaign/accounting completeness remain separate acceptance obligations.
- Jeffrey's catalog was checked; installed anti-ceremony and real-service-testing skills were read. Selection uses the catalog plus installed inventory, then relevant full skills, not bulk installation or a second runtime authority.
- Latest measured available space is above both documented floors. This removes a space-only blocker, not the requirements for exact-target protected execution authorization and current preflight.
- No /Library/GRRR access even metadata, protected installation/accounting/reconcile/unstop, VM/live replay, contract admission/promotion, main/production mutation, or push is authorized by this pilot. The operator's request for normal-user upstream tests does not expand this GRRR story's protected scope. Optional research expansions remain optional; no original acceptance criterion was removed.

### proof
- [x] Original failed trial attempts retained and separated from passing normal-user evidence.
- [x] Current core WIP preserved; no false delivery, acceptance, merge, or promotion claim.
- [ ] AC #2-11 complete implementation and integrated source verification remain unfinished.
- [ ] AC #12 complete independent security/PM acceptance remains pending.


## nd_contract
status: in_progress

### evidence
- Reviewed partial backend source WIP is committed on story/GRRR-k3j7 as 419c312a116476ff22486737883d4b19b4a2ddb4. The epic and main branches were not merged or pushed. All12 original story criteria remain required; this is neither delivery nor acceptance.
- Exact independently scoped review reports and parent-run evidence are committed at docs/evidence/source-backend/current-source-20261104/. Parent combined143 tests passed on Python3.14/3.12/3.9, plus direct required-suite entrypoint on3.14. These are public source fixtures, not installation/UID/ACL/VM/authority proofs. Earlier failed attempts remain in private WIP evidence.
- A finite, normal-user PAIVOT/Autoloop/source-test connector exists at outputs/paivot-autoloop-pilot/ outside the GRRR checkout. It captures the actual loop decision and current owned claim; runs exactly22 contract and29 index source tests through the actual pinned Autoloop hub/kernel/worker; retains outputs and skills digests; observed both fixed-job processes overlapping; and stops the hub. PAIVOT returned stalled; no new story was selected/claimed. No AI adapter, real provider credential, permanent service, production, protected installation, or promotion was used.
- Independent finite-pilot reproduction review SHA256 72dd8227168f36903ddd01b2abed95dead8aac468b99e0029fc2ffd14ca91355 approves only the single reproduced run. Broader reuse is blocked until the source-guard dependency is digest-pinned; normal-user access is not OS-enforced read-only. The concurrency intervals cover full job processes, not solely the guarded commands or AI speedup.
- /root/fix_pilot_review is addressing this exact digest/label finding; independent re-review remains required. /root/installation_record_codec owns only a data-only InstallationV2 descriptor codec/test; it grants no authority and cannot open protected files. /root/review_authority_cycle is independently checking the architect's proposal and exact full-byte installation/registry/authorization cycle. Those tasks are ongoing; no success is claimed yet.
- Architect's uncommitted authority proposal has SHA256 f4d9b2bf86a9c1d6b60d03d5a48232bf43d9bade991dd9cd8375644a92e73734 and explicitly marks newly proposed records, missing independently validated import provenance, and unresolved cyclic hashes. No existing hash semantics are silently altered and the proposal is not approved authority.
- Existing user decision keeps optional research ecosystem additions optional; the separately requested verification lane does not replace PAIVOT selection, trusted evaluator, ledger, required Jev comparison, or any original gate. No /Library/GRRR access including metadata, protected installation/accounting/reconcile/unstop, VM/live replay, permanent contract admission/promotion, main/production mutation, or push was authorized by the pilot.

### proof
- [x] WIP source/review/test evidence was committed without closing or merging the story.
- [x] One finite real Autoloop verification connection was independently reproduced within the stated source-only limits.
- [ ] Pilot guard digest fix and fresh scoped review.
- [ ] AC #2-11 full backend implementation and integrated source/installed verification remain incomplete.
- [ ] AC #12 complete independent security and PM acceptance remains pending.


## nd_contract
status: delivered

## Implementation Evidence

PROOF:

### CI/Test Results
Commands run:
- PYTHONPATH=research:tests /opt/homebrew/bin/python3.14 tests/unit_capstone_backend_suite.py
- PYTHONPATH=research:tests /opt/homebrew/bin/python3.12 tests/unit_capstone_backend_suite.py
- PYTHONPATH=research:tests /usr/bin/python3 tests/unit_capstone_backend_suite.py
- PYTHONPATH=research:tests /opt/homebrew/bin/python3.14 -m unittest discover -s tests -p 'unit_capstone*.py'
Summary: PASS source257 tests on EACH of Python3.14.3,3.12.9,3.9.6; failures0/errors0/skipped0, each exit0. Campaign reducer, CampaignManifestV2 derivation, real-Ledger append, two-leaf campaign, fence and both stop-outcome paths covered. All 11 gate phases and all seven capstone journeys NOT-RUN; no installed topology, VM replay, admission, promotion, production or q3hp claim. Producing SHA8c3e607cf4611da88d3bd3200593cc3e150e1268.

- Commands run:
  - PYTHONPATH=research:tests /opt/homebrew/bin/python3.14 tests/unit_capstone_backend_suite.py
  - PYTHONPATH=research:tests /opt/homebrew/bin/python3.12 tests/unit_capstone_backend_suite.py
  - PYTHONPATH=research:tests /usr/bin/python3 tests/unit_capstone_backend_suite.py
  - PYTHONPATH=research:tests /opt/homebrew/bin/python3.14 -m unittest discover -s tests -p 'unit_capstone*.py'
- Summary: source-only delivery. 257 tests per interpreter, 0 failures/errors/skips. No external CI claimed. Gate phases, capstone journeys, installation, admission and promotion remain not-run and are not claimed.

### Commit
- Branch: story/GRRR-k3j7
- SHA: 8c3e607cf4611da88d3bd3200593cc3e150e1268
- Worktree clean at delivery time; no merge, no push, no protected access.

### Acceptance Criteria
- [x] AC1: accepted design and independent review bound; implementation conforms at source.
- [x] AC2: InstallationV2 open-only topology, 44 source tests.
- [x] AC3: backend-v2 schema, index, reducer, replay equality and stop-pending transitions.
- [x] AC4: issuance idempotence, intent continuity and reopen behaviour.
- [x] AC5: two-leaf JIT composition with distinct Plans and verifier-injected owner/gate proof.
- [x] AC6: ReviewV2 store/service/RPCs with peer identity, idempotency and crash-conservative replay.
- [x] AC7: AF_UNIX SCM_RIGHTS gate/broker with real multiprocess and wrong-inode tests.
- [x] AC8: stop commits stop-pending before cancellation; verified outcome stopped, else recovery-required.
- [x] AC9: v4 unchanged and read-only; operational v5 accounting implemented and tested.
- [x] AC10: two-leaf campaign executes through the real Ledger with truthful manifest links.
- [x] AC11: 257 regressions reproducible on Python 3.14, 3.12 and 3.9 with zero skips.
- [ ] AC12: independent review and PM acceptance pending for this delivery.

### Independent Review and Scope
- Pending: one fresh-context read-only review of the campaign reducer, the Ledger version change, the journal version check and the integration tests. No merge, push, promotion, admission, installation or /Library/GRRR access is authorized by this delivery.

### proof
- [x] AC1: accepted design and independent review bound; implementation conforms at source.
- [x] AC2: InstallationV2 open-only topology, 44 source tests.
- [x] AC3: backend-v2 schema, index, reducer, replay equality and stop-pending transitions.
- [x] AC4: issuance idempotence, intent continuity and reopen behaviour.
- [x] AC5: two-leaf JIT composition with distinct Plans and verifier-injected owner/gate proof.
- [x] AC6: ReviewV2 store/service/RPCs with peer identity, idempotency and crash-conservative replay.
- [x] AC7: AF_UNIX SCM_RIGHTS gate/broker with real multiprocess and wrong-inode tests.
- [x] AC8: stop commits stop-pending before cancellation; verified outcome stopped, else recovery-required.
- [x] AC9: v4 unchanged and read-only; operational v5 accounting implemented and tested.
- [x] AC10: two-leaf campaign executes through the real Ledger with truthful manifest links.
- [x] AC11: 257 regressions reproducible on Python 3.14, 3.12 and 3.9 with zero skips.
- [ ] AC12: independent review and PM acceptance pending for this delivery.


## History
- 2026-11-04T21:39:55Z dep_added: blocks GRRR-q3hp
- 2026-11-04T21:39:55Z status: open -> in_progress
- 2026-11-04T21:39:55Z auto-follows: linked to predecessor GRRR-yt6a
- 2026-11-04T21:39:56Z claimed by dev-GRRR-k3j7
- 2026-11-05T04:22:36Z status: in_progress -> open
- 2026-11-05T04:22:37Z released by speed
- 2026-11-05T04:23:00Z status: open -> in_progress
- 2026-11-05T04:23:00Z auto-follows: linked to predecessor GRRR-wcwy
- 2026-11-05T04:23:00Z claimed by dev-GRRR-k3j7
- 2026-11-05T08:18:47Z status: in_progress -> open
- 2026-11-05T08:18:47Z released by speed
- 2026-11-05T12:44:36Z status: open -> in_progress
- 2026-11-05T12:44:36Z auto-follows: linked to predecessor GRRR-ev2w
- 2026-11-05T12:44:36Z claimed by dev-GRRR-k3j7
- 2026-11-05T15:00:01Z status: in_progress -> in_progress
- 2026-11-05T15:00:01Z auto-follows: linked to predecessor GRRR-888u
- 2026-11-05T20:25:47Z status: in_progress -> closed
- 2026-11-05T20:25:47Z dep_removed: no_longer_blocks GRRR-q3hp
- 2026-11-11T21:15:17Z dep_added: blocks GRRR-2hib
- 2026-11-11T21:17:48Z dep_removed: no_longer_blocks GRRR-2hib

## Links
- Parent: [[GRRR-2t3h]]
- Follows: [[GRRR-yt6a]], [[GRRR-wcwy]], [[GRRR-ev2w]], [[GRRR-888u]]
- Led to: [[GRRR-q3hp]], [[GRRR-hbc6]], [[GRRR-n49g]], [[GRRR-734u]]

## Comments
