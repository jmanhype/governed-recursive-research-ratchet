# Explicit FDT include/link path retry — failed closed

Parent authorized one fresh-directory retry with the exact dtc 1.8.1 paths.
`build-fdt-paths` added:
`--extra-cflags=-I/opt/homebrew/Cellar/dtc/1.8.1/include` and
`--extra-ldflags=-L/opt/homebrew/Cellar/dtc/1.8.1/lib`.
All other static/minimal/no-module/no-plugin flags remained unchanged.

Configure again returned exit 1 at meson.build:2048:
`C prefer_static library 'fdt' not found`.
The include argument appears in actual compiler probe commands. There is no
successful FDT link probe or static archive selection in the log; no claim of
selecting the hashed archive is made. Full logs are retained and previous
directories untouched. The script now requires the exact archive pathname in
Meson logs before any target build, but that check was never reached.

Parent was informed. The next investigation must distinguish Meson's compiler
library search mechanism from QEMU's extra link arguments; simply repeating
the same flags is not a remedy. No further retry occurred.

No QEMU target compilation/execution, immutable closure, installation, or
execution request. Shell syntax and whitespace checks passed. Existing
application host inventory and v3 guest pins are unchanged.
