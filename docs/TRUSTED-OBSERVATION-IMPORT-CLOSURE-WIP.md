# GRRR-gu87 — second security re-review checkpoint

Source checkpoint `db53a47`. This is implementation evidence, not independent
security approval. No installation, provisioning, root, sudo, QEMU, or guest
execution occurred. No execution authorization is requested. Claim remains held.

## Import closure

The flattened integration entry and reused BudgetChecks module no longer derive
import paths from their location. `isolated_entry.py` is the sole runtime import
root authority: isolated Python, root-controlled directory and read-only files,
then the exact authenticated runtime code directory.

Audit of staged modules: every `research/*.py` except isolated_entry, both staged
integration modules, the budget test mixin and launch-lock probe have no sys.path
access (AST regression). The staged launcher and preparation/read-back scripts
retain repository-relative roots only in the **preserved directory structure**
of the bootstrap-authenticated `/Library/GRRR/snapshots` bundle. They are not
runtime identity targets; isolated_entry's three-target allowlist excludes them.
The standalone bootstrap imports only standard library before authenticating
and copying the complete bundle. The nonprivileged review utility is not a
privileged entrypoint. `test-story` refuses direct trusted execution and directs
callers to the approved isolated launcher.

The regression copies the actual application and integration modules into the
actual flattened layout, poisons both old ancestor locations with modules that
raise if imported, and imports the real suite in an isolated subprocess. It
asserts unchanged sys.path and every checked module's exact staged provenance.
This proves import closure without pretending to prove root-owned identity.

## Dynamic dependency closure

Every LC_RPATH is now rejected, even unused entries. Every non-system dependency
must be a normalized absolute path inside the exact immutable inventory. Tokens
`@rpath`, `@loader_path`, and `@executable_path` are forbidden. Existing full
inventory checks still reject symlinked/writable ancestors, changed bytes,
unreviewed modules/plugins/data, and OS-build drift.

Thus there is no approved search order to shadow. Negative tests create real
early shadow, writable search, symlink-search, and ambiguous repeated-directory
fixtures and reject all of them before resolution. Absolute closure and
noncanonical/tokenized paths have separate tests. No installed QEMU closure is
claimed: the required reviewed installation and its manifest remain absent.

## Evidence and outstanding gates

`docs/evidence/trusted-observation/security-rereview/` records both Python suites
(81/81 each), pvg verification (12 recognized files, zero issues), Go coverage,
trace coverage, host inventory and unchanged v3 media read-back. Both Python
installations also completed explicit py_compile checks with exit zero.
The evidence manifest binds these outputs.

Host inventory: `742625e1254dc50a41642508e3df1db6d7f1bf019079861bfbc77003dc50255a`.
Bootstrap unchanged: `615cbfab84ddce1d84b397da9b4e99d2a51c1404bfd637defcc313238512ed9f`.
Measured free bytes at inventory: 15,736,254,464. Go protocol coverage 90.6%;
Python trace line coverage: installation validator 49%, transport 88%,
persistent budget 72%. This partial coverage is not privileged execution proof.

Persistent accounting, independent control capacity, isolated bootstrap and
root-controlled execution requirements are preserved. The reviewed QEMU
installation, accounting binding, bootstrap installation, composed execution
profile, and independent security approval are still missing. All ten mandatory
service/guest scenarios remain not-run; all six story ACs remain incomplete.
No delivery or admission is implied by unit success.
