---
id: GRRR-k3j7
title: "Executable evaluator backend: finite JIT campaign, accounting and isolated launch bridge"
status: in_progress
priority: 0
type: feature
labels: [milestone-1, integration, security, source-only]
parent: GRRR-2t3h
created_at: 2026-11-04T21:39:45Z
created_by: speed
updated_at: 2026-11-04T21:41:26Z
content_hash: "sha256:f04c696d72ce2fbddacffd0b9be3db1bfdd67674b9c0ce239a62e5a56b2a12c7"
blocks: [GRRR-q3hp]
assignee: dev-GRRR-k3j7
follows: [GRRR-yt6a]
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

## History
- 2026-11-04T21:39:55Z dep_added: blocks GRRR-q3hp
- 2026-11-04T21:39:55Z status: open -> in_progress
- 2026-11-04T21:39:55Z auto-follows: linked to predecessor GRRR-yt6a
- 2026-11-04T21:39:56Z claimed by dev-GRRR-k3j7

## Links
- Parent: [[GRRR-2t3h]]
- Blocks: [[GRRR-q3hp]]
- Follows: [[GRRR-yt6a]]

## Comments
