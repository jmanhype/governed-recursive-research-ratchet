---
id: GRRR-43i8
title: "Bug: independent replay accounting profile unavailable"
status: open
priority: 0
type: task
labels: [milestone-1, integration, discovered-by-developer, rejected]
parent: GRRR-2t3h
created_at: 2026-10-23T22:09:12Z
created_by: speed
updated_at: 2026-10-24T13:40:34Z
content_hash: "sha256:cf3176a4e4807dc22e6e457e94451dbd6938ab1b0fce4d775f013a90cfb64f58"
blocks: [GRRR-z3w9]
follows: [GRRR-w1lt, GRRR-bnkf, GRRR-c875]
---

## Description
## Context

GRRR-z3w9 requires independent replay to consume the existing cumulative accounting campaign, but the active successor store has no `independent-replay` profile and remains stopped. The current active binding is `/Library/GRRR/accounting-poc2/active.json`; its protected store directory is `901acaff42b5a42f667b1c435be7c9a9ae8312539cc36eb023c45584fd2e06d6`, state is stopped, and registered profiles are only `synthetic`, `offline`, and `trusted-observation`.

The implemented replay preflight intentionally fails before namespace creation. It must not create a fresh allowance, reset cumulative ceilings, or reinterpret corpus/runtime-smoke events as independent replay.

## Root Cause

The successor accounting slice preserved ambiguous prior history conservatively but did not include a reviewed independent-replay profile or recovery path. Independent replay now needs cumulative registration without fabricating missing historical usage or silently releasing the stop.

## Affected Components

- `research/persistent_budget.py`
- Protected active accounting binding
- Stopped successor budget store
- Independent replay preflight and evaluator reservations
- Evidence/history preservation

## Acceptance Criteria

1. Produce an independently reviewed migration/recovery plan that identifies the exact active binding, store identity, stop record, existing reservations/holds/settlements/events, usage totals, and unknowns without mutating protected state.
2. Register an `independent-replay` profile only through a reviewed, root-owned, exclusive, atomic, permission-restricted path that preserves all existing bytes/history and carries forward cumulative usage and every uncertain hold conservatively.
3. The profile must use approved explicit ceilings and deny fresh-allowance reset, recasting of corpus/smoke events as independent replay, stop release by installer side effect, and unknown-history zeroing.
4. Stop recovery must require separate operator authorization and independent review, prove baseline intact, preserve unresolved history, and leave promotion/admission disabled.
5. Read-only preflight and post-install verification must prove binding/device/inode identity, hashes, ownership/modes/ACLs, profile registration, cumulative balances, stopped-state disposition, and fail-closed behavior for tampered/partial state.
6. Actual independent replay remains blocked until registration/recovery is accepted and all replay gates pass; no fresh replay Budget database may substitute for the cumulative store.

## Testing Requirements

- No-guest unit tests for binding/profile validation, conservative history carry-forward, stop persistence, uncertain holds, partial-state refusal, and ceiling enforcement.
- Integration proof requires separately reviewed parent-mediated execution and read-only before/after protected-state verification.
- No skipped mandatory tests or fabricated receipts.

## Discovered During

Story GRRR-z3w9 at WIP commit `6079af60ea7d8dc3b5927d0d51748903230a2`.

## Skills To Use

- `pvg` and `nd`
- independent security/architecture review before privileged effects

## nd_contract
status: new

### evidence
- Created from GRRR-z3w9 DISCOVERED_BUG report on 2026-10-23.

### proof
- [ ] Pending reviewed migration, authorization, installation, and verification.

## Acceptance Criteria


## Design


## Notes


## nd_contract
status: delivered

### evidence
- Transitioned via pvg story deliver on 2026-10-24.

### proof
- [ ] Developer evidence block must remain authoritative above this contract.


## Parent Preflight Revalidation

- Revalidated story worktree at evidence commit cb9f83364523fc7575e1735910b8a525f5598321 and implementation commit 2dbf825e93376c6df5b974e339ea7846a9bc9165; both story and main worktrees are clean.
- Rehashed reviewed sources: accounting_registration.py 74975c0da25303f05a7701008d87a22be7d8e6ed029bdee619f626a0d6ee10ab; persistent_budget.py ef038d60706f8f103387a6f41c28695da605f541666fa231abaa99e2af9255af; budget.py 41548c9f1c9f8f58e48587deaf56cd236fa78cc5716e799da9d678ab6b95b500; replay-root-prepare fb0828433d35fe7f96e46d19a127a32b19104ab53113f4929be30fa3d441ca37.
- Protected active binding remains unchanged at SHA256 e5629ee930fc909b38bcdf8c6cdbd673233651b1b507d73a2230f4ce1e304c95 with the exact beba store identity and three legacy profiles; candidate protected bootstrap destination is absent; no QEMU/accounting runner process is visible; root free space is approximately 17.06 GB.
- Independently reran focused registration suite on both required interpreters: 30/30 passed each, zero failures/errors/skips.
- No protected staging, registration, stop release, replay, promotion, admission, or merge was performed. Operator authorization for protected staging/read-only inspect remains the gating action.

## nd_contract
status: blocked

### evidence
- Direct live-state preflight and parent test rerun recorded.

### proof
- [x] Registration-only implementation remains independently review-ready.
- [ ] Protected bootstrap staging and read-only inspect await explicit operator authorization.
- [ ] Registration/installation, stop recovery, and replay remain not-run.

## Independent BLOB-Fix Re-review

SECURITY_REVIEW: READY_FOR_PROTECTED_REGISTRATION_REVIEW

- Reviewed code commit 2dbf825e93376c6df5b974e339ea7846a9bc9165 and evidence commit cb9f83364523fc7575e1735910b8a525f5598321.
- No blocking finding within the documented trusted-runtime boundary. Registered, stale, and partial-state guards cover settlement, metering, overhead, halt, inherited calls, SQL cursor paths, and writable blobopen; tests preserve DB bytes, inode, totals, and pending holds.
- Independent reruns: Python 3.14 focused 30/30; Python 3.9 full 228/228; Python 3.14 full 228/228; diff check passed.
- Boundary: this is not a sandbox against arbitrary evaluator code or base C misuse. Old processes/handles must cease and a privileged parent must establish exclusive writer control before registration.
- Protected staging/installation/postflight, stop recovery, and replay remain unproven and require separate authorization/review. No privileged operation occurred.

## nd_contract
status: in_progress

### evidence
- Independent reviewer was read-only and reran no-guest suites only.

### proof
- [x] Registration-only implementation and no-guest tests reviewed.
- [ ] Exact live protected inventory, immutable bootstrap/plan staging, protected registration/postflight, stop recovery, and replay remain blocked/not-run.

# GRRR-43i8 incremental BLOB review correction

Implementation: `2dbf825e93376c6df5b974e339ea7846a9bc9165`.
The second review correctly identified that SQLite incremental BLOB writes bypass
SQL authorizers on stale writable connections. This correction forbids writable
`blobopen` entirely: no accounting operation needs it. Denial precedes native API
lookup for every table/column, database name, profile, and registration state.
Only literal `readonly=True` is accepted; native read-only access is preserved.
Python 3.9 lacks native blobopen and explicitly raises sqlite3.NotSupportedError
for read-only requests; writable requests still refuse on that interpreter.

## PROOF

Commands from story worktree at the implementation SHA above:

| Command | Result |
|---|---|
| `/usr/bin/python3 -m unittest discover -s tests -p unit_replay_accounting_registration.py` | Python 3.9.6: 30 passed, 0 failures/errors/skips, 1.433s |
| `/opt/homebrew/bin/python3 -m unittest discover -s tests -p unit_replay_accounting_registration.py` | Python 3.14.3: 30 passed, 0 failures/errors/skips, 1.365s |
| `/usr/bin/python3 -m unittest discover -s tests -p 'unit_*.py'` | 228 passed, 0 failures/errors/skips, 21.908s |
| `/opt/homebrew/bin/python3 -m unittest discover -s tests -p 'unit_*.py'` | 228 passed, 0 failures/errors/skips, 20.640s |
| `/usr/bin/python3 -m compileall -q research tests/unit_replay_accounting_registration.py` | exit 0 |
| `/opt/homebrew/bin/python3 -m compileall -q research tests/unit_replay_accounting_registration.py` | exit 0 |
| `pvg verify research/persistent_budget.py tests/unit_replay_accounting_registration.py docs/REPLAY-ACCOUNTING-REGISTRATION.md --format=text` | PASS: 2 files scanned, 0 issues; Markdown not scanned |
| `git diff --check` and `git diff --cached --check` | exit 0 |

Logs: `/tmp/GRRR-43i8-blob-full-py39.log` and
`/tmp/GRRR-43i8-blob-full-homebrew.log`; final suites report OK, no warnings.
Regressions iterate every column of reservations, metering, overhead, state and
store_identity. They cover defaults and nonboolean readonly inputs, all registered
profiles, legacy handles before/after publication and partial-registration handles.
Tests assert unchanged bytes/inode, cumulative totals and pending holds. Native
read-only reads succeed on 3.14; both write() and item assignment refuse. The 3.9
unsupported-read assertion executes rather than skipping a test.

Coverage command:

```sh
/usr/bin/python3 -m trace --count --missing --summary \
  --file /tmp/GRRR-43i8-blob-trace --coverdir /tmp/GRRR-43i8-blob-coverage \
  --module unittest discover -s tests -p unit_replay_accounting_registration.py
```

30 passed in 2.395s. Python 3.9 reported executable-line coverage: PersistentBudget
96% (146 lines), Budget 91% (175 lines). Not branch coverage; native read-only BLOB
behavior is exercised separately by the Python 3.14 run. Coverage log:
`/tmp/GRRR-43i8-blob-coverage.log`.

New PersistentBudget SHA256:
`ef038d60706f8f103387a6f41c28695da605f541666fa231abaa99e2af9255af`.
Budget, bootstrap and source launcher pins are unchanged; full suites verify
the existing launcher pins. No installed artifact changed.

## LEARNINGS

- The prior freeze correction covered SQL but missed a separate SQLite mutation
  API. An authorizer is not a complete incremental-BLOB write boundary.
- Denying unused writable BLOB access is smaller and safer than handing out a
  wrapper whose write, slice assignment, lifetime and stale-state semantics would
  all need auditing. Native read-only handles remain useful and safe.
- Handles opened by older code cannot be retroactively revoked by this override.
  Installer writer/process quiescence and exclusive-parent operation remain
  mandatory. Deliberate base-C-method invocation/guard disabling by arbitrary
  evaluator code is not sandboxed by this trusted API, as documented previously.
- pvg initially flagged NotImplementedError for absent native support as a stub;
  the final code uses the specific sqlite3.NotSupportedError with executed tests.

## nd_contract
status: in_progress

### evidence
- Code `2dbf825e93376c6df5b974e339ea7846a9bc9165`; focused 30/30 and full 228/228 both required interpreters.
- No root/sudo, protected mutation, QEMU/VM, stop release, replay, delivery or push.
- Independent re-review pending; installer baseline and quiescence requirements unchanged.

### proof
- [x] Writable incremental BLOB access refused across profiles, stale/partial states and protected tables/columns; bytes/inode/holds preserved.
- [x] Read-only native BLOB behavior preserved; Python 3.9 compatibility refusal tested without skips.
- [ ] AC2/5 protected installation/postflight: BLOCKED, not-run.
- [ ] AC4 recovery: BLOCKED, not-authorized, not-run.
- [ ] Actual independent replay: BLOCKED, not-run.

## Independent Implementation Re-review

SECURITY_REVIEW: CHANGES_REQUIRED

- Reviewed freeze-fix commit 8820a6ba5ebaa5b503f3242b2f0c006df8a2ba2c without protected effects.
- Original settle/meter/overhead/halt mutation gap is fixed and focused/full tests pass.
- New blocking gap: inherited sqlite Connection.blobopen on a stale legacy handle bypasses the SQL authorizer after registration. Reviewer reproduced a valid reservations.maximum BLOB write changing cumulative holds and DB bytes on Python 3.14.
- Required fix: deny or guard every writable incremental-BLOB path, including stale and partial-registration states; retain writer quiescence for already-open handles. Add byte/inode/hold preservation regressions.

## nd_contract
status: in_progress

### evidence
- Reviewer reproduced the gap only in temporary fixtures.

### proof
- [ ] Guarded BLOB access and regressions remain pending.
- [ ] Protected installation/recovery/replay remain blocked.

# GRRR-43i8 frozen-runtime review correction

Implementation commit: `8820a6ba5ebaa5b503f3242b2f0c006df8a2ba2c`.
This supersedes the earlier runtime-freeze claim at `8f90d35`; the independent
review correctly found inherited mutation paths unguarded. Story remains
in_progress, not delivered. No protected operation or push was performed.

## PROOF

Version 2 opens `mode=ro`, bypassing chmod/schema initialization. A shared dynamic
guard runs before reserve, meter, settle, overhead and halt, including explicit
base-class calls. Every profile is frozen. Legacy handles check the current
binding and any partial registration output before mutation; legacy stopped
settlement/meter/overhead behavior is preserved before registration. Persistent
connection/cursor authorizers refresh before all SQL execution entrypoints so
already-prepared statements cannot retain a stale authorization decision.

Regressions assert refusal with unchanged DB bytes/inode and unchanged pending
holds for every mutator and all profiles, direct inherited calls, stale legacy
handles and cursors, duplicate metering/requests, zero reservations, and partial
registration. SQLite execute/executemany/executescript are also exercised. The
independent installer and baseline checks were not changed.

Commands from the story worktree; source tree corresponds exactly to the commit
above (commit changes no source bytes during final testing):

| Command | Result |
|---|---|
| `/usr/bin/python3 -m unittest discover -s tests -p unit_replay_accounting_registration.py` | 27 tests, 0 failures/errors/skips; 1.289s; OK |
| `/opt/homebrew/bin/python3 -m unittest discover -s tests -p unit_replay_accounting_registration.py` | 27 tests, 0 failures/errors/skips; 1.236s; OK |
| `/usr/bin/python3 -m unittest discover -s tests -p 'unit_*.py'` | 225 tests, 0 failures/errors/skips; 21.392s; OK |
| `/opt/homebrew/bin/python3 -m unittest discover -s tests -p 'unit_*.py'` | 225 tests, 0 failures/errors/skips; 20.981s; OK |
| `/usr/bin/python3 -m compileall -q research tests/unit_replay_accounting_registration.py scripts/replay-root-prepare` | exit 0 |
| `/opt/homebrew/bin/python3 -m compileall -q research tests/unit_replay_accounting_registration.py scripts/replay-root-prepare` | exit 0 |
| `pvg verify research/budget.py research/persistent_budget.py tests/unit_replay_accounting_registration.py scripts/replay-root-prepare docs/REPLAY-ACCOUNTING-REGISTRATION.md --format=text` | PASS, 3 Python files scanned, 0 issues; script/Markdown excluded by scanner |
| `git diff --check` and `git diff --cached --check` | exit 0 |

Interpreters: `/usr/bin/python3` 3.9.6, `/opt/homebrew/bin/python3` 3.14.3.
Full logs: `/tmp/GRRR-43i8-freeze-full-py39.log` and
`/tmp/GRRR-43i8-freeze-full-homebrew.log`. No final test warnings.

Coverage command:

```sh
/usr/bin/python3 -m trace --count --missing --summary \
  --file /tmp/GRRR-43i8-freeze-trace \
  --coverdir /tmp/GRRR-43i8-freeze-coverage \
  --module unittest discover -s tests -p unit_replay_accounting_registration.py
```

27 passed, 1.737s. Reported line coverage (not branch coverage): Budget 91%
(175 executable lines), PersistentBudget 97% (139), registration 90% (350), tests
99% (472). Output `/tmp/GRRR-43i8-freeze-coverage.log`.

Current source hashes:

```text
41548c9f1c9f8f58e48587deaf56cd236fa78cc5716e799da9d678ab6b95b500  research/budget.py
107602f75dc33e707639fa39a25d974511a1f0d28d8631a9ac36174bf8ed0c38  research/persistent_budget.py
fb0828433d35fe7f96e46d19a127a32b19104ab53113f4929be30fa3d441ca37  scripts/replay-root-prepare
```

## LEARNINGS

- The initial implementation checked reserve only; inherited settlement could
  release a hold. A freeze must protect every mutation and initialization path.
- SQLite `mode=ro` provides an additional engine boundary for newly opened frozen
  handles; stale legacy handles still require current binding checks.
- A failing regression demonstrated Python 3.9 reusing the previous SQL authorizer
  decision despite `cached_statements=0`. Rearming the authorizer before each
  execution makes the same already-used statement refuse after publication.
- These guards protect trusted runtime entrypoints, not arbitrary evaluator code
  intentionally disabling authorizers or opening another raw database connection.
  Installer quiescence and exclusive privileged-parent coordination remain required.

## nd_contract
status: in_progress

### evidence
- Implementation `8820a6ba5ebaa5b503f3242b2f0c006df8a2ba2c`; focused 27/27 and full 225/225 on both required interpreters.
- Corrected source Budget pin only; no installed closure changed.
- Independent re-review pending. No root/sudo, protected mutation, VM/QEMU, stop release, replay, delivery or push.

### proof
- [x] Runtime mutation freeze regression coverage across profiles, inherited APIs and stale handles; bytes/inode/holds unchanged.
- [x] Legacy behavior and full no-guest suites retained.
- [ ] AC2/5 protected registration/integration: BLOCKED, not-run.
- [ ] AC4 recovery: BLOCKED, not-authorized, not-run.
- [ ] Actual independent replay: BLOCKED, not-run.

## Independent Implementation Review

SECURITY_REVIEW: CHANGES_REQUIRED

- Reviewed implementation commit 8f90d35c9008478c4258f07c171442e84de11235 without protected effects.
- Blocking finding: registered PersistentBudget freezes reserve/verification only. Inherited settle(), meter(), and disclose_overhead() can mutate the stopped cumulative database and release a pending hold before later verification detects drift.
- Required fix: registration-only version 2 must be read-only/fail-closed across every profile and mutation entrypoint until separately reviewed recovery. Add regressions for settlement, metering, overhead, and stale handles with unchanged bytes/inode and unchanged pending holds.
- Reviewer otherwise observed baseline checks, atomic receipt publication, profile binding, stop-before-idempotency, source pins, and focused tests consistent, but this is not acceptance.

## nd_contract
status: in_progress

### evidence
- Independent reviewer reproduced the mutation only in temporary fixtures; no protected operation.

### proof
- [ ] Runtime mutation freeze and regressions remain pending.
- [ ] No installation, stop recovery, or replay is authorized.

# GRRR-43i8 registration-only verification

Status: implementation WIP, BLOCKED for privileged ACs; not delivered.
Tested source tree: `8f90d35c9008478c4258f07c171442e84de11235`.
No protected installation/mutation, root/sudo, stop release, guest/VM/QEMU,
independent replay, promotion, admission or push was performed.

## PROOF

Commands ran from `.claude/worktrees/dev-GRRR-43i8` on 2026-10-23.

| Command | Result |
|---|---|
| `/usr/bin/python3 -m unittest discover -s tests -p unit_replay_accounting_registration.py` | Python 3.9.6: 23 tests, 0 failures, 0 errors, 0 skipped; 0.923s; OK |
| `/opt/homebrew/bin/python3 -m unittest discover -s tests -p unit_replay_accounting_registration.py` | Python 3.14.3: 23 tests, 0 failures, 0 errors, 0 skipped; 0.860s; OK |
| `/usr/bin/python3 -m unittest discover -s tests -p 'unit_*.py'` | 221 tests, 0 failures, 0 errors, 0 skipped; 20.915s; OK |
| `/opt/homebrew/bin/python3 -m unittest discover -s tests -p 'unit_*.py'` | 221 tests, 0 failures, 0 errors, 0 skipped; 20.461s; OK |
| `/usr/bin/python3 -m compileall -q research tests/unit_replay_accounting_registration.py scripts/replay-root-prepare` | exit 0 |
| `/opt/homebrew/bin/python3 -m compileall -q research tests/unit_replay_accounting_registration.py scripts/replay-root-prepare` | exit 0 |
| `pvg verify research/accounting_registration.py research/budget.py research/persistent_budget.py tests/unit_replay_accounting_registration.py scripts/replay-root-prepare docs/REPLAY-ACCOUNTING-REGISTRATION.md --format=text` | PASS: 4 files scanned, 0 issues; extensionless script and Markdown not scanned |
| `git diff --check` and `git diff --cached --check` | exit 0 |

Full test stdout/stderr captures: `/tmp/GRRR-43i8-final-full-py39.log` and
`/tmp/GRRR-43i8-final-full-homebrew.log`. Both end with `Ran 221 tests` / `OK`.
No final suite warnings. These are no-guest units, not protected integration.

Coverage command (stdlib trace; not branch coverage):

```sh
/usr/bin/python3 -m trace --count --missing --summary \
  --file /tmp/GRRR-43i8-trace-final \
  --coverdir /tmp/GRRR-43i8-coverage-final \
  --module unittest discover -s tests -p unit_replay_accounting_registration.py
```

23 tests passed in 1.285s. Reported executable-line coverage: registration module
90% (350 lines), Budget 86% (162 lines), PersistentBudget 97% (91 lines), tests
99% (383 lines). Coverage output `/tmp/GRRR-43i8-coverage-final.log`.
The Homebrew interpreter lacks third-party `coverage`; no dependency was installed.
An initial trace without `--missing` reports a misleading executed-only denominator;
that result is explicitly discarded and is not the coverage claim above.

Source SHA256 values:

```text
74975c0da25303f05a7701008d87a22be7d8e6ed029bdee619f626a0d6ee10ab  research/accounting_registration.py
576b77e2bcc1782ab5cdc8fad80ad7b550e110f2f617280982b93363e0974a23  research/budget.py
d658334fc35228cac1b70c8e9e0e1c173bff90ca51d5470dbfbfa6da463e606b  research/persistent_budget.py
1285f6bf5f1e1973c5539437e99021b85c872b7452aa93564037ba3f59a41183  scripts/replay-root-prepare
```

## AC disposition

| AC | Implementation/test support | Remaining blocker |
|---|---|---|
| 1 | Reviewed proposal; exact pinned parent-observed identities; read-only snapshot code captures all raw rows and unknowns | Actual protected inventory/provenance not collected by worker; implementation review pending |
| 2 | Root-only, exclusive, receipt-first/atomic binding source; temporary fixture byte/inode preservation tests | Protected registration NOT RUN; no integration proof |
| 3 | Exact existing shared ceilings; POC-only replay; no DB writes/new store/reset; full uncertain holds retained | Independent review of implementation remains required |
| 4 | No recovery command; stop preserved; changed stopped DB rejects verification; duplicate/zero requests refuse | Recovery NOT AUTHORIZED/NOT RUN; separate decision and review required |
| 5 | Read-only baseline/postflight source; ACL/mode/link/identity/tamper/partial tests, fault injection before/after activation | Protected before/after verification NOT RUN |
| 6 | Legacy denies replay; registered store remains frozen/stopped; no dispatch authority added | Actual replay remains blocked behind registration/recovery and all replay gates |

## LEARNINGS

- A profile registration need not migrate SQLite: only the root binding changes;
  the exact stopped database, original binding bytes and all unknown holds remain.
- Idempotent duplicate reservation lookup previously preceded stop checking;
  fail-closed ordering must deny it before returning an old reservation.
- Updating Budget requires refreshing the checkout smoke launcher's source pin;
  that does not update or approve its installed closure.
- Legacy `PROFILES` is consumed by fixtures/clients; retain that three-profile API
  and add explicit `REGISTERED_PROFILES` rather than changing legacy semantics.
- Unit root emulation must restore original directory modes, not assume 0555:
  Python 3.14 Path.replace uses the patched os.replace where Python 3.9 differs.

Initial fixture permission errors, source-pin/legacy export regression failures,
and the Python 3.14 fixture-mode mismatch were fixed before the final clean runs.
Future parent commands and remaining privileged-parent exclusion obligation are
in `docs/REPLAY-ACCOUNTING-REGISTRATION.md`. Story remains in_progress.

## Independent Security Review

SECURITY_REVIEW: READY_FOR_REGISTRATION_IMPLEMENTATION

- Reviewed documentation-only commit f16d4628d26a49fb344a2ecc935b2e6e4558a31c and proposal SHA256 b2a6bcf72d6b22f8bbf6e6ea1f82c79069811010053aafb5e206b35bafc36c5c.
- No blocking defect in the proposal-only basis. Mandatory prerequisites remain: exact protected inventory/provenance, explicit approved replay limits/stage, complete publication/receipt and writer-lock protocol, implementation, tests, and separate independent verification.
- This review does not satisfy GRRR-43i8 delivery and authorizes no installation, stop recovery, protected mutation, replay, admission, or promotion.

## nd_contract
status: in_progress

### evidence
- Security reviewer was read-only; no privileged execution.

### proof
- [ ] Registration-only implementation and all tests remain pending.
- [ ] Protected installation/recovery remain blocked and not-run.

## History
- 2026-10-23T22:09:12Z dep_added: blocks GRRR-z3w9
- 2026-10-23T22:09:24Z status: open -> in_progress
- 2026-10-23T22:09:24Z auto-follows: linked to predecessor GRRR-w1lt
- 2026-10-23T22:09:24Z claimed by dev-GRRR-43i8
- 2026-10-23T22:44:55Z status: in_progress -> blocked
- 2026-10-24T12:30:25Z status: blocked -> in_progress
- 2026-10-24T12:30:25Z auto-follows: linked to predecessor GRRR-bnkf
- 2026-10-24T13:31:24Z status: in_progress -> in_progress
- 2026-10-24T13:31:24Z auto-follows: linked to predecessor GRRR-c875
- 2026-10-24T13:40:34Z status: in_progress -> open
- 2026-10-24T13:40:34Z released by speed

## Links
- Parent: [[GRRR-2t3h]]
- Blocks: [[GRRR-z3w9]]
- Follows: [[GRRR-w1lt]], [[GRRR-bnkf]], [[GRRR-c875]]

## Comments

### 2026-10-23T22:16:52Z speed
BLOCKED: No independent-replay ceilings, privileged registration, or stop recovery authorized in this turn. Current AC2/5 and integration requirements cannot be met by a proposal. Draft docs/REPLAY-ACCOUNTING-RECOVERY-PROPOSAL.md preserves parent-observed identity, conservative semantics and exact decisions needed. No protected effects, no production code changes. Baseline focused tests 7/7 and full no-guest tests 198/198 pass on Python 3.9.6 and 3.12.7; these do not prove proposed migration. Await independent review and explicit operator decisions; not delivered.

### 2026-10-23T22:48:33Z speed
## Parent Blocked-Audit Contract

GRRR-43i8 remains blocked because protected staging and read-only inspect require a separate explicit operator authorization that has not been supplied. This is the third consecutive goal-turn live check with the same gate: reviewed bootstrap commit/hash present, worktree clean, protected bootstrap absent, active binding unchanged, and no privileged runner visible.

## nd_contract
status: blocked

### evidence
- Implementation commit 2dbf825e93376c6df5b974e339ea7846a9bc9165; evidence commit cb9f83364523fc7575e1735910b8a525f5598321.
- Bootstrap source SHA256 74975c0da25303f05a7701008d87a22be7d8e6ed029bdee619f626a0d6ee10ab.
- /Library/GRRR/bootstrap/register-independent-replay is absent.
- active.json SHA256 e5629ee930fc909b38bcdf8c6cdbd673233651b1b507d73a2230f4ce1e304c95; store/profiles unchanged.
- No registration, protected mutation, stop release, replay, promotion, admission, or merge occurred.

### proof
- [x] Independently reviewed registration-only implementation and no-guest tests are complete.
- [ ] Exact operator approval for protected staging/read-only inspect is missing.
- [ ] Protected registration/postflight, recovery, and replay remain not-run.

### 2026-10-24T12:30:25Z speed
## Operator Authorization — protected staging and inspect only

APPROVED [2026-10-24]: The operator supplied the exact requested authorization for GRRR-43i8 commit 2dbf825e93376c6df5b974e339ea7846a9bc9165 and bootstrap SHA256 74975c0da25303f05a7701008d87a22be7d8e6ed029bdee619f626a0d6ee10ab.

Authorized effects:
1. Stage that exact bootstrap only at /Library/GRRR/bootstrap/register-independent-replay as root:wheel 0444.
2. Run read-only inspect using the pinned isolated CLT Python 3.9.6.
3. Preserve staging/inspection evidence.

Explicit denials: no registration install, no active.json or budget.sqlite change, no stop clearing/recovery, no replay, no promotion, no merge.

## nd_contract
status: in_progress

### evidence
- Preflight confirmed code ancestry, exact source hash, clean worktree, absent destination, unchanged active binding hash/identity/profiles, and no visible privileged runner.
- Current free space is below the prior 15 GiB execution floor (about 12.9 GB), but the authorized action is only a tiny bootstrap copy plus read-only inspection; no VM/registration execution is authorized.

### proof
- [ ] Protected staging and read-only inspect pending.
- [ ] Registration/installation/recovery/replay remain denied.

### 2026-10-24T12:34:57Z speed
## Protected Staging and Read-only Inspect Evidence

- Operator authorization was exact and limited to staging plus inspect; no registration/recovery/replay/promotion/merge authority.
- Preflight confirmed implementation commit 2dbf825e93376c6df5b974e339ea7846a9bc9165 is an ancestor of clean evidence HEAD cb9f83364523fc7575e1735910b8a525f5598321, and both committed and working-tree accounting_registration.py bytes hash to 74975c0da25303f05a7701008d87a22be7d8e6ed029bdee619f626a0d6ee10ab.
- A first staging attempt failed before publication because the parent script called nonexistent /usr/bin/sync. Its exclusive temporary file was removed, destination remained absent, and active/database state was untouched. Corrected script used /bin/sync.
- Final stage created /Library/GRRR/bootstrap/register-independent-replay as root:wheel regular file mode 0444, one link, device 16777229, inode 684952620, exact SHA256 74975c0da25303f05a7701008d87a22be7d8e6ed029bdee619f626a0d6ee10ab.
- Pinned isolated CLT Python 3.9.6 read-only inspect exited 0. Raw canonical result preserved at outputs/grrr-43i8-protected-inspect/inspect.json, SHA256 0ab4ee35d5a8c2790228409624273c4ba0882b976597ef2f58ed6bec1a8e0e11. Canonical baseline SHA256 a0c0d9770f8cc90c7eaa31f0cb13f672b5be0e84c4030f582f2b0e83c751ee5f.
- Inspect proved database SHA256 2347a548429cd8bf07048e15898de1432c960d7a08743e17dc31d39efdb5bbaf, stopped=1, pending=3, metering rows=8, reservation rows=11, overhead rows=0, known encumbered POC/milestone=[0,1108265788,0], historical_unknowns=unresolved, spendable=null.
- Postflight active.json remained root:wheel 0444 inode 682589456 with SHA256 e5629ee930fc909b38bcdf8c6cdbd673233651b1b507d73a2230f4ce1e304c95, version 1, exact beba store, and three legacy profiles. registration/ directory remains absent.
- No active.json/budget.sqlite mutation, registration install, stop clear, recovery, replay, promotion, admission, or merge occurred.
- Current free space is about 12.89 GB, below the prior 15 GiB replay floor. This tiny authorized operation completed, but future replay execution must not proceed without safe space remediation and separate authorization.

## nd_contract
status: in_progress

### evidence
- Evidence directory outputs/grrr-43i8-protected-inspect contains inspect.json, stage-inspect.sh, POSTFLIGHT.txt, baseline.sha256, and SHA256SUMS.

### proof
- [x] Exact bootstrap staged with verified ownership/mode/hash.
- [x] Read-only inspect completed and exact stopped baseline captured.
- [ ] Independent registration plan/review and separate installation authorization remain pending.
- [ ] Stop recovery and replay remain not-run.

### 2026-10-24T12:38:34Z speed
## Independent Registration Plan Review

SECURITY_REVIEW: APPROVED_REGISTRATION_PLAN

- Reviewer verified staged installer SHA256 74975c0da25303f05a7701008d87a22be7d8e6ed029bdee619f626a0d6ee10ab, canonical baseline SHA256 a0c0d9770f8cc90c7eaa31f0cb13f672b5be0e84c4030f582f2b0e83c751ee5f, review SHA256 fe0cfdc4d761630801e7c2b5c4266c36e933f0b16ee23d31f34f43871417d8eb, and plan SHA256 24e6fa0d6ae3f9bd4a4cd8dec8dcf1f8d464c2eec0e61224516c91ee2f74341c.
- Exact installer expectations verified: unchanged ceilings, ordered four profiles, stage=poc, stop_release=false, execution_authorized=false, exclusive_parent=true.
- Reviewer confirmed staged bootstrap equals implementation commit 2dbf825e source bytes, review/plan bytes are canonical, active remains version 1, and registration directory is absent.
- Reviewer could not independently reread live DB stopped state because of filesystem permissions; protected parent inspect proved stopped=1 and future installer acquire/baseline must revalidate it plus writer exclusion immediately before any separately authorized installation.
- Review/plan candidates were renamed to immutable hash-derived filenames only in the user workspace; they have NOT been staged under /Library/GRRR/bootstrap and confer no execution authority.

## nd_contract
status: in_progress

### evidence
- Independent reviewer was read-only and performed no privilege escalation or installation.

### proof
- [x] Exact registration plan/review independently approved with hashes.
- [ ] Separate operator authorization and root-owned staging of review/plan remain pending.
- [ ] Registration installation/postflight, stop recovery, and replay remain not-run.

### 2026-10-24T13:27:55Z speed
## Operator Authorization — registration-only install

APPROVED [2026-10-24]: The operator supplied exact authorization for registration-only installation using installer SHA256 74975c0da25303f05a7701008d87a22be7d8e6ed029bdee619f626a0d6ee10ab, baseline SHA256 a0c0d9770f8cc90c7eaa31f0cb13f672b5be0e84c4030f582f2b0e83c751ee5f, review SHA256 fe0cfdc4d761630801e7c2b5c4266c36e933f0b16ee23d31f34f43871417d8eb, and plan SHA256 24e6fa0d6ae3f9bd4a4cd8dec8dcf1f8d464c2eec0e61224516c91ee2f74341c.

Authorized effects:
1. Stage the exact root-owned immutable review and plan under /Library/GRRR/bootstrap.
2. Run the reviewed installer's registration-only install command.
3. Run protected verify.
4. Preserve original budget.sqlite bytes/inode/history and stopped state.

Explicit denials: no stop release or recovery, no replay, no promotion/admission, no merge, no fresh database/allowance.

Preflight revalidated clean story/evidence HEAD cb9f83364523fc7575e1735910b8a525f5598321, exact installer/review/plan/baseline bindings, active version-1 binding hash e5629ee930fc909b38bcdf8c6cdbd673233651b1b507d73a2230f4ce1e304c95, absent registration directory and protected plan/review destinations, and no visible privileged runner. Free space is about 12.47 GB; registration is tiny and replay remains separately blocked by the 15 GiB floor.

## nd_contract
status: in_progress

### evidence
- Operator authorization and live preflight recorded before protected effects.

### proof
- [ ] Root-owned review/plan staging pending.
- [ ] Registration-only install and protected verify pending.
- [ ] Stop recovery and replay remain denied/not-run.

### 2026-10-24T13:31:24Z speed
## Implementation Evidence — protected registration-only install

PROOF:
- Implementation commit 2dbf825e93376c6df5b974e339ea7846a9bc9165; repository evidence HEAD cb9f83364523fc7575e1735910b8a525f5598321; both worktrees clean before authorized effects.
- Operator authorized exact installer 74975c0da25303f05a7701008d87a22be7d8e6ed029bdee619f626a0d6ee10ab, baseline a0c0d9770f8cc90c7eaa31f0cb13f672b5be0e84c4030f582f2b0e83c751ee5f, review fe0cfdc4d761630801e7c2b5c4266c36e933f0b16ee23d31f34f43871417d8eb, and plan 24e6fa0d6ae3f9bd4a4cd8dec8dcf1f8d464c2eec0e61224516c91ee2f74341c.
- Root-owned staged review and plan retained exact hashes and modes 0444. Install command used the pinned isolated CLT Python 3.9.6 and exact REGISTER_STOPPED_INDEPENDENT_REPLAY authorization.
- Install returned registered=true, stopped=true, execution_authorized=false; binding SHA256 97ad3cd38a90a71d412afccad5ed49fc73af73e5413edcc4e07a1e0d23f451c5; receipt SHA256 fb2132f1dce4867d0a28895215ef9d5f9ad1ea947b3a373de5efd7ddad04f397.
- Protected verify exited 0. Active binding is version 2 with ordered profiles synthetic,offline,trusted-observation,independent-replay and registration hash fb2132f1dce4867d0a28895215ef9d5f9ad1ea947b3a373de5efd7ddad04f397.
- Direct root read-only postflight proved exact inventories; root:wheel 0444 active/prior/receipt/plan/review/installer; evaluator-owned original store directory 0700 and database 0600; original database inode 682589447 unchanged; database SHA256 2347a548429cd8bf07048e15898de1432c960d7a08743e17dc31d39efdb5bbaf unchanged; no journal/WAL/SHM; SQLite integrity ok; state 1|1; store identity exact; reservations 11, metering 8, overhead 0.
- Cumulative known encumbered remains [0,1108265788,0] in both POC and milestone; three pending holds remain; historical_unknowns=unresolved and spendable=null. Prior active version 1 bytes are preserved at registration/prior-active.json with SHA256 e5629ee930fc909b38bcdf8c6cdbd673233651b1b507d73a2230f4ce1e304c95.
- No stop release, recovery, replay, promotion, admission, production mutation, or merge. execution_authorized and stop_release remain false.

### CI/Test Results
Commands run:
- Protected install using exact root-only command with plan 24e6fa0d6ae3f9bd4a4cd8dec8dcf1f8d464c2eec0e61224516c91ee2f74341c.
- Protected verify using exact root-only command.
- Direct root read-only metadata/hash/SQLite postflight.
- Prior no-guest verification at implementation: focused 30/30 and full 228/228 on both required Pythons.
Summary: protected install PASS, protected verify PASS, read-only postflight PASS, no skipped protected gates.

### Commit
- Branch: story/GRRR-43i8
- Code SHA: 2dbf825e93376c6df5b974e339ea7846a9bc9165
- Evidence SHA: cb9f83364523fc7575e1735910b8a525f5598321
- Protected evidence: outputs/grrr-43i8-protected-inspect/protected-install/

### AC Verification
| AC | Requirement | Evidence | Status |
|---|---|---|---|
| 1 | Independently reviewed exact migration/recovery plan and inventory without mutation | Review-approved proposal, read-only inspect baseline, independent plan review | PASS |
| 2 | Root-owned exclusive atomic registration preserving bytes/history | Exact reviewed plan/review staged; installer verify and direct postflight | PASS |
| 3 | Explicit cumulative ceilings; no reset/recast/stop release/zeroing | Receipt and postflight preserve ceilings, unknowns, holds, stopped DB | PASS |
| 4 | Recovery requires separate authorization/review and leaves promotion disabled | stopped=1; stop_release=false; no recovery command/run | PASS |
| 5 | Preflight/postflight identity/hash/ownership/profile/balance/stopped/fail-closed proof | Inspect, verify, direct root postflight, prior fault tests | PASS |
| 6 | Replay blocked on cumulative store; no fresh DB | Same inode/hash DB; execution_authorized=false; GRRR-z3w9 remains blocked | PASS |

LEARNINGS: Registration can safely alter only a root-owned binding while freezing the original evaluator-owned database. Direct protected postflight is necessary because code review and no-guest tests cannot prove installation state.
DISCOVERED_BUG: none in this protected execution.

## nd_contract
status: delivered

### evidence
- Protected install/verify/read-only postflight artifacts and hashes recorded.

### proof
- [x] AC #1: exact reviewed plan and inventory.
- [x] AC #2: reviewed root-owned registration.
- [x] AC #3: cumulative ceilings preserved without reset.
- [x] AC #4: stopped state and separate recovery boundary preserved.
- [x] AC #5: protected preflight/postflight verification.
- [x] AC #6: replay remains blocked on original cumulative store.

### 2026-10-24T13:31:44Z speed
## Implementation Evidence

Protected registration-only install completed at exact implementation commit 2dbf825e93376c6df5b974e339ea7846a9bc9165 using independently reviewed installer/baseline/review/plan hashes. Exact install and verify outputs plus direct root read-only postflight are preserved under outputs/grrr-43i8-protected-inspect/protected-install/. Original database inode and SHA256 remain unchanged; stopped=1; execution_authorized=false; no recovery/replay/promotion/admission/merge.

### CI/Test Results
Commands run:
- Exact protected install command.
- Exact protected verify command.
- Direct root read-only metadata/hash/SQLite postflight.
Summary: all PASS; prior focused 30/30 and full 228/228 suites passed on both required Pythons.

### Commit
- Branch: story/GRRR-43i8
- SHA: 2dbf825e93376c6df5b974e339ea7846a9bc9165

### AC Verification
| AC | Status |
|---|---|
| 1 exact reviewed inventory/plan | PASS |
| 2 root-owned registration preserving original DB | PASS |
| 3 cumulative ceilings/no reset | PASS |
| 4 separate recovery, still stopped | PASS |
| 5 protected preflight/postflight | PASS |
| 6 replay blocked on cumulative store | PASS |

## nd_contract
status: delivered

### evidence
- Install result, verify result, direct postflight, hashes, and receipt recorded.

### proof
- [x] All six GRRR-43i8 ACs verified.
