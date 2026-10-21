# Explicit required FDT retry — failed closed

Parent authorized enabling only required FDT and using existing dtc 1.8.1.
Archive, all three public headers, pkg-config record, formula, receipt and SBOM
hashes are in `fdt-provenance.txt`. Header SPDX license is
`GPL-2.0-or-later OR BSD-2-Clause`; the formula records the same choice.

Fresh directory: `.tmp-sr_pm/qemu-upstream-11.1.2/build-fdt`.
Added only `--enable-fdt=system`; static/no-module/no-plugin and all other
minimal feature settings were retained. Configure returned exit 1:

`meson.build:2048:11: ERROR: C prefer_static library 'fdt' not found`

Source inspection at meson.build:2048 confirms compiler.find_library is used
directly, not pkg-config. The pinned archive exists but its keg include/library
paths were not explicit compiler paths. Parent was informed; no further retry
or dependency fallback was attempted. Prior failure directory/logs remain intact.

No QEMU target compilation/execution or root installation occurred. Compiler
configuration probes are not represented as target execution. Binary/closure
hashes remain absent. Static shell syntax and git diff whitespace checks passed.
The next bounded correction would explicitly bind the reviewed dtc keg paths;
it is not implemented or run in this checkpoint.
