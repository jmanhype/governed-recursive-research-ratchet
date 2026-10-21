# GRRR-gu87 — security changes staged, execution request withheld

The parent reported **SECURITY_REVIEW: CHANGES_REQUIRED** against the earlier
host adapter. This document records the response, not an independent approval
of the response. Source checkpoint: `66f4ba1`, plus the subsequently committed
QEMU data-tree symlink check and evidence. No sudo/root/QEMU/guest run occurred.
The story remains claimed, in progress, and not delivered.

## Four findings and staged changes

### 1. Persistent accounting lifecycle

`research/persistent_budget.py` requires the root-controlled, read-only binding
`/Library/GRRR/accounting/active.json`. It identifies exactly one campaign/store,
the database device/inode, a reviewed prior-history receipt, and all three
profiles (`synthetic`, `offline`, `trusted-observation`). The data directory is
private UID 320 beneath a root-controlled namespace.

There is no initialization, reset, missing-state fallback, or automatic schema
repair in this adapter. Existing database identity, integrity, journal mode,
stop row, stages, resource vectors and settled meter receipts are checked.
Opening an absent store cannot create a fresh allowance. A changed store inode
or history identity fails closed. SQLite reservations remain serialized across
connections; POC/milestone totals include every profile and outstanding hold.

Synthetic evaluator and offline preflight reservation paths now use this same
store. Offline observations conservatively retain their full reservations until
a complete offline meter adapter is separately reviewed; missing cost is not
zero. VM resources/guest command profiles did not change. Legacy launcher changes
only copy the additional accounting modules. Their older host execution designs
are **not newly certified by this work**.

The new root launcher also holds a separate root-owned campaign `launch.lock`
through its run, rejecting a second hardened launcher. Prior persisted stops
block it before service/guest effects. The mandatory watchdog control leaves a
persistent stop. The deliberate SQLITE_FULL test uses an isolated actual
UID-320 fixture, never fills the campaign's real accounting database.

**Missing:** the protected binding/database, reviewed migration of prior accepted
profile costs/holds/stops, and actual UID-320 lifecycle proof. No initialization
tool or root state was run or fabricated. This absence blocks execution.

### 2. Pre-authentication and control availability

`research/trusted_transport.py` authenticates kernel peer UID **before reading
payload bytes or consuming a request worker**. Data and control use separate
Unix sockets, listener loops and worker pools. Data request reads have a 1-second
absolute deadline and 3 MiB cap; control reads have a 250 ms absolute deadline
and 4096-byte cap. Dispatch is rejected on the control channel and stop/status
are rejected on the data channel.

Nonprivileged tests use actual Unix sockets and kernel peer credentials, not a
mock transport. They exercise 24 unauthorized peers sending no payload, 24 idle
authenticated data peers while a separate control stop succeeds within 2 s,
initial-read expiry, and wrong-channel actions.

The actual-identity/guest suite additionally stages 16 idle data peers while
stopping a real VM, checks acknowledgement/cessation, and runs pre-authentication
denials as actual operator/runner UIDs. **That privileged test is not run.**
The socket-only test does not prove guest cessation or resistance to unlimited
host-wide resource exhaustion.

### 3. Immutable executable and dependency binding

The trusted executor no longer hashes and then executes the Homebrew path.
`research/trusted_install.py` requires a separately reviewed installation under
`/Library/GRRR/qemu-*`. The executable, Mach-O dependency closure, build record,
firmware/data files and every ancestor must be root-controlled, nonsymlinked,
without writable group/world modes or ACL grants. Files must be read-only and
single-link. Data-tree symlinks/uninventoried files are rejected.

Mach-O load commands are parsed without executing QEMU. Non-system dependencies
must resolve uniquely inside the reviewed inventory; mutable or unsupported
search paths, embedded dyld environment commands and non-system dynamic linkers
are rejected. Sealed system dependencies are bound to the actual macOS build.
A reviewed build record must bind QEMU 11.1.2, its source/executable, fixed root
prefix, and disabled module/plugin build options. QEMU receives `-L` pointing
only to the reviewed data directory. The service environment has no inherited
DYLD variables.

**Missing:** a real reviewed immutable installation, its build/runtime-load-path
audit and manifest. Static Mach-O parsing is not proof of all possible runtime
`dlopen` behavior; the installation review must establish that closure, including
third-party module defaults. No installation hash or successful tamper denial
against a real root installation is claimed. Actual write/replacement-denial
probes are staged for the parent identity suite.

The original prepared-v3 JSON names Homebrew QEMU. It is preserved as the media
preparation identity, **not misrepresented as the hardened execution profile**.
A new composed `execution_profile` digest must bind prepared-v3, the immutable
installation, accounting binding, bootstrap/interpreter, host code and unchanged
limits. It cannot be finalized while those artifacts are absent.

### 4. Root bootstrap trust

`scripts/trusted-root-bootstrap` is standalone standard-library-only source for
an **independently reviewed and installed**, root-controlled bootstrap. It must
not be run as root from this checkout.

The intended interpreter is the canonical, root-controlled Apple CLT binary:
`/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/bin/python3.9`,
with `-I -S -B`. The bootstrap checks itself, the interpreter and standard-library
search paths before accepting source. User site packages, `.pth` processing,
PYTHONPATH, current-directory imports and bytecode writes are disabled.

The root-owned approval must bind bootstrap/interpreter hashes, the complete
host source inventory, installation, accounting and composed execution profile.
The bootstrap reads source bytes with no-follow/nonblocking file opens, checks
every approved hash, copies the entire bundle into a new immutable root snapshot,
and rehashes it **before any application import**. It then invokes only the
reviewed launcher from that snapshot. Identity children use an isolated,
root-controlled entry module and code snapshot.

Direct root execution of the checkout launcher is withdrawn and rejected by its
guard. The old `--run` instruction is not the current interface. No bootstrap was
installed and no root bootstrap or root application import was executed.

## Current pins and unavailable bindings

| Item | SHA-256 / state |
|---|---|
| Host source inventory | `f5170737b386d3f80039b40f70a6ec878ec0144d4db518d680479045498ff9e9` |
| Bootstrap source (not installed) | `615cbfab84ddce1d84b397da9b4e99d2a51c1404bfd637defcc313238512ed9f` |
| Canonical Apple CLT Python binary | `5c5950c62eee5fd227a67e4bdfcde81c9add59799bba0949635f3d5ba9661c26` |
| v3 supervisor, unchanged | `a9a0fd9a8471bc1859e5ab91c3746a139942562f719784fec51b8254eb8307d6` |
| v3 detached ISO, unchanged | `799ec744f27e7329686e5acb8a3e1f663c82a321f7bc1d4bc940ea5c97068233` |
| v3 media/preparation profile, unchanged | `3edebcd4b85ae7ce666d953bd3c5527606a7043c42294a0f60000875f8d2eec0` |
| v3 preparation receipt, unchanged | `775a767ca74f9c18678fc998111b0c9870df1a68db68e453b6af0c50ae9d6c0c` |
| Immutable QEMU installation approval | **absent / null** |
| Persistent accounting binding/migration | **absent / null** |
| New composed execution profile | **unavailable / null** |
| Execution authorization | **absent** |

All original resource limits remain: 1024 MiB RAM, 1 vCPU, 512 MiB `/work`,
30 s boot, 240 s command, 300 s total, 2 s stop target, 5 s TERM grace,
2 s kill wait, 1 MiB guest output, 3 MiB wire, 15 GB free-space floor.
Host UIDs 320/321; guest supervisor 0, candidate 1000:1000. Network, shares and
paid dispatch remain disabled. The separate accepted synthetic 512 MiB and
offline 1024 MiB profiles retain their existing VM resource settings.

Latest read-only capacity measurement: **16,108,326,912 bytes free**. This worker
did no cleanup. Meeting the floor does not resolve missing trust prerequisites.

## Measured verification

Evidence: `docs/evidence/trusted-observation/security-wip/`.

- System Python 3.9.6 with `-I -S -B`: **76/76 unit tests pass**.
- Homebrew Python unit suite: **76/76 pass**.
- Real socket tests are among those tests; accounting unit tests explicitly
  substitute only their local UID constants. They are not actual UID-320 proof.
- A separate real process fails to acquire the held launcher lock; no simulated
  flock implementation is used. This is not a privileged launcher run.
- Go protocol tests: pass, **90.6% statement coverage**; guest binaries/images
  were not rebuilt or run.
- Explicit-path `pvg verify --include-tests --format=text`: **15 recognized
  files, 0 issues**.
- Explicit host-source `py_compile`: exit 0. `git diff --check`: exit 0.
- Independent v3 read-back: exit 0, **7 ISO members and 52 source files**.
- Root bootstrap invoked only as actual nonroot user: exit 1 before copying,
  importing application code or starting services.
- Nonexecuting launcher dry-run: exit 1 on absent root installation manifest,
  no fallback and no guest/service start.
- Mandatory suite: **10 required, 0 executed, 0 skipped, 1 identity setup error**.
- Python trace with missing-line denominator: transport 88%, persistent budget
  72%, installation validator 38%, executor 41%, evaluator adapter
  48%, standalone bootstrap 23%. This is partial line coverage, not branch,
  root integration or guest behavioral coverage.

The old prepared/host documentation now labels its stale statements and command
as historical. Exact former documents are exported from commits `91a7ad5` and
`d53deaf` in this evidence directory. Their old checksums apply to those committed
versions; historical manifests were not silently rewritten to bless edits.

### AC Verification

All six ACs remain incomplete end to end. Static/unit results do not demonstrate
the privileged trust setup, actual candidate isolation/race behavior, root
installation tamper rejection or guest cessation. Independent review must assess
the expanded diff and persistent cross-profile migration before any delivery.

## Exact next request — review, not execution

> Please independently re-review the four security changes at this checkpoint.
> Do not authorize or run the guest profile. If the design is accepted, identify
> the separately required provisioning-only authorization for an immutable QEMU
> 11.1.2 runtime/dependency closure, independently installed bootstrap, and
> migration of prior campaign accounting costs/holds/stops. Return their verified
> hashes and the new composed execution-profile digest for a later decision.
> No resource expansion, paid calls, host fallback, production mutation,
> automatic admission or guest execution is requested.

There is deliberately **no current AWAITING_PARENT_IDENTITY_RUN execution
command**: it would be premature while the installation/accounting/profile
bindings are null and the independent re-review has not cleared the changes.
