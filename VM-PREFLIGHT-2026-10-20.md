# Governed Research Ratchet VM Preflight — 2026-10-20

## Status

**PASS for the measured local QEMU smoke preflight.**

This result authorizes no implementation by itself. The first walking-skeleton story still requires operator approval of the standalone runner grammar, restricted identities/permissions, policy scope, and final numeric execution limits.

## Operator authorization

The operator authorized:

1. Removal of the two named stale caches.
2. Additional removal of the CoreSimulator dyld cache after the first cleanup remained below 15 GB free.
3. QEMU installation.
4. A no-network, disposable-snapshot VM preflight.

## Disk preparation

### First authorized cleanup

Removed:

- `/Users/speed/Library/Caches/com.openai.codex/org.sparkle-project.Sparkle/Installation`
  - 9.1 GiB
  - 19,900 files
- `/Users/speed/Library/pnpm/store/v3`
  - 7.3 GiB
  - 419,743 files

Observed free space moved from approximately **4 GB to 14 GB**, short of the required 15 GB. QEMU installation therefore did not begin at that point.

Manifest:

- `docs/evidence/vm-preflight/vm-cleanup-manifest.txt`

### Second authorized cleanup

Removed:

- `/Users/speed/Library/Developer/CoreSimulator/Caches/dyld`
  - 3.5 GiB
  - Four files

No active CoreSimulator process was present.

Observed free space moved from approximately **14 GB to 17 GB**, satisfying the minimum 15 GB preflight condition.

Manifest:

- `docs/evidence/vm-preflight/coresimulator-cleanup-manifest.txt`

## Installed VM tool

- Executable: `/opt/homebrew/bin/qemu-system-aarch64`
- Version: `QEMU emulator version 11.1.2`
- Installed package size reported by Homebrew: 729 MB

Homebrew updated itself from `7.0.4` to `7.0.10` and installed or upgraded QEMU dependencies as part of the authorized install.

### License boundary

QEMU is GPL-2.0-only. The approved use is an independent external executable: no QEMU source is copied into this project, no QEMU code is linked, and no QEMU binary is redistributed. This does not classify the project itself as GPL-licensed.

## Pinned guest assets

- Alpine ISO: `alpine-virt-3.22.6-aarch64.iso`
- ISO SHA-256: `09d601858d72484c89d576fb735215cccf54a92a03e67ca4a7fa7e4b8ec4a7a2`
- Kernel SHA-256: `dd37c4460f933ec909ff022c34944ff7e1a5300aff99750e3bdc02cd4074c332`
- Initramfs SHA-256: `899b8023e92db85345375b3ad10c2c9e5b977dc35a0429489ab2476ebad507ec`

The official `.sha256` file matched the downloaded ISO.

## QEMU control boundary

The tested command used:

```text
-machine virt
-cpu host
-accel hvf
-m 512
-smp 1
-net none
-nographic
-monitor none
-no-reboot
-snapshot
```

It included no host-shared filesystem, `virtfs`, `fsdev`, or 9p device.

## Measured runs

Two independent boots reached the Alpine login marker.

| Run | Time to marker | Stop mode | Stop latency | Output | ISO unchanged |
|---|---:|---|---:|---:|---|
| 1 | 6,422.769 ms | SIGTERM within 5-second grace | 63.655 ms | 23,186 bytes | Yes |
| 2 | 6,545.848 ms | SIGTERM within 5-second grace | 59.223 ms | 23,186 bytes | Yes |

Both runs:

- Used a disposable snapshot.
- Had networking disabled by `-net none`.
- Had no host-share device.
- Were limited to 512 MiB RAM and one virtual CPU.
- Had the QEMU monitor disabled.
- Remained below the 1 MiB output cap.
- Preserved the input ISO byte-for-byte.

The `eth0` string was not observed in either boot log, but the authoritative control evidence is the explicit QEMU `-net none` configuration rather than textual absence alone.

Machine evidence:

- `docs/evidence/vm-preflight/qemu-no-network-preflight.json`
- `docs/evidence/vm-preflight/qemu-no-network-run-1.log`
- `docs/evidence/vm-preflight/qemu-no-network-run-2.log`

## Limits supported by measurement

The successful smoke preflight supports this initial proposal:

- VM memory: **512 MiB**
- Virtual CPUs: **1**
- Boot/login deadline: **30 seconds**
- Stop acknowledgement target: **2 seconds**
- SIGTERM grace: **5 seconds**
- Forced kill after grace: **required**
- Guest output cap: **1 MiB**
- Minimum host free space: **15 GB**

These remain proposals for `GRRR-0g4n`; the operator must approve them before implementation or synthetic experiment execution.

## Not proven by this preflight

This smoke test did **not** establish:

- A standalone runner CLI grammar.
- Separate restricted evaluator/executor OS identities or endpoint ACLs.
- An authenticated evaluator-owned control transport.
- A durable append-only evidence ledger.
- Trusted observation of arbitrary candidate output.
- A full clean/faulty `vlt` challenge.
- Independent replay or contract admission.
- License clearance for every transitive project dependency.

Those remain mandatory first-story or downstream gates and must fail closed if absent.
