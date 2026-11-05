# Executable backend — source WIP, not delivery

Story: GRRR-k3j7. Base: `2b601462ba0ffb5aee6239aa22b06c26801dfaf9`.
This change does **not** complete the accepted backend, authorize execution, or
qualify any capstone journey. It is a tested-mechanics work-in-progress, not a
replacement report stage or a claim that the missing integration is optional.
All twelve acceptance criteria remain unchanged. Parent verification and
independent architecture/security/PM acceptance remain required.

## Normative inputs

The original bytes are archived in `docs/evidence/source-backend/`. Precedence:

1. `grrr-backend-jit-integration-corrections-20261104.md`
   `97c918328606cd69c62c6eaf52528ee4b024a76a8c5983a9e46f59c6a0bb7cee`
2. `grrr-backend-jit-plan-amendment-v3-20261104.md`
   `3ab960191613b2e10018f5c9444532080e9757693c49393f888c6beff0793e09`
3. `grrr-backend-jit-plan-amendment-20261104.md`
   `3f2c661bf93b8513440f3a31daed2f3d2f37cd312137c3181304195402ebb488`
4. `grrr-executable-backend-design-v2-20261104.md`
   `954a8578ca9354c0af2d1d19a25bff3dcd2f41b2ef98e62e5667254230239c56`

Accepted design input:
`grrr-backend-design-acceptance-20261104.md`,
`55155e52a5543325b1b071ca66b596e3795fa9456f04e6fda0efb9ce43e425d1`.
Independent design review:
`grrr-jit-integrated-review-20261104.md`,
`2e6d50ddd3e638365284f344cc5412975362cd6d7ee94dc87651e402b8b9d3d3`.
Design acceptance is not implementation acceptance.

## Implemented mechanics

### Locked-description launch handoff

`research/capstone_launch.py` opens a fresh read-only/no-follow description for
each gate contender. It validates regular single-link inode identity and never
issues `LOCK_UN`. The sender transfers exactly one description using SCM_RIGHTS
and closes its local copy on every outcome. Complete canonical tickets are
length-framed and request-half-closed; receiver authenticates before reading,
uses recvmsg throughout, rejects extra/truncated ancillary data and trailing
bytes, marks received descriptors non-inheritable, and closes all rejected FDs.

Broker preparation resolves a trusted compiled command callback, never argv in
the ticket. Each boot/operation has one launch identity; it is not reconstructed
from PIDs. Physical Popen creation uses close_fds and no new session. An owned
map retains the actual unreaped child. The gate remains held through the trusted
evaluator commit callback and exact COMMITTED identity/hash verification. Lost
COMMITTED marks the session unusable, closes the gate, then cancels/reaps outside
the gate. Signals and every poll/reap share the child lock; no process-name/PID
adoption is implemented. Pipe IO has bounded nonblocking waits.

The trusted callbacks are **not** the missing campaign/ledger implementation.
Source tests use real private SQLite commits and harmless owned children to
exercise the mechanics, not production-authority pass booleans. Installed
catalog closure, launchd death containment, existing-intent replay, complete
timing qualification and evaluator stop wiring remain missing.

### Independent durable review store and RPC

`research/capstone_review.py` stores original request/result objects before
hash-linked SQLite references, with file/directory fsync, FULL synchronous
transactions, immutable SQL guards, exact schema/index inventory, and full
event/row/object replay. Intent is irreversible. A crash/exception after intent
cannot remint a result; an exact repeat of a committed request returns its
original bytes, even if expired or failing. Retrieval cannot extend timestamps.

`research/capstone_review_service.py` separates reviewer and read-only context
handler capacity. Authentication precedes payload read. Context retains original
prospective Plan/receipt bytes and a live owner object only in memory. Trusted
current-state validation is called on registration and lookup; wrong bytes,
nonce, epoch or lost context refuses. The client retrieves from the peer-checked
durable reviewer endpoint, verifies exact result/request hashes and all expected
review bindings, and denies expiry/phase/verdict substitution before acceptance.

The complete deterministic approved-policy verifier is **not implemented**.
Verifier/current-state callbacks are trusted seams, not endpoint inputs. Source
fixtures use separate stores/processes but the actual unprivileged OS UID, not
UID322 separation or ACL proof. Low-level `open_existing` checks do not replace
InstallationV2 retained-inode/ACL/runtime-closure validation; complete installed
factories are missing. No deployment should wire these primitives yet.

### Composition test boundary

`unit_capstone_backend_composition.py` composes the unchanged real Journal with
two dynamically fresh Plans, independent reviewer processes/context RPC, two
one-use Journal permits, two FD handoffs and two real harmless children. It
asserts that the precomputed second Plan is stale after the first real ledger
transition, without changing its static Request/Grant. Selfhash and complete raw
bytes hash are kept distinct.

The composition fixture directly preinstalls public grants and fixture reservation
identities. Its root bytes and policy evidence are explicitly synthetic fixtures;
the broker intent is a source callback, not the full backend reducer. It therefore
does not prove campaign issuance, independent static approval, v5 allowance,
binding-only durability, campaign stop, a real baseline/candidate corpus result,
or a root Manifest. No fake public Operation/Manifest is emitted.

## Required source test entrypoint

```sh
/opt/homebrew/bin/python3 tests/unit_capstone_backend_suite.py
/Users/speed/miniconda3/bin/python3 tests/unit_capstone_backend_suite.py
/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/bin/python3.9 tests/unit_capstone_backend_suite.py
```

The suite includes all original protocol/journal/durable-evidence tests, the
parallel pure backend contract tests, and the new mechanics/composition tests.
Missing modules, zero tests, skipped required tests, errors and failures are
nonzero outcomes. Only short-lived owned harmless host children are launched;
no candidate Go/vlt, VM, paid network, production account or protected metadata
probe is part of the new tests. Existing historical test identity patches are
not production UID proof and are not used by the new positive fixture factories.

Raw worker outputs are retained under
`/tmp/grrr-k3j7-backend-evidence-20261104/`; measured commands/results and hashes,
not this document, are the test record. Parent runs/review are independent.

## Explicit remaining acceptance gaps

| AC | Remaining work (not waived) |
|---|---|
| 1 | Inputs archived exactly; integrated v3 reducer/provenance/reviewer semantics not complete. |
| 2 | InstallationV2 fixed topology, actual UID320/321/322, ACL/inventory/retained-inode and no-create factories. |
| 3 | Complete campaign event reducer and authority/control prefix joins remain missing. Eight-table SQL inventory and base issuance/index replay now exist; they do not complete campaign replay. Journal v1 source remains unchanged. |
| 4 | Authority registry/current capture and authoritative provenance validation. Reviewed finite data-only issuance intent/commit mechanics are not approval authority. |
| 5 | Campaign root-once live capability, bounded sequencer, binding-only persistence, no restart resume and authoritative JIT prebind/claim joins. |
| 6 | Complete independently approved deterministic verifier, installed reviewer inventory/ACL/custody, full policy/evidence joins and trusted review-cost metering. |
| 7 | Installed-equivalent backend handoff/control integration, all stop orderings, broker/evaluator death and partial-delivery matrix, durable intent recovery, measured deadlines. Mechanics tests are a subset. |
| 8 | Complete open-only StopCoordinator adapter, campaign stop/cessation outcomes and unclaimed-leaf fences. A reviewed subordinate SQL-only base hook exists, but has no positive campaign-start path or complete projection handling. |
| 9 | v4 read-only capture and operational v5 reserve/meter/settle/halt with complete current lineage/holds/caps and cross-DB conservative intents. No v5 activation is authorized. |
| 10 | Pre-reserved real replay/material extraction, full frozen corpus profile/spec mapping, all phase evidence and truthful immutable final projection/manifests. |
| 11 | Full implemented-backend regression matrix, source hashes and delivery shape after remaining implementation. Current suite covers WIP only. |
| 12 | Independent complete implementation architecture/security review and PM acceptance; no accepted merge or capstone-complete claim. |

Files still absent from this worker's implementation include
`capstone_installation.py`, `capstone_authority.py`,
`capstone_campaign.py`, `capstone_accounting.py`, `capstone_backend.py`,
`capstone_projection.py`, `replay_material.py`, `capstone_replay.py`, and
`capstone_corpus_profile.py`. Required integration changes to `control.py`,
`control_worker.py`, `trusted_transport.py`, `replay.py`, `corpus_execution.py`,
`capstone_client.py` and `capstone_service.py` are not represented as complete.

All eleven gate phases and all seven capstone journeys remain **not live
qualified**. Admission is blocked, promotion disabled, and production readiness
unclaimed. No protected installation, accounting reconciliation/reset/unstop,
live replay, q3hp driver, main mutation, commit/push or secret access is performed
by this worker.

## Reviewed source checkpoint — November 4, 2026

The combined explicit backend WIP suite now contains 143 tests, including the
29 index tests. Parent-guarded runs passed on installed Python3.14,3.12,3.9, plus
the direct required-suite entrypoint on3.14, with zero failures/errors/skips.
This remains public source-fixture evidence, not installed authority or capstone proof.

Four independently scoped reviews approve the implemented codec, launch rework,
base index mechanics, and review-store/RPC mechanics, including the Queue-test
repair. None accepts the entire story. Exact reports, source hashes, raw combined
test output and the original commands are retained in
`docs/evidence/source-backend/current-source-20261104/`.

The separate PAIVOT/Autoloop/selected-skills pilot is an optional development
verification lane outside this source checkout. It does not supply any missing
campaign, accounting, installation, evaluation, or promotion authority.
