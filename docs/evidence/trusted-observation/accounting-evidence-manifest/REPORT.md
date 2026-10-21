# Accounting evidence manifest — BLOCKED

Schema version: **1**. Decision: **blocked-ambiguous-history**.

This is a private, metadata-only readback of the stopped conservative store.
It contains no artifact bodies or raw logs. It authorizes no migration,
settlement, hold release, stop release, reservation, dispatch, or guest
execution. An available source pointer is **not** a trusted meter receipt.

## Source readback

| Source | SHA-256 | Readback |
|---|---|---|
| `/Library/GRRR/accounting/active.json` | `cc45b70fed84bae583959379559e8fc8336a0da3b4bca1750fc20c2848619f1b` | unchanged |
| `/Library/GRRR/accounting/budget.sqlite` | `9fe4000c0c45b83cc818c29640e561167c34bd663abc26267e2a1b009f878234` | unchanged |
| `/Library/GRRR/accounting/receipt.json` | `9f64395bec815a6bb2281d3b5d96d2356899138b1929b0a9881c16483c486dde` | unchanged |
| Prior installed reconciliation report | `2bd034edfc99d433ea9bc01d8fb6b1afd7715a18dea975fc20188459c747359e` | matched |

The database was opened through `O_NOFOLLOW`, checked as a regular file, and
queried with SQLite `mode=ro&immutable=1` plus `PRAGMA query_only=ON`.
Integrity is `ok`; state is `[[1, 1]]`; reservations are zero. The bound
database metadata is device `16777229`, inode `681781547`, root:wheel,
mode `0444`, and one hard link.

## Inventory

- Artifacts: **259/259**; every stored hash matches its body hash and byte count.
- Events: **110/110**; every body was hashed and matched its prior event key/source record.
- Event kinds: 48 reserved, 40 offline-observation, 8 observation, 6 denied,
  4 stop-fenced, 4 stop-outcome.
- Event source references: **322** across **46** distinct artifacts.
- Prior-report key mismatches: **0**. Prior-report source mismatches: **0**.

Every event explicitly classifies original reservation mapping, principal,
request key, stage, currency, paid service, start/end/overlap intervals,
trusted meter receipt, settlement status/trusted settlement receipt, and stop
scope. Missing values remain `null`; none are inferred or replaced by zero.
The full counts are in `MANIFEST.json`.

The unresolved-history result is not changed by successful collection. In
particular, principal, request key, stage, currency, start/end/overlap
intervals, trusted meter receipts, and trusted settlement receipts are missing
for all 110 events. Historical campaign stop remains unknown.
