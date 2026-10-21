# Conservative accounting migration design — PROPOSAL ONLY

Basis: `story/GRRR-gu87` commit `6f47e89` plus this follow-up diff. This file
grants no migration, installation, stop release, reservation, settlement,
QEMU/guest execution, or runtime authority. The protected conservative source
must remain byte-for-byte unchanged and `state.stopped` must remain `1`.

The design goal is to permit a fresh candidate store for independent review,
never to transform the current `/Library/GRRR/accounting` store in place.

## 1. Source evidence gate

Before a private candidate build, one independent collector must:

1. Hash and stat `active.json`, `budget.sqlite`, and `receipt.json`; recheck the
   exact active/database/receipt digests in `INPUT-READBACK.json`, owner, mode,
   link count, device, and inode before and after collection.
2. Open SQLite only with `mode=ro&immutable=1` plus `PRAGMA query_only=ON`;
   require `integrity_check=ok`, one stopped state row, zero runtime
   reservations, exactly 259 artifact rows, and exactly 110 legacy event rows.
3. Rehash every artifact body and every event body; compare paths, digests,
   evidence keys, and canonical bodies against the installed reconciliation
   report and its source pointers.
4. Collect the original evaluator receipts and invocation boundaries behind
   every reservation, observation, denied event, and stop event. Preserve
   conflicts and duplicates rather than selecting a convenient row.
5. Obtain explicit stage, currency, paid-service, preparation, selector,
   execution, replay, and review records with start/end intervals. Missing or
   overlapping evidence is an unresolved hold, never zero and never omitted.

The collector emits a signed/immutable source manifest but performs no writes
to the protected source. Any mismatch aborts before candidate construction.

## 2. Exact mapping and non-promotion rules

| Source | Candidate target | Rule |
|---|---|---|
| Active `campaign` | `migration_source.campaign` and `store_identity.campaign` | Preserve exactly as ancestry. |
| Active `store_id` | `migration_source.source_store_id` | Preserve as source identity; it is not reused as the new runtime identity. |
| All 259 `artifacts` rows | `legacy_artifacts` | Same path, SHA-256, bytes, and ordering manifest; no replacement or recompression. |
| All 110 `legacy_events` rows | `legacy_events` | Same evidence key and canonical bytes; duplicates/conflicts stay distinct. |
| Source `state(1,1)` | `state(1,1)` and `migration_controls` | Candidate remains stopped; no source trigger or stop history is cleared. |
| Empty runtime `reservations` | empty `reservations` | No legacy event is promoted to a reservation. |
| Historical maxima, observations, denials, and stops | unresolved legacy evidence plus full admission controls | They are not actuals, settlements, releases, or zero charges. |
| POC/milestone encumbrance | `migration_controls` | Full `$50/$150`, 21600/86400 execution seconds, and 3600/10800 review seconds remain blocked; POC is included in milestone. |
| Receipt/proposal metadata | `legacy_artifacts`/`migration_source` | Exact bytes and hashes retained; not treated as trusted usage metering. |

A legacy event may become a runtime reservation or settlement only in a later,
separately reviewed mapping that proves reservation identity, request key,
principal, stage, finite maximum, overlap interval, and bound trusted meter
receipt. No such proof exists here. An evidence digest is not a reservation ID;
a run ID is not a reservation ID. Absence of money/review data is unknown cost.
Reported zero is not a settlement, and a missing/lost receipt retains the full
maximum. Fractional observations remain decimal evidence, never rounded usage.

## 3. Candidate schema and identity binding

A private, non-production candidate may add these exact projections to the
runtime tables already required by `persistent_budget.validate_store`:

- runtime: `reservations`, `metering`, `overhead`, `state`;
- identity: `store_identity(campaign, store_id, prior_history_receipt)`;
- ancestry: `migration_source(source_active_sha256, source_database_sha256,
  source_receipt_sha256, source_store_id, source_device, source_inode,
  artifact_count, legacy_event_count, reconciliation_report_sha256)`;
- preservation: `legacy_artifacts(path, sha256, body)` and
  `legacy_events(evidence_key, body)`;
- controls: one row recording `stopped=1`, `unresolved_history=1`,
  `release_authorized=0`, and the full POC/milestone encumbrance.

The candidate uses a deterministic new store ID derived from the exact source
campaign, source store ID, source database hash, and reviewed migration-plan
digest. Its `prior_history_receipt` is a digest over the complete ancestry and
preservation manifest. The source store ID is retained only as ancestry.

The eventual active binding is version 1 with exactly the reviewed campaign,
new candidate store ID, candidate directory, prior-history receipt, three
registered profiles, and the installed candidate database device/inode. The
candidate directory and database are bound by hash, device, inode, owner
UID 320, private modes, single link, and no symlink/ACL. Runtime tables begin
empty and stopped; the preserved legacy tables are not consulted as charge
authority. `validate_store` must be strengthened only if discrepancy classes
are discovered, never weakened to accept this conservative binding.

## 4. Build, reproduction, installation, and rollback gates

Mandatory sequence:

1. Build a fresh private candidate from the frozen source manifest; never copy
   into or overwrite `/Library/GRRR/accounting`.
2. Re-open the candidate read-only and verify schema, integrity, all 259/110
   preserved rows, zero reservations, stopped state, identity, device, inode,
   modes, links, ACLs, and database hash.
3. Independently reproduce the candidate from the same source manifest and
   compare the complete canonical table projections and receipts; differences
   block installation.
4. Obtain separate operator authorization naming the candidate database hash,
   active binding hash, directory, device, inode, and migration receipt.
5. Install only a newly created candidate namespace and immutable binding.
   Refuse if any destination exists; never replace, rewrite, delete, or roll
   back into the current conservative store.
6. Independently review the installed accounting adapter and launcher behavior
   before any runtime adapter claim.

Rollback authority applies only to a newly created candidate namespace or a
candidate active binding. The current conservative store is never a rollback
target or mutable recovery destination. Any unknown build, reproduction, hash,
identity, permission, concurrency, or installation outcome aborts and retains
diagnostics; there is no automatic retry, fresh allowance, stop release, or
missing-cost-to-zero conversion.

## 5. Remaining blockers

This plan is intentionally incomplete for execution: original event identity,
intervals, stage mapping, money-service records, trusted meter receipts,
review overlap, historical campaign stop state, independent candidate
reproduction, installation authorization, and runtime adapter review remain
unresolved. The launcher may only fail closed with `RecoveryRequired`; this
does not make the conservative binding compatible or authorize a migration.
