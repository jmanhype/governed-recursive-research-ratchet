# Independent replay accounting: blocked proposal

Story: GRRR-43i8. Status: **draft, not approved, not installed**.

This document confers no registration, recovery, replay, promotion, admission,
paid-dispatch, or privileged execution authority. The accepted GRRR-w1lt runtime
smoke does not approve this accounting change. Current story ACs are not met.
There is deliberately no executable installer in this package: missing approved
ceilings, verified baseline inventory, independent review, and operator decisions
must not be replaced by author-chosen defaults or a runnable privileged draft.

## Observations and evidence boundary

Source inspected at epic HEAD `295edd4` (2026-10-23):

- `research/persistent_budget.py` permits exactly synthetic, offline, and
  trusted-observation. It requires the same three-profile list in active.json.
- `research/budget.py` aggregates actual settled usage and full outstanding
  reservation maxima. POC consumption also consumes milestone allowance.
- The current successor installer creates a fresh database. It is **not** a
  suitable replay registration mechanism and must not be reused for that purpose.
- Matching duplicate reservation requests return before the stopped-bit check.
  The return includes `dispatch_lease=False`, but this ordering is insufficient
  for the stronger proposed rule that stopped accounting refuses every reserve.

The following are parent-reported read-only observations, not worker measurements:

| Item | Parent-reported value |
|---|---|
| Active binding | `/Library/GRRR/accounting-poc2/active.json` |
| Binding SHA-256 | `e5629ee930fc909b38bcdf8c6cdbd673233651b1b507d73a2230f4ce1e304c95` |
| Campaign | `9ea9cd9b2669bc0d3fe119d722224907e1bbb06a4ca28f860c8044e2491092a9` |
| Store_id/directory basename | `901acaff42b5a42f667b1c435beba9a9ae8312539cc36eb023c45584fd2e06d6` |
| Prior-history receipt | `9f64395bec815a6bb2281d3b5d96d2356899138b1929b0a9881c16483c486dde` |
| Database SHA-256 | `2347a548429cd8bf07048e15898de1432c960d7a08743e17dc31d39efdb5bbaf` |
| Device | 16777229 |
| Active inode/owner/mode | 682589456, root:wheel, 0444 |
| Store directory inode/owner/mode | 682589446, _grrr_evaluator:_grrr_evaluator, 0700 |
| Database inode/owner/mode | 682589447, _grrr_evaluator:_grrr_evaluator, 0600 |
| SQLite integrity_check | ok |
| State rows | `(id=1, stopped=1)` |
| Reservations | 11 |
| Metering rows | 8 |
| Unsettled/uncertain holds | 3 |
| Overhead rows | 0 |
| Metered aggregate | approximately 203.3 execution seconds, zero USD |

The story has a store_id typo (`...be7c...`): the parent's subsequent direct
read-only check confirmed `...beba...` in both active binding and store_identity.
The story history is not rewritten here. Exact integer usage vectors, hold maxima
and stages, row bindings, stop provenance, complete permission/ACL inventory, and
prior unknown-history disposition were not supplied to this worker.
Approximate elapsed time is not a
balance; counts are not proof of settlement. These unknowns remain unknown.

## Recommended ceilings, explicitly not approved

Recommend retaining the existing cumulative ceilings without any increase:

| Scope | USD cents | Execution microseconds | Review microseconds |
|---|---:|---:|---:|
| POC | 5000 | 21600000000 | 3600000000 |
| Milestone, inclusive of POC | 15000 | 86400000000 | 10800000000 |

Independent replay would use the **remaining POC allowance**, not receive another
POC-sized allowance or bypass POC by selecting milestone. These are recommended
upper bounds shared by all profiles, not a proposed new profile balance. A tighter
replay-specific cap or per-run maximum needs an explicit decision before coding.
No current record approves an independent-replay budget.

For dimension d and cumulative scope s:

    known_encumbered[s,d] = sum(validated_actual[d] for settled rows in s)
                         + sum(maximum[d] for all unsettled rows in s)

All POC rows belong to milestone as well. A meter row without a validated
settlement does not release its maximum. Preserve original reservation ids,
keys, binding bytes, run/stage values, maxima, actuals, receipts, and overhead.
Do not relabel any corpus/smoke row as replay. Do not net overhead against execution.
Unknown historical usage has no numeric zero representation: keep the stop and
report spendable balance as unavailable until independently resolved. Even when
known_encumbered is below a ceiling, that is not proof of usable headroom.
Negative headroom, over-maximum settlements, orphan receipts, missing rows, and
unknown stages or currencies cause refusal, not repair.

## Proposed registration transaction contract

Registration changes only root-owned profile authorization metadata. It must not
write, copy, replace, rebuild, VACUUM, initialize, settle, or clear the database.
The existing database's bytes, inode/device, identity, and stopped state remain
unchanged. The current store must exist; refusal of *existing registration output*
must not be confused with refusal of the required existing cumulative database.

Before any filesystem write, the future root-only standalone installer must:

1. Require a reviewed root-owned immutable installation location, exact isolated
   interpreter/toolchain identity, restricted modes, safe ancestors, no symlinks,
   no extra hardlinks, no ACLs, and bounded no-follow reads. Checkout code must
   never be imported by a privileged installation path.
2. Require a signed-off plan digest and distinct operator authorization bound to
   that exact plan and independent review artifact. Neither a field named
   approved nor an authorization string generated by the installer is approval.
3. Hold the existing accounting launch lock exclusively/nonblocking and every
   reviewed caller launch lock in one fixed order. Prove all evaluator/runner
   processes and QEMU are absent. Document all writers and their lock protocol;
   an advisory lock alone does not serialize a noncooperating writer.
4. Capture immutable before-images of active bytes and schema/row inventories,
   hashes and metadata. Verify exact database device/inode, schema and integrity,
   canonical unique-field JSON, store_identity, stopped=1, all settlements and
   uncertain holds. Require an exact closed inventory of namespace files and
   reject journal/WAL/SHM, unexplained tables/triggers, or partial artifacts.
5. Compare the full baseline with the reviewed plan; refuse stale hashes or any
   changed field. Validate unchanged cumulative ceilings and profile uniqueness.
   Reject an existing registration receipt, staged output, or interrupted attempt;
   never auto-clean, overwrite, resume, or silently re-run it.

Only after every precondition passes may it create root-owned exclusive restricted
staging artifacts. Save exact old binding bytes as immutable evidence; produce a
new binding version that explicitly registers independent-replay and binds the
reviewed plan/receipt and unchanged database identity. Fsync staged artifacts and
directory. Repeat baseline and process/lock checks immediately before an atomic
binding publication. Preserve the old binding bytes in the evidence archive.

Multiple-file publication is not magically atomic. The future design must specify
one final atomic activation point and require a matching complete receipt on every
runtime open. If activation fails, the old binding must stay valid and stopped;
if activation succeeds but verification fails, the new binding must remain
unusable/stopped. No compensating database reset or automatic stop release.
Any partial state requires a new separately reviewed recovery plan.

Runtime schema changes should accept the exact legacy three-profile binding and
the exact new receipt-bound version, not arbitrary subsets/supersets. A legacy
binding still rejects independent-replay. A new binding requires all registration
evidence and the same physical cumulative database. Profile membership is not
launch authority. Every `reserve`, including duplicate keys and zero vectors,
must check persisted stopped state before returning. The latter is a targeted
Budget behavior change requiring downstream duplicate/idempotency regression tests.

## Separate recovery contract

Registration must finish with stopped=1. There is no `--resume` option, recovery
subcommand, implicit success-path stop clear, or automatic allowance release.
Stop recovery needs a second operator decision and independent security review
after registration verification. It must identify the stop cause, account for
every unresolved hold and historical unknown, prove baseline history intact, and
state the precise recovery transition. Unknowns cannot be declared zero merely
to fit available ceilings. If safe recovery cannot be proven, stay stopped.
Promotion and admission stay disabled even if future bounded replay is authorized.

## Required implementation and tests after decisions

No tests below are claimed implemented or executed by this proposal.

- No-guest fixture tests: exact legacy/new binding schemas; duplicate fields,
  unknown profiles, bool/integer confusion, extra keys and profile-order changes.
- Settled actuals plus every full uncertain maximum carried forward in both
  scopes; orphan/changed receipts, actual above maximum, missing identity/state,
  malformed/unknown vectors and unknown-history refusal.
- Boundary tests per dimension: exact remaining ceiling allowed only when
  separately recovered; one unit above denied; profiles share the same store;
  milestone includes POC; no fresh database fallback.
- Stopped new, duplicate, changed duplicate, and zero-vector reserve all refuse;
  reopening cannot reset stop. Registration preserves every database byte.
- Non-root refusal before writes; wrong bootstrap/interpreter/modes/owner/ACL,
  symlink/hardlink, busy lock/process, stale baseline and unsupported journal mode.
- Fault injection at every publication boundary; partial/existing output refused;
  exact before/after bytes, metadata, hashes and device/inode preservation.
- Full no-guest suites on both supported Python interpreters, compilation,
  explicit-path pvg verify, diff checks, measured coverage, and independent review.
- Separately authorized parent-mediated protected integration with captured
  before/after hashes, ownership/modes/ACLs, identity, exact totals/holds, profile
  registration and stopped-state refusal. No mocked test substitutes for this.

## Operator/reviewer decisions required

1. Confirm authoritative active/store/receipt identity and supply a redacted exact
   read-only inventory with integer usage/hold vectors and stop/unknown provenance.
2. Approve or change the recommended shared ceilings, replay stage and any narrower
   replay/run cap. Confirm there is no new campaign/store/allowance.
3. Authorize bounded implementation of registration-only code/tests and independent
   security review. This is separate from approval to install the reviewed result.
4. After review and tests, approve the precise protected installer/plan hashes and
   parent command. A runnable privileged command cannot be given honestly before
   those artifacts exist. The intended future interface is
   `register-independent-replay install PROTECTED_PLAN PLAN_SHA256 AUTHORIZATION`;
   **that command does not exist and must not be executed**.
5. Decide separate stop recovery only after unresolved history is accounted for.
   Registration approval alone never permits recovery or actual replay.

GRRR-z3w9 remains blocked. This proposal is not delivery of GRRR-43i8, and no
protected installation, root/sudo operation, QEMU/VM, stop release, or replay was run.

## Draft verification, not implementation proof

No production code was changed. Baseline commands run from story worktree at
`295edd4` on 2026-10-23:

| Command | Measured result |
|---|---|
| `/usr/bin/python3 -m unittest discover -s tests -p unit_successor_accounting.py` | Python 3.9.6: 7 passed, 0 failures, 0 skipped |
| `python3 -m unittest discover -s tests -p unit_successor_accounting.py` | Python 3.12.7: 7 passed, 0 failures, 0 skipped |
| `/usr/bin/python3 -m unittest discover -s tests -p 'unit_*.py'` | 198 passed, 0 failures, 0 skipped, 19.822 seconds |
| `python3 -m unittest discover -s tests -p 'unit_*.py'` | 198 passed, 0 failures, 0 skipped, 28.026 seconds |
| `/usr/bin/python3 -m compileall -q research` | exit 0 |
| `python3 -m compileall -q research` | exit 0 |
| `pvg verify docs/REPLAY-ACCOUNTING-RECOVERY-PROPOSAL.md --format=text` | PASS, **0 files scanned**, 0 issues; not a Markdown/content security review |
| `git diff --check` | exit 0; proposal still untracked at time of initial check |

Baseline suite logs are local `/tmp/GRRR-43i8-{focused,full}-py{39,312}.log`.
Coverage was not measured. These tests prove only the unchanged baseline; the
proposed migration and recovery have no execution coverage or integration proof.
No mandatory integration test was represented as passed or skipped; privileged
integration is not run and blocks delivery.

Environment diagnostics: repository `docs/findings/` and repository AGENTS.md
were absent. `pvg notes search 'persistent budget'` failed because this worktree's
local `.vault` directory does not exist; issue reads through `pvg issues` worked.
Code graph inventory had no index for this worktree, so source reads were used.
