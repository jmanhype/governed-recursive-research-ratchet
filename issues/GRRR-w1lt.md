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
updated_at: 2026-10-23T19:25:28Z
content_hash: "sha256:2deed38163301e37e1d0f61b9599c830c3c0c37f185a30f7fe0b53b8d8b6b1b2"
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
