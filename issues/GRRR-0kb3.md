---
id: GRRR-0kb3
title: "E2e: Operator completes one governed vlt ratchet journey"
status: open
priority: 0
type: task
parent: GRRR-2t3h
created_at: 2026-11-11T21:17:50Z
created_by: speed
updated_at: 2026-11-11T21:17:51Z
content_hash: "sha256:d84bca7c1f5ccc57c9221bf9fd2c18adc62d6364e84081f7b4047d35fa192ec2"
labels: [milestone-1, capstone, integration, security, e2e]
blocked_by: [GRRR-43i8, GRRR-d8ji, GRRR-ev2w, GRRR-k3j7, GRRR-n49g, GRRR-q3hp, GRRR-w1lt, GRRR-wcwy, GRRR-yt6a, GRRR-0g4n, GRRR-34ve, GRRR-888u, GRRR-90te, GRRR-bnkf]
---

## Description
## Context (Embedded)

This successor capstone exists because `GRRR-6sso` reached the three-rejection
escalation limit. It must not be reopened, reset, weakened, or used as a
dependency. This new story is the bounded final gate for the current integrated
core; it neither retries the old package nor treats historical component
evidence as a fresh end-to-end run.

The integrated source base after the operator-authorized merges is local epic
commit `ad4f9edc3e612866aefcac368ebee17137861c33`:

- accepted `GRRR-n49g` tip `632912391db2bfdf59c339d4627d965fffc7bb08`;
- accepted `GRRR-734u` tip `bdbc4ec1e34845836473d73ea4a681dbb4b46ff8`;
- integrated suite measured 363/363 on Python 3.14.3, 3.12.9, and 3.9.6 with
  zero failures/errors/skips;
- `pvg verify` over the newly integrated report/status/replay modules passed
  with zero issues.

Frozen inputs:

- corpus version: `validated-corpus-v2.2-isolated`;
- corpus freeze digest: `dfa75ef2bf3d43fd4f750094fe643afe4f204812c0ae2426276bedb471fa8529`;
- corpus manifest SHA-256: `32fb59c74ea96653c50e3deea0d66474bafdd78caf56c3e9c4c589aba703e354`;
- protected truth SHA-256: `7cf9f99f5836c4e3e147df2866d54480a706f2665a732fbf61bd1a0d0b4c52ea`;
- public projection SHA-256: `c6aa57a2eb595fd2fe35ae817295df2220738b8538755826c5af11af648fd361`;
- corpus composition: 32 total, 24 defects, 8 clean controls, 17 critical
  defects, 7 noncritical defects;
- vlt source commit: `129e0b3f15a3bd6af949ee47d76f6855c582ab73`;
- vlt source archive SHA-256: `e644b9848b306f158a2367293dd96c66dac2bed97c0dd42891db007667c0ae7e`.

Binding historical results, which may be mapped but not reinterpreted as fresh
runtime evidence:

- admitted D011 contract digest: `ab4339807b8fae5b96713131ef524a409b475bb7c158a4318fce5de80b668aa4`;
- accepted three-arm report SHA-256: `b7bb2ec8717e8921e16f9a3e312f6ad46839a125634dc6e3d144499cc841fefb`;
- measured selector means: deterministic 0.0, random 6.0, Jev 5.0;
- permitted selector conclusion: `inconclusive-jev-did-not-win`, no runtime selector promotion;
- adaptation cycle report SHA-256: `550944a2b81b1e52cf4c9aaf410b5e43bcb5758aa0eb1bfa9ba4a63094d352ba`;
- adaptation outcome: no composed strategy change;
- Sean Chatman Anti-Cheat Scorecard: advisory only, never a mandatory gate;
- accounting v4 recovery receipt: `8b7958e5be76f6b35c4bfafc1f17a2926badfdd813addbefd5d683e379e8eeeb`.

Mandatory live gate inventory, each with an individual pass/fail/error/not-run
record and immutable evidence:

1. `source_environment_identity`
2. `isolation`
3. `protected_asset_integrity`
4. `baseline_correctness`
5. `trusted_observation`
6. `independent_replay`
7. `specification_traceability`
8. `evidence_integrity_currency`
9. `budget_state`
10. `reviewer_outcome`
11. `action_specific_human_approval`

No aggregate exit code, all-empty check, subset count, missing file, skipped
test, timeout, or stale receipt may manufacture a pass.

## USER INTENT

I can inspect and safely control one fresh, complete, evidence-backed governed
vlt research journey from the integrated GRRR core, and understand exactly what
is verified, uncertain, authorized, blocked, and reversible without reading
source code.

## OUT OF SCOPE

- No new Jev/model/provider/network call and no new selector-superiority claim;
  the accepted three-arm result remains historical selector evidence.
- No autonomous implementation-patch generation, promotion, production mutation,
  deployment, or automatic merge to `main`.
- No new permanent contract admission in this story; validate the existing D011
  contract and recurrence rejection rather than minting another authority.
- No Karpathy-style ongoing autoresearch loop and no additional Harness² cycle;
  their accepted foundations and honest non-improvement result are final-packet
  context only.
- No GraphLaw, ggen, wasm4pm, dteam, Bend 2, dashboard, or Anti-Cheat gate
  integration.
- No reset of a consumed replay sequence, accounting stop, hold, unknown, ledger,
  authorization, or rejection history.
- No weakening of any old or new acceptance criterion; infrastructure absence or
  a failed gate blocks the capstone.

## DIFF BUDGET

Approximately 7 repository files and under 1,200 changed lines, expected to be
mostly request/evidence/report records plus at most one thin operator CLI
wrapper. Gross overrun requires PM investigation, not automatic rejection.

## Boundary Map

### PRODUCES

- `docs/evidence/final-capstone-v2/REQUEST.json` -> schema:
  exact integrated/source/corpus/runtime/accounting/contract hashes, 32 ordered
  challenge IDs, four fixed batches of eight, output namespace, gates, budgets,
  stop conditions, denied actions, and all authorization flags initially false.
- `docs/evidence/final-capstone-v2/PREFLIGHT.json` -> schema:
  namespace non-reuse, accounting preservation, identity/permission/isolation,
  capacity, runtime, corpus integrity, accessibility plan, and per-gate state.
- `scripts/grrr-final-capstone` -> `main(argv: Optional[Sequence[str]]) -> int`
  as a thin read-only/operator journey coordinator over existing modules; it
  must not implement evaluator truth or bypass a gate.
- `docs/evidence/final-capstone-v2/RESULT.md` -> operator decision summary,
  complete per-gate map, costs, journeys, negative controls, recovery state,
  and explicit unresolved limits.
- `docs/evidence/final-capstone-v2/FINAL-PACKET.md` -> architecture/business/
  design outcome map to exact immutable receipts and honest optional-lane status.

### CONSUMES

- `GRRR-n49g`: `research/status_view.py` ->
  `project_status(data: Dict[str, Any]) -> Dict[str, Any]`
  Usage: project each archived replay/evidence object before text/Markdown/JSON
  rendering; unknown cost/states remain unknown and all action authority stays
  false unless independently established elsewhere.
- `GRRR-n49g`: `scripts/grrr-review` ->
  `--view review|status --format text|markdown|json`
  Usage: render the same historical projection; never use it as live freshness
  or approval authority.
- `GRRR-734u`: `research/fresh_replay_runtime.py` ->
  `prepare(request: dict, expected_request_hash: str) -> Proposal` and
  `validate_proposal(proposal: Proposal, request: dict,
  expected_request_hash: str) -> None`
  Usage: produce/validate only a `prepared_not_issued` distinct namespace;
  protected installation requires separate review and authorization.
- `GRRR-bnkf`: `corpus/manifest.json` ->
  schema fields `version`, `freeze_digest`, `challenge_ids`, `counts`, `source`
  Usage: bind exact corpus version/freeze/source and the ordered 32 IDs; do not
  expose protected truth or holdout membership to the candidate.
- `GRRR-hbc6`: protected accounting v4 evidence ->
  recovery receipt `8b7958e5be76f6b35c4bfafc1f17a2926badfdd813addbefd5d683e379e8eeeb`
  Usage: preserve unknowns/holds and cumulative identity; no spendability or new
  allowance is inferred.
- `GRRR-c875`: `research/control.py` ->
  `StopCoordinator.stop(principal: int, run: str, key: str,
  reason: Optional[str]=None) -> dict` and
  `StopCoordinator.stop_status(principal: int, operation: str) -> dict`
  Usage: perform and inspect one real safe-stop journey; acknowledgement never
  means cessation until stop status and baseline checks verify it.
- `GRRR-34ve`: `research/admission.py` ->
  `recurrence_rejected(admission, replay_receipt)` evaluates the already
  admitted D011 contract without minting a new authorization.
- `GRRR-dbbi`: `docs/evidence/jev-selector-measurement/three-arm-result-20261103T214701Z/report.json`
  -> schema version 1 selector-quality report
  Usage: map the accepted historical random-led result; do not rerun Jev or
  claim superiority.

## Story Acceptance Criteria

1. **Exact successor request.** Build `REQUEST.json` against the integrated
   commit and all frozen hashes above. It selects exactly the manifest's 32 IDs
   in fixed order, partitions them into four immutable batches of eight, permits
   one attempt per scenario and zero retries/extra scenarios, and explicitly
   forbids external model/provider calls. It records all eleven gates as
   `not-run`, all protected/runtime authorities as false, and exact output
   namespace/stop/denial semantics. Self-consistent hashes alone are not origin
   or authority.
2. **Independent request review.** At least three differently scoped independent
   read-only reviews approve the exact request bytes: (a) source/runtime binding,
   (b) namespace/accounting/isolation/security, and (c) operator journey,
   budget, accessibility, and denial semantics. Reviewers must not mutate code,
   tracker, protected state, or evidence.
3. **Fresh namespace and protected preflight.** After separate exact operator
   authorization, use `GRRR-734u` to prepare a distinct non-reused namespace and
   independently review/install/verify only that namespace. Prove predecessor
   preservation, accounting v4 receipt binding, protected-asset integrity,
   evaluator/runner identity separation, offline isolation, capacity, corpus
   digest equality, and stopped/unstopped disposition without zeroing unknowns,
   releasing holds, creating spendability, or resetting consumed state. A failed
   preflight halts before guest launch.
4. **One bounded live verification journey.** After another exact human
   authorization, execute all 32 frozen scenarios once across four batches,
   archiving immutable evidence between batches. The full mandatory system must
   detect and independently replay 17/17 critical defects and at least 7/7
   noncritical defects, reject all 8 clean controls as non-defects, produce zero
  verified false positives, and prove the existing D011 contract rejects
   recurrence. Exactly one failed/inconclusive observation stops the campaign;
   no automatic rerun or threshold change is allowed.
5. **Operator control journeys.** In one unedited session, the operator must
   start, monitor, inspect Level 1/2/3 evidence, request more evidence for an
   incomplete case, invoke a real hung-run safe stop, inspect idempotent stop
   status, and distinguish stopped safely from recovery required. Repeated same
   stop key returns the original receipt; a changed/duplicate authorization does
   not create effects. Cessation, baseline integrity, and preserved evidence are
   verified before any safe outcome is claimed.
6. **Adversarial fail-closed matrix.** Real negative controls must refuse stale
   or reused authorization, missing/extra/malformed gate records, unknown or
   exhausted budget, protected-path writes, candidate-supplied expected truth,
   tampered/truncated/missing ledger exports, ambiguous specification, and
   promotion/admission attempts. Every refusal must provide the same facts and
   next safe action in plain text, Markdown, and JSON through the shared
   `project_status` projection.
7. **Cost, report parity, and accessibility.** Record wall/runtime/review times,
  exact compute provenance, and explicit `$0` external incremental spend only
   because no external/provider call occurs. The operator completes an informed
   keyboard-only/plain-text walkthrough in at most 30 minutes, showing separated
   proposed/observed/verified/approved/deployed states, emergency stop, recovery,
  and unknown cost. Text/Markdown/JSON must agree on snapshot identity and all
   state dimensions; no raw JSON is required for an ordinary decision.
8. **Final packet and independent acceptance.** Produce a final packet mapping
   architecture requirements 1–12 and business/design outcomes to immutable
   receipts, exact revisions, counts, costs, negative controls, stop/recovery,
   accessibility, warnings, unresolved risks, and rollback evidence. State that
   random led the selector comparison, Harness² made no strategy change, Sean’s
   scorecard is advisory-only, and optional lanes remain non-runtime. The story
   is deliverable only with all eight ACs supported by real evidence and then
   requires independent PM acceptance; no self-acceptance, merge, push,
   promotion, admission, production mutation, or deployment is permitted without
   separate authorization.

## Testing Requirements

- E2E/real-system evidence ONLY for this story: no mocks, fake protected state,
  mocked-success I/O, skipped mandatory gates, or unit-test substitution.
- Required source preflight before any protected action:
  `PYTHONPATH=research:tests python3 -B tests/unit_capstone_backend_suite.py`
  on installed Python 3.14, 3.12, and 3.9 under `/Library/GRRR` read/write
  denial; expected current count is 363 with zero failures/errors/skips.
- Required static checks: `pvg verify` over changed executable/source files,
  `git diff --check`, exact SHA256 manifests, and `pvg story verify-delivery`.
- Live evidence must retain unedited commands, stdout/stderr, exit codes,
  timestamps, interpreter/runtime identities, process identities, snapshots,
  object hashes, ledger export receipts, stop/recovery outcomes, review timing,
  and accessibility transcript.
- Any protected read, VM/QEMU action, namespace installation, accounting access,
  replay, stop/recovery effect, external credential use, production mutation,
  merge, or push requires its own exact operator authorization after the request
  review; absence blocks execution rather than weakening a gate.

## MANDATORY SKILLS

- `pvg` and `nd`: canonical live tracker/state transitions only.
- `developer`: one bounded story, no recursive delegation, deliver but never
  self-accept.
- `pm_acceptor`: independent evidence-based acceptance after delivery.
- `anchor`: adversarial final-milestone review if requested by the dispatcher.
- No vlt CLI operation is authorized unless separately needed and explicitly
  authorized; do not modify pvg/nd/vlt core.

## Delivery Requirements

- Append an AC-by-AC proof block with exact commands, output counts, commit and
  artifact hashes, and immutable evidence references.
- Keep execution and authorization state separate. `prepared_not_issued`,
  `issued`, `installed`, `executed`, `verified`, `reviewed`, `approved`,
  `accepted`, and `deployed` must never collapse.
- Preserve all old GRRR-6sso rejection evidence; do not reset its labels or
  dependency state.
- Work only in the assigned story worktree/current integrated epic source;
  preserve concurrent edits.

## nd_contract
status: new

### evidence

- Created 2026-11-11 as a bounded successor to deferred/rejected-x3
  GRRR-6sso; no implementation, protected access, replay, authorization,
  admission, promotion, production mutation, merge, or push claimed.
- Source base `ad4f9edc3e612866aefcac368ebee17137861c33`; integrated source
  suite 363/363 on Python 3.14.3/3.12.9/3.9.6.

### proof

- [ ] AC #1: exact successor request and frozen identities.
- [ ] AC #2: three independent exact-byte request reviews.
- [ ] AC #3: fresh namespace preflight/install/verify with preservation.
- [ ] AC #4: one 32-scenario live verification journey and recurrence rejection.
- [ ] AC #5: real operator monitoring/evidence/safe-stop/recovery journey.
- [ ] AC #6: adversarial fail-closed and evidence-integrity matrix.
- [ ] AC #7: cost/report-parity/accessibility proof.
- [ ] AC #8: final packet, independent PM acceptance, and honest limits.

## Acceptance Criteria


## Design


## Notes


## History
- 2026-11-11T21:17:51Z dep_added: blocked_by GRRR-43i8
- 2026-11-11T21:17:52Z dep_added: blocked_by GRRR-d8ji
- 2026-11-11T21:17:52Z dep_added: blocked_by GRRR-ev2w
- 2026-11-11T21:17:53Z dep_added: blocked_by GRRR-k3j7
- 2026-11-11T21:17:53Z dep_added: blocked_by GRRR-n49g
- 2026-11-11T21:17:53Z dep_added: blocked_by GRRR-q3hp
- 2026-11-11T21:17:54Z dep_added: blocked_by GRRR-w1lt
- 2026-11-11T21:17:54Z dep_added: blocked_by GRRR-wcwy
- 2026-11-11T21:17:54Z dep_added: blocked_by GRRR-yt6a
- 2026-11-11T21:17:54Z dep_added: blocked_by GRRR-0g4n
- 2026-11-11T21:17:55Z dep_added: blocked_by GRRR-34ve
- 2026-11-11T21:17:55Z dep_added: blocked_by GRRR-888u
- 2026-11-11T21:17:55Z dep_added: blocked_by GRRR-90te
- 2026-11-11T21:17:55Z dep_added: blocked_by GRRR-bnkf

## Links
- Parent: [[GRRR-2t3h]]
- Blocked by: [[GRRR-43i8]], [[GRRR-d8ji]], [[GRRR-ev2w]], [[GRRR-k3j7]], [[GRRR-n49g]], [[GRRR-q3hp]], [[GRRR-w1lt]], [[GRRR-wcwy]], [[GRRR-yt6a]], [[GRRR-0g4n]], [[GRRR-34ve]], [[GRRR-888u]], [[GRRR-90te]], [[GRRR-bnkf]]

## Comments
