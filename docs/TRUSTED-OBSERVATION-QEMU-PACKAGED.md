# QEMU closure packaged — provisioning only, never executed

## Verified staging result

The immediate packaging space check passed (17,096,044,544 bytes). Packaging
completed without executing QEMU. Independent read-back under both Python
installations verified **191 files**, including **185 data/license files**.

Staging:
`.tmp-sr_pm/qemu-upstream-11.1.2/staged-qemu`

| Artifact | SHA-256 |
|---|---|
| Installation manifest | `e40888d8d14bc9c2b8db38d8468bc53fdbf77421b284d9eacbbce1d37818b625` |
| Transformed/signed QEMU | `352108bbc46171ed74ee3ef0b74ac1f32403c7e076ebac623ce2c265724699da` |
| GLib | `d079259cc233208c80938170c06a4734d4d0d4ac8be75f5bb1df322c52bffe7b` |
| gettext | `925b627b3cd7b6334aaad8c54e9f182563c5fda7c19daf99d0a106d1c08e0d75` |
| PCRE2 | `6adc5f7e794acfc9f82c7b74f1b4a854f3f30ea8650ddce457f25643fd6d9957` |

Every non-system load path and dylib ID now targets exact
`/Library/GRRR/qemu/lib/...`. Every LC_RPATH was removed. All four signatures
verify; QEMU retains only the reviewed upstream Hypervisor entitlement.
System libraries/frameworks remain OS-owned and bound to OS build `26A428`.
Staging is user-owned, **not an installed root-controlled runtime**.

Dynamic linkage was necessary because the fully static build failed at Apple's
missing crt0.o. Both source builds, the minimal FDT-only patch, prior failures,
source/tag/license/static-input provenance and before-transformation hashes
remain committed. The final-prefix binary was rebuilt, never string-shortened.

## Data/module/config boundary

- CONFIG_MODULES and CONFIG_PLUGIN are undefined; build records require explicit
  disable flags. No module directory/library or plugin interface is enabled.
- All upstream pc-bios regular files were compared against the pinned official
  archive before copying; two QEMU license files were added. Manifest binds each
  byte. Source files/compressed firmware included in this bounded tree are not
  permission to select another firmware/profile.
- Fixed `-L /Library/GRRR/qemu/data` selects the protected data tree. Default
  firmware/config/helper fallbacks are compiled under `/Library/GRRR/qemu`;
  historical qemu-reviewed prefix bytes are absent.
- Host launch disables user config, fixes LANG/LC_ALL=C, has minimal environment,
  disables networking and accepts no arbitrary candidate arguments. Thus config,
  locale, and network-helper defaults cannot become candidate-controlled inputs.
- Full installed-tree inventory rejects extra config/data/module files or links.
  Root directories must have safe ownership/modes/ACLs. Missing optional default
  data paths stay inside the protected prefix and fail rather than falling back
  to an operator-controlled Homebrew path.
- Static symbol inspection found no direct dlopen/g_module imports in the four
  images. This does **not** prove OS-framework internals or runtime correctness.
  Runtime loading and guest execution remain untested and unauthorized here.

## Exact parent-only provisioning boundary

New QEMU-only mode explicitly excludes all accounting fields and returns before
touching `/Library/GRRR/accounting`. It installs the reviewed source snapshot,
bootstrap and QEMU closure, statically verifies installed bytes/ownership, and
records `accounting_touched:false`, `execution_authorized:false`.
No allowance or execution-profile digest is created.

Proposed plan:
`docs/evidence/trusted-observation/qemu-package/provisioning-plan.json`

Plan SHA-256:
`d1bf4b297c3d31f48e494abfb3c1bd9456d438b8f4e328d62787841e0aaf0fcd`

Provisioner SHA-256:
`f6190845f01c4935759e03dcc1df0a04bb2ce56986ecf439c972fefd1dbbe1df`

Host inventory:
`7e887f77bfc1a57f1a4fa26cb95c72e5567836ce98fb08553ae02e6a19744a97`

Bootstrap unchanged:
`615cbfab84ddce1d84b397da9b4e99d2a51c1404bfd637defcc313238512ed9f`

AWAITING_PARENT_IDENTITY_RUN

After independent security review of the new installer and exact plan, the parent
must independently create/verify root-owned 0755 `/Library/GRRR/bootstrap` with
safe ancestors and no ACLs. `/Library/GRRR` was absent at this checkpoint; refuse
unexpected existing state rather than overwrite it. Using standard system copy/
install tools (not executing checkout code), install:

- reviewed `scripts/provision-trusted-host` as root:wheel 0444 at
  `/Library/GRRR/bootstrap/provision-trusted-host`;
- exact plan bytes as root:wheel 0444 at
  `/Library/GRRR/bootstrap/qemu-provisioning-plan.json`.

Read back both hashes above and verify the canonical interpreter hash
`5c5950c62eee5fd227a67e4bdfcde81c9add59799bba0949635f3d5ba9661c26`,
version 3.9.6, root ownership, safe ancestors and standard-library origins.
Do not execute the mutable checkout script as root.

Then the exact **provisioning-only** command is:

```text
/usr/bin/env -i PATH=/usr/bin:/bin LC_ALL=C /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/bin/python3.9 -I -S -B /Library/GRRR/bootstrap/provision-trusted-host /Library/GRRR/bootstrap/qemu-provisioning-plan.json d1bf4b297c3d31f48e494abfb3c1bd9456d438b8f4e328d62787841e0aaf0fcd
```

Expected output record:
`/Library/GRRR/bootstrap/qemu-provisioning-readback.json`.
The command does not launch QEMU or guest controls. Existing inconsistent files,
source/hash drift, unsafe ancestors/ACLs, extra files, missing libraries, any
RPATH or space below the 15 GB installation floor fail closed.

## Remaining work / checks

Both Python unit suites: **85/85**, both staging read-backs: pass. Both Python
syntax checks pass; explicit pvg checks pass (three recognized Python files).
Evidence lives in `docs/evidence/trusted-observation/qemu-package/`.

Independent review and parent root installation are pending. Persistent accounting
reconciliation, installed service-identity checks, final composed execution
binding and all ten guest controls remain blocked/not-run. v3 guest pins remain
unchanged. No root/install/QEMU execution was performed by this worker; no
execution approval is requested and the story is not delivered.
