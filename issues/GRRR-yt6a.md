---
id: GRRR-yt6a
title: "Source-only durable capstone grant and operation journal"
status: open
priority: 0
type: task
labels: [milestone-1, source-only, security-boundary]
parent: GRRR-2t3h
created_at: 2026-11-04T18:42:49Z
created_by: speed
updated_at: 2026-11-04T18:42:49Z
content_hash: "sha256:cbe2a071f2733080d0eb7c8255b7af51f6e1250aca6f4f3f0dd7f4bc06004d30"
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


## History


## Links
- Parent: [[GRRR-2t3h]]

## Comments
