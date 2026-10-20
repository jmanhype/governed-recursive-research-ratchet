# Operator approval amendment: offline build RAM 1024 MiB

The operator explicitly authorized increasing only offline-build VM memory from
512 MiB to 1024 MiB and rerunning parent identity integration. Authorization is
recorded in GRRR-90te nd notes and dispatcher handoff. This supersedes only the
memory restriction in OFFLINE-PREFLIGHT-APPROVAL-2026-10-20.md, whose SHA-256 is
`1a0169d56c118004243ed3d1c1ba080628277c94196f39173643306997361815`.
The original approval and 512-MiB failure evidence remain immutable.

Retain exactly: one vCPU; two fresh VMs; 300 seconds total per invocation;
240-second initial command timeout pending successful measured result;
600-second cumulative build/test ceiling; 350-MiB work tmpfs; 30-second boot
deadline; two-second stop acknowledgement target; five-second TERM grace then
forced kill; 1-MiB output cap; 15-GB free-space gate.

Pinned source/toolchain, license review and no-network/no-host-share/no-clipboard/
no-forwarded-agent boundaries remain unchanged. No host fallback, paid service,
production access, automatic merge, promotion or synthetic-profile change.
The registered synthetic profile remains 512 MiB.

Only the parent may run privileged integration. If compilation is killed again
at 1024 MiB, stop and report: no further resource increase is authorized.
This approval does not establish successful builds or permit delivery.
