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
updated_at: 2026-11-08T17:38:01Z
content_hash: "sha256:fd5b45cb29d18e703167aa5b933f369ae12547374adfbf1b5d3dacdd7fed4201"
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
## Implementation Evidence (DELIVERED)

PROOF:

### CI/Test Results

Commands run:
- `/opt/homebrew/bin/python3.14 -B tests/unit_capstone_backend_suite.py`
- `/opt/homebrew/bin/python3.12 -B tests/unit_capstone_backend_suite.py`
- `/usr/bin/python3 -B tests/unit_capstone_backend_suite.py`
- `PYTHONPATH=research:tests /opt/homebrew/bin/python3 -B -m unittest tests.unit_capstone_recovery_v4`
- `PYTHONPATH=research:tests /opt/homebrew/bin/python3 -B docs/evidence/accounting-recovery-v4/r9/pre-unhalted-fixture.py`
- Operator-authorized root invocation: `/bin/bash /private/tmp/grrr-recovery-v4-r9-install.sh fc4cd5f9df2ada6cfe2784e940759ee0dae066b96e30c258a57feec873c60457`, executed through macOS administrator authentication. Exact reviewed wrapper hash e99671240988b6352a2de9a9852d68f0a4f14dcf6d7d705391c350d15491815f.
- Root live commands inside that reviewed invocation: `/usr/bin/python3 -I -S -B /Library/GRRR/bootstrap/recovery-v4/operator-r9.py --install`, then the same command with `--verify` in a fresh process.
- Wrong-flags and wrong-interpreter negative driver invocations refused before protected path access; exact commands and raw expected assertion outputs retained in the invocation and refusal logs.
- `git diff --check`; record `cmp` and SHA256 checks against retained protected records; final worktree clean.

Summary: Required backend suite PASS: 307 tests on Python 3.14.3, 3.12.9 and 3.9.6 separately; each zero failures/errors/skips. Focused recovery fixture suite PASS: 32 tests. Additional fresh pre-unhalted fixture PASS: 1 test, exit 0, independently rerun by parent. Supplemental discovery PASS: 300 tests per interpreter. Live install PASS and fresh standalone verify PASS: published-durable.

Coverage: Acceptance-evidence mapping 7/7 (100% of listed story ACs below). Line/branch coverage was not measured; no line/branch percentage is claimed. These source results do not qualify the full GRRR capstone.

Commit SHA: d3e74cbcc9727dab29b9144639d03cc1a7f7adcd on story/GRRR-hbc6. Source fix tested and independently reviewed at 09ef310b7b5eb1df021ac6c56b8251cf68ff625b; approval artifact committed at 302d083. No production source changed after independent review; final commit contains retained operation evidence and the supplemental fixture only.

### Independent Review

- Fresh, separate reviewer /root/hbc6_review_r9 (zai-coding/glm-5.3) wrote REVIEW_RESULT: APPROVED; parent read it and independently recomputed the hash: fc4cd5f9df2ada6cfe2784e940759ee0dae066b96e30c258a57feec873c60457.
- Reviewer closed F1 structurally, verified all five staged hashes and exact canonical record bindings, and confirmed prior r8-closed controls remained unchanged. Reviewer did not rerun tests, run the installer, or inspect runtime accounting.
- Implementation escalation was a different Astra agent. CoS dispatch was unavailable; no secrets or unrelated files were supplied to workers.

### Live Result and Evidence

- Source module SHA256 79bce91b4a5054bc2e59e05e9d3e55f924715f2ee44f34a61cc716b7a72c79d7; planner 3a2c6fa896ba59f864af215de3b55fe88bb83544a87fe6c425c43a506e9aa61c.
- Plan SHA256 4603b443783e8bfc91f6a1c1c408f54cd8f3f073aaf35f14af9278d01d8f0953; review template 1bcb3351e435ff476c35e5df713b6facd519a9fa96d0670db9f2df13388ea2dc; operator authorization 5d1deb5fe0c26e378233c0a1fa1c1104fa60ce8aaee38673b2fd4efa9f6e026e.
- Observed accounting stopped transition 1 -> 0 only. Active binding bytes and metadata, database inode/device, stable header fields, schema, historical rows, holds and unknowns passed exact preservation checks in both install and a separate fresh verification process.
- historical_unknowns=unresolved; spendable=unknown. This is not reconciliation or a spendability claim.
- Root-owned 0555 recovery directory, four root-owned 0444 records. Receipt SHA256 8b7958e5be76f6b35c4bfafc1f17a2926badfdd813addbefd5d683e376e8eeeb; completion ea5dae2b353a1e7c0747f92b5bdb0b907a92f3b0939588ea63046a70403407af. Local copies compare byte-for-byte.
- Raw install/fresh-verify log docs/evidence/accounting-recovery-v4/r9/install-and-fresh-verify.log SHA256 10886e488a80c38d5bb8886fe6328d208e77657745d6f067712be2031754f3b4.
- Human result docs/evidence/accounting-recovery-v4/r9/RESULT.md SHA256 a3a329ead3f05aef36f35534eadeaefda77893c56569b21fb120332d27de5363. Full test logs, exact staged packet, inputs, copied receipts and driver are alongside it.

### AC Verification

- [x] AC #1: Planner captured the exact read-only live v4 baseline (active hex, metadata, typed inventory including all tables/header, and source hashes). Staging outcome was staged-not-installed with stopped=1; no accounting mutation during planning.
- [x] AC #2: Fixed canonical plan/review/authorization schemas bind action, baseline, exact source hashes, ceilings, release-stop mutation, unresolved history, unknown spendability, typed authorization flags. Fixture tampering regressions and independent exact-binding review pass.
- [x] AC #3: Independent reviewer approved exact five staged file hashes and canonical record cross-bindings; separate root-owned operator authorization binds the exact plan and review. Actual independent verdict retained and hash-pinned before execution.
- [x] AC #4: Exact root-owned 0444 canonical source and reviewed isolated system-Python invocation installed one stopped=1 -> 0 UPDATE, then verified logical equality except the authorized stop cell and transaction bytes. Actual live receipt and fresh process prove unchanged active binding/database identity/history/holds/unknowns.
- [x] AC #5: Intent, prior-active, receipt, complete records published durably; fixture tests cover partial namespace refusal, mismatched repeats, exact idempotence, and completion invalidation on failure. Root record hashes archived.
- [x] AC #6: Happy path, fresh already-unhalted refusal (additional real-SQLite fixture), inventory/plan/review/authorization tampering, partial/repeat/failure paths pass; actual root driver refuses wrong flags and wrong interpreter before protected access. F1 empty generated-alias/direct-probe regressions pass across installed interpreters.
- [x] AC #7: All fixture/source tests use disposable non-live stores. Only the separately authorized recovery changed live accounting. No reconciliation, replay, runtime reset, contract admission, promotion, production mutation, merge or push.

### Documentation and Scope

- The old r8 review packet is explicitly historical; its exact rejected root closure was preserved at /Library/GRRR/bootstrap/recovery-v4-history/rev8-4db1623-f01aa240.
- Source-only suites, independent source review, actual recovery execution, and full-capstone status remain distinct. Full capstone has NOT been run by this story.
- bd prime ran; bd sync --from-main --no-push reports no beads database. No parallel tracker was initialized; pvg nd is the authoritative shared backlog. No push occurred.
- Delivery is for independent PM acceptance. Developer/orchestrator does not self-accept, merge, or close the story.

LEARNINGS:
- SQLite table_info omits generated columns even on empty tables; use complete metadata plus a qualified zero-row rowid probe instead of parsing schema SQL text.
- A qualified probe prevents SQLite's double-quoted-string fallback; only the exact missing-column error may indicate WITHOUT ROWID, and unexpected errors must propagate.
- macOS administrator authentication does not grant Documents privacy access. Stage exact hash-verified temporary copies rather than weakening privacy or protected permissions.
- The required backend runner includes durable-evidence tests that generic capstone discovery omits; report its actual 307-test count distinctly from 300-test discovery.

## nd_contract
status: delivered

### evidence
- Source fix 09ef310; independent approval 302d083; archived live install/fresh verification d3e74cbcc9727dab29b9144639d03cc1a7f7adcd.
- Receipt 8b7958e5be76f6b35c4bfafc1f17a2926badfdd813addbefd5d683e376e8eeeb; install and fresh verify published-durable.

### proof
- [x] AC #1: Exact read-only live v4 planner baseline and source binding.
- [x] AC #2: Fixed canonical schemas and typed/exact authority binding.
- [x] AC #3: Independent exact-target approval plus separate operator authorization.
- [x] AC #4: Canonical root install changed stopped 1 -> 0 and preserved every other protected invariant.
- [x] AC #5: Durable intent/receipt/completion with fail-closed partial/repeat controls.
- [x] AC #6: Fixture and actual invocation refusal coverage, zero mandatory source-suite skips.
- [x] AC #7: No live mutation during fixture tests; only authorized recovery outside tests; no out-of-scope actions.

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
