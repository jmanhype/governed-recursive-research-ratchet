# GRRR-w1lt: C001 runtime-lifecycle-only smoke

Status: reviewable implementation, **not installed or run**. The parent already
prepared the base namespace at 3f2658b; that evidence remains immutable under
`evidence/replay-prerequisites/live-install/`. This revision requires fresh
independent security/architecture review and parent installation. Do not rerun
`--prepare`, reset the namespace, or reuse the former review approval.

## Narrow authority

Exactly one `GRRR-VC-C001` execution is allowed, labeled
`C001-runtime-lifecycle-only`. No allegation classification, defect verification,
independent ReplayReceipt, contract admission, promotion or merge is implemented.
GRRR-z3w9 still owns those semantics. No corpus truth, supervisor, build, probe,
prepared ISO, policy bytes or corpus failure counter changes. Smoke failure is
not an independent-replay failure; the two-consecutive-failure policy is neither
consumed nor reset. One-shot failure blocks further smoke attempts even earlier.

The existing CorpusExecutor supplies the exact offline disposable VM arguments,
read-only prepared inputs, no host shares/network, one vCPU, 1024 MiB RAM,
512 MiB guest workspace, boot/output/wire caps, guest credentials and isolation
validation. Its only shared change is a spawn hook preserving corpus defaults.
Smoke overrides that hook to keep QEMU inside the parent-created runner process
group, with a private runner-owned scratch cwd and explicit credential-free env.
Root's work cutoff is 473s after starting the lifecycle clock; all groups receive
TERM concurrently (up to 5s), then KILL concurrently (up to 2s), inside 480s.
Kernel process inventory, not service exit alone, establishes cessation. Deadline
or observation failures preserve state and report failure, never success.
The accepted internal 475s executor watchdog is not claimed as the smoke bound.
The exact 16106127360-byte host floor is rechecked immediately before guest spawn.

## Installation and exact review contract

Trusted parent must archive the previous installed launcher/package/review, then
install this revision's root-owned read-only launcher at
`/Library/GRRR/bootstrap/replay-root-prepare` and **exactly the 12 CODE members**
in that script at `/Library/GRRR/replay-package`. CODE pins are executable checks,
not suggestions; no extras/symlinks/ACLs or writable ancestors are permitted.
Do not replace the historical base namespace's nine-file code snapshot. Inputs
remain the exact previously reviewed 14-file corpus/VM/source/policy inventory;
only the separate installation review record changes. Preserve all old evidence.

Launcher SHA256: `366d5e498c36008186caf736eb243f84c7cde834a10edcd4cf8a7977bfb99b8c`.
Changed CODE pins:

| Member | SHA256 |
|---|---|
| replay_smoke.py | 89c1e4e01b8d03e9c6fcaf86999662a78484334f55a5f0a52f09e537f6db84b4 |
| replay_prerequisites.py | f013d32b2cb646e9dc28859c3df6ceafb8d2fb447736d945888d5ed40878da64 |
| corpus_execution.py | 9613c1874502f7204ab3546bb4a8d20230f2431bad20583cda4b39b7c1ad84f4 |
| budget.py (added closure member) | 8fffe1390b4094c6519cc4d37e83774aa6eb5c9402b5e3f2a40f748d320de5ab |
| ledger.py (added closure member) | 90dc7b0d33cdb2b7eab6854d0a2237939ba2b9f9c75cc06d89e595c0a9285514 |

Root-owned `/Library/GRRR/replay-inputs/review.json` has exactly the original
review fields (`version`, `decision`, `launcher_sha256`, `python_sha256`, `code`,
`policy_sha256`, `review_reference`, `runtime_identity`,
`runtime_prelaunch_verified`, `preexec_boundary`, `preexec_environment`) plus
`smoke`. Set decision to `approved-replay-runtime-smoke`, version to integer 1,
code to the exact 12-member CODE map, launcher hash above, and review_reference
to the new independent review's SHA256. Unchanged policy/runtime/interpreter
pins and prelaunch attestation retain their prior strict meanings. `smoke` is:

```json
{"attempts":1,"challenge":"GRRR-VC-C001","contract_admission_authorized":false,"independent_replay_authorized":false,"scope":"C001-runtime-lifecycle-only","total_seconds":480,"work_seconds":473}
```

Before elevation run the same independently reviewed runtime audit, through the
sanitized pre-exec boundary, from the reviewed checkout:

```sh
/usr/bin/env -i PATH=/usr/bin:/bin LC_ALL=C /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/bin/python3.9 -I -S -B scripts/replay-runtime-preflight
```

After new review, installation and prelaunch verification, the **trusted root
parent only** may execute this exact fixed command:

```sh
/usr/bin/env -i PATH=/usr/bin:/bin LC_ALL=C /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/bin/python3.9 -I -S -B /Library/GRRR/bootstrap/replay-root-prepare --runtime-smoke
```

No inherited DYLD_*, PYTHON*, credentials, HOME, caller-selected runtime paths or
other variables may reach interpreter/native-loader startup. The root launcher
starts fixed runner/evaluator child commands with an equivalent explicit exec
environment `{PATH:/usr/bin:/bin, LC_ALL:C}`, isolated flags, and supplementary
groups cleared before dropping to real/effective UID/GID 321 or 320. Child
commands cannot be entered by the operator or by root pretending to be a role.
Runtime/ancestor/ACL/hash verification is not relaxed.

## Lifecycle and evidence boundaries

The root parent holds the accepted corpus lock for the entire operation,
revalidates corpus/spec/source/QEMU/runtime/account/disk/process identities and
the existing protected prepared marker, and exclusively creates
`/Library/GRRR/independent-replay/runtime-smoke`. Any existing/partial smoke
state refuses execution. Root reopens/verifies exact created inventory, bytes,
UID/GID, modes, links and ACLs before children start. Root owns code, immutable
assets/config/plan and private review/logs/lifecycle record. UID 320 exclusively
owns smoke policy, Budget reservations/metering/settlement and hash-linked
append-only Ledger. UID 321 owns scratch and authenticated executor sockets only.

The evaluator reserves 480000000 microseconds and zero USD cents before dispatch,
accepts only the fixed root run/C001 binding, stores raw transport evidence,
validates cessation and isolation (not expected corpus answers), requests stop
acknowledgment within 2s, then settles measured runtime. Unknown outcomes halt
the budget and retain its reservation. No independent-replay budget is reset or
spent. The inherited `disposable-corpus-budget` config binding is required solely
by the unchanged accepted executor schema; actual smoke accounting is the
separate evaluator-owned smoke database, never the corpus ledger.

The parent writes a private lifecycle event with all child exit codes, elapsed
time and observed group cessation. A settled evaluator record alone cannot
prove parent lifecycle completion; both records and live UID/asset/ledger probes
must be reviewed. Failure paths retain logs, reservations and partial state.
Nothing automatically retries or removes failed state.
Parent TERM/INT requests enter the same bounded cleanup; repeated TERM/INT is
ignored during cleanup. An uncatchable root SIGKILL/host failure cannot provide
cessation proof and requires trusted-parent process inspection/recovery.

## Still not-run

Independent review of this revision; parent installation/update and runtime
audit; root-positive smoke provisioning; actual offline C001 VM execution;
UID 320/321 ownership/access and protected asset unchanged probes for the new
subnamespace; live runtime reservation/settlement and append-only evidence;
live normal/timeout/stop/TERM/KILL and full child cessation within 480s.
AC #4 is unresolved until those parent-mediated lifecycle proofs exist.
No-guest tests are not a substitute. GRRR-w1lt remains in_progress; no delivery.
