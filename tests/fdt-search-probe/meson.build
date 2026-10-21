project('pinned-fdt-search-probe', 'c')
cc = meson.get_compiler('c')
fdt = cc.find_library('fdt', static: true, required: true)
assert(cc.links('''
#include <libfdt.h>
int main(void) { fdt_find_max_phandle(0, 0); return 0; }
''', dependencies: fdt), 'Pinned static FDT must link')
# Only a compiler/link probe, never execute the generated program.
