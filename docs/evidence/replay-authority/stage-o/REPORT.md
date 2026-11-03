# Stage O v4 runtime adapter — design-only, blocked

## Scope

Stage O implements a pure repository-retained runtime adapter for the approved
Stage N candidate v4 replay-successor contract. It performs no filesystem,
SQLite, process, VM, credential, network, or protected-path access. It does not
install a store, amend a budget, authenticate an operator, reconcile
spendability, execute replay, promote or admit anything, merge, or push.

## Adapter behavior

The adapter accepts exactly one runtime observation:

- repository-hypothetical;
- predecessor active binding version 3;
- not installed;
- no installer/review/authorization hashes;
- no store device/inode;
- no budget-amendment or per-run approval receipt;
- no execution request.

Any attempt to claim installation, identities, approvals, or execution is
rejected before an adapter status is produced.

The generated status binds the exact Stage N receipt and binding and reports:

- Stage N candidate contract: pass;
- predecessor history and three holds preserved: pass;
- independent runtime review: not-run;
- operator budget amendment: not-run;
- protected v4 installation: not-run;
- installed store identity: not-run;
- fresh per-run operator approval: not-run;
- mandatory live replay: not-run;
- replay execution: blocked.

The outcome always retains:

- `adapter_valid=true` only for this design state;
- `design_only=true`;
- `replay_possible=false`;
- `execution_authorized=false`;
- `allowed_mutations=[]`;
- `spendable=null`;
- `failure_mode=refuse-before-effects`;
- every authority flag false.

## Future request contract

The adapter also defines the shape of a future request. A structurally valid
request must bind:

- the exact Stage N receipt and binding hashes;
- `independent-replay` at POC stage;
- one registered mode and its exact session index;
- 480,000,000 execution microseconds;
- the mode’s exact guest-launch count;
- five distinct installer/review/authorization/amendment/per-run receipts.

Even that valid shape returns `execution_authorized=false`. It only says that
protected installation and live per-run verification remain required; it never
authenticates those receipts.

## Verification

- Focused Stage O tests:
  - Homebrew Python 3.14.3: 22/22 passed.
  - Miniconda Python 3.12.7: 22/22 passed.
- Full no-guest unit suites:
  - Homebrew Python 3.14.3: 534/534 passed.
  - Miniconda Python 3.12.7: 534/534 passed.
- Deterministic adapter emission: byte-identical.
- No warnings or failures appear in the retained Stage O logs.
- `pvg verify`: PASS.
- `git diff --check`: PASS.

## Remaining gates

Independent review returned:

```text
STAGE_O_RUNTIME_ADAPTER_REVIEW: APPROVED
```

Approval covers only the design-only adapter. Exact installer bytes, operator
budget amendment, protected v4 installation, actual store identity, dedicated
identities, per-run approvals, real four-mode replay, PM acceptance, merge, and
push remain separate gates.
