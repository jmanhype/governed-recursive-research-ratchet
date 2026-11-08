---
id: GRRR-hbc6
title: "Recovery: reviewed v4 accounting unhalt planner"
status: in_progress
priority: 2
type: task
labels: [milestone-1, security, accounting]
parent: GRRR-2t3h
created_at: 2026-11-08T15:08:46Z
created_by: speed
updated_at: 2026-11-08T17:25:08Z
content_hash: "sha256:fab63b34e0fa94df87c5c74ac4145a41a24525dfda5551d29172d12a53d8b2bc"
assignee: dev-GRRR-hbc6
follows: [GRRR-q3hp]
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
## nd_contract
status: in_progress

### evidence
- Re-read live epic/worktree/tracker state; hbc6 is the sole in-progress story. Root epic HEAD 6729cc1; story source fix 09ef310. No merge or push.
- r8 rejection preserved in docs/reviews/RECOVERY-V4-REVIEW-r8-rejected-5a1f3532.md (SHA256 5a1f35323752910b91bc4d4f1fafce4efe755025a7ca45b8877d71c762c846cc).
- F1 direct probe fix: table_xinfo includes generated columns; qualified LIMIT 0 probe replaces SQL-tail parsing. Source SHA256 79bce91b4a5054bc2e59e05e9d3e55f924715f2ee44f34a61cc716b7a72c79d7. Five added regression methods; focused fixture suite 32 tests passed.
- Actual required backend suite: /opt/homebrew/bin/python3.14, /opt/homebrew/bin/python3.12, /usr/bin/python3 -B tests/unit_capstone_backend_suite.py: each 307 tests, zero failures/errors/skips. Raw logs committed under docs/evidence/accounting-recovery-v4/r9/. Supplemental discovery: 300 tests each on the same interpreters.
- Existing rev8 root-staged closure archived under /Library/GRRR/bootstrap/recovery-v4-history/rev8-4db1623-f01aa240. r9 staging emitted staged-not-installed; protected accounting baseline still stopped=1. plan SHA256 4603b443783e8bfc91f6a1c1c408f54cd8f3f073aaf35f14af9278d01d8f0953; review template 1bcb3351e435ff476c35e5df713b6facd519a9fa96d0670db9f2df13388ea2dc; authorization 5d1deb5fe0c26e378233c0a1fa1c1104fa60ce8aaee38673b2fd4efa9f6e026e. These templates are not independent approval.
- First staging attempt was refused by macOS Documents privacy before staging mutations. Retried from exact hash-verified temporary source copies without weakening permissions; success log retained.
- Routing: security implementation escalation to Astra; CoS native dispatch unavailable (connection failed), independent review dispatched fresh to exact zai-coding/glm-5.3 route. Approval is pending, not assumed.
- bd prime ran; bd sync --from-main --no-push reports no beads database. This repo's live source of record remains pvg nd; no parallel tracker initialized.

### proof
- [x] F1 direct-probe fixture coverage and required source suite pass on three installed interpreters.
- [x] Exact r9 sources and plan/review/authorization staged with original rev8 evidence preserved.
- [ ] Independent review approves the exact r9 closure.
- [ ] Operator-authorized v4 stop release installed and standalone verification succeeds.
- [ ] Full story delivery and PM acceptance; no self-acceptance.

No reconciliation, replay, contract admission, promotion, production mutation, merge or push is authorized by this progress note.

## History
- 2026-11-08T15:08:54Z status: open -> in_progress
- 2026-11-08T15:08:54Z auto-follows: linked to predecessor GRRR-q3hp
- 2026-11-08T15:08:54Z claimed by dev-GRRR-hbc6

## Links
- Parent: [[GRRR-2t3h]]
- Follows: [[GRRR-q3hp]]

## Comments
