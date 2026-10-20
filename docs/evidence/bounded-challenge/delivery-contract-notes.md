## Implementation Evidence

Commit: 83bab97b3f5edea53005f4cb18374a24faaa12b6
Integration commit: dee02e80f6a99c3c8a21f79bd0e15390ff85a4b9
Branch: story/GRRR-0g4n. No push, acceptance or close performed.

### CI/Test Results

Commands run:
- Parent root: ./scripts/identity-integration /Users/speed/Documents/Codex/2026-10-19/3e4m-b-4/outputs/governed-recursive-research-ratchet/.tmp-sr_pm/vm — exit 0; launches restricted services and ./scripts/test-story bounded-challenge synchronously.
- ./scripts/test-story bounded-challenge — exit 0; 12 required, 12 executed, 0 skipped, 0 failures, 0 errors; 17.875 seconds.
- python3 tests/unit_contracts.py — exit 0; 9/9 passed.
- ./scripts/verify-evidence docs/evidence/bounded-challenge/attempt-20261020T153803Z-4d13bc7b — exit 0; 20 artifact hashes plus chains/anchors/raw objects and all four safety controls verified.
- pvg verify research/common.py research/policy.py research/ledger.py research/execution.py research/evaluator.py research/runner.py bin/grrr scripts/test-story scripts/identity-integration scripts/inspect-attempt scripts/verify-evidence tests/integration/bounded_challenge.py tests/integration/permission_probe.py tests/integration/absent_vm_probe.py tests/unit_contracts.py --format=text — exit 0; 10 recognized files scanned, 0 issues.
- git diff --check — exit 0.

Summary: 12/12 real integration tests and 9/9 supplementary unit tests pass; no skipped tests. Missing policy, absent QEMU, output cap and command deadline were actively tested. Clean execution passes its assertion; forged-PASS execution fails. Both remain blocked for Verified/admission. No hosted CI execution is claimed.

### PROOF

- [x] AC 1: Approved grammar, identity setup and numeric limits recorded; help exposes inspection and stop; pvg core unchanged.
- [x] AC 2: Real CLI/evaluator/QEMU/ledger/report path produced exact CLEAN versus PASS results and durable receipts.
- [x] AC 3: Typed validation/authentication/metadata/budget/rate/audit/error mechanisms wired; mandatory real integration entrypoint fails closed.
- [x] AC 4: Five denied capabilities tested against real evaluator transport, each GateBlocked.
- [x] AC 5: All 11 gates visible; replay/spec/review/approval remain not-run; verified/admitted states blocked.
- [x] AC 6: VM reset/network/sharing/identity/output/deadline/reservation/stop and malformed/unauthorized/stale/duplicate/absent-policy/absent-VM/forged-PASS negative controls passed.
- [x] AC 7: Independent chain/object/anchor verifier and CLI text/Markdown/JSON parity; preserved faulty evidence and unchanged assets.

Evidence: docs/evidence/bounded-challenge/DELIVERY-GRRR-0g4n.md contains the detailed AC table, wiring, measurements, all residual boundaries and histories. Final audit: docs/evidence/bounded-challenge/final-audit-12-tests.json. Final manifest SHA256: 5758264cf727dd9abd1c84e9b3b3c0d7b28575f2919271c5a105ebc26e9def54. Test log SHA256: 3a4fa144133976f27014091dfd3dec95e72dca767df28b2907a7eb36ae396bfe.

### LEARNINGS

- Preserve failed attempts: Documents-path EACCES required narrowly deployed temporary runtimes, not broad permission grants.
- Interactive ls colors caused a legitimate isolation assertion failure; exact shell inventory and observed readiness repaired it without loosening gates.
- Avoid TestCase.run attribute collision; bind idempotency keys even for denied requests.
- Absence and limit branches need real active controls; large raw output needs separate bounded content objects.
- The full 300-second outer watchdog was not allowed to expire; five-second command deadline was actively proven. Recovery/replay/admission, vlt validation and hosted CI execution remain outside these claims. PM must review evidence-driven file/line budget overrun.
