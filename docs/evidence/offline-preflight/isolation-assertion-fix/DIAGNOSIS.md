# Isolation assertion repair

Preserved attempt `attempt-20261020T174728Z-f95be96e`: tests 1–5 passed;
6/6 executed, zero skipped, first build exited 1 before isolation PASS.
Build receipt SHA-256: `80f7573bcd9bbe2146e0d9144ee15de9f067ea1cbb9afdd6d3ff0182b43e5312`.
Test output SHA-256: `4cce4bd4b4236a340adf8311efe5dbae6352f295f4610575c75be203b843b17f`.

Decoded receipt proves `/dev/vda /media/vda iso9660 ro` and
`/dev/vdb /inputs iso9660 ro`, and only loopback network interface. It begins
with two IPv6 loopback route rows, without an IPv4 route header. Thus the old
`wc -l /proc/net/route == 1` assertion is incompatible with this empty IPv4
table and occurs before the boot-block assertion. The old script did not print
individual assertion results or sysfs ro values: the precise exiting shell line
cannot be proven retrospectively from this output alone. No line-level proof
is fabricated. New named check markers make subsequent failures inspectable.

The IPv4 predicate now accepts empty/header-only tables, rejects every actual
route row, and is tested through real awk execution. IPv6 rows must be loopback.
The boot ISO must be mounted read-only at `/media/vda`; its snapshot block-layer
sysfs flag need not be 1. Detached `/dev/vdb` must have block ro=1 and its ISO9660
mount at `/inputs` must be ro. The write-denial test remains. All other no-share,
no-credential, reset, source, and resource assertions remain, with `set -eu`.

Repackaged only evaluator-authored script using retained verified Go archive
and source media. Previous image/receipt preserved as `input-v2.iso` and
`asset-receipt-v2.json`; earlier v1 also retained. Generated Go extraction retained
for now; no extra deletion performed. Free bytes after packaging: 15,839,195,136.
Both failed attempts are preserved unchanged. No guest/root execution performed.

New image SHA-256: `1a5dc0e5c64fa107fd186196d88d0d138a71b2d0796b30766841e75fbbb4ad89`.
New receipt SHA-256: `3f8fefed6a5b9b2c1569295d75df470fa0cb6107154e16c97c3607029d17b5d6`.
Guest script SHA-256: `5eb34ab39ffbdf06e3f5d83718043551f094693859180a7072a520f25b39598f`.
Profile SHA-256 unchanged: `d883d13b6b7214a7e6e479a6135f5535f04819abfd0b4506e2b9c0c056612400`.
License-review SHA-256 unchanged: `4ce0bb6c8533eb9036b28d0145f6856a80a8f66a0cb93cee0fe6124b5acc8aaf`.
Root launcher derives new immutable runtime config image binding from the updated
receipt. Inventory, license review, and approval scope are unchanged.

28 unit tests pass; shell syntax and Python compilation pass; pvg verify scans
the changed Python test with zero issues (shell script checked separately).
Mandatory real baseline proof remains outstanding; story not delivered.
