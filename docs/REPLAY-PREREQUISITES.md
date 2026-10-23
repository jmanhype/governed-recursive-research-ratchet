# GRRR-w1lt replay prerequisite package — independent review required

## Status and authority

This is a reviewable prerequisite package with an executable root-only namespace
preparer, **not an installed replay launcher**.
The operator approved GRRR-w1lt at 2026-10-23T19:15:39Z. The canonical
`replay-policy-v1.json` preserves that exact bounded authorization.
SHA-256: `355e6f7d9dd0a65817cdc1a6421fba6347f5075c40f4a456ed601e753f14a77a`.
The byte pin makes edits fail closed; it does not make a writable checkout
root-trusted. Install only independently reviewed bytes in root-owned 0444
single-link files under safe, ACL-free ancestors.

No root operation, identity change, QEMU invocation, VM, installation, replay,
or /Library/GRRR mutation was performed by this package. No independent
ReplayReceipt exists. Corpus fixture ledgers remain corpus fixture ledgers.
GRRR-z3w9 remains blocked until this prerequisite is accepted, and real
replay must additionally pass the live gates below.

## Implemented, read-only preparation

`python3 scripts/replay-prerequisites --check-package` checks exact policy and
accepted corpus/spec/source bindings from actual files. Exit zero means only
package byte validation; output explicitly denies execution authority.

`python3 scripts/replay-prerequisites --protected-preflight CORPUS VM SOURCE_ARCHIVE POLICY`
inspects a future protected installation. It checks exact immutable assets,
QEMU closure (including build/system identity), VM hashes, v2.2 input/profile,
source archive, full frozen corpus/spec hashes, UID separation, existing
corpus/replay launch lock availability, process absence and disk headroom.
It neither creates the lock nor writes any protected file. Even a valid
snapshot exits nonzero: independent review and installation are still required.
A snapshot is not a lease or authorization and cannot be reused for dispatch.

The root checkout guard executes before importing checkout modules and refuses
real or effective UID 0. Unsupported provisioning/dispatch modes fail closed.
The separate `scripts/replay-root-prepare` is the only effectful entrypoint.
It refuses non-root before inspecting inputs, imports only a hash-pinned,
independently reviewed root-owned closure, repeats preflight under the parent
lock and exclusively constructs the UID-separated namespace. It never starts
services or QEMU. Budget/reservations/ledger genesis files explicitly say
`uninitialized` and `dispatch_enabled: false`; they are not replay receipts.

The approved floor is **15 GiB = 16106127360 bytes**, not the older corpus
executor's 15000000000 bytes. Paid-cost allowance is zero, derived directly
from the paid-dispatch denial; no paid or aggregate campaign authority is added.
The 480-second total watchdog is inclusive of cleanup; the future implementation
must reserve the 5-second TERM plus 2-second KILL interval inside that bound.
No existing corpus transport timer is silently relabeled as a replay watchdog.

## Root-owned launcher design (namespace preparation implemented; not live-proven)

The namespace preparer implements steps 1–4 below. Service/VM lifecycle steps
5–7 remain the downstream design, not claimed execution. This is not permission
to execute checkout code as root.

1. A trusted parent first runs the mandatory unprivileged runtime audit below,
   before elevation; only then installs an isolated, dependency-pinned launcher and Python
   interpreter under /Library/GRRR/bootstrap after reviewing exact hashes.
   Root entry requires real/effective UID 0, isolated/no-site/no-bytecode flags,
   canonical registered installation location, and root-owned ACL-free,
   non-writable, no-link ancestors for interpreter, launcher, import closure,
   policy and review record. Refuse non-root before opening runtime state.
   A review record binds policy hash, complete code inventory, interpreter,
   QEMU/VM/source/corpus/spec identities and reviewer approval; a checkout
   hash, caller-supplied decision or corpus approval is not a substitute.

2. Acquire the existing root-owned corpus/replay lock using O_NOFOLLOW and
   nonblocking flock; hold it until all child processes have ceased. Recheck
   process inventory for UID 320/321 and every QEMU process, all protected
   assets, disk space, dedicated nonlogin accounts and safe ancestors under
   that lock. Any stale process, held lock, malformed/inaccessible record,
   symlink/ACL, unexpected asset, or partial namespace blocks before mkdir,
   chown, file copy, service start or guest dispatch. This design does not
   authorize creating identities; missing identities require parent review.

3. Exclusively create /Library/GRRR/independent-replay under root's safe
   directory, mode 0711, with no exist_ok and no automatic reuse. Refuse
   complete, partial, and dangling-link state. Root owns immutable assets,
   code and private failure/recovery records (0700 directory, 0600 logs).
   Evaluator subtree is UID/GID 320 mode 0700: policy, expectations, budget,
   reservations and append-only ledger are evaluator-owned. Runner UID/GID
   321 owns only approved executor runtime/scratch; it cannot read evaluator
   state or private logs. Installed executor code/config remains root-owned
   read-only. IPC uses authenticated UID checks and separate control channel;
   never grant runner ledger, policy or expectation authority.

4. Copy only enumerated, hash-bound input assets; reopen and verify every created
   object against the locally built exact inventory (UID, GID, mode, no links,
   no ACLs, file bytes). Refuse extra/missing objects. Verify the pending marker
   with all other objects before renaming it to prepared.json, then recheck the
   final namespace. Failure retains partial state and never returns success.
   Never copy environment, operator
   HOME, credentials, raw private logs or protected truth into runner/guest
   inputs. Preserve failed staging outside runner control. Do not automatically
   clean or reset partial state; recovery needs independent review. Successful
   staging is not replay completion.

5. Drop supplementary groups, then GID/UID for each service. The runner uses a
   fresh disposable offline VM per replay with the pinned QEMU executable and
   explicit -no-user-config, -net none, -monitor none, -snapshot, fixed
   read-only disk inputs, 1 vCPU, 1024 MiB RAM and 512 MiB guest workspace.
   No virtfs, 9p, virtiofs, networking, host directory mount, inherited
   credentials, shell-expanded candidate command, host candidate execution,
   or arbitrary QEMU arguments. Require observed guest isolation/reset
   before accepting output. Transport enforces 1 MiB captured/3 MiB wire caps,
   45-second boot and 480-second total bound including cessation.

6. Evaluator reserves bounded runtime before dispatch. Stop acknowledgement
   must arrive within 2 seconds; TERM grace is 5 seconds; KILL wait 2 seconds.
   Failure to prove cessation fences the run, retains private evidence and
   requires recovery; never free/reuse an uncertain reservation. Exactly two
   consecutive independent replay failures stop further replay dispatch;
   a success resets that consecutive counter. Persist the counter under UID
   320, not in runner memory. Accounting/verdict/ReplayReceipt logic belongs
   to GRRR-z3w9 and is deliberately not implemented here.

7. Root preserves process status, bounded private logs and failure/recovery
   evidence outside candidate control. Export only approved sanitized hashes
   and status; never return raw private logs, credentials or protected truth.
   On every exit, prove child cessation before releasing the lock. A runtime
   is never accepted merely because the launcher exited zero.

## Required review and live proof, still not-run

- Independent review of the exact package and eventual installed code closure.
- Review the executable namespace preparer; implement/review service dispatch
  separately before any replay (no dispatch mode exists in this package).
- Parent-mediated root installation, ownership/mode/ACL verification and
  positive provisioning test on a truly fresh namespace.
- Actual UID 321 and operator denial probes against evaluator-owned assets;
  positive UID 320 access, authenticated IPC and bounded lifecycle proof.
- Actual lock-contention, active-process, disk-floor and recovery controls
  under the parent lock; no simulated pass substitutes for this proof.
- Offline guest replay, resource bounds and observed cessation.
- GRRR-z3w9 independent ReplayReceipt/verdict tests.

## No-guest proof boundary

Tests use real on-disk corpus bytes, tampered copies, paths/symlinks and CLI
subprocesses without mocks, skips, environment gates or identity substitution.
The process parser's synthetic byte cases are unit tests, not a live process
absence proof. Protected positive provisioning/dispatch tests are not collected
in this suite and are explicitly not-run, never skipped-green. Package tests
cannot establish UID separation or root installation correctness.

The existing corpus root-bootstrap and identity launcher supply accepted
patterns, not replay authority. Reuse their protected-file checks, QEMU closure
verifier and authenticated IPC; do not reuse corpus approval, ledger, budget or
claim independent replay from corpus fixture execution.

## Exact future parent command and installation contract

After independent review, but BEFORE any root interpreter launch, run as the
unprivileged parent from the reviewed checkout:

```sh
/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/bin/python3.9 -I -S -B scripts/replay-runtime-preflight
```

The exact runtime identity is
`59073b8282cb4333c7719d4eac417c061c82f534bf11873d26bf2b26f7531526`.
It pins the direct non-symlink executable, Python3 framework, entire stdlib/native
module inventory, safe ancestors, modes/ownership/ACL absence and OS build for
sealed-system dependencies. The two config-3.9-darwin development symlinks are
recorded exactly but never followed as import or executable paths. Every actual
runtime entrypoint/import path is non-symlink. Extra zip/venv inputs are denied.
The full audited inventory is in the evidence directory.

The parent must review this audit code and observed receipt before elevation,
and record that independent prelaunch check in the root-owned review record.
Runtime bytes are root-controlled across this boundary; a privileged concurrent
change invalidates the audit and requires repeating it. Python cannot establish
trust in its own already-loaded stdlib retroactively. The root-side repeat is
defense in depth, not a replacement for this mandatory prelaunch phase.

After successful prelaunch audit AND trusted parent installation only:

```sh
/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/bin/python3.9 -I -S -B /Library/GRRR/bootstrap/replay-root-prepare --prepare
```

Do not run this from the checkout. The parent must independently install the
script as root-owned 0444 and the exact nine `CODE` members listed in it under
`/Library/GRRR/replay-package` (no extra files). Existing accepted root assets
are read-only; no corpus installation is overwritten. Parent-reviewed inputs
under `/Library/GRRR/replay-inputs` are `corpus/` (full frozen corpus), `vm/`
(ISO and boot assets), `source.tar` (pinned archive), `policy.json` (exact policy
bytes), and `review.json`. All paths/ancestors must satisfy the protected checks.

The root-owned canonical review record must contain exactly `version: 1`,
`decision: approved-replay-prerequisite-installation`, `launcher_sha256`,
`python_sha256` (actual direct executable), `code` (exact hard-coded inventory),
`policy_sha256`, `runtime_identity` (the exact pin above),
`runtime_prelaunch_verified: true` (independent parent's pre-elevation attestation), and
`review_reference` (SHA-256 of independent review evidence). No such record is
manufactured by this package. Missing review/inputs fail before mutation.
The review pin is separate from the operator's policy approval.

The preparer creates no account, grants no dispatch authority and launches no
guest. A partial namespace is retained and blocks retries; only parent-reviewed
recovery may handle it. Private preflight/review/prepared records stay root-only;
the namespace and preserved inputs remain available for downstream review.

Destination verification tests exercise real user-owned files, UID/GID/mode
mismatches, modified expected bytes, extra members, symlinks, hardlinks and actual
macOS ACLs. They do not substitute for mandatory root-positive creation or actual
UID 320/321 access-denial probes. Those probes remain not-run and required before
any dispatch. No permission checks were weakened to accommodate the former
`/usr/bin/python3` Xcode symlink entrypoint; that command is withdrawn.
