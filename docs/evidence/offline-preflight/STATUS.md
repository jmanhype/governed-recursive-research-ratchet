# GRRR-90te — preparation checkpoint, not delivery

No vlt source, Go build, Go test, or new VM profile was executed. No baseline
has passed. Software admission/promotion remains unavailable. The existing
synthetic policy, evaluator, executor, CLI and integration suite are unchanged.

The dispatcher required a stop at the offline-profile authorization boundary.
The operator-approved document limits dispatch/semantics to GRRR-0g4n; that is
not authority to execute Go/vlt or raise the synthetic five-second command limit.

## Implemented checkpoint

- `research/offline.py`: exact source-byte inventory, toolchain archive inventory,
  strict structural compliance validation, distinct unregistered profile proposal,
  root-owned read-only explicit approval binding. Structural compliance checks
  do **not** authenticate evidence references or confer clearance.
- `scripts/prepare-offline-preflight`: offline, non-executing preparation with
  append-only attempt directories and failure receipts. It returns preparation
  success separately from an explicitly blocked preflight. No core changes.
- `tests/unit_offline.py`: eight supplementary contract tests. The full available
  unit set passes 17/17 with no skipped tests. Coverage is **unit-only**: 22.95%
  of `research/`, 41.76% of `research/offline.py`. Neither is VM coverage.
- `pvg verify` passed, scanning two `.py` files; its extension filter omitted the
  extensionless preparation script. `py_compile` checked all three code files.

## Reproducibility inputs and evidence

Final preparation: `preparation-20261020T160545Z-bc3d6dc7/`.
`manifest.json` binds every artifact. `profile-proposal.json` binds exact bytes of
`inventory.json`; the inventory binds full Go members/notices files.

- Source: https://github.com/paivot-ai/vlt commit
  `129e0b3f15a3bd6af949ee47d76f6855c582ab73`; every tracked blob compared with
  working bytes using Git blob SHA-1 plus SHA-256; ignored/untracked extras rejected.
  Canonical source file inventory SHA-256:
  `3c43f236b2f3bc86e1fcd8c634c88ecd119a759458fc3f7b3580dda46271a487`.
- Correct LICENSE blob: `c004659349c7a1f6c55e5107b53a0766085e8d2e`.
  The original dispatch brief's `...c551...` hash was a typo; upstream/story use
  `...c55e...`. Apache-2.0 text is preserved, not treated as total clearance.
- Toolchain: https://go.dev/dl/go1.26.10.linux-arm64.tar.gz, SHA-256
  `3f4227ce7b206a513e794f1393adb473a07b46e94d18bd15d1c684bbb7319797`.
  Official download metadata matched before archive inspection. Archive contents
  were read, never extracted/executed. Every regular member is hashed; notice
  matches preserve text or exact hex for non-UTF8 bytes. No model/API calls.
- Source `go.mod` declares no external module dependencies. This is **not** proof
  of complete resolved dependencies: offline `go list -deps`, standard-library
  bundled components, host dynamic libraries and Alpine APK review remain pending.
- The previously approved ISO/kernel/initramfs were rehashed and matched; that
  identity check is not package-level license clearance or new guest isolation proof.
- First failed preparation (`preparation-20261020T160442Z-1bd0c23f`) is preserved.
  A binary fixture matched the notice filename search; strict UTF-8 decoding failed.
  The corrected inventory preserves non-text matches as hex instead of discarding
  them. An intermediate successful preparation remains on disk, not canonical.

Untracked preparation inputs remain under `.tmp-sr_pm/offline-preflight/` (source
Git clone, official Go metadata and archive). No upstream code/toolchain/QEMU
binary was added to Git. Reproduce preparation, with the story worktree as cwd:

```sh
python3 scripts/prepare-offline-preflight \
  .tmp-sr_pm/offline-preflight/vlt \
  .tmp-sr_pm/offline-preflight/go1.26.10.linux-arm64.tar.gz \
  /Users/speed/Documents/Codex/2026-10-19/3e4m-b-4/outputs/governed-recursive-research-ratchet/.tmp-sr_pm/vm
```

## Approval requested (not granted)

Permit an evaluator-controlled offline vlt compile/test preflight using the pinned
source and Go 1.26.10 in the already approved no-network 512-MiB/1-vCPU disposable
VM. Two independent fresh VMs, each limited to 300 seconds total, count at most
600 seconds cumulatively before other probes/replays. No host shares, networking,
clipboard, forwarded agent, production access, paid service, or host build fallback.
Proposed per-build/test command timeout: **240 seconds, unmeasured**. Do not
represent this as a measured bound; measure after authorization under the existing
300-second hard ceiling. Keep 30-second boot, 2-second stop acknowledgement,
5-second TERM grace and mandatory force-kill, 1-MiB output and 15-GB host-free gate.

Separate review is still required for Alpine/kernel/GPL components and bundled
toolchain/dependency notices. Existing QEMU approval only permits the external
executable; it does not clear the entire guest/toolchain or authorize redistribution.

## Remaining work / AC accounting

| AC | Checkpoint | Still required |
|---|---|---|
| 1 | Source/license/blob and asset hashes verified | Offline baseline correctness, build hashes, evaluator receipt |
| 2 | Source/toolchain provenance prepared | Two independent fresh offline builds, byte equality, complete resolved dependency/tool/image inventory |
| 3 | Strict structural license gate; notices preserved | Actual per-component compliance verification and separate reviews |
| 4 | No new candidate execution or weakened boundary | Real routes/mounts/devices/host-secret/protected-path probes and synthetic I/O |
| 5 | Existing identities/caps not changed | New-profile evaluator-controlled input image, clean reset/ACL/resource measurements |
| 6 | New profile blocked pending explicit approval | Watchdog/ACK/TERM/KILL measurements and misconfigured network/share/identity/image/dependency tests |

The new VM adapter, root-mediated launcher, and mandatory
`./scripts/test-story offline-preflight` real integration suite are **not yet
implemented**. The existing test entrypoint rejects that slug; do not claim it ran
or passed. Do not deliver/accept the story from this checkpoint. Resume implementation
after approval; root/service-identity integration will then require a parent-mediated
run. There is deliberately no speculative root command that could imply a working
launcher exists.

## Learnings

Top-level licensing, source identity and clean Git state answer different questions.
A notice scan can encounter binary fixtures; preserve bytes and require review.
Preparation success must never share a success field with baseline/preflight success.
An approved synthetic runtime does not authorize a new build command profile.
