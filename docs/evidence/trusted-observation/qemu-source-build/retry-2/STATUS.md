# Configure failure retained unchanged

Ninja 1.13.2 was independently installed by the parent at `/opt/homebrew/bin/ninja`;
formula/source pin `974d6b2f4eeefa25625d34da3cb36bdcebe7fbce40f4c16ac0835fd1c0cbae17`,
Apache-2.0 license. Keg executable/formula/receipt/SBOM/license hashes are recorded.

Initial free space: 18,544,795,648 bytes. Configure ran using pinned QEMU source,
bundled Meson, Apple clang 17.0.0 and Ninja 1.13.2, but returned exit 1:
`meson.build:3445: fdt disabled but required by targets aarch64-softmmu`.
No QEMU target was compiled or executed. Compiler configuration probes ran,
not QEMU. Full configure and Meson logs are retained.

Parent subsequently authorized a fresh-directory retry enabling only required
system FDT from pinned Homebrew dtc 1.8.1. This failed directory/log is not reused.
