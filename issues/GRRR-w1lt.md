---
id: GRRR-w1lt
title: "Bug: independent replay lacks approved privileged prerequisites"
status: in_progress
priority: 0
type: task
labels: [milestone-1, integration, discovered-by-developer, delivered]
parent: GRRR-2t3h
created_at: 2026-10-23T18:55:10Z
created_by: speed
updated_at: 2026-10-23T21:20:55Z
content_hash: "sha256:021c5ae9d55f19b6659be4bf78913f6284b33046d84579f85f1f231a371b33e4"
blocks: [GRRR-z3w9]
assignee: dev-GRRR-w1lt
follows: [GRRR-bnkf, GRRR-c875]
---

## Description
## Context

GRRR-z3w9 requires a fresh, evaluator-controlled, UID-separated, offline VM replay of an allegation from the accepted corpus v2.2. A developer verified the repository corpus artifacts, but no replay-specific operator policy record, replay launcher, fresh runtime, protected replay assets, or privileged parent execution path exists. A UID-501 developer must not create the required evaluator/runner identities, invoke QEMU, or mutate `/Library/GRRR`.

## Root Cause

The milestone supplied the trusted corpus execution path but deferred independent replay infrastructure and action-specific authority. The proposed two-consecutive-failure stop rule and resource limits have not been converted into an approved replay policy binding. As a result, GRRR-z3w9 is structurally ready in the dependency graph but cannot execute its mandatory no-mock integration path.

## Affected Components

- Proposed `research/replay` / replay receipt path
- Proposed `tests/integration/independent-replay`
- `scripts/test-story independent-replay`
- Evaluator UID 320 policy/expectation/budget/ledger ownership
- Runner UID 321 approved executor ownership
- Root-owned immutable QEMU, VM, source/build, corpus, and specification inputs

## Acceptance Criteria

1. An operator explicitly approves a replay-specific policy record binding corpus `GRRR-validated-corpus-v2.2-isolated`, freeze digest `dfa75ef2bf3d43fd4f750094fe643afe4f204812c0ae2426276bedb471fa8529`, source commit `129e0b3f15a3bd6af949ee47d76f6855c582ab73`, exactly two consecutive independent replay failures, and explicit numeric watchdog/termination/grace/kill/output/runtime/cost limits. The record must deny network, paid dispatch, host shares, contract admission, and promotion.
2. A reviewed, root-owned provisioning path creates a fresh disposable replay runtime with evaluator UID 320 owning policy, expectations, budget, reservations, and ledger; runner UID 321 owning only the approved executor; immutable installed QEMU/VM/source/corpus/spec identities; and verified safe ancestors, ownership, modes, and ACL-free paths.
3. Read-only preflight proves exact protected asset hashes, corpus/spec binding, disk headroom, process/lock absence, isolation controls, and identity separation before any replay dispatch.
4. The parent-mediated launcher can execute a replay without exposing credentials, protected truth, raw private logs, or host shares, and preserves all failure/recovery evidence outside candidate control.
5. GRRR-z3w9 remains blocked until this prerequisite bug is accepted; no corpus fixture ledger may be relabeled as an independent ReplayReceipt.

## Testing Requirements

- Integration tests: MANDATORY (no mocks) for provisioning/preflight/launcher behavior where authorized.
- Privileged operations require a separately recorded operator authorization and parent-mediated execution.
- Missing approval or failed preflight must produce explicit blocked/not-run evidence, never a skipped green test.

## Discovered During

Story GRRR-z3w9: developer preflight found corpus artifacts valid but replay policy/runtime prerequisites absent.

## Skills To Use

- `pvg` and `nd` for tracker state
- `architect` or security review for provisioning/runtime changes
- `vlt` only if vault tooling itself is used

## nd_contract
status: new

### evidence
- Created from the GRRR-z3w9 DISCOVERED_BUG report on 2026-10-23.

### proof
- [ ] Pending operator approval and reviewed provisioning.

## Acceptance Criteria


## Design


## Notes


## nd_contract
status: delivered

### evidence
- Transitioned via pvg story deliver on 2026-10-23.

### proof
- [ ] Developer evidence block must remain authoritative above this contract.


## Implementation Evidence

PROOF:

### CI/Test Results
Commands run:
- `/usr/bin/python3 -B docs/evidence/replay-prerequisites/runtime-smoke-live/verify-copies.py`
- `/opt/homebrew/bin/python3 -B docs/evidence/replay-prerequisites/runtime-smoke-live/verify-copies.py`
- Both required Pythons: `-B -m unittest discover -s tests -p 'unit_replay*.py'` and `-B -m unittest discover -s tests -p 'unit_*.py'` at e0dfaf3.
- `/usr/bin/python3 -B -m trace --count --missing --summary --coverdir /tmp/grrr-w1lt-delivery-coverage --module unittest discover -s tests -p 'unit_replay*.py'` at03ff000.
- `pvg verify docs/evidence/replay-prerequisites/runtime-smoke-live --format=text`
- `shasum -a 256 -c docs/evidence/replay-prerequisites/runtime-smoke-live/SHA256SUMS`
- `git diff --check`; `git diff --cached --check`.

Summary: unit PASS (32 focused /198 full on each required Python,0 failures/errors/skips); fresh trace32 PASS; copied-live-evidence verification2 PASS; checksum18 PASS; static PASS (1 file,0issues); parent live integration1 successful normal C001 lifecycle. Historic failed attempts preserved, not hidden.
Coverage: no-guest replay_prerequisites62%, replay_runtime96%, replay_smoke31%. Parent protected live execution not instrumented; no root coverage claim.

### Commit
- Branch: story/GRRR-w1lt
- SHA: 3283c0ee854d7cae2a98d5c2977c00eb0164ce8d
- Executed implementation: e0dfaf33d3b2725a2fad63401d2b717a8365e0a6

### pvg verify
VERIFY: PASSED (1 files scanned, 0 issues)

### AC Verification
| AC # | Requirement | Code Location | Test Location | Status |
|---|---|---|---|---|
| 1 | Approved exact policy/limits/denials | docs/replay-policy-v1.json | policy tests and parent unchanged hash | PASS |
| 2 | Reviewed root provisioning, UID boundaries/assets | scripts/replay-root-prepare | prior base live report and runtime-smoke-live parent probes | PASS |
| 3 | Protected exact preflight before dispatch | research/replay_prerequisites.py | parent sanitized preflight and negative tests | PASS |
| 4 | Offline parent lifecycle, no exposed protected state, retained failures | research/replay_smoke.py | live lifecycle24.019100959s, copied settled DB/hash-chain/guest evidence, ceased children | PASS |
| 5 | GRRR-z3w9 blocked until acceptance, no relabeled ReplayReceipt | unchanged tracker dependency and smoke scope | live BlockedBy=[GRRR-w1lt], all smoke authorization flagsfalse | PASS |

LEARNINGS:
- Exact group vectors and private modes must match live platform behavior.
- Preserve spawn registration before handling stop and always attempt KILL on uncertain observation.
- Parent source/access observations and worker read-only copy verification are distinct evidence.

Downstream not-run: PM acceptance, independent allegation replay/verdict/ReplayReceipt/failure sequence, contract admission/promotion. No root/QEMU/VM/protected mutation/push by worker. See preceding full PROOF and LIVE-REPORT.md for exact evidence and limitations. DISCOVERED_BUG: none unresolved in prerequisite scope.

## Implementation Evidence (DELIVERY REQUESTED)

PROOF:
- Branch story/GRRR-w1lt; final clean evidence commit 3283c0ee854d7cae2a98d5c2977c00eb0164ce8d, live-copy commit03ff00075ff1c15db7c96c99e255e6e741be9dca; parent executed implementation e0dfaf33d3b2725a2fad63401d2b717a8365e0a6.
- Report and exact copied artifacts: docs/evidence/replay-prerequisites/runtime-smoke-live/LIVE-REPORT.md and SHA256SUMS. All18 checksums pass. Copied DBs opened mode=ro&immutable=1; integrity_check ok, bytes unchanged. Worker verified budget/meter settlement, ledger hash chain, object/raw hashes, guest identity and lifecycle/recovery binding.
- Commands `/usr/bin/python3 -B docs/evidence/replay-prerequisites/runtime-smoke-live/verify-copies.py` and `/opt/homebrew/bin/python3 -B docs/evidence/replay-prerequisites/runtime-smoke-live/verify-copies.py`: 2 successful verification runs, 0 failures. Copied budget: halted0, one settled reservation, 0USD, 22823014us; ledger reserved/transport/settled; object444262c5a0457cd27c6b6ef29be3c474426707d62e2eeda458c74376c9e07a16.
- Parent root integration: 1 successful C001 runtime-lifecycle smoke, 24.019100959s, children_ceased=true, evaluator_succeeded=true, exit_codes[-15,0]. Actual offline VM transport exit0/forcedfalse/errornull/complete/ceased; raw27673bytes SHA adf82b14c9ac434e3883751e2648690b88e0324d1b55459631a4fe3fb4725bbd. Guest UID/GID1000, empty groups/caps, NoNewPrivs1, unchanged supervisor, three identical repetitions exit0. This is NOT an independent ReplayReceipt or defect verdict.
- Parent reports reviewed recovery archived failed d89cec7 by unchanged-inventory atomic rename; sanitized audit exit0, installed hashes exact, UID access/truncation denials and positive own-storage probes passed, protected hashes unchanged, no service/QEMU remained, repeat smoke refused existing namespace. Worker did not repeat privileged operations; original ownership/access observations are parent-reported, distinct from copy verification.
- Implementation e0dfaf3 tests: both required Pythons `-B -m unittest discover -s tests -p 'unit_replay*.py'`32 passed and `-B -m unittest discover -s tests -p 'unit_*.py'`198 passed each; zero failures/errors/skips, logs ../runtime-smoke-r3/.
- Fresh at03ff000: `/usr/bin/python3 -B -m trace --count --missing --summary --coverdir /tmp/grrr-w1lt-delivery-coverage --module unittest discover -s tests -p 'unit_replay*.py'`:32 passed,0failed/errors/skips. Measured no-guest coverage replay_prerequisites62%, replay_runtime96%, replay_smoke31%; root live path not instrumented, no combined/root coverage claimed. Full coverage.log committed.
- `pvg verify docs/evidence/replay-prerequisites/runtime-smoke-live --format=text`: VERIFY PASSED (1 files scanned,0issues). git diff --check and staged check passed; source code unchanged in evidence commits.

### AC Verification
| AC # | Requirement / code | Test / live evidence | Status |
|---|---|---|---|
| 1 | Canonical docs/replay-policy-v1.json exact corpus/freeze/source, two consecutive independent failures, numeric limits/denials | Recorded operator approval, policy pin and unchanged parent readback; policy mutation tests | PASS |
| 2 | Reviewed root provisioning and UID-separated runtime; scripts/replay-root-prepare, research/replay_smoke.py | Prior base live preparation plus fresh smoke namespace, parent UID/access/asset probes; root-only code and evaluator policy/expectations/accounting/ledger | PASS |
| 3 | Protected locked read-only preflight, research/replay_prerequisites.py | Parent successful exact identity/disk/process/lock/runtime preflight before actual dispatch; retained fail-closed tests | PASS |
| 4 | Parent-mediated offline launcher and preserved evidence | Successful live C001 VM/service lifecycle, guest isolation, budget/ledger read-only verification, ceased children; failed predecessor preserved | PASS |
| 5 | Downstream acceptance gate and no fixture-ledger relabeling | Live pvg issues show GRRR-z3w9 BlockedBy=[GRRR-w1lt]; no dependency removed; smoke scope denies independent replay/admission throughout | PASS |

LEARNINGS:
- Exact macOS account vectors, not empty supplementary groups, are enforceable after setuid.
- Private record consumer mode must match its creator; signal-safe registration precedes deferred stop; observation uncertainty must still attempt KILL.
- Preserve failed state and provenance separately from successful runs; copy verification does not establish original UID metadata.

### Downstream not-run gates
- Independent PM acceptance of GRRR-w1lt remains required; worker does not accept/close. GRRR-z3w9 remains blocked until acceptance.
- GRRR-z3w9 allegation replay/verdict/ReplayReceipt and consecutive-independent-failure sequence not-run; contract admission/promotion/production mutation not-run.
- Live forced-timeout/KILL fault injection not claimed; harmless real process regressions cover cleanup branches. Used namespace cannot be reused; future fresh runtime needs explicit authorization/recovery.
- No worker root/QEMU/VM, /Library mutation or push. DISCOVERED_BUG: none unresolved within prerequisite scope.

## nd_contract
status: in_progress

### evidence
- PROOF: clean commit e0dfaf33d3b2725a2fad63401d2b717a8365e0a6. Corrects live macOS account-vector rejection; no privileged action or retry by worker.
- Parent reports d89cec7 failed before runner readiness/VM execution: evaluator_succeeded=false, exit_codes=[1], children_ceased=true, elapsed0.128s. Failed runtime-smoke namespace remains preserved; worker did not mutate it.
- Read-only live pwd/getgrouplist and /usr/bin/id agree: UID320 groups {12,61,100,320,701}, UID321 groups {12,61,100,321,701}. Exact vectors pinned and recomputed before initgroups/drop and at role entry. No empty supplementary-group claim remains in current contract. Existing printer/sharepoint memberships explicitly disclosed for review; root/wheel, staff/admin, operator501, opposite-role and any other extra/missing membership rejected.
- Both /usr/bin/python3 and /opt/homebrew/bin/python3: focused unit_replay*.py 32 passed; full unit_*.py 198 passed; no skips/errors/failures. Real macOS group-data regression and nonmember tamper rejection included. pvg verify explicit paths passed (3 Python files, zero issues); diff/staged checks passed; 12 SHA256SUMS verified.
- Evidence: docs/evidence/replay-prerequisites/runtime-smoke-r3/. Updated contract docs/REPLAY-RUNTIME-SMOKE.md; launcher SHA256 aa48f31bfca3f38c6e4792a685574bb09437fdef9b2f41d38813d7ad189bc698. Future sanitized parent command unchanged.

### proof
| AC | Evidence | Status |
|---|---|---|
| #1 | Original policy and C001-only scope unchanged | New group vector needs independent review |
| #2 | Exact live account vector computed/pinned; initgroups then UID/GID drop; strict role checks | Revised parent install/drop/access probes not-run |
| #3 | Protected preflight/runtime/asset checks retained; group checks added | Updated positive preflight not-run |
| #4 | Failed attempt preserved; no-guest identity regression passed | UNRESOLVED: successful parent VM/service/accounting/stop lifecycle not-run |
| #5 | No verdict/ReplayReceipt/admission/counter mutation | GRRR-z3w9 separate |

### unresolved not-run gates
- Renewed independent review, parent archive/update installation/review and sanitized runtime audit; explicit preserved-failure recovery/fresh namespace authorization.
- Actual root UID/GID drop and access/unchanged-asset probes, offline C001 VM/service/accounting/stop/cessation lifecycle.
- No root/QEMU/VM, /Library/GRRR mutation, delivery, acceptance or push. Keep in_progress.

### LEARNINGS
- macOS setuid can repopulate directory-service membership after setgroups([]); the enforceable boundary is the exact reviewed account vector, not empty supplementary groups.

### DISCOVERED_BUG
- Live account-vector mismatch corrected here; no other finding deferred.

## nd_contract
status: in_progress

### evidence
- PROOF: clean commit d89cec7f57367fe512fe11b71f63be3098312c6e corrects all three security-review findings against 6b90f01. No delivery or privileged operation.
- Private prepared marker now uses bounded no-follow root-owned 0400 reader with shared creator mode; protected_bytes unchanged. Real ACL/mode/symlink fixture checks plus root-wrapper rejection passed.
- Observation failure/deadline exhaustion cannot bypass tracked-group KILL attempts; uncertain cessation remains false. Real exhausted-deadline and TERM-resistant process-group regressions passed.
- TERM/INT records deferred intent; spawned children register before checkpoint can unwind. Real child pre-exec signal regression proves registered-before-stop and no orphan.
- Both /usr/bin/python3 and /opt/homebrew/bin/python3: focused unit_replay*.py 31 passed; full unit_*.py 197 passed; no errors/failures/skips. pvg verify explicit changed paths: 4 Python files, zero issues. git diff --check/staged check passed. All 12 evidence SHA256SUMS verified.
- Exact logs/report: docs/evidence/replay-prerequisites/runtime-smoke-r2/. Updated review/install contract and unchanged exact sanitized parent command: docs/REPLAY-RUNTIME-SMOKE.md. Launcher SHA256 c2085274072c4b147865b38d5a953fde3249347a5473373a24218ac9d3226325.

### proof
| AC | Verifiable evidence | Status |
|---|---|---|
| #1 | Approved policy and C001-only scope unchanged | Fresh independent review required |
| #2 | Corrected actual0400 private marker contract, safe metadata/ACL/no-follow read | Updated root-positive install/readback not-run |
| #3 | Existing protected preflight/runtime/asset identity checks retained | Updated parent positive preflight not-run |
| #4 | Fail-safe KILL and deferred signal registration; real harmless process regressions | UNRESOLVED: actual parent-mediated VM/service/accounting/stop lifecycle not-run |
| #5 | No verdict/ReplayReceipt/admission or failure-counter mutation | GRRR-z3w9 separate, independent replay not-run |

### unresolved not-run gates
- Renewed independent review of d89cec7; parent archive/update installation/review and sanitized runtime audit.
- Root-positive new smoke namespace/access/unchanged-asset probes; actual offline C001 execution, reserve/settle/ledger readback, normal/timeout/stop/TERM/KILL within480s.
- No root/QEMU/VM, /Library/GRRR mutation, delivery/acceptance or push by worker. Keep in_progress.

### LEARNINGS
- Consumer permissions must match producer's exact mode; observation uncertainty must never disable forced cessation; async stop must not unwind child creation before registration.

### DISCOVERED_BUG
- All three reviewed findings fixed in this revision; none deferred.

## nd_contract
status: in_progress

### evidence
- PROOF: clean story commit 6b90f0100d09fa3acc66724127f34ecc12934237, bounded C001 runtime-lifecycle-only package. No delivery/acceptance/push or privileged operation.
- /usr/bin/python3 and /opt/homebrew/bin/python3: `-B -m unittest discover -s tests -p 'unit_replay*.py'` => 28 passed each; `-B -m unittest discover -s tests -p 'unit_*.py'` => 194 passed each. No skips/errors/failures in final rerun.
- pvg verify explicit changed code/tests/docs/logs passed: 5 Python files scanned, 0 issues. git diff --check and staged diff check passed; 14 SHA256SUMS entries verified. Final logs/report: docs/evidence/replay-prerequisites/runtime-smoke/.
- Launcher SHA256 366d5e498c36008186caf736eb243f84c7cde834a10edcd4cf8a7977bfb99b8c. Exact 12-member closure and sanitized prelaunch/root command: docs/REPLAY-RUNTIME-SMOKE.md.
- Real harmless process-group tests verify TERM cessation and TERM-resistant child/grandchild KILL within 7s; these are not VM-positive evidence. Actual UID refusal/argument/scope/result/hash tests do not substitute for root-positive proof.

### proof
| AC | Evidence | Status |
|---|---|---|
| #1 | Immutable approved policy unchanged; exact C001-only scope, 473s work + 7s cessation | Reviewable; new review pending |
| #2 | Root-only closure, locked preflight, exact destination verification, UID-separated new subtree | Prior base preparation live-proven by parent; new smoke installation not-run |
| #3 | Original corpus/spec/source/QEMU/runtime identity and ACL/ancestor checks retained; exact15GiB recheck | No-guest negative proof passed; updated positive preflight pending |
| #4 | Executable service/VM lifecycle, evaluator-only smoke reserve/settle and append-only evidence | UNRESOLVED: actual parent-mediated offline C001 lifecycle, access/asset probes, stop/watchdog/cessation/accounting not-run |
| #5 | No verdict, independent ReplayReceipt, admission or failure-counter mutation | GRRR-z3w9 separate; independent replay still not-run |

### unresolved not-run gates
- Fresh independent security/architecture review of 6b90f01; parent archive/update of installed launcher/package/review and sanitized runtime audit.
- Root-positive smoke namespace/access probes; actual offline VM lifecycle, reserve/settle/ledger readback, normal/timeout/stop/TERM/KILL cessation within480s. Root SIGKILL/host failure requires manual inspection/recovery.
- Never rerun --prepare or reset failed smoke state; preserve original installed base evidence. No root/QEMU/VM or /Library/GRRR mutation by worker. Keep in_progress; do not deliver.

### LEARNINGS
- Parent must own QEMU's process group, not merely the executor service. Concurrent group grace periods preserve inclusive480s. macOS killpg(pid,0) may return EPERM after a group empties; strict kernel ps inventory establishes group absence.
- Initial pvg bare-pass and transitional code-pin test failures were corrected; final complete dual-interpreter rerun passed. No failed guest attempt occurred.

### DISCOVERED_BUG
- None deferred: the observed macOS process-group probe behavior was corrected inside this scope.

# Parent-mediated replay prerequisite installation — 3f2658b

## Provenance and scope

This report preserves facts supplied by the coordinating parent after its live
installation/provisioning and readback. The developer worker did not repeat the
privileged commands, inspect protected contents, or run root, QEMU or a VM.
Raw privileged transcripts were not supplied with this handoff; the observations
below are explicitly parent-reported, not an independent worker verification.

Status: **GRRR-w1lt remains in_progress**. Namespace provisioning succeeded;
service/replay lifecycle (AC #4) remains **not-run**. No delivery or acceptance.

## Failed predecessor retained

The first installed 6e89e6 preflight rejected the legitimate
`-2 /usr/sbin/distnoted` UID before namespace creation. The parent preserved the
old package, launcher, review and failed-install record at:

`/Library/GRRR/replay-install-history/6e89e6b89aebb0d6a08ce61b1898a299158da43a/`

This failure is not overwritten or relabeled as successful provisioning.

## Renewed review and exact identities

| Item | SHA-256 or commit |
|---|---|
| Approved source commit | `3f2658ba29d6fa6a6177ea83b98f75245e4cb20d` |
| Independent review_reference | `1eac14967d28e1807cac87fdbeb3654aa4893de03e58fd8bb7776ec99213273b` |
| Installed launcher | `2ba4b712044470c7c378cf487b9a10a47ad9ec1c8361c1db7a7deb49dc6aca55` |
| replay_prerequisites.py | `85f7a14d271688d554f1af4e0e539a084fd66fd9bea7920cfdf712dd2d20a237` |
| Canonical policy | `355e6f7d9dd0a65817cdc1a6421fba6347f5075c40f4a456ed601e753f14a77a` |
| Runtime identity | `59073b8282cb4333c7719d4eac417c061c82f534bf11873d26bf2b26f7531526` |

The parent reported an exact nine-file code inventory and exact fourteen-file
input inventory matching the installed contract. No raw inventory listing is
reconstructed here.

## Successful sanitized parent command

```sh
/usr/bin/env -i PATH=/usr/bin:/bin LC_ALL=C /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/bin/python3.9 -I -S -B /Library/GRRR/bootstrap/replay-root-prepare --prepare
```

Exact supplied result:

```json
{"execution_authorized":false,"namespace":"/Library/GRRR/independent-replay","replay_dispatch":"not-run"}
```

Parent readback confirmed namespace/root-private/code ownership and modes,
evaluator UID 320 ownership of policy, expectations, budget, reservations and
ledger, and runner UID 321 ownership of only the executor directory.
Root code remained protected. The prepared record read back:

```json
{"root_installation":"prepared","replay_dispatch":"not-run","execution_authorized":false,"verdict_engine":"not-installed"}
```

This is prerequisite namespace preparation, not a ReplayReceipt or authorization
to start replay. Corpus fixture ledgers have not been relabeled.

## Parent-reported identity and integrity probes

| Probe | Observed outcome |
|---|---|
| Evaluator UID 320 reads policy | Exit 0; hash matched |
| Runner UID 321 reads evaluator subtree | Denied |
| Runner UID 321 reads private subtree | Denied |
| Evaluator UID 320 reads private subtree | Denied |
| Operator UID 501 reads evaluator subtree | Denied |
| Runner UID 321 stats executor directory | Exit 0 |
| Runner writes/truncates root code | Denied; code hash unchanged |
| Evaluator writes/truncates root code | Denied; code hash unchanged |

The write-probe shell emitted the expected `getcwd` warning because the root
parent shell's working directory was inaccessible to the reduced identity.
That warning alone is not denial proof: the reported file-write denial and
unchanged code hash are the evidence. No unreported numeric denial exit codes,
probe command strings or raw output have been fabricated.

## Acceptance-criteria boundary and remaining work

- AC #1: approved policy bindings retained; parent reports installed policy hash.
- AC #2: renewed independent review and live UID-separated namespace preparation
  now have parent-reported positive evidence.
- AC #3: parent command passed protected preflight and namespace readback/probes.
- **AC #4: services, authenticated replay lifecycle, VM isolation/cessation and
  independent replay/ReplayReceipt remain not-run. Verdict engine not installed;
  execution_authorized remains false.**
- AC #5: story remains in_progress; no delivery/acceptance or fixture-ledger
  relabeling. GRRR-z3w9's prerequisite dependency is not closed by this report.

The source tests remain those recorded at 3f2658b: 20 focused and 186 full
no-guest tests passed on each required Python. This documentation-only evidence
commit does not claim a new code test run.

## Integrity

This versioned report is frozen by its sibling SHA256SUMS and Git commit.
Verify with `shasum -a 256 -c SHA256SUMS` from this directory. Future observations
must be separate reports rather than edits to this record. No OS-level immutable
flag or independent cryptographic attestation by the worker is claimed.
## Evidence persistence proof

PROOF:
- Documentation-only commit f1db89ff954ddbf91aa9d8156fd2d78dad12e244 on story/GRRR-w1lt; clean worktree.
- Frozen report: docs/evidence/replay-prerequisites/live-install/3f2658b-parent-report.md.
- Report SHA256 3760147393e63ae4f74fdc352c65f3a4e13eb40d1df59d243525af48626753bd; sibling SHA256SUMS.
- From live-install directory, shasum -a 256 -c SHA256SUMS: 3f2658b-parent-report.md: OK.
- pvg verify docs/evidence/replay-prerequisites/live-install/3f2658b-parent-report.md docs/evidence/replay-prerequisites/live-install/SHA256SUMS --format=text: PASSED, 0 files scanned, 0 issues (documentation not substantively code-scanned).
- git diff --check and git diff --cached --check: passed.
- No code changed and no new test execution claimed. Prior source revision 3f2658b had 20 focused/186 full tests pass per required Python.
- Live facts above were supplied by the trusted coordinating parent; worker did not repeat root operations or independently inspect protected raw evidence.

LEARNINGS:
- Preserve failed predecessor installation separately from the successful reviewed revision.
- Expected getcwd warning is not access-denial proof; actual denied writes and unchanged code hash matter.
- Positive namespace provisioning does not imply replay authorization or service lifecycle completion.

## nd_contract
status: in_progress

### evidence
- Parent-reported installation/readback/UID probes preserved at f1db89ff954ddbf91aa9d8156fd2d78dad12e244 with SHA256SUMS.
- No worker root/QEMU/VM, protected mutation, push, deliver or acceptance.

### proof
- [x] Renewed independent review and parent live namespace preparation/probes recorded with exact identities.
- [x] Failed predecessor/history and expected warning retained without inventing transcripts.
- [ ] AC #4 services, authenticated replay lifecycle, VM isolation/cessation, independent replay/ReplayReceipt not-run; verdict engine not-installed, execution_authorized=false.
- [ ] Story remains in_progress, not delivered or accepted.

## Live preflight signed-UID correction

PROOF:
- Clean commit 3f2658ba29d6fa6a6177ea83b98f75245e4cb20d on story/GRRR-w1lt.
- Parent reported installed 6e89e6 sanitized root preflight failed before mutation: Malformed process inventory for -2   345 /usr/sbin/distnoted. Parent reports no independent-replay namespace created; installed old package/inputs remain partial. This worker did not invoke or retry root preflight.
- check_idle accepts exactly one optional leading sign and decimal UID digits; malformed/nonnumeric fields still fail. UID 320/321 including +320/+321 and QEMU denial unchanged.
- New regression covers the exact reported negative row, positive signed UID, nonnumeric/sign-only/repeated-sign cases, both protected identities and QEMU under negative UID.
- Both /usr/bin/python3 and /opt/homebrew/bin/python3:
  PYTHON -B -m unittest discover -s tests -p unit_replay_prerequisites.py -v: 20 passed, 0 failures/errors/skips.
  PYTHON -B -m unittest discover -s tests -p 'unit_*.py': 186 passed, 0 failures/errors/skips.
- pvg verify research/replay_prerequisites.py scripts/replay-root-prepare tests/unit_replay_prerequisites.py docs/REPLAY-PREREQUISITES.md docs/evidence/replay-prerequisites/README.md --format=text: PASSED, 2 files scanned, 0 issues.
- git diff --cached --check passed.
- Module pin: 85f7a14d271688d554f1af4e0e539a084fd66fd9bea7920cfdf712dd2d20a237.
- Launcher SHA256: 2ba4b712044470c7c378cf487b9a10a47ad9ec1c8361c1db7a7deb49dc6aca55.
- Policy/interpreter/runtime pins and sanitized pre-exec contract unchanged. Parent must update module inventory AND launcher hash after renewed independent review; old root review cannot authorize new bytes.
- Persistent focused/full logs updated under docs/evidence/replay-prerequisites/. Previous coverage-r2 remains historical; no root-positive inference or new coverage percentage claim.

AC: AC3 process parsing corrected without changing isolation or identity denial; AC1 policy unchanged. AC2/4 successful privileged postconditions and dispatch remain not-run. AC5 downstream dependency remains unchanged.

DISCOVERED_BUG:
  title: macOS negative numeric process UID rejected as malformed
  context: Parent live preflight observed UID -2 for distnoted; unsigned-only parsing rejected legitimate process inventory before mutation.
  affected_files: research/replay_prerequisites.py, scripts/replay-root-prepare
  discovered_during: GRRR-w1lt
  status: fixed in 3f2658b; renewed live parent run not-run

LEARNINGS:
- macOS ps may render service UID values as signed integers; require strict numeric syntax rather than unsigned-only UID parsing.
- Update source inventory and root launcher approval hash together; never relabel an old reviewed installation.
- Live parent failure evidence remains distinct from passing no-guest unit regressions.

## nd_contract
status: in_progress
### evidence
- 3f2658ba29d6fa6a6177ea83b98f75245e4cb20d; 20 focused + 186 full passed on each required interpreter.
- No root/QEMU/VM, /Library/GRRR mutation, push, deliver or acceptance by this worker.
### proof
- [x] Signed UID regression and existing protected-identity/QEMU denials pass.
- [ ] Renewed independent review, parent installation/review update, successful live protected preflight, root namespace creation, UID probes, service/VM lifecycle and independent replay/ReplayReceipt remain not-run for this revision.

## Native-loader environment security correction

PROOF:
- Clean commit 6e89e6b89aebb0d6a08ce61b1898a299158da43a on story/GRRR-w1lt.
- Both parent commands now use literal /usr/bin/env -i PATH=/usr/bin:/bin LC_ALL=C before the fixed direct CLT Python interpreter. Root review schema requires exact preexec_boundary and preexec_environment attestation. All previous pins, safe ancestors/ACLs and destination postconditions remain unchanged.
- Real unprivileged regression: poisoned DYLD_INSERT_LIBRARIES, DYLD_LIBRARY_PATH, PYTHONHOME, PYTHONPATH, synthetic credential, PATH and CF variable are passed to /usr/bin/env. The direct Python child sees only PATH/LC_ALL plus framework-generated CF metadata, never inherited poison; stderr empty, direct interpreter and isolated flags confirmed.
- /usr/bin/codesign --verify --strict /usr/bin/env passed. Root-owned regular env executable and safe ancestors recorded in docs/evidence/replay-prerequisites/env-boundary.log.
- Both /usr/bin/python3 and /opt/homebrew/bin/python3:
  PYTHON -B -m unittest discover -s tests -p unit_replay_prerequisites.py -v: 19 passed, 0 failures/errors/skips.
  PYTHON -B -m unittest discover -s tests -p 'unit_*.py': 185 passed, 0 failures/errors/skips.
- pvg verify scripts/replay-root-prepare tests/unit_replay_prerequisites.py tests/replay_environment_probe.py docs/REPLAY-PREREQUISITES.md docs/evidence/replay-prerequisites/README.md --format=text: PASSED, 2 scanned, 0 issues.
- git diff --cached --check passed.
- Unprivileged sanitized prelaunch runtime audit rerun successfully; no root launch occurred.
- Coverage-r2.log remains historical from c667ae9; no new coverage claim for this environment-only revision.

Exact commands after independent review:
PRE-ELEVATION:
  /usr/bin/env -i PATH=/usr/bin:/bin LC_ALL=C /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/bin/python3.9 -I -S -B scripts/replay-runtime-preflight
FUTURE ROOT PARENT ONLY, after trusted installation:
  /usr/bin/env -i PATH=/usr/bin:/bin LC_ALL=C /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/bin/python3.9 -I -S -B /Library/GRRR/bootstrap/replay-root-prepare --prepare
Do not invoke bare interpreter/shebang, inherit DYLD_*/PYTHON*/credentials or select runtime paths from caller input. Late Python sanitization is not the boundary.

AC status: canonical policy unchanged; AC2/3/4 parent launch contract corrected and real no-guest evidence supplied. Independent re-review, installation, positive root preparation, UID denial/access probes and replay remain not-run. AC5 downstream block retained.

LEARNINGS:
- Native-loader variables must be removed before interpreter startup, not checked afterwards.
- Pinned macOS framework creates __CF_USER_TEXT_ENCODING after startup. The test also poisons its outer value and confirms replacement; env -i still passes exactly two variables.
- Environment probe now asserts actual interpreter, non-root UID and isolation flags as well as sanitized variable names.

DISCOVERED_BUG: no additional unresolved defect observed in this revision. Initial child-name assertion exposed generated CF metadata and was corrected without adding an inherited allowlist exception.

## nd_contract
status: in_progress
### evidence
- 6e89e6b89aebb0d6a08ce61b1898a299158da43a and persistent logs.
- No root/QEMU/VM, protected mutation, push, deliver or accept.
### proof
- [x] Sanitized pre-exec parent contract and real poisoned-loader environment regression.
- [ ] Independent review, trusted installation, root-positive and replay gates not-run.

## Independent-review revision — awaiting re-review

PROOF:
- Clean story/GRRR-w1lt revision c667ae9c18bc87ac97722a17f0c261b06c0c0280.
- Fixed blocked runtime entrypoint: direct non-symlink CLT python3.9 plus entire pinned runtime/dependency inventory, mandatory unprivileged trusted-parent prelaunch audit, review runtime attestation, root-side repeat before effects.
- Runtime identity 59073b8282cb4333c7719d4eac417c061c82f534bf11873d26bf2b26f7531526, full inventory and real unprivileged audit evidence in docs/evidence/replay-prerequisites/.
- Fixed missing destination postconditions: reopen exact file/directory inventory, check UID/GID/mode/type/nlink/ACL/raw bytes and stable opened identity before publishing prepared.json; partial state retained on failure.
- Required interpreters /usr/bin/python3 and /opt/homebrew/bin/python3, each:
  PYTHON -B -m unittest discover -s tests -p unit_replay_prerequisites.py -v: 18 passed, 0 failures/errors/skips.
  PYTHON -B -m unittest discover -s tests -p 'unit_*.py': 184 passed, 0 failures/errors/skips.
- pvg verify research/replay_runtime.py research/trusted_install.py research/trusted_execution.py scripts/replay-root-prepare scripts/replay-runtime-preflight tests/unit_replay_prerequisites.py docs/REPLAY-PREREQUISITES.md docs/evidence/replay-prerequisites/README.md --format=text: PASSED, 4 files scanned, 0 issues.
- git diff --cached --check: PASS.
- /usr/bin/python3 -B -m trace --count --missing --summary --coverdir /tmp/GRRR-w1lt-r2-coverage --module unittest discover -s tests -p unit_replay_prerequisites.py: 18 passed; runtime verifier 96%, prerequisite module 52%, root preparer 38%. No root-positive coverage claim.
- Future parent PRE-ELEVATION command from reviewed checkout:
  /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/bin/python3.9 -I -S -B scripts/replay-runtime-preflight
- Future parent command ONLY after independent review, successful prelaunch audit, and trusted installation:
  /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/bin/python3.9 -I -S -B /Library/GRRR/bootstrap/replay-root-prepare --prepare
- The former /usr/bin/python3 root command is withdrawn. No symlink/ancestor checks weakened.

AC table:
| AC | Revision proof | Unresolved |
| 1 | Policy pin unchanged, all leaf mutations denied | Protected install not-run |
| 2 | Direct protected runtime binding and verified destination postconditions implemented | Independent re-review and root-positive preparation not-run |
| 3 | Runtime/asset checks plus shared ACL correction and real ACL/xattr tests | Positive full protected preflight not-run |
| 4 | Private exact postconditions and retained failures; no services started | UID 320/321 access probes and replay lifecycle not-run |
| 5 | No deliver/accept, no relabeled fixture ledger | GRRR-z3w9 still blocked |

DISCOVERED_BUG:
  title: ACL plus-marker-only checks miss ACL entries when macOS xattrs display at-sign
  context: A real destination ACL test failed before the fix. Per coordinator direction, fixed every reachable shared check in this revision: trusted_install.acl_free/immutable and trusted_execution._acl_free/protected_bytes. Actual file and directory ACLs with and without xattrs now reject; ACL-free paths pass.
  affected_files: research/trusted_install.py, research/trusted_execution.py, scripts/replay-root-prepare, research/replay_runtime.py
  discovered_during: GRRR-w1lt
  status: fixed in c667ae9; no privileged execution performed

LEARNINGS:
- Python cannot retroactively authenticate its loaded stdlib: pre-elevation parent audit is a separate required boundary.
- Direct CLT python3.9 is regular; convenience python3 entrypoints are symlinks and remain disallowed.
- Verify destination bytes and metadata before publishing prepared status, not merely after writes.
- macOS ACL text entries must be checked even if the mode marker displays @.
- Intermediate full-suite failure enforced the existing no-sys.path-in-research invariant; path validation was moved into the launcher without weakening tests.

## nd_contract
status: in_progress
### evidence
- c667ae9c18bc87ac97722a17f0c261b06c0c0280 and persistent logs.
- No root/QEMU/VM, /Library/GRRR mutation, push, delivery or acceptance.
### proof
- [x] Both independent-review blockers addressed in code and no-guest tests.
- [ ] Independent re-review, trusted installation, root-positive namespace preparation, UID access probes, service/VM lifecycle and independent ReplayReceipt remain not-run.

## Implementation package awaiting independent review

PROOF:
- Branch story/GRRR-w1lt; clean commit c1cd13c73224c53f4cc71b87e2fd8b32afe23124.
- /usr/bin/python3 (3.9.6) and /opt/homebrew/bin/python3 (3.14.3), each:
  - PYTHON -B -m unittest discover -s tests -p unit_replay_prerequisites.py -v: 14 passed, 0 failures/errors/skips.
  - PYTHON -B -m unittest discover -s tests -p 'unit_*.py': 180 passed, 0 failures/errors/skips.
- pvg verify research/replay_prerequisites.py scripts/replay-prerequisites scripts/replay-root-prepare tests/unit_replay_prerequisites.py docs/replay-policy-v1.json docs/REPLAY-PREREQUISITES.md docs/evidence/replay-prerequisites/README.md --format=text: PASSED, 2 files scanned, 0 issues.
- git diff --cached --check: passed before commit. Extensionless scripts additionally exercised/imported by real subprocess/tests.
- /usr/bin/python3 -B -m trace --count --missing --summary --coverdir /tmp/GRRR-w1lt-coverage --module unittest discover -s tests -p unit_replay_prerequisites.py: 14 passed, replay_prerequisites.py 52% line coverage, 117 executable lines. No root-positive execution or coverage claim.
- Durable raw logs and AC table: docs/evidence/replay-prerequisites/.
- Canonical policy SHA256 355e6f7d9dd0a65817cdc1a6421fba6347f5075c40f4a456ed601e753f14a77a.
- Exact future parent command AFTER independent review and trusted installation:
  /usr/bin/python3 -I -S -B /Library/GRRR/bootstrap/replay-root-prepare --prepare
  Installation/review schema: docs/REPLAY-PREREQUISITES.md. Never run checkout as root.

AC verification:
| AC | Package proof | Unresolved live gate |
| 1 | Exact approval policy, limits, UID ownership, denials, all-leaf tamper rejection | Root policy installation not-run |
| 2 | Executable root-only preparer, reviewed import pins, exclusive namespace, UID ownership, locked preflight | Independent security review and real root provisioning not-run |
| 3 | Exact corpus/spec/source/VM/QEMU checks, safe paths/ACLs, process/lock/identity/disk checks | Positive protected preflight not-run |
| 4 | Root-only private records, no credentials/services/VM dispatch; lifecycle design | Replay service/guest dispatch and ReplayReceipt not-run |
| 5 | No corpus-ledger relabeling; no acceptance; downstream dependency unchanged | GRRR-z3w9 remains blocked |

LEARNINGS:
- Approved literal 15 GiB is 16106127360 bytes, unlike older corpus 15000000000.
- Keep byte-validation success distinct from privileged execution authority.
- Preserve one parent lock descriptor across preflight and all namespace effects.
- Partial namespaces block retries; no automatic destructive recovery.
- Worktree vault search failed, root-context retry returned no relevant result; no config changed.

DISCOVERED_BUG:
- No implementation defect currently known from no-guest tests; root-positive behavior is explicitly unverified.
- Tooling observations: coverage.py unavailable on both interpreters, so measured with stdlib trace --missing; worktree-local vault query corrected by repository-root query.

## nd_contract
status: in_progress

### evidence
- Commit c1cd13c73224c53f4cc71b87e2fd8b32afe23124; 14 focused and 180 full no-guest tests passed on each required interpreter.
- Coordinator directed retaining in_progress for independent review. No story deliver/accept invoked.

### proof
- [x] Reviewable canonical policy and fail-closed executable namespace preparer committed.
- [x] Real non-root refusal-before-effects and argument/path/code-pin tests pass.
- [ ] Independent review, root installation, positive privileged tests and replay dispatch not-run.

## Operator Authorization

APPROVED [2026-10-23T19:15:39Z]: The operator replied exactly: `Approve GRRR-w1lt`.

This approves only the replay prerequisite scope recorded in this issue:

- Corpus: `GRRR-validated-corpus-v2.2-isolated`
- Freeze digest: `dfa75ef2bf3d43fd4f750094fe643afe4f204812c0ae2426276bedb471fa8529`
- Source commit: `129e0b3f15a3bd6af949ee47d76f6855c582ab73`
- Stop after exactly two consecutive independent replay failures.
- Per replay: 1 vCPU, 1024 MiB memory, 512 MiB disposable workspace, 45 s boot watchdog, 480 s total watchdog, 2 s stop acknowledgement, 5 s termination grace, 2 s kill wait, 1 MiB captured output, 3 MiB wire limit, and 15 GiB host free-space floor.
- Evaluator UID 320 owns policy, expectations, budget, reservations, and ledger.
- Runner UID 321 owns only the approved executor.
- Root owns immutable replay/QEMU/corpus/spec assets and the parent launcher.
- Denials: no network, no host shares, no paid dispatch, no contract admission, no production mutation, no automatic merge, and no promotion.
- Independent security/architecture review is still required before root installation or replay dispatch.

## nd_contract
status: in_progress

### evidence
- Operator approval recorded from this thread on 2026-10-23T19:15:39Z.

### proof
- [ ] Reviewed provisioning path still pending.
- [ ] Root installation and replay dispatch remain blocked until review.

## Operator Input Required

GRRR-w1lt cannot be implemented safely until the operator approves the replay-specific policy and privileged provisioning scope.

Requested approval:
- corpus: GRRR-validated-corpus-v2.2-isolated
- freeze: dfa75ef2bf3d43fd4f750094fe643afe4f204812c0ae2426276bedb471fa8529
- source: 129e0b3f15a3bd6af949ee47d76f6855c582ab73
- stop policy: stop after exactly two consecutive independent replay failures
- per replay: 1 vCPU, 1024 MiB memory, 512 MiB disposable workspace, 45 s boot watchdog, 480 s total watchdog, 2 s stop acknowledgement, 5 s termination grace, 2 s kill wait, 1 MiB captured output, 3 MiB wire limit, 15 GiB host free-space floor
- authority: evaluator UID 320 owns policy/expectations/budget/ledger; runner UID 321 owns only approved executor; root owns immutable replay/QEMU/corpus/spec assets and parent launcher
- denials: no network, no host shares, no paid dispatch, no contract admission, no production mutation, no automatic merge or promotion
- required review: independent security/architecture review before root installation or replay dispatch

## nd_contract
status: blocked

## History
- 2026-10-23T18:55:10Z dep_added: blocks GRRR-z3w9
- 2026-10-23T18:55:39Z status: open -> blocked
- 2026-10-23T19:15:39Z status: blocked -> open
- 2026-10-23T19:15:39Z status: open -> in_progress
- 2026-10-23T19:15:39Z auto-follows: linked to predecessor GRRR-bnkf
- 2026-10-23T19:15:39Z claimed by dev-GRRR-w1lt
- 2026-10-23T21:20:55Z status: in_progress -> in_progress
- 2026-10-23T21:20:55Z auto-follows: linked to predecessor GRRR-c875

## Links
- Parent: [[GRRR-2t3h]]
- Blocks: [[GRRR-z3w9]]
- Follows: [[GRRR-bnkf]], [[GRRR-c875]]

## Comments
