---
id: GRRR-hbc6
title: "Recovery: reviewed v4 accounting unhalt planner"
status: open
priority: 2
type: task
labels: [milestone-1, security, accounting]
parent: GRRR-2t3h
created_at: 2026-11-08T15:08:46Z
created_by: speed
updated_at: 2026-11-08T15:08:46Z
content_hash: "sha256:cf8920885c715e4100f9abcffe20517245749177e6e89d15af989ff2ab9afc78"
---

## Description
## Context
The 2026-11-08 replay attempt halted the live v4 accounting store (state stopped=1, reservation a549efbdca5743878052c0226c617c1f unsettled). The only existing recovery closure under `/Library/GRRR/bootstrap/recovery` is bound to the old v2 store `901acaff...` and cannot apply to the live v4 store `a142cabb...`.

## Scope
Build a reviewed, root-only **v4 recovery planner and installer** that releases the stop bit while retaining every historical row, hold and unknown. No reconciliation, no spendability claim, no admission, no promotion.

## Acceptance criteria
1. Planner runs read-only against the live v4 binding and emits an exact plan: active hex, metadata, full inventory (reservations, metering, overhead, state, store_identity) and source hashes. It performs no mutation.
2. The plan schema is fixed and review binds: action, baseline_sha256, sources, ceilings, allowed_mutations, historical_unknowns, spendable, execution_authorized.
3. An independent read-only review approves the exact plan bytes, and a separate authorization record binds plan and review hashes.
4. Installer is staged root-owned 0444 under `/Library/GRRR/bootstrap/recovery-v4`, runs `python -I -S -B` as root, refuses any noncanonical path, and performs exactly one `UPDATE state SET stopped=0 WHERE id=1 AND stopped=1` inside a single transaction, then verifies the inventory is unchanged except `stopped` and the database bytes.
5. Installer writes intent/receipt/complete records and refuses any partial or repeated recovery unless the exact outcome already exists.
6. Fixture tests cover: happy path sets stopped=0; stopped=0 already refuses; changed inventory refuses; changed plan/review/authorization refuses; partial recovery refuses; wrong interpreter/flags refuses in the live path only.
7. No live mutation occurs during tests. No reconciliation, admission, promotion, merge or push.

## Out of scope
Replay session reset (`replay_state`), fresh replay runtime provisioning, and any campaign execution.

## Acceptance Criteria


## Design


## Notes


## History


## Links
- Parent: [[GRRR-2t3h]]

## Comments
