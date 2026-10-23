# GRRR-w1lt live prerequisite proof

Executed implementation: **e0dfaf33d3b2725a2fad63401d2b717a8365e0a6**.
Scope: **C001-runtime-lifecycle-only**, not independent replay, defect verification,
ReplayReceipt, contract admission or promotion. This report supports developer
delivery of the five prerequisite ACs; independent PM acceptance remains required.

## Provenance and verification

The parent performed approved privileged installation, recovery, smoke and access
probes, then copied the selected immutable artifacts in this directory. The
worker verified these copies, not the protected originals. Original ownership,
access-probe outcomes, installation/preflight transcript and repeat refusal below
are explicitly parent-reported; copied files are not proof of their original UID.
No worker root/QEMU/VM execution, protected mutation or push occurred.

`verify-copies.py` passed under `/usr/bin/python3 -B` and
`/opt/homebrew/bin/python3 -B`: both SQLite databases opened with
`mode=ro&immutable=1`, integrity_check=ok, hashes unchanged after read. Checks
cover reservation/metering settlement, ledger hash chain, object/raw hashes,
guest credentials/repetitions and lifecycle/run/recovery binding. Output is in
the two copy-check logs. SHA256SUMS binds every selected copy and report/check
artifact (excluding itself). Previous implementation tests remain 32 focused /
198 full passing on each required Python in `../runtime-smoke-r3/`.

## Observed result

- Sanitized runtime audit exit0; parent confirms installed code/launcher/review
  exactly e0dfaf3. Copied runner approval authorization_reference:
  `58ac658e57f3ec31e969f1b6674e1b0cd8b45266c54db1626956f96338f35837`.
- Root lifecycle completed in **24.019100959s**, children_ceased=true,
  evaluator_succeeded=true, exit_codes=[-15,0], below inclusive480s. Run:
  `9e4b2c6cedae4df1a7d931add73a29b4`. Independent replay/admission both false.
- Actual offline C001 transport exit0, forced=false, error=null,
  transport_complete=true, ceased=true; 27,673 raw bytes, SHA256
  `adf82b14c9ac434e3883751e2648690b88e0324d1b55459631a4fe3fb4725bbd`.
  Supervisor unchanged; guest real/effective/saved UID/GID1000, no supplementary
  groups/capabilities, NoNewPrivs=1. Three repetitions exit0 with identical output
  hashes. These are lifecycle observations, not allegation verdicts.
- Budget halted=0; one reservation settled for **0 USD / 22,823,014us**.
  Ledger sequence reserved → transport → settled; verified object SHA256
  `444262c5a0457cd27c6b6ef29be3c474426707d62e2eeda458c74376c9e07a16`.
- Failed d89cec7 namespace retained by reviewed atomic rename; copied recovery
  record confirms unchanged inventory and verified base inventory. Its prior
  failed lifecycle remains separate, not relabeled as a success.

## Parent-reported protected probes

Evaluator read own policy successfully with approved hash; runner could not read
evaluator/private; evaluator could not read private; operator501 could not read
evaluator. Runner could use its scratch; evaluator could not list runner scratch.
UID320/321 plan truncation attempts were denied and its hash unchanged. No UID320,
UID321 or QEMU processes remained. Repeating --runtime-smoke refused the existing
namespace, preserving one-shot semantics. No worker retry was attempted.

Parent confirmed unchanged protected corpus input (6c3cb…), profile (b3b92…),
preparation (755af…), policy (355e…), source (e644…), QEMU (352108…), launcher
(aa48…) and replay_smoke (2b388…). Abbreviations are parent report identifiers,
not substitute full checksum claims. Full installed code/policy pins are in
`docs/REPLAY-RUNTIME-SMOKE.md`, the source closure, and copied runner approval.

## AC-by-AC PROOF

| AC | Proof | Developer result |
|---|---|---|
| 1 | Operator-approved canonical policy binds corpus/freeze/source, exactly two consecutive independent failures, numeric limits and denials; policy hash355e… preserved | Met |
| 2 | Previously proven base UID-separated preparation plus reviewed live fresh smoke; root-owned assets/code, UID320 policy/expectations/accounting/ledger, UID321 executor; parent access probes above | Met |
| 3 | Parent successful sanitized protected preflight before dispatch; exact installed/protected identities, disk/process/lock/isolation checks; original fail-closed tests retained | Met |
| 4 | Actual parent-mediated offline C001 VM/service lifecycle, credential/isolation observations, private failure/recovery preservation, settled budget/hash-linked evidence, ceased children | Met |
| 5 | Live tracker GRRR-z3w9 BlockedBy=[GRRR-w1lt]; no dependency removed; all smoke records deny independent replay/admission and no fixture ledger relabeling | Met |

## LEARNINGS and downstream not-run gates

macOS identity vectors must match actual reviewed account membership; private
record modes must match their creator; uncertain process observation must still
force KILL; asynchronous stop intent must not interrupt spawn registration.
Failures remain evidence, not erased retries. No DISCOVERED_BUG remains deferred.

**Not-run:** GRRR-z3w9 independent allegation replay/verdict/ReplayReceipt,
independent two-consecutive-failure sequence, contract admission, promotion and
production mutation. PM acceptance of GRRR-w1lt is not performed by this worker;
GRRR-z3w9 stays blocked until acceptance. Live forced-timeout/KILL fault injection
was not claimed: harmless real process regressions cover those cleanup branches,
while this live run proves the normal offline runtime lifecycle. Fresh subsequent
runtime authorization/recovery is required; this used namespace is not reusable.
