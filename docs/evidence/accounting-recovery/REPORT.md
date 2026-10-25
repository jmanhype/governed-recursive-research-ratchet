# GRRR-d8ji evidence — no-guest PASS; protected stop-only integration PASS

## Current protected result, 2026-10-25

This section supersedes all historical pending/live-blocked statements below.
Implementation commit `65bb7945299851c078f5b48e9083d3aee13a7c4a` passed final
exact-byte follow-up review (`READY_FOR_PROTECTED_RECOVERY_REVIEW`), followed by
independent plan review (`APPROVED_STOP_ONLY_RECOVERY_PLAN`). Separate operator
authorizations covered staging/review, stop-only install/verify, and controlled
refusal proof. Neither review alone was execution authority. The parent performed
the protected actions; this documentation-only delivery does not repeat them.

Exact approved closure and inputs (SHA256):

```text
88cf699236288ba989fcb2b21e5966720faadc13f420c83c0f64e99bade8760a accounting_recovery.py
db2d5965a78443fcd4205f8c73950ab0649876624fadfd79a17de086f3b1a038 accounting_registration.py
dfc4bfcfd56a2fe8cfbc4416f912829b35e2dced5c31b23f181cbed38f63b73f baseline
478cbae360092c5b6a9659516be75b0a2c7e9d9741509bfbb8b4d6468f77307e plan
94f9b8113b2b08595783d16223a2c10cdcde6b79de5c09076de1075de5fbec81 review
9235640b58b973913e9b14f2ade420085daeed91a1e048ad5b2b09da41079a60 authorization
```

Protected install and verify each exited 0. Active v3 SHA256 is
`9c5194dd12ff7601917fcccc293c459db09a41da8bad9fa9983cbef618d453f8`;
recovery receipt SHA256 is
`6d3d5b092c0ee8273a657c83823d8465b215f2b1b66ec627dfde2d96b21fe587`.
Original DB inode `682589447`, evaluator ownership/mode, store/campaign, ceilings,
schema and historical accounting were retained. The authorized stopped=1→0
transition changed DB SHA256 from
`2347a548429cd8bf07048e15898de1432c960d7a08743e17dc31d39efdb5bbaf` to
`9c6ff2561a364ed982cd5477dd4b200c995da6910c9a17aa3d3c411a962d64f3`.
Integrity is ok; state `1|0` means id=1, stopped=0, not a new allowance.
Reservations=11, metering=8, overhead=0, pending holds=3; known encumbered remains
`[0,1108265788,0]` in both cumulative scopes. Historical unknowns remain unresolved,
spendable=null, allowed mutations=[], execution_authorized=false.

Parent postflight verified immutable registration ancestry and exact preserved v2
prior-active SHA256
`97ad3cd38a90a71d412afccad5ed49fc73af73e5413edcc4e07a1e0d23f451c5`.
Recovery directory is 0555; exactly intent/prior-active/receipt/complete JSON files
are root:wheel 0444. No uncertain/next-active artifact remains. Locks/quiescence,
DB integrity and absence of evaluator/runner/QEMU were reverified by the parent.

Duplicate install with consumed authorization exited 1 with
`partial/unknown registration state`. A parent-staged, hash-pinned probe ran as
UID320: 12/12 mutations refused (reserve, meter, settle, disclose_overhead, halt;
connection and cursor execute/executemany/executescript; writable blobopen).
API calls returned read-only Failure, SQL returned DatabaseError/not authorized,
and BLOB returned Writable accounting BLOB handles are forbidden. The probe checked
hashes/state/counts after every refusal. Duplicate and probe postflights retained
the same active/DB hashes, inode, inventory and recovery artifacts:
all_refused=true, protected_state_changed=false, execution_authorized=false.
These are real controlled live refusals, not mocked unit substitutes. They do not
claim exhaustive live testing of every crash/tamper case covered by unit tests.

External raw evidence is retained at
`/Users/speed/Documents/Codex/2026-10-19/3e4m-b-4/outputs/grrr-d8ji-recovery-staging/`;
private accounting rows are not copied here. The two manifests
`protected-recovery-SHA256SUMS` and `refusal-proof-SHA256SUMS` bind:

```text
56476efca0fd6f379cca965eee5ebd0efe2ae1d0e97bc98f01a8a76c717df974 recovery-install.json
56476efca0fd6f379cca965eee5ebd0efe2ae1d0e97bc98f01a8a76c717df974 recovery-verify.json
18ba02d0e4044b2775abd09d6ddc06dd6834948ec6ff9d629a63f67dde5ce928 v3-protected-postflight.log
ccb69d1cf62fa6ec865b96b43dbf05bddc63ab2948292acbd7879b9ed34474ec duplicate-install-refusal.log
22202128007a20adf323ab8c6b00917c5e578bed0741142aea0c6ebf3f4baf0b duplicate-install-refusal-summary.log
6caf3d9be0aacb175aa1cbc4d115f0cc646c61135ef7015970181641191efdb1 v3-refusal-probe.json
18ba02d0e4044b2775abd09d6ddc06dd6834948ec6ff9d629a63f67dde5ce928 refusal-proof-postflight.log
```

### Current AC verification (supersedes historical table)

| AC | Evidence/status |
|---|---|
| 1 | PASS: exact contract/source, final follow-up and independent plan review; stop-only transition matches reviewed inputs. |
| 2 | PASS: parent before/after identities/inventory preserve cumulative history/holds/unknowns; only authorized stop/physical hash changed. |
| 3 | PASS: hash-bound intent/receipt/completion, immutable prior-v2/registration ancestry; partial-outcome unit cases retained. |
| 4 | PASS: 20 recovery/30 registration unit cases per interpreter plus duplicate refusal and 12/12 live runtime refusals; no protected-state change. Crash coverage remains bounded, not exhaustive power-loss proof. |
| 5 | PASS: developer tests had zero privileged effects; later parent effects had distinct exact authorizations; no authority inherited from registration. |
| 6 | PASS: both full suites 253/253 and focused gates below, zero failures/errors/skips/warnings at implementation commit. No code/tests changed in this documentation update. |
| 7 | PASS for this stop-only live gate: actual install/verify success and separately authorized refusals with parent postflights. PM acceptance remains independent. |

No spendability reconciliation, replay, promotion, admission, production mutation,
merge or push occurred. GRRR-z3w9 remains gated on its own capacity, identity,
review, spendability and replay approvals. Stop-only recovery is not spendable
recovery or permission to execute research. Current delivery authorization permits
only documentation, story commit/delivery and independent PM review.

## Historical post-reboot cessation fix, 2026-10-24 22:35 UTC

This section supersedes the historical full-suite blockers below. Capacity was
21GiB free at verification; fixed disk floors and all existing assertions remain
unchanged. No privileged/protected recovery, guest, replay or production action ran.
The operator authorized the focused cessation fix and commit if verification was
clean; this is not delivery, live acceptance, merge or push authorization.

Diagnosis: the original exact Python3.9 test passed 5/5 before editing and an
instrumented run observed normal TERM→KILL→absence. Thus the original intermittent
host observation failure's cause was **not established**. A deterministic single
TERM-inventory timeout reproduced its False!=True symptom while real SIGKILL and
fresh absence succeeded: phase-global uncertainty incorrectly poisoned the KILL
result. Uncertainty now resets only upon entering the KILL phase. Failed/uncertain
KILL observation still fails closed. Inventory arriving after the global deadline
is rejected. TERM 5s, KILL 2s, ps 0.2s cap and total 7s remain unchanged.
Two of five new regressions failed before the fix and all five pass afterward.
The actual process-group assertion/helper is unchanged. Only one root-launcher
source hash pin was refreshed; no launcher execution or installation occurred.

Both `/usr/bin/python3` 3.9.6 and `/opt/homebrew/bin/python3` 3.14.3:

| Command (per interpreter) | Result |
|---|---|
| `-m unittest tests.unit_replay_smoke.RuntimeSmoke.test_real_term_resistant_group_is_killed_within_deadline` repeated five times | 5/5 passes |
| `-m unittest discover -s tests -p unit_replay_cessation.py` | 5/5 passes |
| `-m unittest discover -s tests -p unit_replay_smoke.py` | 12/12 passes |
| `-m unittest discover -s tests -p unit_replay_accounting_recovery.py` | 20/20 passes |
| `-m unittest discover -s tests -p unit_replay_accounting_registration.py` | 30/30 passes |
| `-m unittest discover -s tests -p 'unit_*.py'` | 253/253 passes, including all nine genesis tests |
| `-m py_compile research/replay_smoke.py tests/unit_replay_cessation.py scripts/replay-root-prepare` | exit0 |

All final commands exit0; zero failures/errors/skips/warnings. Coverage not measured.
`pvg verify research/replay_smoke.py tests/unit_replay_cessation.py scripts/replay-root-prepare --format=text`
passes (2 code/test files scanned, 0 issues); `git diff --check` passes.
At that checkpoint AC6 passed; AC7 separate authorized live integration was
NOT RUN (superseded above). The earlier independent recovery-package review did not imply independent
review of this later cessation fix or grant protected execution authority.

Raw files remain under `outputs/grrr-d8ji-no-guest/` in the enclosing workspace:

```text
b2825f94a76a2d04969b993942c80b7e4b5906d19dddeae848219d25ad4eb433 cessation-final.txt
cea7416ab3ee29424a8c267f0c5751287f645860598d4dee8d8403d20bec1639 cessation-red.txt
b31a3e904d7fa42ef901e6f7de285878e24ab2bdcb6b0f0ec9c87a77a6b85928 cessation-repeat-before.txt
a2f1dfad2c31d76ac2762ae544df8a070faabd70d570394857b64b4201f26d6e cessation-before.txt
79d5a5ae84b498ad4ac84e0e9e7dbbc245295b424ecf9353ecaee67c4ab7d42b cessation-before-pin-refresh.txt
819ab8e37ebaf138eca6b69abee78bf356124809b64ca60c28ecd5b957749612 research/replay_smoke.py
d3ee8811a442d02936ee39c4eb16c608c12f4caeba8f163158841f461737bbd2 tests/unit_replay_cessation.py
5908b3134f2cc13bc6c10e046630c0e0bfe8742618acc36a75be855e6b645a8c scripts/replay-root-prepare
```

## Historical pre-reboot blocked evidence (retained, superseded above)

2026-10-24. Branch `story/GRRR-d8ji`, base HEAD
`6afd643df51aa6a2f046512dfc3fbe7572dd8d67`. The operator explicitly authorized
committing this independently reviewed stop-only recovery WIP to `story/GRRR-d8ji`.
This authorizes no delivery/acceptance, merge, protected recovery, stop release,
replay, promotion, admission, production mutation or push. No live success is claimed.
Independent exact-byte security/architecture review returned
**SECURITY_REVIEW: READY_FOR_COMMIT_REVIEW**: no blocking design defect found;
reviewer independently reran recovery 20/20 and registration 30/30 on both Pythons.
This is not delivery acceptance or protected-execution approval. Crash-durability
coverage is limited to tested publication stages, not exhaustive kill/power-loss/
fsync failures. All seven reviewed hashes were verified before this report-only
status update; source, tests, contract and external raw evidence remain unchanged.

## Raw evidence

Complete first-run failures and post-repair runs retained outside this package:
`/Users/speed/Documents/Codex/2026-10-19/3e4m-b-4/outputs/grrr-d8ji-no-guest/no-guest.txt`

SHA256 `aa41940ba6288b4a97642188a7b95ed67f32e2e3a26894dd872180034b99015d`.
Earlier first-run source changed during verification; its end hashes are explicitly
not attributed to the earlier failing source. Final post-repair hashes below are
the exact source used for the final runs. Raw logs are external solely to preserve
the story's approximate diff budget; no failed output was discarded.

## Historical pre-reboot measured results (superseded)

| Command suffix | /usr/bin/python3 3.9.6 | /opt/homebrew/bin/python3 3.14.3 |
|---|---|---|
| `-m unittest discover -s tests -p unit_replay_accounting_recovery.py` | 20 run, pass, exit0 | 20 run, pass, exit0 |
| `-m unittest discover -s tests -p unit_replay_accounting_registration.py` | 30 run, pass, exit0 | 30 run, pass, exit0 |
| `-m unittest discover -s tests -p 'unit_*.py'` | 239 run, 1 failure, 1 setup error, exit1 | 239 run, 0 failures, 1 setup error, exit1 |
| `-m py_compile research/accounting_recovery.py research/accounting_registration.py research/persistent_budget.py tests/unit_replay_accounting_recovery.py` | exit0 | exit0 |

Final runs report zero explicit skips and no warnings. **Nine ConservativeGenesis
tests did not execute** because class setup failed; these are not green/skipped
passes. Both failed the unchanged `15_350_000_000` byte preparation-space floor at
`scripts/conservative-genesis:85`; disk measured about 12GiB free. No cleanup or
floor change was performed. Python3.9 additionally failed
`RuntimeSmoke.test_real_term_resistant_group_is_killed_within_deadline` at
`tests/unit_replay_smoke.py:153`: cessation result False versus expected True.
No process timing, replay code or assertions were changed to mask this failure.

`pvg verify research/accounting_recovery.py research/accounting_registration.py research/persistent_budget.py tests/unit_replay_accounting_recovery.py docs/ACCOUNTING-RECOVERY.md --format=text`
reported `VERIFY: PASSED (4 files scanned, 0 issues)`, exit0. `git diff --check`
exit0. Coverage instrumentation not measured. Live integration: **0 executed**.

## Historical reviewed package SHA256 (contract document since updated)

```text
88cf699236288ba989fcb2b21e5966720faadc13f420c83c0f64e99bade8760a research/accounting_recovery.py
db2d5965a78443fcd4205f8c73950ab0649876624fadfd79a17de086f3b1a038 research/accounting_registration.py
78f0e145d902dbeadbb1693055551dfdf59aee16d1bc2d5fd4bc4c403bcaaf32 research/persistent_budget.py
ff52097fa7ba0002ea9df2600afbc388a46a48efa3c8c08718f011f135281d5e tests/unit_replay_accounting_recovery.py
88635272ae4f4b7d475f5832bcdb56b265cb2d512f97e3ca1faee6f962521e8c docs/ACCOUNTING-RECOVERY.md
```

## Historical pre-reboot AC status (superseded)

| AC | Evidence/status |
|---|---|
| 1 | Exact stop-only contract and implementation reviewed: READY_FOR_COMMIT_REVIEW, not execution approval. |
| 2 | Real temporary SQLite success preserves schema/history/holds/identity; three-pending/exact-ceiling case passes; unknowns remain unresolved/null. |
| 3 | Canonical intent/result/completion and uncertain outcomes tested; original ancestry retained. |
| 4 | Authority, hashes, tamper, sidecars, inode/mode/link, real competing locks, partial publication, runtime/inherited/SQL/BLOB/stale guards tested; review READY_FOR_COMMIT_REVIEW, with crash-coverage limits above. |
| 5 | No privileged effects, protected reads/writes, guest or replay operations. |
| 6 | BLOCKED: full suites not clean; nine tests unexecuted per interpreter. |
| 7 | PENDING: separately authorized parent live integration and reviewed exact-byte staging. |

## Learnings and additional blockers

- An isolated standalone entrypoint must not alter sys.path: fixed the initial
  import-closure regression with fixed-file importlib loading after root/ACL checks.
- Python3.14 exposed a test's unclosed SQLite connection: fixed with closing();
  final suites contain no recurrence of that ResourceWarning.
- Worktree vault search failed: `pvg notes search 'accounting recovery'` reported
  missing worktree `.vault`. No unrelated vault repair attempted.
- Graph index covered only a stale downstream worktree; accounting sources were
  read directly rather than claiming current graph coverage.
