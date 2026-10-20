# BLOCKED — 350 MiB guest workspace capacity

Attempt `attempt-20261020T205833Z-60a4135e` used approved 1024 MiB VM RAM.
Tests 1–5 passed; all six executed, zero skipped, one failure. Compilation
reached linking without the prior compiler-kill diagnostic. Linker failed:

```
/work/go/pkg/tool/linux_arm64/link: mapping output file failed: no space left on device
```

The guest ephemeral `/work` tmpfs is capped at 350 MiB. This is its capacity
boundary, not evidence of host disk exhaustion or another VM RAM kill.
Total elapsed: 18.121606208 seconds; command: 16.788934333 seconds.
No successful first/second build or baseline admission exists.

All 24 manifest artifact hashes verified:
- Manifest: `0a0b4707b4c4f6a40d9dab62b2d4948cabf3e858fd47d8dad2e9db5aacb93ebb`
- Build: `362724662f774edefae58a42cbd2384105d72b4116418fa66ee08daccc9cdbef`
- Test output: `7e2068f1d8654238bef8dcccae589fb6442c960cf461717988160aa6fff270c7`

**Operator decision requested, not applied:** increase only guest ephemeral
`/work` tmpfs from 350 MiB to fixed 512 MiB. VM RAM remains 1024 MiB and all
other limits/boundaries remain unchanged. This proposal is not a guarantee
that the next build will fit or pass.

No workspace-cap change, VM rerun, delivery, merge or promotion performed.
All attempts retained; baseline remains false pending explicit authorization.
