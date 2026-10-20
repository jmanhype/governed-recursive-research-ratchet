# Standalone bounded runner, protocol v1

This implements the grammar approved in IMPLEMENTATION-APPROVAL-2026-10-20.md.
It is not a pvg extension. `bin/grrr --help` lists inspection and emergency stop.
No vlt behavior or defect is asserted by this synthetic walking skeleton.

```
bin/grrr start --policy DIGEST --challenge grrr-walk-001 --variant DIGEST
bin/grrr status RUN
bin/grrr review RUN
bin/grrr evidence RUN --level decision|technical|audit --format text|markdown|json
bin/grrr decide RUN --action approve-evidence|admit-contract|reject|needs-evidence|request-change --target DIGEST
bin/grrr stop RUN [--key ID] [--reason TEXT]
bin/grrr recover RUN [--plan ID] [--execute]
```

Exit 0 means the requested supported operation completed; it never implies
Verified defect, review, approval or admission. Exit 3 is a blocked/failed
operation, including a failed synthetic assertion. Parser errors exit 2.
`review`, all decisions and recovery explicitly return GateBlocked, not fake
downstream outcomes. Main merge, production mutation, patch generation, harness
adaptation and paid calls are denied at the evaluator boundary.

## Frozen synthetic scope

Parent-authorized on 2026-10-20 for GRRR-0g4n: exact UTF-8 `CLEAN\n` bytes and
exit zero are the evaluator expectation. Clean packet executes `printf 'CLEAN\n'`;
faulty packet executes `printf 'PASS\n'`. Packets are canonical JSON objects
with integer `version: 1` and `command`; SHA-256 covers their exact ASCII JSON
bytes, sorted keys, no spaces, no trailing newline. No input-supplied commands,
expectations, roles or bypass flags are accepted. Assertions stay on the host
under the evaluator UID; candidate packets execute exclusively in QEMU.

## Deployment and verification

Python standard library only; QEMU remains an external executable. Logical
`research/{policy,execution,ledger,runner,evaluator}` maps to same-name `.py`.
Control/budget are contained in evaluator.py for this small vertical slice.
Unix socket peer credentials authenticate local operator/evaluator UIDs using
macOS getpeereid. Separate directories owned by UID 320/321 enforce boundaries.
No environment-provided role or endpoint override is trusted.

The parent runs `scripts/identity-integration APPROVED_ASSET_DIRECTORY` as root
through an already-authorized mechanism. It does not prompt, install, access
credentials or alter accounts. Following the first Documents-path permission
failure, parent-authorized launchers create a fresh root-owned `/private/tmp/grrr-*`
runtime with mode 0711 and separate mode-0700 service directories. Only approved
code/assets are copied out; services never need broad access to Documents.
Evaluator and executor sockets still authenticate kernel peer UIDs in both
directions. The operator-owned mode-0600 `.runtime-endpoint.json` records the
current endpoint, not authority; clients reject unsafe bindings and wrong peers.
Every attempt retains its runtime and writes a distinct
`docs/evidence/bounded-challenge/attempt-TIMESTAMP-ID/` evidence directory.
The previous `.runtime` and failed logs remain untouched. Historical failure
hashes are rechecked and never counted as success. TCC is a suspected cause of
the original EACCES, not a confirmed diagnosis.
Restarting evaluator state remains RecoveryRequired. This test launcher is not
a persistent service deployment.

The launcher verifies runner denied reads/writes and impersonation, then runs
`./scripts/test-story bounded-challenge` synchronously. The suite first verifies
direct stop against a real booted VM before either synthetic variant is run.
The same command is the mandatory CI entrypoint; absent services are an error,
never skip/success. Supplementary pure tests: `python3 tests/unit_contracts.py`.

Raw snapshots/anchors and Markdown are preserved under
each `docs/evidence/bounded-challenge/attempt-*` directory; protected
journal/objects remain in the recorded `/private/tmp/grrr-*/evaluator/`, outside
disposable guests. Independent verification uses
`ledger.verifySnapshot(snapshot, separately_retained_anchor)` and checks event
sequence/prior links, object hashes and snapshot identity. Hashes are not human
approval and do not protect against a privileged host attacker.

Reservations retain the full 300-second maximum conservatively; actual duration
is recorded separately. Local incremental API spend is zero; paid dispatch is
impossible. Review time is unknown/not-run, not falsely zero. No recovery,
independent replay, comparative score, contract admission or production ability
is implemented. The full gate registry remains visible with not-run states.
