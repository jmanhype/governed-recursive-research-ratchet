---
id: GRRR-888u
title: "Evaluate Sean Chatman Anti-Cheat Scorecard"
status: in_progress
priority: 1
type: task
labels: [milestone-2, research, external-tooling, security-review, rejected]
parent: GRRR-2t3h
created_at: 2026-11-03T23:26:01Z
created_by: speed
updated_at: 2026-11-04T00:37:48Z
content_hash: "sha256:14cb6d7ae80c0b973cb00be0aac729d5756e49399c3c85563bfc68ca7b1f5cd6"
follows: [GRRR-gge0, GRRR-fmvp, GRRR-34ve]
assignee: dev-GRRR-888u
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
## Implementation Evidence (DELIVERED)

Summary: Proof-format rework for the completed advisory-only Anti-Cheat Scorecard evaluation. The substantive evidence and independent review remain unchanged; this note supplies the canonical AC table and retrospective learnings required by the delivery gate.

Commit SHA: 86ace00860f62f302f4f633eefa6c98b5cce8252.

### CI/Test Results

Commands run (recorded from the unchanged evidence at commit 86ace00860f62f302f4f633eefa6c98b5cce8252; not rerun in this proof-format rework):
- git clone/checkout v26.8.29 and commit identity check — exit 0.
- go test ./internal/llmcheat/patterns/... -count=1 — exit 0, 53/53 pattern-related packages OK.
- go build -o /tmp/anti-cheat-scorecard-v26.8.29 . — exit 0, binary SHA-256 d6df6a07b5d818bf11bed026455acf531307afb39c92bf7b58cae0c93883ee4e.
- Full GRRR-gge0 Anti-Cheat scan — exit 0, 79.67s, score 1/10, 5,487 detail rows (5,486 warnings plus one informational row).
- Five-file subset scan — exit 0, 0.15s, score 7/10, two warnings.
- Seeded textual-cheat control — exit 0, five warnings.
- Absent-input control — exit 0 with no output, classified failure.
- Empty-root control — exit 0 with perfect 10/10, classified unsafe coverage behavior.
- Same-target subset rerun — exit 0; JSON outputs were semantically equal after timestamp removal.
- pvg verify selected evidence files — PASS.
- pvg gates selected evidence files — PASS.
- git diff --check — PASS.

Rework boundary: no source or evidence file was changed and no external evaluation, protected-path access, replay, admission, promotion, production mutation, merge, push, credential use, or commit was performed.

### AC Verification

| AC # | Requirement | Recorded Evidence | Status |
|---|---|---|---|
| 1 | Pin and verify upstream repository, tag, commit, license, module, Go/tool identities without using unpinned main. | v26.8.29 at 5271351d079f79634de2f8b91970b80daf9bcb86; Apache-2.0; module and local Go/binary identities recorded. | PASS |
| 2 | Independently verify detector registration/count and run all detector package tests at the pinned tag. | 52 registered detector packages across seven categories; 53 pattern-related packages tested OK. | PASS |
| 3 | Build the pinned CLI locally, record SHA-256, and keep source, credentials, protected truth, and private paths remote. | Local binary SHA-256 d6df6a07b5d818bf11bed026455acf531307afb39c92bf7b58cae0c93883ee4e; no remote scan or credential submission. | PASS |
| 4 | Run read-only full-tree and five-file changed-subset scans with target identity, timing, output hash, score, and counts. | Clean target cf3eb55422ba18898541318c138cd82543419d12; full and subset outputs, hashes, elapsed times, scores, finding counts, and pattern counts recorded. | PASS |
| 5 | Run seeded positive, absent-input, empty-root, and same-target rerun controls. | Five-warning seeded detection; absent-input zero-with-no-output failure; empty-root perfect-score weakness; timestamp-normalized rerun stability recorded. | PASS |
| 6 | Classify material GRRR false positives and useful advisory signals. | Repeated accounting hashes/historical prose classes and useful textual-cheat signals classified with measured counts and examples; 4,599 false lockfile-checksum mismatches identified. | PASS |
| 7 | State integration recommendation and trust boundaries, including wrapper validation if not trusted. | Advisory-only recommendation recorded; mandatory/trusted authority rejected; isolated future wrapper must validate output existence, coverage, and failure semantics. | PASS |

- [x] AC #1: exact pinned repository, release, commit, license, module, Go, and binary identities verified.
- [x] AC #2: detector registration/count and all pattern-related package tests verified.
- [x] AC #3: pinned local CLI identity and privacy boundary verified.
- [x] AC #4: clean full-tree and five-file subset scans verified.
- [x] AC #5: seeded, absent, empty, and rerun controls verified.
- [x] AC #6: GRRR false-positive classes and useful advisory signals verified.
- [x] AC #7: advisory-only trust boundary and wrapper validation requirements verified.

LEARNINGS:
- The deterministic delivery parser requires the canonical `### AC Verification` heading and recognizable table/checklist syntax; a semantically complete differently headed table is not sufficient.
- A rejection can remove the delivered label even when committed evidence remains coherent, so proof-format rework must end with the atomic `pvg story deliver` transition rather than manual label choreography.
- Do not rerun expensive or external evaluations to repair a delivery-contract defect when the immutable evidence commit already contains the required measurements.
- The Anti-Cheat tool’s zero-exit behavior on absent input and perfect score on an empty root are material wrapper requirements, not incidental observations.

## nd_contract
status: delivered

### evidence
- Evidence commit: 86ace00860f62f302f4f633eefa6c98b5cce8252.
- Substantive evidence files, external scan results, and independent approval are unchanged.
- Rework limited to the nd delivery note; no source/evidence file mutation, external call, protected access, replay, admission, promotion, production mutation, merge, push, or commit.

### proof
- [x] AC #1: pinned source identity verified.
- [x] AC #2: detector count and pattern tests verified.
- [x] AC #3: local binary identity and privacy boundary verified.
- [x] AC #4: full and subset scan evidence verified.
- [x] AC #5: deterministic and failure-mode controls verified.
- [x] AC #6: false positives and advisory signals classified.
- [x] AC #7: advisory-only trust boundary recorded.

## nd_contract
status: rejected

### evidence
- PM rejection applied via pvg story reject on 2026-11-03.

### proof
- [ ] Story requires another developer delivery before it can be accepted.


## AC Verification Checklist

- [x] AC #1: exact repository, tag, commit, license, module, source Go version, local Go version, and binary identity verified.
- [x] AC #2: 52 registered detector packages across seven categories verified; 53 pattern-related packages passed tests.
- [x] AC #3: pinned CLI built locally with recorded SHA-256; no source, credential, protected truth, or private remote scan submitted.
- [x] AC #4: clean full GRRR-gge0 scan and five-file subset scan recorded with target commit, elapsed time, output hash, score, findings, and pattern counts.
- [x] AC #5: seeded positive, absent-input, empty-root, and same-target rerun controls recorded with exit and output behavior.
- [x] AC #6: material GRRR false-positive classes and useful advisory signals classified with measured counts and examples.
- [x] AC #7: advisory-only recommendation and false authority flags recorded, with mandatory future wrapper gates.

## nd_contract
status: delivered

### evidence
- Commit 86ace00860f62f302f4f633eefa6c98b5cce8252.
- All 53 pattern-related Go packages passed.
- Full, subset, seeded, absent, empty, and rerun controls completed.
- Independent reviewer returned ANTI_CHEAT_EVAL_REREVIEW: APPROVED.
- pvg verify and pvg gates passed on committed evidence.

### proof
- [x] AC #1 through AC #7 independently verified from evidence.

## nd_contract
status: delivered

### evidence
- Transitioned via pvg story deliver on 2026-11-03.

### proof
- [ ] Developer evidence block must remain authoritative above this contract.


## Implementation Evidence

Summary: Evaluated Sean Chatman’s Anti-Cheat Scorecard at stable tag v26.8.29 and concluded it is useful for advisory textual-cheat triage but unsuitable as a trusted or mandatory GRRR gate. The full GRRR-gge0 scan produced 5,487 detail rows—5,486 warnings and one informational row—score 1/10, dominated by 4,599 false lockfile-checksum-mismatch findings. The five-file adaptation subset produced two warnings, and the seeded control detected five real textual-cheat patterns. Missing input exited zero without output and an empty eligible root exited zero with perfect 10/10, proving the need for a strict future wrapper and advisory-only authority boundary.

Commit SHA: 86ace00860f62f302f4f633eefa6c98b5cce8252.

Changed files and SHA-256:
- docs/evidence/anti-cheat-scorecard/evaluation.json — 2bcaa7cdaacc6b8d642846c498fcf1e93655948afa2cd1a8463fcbc36359bd12
- docs/evidence/anti-cheat-scorecard/EVALUATION.md — 1105fbfeb68a407cf6ec465190d5ec2226f06a00786f7fbc8f23c68348d504c8
- docs/evidence/anti-cheat-scorecard/ARTIFACTS.md — 643ee210dd0abfa925abe6cb454d939cb5102738d3e9d46ca9688a357eef1fa0

Pinned source identity:
- Repository https://github.com/seanchatmangpt/anti-cheat-scorecard
- Tag v26.8.29
- Commit 5271351d079f79634de2f8b91970b80daf9bcb86
- License Apache-2.0
- Module github.com/ossf/scorecard/v5
- Built binary SHA-256 d6df6a07b5d818bf11bed026455acf531307afb39c92bf7b58cae0c93883ee4e
- Target GRRR-gge0 commit cf3eb55422ba18898541318c138cd82543419d12, clean worktree

### CI/Test Results

Commands run:
- git clone --filter=blob:none https://github.com/seanchatmangpt/anti-cheat-scorecard /tmp/anti-cheat-scorecard-research — exit 0
- cd /tmp/anti-cheat-scorecard-research && git checkout v26.8.29 && test "$(git rev-parse HEAD)" = 5271351d079f79634de2f8b91970b80daf9bcb86 — exit 0
- go version — Go 1.26.7 darwin/arm64
- go test ./internal/llmcheat/patterns/... -count=1 — exit 0, 53/53 packages OK
- go build -o /tmp/anti-cheat-scorecard-v26.8.29 . — exit 0, binary SHA d6df6a07b5d818bf11bed026455acf531307afb39c92bf7b58cae0c93883ee4e
- Full target Anti-Cheat scan — exit 0, 79.67s, output SHA f56ee077318bea77d1678e5666b5a06904ff5651477f9a8a9f630d923e1f418f, score 1/10, 5,487 rows
- Five-file subset scan — exit 0, 0.15s, output SHA 9b6e5e04fdc52208670d74ba53c63ad20146badcf7c36ac68cb57e5ea0c284a2, score 7/10, two warnings
- Seeded textual-cheat scan — exit 0, 0.04s, output SHA af70a5118096b3d792e381c07bb5711521d81e53b9d3b34ab3506902ef3fcdd3, five warnings
- Absent-input control — exit 0 without output, classified failure
- Empty-root control — exit 0, output SHA 57ec647ca337d632ae1894c34f3e4d2fd2a8c1a575db585519f52fb02ea2a000, perfect 10/10, classified unsafe
- Subset rerun control — exit 0, valid 1,406-byte output, semantically equal after timestamp removal
- pvg verify selected evidence files — PASS
- pvg gates selected evidence files — PASS
- git diff --check — PASS

Independent review:
- Initial technical review rejected a warning-count error and missing command/exit evidence.
- Corrected full count to 5,486 warnings + 1 information row and added complete reproduction evidence.
- Final narrow reviewer returned ANTI_CHEAT_EVAL_REREVIEW: APPROVED.

Diff-budget disclosure: 3 files and 429 inserted lines, within the approximate 3-file/under-400-LOC budget by file count and 29 lines over the rough LOC guide because exact reproduction commands and safety limitations were mandatory.

## AC Verification

| AC | Result |
|---|---|
| 1 | PASS: exact repository/tag/commit/license/module/Go/tool identities verified. |
| 2 | PASS: 52 detector packages and seven categories verified; 53 pattern-related packages tested OK. |
| 3 | PASS: pinned local binary built, hashed, and used; no remote scan or credential use. |
| 4 | PASS: clean full target and five-file subset scans recorded with commit, elapsed time, hashes, scores, and counts. |
| 5 | PASS: seeded, absent, empty, and rerun controls recorded with exit/output behavior. |
| 6 | PASS: false-positive classes and useful advisory signals classified with counts and examples. |
| 7 | PASS: advisory-only recommendation and all authority flags false. |

## nd_contract
status: delivered

### evidence
- Evidence commit 86ace00860f62f302f4f633eefa6c98b5cce8252; all pattern tests and local controls completed; independent narrow review approved.

### proof
- [x] AC #1: pinned source identity verified.
- [x] AC #2: detector registry/count and tests verified.
- [x] AC #3: pinned local binary identity and privacy boundary verified.
- [x] AC #4: full and subset target scans recorded.
- [x] AC #5: deterministic and failure-mode controls recorded.
- [x] AC #6: false positives and useful signals classified.
- [x] AC #7: advisory-only trust boundary recorded.

## History
- 2026-11-03T23:27:53Z status: open -> in_progress
- 2026-11-03T23:27:53Z auto-follows: linked to predecessor GRRR-gge0
- 2026-11-03T23:27:53Z claimed by dev-GRRR-888u
- 2026-11-04T00:16:12Z status: in_progress -> in_progress
- 2026-11-04T00:16:12Z auto-follows: linked to predecessor GRRR-fmvp
- 2026-11-04T00:34:59Z status: in_progress -> open
- 2026-11-04T00:34:59Z released by speed
- 2026-11-04T00:35:44Z status: open -> in_progress
- 2026-11-04T00:35:44Z auto-follows: linked to predecessor GRRR-34ve
- 2026-11-04T00:35:44Z claimed by dev-GRRR-888u

## Links
- Parent: [[GRRR-2t3h]]
- Follows: [[GRRR-gge0]], [[GRRR-fmvp]], [[GRRR-34ve]]

## Comments

### 2026-11-03T23:27:56Z speed
## 2026-11-03 Anti-Cheat Scorecard Evaluation Started

Story claimed and stacked from accepted GRRR-gge0 commit cf3eb55422ba18898541318c138cd82543419d12. Pinned external source is seanchatmangpt/anti-cheat-scorecard v26.8.29 commit 5271351d079f79634de2f8b91970b80daf9bcb86. Scope is research/advisory evaluation only; no runtime integration, trusted-gate authority, protected access, network scan, credential use, replay, admission, promotion, production mutation, merge, or push.

### 2026-11-03T23:30:02Z speed
## 2026-11-03 Anti-Cheat Scorecard Evaluation WIP — Complete, Review Pending

Pinned source: seanchatmangpt/anti-cheat-scorecard v26.8.29 commit 5271351d079f79634de2f8b91970b80daf9bcb86, Apache-2.0. Built binary SHA d6df6a07b5d818bf11bed026455acf531307afb39c92bf7b58cae0c93883ee4e. All 53 pattern-related packages passed; log SHA bbfe64ec1c98b9f55da6243b896415d2c621815481d0cf7cffeb1106dcd7ec0a.

Clean GRRR-gge0 target at cf3eb55422ba18898541318c138cd82543419d12: full scan exited 0 in 79.67s, output SHA f56ee077318bea77d1678e5666b5a06904ff5651477f9a8a9f630d923e1f418f, score 1/10, 5487 warnings, dominated by 4599 false lockfile-checksum-mismatch findings. Five-file subset exited 0 in 0.15s, score 7/10, two warnings. Seeded control detected five textual-cheat patterns. Absent input exited 0 without output; empty input exited 0 with perfect 10/10; subset rerun was semantically stable after timestamp removal but raw hashes changed.

Current evidence files:
- docs/evidence/anti-cheat-scorecard/evaluation.json 387770a18b120695c749bf6593f220af38b119c97a54c44fb1ecf0909626f74b
- docs/evidence/anti-cheat-scorecard/EVALUATION.md 6b93c9a66fe92331609c9588ac85f5dfe9dc43d522478d4fd85b37589f39715eb
- docs/evidence/anti-cheat-scorecard/ARTIFACTS.md 2a5262792af02554e9c65e082a4a924041322e4ecf35a4c53f7dbcbdbf1ec5a5

Recommendation: advisory only, not a trusted/mandatory gate. pvg verify/gates and diff checks passed; JSON parsed; local-path/credential scan clean. No commit, external repo mutation, network scan, secret use, protected access, replay, admission, promotion, production mutation, merge, or push.

### 2026-11-03T23:30:33Z speed
## Correction: Exact Anti-Cheat Evidence Hashes

The previous note included incorrect anticipated hashes. Parent-measured current file hashes are authoritative:
- docs/evidence/anti-cheat-scorecard/evaluation.json 39ec7f8de7d303e23cc3cc9bfffafe5a869278a3f1000e4f6cb25fb7684eed88
- docs/evidence/anti-cheat-scorecard/EVALUATION.md 070554384855387af6d6b27e928b35451cdd22a3559df4ccc548051dcf5957b6
- docs/evidence/anti-cheat-scorecard/ARTIFACTS.md 5c44d2058745dc4afbcf2ed016e80ec2d3849a00b1893590ce85e08996ffa943

All other measured counts, output hashes, controls, and advisory-only recommendation remain unchanged.

### 2026-11-03T23:42:48Z speed
## 2026-11-03 Anti-Cheat Evaluation Review Rework

Independent review rejected two evidence gaps. Corrected full scan warning count from 5487 to 5486 plus one informational row; pattern counts now total warnings exactly. Added auditable reproduction_commands for clone/checkout, target identity, all-pattern tests, binary build, full scan, five-file subset construction/scan, seeded fixture/scan, absent input, empty input, and rerun. Updated hashes and retained control exit codes. Advisory-only recommendation unchanged.

### 2026-11-03T23:49:02Z speed
## 2026-11-03 Anti-Cheat Evaluation Narrow Re-review — APPROVED

Fresh reviewer verdict: ANTI_CHEAT_EVAL_REREVIEW: APPROVED. Reviewer verified current evidence hashes 2bcaa7cdaacc6b8d642846c498fcf1e93655948afa2cd1a8463fcbc36359bd12, 1105fbfeb68a407cf6ec465190d5ec2226f06a00786f7fbc8f23c68348d504c8, and 643ee210dd0abfa925abe6cb454d939cb5102738d3e9d46ca9688a357eef1fa0; confirmed missing exit-code/output fields; corroborated 53 pattern-test packages, binary identity, subset rerun validity, full count arithmetic, and unchanged advisory-only conclusion. No mutation or operational authority.

### 2026-11-04T00:18:41Z speed
## Implementation Evidence

Summary: Sean Chatman Anti-Cheat Scorecard v26.8.29 was pinned, built, tested, and evaluated read-only against clean GRRR-gge0 evidence. Result is advisory-only because the tool detects real textual cheats but misclassifies GRRR accounting evidence and exits zero on absent or empty inputs.

Commit SHA: 86ace00860f62f302f4f633eefa6c98b5cce8252.

Evidence hashes:
- docs/evidence/anti-cheat-scorecard/evaluation.json — 2bcaa7cdaacc6b8d642846c498fcf1e93655948afa2cd1a8463fcbc36359bd12
- docs/evidence/anti-cheat-scorecard/EVALUATION.md — 1105fbfeb68a407cf6ec465190d5ec2226f06a00786f7fbc8f23c68348d504c8
- docs/evidence/anti-cheat-scorecard/ARTIFACTS.md — 643ee210dd0abfa925abe6cb454d939cb5102738d3e9d46ca9688a357eef1fa0

### CI/Test Results

Commands run:
- git clone/checkout v26.8.29 and commit identity check — exit 0
- go test ./internal/llmcheat/patterns/... -count=1 — exit 0, 53/53 packages
- go build -o /tmp/anti-cheat-scorecard-v26.8.29 . — exit 0, binary SHA d6df6a07b5d818bf11bed026455acf531307afb39c92bf7b58cae0c93883ee4e
- full GRRR-gge0 scan — exit 0, 79.67s, score 1/10, 5,487 rows
- five-file subset scan — exit 0, 0.15s, score 7/10, two warnings
- seeded control — exit 0, five warnings
- absent-input control — exit 0 with no output, classified failure
- empty-root control — exit 0, perfect 10/10, classified unsafe
- subset rerun — exit 0, valid output, semantically equal after timestamp removal
- pvg verify/gates and git diff checks — PASS

## AC Verification

| AC | Result |
|---|---|
| 1 | PASS: exact source/tag/commit/license/module/tool identities verified. |
| 2 | PASS: 52 detector packages and 53 pattern-related tests verified. |
| 3 | PASS: pinned local binary identity and privacy boundary verified. |
| 4 | PASS: full and five-file target scans recorded with hashes and counts. |
| 5 | PASS: seeded, absent, empty, and rerun controls recorded. |
| 6 | PASS: false-positive classes and advisory signals classified. |
| 7 | PASS: advisory-only boundary and all authority flags recorded. |

## nd_contract
status: delivered

### evidence
- Commit 86ace00860f62f302f4f633eefa6c98b5cce8252; all local controls and independent review approved.

### proof
- [x] AC #1 through AC #7 independently verified.

### 2026-11-04T00:19:13Z speed
## Implementation Evidence

Summary: Authoritative per-AC delivery proof for the completed advisory-only Anti-Cheat Scorecard evaluation.

Commit SHA: 86ace00860f62f302f4f633eefa6c98b5cce8252.

### CI/Test Results

Commands run:
- go test ./internal/llmcheat/patterns/... -count=1 — exit 0
- go build -o /tmp/anti-cheat-scorecard-v26.8.29 . — exit 0
- full target scan — exit 0
- five-file subset scan — exit 0
- seeded control — exit 0
- absent-input control — exit 0 with no output
- empty-root control — exit 0
- subset rerun — exit 0
- pvg verify/gates — PASS
- git diff --check — PASS

## AC Verification

- [x] AC #1: exact repository/tag/commit/license/module/tool identities verified.
- [x] AC #2: 52 detector packages, seven categories, and 53 pattern-related tests verified.
- [x] AC #3: pinned local binary identity and privacy boundary verified.
- [x] AC #4: full and five-file target scans recorded with hashes and counts.
- [x] AC #5: seeded, absent, empty, and rerun controls recorded.
- [x] AC #6: false-positive classes and useful advisory signals classified.
- [x] AC #7: advisory-only boundary and all authority flags recorded.

## nd_contract
status: delivered

### evidence
- Commit 86ace00860f62f302f4f633eefa6c98b5cce8252.
- All pattern tests and local controls completed.
- Independent reviewer returned ANTI_CHEAT_EVAL_REREVIEW: APPROVED.

### proof
- [x] AC #1: pinned source identity verified.
- [x] AC #2: detector registry/count and tests verified.
- [x] AC #3: pinned local binary identity and privacy boundary verified.
- [x] AC #4: full and subset target scans recorded.
- [x] AC #5: deterministic and failure-mode controls recorded.
- [x] AC #6: false positives and useful signals classified.
- [x] AC #7: advisory-only trust boundary recorded.

### 2026-11-04T00:35:00Z speed
## PM Decision
REJECTED [2026-11-03]:
EXPECTED: A delivered story must pass the deterministic delivery-proof gate with a machine-recognizable AC verification table/checklist, and the delivery proof must include a LEARNINGS: section.
DELIVERED: Fresh `pvg story verify-delivery GRRR-888u --json` passed 8/9 but failed `proof:ac_items` with "missing AC verification (checklist or table)". The notes use `## AC Verification` and `- [x] AC #...`, but not the canonical `### AC Verification` heading/bare `[x] AC` form recognized by the gate. The story body also has no `LEARNINGS:` section. Substantive committed evidence at 86ace00860f62f302f4f633eefa6c98b5cce8252 was otherwise coherent: branch ancestry and three artifact hashes matched, JSON parsed, warning counts summed to 5,486, all authority flags were false, diff-check passed, and the five-file target list matched GRRR-gge0.
GAP: The pipeline cannot certify delivery while its required AC-proof parser fails, and the mandatory retrospective learnings block is absent. These are proof-format defects, not grounds to rerun the external evaluation.
FIX: Append a new authoritative delivered note (no source or evidence-file changes required unless corrections are found) containing `### AC Verification` with a table or literal `[x] AC #n` proof for all seven ACs and a `LEARNINGS:` section; preserve commit 86ace00860f62f302f4f633eefa6c98b5cce8252. Re-deliver only after `pvg story verify-delivery GRRR-888u` passes 9/9.

## nd_contract
status: rejected

### evidence
- Fresh pvg story verify-delivery GRRR-888u --json: 8 passed, 1 failed (`proof:ac_items`).
- Story body lacks LEARNINGS and the canonical `### AC Verification` machine-readable form.

### proof
- [ ] AC #1-#7: substantive evidence was reviewed, but authoritative delivery proof does not pass the mandatory PM delivery gate.
