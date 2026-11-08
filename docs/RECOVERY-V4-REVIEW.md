REVIEW_RESULT: APPROVED

## Scope and exact bindings

- Worktree HEAD is `09ef310`; reviewed diff is `4db1623..09ef310`.
- Recomputed SHA256 for `/Library/GRRR/bootstrap/recovery-v4`:
  - `accounting_recovery_v4.py` `79bce91b4a5054bc2e59e05e9d3e55f924715f2ee44f34a61cc716b7a72c79d7`
  - `accounting_recovery_planner_v4.py` `3a2c6fa896ba59f864af215de3b55fe88bb83544a87fe6c425c43a506e9aa61c`
  - `records/plan.json` `4603b443783e8bfc91f6a1c1c408f54cd8f3f073aaf35f14af9278d01d8f0953`
  - `records/review.json` `1bcb3351e435ff476c35e5df713b6facd519a9fa96d0670db9f2df13388ea2dc`
  - `records/authorization.json` `5d1deb5fe0c26e378233c0a1fa1c1104fa60ce8aaee38673b2fd4efa9f6e026e`
- Each staged file is byte-identical (`cmp` exit 0) to its worktree counterpart in `research/` or `docs/evidence/accounting-recovery-v4/r9/`.
- Independently canonicalized and hashed the records: plan `4603b443783e8bfc91f6a1c1c408f54cd8f3f073aaf35f14af9278d01d8f0953`; review `1bcb3351e435ff476c35e5df713b6facd519a9fa96d0670db9f2df13388ea2dc`; authorization `5d1deb5fe0c26e378233c0a1fa1c1104fa60ce8aaee38673b2fd4efa9f6e026e`; embedded baseline `e2e9289a971b069437113843309565b6706142e3a205e18a23beea583d639c5d`. The plan's review reference, review/authorization baseline and source references, and authorization plan/review references all match those recomputations and the two staged source hashes.
- `packet-r9.md` SHA256 is `b4e0acaf83d5db71cb1b564994d86340d248db2dd9afe45ab7bd54e5eab8e852`.

## F1 rowid identity — CLOSED

The revised `inventory()` closes the r8 structural defect:

- It uses `PRAGMA table_xinfo`, so generated and hidden column names are visible even when the table is empty (`research/accounting_recovery_v4.py:150-159`).
- It fails closed when all SQLite rowid aliases are masked, and, after a successful direct probe, refuses if any of `rowid`, `_rowid_`, `oid`, or `_grrr_rowid` appears in that complete metadata-name set (`:157-159`, `:172-177`). Thus one unmasked probe alias cannot conceal masking of another alias, including generated VIRTUAL/STORED masks on empty tables.
- It probes a qualified identifier, `_grrr_probe.<probe>`, with `LIMIT 0`; success resolves independently of rows, while only the exact missing-column failure classifies the table as `WITHOUT ROWID` (`:160-171`). Unexpected `sqlite3.OperationalError` values re-raise; non-operational failures are not caught.
- It no longer parses a SQL tail. Genuine rowid tables capture `rowid AS _grrr_rowid, *` and check captured arity/type when nonempty (`:172-182`); genuine `WITHOUT ROWID` tables use `SELECT *` (`:172-174`).

The real-SQLite regressions cover the required boundaries: empty generated VIRTUAL and STORED masks for all four names (`tests/unit_capstone_recovery_v4.py:360-375`); trailing comment words versus an actual rowid-only change (`:377-403`); an empty genuine `WITHOUT ROWID` table with a split options comment, an empty quoted ordinary table, and later rowid capture (`:405-420`); unmasked generated columns with both storage kinds (`:422-432`); and an empty table masking all three native aliases (`:434-440`).

## Preserved controls

- **A/header — CLOSED.** Stable SQLite header fields are captured (`research/accounting_recovery_v4.py:112-118`), recorded (`:138-146`), and compared by `unchanged()` after the stop commit (`:246-256`). As in r8, the intentionally volatile file-change counter is not one of the compared fields.
- **F2 — CLOSED.** Restoration checks rowcount and reads `stopped=1` back (`:394-406`); restore failures become accumulated operator-recovery failures (`:409-424`).
- **F3/B — CLOSED.** Failure cleanup invalidates and syncs completion first (`:367-385`), resolves an unknown target only through the protected binding (`:386-391`), durably records incomplete state, and raises rather than returning success (`:411-424`). `apply_install()` rethrows the original failure after recovery (`:261-277`).
- **F4 — CLOSED.** Final mode precedes descriptor fsync in `publish()` (`:36-47`); publication and failure paths fsync directories after final chmod (`:349-363`, `:411-419`).
- **F5 — CLOSED.** `BEGIN IMMEDIATE` precedes the complete guarded-baseline comparison (`:303-312`).
- **F6 — CLOSED.** Approval requires exact canonical review and authorization construction plus their hashes and typed boolean flags (`:229-243`).
- **F7 — CLOSED.** The writer reacquires `BEGIN IMMEDIATE` from mutation through publication/verification (`:320-327`), and verification rejects WAL/journal sidecars (`:460-462`).
- **F8 — CLOSED.** A repeat with matching intent calls the same `verify()` inside the failure boundary and invalidates completion if verification fails (`:288-295`, `:261-277`).
- **C — CLOSED.** Both initial publication and repeat verification end in the standalone published-state predicate: `_publish()` returns `verify()` (`:353-364`), repeat `_install()` returns `verify()` (`:288-295`), and `verify()` enforces the same inventory/hash predicate (`:463-479`).

The production-code portion of `4db1623..09ef310` changes only `inventory()`; the remainder of that module controlling A and F2-F8, B, and C is unchanged. Added tests do not weaken those predicates.

## Operator driver

`docs/evidence/accounting-recovery-v4/r9/install-verify.py:9-22` requires root, isolated/no-site/no-bytecode execution, the reviewed system Python, one explicit action, and pins all five staged hashes. It checks the directory chain and exact staged regular files for root ownership, expected mode, and single link before import (`:23-33`), validates the exact records through `approval()` (`:34-37`), snapshots the target (`:38-41`), and only `--install` applies `apply_install()` after exact live-baseline equality; `--verify` calls the standalone verifier (`:42-46`). Both paths independently resnapshot and require unchanged history/inventory plus exact active bytes and metadata before accepting the result (`:47-53`).

## Operator invocation artifact

The prepared but not executed invocation wrapper is `/private/tmp/grrr-recovery-v4-r9-install.sh` SHA256 `e99671240988b6352a2de9a9852d68f0a4f14dcf6d7d705391c350d15491815f`; it pins the driver hash `fc5326471b92447cbc4eb70a0230ad9f6478cf74b55de3833a137e982a76dec1` and requires the caller-supplied SHA256 plus first-line approval verdict for `/private/tmp/grrr-review-r9.md` before root-staging either file (`/private/tmp/grrr-recovery-v4-r9-install.sh:3-14`). It proves wrong flags and the wrong interpreter refuse before protected access (`:15-26`), then invokes the reviewed system Python once for `--install` and again in a fresh process for `--verify` (`:27-29`).

The review hash must be computed from this final verdict file and supplied as the wrapper's sole argument; embedding that self-hash inside the file would change the hash. The operator invocation shape is therefore:

```bash
REVIEW_SHA256=$(/usr/bin/shasum -a 256 /private/tmp/grrr-review-r9.md | /usr/bin/awk '{print $1}')
/usr/bin/sudo /private/tmp/grrr-recovery-v4-r9-install.sh "$REVIEW_SHA256"
```

## Verification boundary

- Tests were **not rerun** by this reviewer; fixture execution would violate this read-only/no-write brief.
- Installer, live `--verify`, and runtime-accounting access were not run.
- The operator-reported source-only logs state 307 backend tests with 0 failures, 0 errors, and 0 skips on Python 3.14.3, 3.12.9, and 3.9.6. Those results are reported evidence only, not an independent rerun or a live capstone/installation claim.
