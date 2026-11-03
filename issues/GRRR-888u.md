---
id: GRRR-888u
title: "Evaluate Sean Chatman Anti-Cheat Scorecard"
status: open
priority: 1
type: task
labels: [milestone-2, research, external-tooling, security-review]
parent: GRRR-2t3h
created_at: 2026-11-03T23:26:01Z
created_by: speed
updated_at: 2026-11-03T23:26:01Z
content_hash: "sha256:2772ef223e5f53e929e5d8e406b55cb69915506f5d4fd8e9c6e0b302818de611"
---

## Description
## Description
## Context (Embedded)

Operator authorized evaluating Sean Chatman's Anti-Cheat Scorecard after the first governed adaptation cycle. The canonical repository is `https://github.com/seanchatmangpt/anti-cheat-scorecard`. Latest stable release at evaluation time is `v26.8.29`, commit `5271351d079f79634de2f8b91970b80daf9bcb86`, released 2026-08-29. License is Apache-2.0. The tool is a fork of OpenSSF Scorecard adding an `Anti-Cheat` check with 52 registered detector packages.

The evaluator target is accepted adaptation commit `cf3eb55422ba18898541318c138cd82543419d12` on `story/GRRR-gge0`. That cycle produced a no-change result: reverse lexical scored 8/8 but was rejected for D/C ID leakage; random seeds 45/46/47 scored [4,6,4], mean 14/3, below benchmark 6.0.

This is an evaluation story, not an integration story. The scorecard may recommend; it must never replace GRRR's trusted evaluator, independent replay, human approval, accounting, or promotion authority.

## USER INTENT

I need to know whether Sean Chatman's Anti-Cheat Scorecard adds real benchmark-hardening value before deeper recursive adaptation, without granting it trust authority.

## OUT OF SCOPE

- Installation into PAIVOT/pvg or the GRRR runtime: requires a later reviewed integration story.
- Treating scorecard findings as verified defects: textual heuristics are advisory only.
- Any network scan of private repositories, credential use, production mutation, replay, admission, promotion, merge, or push.
- ggen, wasm4pm, dteam, or Bend integration: separate future investigations.

## DIFF BUDGET

~3 evidence/report files and under 400 changed LOC. No runtime implementation expected.

## Boundary Map

PRODUCES:
- docs/evidence/anti-cheat-scorecard/EVALUATION.md -> operator-readable evidence review and recommendation
- docs/evidence/anti-cheat-scorecard/evaluation.json -> pinned source/tool identities, command results, pattern counts, target hashes, controls, limitations, and recommendation
- docs/evidence/anti-cheat-scorecard/ARTIFACTS.md -> retained artifact hashes and redaction policy

CONSUMES:
- GRRR-gge0: story/GRRR-gge0 commit cf3eb55422ba18898541318c138cd82543419d12 -> five-file adaptation tree to scan
- external: seanchatmangpt/anti-cheat-scorecard tag v26.8.29 -> `go run . --local <repo> --checks Anti-Cheat --format json --show-details`
- existing: LICENSE -> Apache-2.0 permission review
- existing: internal/llmcheat/patterns -> 52 detector packages and focused tests

## Acceptance Criteria

1. Pin and verify the exact upstream repository, release tag, commit, license, module path, Go version, and binary/source identities; do not use an unpinned `main` branch.
2. Independently verify actual detector registration/count and run all detector package tests at the pinned tag.
3. Build the pinned CLI locally and record its SHA-256; do not submit source, credentials, protected truth, or private paths to a remote service.
4. Run `Anti-Cheat` read-only against the clean GRRR-gge0 adaptation tree and a five-file changed-file subset; retain target commit, elapsed behavior, output hash, score, finding count, and pattern counts.
5. Run deterministic controls: a seeded textual-cheat fixture must be detected; an absent input must not be misreported as success; an empty eligible root must expose the tool's perfect-score/coverage weakness; a same-target rerun must be semantically stable after removing the timestamp.
6. Classify material false positives against GRRR evidence formats, especially repeated hash keys in accounting manifests and historical prose, and identify any genuinely useful advisory signals.
7. Make an explicit integration recommendation with trust boundaries. If the tool is unsuitable as a mandatory/trusted gate, state that and recommend at most an isolated advisory wrapper with strict output/coverage validation.

## Testing Requirements

- Research tests are real command executions against pinned source; no mocks.
- Run all 52 pattern detector packages at the tag.
- Execute local scans against the clean target, five-file subset, seeded control, absent control, empty control, and rerun control.
- Verify JSON parseability and output file existence for every successful scan; absence of output must be classified as failure in the evaluation report even if upstream exits zero.
- No network scan, secret use, protected-path access, VM, replay, admission, promotion, production mutation, merge, or push.

## Skills To Use

- `research-software`: pinned-source tool evaluation.
- `pvg` and `nd`: story/evidence workflow.
- `pm_acceptor`: independent review.

## Delivery Requirements

- Record exact commands, exit codes, hashes, counts, limitations, and recommendation.
- Do not modify the external repository.
- Do not commit/push without explicit authorization.
- Developer delivers; PM independently accepts or rejects.

## nd_contract
status: new

### evidence
- Created 2026-11-03 from operator authorization to evaluate Sean Chatman's Anti-Cheat Scorecard.

### proof
- [ ] Pending pinned evaluation and evidence review.

## Acceptance Criteria


## Design


## Notes


## History


## Links
- Parent: [[GRRR-2t3h]]

## Comments
