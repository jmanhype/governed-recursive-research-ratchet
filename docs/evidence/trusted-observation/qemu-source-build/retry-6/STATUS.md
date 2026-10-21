# Authorized FDT-only patch succeeded; final fully-static link failed

The sole source change is the recorded unified diff adding pinned dtc `dirs`
and `static: true` to the FDT lookup. Rationale: Meson/Apple clang does not
enumerate LIBRARY_PATH for static find_library. No other dependency/feature/
target/module/plugin/security setting changed.

meson.build before SHA-256:
`7d45b715ca8e740d787eee6d4a1e8ae4a7456aecfe16dda2a7d32a0f2cc10591`
after:
`7222d581694f1022ba6ab661907af6abf552243e80c9725cc4a7a064d70df4e0`.
All recorded dtc archive/header/provenance hashes passed read-back.

Fresh build-fdt-patched configure succeeded. Meson logs record link probes using
exact `/opt/homebrew/Cellar/dtc/1.8.1/lib/libfdt.a`; summary says fdt system,
static build YES, HVF YES, TCG plugins NO. Modules and optional features stayed
disabled. No FDT subproject/download occurred. Target compilation reached
2022/2023, the final unsigned aarch64 system executable link, then failed:

```text
ld: library 'crt0.o' not found
clang: error: linker command failed with exit code 1
ninja: build stopped: subcommand failed.
make: *** [run-ninja] Error 1
```

The actual final link includes `-static`. No fallback removal of that flag was
attempted. MacOS fully-static startup/link requirements are the next blocker;
the operator must review any bounded policy-compliant linkage change.
Warnings also report unavailable static system z/iconv and dtc archive deployment
target 27.0 versus selected SDK deployment 15.4. These are preserved, not hidden.

Static third-party input hashes/provenance: dtc 1.8.1; glib 2.90.1
(LGPL-2.1-or-later); gettext 1.0 (formula's component-specific licensing);
pcre2 10.49 (BSD-3-Clause). Formulae/receipts/SBOM/license files are bound.
No executable/closure was produced or packaged. No QEMU was executed. Final free
space remained approximately 17.62 GB. Previous failed directories remain intact.
Host inventory/v3 guest artifacts unchanged; no installation or execution request.
