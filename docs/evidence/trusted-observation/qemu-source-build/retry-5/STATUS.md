# Minimal Meson search probe — failed before QEMU retry

Exact environment: LIBRARY_PATH=/opt/homebrew/Cellar/dtc/1.8.1/lib and
CPATH=/opt/homebrew/Cellar/dtc/1.8.1/include. The independent Meson 1.11.1 probe
calls `cc.find_library('fdt', static: true, required: true)`.
It returned exit 1: `C static library 'fdt' not found`. Therefore no new QEMU
configure/build was attempted; the parent's prerequisite was not satisfied.

Diagnosis from the pinned bundled Meson source:
`compilers/mixins/clike.py::_find_library_real` enumerates explicit `extra_dirs`
plus `get_library_dirs` for static libraries. The latter uses compiler
`--print-search-dirs`. Apple clang 17 reports only its resource library directory
even with LIBRARY_PATH set. CPATH affects headers, not that directory list.
Earlier QEMU extra link flags likewise did not supply find_library extra_dirs.
The real compiler output and full minimal-probe log are preserved.

A possible separately reviewed correction is a tiny explicit QEMU source patch
adding the pinned `dirs` and `static: true` arguments to its FDT lookup, with
patch provenance/hash. No such patch or compiler-wrapper spoof was applied.
No target execution, root installation, guest run or execution request occurred.
