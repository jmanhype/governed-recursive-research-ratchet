# Retry 1: genuine source prepared; configure gate blocked

After parent cache recovery, initial measured free space was 18,152,906,752 bytes.
Fetched official `https://download.qemu.org/qemu-11.1.2.tar.xz`, verified SHA-256
`731b5681e4bb18be313231579b8efd0296c5b015fa36dc533874b639ba838016`
against the installed formula's source pin. Upstream GitLab tag query records
annotated tag `ceaea6cb3e2a7d966f9ca97c7ebb5b88cd764dd0`, peeled commit
`4fc49f46dc95d4a27de2509e7fceb2931e91faeb`. Extracted VERSION reads 11.1.2.
This is the official release archive; no claim of a byte-identical git working
tree comparison is made. COPYING and COPYING.LIB hashes preserve license
provenance (GPL-2.0 and LGPL terms respectively; individual files may differ).

Source and archive remain in ignored `.tmp-sr_pm/qemu-upstream-11.1.2/`.
No upstream bulk is committed. `configure --help` only was run to verify supported
flags; it did not configure or compile a target, and it is not QEMU execution.

The exact staged build requests only aarch64-softmmu, static, no default optional
features, modules/plugins/module upgrades/pixman/UI/docs/tools/guest-agent/download
disabled, and HVF/TCG enabled. No installed-library inputs have yet been used by
a compiler, so no dependency closure or library-input manifest is claimed.

The pre-configure gate returned exit 1 with **16,987,373,568 bytes available**.
This is above the invariant 15 GB execution floor but **12,626,432 bytes short**
of the staged conservative 2 GB preparation headroom. This headroom is not an
operator-approved VM resource limit; it was not silently weakened to proceed.
The parent was informed of the exact distinction. Configure/build did not run.

Ninja was not found on the current PATH; Meson 1.11.1 is bundled in the verified
release. No tooling was installed or downloaded to conceal that prerequisite.
Per stop-on-failure instruction, no retry or alternative build was attempted.

Shell syntax checks passed. `pvg verify` recognized zero extensionless shell
files, so its zero-issue exit is not substantive coverage. Existing application
code/host inventory/v3 media are unchanged. No root, installation, QEMU, guest,
paid call, or execution request occurred. Binary/closure hashes remain absent;
there is no runnable parent provisioning command yet.
