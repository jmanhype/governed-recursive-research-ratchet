# Stop-only recovery successor (GRRR-d8ji)

**Protected stop-only install/verify and controlled refusal proof completed on
2026-10-25**, after independent exact-byte review and separate operator
authorizations. The installed implementation is commit
`65bb7945299851c078f5b48e9083d3aee13a7c4a`. This is not reconciliation,
registration authorization, replay approval, a dispatch lease, launch, admission,
promotion, merge or production authority. Developer tests had no protected effects;
the separately authorized parent performed the protected integration. This
document records that completed action, not permission to repeat it. Delivery and
independent PM acceptance are separate workflow gates.

Current recorded result: v3 active SHA256
`9c5194dd12ff7601917fcccc293c459db09a41da8bad9fa9983cbef618d453f8`,
recovery receipt SHA256
`6d3d5b092c0ee8273a657c83823d8465b215f2b1b66ec627dfde2d96b21fe587`,
database SHA256
`9c6ff2561a364ed982cd5477dd4b200c995da6910c9a17aa3d3c411a962d64f3`,
original DB inode `682589447`, state `1|0` (id=1, stopped=0), reservations=11,
metering=8, overhead=0, pending=3. Unknowns remain unresolved, spendable=null,
allowed mutations=[], execution_authorized=false. Duplicate install refused
(exit1, `partial/unknown registration state`); the UID320 controlled probe refused
all 12 API/connection/cursor/BLOB mutation surfaces without changing protected
bytes or inventory. See [evidence report](evidence/accounting-recovery/REPORT.md)
for exact external raw artifacts, hashes and historical limitations.

## Conservative state machine

| Source/event | Result | Runtime writes |
|---|---|---|
| v1 legacy | existing legacy rules unchanged | existing rules only |
| valid registered v2, no separate authorization | unchanged frozen/stopped | none |
| exact v2 + approved plan/review + separate authorization + quiescent locks | v3, stopped 1→0, same DB inode and history | **none** |
| any incomplete attempt, unknown version, stale source/identity/receipt | RecoveryRequired/denial; never retry effect | none |
| repeat install, including already successful install | refusal, not another receipt | none |

This is intentionally stop-only recovery, not spendability reconciliation.
`historical_unknowns=unresolved`, `spendable=null` and every pending maximum remain
unchanged. A third-version binding is always opened read-only. `reserve`, `meter`,
`settle`, `disclose_overhead`, `halt`, inherited/base entrypoints, SQL writes,
PRAGMA/DDL/ATTACH, cursor scripts and writable BLOBs are denied. Zero reservations
and repeated reservation keys are not exceptions. All profiles share the original
POC/milestone store and ceilings. GRRR-z3w9 still needs separate capacity/identity/
review/replay approvals and, if spendability is needed, a separately reviewed
reconciliation successor. This package grants no reconciliation authority.

## Exact APIs and records

`accounting_recovery.sources() -> dict` hashes its two-file installer closure.
`bootstrap() -> None` verifies the fixed root-only isolated interpreter/installation.
`snapshot() -> dict` invokes the unchanged v2 registration verifier and captures
canonical active/registration/prior hex bytes, active/database/directory metadata
and full stopped inventory. `approval(plan, review, authorization) -> None`
checks exact schemas and hashes. `install(plan_path, review_path,
authorization_path, expected_authorization_sha256) -> dict` makes one attempt.
`verify() -> dict` returns binding/receipt only after complete ancestry validation.
`unchanged(before, after) -> None` allows only stopped and physical DB hash changes.
`snapshot_with_attempt(before) -> dict` checks the staged attempt's original source.

Canonical means ASCII JSON with sorted keys, compact separators, no NaN, duplicate
keys, missing/extra fields or trailing whitespace. Version integers reject bools.
`approval()` is the normative exact schema for plan/review/authorization; these are
embedded byte-for-byte canonically in the intent. The baseline is mandatory, not
a discovery hint. The action is exactly `release-stop-retain-unknowns-read-only`.
Independent review approves the exact source hashes and baseline hash, action,
ceilings, empty mutation list and unresolved/null uncertainty. The plan binds that
review; the authorization binds exact plan, review, baseline, source hashes and
action with principal `operator-via-exclusive-root-parent`, exclusive_parent=true,
execution_authorized=false. The CLI additionally requires the authorization hash.
These root-owned records are parent attestations, **not cryptographic signatures**.
The parent must authenticate the operator and independent reviewer out of band;
a registration approval or a fabricated review-shaped JSON is not authorization.

The v3 binding has exactly the original v2 fields with version=3 plus
`recovery_sha256`. Campaign/store/directory/device/inode/prior_history_receipt,
profiles and registration_sha256 are identical. No database/schema is created.
The only SQL mutation is `UPDATE state SET stopped=0 WHERE id=1 AND stopped=1`.
Every historical row, schema, hold, usage, settlement and overhead value must be
identical, including three pending holds on the real source baseline. Inventory
continues to validate resource vectors, orphan meters and cumulative ceilings.
Registration's inventory helper accepts explicit expected_stop=0 only for this
successor; its default, baseline, install, receipt validator and verify still
require stopped=1 and exact original database bytes.

## Publication, locks and crash behavior

Parent excludes ALL other privileged writers and terminates/quiesces old evaluator
handles (including native BLOB handles). No automatic restart is allowed. Lock
order remains accounting launch.lock → corpus v2-launch.lock → SQLite
BEGIN EXCLUSIVE with timeout=0. Process inventory rejects service UIDs and QEMU.
The exclusive SQLite lock rejects active readers/writers; parent exclusion remains
mandatory after SQLite commit releases that lock. Advisory locks alone cannot
exclude arbitrary privileged processes. Any lost exclusion invalidates approval.

1. All authority, protected metadata/ACL, v2 baseline and lock checks precede writes.
2. Create recovery directory once. O_EXCL/no-follow writes canonical `intent.json`
   (`prepared-not-success`) and exact `prior-active.json`; fsync both files and
   recovery/base directories. Existing/partial directory prevents retry.
3. Recheck source and ancestry. Commit the one stop transition with synchronous=FULL.
4. Validate full after inventory. Append `receipt.json` with outcome
   `database-committed-publication-pending`, intent/prior/registration hashes, full
   result inventory, empty mutation list and execution_authorized=false.
5. Write/fsync next-active, recheck original active identity, then atomic replace
   active.json. Fsync recovery/base. Append/fsync `complete.json` binding exact
   receipt and successor hashes with outcome `published-durable`. Freeze directory
   mode 0555, fsync directories, perform full read-only postflight.

Every receipt uses exclusive creation: no overwrites. Receipt → intent → plan →
review/authorization/baseline preserves complete ancestry, with original immutable
registration files retained. Verification requires the exact artifact set.
Before commit failure leaves original DB and partial attempt; after commit failure
can leave stopped=0 but unusable v2 or v3. Exceptions append `uncertain.json` when
possible, never success. A kill/power loss can leave no uncertainty receipt; missing
completion, wrong mode or partial artifacts are independently denied. Even a late
fsync/postflight error adds uncertainty and prevents runtime opening. Failure to
write uncertainty does not license retry. Read-only verification is repeatable;
installation is not idempotently replayable. Review a **new** recovery plan for
every uncertain outcome; never delete artifacts to reuse an authorization.

Errors are fail-closed ValueError/OSError/SQLite errors; runtime wraps invalid
binding/ancestry as RecoveryRequired. No repair, allowance reset or row rewriting.

## Parent command grammar and mandatory live gate (completed for stop-only action)

For any future action, new exact authorization is required. The reviewed staging
and command contract used for the completed action is retained below; it is not a
retry instruction. After exact authorization for staging, install the reviewed recovery and
registration source files root-owned 0444 under `/Library/GRRR/bootstrap/recovery/`.
The entire import closure and ancestors must be root controlled and ACL-free.
Stage separate canonical plan/review/authorization records there, also 0444.
The pinned Python path/hash is the existing registration contract's Python 3.9.6.

```text
PINNED_PYTHON -I -S -B /Library/GRRR/bootstrap/recovery/accounting_recovery.py install PLAN REVIEW AUTHORIZATION AUTHORIZATION_SHA256
PINNED_PYTHON -I -S -B /Library/GRRR/bootstrap/recovery/accounting_recovery.py verify
```

These commands are deliverable grammar, **not permission to execute**. The parent
live test is install followed by verify under the documented locks/quiescence.
Before it: independently compare source hashes against approved review, authenticate
exact operator action, inspect fixed binding/receipt/inventory hashes, owners/modes/
ACLs/links and DB/directory device+inode; reject changed state. After it: verify
complete receipt ancestry, unchanged source identities/history/three pending holds,
unresolved/null uncertainty and exact stop disposition; exercise permitted success
plus stale/duplicate authorization and write refusals in separately authorized
controlled state. No mocks may substitute. Keep raw command outputs and hashes.
No actual replay, guest or production mutation belongs to this test. Missing live
proof would mean **not fully recovered**, irrespective of no-guest unit results.
The stop-only success and separately authorized refusal gates are now recorded;
no spendability reconciliation or actual replay was performed.

## Developer verification

Both `/usr/bin/python3` and `/opt/homebrew/bin/python3` must run unittest discovery
for `unit_replay_accounting_recovery.py`, `unit_replay_accounting_registration.py`,
and `unit_*.py`, plus compilation, explicit-path pvg verify and diff checks.
Fixtures translate ownership/bootstrap boundaries only; actual SQLite mutations,
locks, canonical records and file publication execute locally. Fault injection is
unit evidence, not live integration. Fixed disk floors remain unchanged; setup
errors/unexecuted classes block clean delivery. Independent review of exact diff
and final hashes is still mandatory; this document is not that review.
