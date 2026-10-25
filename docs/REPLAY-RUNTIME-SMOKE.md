# GRRR-w1lt: C001 runtime-lifecycle-only smoke

Status: the reviewed **e0dfaf33d3b2725a2fad63401d2b717a8365e0a6** package was
installed; sanitized runtime preflight, parent provisioning and the one-shot
offline C001 runtime-lifecycle smoke succeeded. GRRR-w1lt was delivered, then
PM-rejected solely for stale documentation; this document is the rejection
rework, submitted for redelivery, not acceptance. No further root/QEMU/VM
execution is authorized or needed for this documentation-only rework. Do not
rerun `--prepare` or `--runtime-smoke`, reset the namespace, or reuse approval.

Canonical live evidence: [LIVE-REPORT.md](evidence/replay-prerequisites/runtime-smoke-live/LIVE-REPORT.md)
and its checksummed copies. Earlier base preparation remains immutable under
`evidence/replay-prerequisites/live-install/`. Parent-reported protected access
observations are distinguished from worker read-only copy verification there.

## Completed live prerequisite result

- Parent lifecycle completed in **24.019100959s**, evaluator_succeeded=true,
  children_ceased=true, exit_codes=[-15,0]. Offline C001 transport completed with
  exit0, forced=false and error=null; supervisor unchanged, guest UID/GID1000,
  no guest supplementary groups/capabilities, NoNewPrivs=1.
- Parent UID/access probes passed: evaluator own policy readable; runner denied
  evaluator/private, evaluator denied private/runner scratch, operator denied
  evaluator; runner scratch usable. Root plan truncation attempts were denied
  with unchanged hash; no service/QEMU processes remained. Repeat invocation
  refused the existing namespace, proving the one-shot boundary.
- Budget halted=0, one reservation settled at **0 USD / 22,823,014us**; ledger
  reserved/transport/settled and object/raw hashes verified from read-only copies.
  Reviewed recovery preserved the failed d89cec7 attempt by atomic rename with
  unchanged inventory; failure and successful-run evidence remain separate.
- All five prerequisite ACs have delivery proof. Independent replay, verdict,
  ReplayReceipt and admission were neither implemented nor claimed by this smoke.

## Narrow authority

Exactly one `GRRR-VC-C001` execution was authorized and completed, labeled
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

The reviewed parent installation archived the previous launcher/package/review
and installed the e0dfaf3 root-owned read-only launcher at
`/Library/GRRR/bootstrap/replay-root-prepare` and **exactly the 12 CODE members**
in that script at `/Library/GRRR/replay-package`. CODE pins are executable checks,
not suggestions; no extras/symlinks/ACLs or writable ancestors are permitted.
Do not replace the historical base namespace's nine-file code snapshot. Inputs
remain the exact previously reviewed 14-file corpus/VM/source/policy inventory;
the separate installation review record binds e0dfaf3. Preserve all old evidence.

Launcher SHA256: `aa48f31bfca3f38c6e4792a685574bb09437fdef9b2f41d38813d7ad189bc698`.
Changed CODE pins:

| Member | SHA256 |
|---|---|
| replay_smoke.py | 2b388ac81f6e4ff5a5cbf48c80ec5c5ac9c9f39931fe77ba3e0fbccc01b7bebb |
| replay_prerequisites.py | 0c283e17ec34e4b0dad033ecfc04ba9e23b3ae39006dd242c6df4a3551845384 |
| corpus_execution.py | 9613c1874502f7204ab3546bb4a8d20230f2431bad20583cda4b39b7c1ad84f4 |
| budget.py (added closure member) | 8fffe1390b4094c6519cc4d37e83774aa6eb5c9402b5e3f2a40f748d320de5ab |
| ledger.py (added closure member) | 90dc7b0d33cdb2b7eab6854d0a2237939ba2b9f9c75cc06d89e595c0a9285514 |

Root-owned `/Library/GRRR/replay-inputs/review.json` has exactly the original
review fields (`version`, `decision`, `launcher_sha256`, `python_sha256`, `code`,
`policy_sha256`, `review_reference`, `runtime_identity`,
`runtime_prelaunch_verified`, `preexec_boundary`, `preexec_environment`) plus
`smoke`. The installed decision is `approved-replay-runtime-smoke`, version integer1,
code is the exact 12-member CODE map, launcher hash is above, and review_reference
binds the independent review. Unchanged policy/runtime/interpreter
pins and prelaunch attestation retain their prior strict meanings. `smoke` is:

```json
{"attempts":1,"challenge":"GRRR-VC-C001","contract_admission_authorized":false,"independent_replay_authorized":false,"scope":"C001-runtime-lifecycle-only","total_seconds":480,"work_seconds":473}
```

Historical successful pre-elevation runtime audit command, preserved for the
installation contract only; **do not rerun for this rework**:

```sh
/usr/bin/env -i PATH=/usr/bin:/bin LC_ALL=C /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/bin/python3.9 -I -S -B scripts/replay-runtime-preflight
```

Historical successful **trusted-root-parent** command after review, installation
and prelaunch verification; **not current permission to execute again**:

```sh
/usr/bin/env -i PATH=/usr/bin:/bin LC_ALL=C /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/bin/python3.9 -I -S -B /Library/GRRR/bootstrap/replay-root-prepare --runtime-smoke
```

No inherited DYLD_*, PYTHON*, credentials, HOME, caller-selected runtime paths or
other variables may reach interpreter/native-loader startup. The root launcher
starts fixed runner/evaluator child commands with an equivalent explicit exec
environment `{PATH:/usr/bin:/bin, LC_ALL:C}` and isolated flags. Before dropping
root privilege, it validates pwd/getgrouplist against the exact reviewed account
vector, calls initgroups for that account, then setgid/setuid to 321 or 320.
macOS repopulates account memberships on setuid: supplementary groups are NOT
empty. Every role entry requires the exact current approved vector:

- UID 320 `_grrr_evaluator`: groups `{12,61,100,320,701}`.
- UID 321 `_grrr_runner`: groups `{12,61,100,321,701}`.

Shared groups are everyone (12), localaccounts (61), _lpoperator (100), and
com.apple.sharepoint.group.1 (701). These existing memberships are explicitly
reviewed, not silently treated as empty or harmless. No root/wheel (0), staff
(20), admin (80), operator 501, opposite service group, or any unlisted membership
is permitted. Missing groups also fail. Account changes require renewed review;
this package creates or changes no group membership. Root real/effective UID/GID
must be removed before any service entry; the parent successfully exercised the
dedicated identities and access boundaries in the recorded live run. Child
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
Parent TERM/INT handlers only record stop intent. Checkpoints occur after child
registration and during work waits; signals cannot unwind Popen between creation
and registration. Requests enter the same bounded cleanup; repeated TERM/INT is
ignored during cleanup. Observation failures or exhausted observation deadlines
never suppress the KILL phase for tracked groups. Entering SIGKILL resets
TERM-phase observation uncertainty; success still requires fresh, valid post-KILL
group-absence evidence completed within the global deadline. Persistent KILL-phase
uncertainty, malformed inventory and deadline exhaustion remain failures. This
supersedes the earlier phase-global uncertainty behavior; see the
[cessation fix evidence](evidence/accounting-recovery/REPORT.md).
An uncatchable root SIGKILL/host failure cannot provide
cessation proof and requires trusted-parent process inspection/recovery.

The installed private prepared marker is read using its actual root-owned 0400
contract, shared with its creator. The dedicated reader enforces safe ancestors,
ACL absence, no-follow/nonblocking opening, one link, a 16 KiB bound and stable
metadata across the read. Public protected_bytes remains unchanged at 0444.
Revision evidence: `evidence/replay-prerequisites/runtime-smoke-r2/`; prior smoke
evidence describes the superseded 6b90f01 package, not this corrected revision.

The d89cec7 parent attempt subsequently failed at runner identity entry before VM
readiness: parent reports exit_codes=[1], children_ceased=true, elapsed 0.128s.
Its partial state was preserved under reviewed recovery before the separately
reviewed e0dfaf3 fresh namespace succeeded. Group-vector correction tests remain
under `evidence/replay-prerequisites/runtime-smoke-r3/`; the recovery record and
successful live artifacts are under `evidence/replay-prerequisites/runtime-smoke-live/`.
No automatic retry or cleanup is authorized.

## Downstream not-run and acceptance boundary

Independent allegation replay, ReplayReceipt, verdict, contract admission,
comparison and promotion remain downstream and **not-run**. GRRR-z3w9 remains
blocked until independent PM acceptance of this prerequisite; the developer does
not accept or close it. This documentation rework closes the stale-status
rejection, not those downstream gates.

The live run proves normal offline lifecycle/settlement/cessation. Live forced
timeout/KILL fault injection is not claimed; real harmless no-guest process
regressions cover those cleanup paths. No more privileged execution is needed
or authorized for redelivery. Any future fresh runtime requires separate scope,
authorization and preserved-state recovery; the completed namespace is not reusable.
