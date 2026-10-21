# Final-prefix build complete; packaging refused before side effects

Parent authorized only a prefix change in a fresh `build-final-prefix`.
Configure, compilation and ad-hoc signing completed 2023/2023. The exact binary
SHA-256 is `616b0284fbaba079be4e2701061741eb9e9bae44e55af3980730f89497bd14f2`.
The original dynamic build and every earlier failure are preserved.
Compiled data/config/helper fallback strings now target `/Library/GRRR/qemu`,
not qemu-reviewed. The FDT-only source patch and all feature settings are unchanged.

Post-build available bytes: 16,862,679,040. Later a read-only check briefly saw
17,000,886,272, but the packaging script's own immediate check saw less than
17 GB and refused before creating any staging directory. `package-errors.txt`
is the exact failure; empty `package-receipt.json` is failed-command stdout,
not a successful receipt. No copy, install-name rewrite, or new signing ran.
The parent was notified that stable margin, not threshold equality, is needed.

## Staged code changes

- package-qemu-closure: non-root only, pinned source/FDT patch, verifies upstream
  data/entitlements against the source archive, hashes all exact closure inputs,
  copies into a fresh staging tree, rewrites IDs/load paths, deletes every RPATH,
  signs with the upstream HVF entitlement, validates absolute closure, and emits
  build/installation records. It has **not yet passed a complete packaging run**.
- verify-staged-qemu: independent read-back of inventory, immutable staging
  modes, signatures, absolute dependencies and absence of old prefix. It makes
  no root-ownership or runtime-loading claim.
- trusted_install now requires exact `/Library/GRRR/qemu` and rejects every
  unlisted file, symlink, mutable directory or extra config/module artifact.
- provisioner targets that same exact root.
- trusted executor disables user config with `-no-user-config` and explicitly
  pins LANG/LC_ALL=C (gettext locale lookup disabled). Existing -L pins data;
  modules/plugins remain compiled out, networking disabled, environment minimal.
  These host-code changes require renewed independent review.

New host inventory:
`7e887f77bfc1a57f1a4fa26cb95c72e5567836ce98fb08553ae02e6a19744a97`.
Provisioner:
`206df1f4aead529be79dc2f89fd3089f0f0b616422797a7f3e8e4054ec913c49`.
Bootstrap and v3 guest artifacts unchanged.

Both Python unit suites pass 84/84; both py_compile checks passed.
Explicit pvg verify recognized three Python files with zero issues; extensionless
scripts additionally received Python compilation/shell syntax checks.

Final transformed package/installation/composed execution hashes remain absent.
Accounting reconciliation is independently incomplete. No root install or QEMU/
guest execution happened; no execution approval is requested. Claim retained.
