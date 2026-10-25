# GRRR-43i8 completed protected registration

Historical registration checkpoint, reconciled 2026-10-24. **Install PASS; verify PASS; read-only
postflight PASS.** This supersedes pre-install blocked/not-run statements in the
proposal, implementation narrative and earlier evidence files. It does not erase
their historical test results or grant further authority.

The stopped-v2 hashes/state and recovery-not-run statements below describe this
registration checkpoint only. See the later
[stop-only v3 recovery/refusal report](../accounting-recovery/REPORT.md) for current
protected state. Reconciliation and replay remain denied; historical measurements
and registration ancestry are retained unchanged.

The separately authorized parent performed protected operations. This follow-up
worker only read captured artifacts and updated documentation; no implementation
or protected state changed. Raw protected logs, reservation rows and private
baseline contents are deliberately not copied into the repository.

## Exact artifact hashes (SHA256)

| Artifact | SHA256 |
|---|---|
| Installed registration bootstrap | `74975c0da25303f05a7701008d87a22be7d8e6ed029bdee619f626a0d6ee10ab` |
| Canonical baseline object | `a0c0d9770f8cc90c7eaa31f0cb13f672b5be0e84c4030f582f2b0e83c751ee5f` |
| Independent registration review | `fe0cfdc4d761630801e7c2b5c4266c36e933f0b16ee23d31f34f43871417d8eb` |
| Approved registration plan | `24e6fa0d6ae3f9bd4a4cd8dec8dcf1f8d464c2eec0e61224516c91ee2f74341c` |
| Registration receipt | `fb2132f1dce4867d0a28895215ef9d5f9ad1ea947b3a373de5efd7ddad04f397` |
| Published active binding | `97ad3cd38a90a71d412afccad5ed49fc73af73e5413edcc4e07a1e0d23f451c5` |
| Unchanged cumulative database | `2347a548429cd8bf07048e15898de1432c960d7a08743e17dc31d39efdb5bbaf` |
| Preserved prior active bytes | `e5629ee930fc909b38bcdf8c6cdbd673233651b1b507d73a2230f4ce1e304c95` |

Baseline hash is of the canonical baseline object, not the inspect output file;
the captured inspect.json file hashes to
`0ab4ee35d5a8c2790228409624273c4ba0882b976597ef2f58ed6bec1a8e0e11`.

## Verified state and preserved accounting

- Binding version **2**; profiles exactly `synthetic`, `offline`,
  `trusted-observation`, `independent-replay`.
- `registered=true`, `stopped=1`, `pending=3`, `execution_authorized=false`,
  `stop_release=false`; stage `poc`.
- Known encumbered POC **[0,1108265788,0]**, milestone inclusive
  **[0,1108265788,0]**, units USD cents / execution microseconds / review microseconds.
- Historical unknowns **unresolved**; spendable **null**, not zero or fresh allowance.
- 11 reservations, 8 metering records, 0 overhead records; no history was recast
  as independent replay. Database integrity_check returned `ok`.
- Campaign `9ea9cd9b2669bc0d3fe119d722224907e1bbb06a4ca28f860c8044e2491092a9`;
  store `901acaff42b5a42f667b1c435beba9a9ae8312539cc36eb023c45584fd2e06d6`.
- Database device/inode **16777229/682589447** retained; store directory inode
  **682589446** retained. Database owner _grrr_evaluator:_grrr_evaluator, mode 0600;
  directory mode 0700. New active/receipt/prior-active are root:wheel 0444;
  registration directory root:wheel 0555. Published active inode **684971692**.
- Postflight closed inventories contain only the expected store database and
  registration receipt/prior-active files; no staged next-active remains.

## Evidence provenance and verification

Captured evidence root:
`outputs/grrr-43i8-protected-inspect/` in the enclosing workspace. Its nested
`protected-install/` directory contains the parent outputs (not a sibling path).
This follow-up verified all **6/6** inspection manifest entries and all **6/6**
installation manifest entries against their bytes, then independently checked
canonical binding/receipt/baseline hashes and the non-sensitive state above.
No raw artifacts were added to Git.

| Captured output | SHA256 |
|---|---|
| protected-install/install.json | `c5a51609361df040bd721e54748a150cde8b42a52acd13d2e0deaf06669b8796` |
| protected-install/verify.json | `da536ef3703e2382b88bb46be3b9c738e74deaaa3376a09d83ac7000226484b8` |
| protected-install/postflight.log | `bb1c8df2a005253411002243b63009a6a2eabab5f23458021b034f42bff7365c` |
| protected-install/summary.txt | `886912d7a1ce8fb6093ded58a28abeff08aca0d95298f7f53133c277929d66f2` |

## Acceptance-criteria disposition

| AC | Registration-only evidence/result |
|---|---|
| 1 | Reviewed plan and canonical baseline identified the active store, stop, history and unresolved unknowns without resetting them; PASS. |
| 2 | Parent protected installation and receipt verification PASS; same DB bytes/device/inode, prior binding bytes and cumulative holds retained. |
| 3 | Unchanged cumulative ceilings, POC registration, retained holds and null spendable balance; no fresh allowance, stop release or relabeling; PASS. |
| 4 | Separate recovery authorization/review requirement retained; no recovery command or side-effect stop release. Recovery itself remains denied/not-run, not claimed complete. |
| 5 | Captured inspect/verify/postflight identities, hashes, metadata and closed inventories PASS; earlier unit evidence covers tamper/partial refusal. |
| 6 | Registration does not satisfy replay gates. Stopped state and execution_authorized=false persist; actual replay remains denied/not-run. |

**Recovery, stop release, actual independent replay, promotion, admission and merge
are denied/not-run.** No push occurred in this follow-up. Do not rerun the installer
or infer recovery/launch authority from registration success. PM acceptance of this
documentation correction remains a separate step; no merge is implied.

## Documentation-correction checks

- `/usr/bin/python3 /tmp/grrr43-verify-install-evidence.py`: 6/6 inspection and
  6/6 installation manifest hashes PASS; canonical binding/receipt/baseline identity
  and stopped-accounting summary assertions PASS. Helper reads captured files only.
- `/usr/bin/python3 -m unittest discover -s tests -p unit_replay_accounting_registration.py`:
  30 passed, 0 failures/errors/skips, 1.753s (Python 3.9.6).
- `/opt/homebrew/bin/python3 -m unittest discover -s tests -p unit_replay_accounting_registration.py`:
  30 passed, 0 failures/errors/skips, 1.535s (Python 3.14.3).
- `pvg verify` with the six changed Markdown paths: PASS, **0 files scanned**;
  this scanner result is not substantive Markdown validation.
- `git diff --check`: PASS. No implementation files changed. Full suites were not
  rerun for this docs-only correction; prior implementation proof remains 228/228
  on each required interpreter. Coverage not remeasured; prior measured line
  coverage and its limitations remain in [blob-guard.md](blob-guard.md).

LEARNINGS: mark pre-install evidence historical rather than rewriting its original
measurements; distinguish successful registration from still-denied recovery;
hash canonical baseline separately from the inspect output file; retain raw
protected evidence outside the repository and publish only aggregate proof.
