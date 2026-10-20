# Base ISO9660 filename repair

Attempt attempt-20261020T181714Z-41dd85d6 reached isolation PASS but could not
open /inputs/go.tar.gz on the no-Joliet Linux mount. The old macOS/libarchive
extension-aware read-back was insufficient to verify the guest namespace.
Actual test-output SHA is
`e5867d9103ac98739bb5143cd6cdd0e48a6f1081fb0760c9dbd7289c06306cda`;
build SHA is `357ad53c03ba81de42a99ba37e3920a9ffd5a9fa2652a5c5eaf89574a2926841`.
This and the earlier prerequisite attempt are preserved unchanged.

Embedded archive is now short single-dot go.tgz. Guest paths and preparation
match. Preparation directly parses the primary ISO9660 volume descriptor and
root directory, not Joliet/Rock Ridge extensions, and reads the file extent to
verify the full pinned SHA. Actual new-image primary name is GO.TGZ, 63,827,526
bytes, exact approved Go SHA. Linux default ISO name mapping lowercases it.
The old image is rejected by this check. No guest execution was performed here.

Authorized deletion removed only go-loose-v4-preserved after recording all
15,045 file hashes and sizes (227,769,067 bytes); manifest hash
`c642ecadfe1b580f9e01361444acf7237e7107b88be14c2027f4052f740db900`.
It reclaimed insufficient space, so repack stopped before mutation. Parent then
reclaimed separately authorized Cargo caches, allowing repack above the floor.
Pre/post df and deterministic deleted-tree manifest are retained here. All pinned
archives/source and previous images/receipts remain intact, including input-v5.iso.

New image SHA: `ff523652e7f0073df3424732d924b5223dc719f1e373ad1cbe44f88194bac38a`.
New receipt SHA: `594cb1a07adc6134be81b05035c275562b558a9853eeb2b3ccb9ed39d512157a`.
Guest SHA: `79b79d5b42c974e052e4f1d771f44a590e1124872035f0105aafb2d6b6bcf1bc`.
Profile, inventory, license review and approved caps unchanged. Free bytes after
repack: 15,486,951,424. Root launcher derives updated image config from receipt.

31 unit tests pass, shell syntax/Python compilation pass, pvg verify passes on
two files. Real build proof remains outstanding; no delivery or root run here.
