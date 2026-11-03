---
id: GRRR-gge0
title: "Run one governed adaptation cycle"
status: open
priority: 1
type: task
labels: [milestone-2, integration, adaptation]
parent: GRRR-2t3h
created_at: 2026-11-03T22:07:39Z
created_by: speed
updated_at: 2026-11-03T22:07:39Z
content_hash: "sha256:b65bf18929336e85c4d4841842735e5c16ae081930ddefbd06be03a6e3c3aba2"
---

## Description
## Description
## Context (Embedded)

The operator has authorized the first post-foundational adaptation cycle now that the approved three-arm selector evaluation is complete. This story runs exactly one bounded, repository-only Propose–Probe–Compose cycle informed by Karpathy-style iteration and the Harness² safety pattern. It must not become unrestricted self-modification.

Measured foundation at source commit `5b50e29272819da205fc09e051f82c2639a7a197`:

- Frozen corpus: `GRRR-validated-corpus-v2.2-isolated`
- Corpus freeze digest: `dfa75ef2bf3d43fd4f750094fe643afe4f204812c0ae2426276bedb471fa8529`
- Protected truth SHA-256: `7cf9f99f5836c4e3e147df2866d54480a706f2665a732fbf61bd1a0d0b4c52ea`
- Approved evaluation plan SHA-256: `97ec4b8ccc34b3fc4da4fcfbef33b49bbb3f4f1c445cfecdb752715ddf034be1`
- Completed result report: `docs/evidence/jev-selector-measurement/three-arm-result-20261103T214701Z/report.json`
- Completed result SHA-256: `b7bb2ec8717e8921e16f9a3e312f6ad46839a125634dc6e3d144499cc841fefb`
- Deterministic lexical primary mean: `0.0`
- Random primary mean: `6.0`
- Jev primary mean: `5.0`
- Pre-registered outcome: `inconclusive-jev-did-not-win`
- Pre-registered default: `retain-deterministic-lexical-baseline`

The two fixed proposals for this first cycle are:

1. **Reverse-lexical probe:** because lexical ordering selected clean controls and scored 0/8, invert local ID ordering. This is expected to expose a governance failure: local `D/C` IDs encode defect/clean semantics, so any improvement derived from that prefix is leakage and must be rejected even if it scores 8/8.
2. **Next random block probe:** continue the already approved random-family design to the next non-cherry-picked seed block 45, 46, and 47. Evaluate all three repetitions; do not search seeds or retain the best subset.

The expected honest result may be **no composed change**. A no-change outcome is valid and must not be treated as failure.

## USER INTENT

I want the now-proven evaluation foundation to begin improving its own research strategy, but only through bounded, reviewable proposals that cannot cheat, spend unapproved resources, or promote themselves.

## OUT OF SCOPE

- Sean Chatman Anti-Cheat Scorecard integration: separate evaluation story; this story uses only a deterministic local leakage gate.
- External Jev/model calls or secret access: the three-arm measurement is complete; this cycle is offline.
- Runtime selector promotion or default-policy mutation: measured evidence may inform a later operator decision, but cannot promote itself.
- VM execution, independent replay, contract admission, source patch generation, production mutation, merge, or push: protected gates remain separate.
- Seed search or selecting the best post hoc random block: only fixed seeds 45, 46, and 47 are allowed.

## DIFF BUDGET

Approximately 4 files and under 500 changed LOC. Gross overrun triggers PM investigation rather than automatic rejection.

## Boundary Map

PRODUCES:
- research/harness_adaptation.py -> `run_adaptation_cycle(plan_path: Path, result_path: Path, corpus_root: Path) -> Dict`
- scripts/run-harness-adaptation-cycle -> deterministic offline CLI requiring an exclusive output path
- reports/adaptation-cycle-1.json -> schema version, immutable input hashes, two proposals, probe results, leakage verdicts, compose decision, and false authority flags
- tests/unit_harness_adaptation.py -> real-input offline tests and fail-closed tamper cases

CONSUMES:
- GRRR-6sso: corpus/evaluation-plan-v2-proposed.json -> `evaluation_plan_v2.load_plan(path: Path) -> Tuple[Dict, bytes]`; exact byte hash must remain `97ec4b8ccc34b3fc4da4fcfbef33b49bbb3f4f1c445cfecdb752715ddf034be1`
- GRRR-6sso: docs/evidence/jev-selector-measurement/three-arm-result-20261103T214701Z/report.json -> completed three-arm result object; exact byte hash must remain `b7bb2ec8717e8921e16f9a3e312f6ad46839a125634dc6e3d144499cc841fefb`
- GRRR-6sso: corpus/protected/truth.json -> local trusted evaluator mapping `challenge` to `{truth, critical}`; exact byte hash must remain `7cf9f99f5836c4e3e147df2866d54480a706f2665a732fbf61bd1a0d0b4c52ea`
- existing: research/selector_comparison.py -> `load_catalog(corpus_path: Path) -> List[str]`, `deterministic_select(catalog, budget, seed=0) -> Dict`, and `random_select(catalog, budget, seed) -> Dict`

## Story Acceptance Criteria

1. Bind the cycle to the exact approved plan, completed result, frozen corpus, and protected truth bytes by SHA-256; any hash or schema drift fails closed before proposing.
2. Propose exactly the two fixed, deterministic candidates described above. Candidate generation must not search seeds, inspect holdout membership, read protected expected behavior text, call a model, or access credentials.
3. Probe reverse lexical against frozen protected truth. It will select eight `D...` IDs and score 8/8, but the deterministic anti-leakage gate must reject it because the `D/C` local-ID prefix encodes defect/clean status. Record both the measured 8/8 and the cheating rejection; never let the score override the leakage verdict.
4. Probe random seeds 45, 46, and 47 as one fixed block. Compute selected IDs, per-repetition true-defect counts, mean, critical mean, clean mean, and unique-defect count. Compare against the measured random benchmark mean 6.0 without relabeling the benchmark or cherry-picking repetitions.
5. Apply the pre-registered compose rule: compose no strategy change unless a non-leaking candidate exceeds the random benchmark mean 6.0 and passes every leakage/integrity gate. Reverse lexical is ineligible; the fixed next random block must be evaluated honestly. Keep the approved `retain-deterministic-lexical-baseline` default and all promotion/admission/execution authority flags false.
6. Emit an exclusive, deterministic JSON report and readable Markdown summary. The report must identify proposals, selected IDs, metrics, leakage reasons, benchmark, decision, input hashes, and `no automatic rerun`. It must not expose credentials, protected expected behavior, raw provider responses, or `/Library/GRRR` paths.
7. Prove fail-closed behavior with real temporary copies or exact-file tampering for plan drift, result drift, truth drift, malformed selection, candidate leakage, unsafe output path, and duplicate output. No test may skip, mock the trusted evaluator, or turn missing evidence into success.

## Testing Requirements

- Unit tests: exact input binding, fixed proposal generation, deterministic reverse-lexical score and leakage rejection, next-block metrics, no-compose decision, authority flags, and sanitized output.
- Integration tests: MANDATORY, real repository inputs, no mocks. Run the actual CLI to generate a fresh report and Markdown summary, then verify hashes, report contents, and exclusive-output refusal.
- Focused commands must pass under both `/usr/bin/python3` and `/opt/homebrew/bin/python3`.
- Run `pvg verify`, `pvg gates`, and `git diff --check`.
- No network, secret read, Jev call, VM, replay, admission, promotion, production mutation, merge, or push.

## Skills To Use

- `developer`: implement exactly this story.
- `pvg` and `nd`: story workflow and evidence updates.
- `codebase-memory`: discover existing selector/evaluation APIs before wiring.
- `pm_acceptor`: independent acceptance after delivery.

## Delivery Requirements

- Append exact implementation/test evidence, hashes, command results, and AC verification using `pvg nd update`.
- Run `pvg story verify-delivery` and `pvg story deliver`.
- Do not close the story; PM-Acceptor reviews independently.
- Preserve the existing GRRR-6sso work and do not revert concurrent edits.

## nd_contract
status: new

### evidence
- Created from the operator's post-foundational adaptation authorization on 2026-11-03.

### proof
- [ ] Pending one bounded offline Propose–Probe–Compose cycle.

## Acceptance Criteria


## Design


## Notes


## History


## Links
- Parent: [[GRRR-2t3h]]

## Comments
