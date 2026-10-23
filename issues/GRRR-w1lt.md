---
id: GRRR-w1lt
title: "Bug: independent replay lacks approved privileged prerequisites"
status: in_progress
priority: 0
type: task
labels: [milestone-1, integration, discovered-by-developer]
parent: GRRR-2t3h
created_at: 2026-10-23T18:55:10Z
created_by: speed
updated_at: 2026-10-23T20:03:28Z
content_hash: "sha256:f0a3b0c9e1c5e1f283677d982af3beaec5d85517f4636e58a1c059738f990343"
blocks: [GRRR-z3w9]
assignee: dev-GRRR-w1lt
follows: [GRRR-bnkf]
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

## Links
- Parent: [[GRRR-2t3h]]
- Blocks: [[GRRR-z3w9]]
- Follows: [[GRRR-bnkf]]

## Comments
