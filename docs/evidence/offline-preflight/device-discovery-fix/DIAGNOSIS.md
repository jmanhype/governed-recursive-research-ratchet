# Detached input discovery repair

The preserved parent attempt `attempt-20261020T174216Z-4fb11b30` failed closed:
2/6 tests executed, one readiness failure, zero skipped, no baseline approval.
Its test-output SHA-256 remains
`9bbb717c9bb33ea67bfea419a79f150c0f66b13eb35d45d0b3d36159722224f6`;
manifest SHA-256 remains
`61c86a32c4382896fceb19bc292326d95866d0aa50c0f85e3e56e6b99290aed6`.

The exported test output proves readiness did not become true. UID 501 cannot
read the protected runtime. The old test asserted readiness before persisting
the returned dispatch receipt, so exported evidence does not establish the
actual guest block-device assignment. The hardcoded `/dev/vda` input selection
is a concrete code defect, but attributing this attempt exclusively to that
device assignment remains an inference pending the next real run.

The adapter now scans virtio block devices, checks the kernel read-only flag,
mounts ISO9660 read-only, and verifies both the script and actual read-only
mount entry. Wrong candidates are unmounted; an unmount failure stops discovery.
Absent input cannot emit readiness. No device order, host share, or host build
fallback is accepted. The guest image remains byte-identical; its preexisting
vda read-only assertion is an additional boot-media check, not input discovery.

Failed readiness now persists the actual dispatch holder before assertion, so
future failed attempts retain serial output/termination diagnostics when the
service returns them. No privileged run was performed for this repair.

Validation: 26 unit tests passed; pvg verify passed on the three changed Python
files with zero issues; Python compilation passed. These checks do not prove
real VM behavior. Parent-mediated integration remains mandatory and the story
is not delivered.
