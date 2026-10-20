# BLOCKED — approved 512 MiB baseline build cannot complete

Canonical latest attempt: `attempt-20261020T182702Z-768d552e`.
All 24 manifest artifact hashes independently match. Manifest SHA-256:
`b4e19f303ae9cf644484de878014a9b51e142cc4989c0a5eb55c8174222ced0b`.
Build-1 SHA-256:
`a0949547b9a7f7c4a700887e80ddda4d391ecda3c7d3bb5bd0ebfb41d9dc8017`.
Detailed measured values and test-output hash are in verification.json.

Tests 1–5 passed; 6/6 executed, zero skipped, one failure. The first real build
passed isolation, exact source checks, pinned Go extraction and dependency
closure, then compilation reported:

```
runtime: /work/go/pkg/tool/linux_arm64/compile: signal: killed
```

Approved configuration: 512 MiB RAM, one vCPU, 350 MiB work tmpfs, no guest
network/share, 240-second command bound and 300-second total hard ceiling.
Measured first build elapsed 193.6099525 seconds; command 174.8244202 seconds.
Adapter error is null, guest command exit is 1, assets unchanged, guest ceased
without forced termination. The compiler kill is directly proven; OOM is the
resource-exhaustion interpretation, not a claimed kernel OOM diagnostic (none
was captured). This is a measured blocker under the approved resource envelope,
not a successful build, timeout, reproducibility proof, or permission to retry
with higher limits.

No second build or full baseline test success exists. Baseline remains false;
downstream research/admission remains blocked. No VM rerun, limit increase,
host fallback, promotion, delivery, or acceptance was performed at this checkpoint.

**Operator decision required:** explicitly authorize a revised memory/resource
profile or an alternative isolated execution strategy, with corresponding
versioned approval and gate changes, before further real build execution.
Dispatcher will release the claim; developer does not deliver this story.

All failed attempts and reproducibility inputs are retained. This checkpoint
supersedes earlier readiness-to-rerun notes, not their immutable evidence.
