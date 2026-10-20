# Implementation Evidence — GRRR-0g4n

## PROOF

Integration source commit: `dee02e80f6a99c3c8a21f79bd0e15390ff85a4b9`.
Final attempt: `attempt-20261020T153803Z-4d13bc7b` in this directory.
Parent-mediated root launcher exit **0**; same mandatory entrypoint
`./scripts/test-story bounded-challenge` executed **12/12**, skipped **0**,
failures **0**, errors **0**, wall time **17.875 seconds**.

Final independent checks (ordinary operator identity, no VM restart):

- `./scripts/verify-evidence docs/evidence/bounded-challenge/attempt-20261020T153803Z-4d13bc7b`: exit 0; verified 20 manifest artifacts, event chains, separately retained anchors, raw objects, clean/faulty assertions, probe ordering and four real negative controls. Results: `final-audit-12-tests.json`.
- `python3 tests/unit_contracts.py`: exit 0, 9/9 passed; `final-unit-tests.txt`.
- `pvg verify` with every explicit research module, executable script and test path: exit 0, 10 recognized files scanned, 0 findings; `final-pvg-verify.txt`. The scanner does not recognize extensionless scripts; Python syntax checks and actual launcher/CLI execution cover those paths.
- `git diff --check`: exit 0.

The root launcher copies only approved code/assets into fresh restricted temporary
runtimes; no sudo/password collection occurs in worker code. Prior failed and
successful attempts are preserved. The installed QEMU was never renamed or changed
by the negative controls.

### AC table

| AC | Implementation and measured proof |
|---|---|
| 1 | Approved grammar/limits/identities in `docs/IMPLEMENTATION-APPROVAL-2026-10-20.md`; `pvg help/version` discovered without core changes. `bin/grrr --help` exposes inspection/stop and unavailable recovery. |
| 2 | `bin/grrr` → `research/runner.py` → kernel-authenticated evaluator → isolated `research/execution.py` → assertions → `research/ledger.py` → reports. Real `CLEAN\n` passes; frozen `PASS\n` fails. Both are execution-completed, neither verified/admitted. |
| 3 | Typed public functions, registered policy/config, strict field allowlists, kernel peer identities, one-active-guest rate bound, conservative finite reservations, deny audit events and structured errors are on the actual path. 12 mandatory integration tests and 9 supplementary unit tests passed. Missing setup fails the same documented CI entrypoint rather than skipping; no hosted CI execution is claimed. |
| 4 | All five denied actions exercised through real evaluator transport in `test_03_all_denied_capabilities`; each returns GateBlocked. There is no merge, production, patch-generation, harness-adaptation or paid-dispatch implementation. |
| 5 | All 11 gates visible. Independent replay, specification traceability, reviewer outcome and action-specific approval remain not-run. Review/decide/recover return blocked; reports explicitly keep Verified/admission blocked. |
| 6 | Separate UID320/321 read/write and impersonation denial; real fresh-VM reset/network/mount checks; direct authenticated stop before candidates; exact output cap and five-second command deadline actively triggered; 300-second outer watchdog remains configured. Missing policy and absent QEMU really fail in separate restricted runtimes. Malformed metadata, wrong/missing policy binding, mismatched duplicate key, stale epoch, concurrency and forged PASS all exercised. |
| 7 | Independent verifier checks receipts/anchors and retained objects outside candidates. Text/Markdown/JSON snapshot parity is tested through the actual CLI. Faulty report remains inspectable; asset hashes unchanged; no Verified defect, approval or admission effect. |

### Measured results

| Item | Result |
|---|---|
| Clean run | `2c91e5b6d3844deab31d7f7c7c36ad24`; 1.292396s; 24,691 captured bytes; assertion pass |
| Faulty run | `824221898a5b4ccf960a462624105562`; 1.294578s; 24,690 captured bytes; assertion fail |
| Output safety probe | GateBlocked; 1,048,576 captured bytes; 4.467509s; cessation/unchanged assets verified |
| Deadline safety probe | GateBlocked; 6.300878s including boot; 24,603 bytes; cessation/unchanged assets verified |
| Missing policy | Same evaluator source; actual absent protected policy; exit 3, Unavailable; no service socket |
| Absent QEMU | Same executor source; root-owned read-only absent path; authenticated dispatch returns Unavailable; installed executable untouched |
| Reservations | 300s each, retained conservatively; 1,500s cumulative reserved by faulty snapshot (later concurrency test also reserves separately) |
| Review/cost | Review time unknown/not-run, not zero; no paid services invoked; no complete preparation-time accounting claimed |

### Durable identities and hashes

- Final manifest SHA-256: `5758264cf727dd9abd1c84e9b3b3c0d7b28575f2919271c5a105ebc26e9def54`.
- Test transcript SHA-256: `3a4fa144133976f27014091dfd3dec95e72dca767df28b2907a7eb36ae396bfe`.
- Negative-control receipt SHA-256: `7b6ad2252dd79ac23c68feea7dff93704e525c4d1e23c1bfd3764c89a0271442`.
- Clean snapshot file SHA-256: `762913430f973eb6b1c158d69fea4a3206c8fa91e4aa7b6e89112771d7a5f92c`.
- Faulty snapshot file SHA-256: `2b21d7e5b4b20d9e50e23df7b7e1c20af69a79b10974bc4d9f00a6473e9893bd`.
- Clean snapshot ID: `82926d2902291ceb8d934fcf3141629a67f32118f484e25dfd693b80bfaa7753`.
- Faulty snapshot ID: `f8f8c723d20288919cfc1e5191ebcc20daf1f8c2d58f635ef834c8b80390cb3e`.
- Clean event anchor: `77df06051ed13bce52777165f7ac3cc8fed88dd2e88c55ee1e8f95887cc8d273`.
- Faulty event anchor: `bdae7dbe080a3492525fa68b7fec5e07c8620368471f947680f0b7cddbdc5470`.
- Every other artifact hash is in the verified manifest; anchor-file hashes are distinct from event anchor values above.

## LEARNINGS

1. The first service launch from Documents returned EACCES. TCC was suspected,
   not proven. Moving narrowly copied code/assets to fresh restricted temp
   runtimes fixed execution without broadening service access to Documents.
2. Alpine's interactive `ls` emitted ANSI colors. The original strict isolation
   check correctly rejected them before the later stop request. Emit exact
   interface names without aliases; preserve original failed evidence.
3. Wait for observed bootstrap readiness before exercising direct stop, and
   recheck the fence when EOF races cancellation. Stopping an already failed
   run must never authorize execution.
4. Never use `run` as a saved unittest attribute; it collides with TestCase.run.
5. A passing happy path is not proof of absence/overflow/deadline branches. The
   final attempt actively exercises all four missing controls, without deleting
   successful policy or mutating the installed VM tool.
6. Keep large raw bytes as separate content objects; nested hex doubles twice
   and can exceed bounded transport even when guest capture itself is bounded.

## Residual boundaries for PM review

- Synthetic walkthrough only, not a vlt defect or validated vlt baseline. Full
  dependency/license preflight, replay, corpus, comparison, recovery, reviewed
  contracts and admission remain downstream. No automatic promotion exists.
- The five-second command safety deadline is actively tested; the full
  300-second outer watchdog is configured but not allowed to expire in this run.
- Services are stopped after the synchronous launcher. Temporary journals are
  retained but not a persistent deployment or disaster-recovery guarantee;
  exported snapshots survive temp-runtime cleanup.
- No hosted CI infrastructure was supplied; the same mandatory entrypoint fails
  closed without its real identity/runtime prerequisites.
- Root/host compromise is outside this boundary; hashes provide integrity
  relative to retained anchors, not administrator-resistant signing.
- Source/test/launcher code is approximately 1,500 lines. File/total-diff budget
  overrun is dominated by preserved evidence and requires PM review, not omission.
- Local `pvg notes search` discovery failed because worktree `.vault` is absent;
  live story operations used shared `pvg nd`. No global notes were consulted.

## nd_contract
status: in_progress

### evidence
- Integration commit dee02e80f6a99c3c8a21f79bd0e15390ff85a4b9; 12/12 mandatory tests passed, zero skipped/failures/errors.
- 9/9 unit tests passed; pvg verify 10 recognized files, zero findings; independent manifest/chain/object audit exit 0.

### proof
- [x] AC #1: Approved grammar, identities and numeric execution policy discovered and implemented without modifying pvg core.
- [x] AC #2: Real clean/faulty VM path, trusted assertions, durable receipts and distinct readable outcomes.
- [x] AC #3: Typed/validated/authenticated/bounded/audited path; mandatory integration entrypoint fails closed.
- [x] AC #4: Five denied capabilities produce tested blocked outcomes.
- [x] AC #5: Full gate inventory with downstream not-run and no verified/admitted result.
- [x] AC #6: Real isolation/reset/permissions/stop and mandatory negative controls, including active cap/deadline probes.
- [x] AC #7: Independently checked receipts and preserved reports with shared snapshot identity and unchanged assets.
