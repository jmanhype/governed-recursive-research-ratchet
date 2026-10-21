# Installed QEMU-only checkpoint

Parent installed plan `d1bf4b297c3d31f48e494abfb3c1bd9456d438b8f4e328d62787841e0aaf0fcd`.
The copied readback is byte-identical to the protected installed readback.
`live-readback.json` records a separate UID 501 read-only audit using
`scripts/audit-installed-qemu`: 221 files, 20 directories including the root,
zero symlinks, exact hashes and ownership/modes, complete absolute dependency
closure. This audit never invokes QEMU or writes installed files.

Parent additionally reported strict codesign verification of all four Mach-O
images, Hypervisor-only QEMU entitlement, OS 27.0/26A428, and real UID 320/321
read/execute access with write/link denial. Those identity attempts were NOT
reexecuted by this worker. Parent measured 16,730,546,176 bytes free afterward.

Accounting is absent. Execution authorization, guest execution, accounting
mutation, and runtime-loading validation are all false in the installed receipt.
Static verification does not establish runtime isolation or candidate correctness.
