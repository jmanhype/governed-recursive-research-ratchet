# GRRR-90te final developer audit

Runtime code commit: `403c907e66095ee9d860158e069e0d963d8a9b48`.
Canonical successful attempt: `attempt-20261020T233115Z-6e1e938c`.
Parent ran `python3 scripts/offline-identity-integration VM_DIRECTORY ASSETS LICENSE_REVIEW`
with the absolute pinned paths recorded in prior handoffs. The registered
`./scripts/test-story offline-preflight` entrypoint delegates to that same launcher
using the ignored .offline-inputs.json binding; it was not separately rerun here.
Launcher exit 0; mandatory integration 6/6, no skips/errors/failures, 348.058 s.
The developer did not execute privileged integration or source on the host.

Independent command:
`python3 scripts/verify-offline-evidence docs/evidence/offline-preflight/attempt-20261020T233115Z-6e1e938c`
passed all manifest hashes, six evaluator snapshots, complete counts, independent
run identities, bounded termination, source/image binding, and matching build bytes.

## Exact identities and measurements

- Manifest: `85fbaadbae832ebb67110bbdfe980025fc011d6adb720866054acb4c690b1c16`
- Test output: `1a88076a5222ac0217f6eb59d642049d1bb3138c3d457d657dbcadcdd7246946`
- Baseline receipt: `cd26c3022ac378d726136079b0989eed5ff8842b6afaf613fdfa2420256ebd50`
- Both build identities: `ae21fbda8127e7560c30bbd1026d79dffafefe4a32a78728521228a1162af5ea`
- Profile: `2e08f0288355a64eba22b75fdeb1e62ac14dfaea3be26cbee38ece6eb4051d47`
- Runtime approval: `3474c0a20999af6048ba862bc37e274da79ca89cbaef1ed84d2c1fe7f7b71ed5`
- License review: `4ce0bb6c8533eb9036b28d0145f6856a80a8f66a0cb93cee0fe6124b5acc8aaf`
- Maximum measured command: 44.959017792 s; invocation: 46.332908917 s.
- Two builds total: 92.563880959 s, below 600 s.
- Measured stop/force acknowledgement roundtrips: 0.000496167 / 0.000453208 s.

The former “unmeasured” timing assumption is superseded by these observations.
Approved command ceiling remains 240 s, total ceiling 300 s; no new ceiling is
silently inferred from one measurement. VM RAM 1024 MiB and work tmpfs 512 MiB
have separate recorded operator amendments; synthetic RAM remains 512 MiB.

## AC Verification

| AC | Verification and mapped implementation | Result |
|---|---|---|
| 1 | `research/offline.py` source_inventory verifies all 52 exact pinned Git blobs, correct LICENSE blob, clean tree and behavior references. Inventory/asset receipt, pinned toolchain, successful baseline receipt and two source hash checks per guest bind identities. | PASS |
| 2 | `research/offline_execution.py` extends accepted Executor without synthetic changes. Two independent fresh VM runs build identical bytes; `offline_preflight.py` test_06 checks fresh reset, full upstream tests and synthetic IO. Complete inventory includes Go archive members/notices, 101 APKs, host dynamic closure, origins/hashes and no models; actual offline dependency closure printed. | PASS |
| 3 | Separate 159-component local-use review binds exact inventory, all risks/resolutions, operator approval and license/provenance evidence. GPL/LGPL local-execution boundaries and Apple terms explicit; no redistribution/new-linking rights claimed. Root launcher rejects missing/incomplete review. | PASS |
| 4 | Guest prints actual routes/mounts/devices, permits loopback only, rejects integration/host/protected paths and input writes; inputs detached read-only, no share/network flags. Host service identity probes deny protected paths. Actual synthetic vault create/read occurs inside guest only. | PASS |
| 5 | Root-mediated launcher verifies independent service identities, ownership/ACLs, root-readonly inputs/config and evaluator-private policy. Test_06 proves fresh reset in both runs, resource caps and unchanged input hashes. Missing capability fails closed; no host fallback. | PASS |
| 6 | Tests 1–5 exercise real network/share/identity/image/dependency misconfiguration, unauthorized peer/protected paths, concurrency, stop acknowledgement, graceful/forced cancellation, watchdog and output cap. Versioned approval documents contain emergency stop procedure and numeric ceilings. Earlier failed attempts remain inspectable. | PASS |

Boundary map: `research/execution` remains accepted synthetic implementation;
offline dispatch specialization is `research/offline_execution.py`; policy loading
is `research/policy.py` plus protected approval validation in `research/offline.py`.
Logical integration path maps to `tests/integration/offline_preflight.py`,
`tests/integration/offline_probe.py`, and root launcher. No pvg/nd/vlt core changes.

## Final supplementary checks

Commands:
- `PYTHONPATH=.tmp-sr_pm/final-coverage-tools COVERAGE_FILE=.tmp-sr_pm/final.coverage python3 -m coverage run --source=research -m unittest discover -s tests -p 'unit*.py' -v`
- Same environment, `python3 -m coverage json -o docs/evidence/offline-preflight/final-audit/unit-coverage.json` and `coverage report`.
- `pvg verify research/offline.py research/offline_execution.py research/policy.py tests/unit_offline.py tests/unit_offline_runtime.py tests/integration/offline_preflight.py tests/integration/offline_probe.py`
- `python3 -m py_compile scripts/prepare-offline-assets scripts/prepare-offline-preflight scripts/offline-identity-integration scripts/test-story scripts/verify-offline-evidence`
- `sh -n research/offline-guest.sh`

31/31 units pass; pvg verify 7 files, zero issues; compilation/shell syntax pass.
Coverage.py 7.13.4, **unit-only research line coverage 24.0761478163% (215/893)**.
No integration coverage instrumentation was performed or inferred. Native host
coverage tooling is auxiliary, not part of candidate execution or VM provenance.

## Residual boundaries and PM investigation

This is a verified offline baseline, not admission/promotion/security certification
against administrators. Baseline receipt intentionally retains admission=blocked.
Full observation attacks and stop/admission linearization remain other stories.
Historical BLOCKED artifacts describe prior attempts, not current baseline status.
Diff budget exceeded: 13 implementation/test files, 1525 added/2 deleted lines
relative to accepted epic base, plus preserved evidence. PM investigation is
required by story; no waiver or automatic acceptance is claimed.

## LEARNINGS

- Verify primary ISO9660 namespace, not extension-aware macOS/Joliet listings.
- Archive exact source/toolchain names; loose ISO trees can alter case/long names.
- Preserve dispatch diagnostics before assertions; missing receipts hide root cause.
- Distinguish VM RAM, ephemeral workspace and host free-space gates.
- Resource failures require explicit narrowly scoped amendments, never automatic increases.
