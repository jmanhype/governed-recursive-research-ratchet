# Persistent accounting reconciliation — BLOCKED

This is a review-only inventory, not a migration approval or fresh allowance.
`scripts/review-accounting-reconciliation` reruns the accepted synthetic and
offline evidence verifiers, checks pinned manifests and every referenced artifact,
deduplicates overlapping ledger snapshots, and emits only bounded metadata.
No accounting database is created or changed. The existing installed host
inventory and guest v3 artifacts are unchanged.

Accepted sources are GRRR-0g4n's 12/12 attempt
`attempt-20261020T153803Z-4d13bc7b` and GRRR-90te's 6/6 attempt
`attempt-20261020T233115Z-6e1e938c`. Exact manifest and artifact hashes are in
`docs/evidence/trusted-observation/accounting-reconciliation/reconciliation.json`.
The visible exports contain five identified reservations, five observations,
four stop events, six unmapped legacy reservation events, and ten earlier
attempt manifests requiring reconciliation. These are NOT complete campaign totals.

Offline legacy reservation events lack reservation IDs. Their reported maxima
and cumulative reserved fields are retained as observations, not converted into
invented identities or settlement receipts. Initial refusal of that schema is
preserved. Synthetic observation timings likewise do not establish authoritative
cumulative review costs. Missing costs remain unknown, never zero.

## Required before a reviewed migration

1. Reconstruct the complete invocation inventory, including every failed attempt.
2. Reconcile cumulative review/replay duration, overlapping intervals, and POC
   carry-forward across synthetic, offline, and trusted-observation profiles.
3. Separate selector/preparation overhead without dropping it or double charging.
4. Map prior reservations and settle only with authenticated bounded receipts;
   unresolved holds retain their maximum charge and cannot be silently erased.
5. Determine campaign-level and run-level stop state; a stop acknowledgement is
   neither a stop reset nor candidate correctness.
6. Approve a complete migration receipt tied to exact evidence, campaign/store
   identity, all three profiles, and the already-existing persistent-store schema.
   Verify restart/concurrency and inode/device bindings before any launch.

The report always sets `execution_gate=blocked`, `migration_authorized=false`,
`unresolved_history=true`, `reset_allowance=false`; totals, remaining allowance,
and campaign stop state stay null. It cannot satisfy the full provisioner's
`approved-complete-accounting-migration` gate. There is deliberately no parent
accounting provisioning command yet. Do not install a blank store or infer
historical completeness from accepted integration checks.

New reconciliation code is an offline review utility, not part of the approved
runtime snapshot. All ten trusted-observation guest controls remain not-run.
No coverage claim for mandatory guest acceptance criteria is made.

## All-visible-attempt genesis proposal (2026-10-21)

`scripts/propose-accounting-genesis` additionally inventories all twelve attempt
manifests (two accepted, ten earlier/nonaccepted attempts), verifies their referenced bytes,
deduplicates event hashes across exports, preserves run/reservation identities and
source hashes, and extracts scalar duration fields with exact JSON pointers.
See `accounting-reconciliation/genesis-proposal.json`. Earlier failed attempt
timings remain evidence, not discarded because their tests failed.

Known reservation maxima remain individual unsettled holds. Missing identities
are not fabricated. Missing bounds for omitted effects cannot honestly yield a
finite historical upper bound: that field is null. Instead the proposed admission
baseline encumbers ALL POC ceilings ($50, 6 execution hours, 1 review hour) and
ALL cumulative milestone ceilings ($150, 24 execution hours, 3 review hours).
These overlapping admission holds are not additive historical charges or a reset;
both stages admit no work. Even this cannot prove prior usage did not exceed a
ceiling. POC carry-forward requires no fresh milestone allowance.

Nine manifests report nonzero exit; three report zero. Nonaccepted is not
synonymous with nonzero exit, and no zero exit implies complete cost accounting.

The mathematical evidence-only lower bound takes the maximum measured run
duration, not a sum of potentially overlapping executions/replays. Zero money and
review lower bounds are explicitly not observed $0/zero review or settlement.
Preparation, selector, replay, review and complete execution totals stay unknown.
Explicit run stops stay run-scoped; campaign stop state remains unknown.

The proposed logical genesis schema retains immutable legacy events, all source
references, reported scalar measurements, unresolved holds and stop events before
any future mapping into runtime reservations. `stopped=1` would represent a NEW
migration safety gate, not an invented historical campaign stop. No database,
approved migration receipt, or accounting provisioning command is produced.

This is complete for visible attempt exports, not a claim that every historical
invocation is recoverable. Missing effects, review history, intervals, stage
assignment, trusted receipts and campaign stop scope are genuinely absent from
the available export schema and require external reconstruction/approval.
