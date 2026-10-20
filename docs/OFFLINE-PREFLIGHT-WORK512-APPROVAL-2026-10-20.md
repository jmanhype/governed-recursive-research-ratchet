# Operator approval amendment: ephemeral workspace 512 MiB

Operator explicitly authorized only offline-build guest /work tmpfs increasing
from 350 MiB to fixed 512 MiB and parent-mediated identity integration rerun,
as recorded in GRRR-90te nd notes and dispatcher handoff.

This supersedes only the workspace cap in the RAM amendment (SHA-256
`2fa136998c51d4a0dc3d3ffc535345d4b1b815dc1c660ae6ceba064efe8c365c`).
VM RAM remains 1024 MiB; synthetic policy remains unchanged at 512 MiB RAM.
Retain one vCPU, two fresh VMs, 300 seconds per invocation, 240-second initial
command timeout pending successful measurement, 600-second cumulative build/test
budget, 30-second boot, 2-second acknowledgement, 5-second TERM grace plus KILL,
1-MiB output cap, and 15-GB host-free gate.

Pinned source/toolchain and license scope remain unchanged. No guest networking,
host shares, clipboard, forwarded agents, host fallback, paid service, production
access, automatic merge, or promotion. Prior attempts remain evidence, not success.
If /work space fails again at 512 MiB, stop; no further increase authorized.
