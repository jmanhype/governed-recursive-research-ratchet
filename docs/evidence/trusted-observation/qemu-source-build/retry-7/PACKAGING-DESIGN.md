# Dynamic minimal build: compiled, NOT packaged or installed

## Measured result

Parent authorized removing **only `--static`** because Apple's fully static
startup link fails on missing crt0.o. Fresh `build-dynamic` retained the exact
FDT-only source patch and all minimal/no-module/no-plugin feature settings.
Configure and all 2023 build steps completed, including QEMU's ad-hoc signing.
QEMU was never executed.

Binary: `.tmp-sr_pm/qemu-upstream-11.1.2/build-dynamic/qemu-system-aarch64`
35,983,056 bytes; SHA-256
`7ac7103c54eb0fc5bee2168e91b9c760999d733cae5a015aa390bc88e100a679`.
This is an intermediate build hash, not an approved final installation hash.

The script's post-build space check then exited 1:
16,970,862,592 bytes free, above 15 GB but below the conservative 17 GB
preparation threshold. Its generic preflight JSON describes the gate, not the
preceding build; the 2023/2023 log is authoritative about compilation.
No packaging copies/rewrites were attempted after this gate.

`closure-inspection.json` records every static dependency and exact input hash.
The non-system closure contains only:
- GLib 2.90.1 `libglib-2.0.0.dylib`
- gettext 1.0 `libintl.8.dylib`
- PCRE2 10.49 `libpcre2-8.0.dylib`

Their formula/receipt/SBOM/license provenance is already bound in retry-6;
dynamic bytes are independently hashed in the new closure inventory.
All load names observed are absolute. The binary has LC_RPATH for the GLib and
gettext keg paths. The dylibs have none. System dylibs/frameworks remain sealed
OS dependencies bound to build `26A428`, not files copied from Homebrew.

Undefined symbol inventory found no direct dlopen/g_module imports in these
four images. This is a useful static observation, **not proof of all runtime
loading or data lookup behavior**.

## Proposed immutable packaging (not performed)

1. Preserve original inputs. In a fresh staging directory, copy exactly the
   binary and three manifest-bound libraries, rehash before any transformations.
   No symlinks, duplicate basenames, unlisted files, or mutation of Cellar inputs.
2. Assign exact destinations:
   `/Library/GRRR/qemu/bin/qemu-system-aarch64`,
   `/Library/GRRR/qemu/lib/libglib-2.0.0.dylib`,
   `/Library/GRRR/qemu/lib/libintl.8.dylib`,
   `/Library/GRRR/qemu/lib/libpcre2-8.0.dylib`.
3. Use install_name_tool on staging copies only: set every dylib ID to its exact
   destination; change every non-system load name to the corresponding exact
   destination. Delete **every** LC_RPATH entry. Preserve system names exactly.
   Refuse unknown/tokenized/relative dependencies instead of guessing resolution.
4. Re-sign dylibs, then QEMU ad-hoc, preserving the reviewed HVF entitlement
   requirement. Record entitlement bytes, code-signature output, transformed
   hashes, transformation tool provenance and complete before/after dependency
   graphs. Signing is not execution or independent trust approval.
5. Prepare an exact bounded data/firmware inventory from the pinned upstream
   source, with license provenance. Do not infer that every source pc-bios file
   is needed or that an empty directory suffices. The real fixed virt/direct
   kernel/ISO command's data requirements need explicit static review.
6. Parent installation only: root-owned safe ancestors, directory 0755,
   executable 0555, libraries/data/records 0444, no ACLs or links; rehash every
   installed byte and verify all ancestors. Re-inspect load commands and reject
   any surviving RPATH, mutable path, missing closure member or unknown data.
   Current operator/user-owned staging is never an executable trusted install.

## Unresolved before packaging/provisioning

- Build prefix is `/Library/GRRR/qemu-reviewed` because the authorized fallback
  changed only --static. Strings include prefix data/config/network-helper
  locations. Requested package root is `/Library/GRRR/qemu`; install_name_tool
  does not rewrite these semantic paths. A reviewed prefix/data/config decision
  is required; no blind binary string substitution is proposed.
- Existing trusted_install/provisioner accept qemu-reviewed/qemu-* conventions,
  not the exact requested `/Library/GRRR/qemu`. Updating these requires a new
  host-code inventory and independent review; they were not silently changed.
- Pinning default data/config/helper behavior and GLib/gettext locale/data
  lookups remains a separate static review obligation. The launcher's minimal
  environment and disabled network do not substitute for that review.
- Accounting reconciliation remains blocked independently.
- Final transformed package/installation/composed execution hashes are absent.

No root provisioning command is currently runnable. No execution authorization
is requested. Prior static/configure failures remain intact; host/v3 pins are
unchanged. Both Python unit suites and syntax checks were rerun; outputs are
included alongside the new inspection evidence.
