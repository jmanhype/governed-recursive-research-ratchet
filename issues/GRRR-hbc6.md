---
id: GRRR-hbc6
title: "Recovery: reviewed v4 accounting unhalt planner"
status: closed
priority: 2
type: task
labels: [milestone-1, security, accounting, accepted]
parent: GRRR-2t3h
created_at: 2026-11-08T15:08:46Z
created_by: speed
updated_at: 2026-11-08T17:59:09Z
content_hash: "sha256:082b37b3ad78d46be76fc4ed06df24dee9a201c07f977afc86e5d7975817d0f7"
assignee: dev-GRRR-hbc6
follows: [GRRR-q3hp, GRRR-k3j7]
closed_at: 2026-11-08T17:44:52Z
close_reason: "Accepted: all seven recovery ACs are supported by exact hash-bound source, independent approval, three-interpreter zero-skip logs, real fixture refusals, durable live receipt, and separate fresh-process verification."
led_to: [GRRR-734u, GRRR-n49g]
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
Merge authorized 2026-11-08: story/GRRR-hbc6 at 9df1bd0081191130bb919b4b36d586a834aacd85 merged locally into epic/GRRR-2t3h at 5f6ce4e83e2426e859127af568aa730c19dc6a9b. Both merge parents and tree identity verified; accepted status unchanged. No push or protected mutation. Next scope: fresh replay-runtime source work only, no replay execution.
Post-merge source verification at epic commit 5f6ce4e83e2426e859127af568aa730c19dc6a9b: /opt/homebrew/bin/python3.14, /opt/homebrew/bin/python3.12, /usr/bin/python3 -B tests/unit_capstone_backend_suite.py each passed 307 tests, zero failures/errors/skips. Raw logs /private/tmp/grrr-hbc6-merged-Python-3.14.3.log (SHA256 faed6d2a99a7d298e67db9b645b0033258dbb4f1405b28656d79ef43bd2c7548), /private/tmp/grrr-hbc6-merged-Python-3.12.9.log (47994250ed9d0e8cc73a9c1a35392476df990fc89302bf5d89151ea2950670cf), /private/tmp/grrr-hbc6-merged-Python-3.9.6.log (702cf63c78a9b5a30df331084ad50245b1788e6f02e36b51203cde12b5d49a88). Merged tree equals accepted story tree 27b7f8928661812af6445213e12988dd5e5b6cf8. No replay, reconciliation, protected mutation, promotion, admission, production mutation or push.

## nd_contract
status: accepted

### evidence
- PM closeout applied via pvg story accept on 2026-11-08.

### proof
- [x] Story closed after accepted label was applied.


## PM Decision
ACCEPTED [2026-11-08]: Independent PM evidence review meets all seven ACs.

### evidence
- Queue direction was pm_review; fresh delivery verifier passed 9/9.
- Reviewed story HEAD d3e74cbcc9727dab29b9144639d03cc1a7f7adcd and exact source fix 09ef310b7b5eb1df021ac6c56b8251cf68ff625b; source/test files are unchanged after independent review.
- Independently recomputed review SHA256 fc4cd5f9df2ada6cfe2784e940759ee0dae066b96e30c258a57feec873c60457 and exact cross-bindings for plan 4603b443783e8bfc91f6a1c1c408f54cd8f3f073aaf35f14af9278d01d8f0953, review 1bcb3351e435ff476c35e5df713b6facd519a9fa96d0670db9f2df13388ea2dc, authorization 5d1deb5fe0c26e378233c0a1fa1c1104fa60ce8aaee38673b2fd4efa9f6e026e, baseline e2e9289a971b069437113843309565b6706142e3a205e18a23beea583d639c5d, and both source hashes.
- Verified full plan inventory covers metering/overhead/reservations/state/store_identity plus schema, stable header, active binding bytes, metadata, and source hashes; staging log reports staged-not-installed with stopped=1.
- Raw required logs record 307 passing tests and zero failures/errors/skips on each installed Python 3.14.3, 3.12.9, and 3.9.6; each includes all 32 recovery tests. The supplemental real-SQLite already-unhalted fixture passed once and was independently rerun.
- Raw install and fresh-process verification logs both report published-durable, stopped 1 -> 0 then 0 -> 0, unchanged active bytes/metadata, and unchanged schema/history/holds/unknowns. Receipt 8b7958e5be76f6b35c4bfafc1f17a2926badfdd813addbefd5d683e376e8eeeb and completion ea5dae2b353a1e7c0747f92b5bdb0b907a92f3b0939588ea63046a70403407af were recomputed. historical_unknowns remains unresolved and spendable remains unknown.
- The isolated driver and invocation pin exact hashes and reject wrong flags/interpreter before protected access. No reconciliation, replay, campaign, admission, promotion, production source mutation after review, merge, or push is claimed.

### proof
- [x] AC #1: Read-only exact v4 planner baseline and source binding.
- [x] AC #2: Fixed canonical plan/review/authorization schemas and typed authority bindings.
- [x] AC #3: Independent exact-target approval plus separate operator authorization.
- [x] AC #4: Root-isolated canonical installer released only the stop bit and preserved protected invariants.
- [x] AC #5: Durable intent/prior-active/receipt/completion records and fail-closed partial/repeat controls.
- [x] AC #6: Required fixture coverage and three-interpreter source suite passed with no skips.
- [x] AC #7: No live mutation during tests; only the separately authorized recovery outside tests; no out-of-scope action.

## nd_contract
status: accepted

### evidence
- PM independently reviewed story proof, committed source/tests, review/plan/authorization JSON, raw test logs, install/fresh-verify log, and retained receipts.

### proof
- [x] AC-by-AC verified from artifacts and exact hashes

## nd_contract
status: delivered

### evidence
- Transitioned via pvg story deliver on 2026-11-08.

### proof
- [ ] Developer evidence block must remain authoritative above this contract.


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
- 2026-11-08T17:38:02Z status: in_progress -> in_progress
- 2026-11-08T17:38:02Z auto-follows: linked to predecessor GRRR-k3j7
- 2026-11-08T17:44:52Z status: in_progress -> closed

## Links
- Parent: [[GRRR-2t3h]]
- Follows: [[GRRR-q3hp]], [[GRRR-k3j7]]
- Led to: [[GRRR-734u]], [[GRRR-n49g]]

## Comments

### 2026-11-08T17:39:36Z speed
## Implementation Evidence

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

### 2026-11-08T17:45:15Z speed
## PM Final Review
ACCEPTED [2026-11-08]: All seven story ACs are independently supported. Production source is unchanged since the fc4cd5f9df2ada6cfe2784e940759ee0dae066b96e30c258a57feec873c60457 review; exact plan/review/authorization and receipt hashes were recomputed; required source logs passed with zero skips; install and a separate fresh process both returned published-durable with only stopped 1 -> 0 and protected history/unknowns retained. This acceptance does not reconcile, establish spendability, qualify the capstone, merge, or push.

## nd_contract
status: accepted

### evidence
- Fresh PM review of GRRR-hbc6 story, committed artifacts, source/tests, independent approval, canonical records, raw logs, and retained live-operation evidence.

### proof
- [x] AC #1: Exact read-only v4 planner baseline and source binding.
- [x] AC #2: Fixed canonical schemas and exact typed authority bindings.
- [x] AC #3: Independent exact-target approval plus separate authorization.
- [x] AC #4: Root-isolated canonical install changed only the stop bit and preserved protected invariants.
- [x] AC #5: Durable records with fail-closed partial/repeat controls.
- [x] AC #6: Happy path, fresh already-unhalted refusal, tampering, partial/repeat/failure, wrong-interpreter/flags, and rowid regressions are covered.
- [x] AC #7: No live mutation during tests and no out-of-scope action.
