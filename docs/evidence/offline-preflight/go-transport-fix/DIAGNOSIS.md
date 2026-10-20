# Go archive transport repair

Preserved attempt `attempt-20261020T180443Z-105b1565` passes isolation and all
52 source hashes, then fails Go dependency resolution. Guest reports missing
crypto/internal/entropy/v1.0.0 and conflicting packages involving a truncated
example_text_marshaling_test.go name. Loose ISO9660 names are not a valid
transport for the exact toolchain tree. Prior attempt/image/receipt remain.

Preparation now ships the exact pinned archive as visible go.tar.gz, never the
loose Go tree. Guest verifies SHA-256 before extracting to /work, then explicitly
sets GOROOT=/work/go and PATH=/work/go/bin. Source tar transport remains unchanged.
The newly generated ISO was read back with libarchive and its embedded Go archive
verified against `3f4227ce7b206a513e794f1393adb473a07b46e94d18bd15d1c684bbb7319797`.
The prepared archive uses an APFS clone of the retained pinned archive; no full
duplicate copy. Extracted tree was moved outside media to go-loose-v4-preserved,
not deleted. Prior input/receipt are input-v4.iso and asset-receipt-v4.json.

Image SHA-256: `fb3a017ecf56fd3f9e211fcd7fefd468ace46e5914c25df35a0689f62e8a5cd9`.
Receipt SHA-256: `7eaf64a4c309d10a5b94740e17c05d83c6ce1aba580c97783acd0ba1e501e090`.
Guest SHA-256: `3adb08289d126537988637899c65281baf342f584c86953c5bdc094443b67420`.
Profile/inventory/license review unchanged. Free bytes after packaging:
15,065,227,264, only ~65 MB above mandatory floor. Parent must recheck before
launch and obtain authorized cleanup if needed. No cleanup was inferred here.

All original resource caps remain, including 350 MiB work tmpfs and 512 MiB VM.
Extracted Go consumes part of that work budget; resource exhaustion remains a
measured blocker, never permission to increase limits or use host fallback.

30 unit tests pass; shell syntax and Python compilation pass; pvg verify passes.
No guest/root execution by worker; real build proof remains outstanding.
