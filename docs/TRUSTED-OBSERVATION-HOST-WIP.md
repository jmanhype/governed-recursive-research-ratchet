# GRRR-gu87 — dedicated host adapter, unexecuted WIP

This checkpoint is development/review only. No root launcher, QEMU process, guest
candidate, paid request, admission, production mutation, or push was executed.
The story remains claimed/in progress, not delivered. Source implementation
checkpoint: `87a8766`; subsequent evidence-only/check adjustments accompany this
document. The diff exceeds the original story size guidance and still requires
independent security/PM review.

## Exact bindings

| Artifact | SHA-256 |
|---|---|
| Original proposal | `1830a92ad2cbd91788051304ec8f6acaebf256b85065b2db2c07271b6906e3f6` |
| Pinned v3 supervisor | `a9a0fd9a8471bc1859e5ab91c3746a139942562f719784fec51b8254eb8307d6` |
| Pinned detached ISO | `799ec744f27e7329686e5acb8a3e1f663c82a321f7bc1d4bc940ea5c97068233` |
| Prepared profile | `3edebcd4b85ae7ce666d953bd3c5527606a7043c42294a0f60000875f8d2eec0` |
| Development-only binding | `9fd432900036552fcdeb95ed1433937e01fbc45b73250aba91f6ed87a0efc209` |
| Preparation receipt | `775a767ca74f9c18678fc998111b0c9870df1a68db68e453b6af0c50ae9d6c0c` |
| Host code inventory (canonical JSON mapping) | `8f4c4aec14549d3d0f458e4cf0fc3837d19586e539ed38716d8fcdb7db423fc8` |

`scripts/review-trusted-host` regenerates the host code inventory without starting
services or checking launch eligibility. Its output explicitly denies execution
authorization. `scripts/verify-trusted-preparation` independently rechecked all
7 ISO entries and 52 source entries against the retained receipt. Guest source,
bootstrap, supervisor, helper and detached ISO are unchanged. Existing approved
synthetic/offline launchers and resource profiles are unchanged by this checkpoint.

## Fixed profile boundary

- RAM 1024 MiB, 1 vCPU, `/work` tmpfs 512 MiB.
- Boot 30 s; command 240 s; total invocation 300 s. Host watchdog fires no later
  than 293 s, leaving 5 s TERM grace and 2 s kill wait. Deadline negative control
  shortens its own watchdog to 1 s, never expands it.
- Stop acknowledgement target 2 s; TERM grace 5 s; force-kill wait 2 s.
- Guest serial output cap 1,048,576 bytes; IPC wire cap 3,145,728 bytes; inner
  candidate capture cap 524,288 bytes.
- Minimum host free space 15,000,000,000 bytes, checked before staging, after
  staging, and before dispatch. Latest binding read measured 14,683,729,920 bytes:
  **below floor**. No space-threshold override or cleanup performed.
- Host evaluator UID/GID 320/320; executor 321/321. Root owns immutable staged
  code/config/assets under a fresh `/private/tmp/grrr-trusted-*` runtime.
  Evaluator evidence/store directory is 0700 UID 320; runner scratch is 0700
  UID 321. Clones use APFS `clonefile` only, no full-copy fallback; every clone
  and source-code copy is rehashed.
- Guest supervisor UID 0; candidate UID/GID 1000/1000, empty groups, empty
  capabilities, no-new-privileges, no controlling TTY or supervisor control
  descriptor. These remain **implementation properties awaiting guest proof**.
- QEMU fixed `virt`/HVF/host CPU, readonly detached input block device, no
  networking, host shares, monitor, paid dispatch, or host candidate fallback.

## Staged implementation

`research/trusted_execution.py` is a separate service, not an alternate mode of
the synthetic/offline executor. Kernel peer identity must be UID 320. Metadata
has an exact allowlist; no caller command, path, role or expectation is accepted.
Duplicate dispatch keys bind the complete request; pending effects cannot be
retried. A stop fence is checked again immediately before process creation.

`research/trusted_evaluation.py` holds the protected expected bytes, reserves
300 seconds before any dispatch, persists the request, validates receipts and
kernel/supervisor bindings, and charges the larger trusted execution/evaluator
elapsed measurement. Missing/incomplete/overrun receipts retain the maximum.
Candidate stdout remains base64 data. A control receipt cannot authorize
correctness, independent replay, review, or admission.

`scripts/trusted-identity-integration` requires separate root-owned, single-link,
read-only approval and license-review records with exact schema and hashes.
Nonroot `--run` fails before any planning/staging. `--dry-run` never creates a
runtime or service. Runtime/evidence remain private and are retained for parent
inspection rather than deleted.

The ten real integration scenarios are staged in
`tests/integration/trusted_observation.py`:

1. VM-ready pre-candidate stop, acknowledgement/cessation bounds, retained hold.
2. Clean real guest supervisor/locking observation and exact protected content.
3. Forged PASS, changed expectations, malformed candidate text and oversized
   capture, without admitting correctness.
4. Actual candidate mutation/control impersonation and host identity denials.
5. Actual service unknown/missing fields, role/command injection, epochs,
   truncated/duplicate/nonfinite/oversized wire data, traversal/symlink/executable
   artifact rejection without dispatch.
6. Actual evaluator SQLite atomic ceilings, carry-forward, concurrency, unknown
   maxima, delayed receipt, additive replay/review/overhead and exhausted store.
   Reuses only the identity-neutral BudgetChecks mixin; no identity substitution.
7. Reservation is not a dispatch lease; fenced/stale-epoch launch and missing
   receipt do not release holds.
8. Lost executor response recovered through status, then exact duplicate returns
   the existing receipt without another launch; changed request rejected.
9. Actual bounded watchdog termination, stopped service, retained unknown cost.
10. Actual SQLite page exhaustion before effect; no new guest launches.

These tests have **not run under the required identity/profile**. They contain
no skip or synthetic service replacement. A failure in one scenario can leave
the fail-closed service halted; later failures are not converted to skips.

## Measured verification

Evidence: `docs/evidence/trusted-observation/host-adapter-wip/`.

- Full Python unit suite: **59/59 pass**; 9 newly added host contract tests.
- Python `trace --count --missing --summary`: trusted executor **41.8%**,
  trusted evaluation **50.0%**, dedicated launcher **18.5%** executed-line coverage.
  This is not branch coverage or privileged integration coverage. The initial
  trace invocation without `--missing` was unsuitable for denominator coverage;
  the retained log is the corrected run. `coverage.py` was unavailable.
- `pvg verify` explicit new/changed paths with `--include-tests --format=text`:
  **5 recognized files scanned, 0 issues**. First scan flagged a handled
  BrokenPipe `pass`; replaced with an explicit bounded-wire assertion and rescanned.
- `py_compile` all seven new/changed host/harness/review files: exit 0.
- Independent pinned preparation read-back: exit 0, **7 ISO / 52 source files**.
- Dedicated launcher dry-run: exit 1, `BudgetExceeded`, unchanged 15 GB floor.
- Nonroot dedicated `--run` with absent approval/review paths: exit 1,
  `Unauthorized`, before planning or side effects.
- `./scripts/test-story trusted-observation`: exit 1; **10 required, 0 executed,
  0 skipped, 1 identity setup error; mandatory guest gate not-run**.
- `git diff --check`: exit 0.

### AC Verification

| AC | Current evidence | Remaining |
|---|---|---|
| 1 | Dedicated bounded adapter and evaluator-owned expected data, unit contracts | Actual approved service/guest invocation |
| 2 | Parser/receipt unit negatives; real service/guest negatives staged | Run all mandatory negative controls |
| 3 | Existing pinned supervisor/UID separation unchanged, independent byte read-back | Actual candidate mutation, impersonation and lock schedule proof |
| 4 | Atomic accounting unit tests; actual UID store tests staged | Real identity proof and independent cross-profile accounting review |
| 5 | Hold/settle/epoch tests; trusted meter path staged | Actual missing/delayed response and overlap/review proof |
| 6 | Real watchdog/lost-response/store exhaustion suite staged | Execution authorization, space floor and parent run |

No AC is declared proven by this WIP. Cross-profile persisted budget lifecycle,
process restart/recovery behavior, mandatory execution coverage and the expanded
security-sensitive diff require independent review before delivery.

## Exact remaining authorization and parent command

Recommended operator text (not consent granted by this document):

> I authorize parent-mediated execution of the ten trusted-observation controls
> using supervisor SHA-256 a9a0fd9a8471bc1859e5ab91c3746a139942562f719784fec51b8254eb8307d6,
> detached ISO 799ec744f27e7329686e5acb8a3e1f663c82a321f7bc1d4bc940ea5c97068233,
> prepared profile 3edebcd4b85ae7ce666d953bd3c5527606a7043c42294a0f60000875f8d2eec0
> and host code inventory 8f4c4aec14549d3d0f458e4cf0fc3837d19586e539ed38716d8fcdb7db423fc8,
> under the unchanged limits above, only after the 15 GB free-space floor and
> exact local-use compiler/toolchain provenance review pass. No resource
> expansion, paid calls, host fallback, production mutation or automatic
> admission is authorized. A passing control is not candidate admission.

Parent must separately record actual local-use approval of host compiler
`e670dfa79b080bad7f7d6b1d7131145c8c49068096650ebf0ac6292f098db60d`
and guest Go toolchain
`3f4227ce7b206a513e794f1393adb473a07b46e94d18bd15d1c684bbb7319797`.
No execution/license approval records exist from this checkpoint.

After actual approval, root-owned mode 0444 single-link JSON records must match
`validate_approval`'s exact schema. The execution record binds `host_code`,
`profile`, `image`, `supervisor`, actual operator UID, version 1, decision
`approved-trusted-execution`, SHA-256 of canonical license-review JSON, and the
SHA-256 of the actual authorization record. License review binds version 1,
decision `approved-local-use`, preparation receipt, compiler, guest toolchain
and actual authorization record hash. Placeholders cannot pass.

From this worktree, parent identity command, **not run**:

```text
AWAITING_PARENT_IDENTITY_RUN
python3 scripts/trusted-identity-integration --run ../../../.tmp-sr_pm/vm .tmp-sr_pm/trusted-observation/prepared-v3 /private/tmp/grrr-trusted-execution-approval.json /private/tmp/grrr-trusted-license-review.json
```

Do not execute this command before separate operator approval and satisfying the
space floor. It must be invoked by the parent through its authorized root
identity path, not by storing or requesting credentials. Preserve the existing
worktree/prepared-v3 assets; do not silently regenerate or repin them.
