---
id: GRRR-gge0
title: "Run one governed adaptation cycle"
status: in_progress
priority: 1
type: task
labels: [milestone-2, integration, adaptation, delivered]
parent: GRRR-2t3h
created_at: 2026-11-03T22:07:39Z
created_by: speed
updated_at: 2026-11-03T23:07:31Z
content_hash: "sha256:60ecbf149b2e7a77b064945e0fbd2864dd1c7820d3f5b7c6a988798e1ce1d7e1"
assignee: dev-GRRR-gge0
follows: [GRRR-fmvp, GRRR-34ve]
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

### CI/Test Results

Focused adaptation suite passed 15/15 under both required interpreters. Worker full no-guest inventory passed 807/807 under Python 3.14 and Python 3.12. `pvg verify`, `pvg gates`, `git diff --check`, and `git diff --cached --check` passed. Canonical CLI generation was deterministic and duplicate output failed closed. Independent security rereview returned GRRR_ADAPTATION_REREVIEW: APPROVED.

## nd_contract
status: delivered

### evidence
- Commit cf3eb55422ba18898541318c138cd82543419d12 contains the exact reviewed five-file adaptation implementation.
- Focused tests: 15/15 on system and Homebrew Python. Full no-guest worker inventory: 807/807 on both interpreters.
- Independent GRRR_ADAPTATION_REREVIEW: APPROVED after concurrent-reservation and output-boundary rework.

### proof
- [x] AC #1: exact immutable bindings and drift refusal.
- [x] AC #2: exactly two fixed offline candidates.
- [x] AC #3: reverse lexical measured 8/8 and rejected for decisive D/C leakage.
- [x] AC #4: fixed random block [4,6,4], mean 14/3, honestly below benchmark 6.0.
- [x] AC #5: no-change compose; approved default retained; all authority flags false.
- [x] AC #6: deterministic sanitized JSON/Markdown outputs with exclusive-output behavior.
- [x] AC #7: tamper, malformed, leakage, protected/traversal/symlink, duplicate, and concurrent-race paths fail closed.

## Implementation Evidence

Summary: First governed offline adaptation cycle completed with an honest no-change result. Reverse lexical scored 8/8 but was rejected for D/C local-ID leakage; fixed random seeds 45/46/47 scored [4,6,4], mean 14/3, below benchmark 6.0. Approved default retained; every authority flag false.

Commit SHA: cf3eb55422ba18898541318c138cd82543419d12.

Changed files and SHA-256:
- research/harness_adaptation.py — 31829168251d51fcede72e795eda1522192cc5f6496ed578dc769b664cf9308a
- scripts/run-harness-adaptation-cycle — 840cd2157ff5a094ea9f6cc1b6c3d92c8b82d195a9b81fde77f8d030fa3bbf20
- reports/adaptation-cycle-1.json — 550944a2b81b1e52cf4c9aaf410b5e43bcb5758aa0eb1bfa9ba4a63094d352ba
- reports/adaptation-cycle-1.md — 8e3c2ec84f2e424b1918dca21754f40a4b5ca6ea2c471cea9caf1017ca09678d
- tests/unit_harness_adaptation.py — f643c75f6799435e0919a5c3d865d30610625b095280b31cab518356cb095c23

Immutable bindings: plan 97ec4b8ccc34b3fc4da4fcfbef33b49bbb3f4f1c445cfecdb752715ddf034be1; result b7bb2ec8717e8921e16f9a3e312f6ad46839a125634dc6e3d144499cc841fefb; corpus dfa75ef2bf3d43fd4f750094fe643afe4f204812c0ae2426276bedb471fa8529; truth 7cf9f99f5836c4e3e147df2866d54480a706f2665a732fbf61bd1a0d0b4c52ea.

## CI/Test Results

Commands run:
- /usr/bin/python3 -I -B -m unittest discover -s tests -p unit_harness_adaptation.py -v — 15/15 OK
- /opt/homebrew/bin/python3 -I -B -m unittest discover -s tests -p unit_harness_adaptation.py -v — 15/15 OK
- Worker full no-guest inventory on Python 3.14 and 3.12 — 807/807 OK each
- pvg verify selected files — PASS
- pvg gates selected files — PASS
- git diff --check and git diff --cached --check — PASS

Independent review: initial GRRR_ADAPTATION_REVIEW rejected unsafe concurrent cleanup; rework removed deletion and added races; GRRR_ADAPTATION_REREVIEW: APPROVED.

Diff-budget disclosure: 5 files, 920 inserted lines, over approximate 500-LOC budget due mandatory safe traversal, concurrency, leakage, and adversarial coverage; reviewer considered structure justified.

## AC Verification

1. PASS — exact immutable bindings fail closed.
2. PASS — exactly reverse lexical and fixed random 45/46/47; no search/model call.
3. PASS — reverse lexical 8/8 measured and rejected for leakage.
4. PASS — random block [4,6,4], mean 14/3; did not beat 6.0.
5. PASS — no-change compose; approved default and false authorities retained.
6. PASS — deterministic sanitized exclusive JSON/Markdown outputs.
7. PASS — tamper, malformed, leakage, protected/traversal/symlink, duplicate, and concurrent-race paths fail closed.

## nd_contract
status: delivered

### evidence
- Commit cf3eb55422ba18898541318c138cd82543419d12; focused 15/15 both interpreters; worker full 807/807 both; independent re-review approved.

### proof
- [x] AC #1: immutable input binding and drift refusal.
- [x] AC #2: exactly two fixed offline candidates.
- [x] AC #3: leakage-rejecting reverse-lexical probe.
- [x] AC #4: honest fixed-block comparison.
- [x] AC #5: no-change compose and false authority flags.
- [x] AC #6: deterministic sanitized outputs.
- [x] AC #7: adversarial fail-closed coverage.

## Implementation Evidence (READY_FOR_REVIEW; intentionally not delivered)

PROOF:

### Scope and result
- Worktree: `.claude/worktrees/dev-GRRR-gge0` on `story/GRRR-gge0`, based on `5b50e29272819da205fc09e051f82c2639a7a197`.
- Completed exactly one offline deterministic Propose-Probe-Compose cycle. Compose decision: `no-change`; retained `retain-deterministic-lexical-baseline`.
- Reverse lexical selected 8 D IDs, measured 8/8, and was rejected by the D/C local-ID-prefix leakage gate.
- Random seeds 45/46/47 were evaluated as one full block: defect counts 4/6/4, mean 14/3 = 4.666667, critical mean 10/3, clean mean 10/3, unique defects 12; did not exceed benchmark 6.0.
- No network, Jev call, secret read, `/Library/GRRR` access, VM, replay, admission, promotion, production mutation, source commit, merge, or push was performed.

### Files and SHA-256
- `research/harness_adaptation.py` — `f090ea195bfe4c540e5e1e6b4192afd4765ca1a175ee974120c9332037b05a92`
- `scripts/run-harness-adaptation-cycle` — `27c1b80ad3dc1aa1b1a0fe5e5c42ab24c1796964b726e36372f67c70e8f0e343`
- `reports/adaptation-cycle-1.json` — `18ce890a47cc057445600b6527c94c34d0fc58b0c41b19643bd6bb2da29b0a8c`
- `reports/adaptation-cycle-1.md` — `530974387a25019a22667bae49c4506ad06758ae3d79d4e58924b1b7bb1921b9`
- `tests/unit_harness_adaptation.py` — `0c272b64ed61184789b27cb9cb5a4e8c77f6e90667659c4ca96fb805013926ea`

### Required CLI
- `scripts/run-harness-adaptation-cycle --plan corpus/evaluation-plan-v2-proposed.json --result docs/evidence/jev-selector-measurement/three-arm-result-20261103T214701Z/report.json --corpus-root corpus --output reports/adaptation-cycle-1.json --summary-output reports/adaptation-cycle-1.md`
- Exit 0; stdout: `{"compose":"no-change",...,"status":"complete"}`. Fresh-output rerun was byte-identical; a duplicate invocation exited 2 without overwriting.

### Test and gate evidence
- `/usr/bin/python3 -m py_compile research/harness_adaptation.py scripts/run-harness-adaptation-cycle tests/unit_harness_adaptation.py` — PASS.
- `/opt/homebrew/bin/python3 -m py_compile research/harness_adaptation.py scripts/run-harness-adaptation-cycle tests/unit_harness_adaptation.py` — PASS.
- `/usr/bin/python3 -m unittest -v tests.unit_harness_adaptation tests.unit_selector_comparison tests.unit_evaluation_plan_v2 tests.unit_jev_three_arm_analysis` — 55/55 PASS, 0 failures/errors/skips.
- `/opt/homebrew/bin/python3 -m unittest -v tests.unit_harness_adaptation tests.unit_selector_comparison tests.unit_evaluation_plan_v2 tests.unit_jev_three_arm_analysis` — 55/55 PASS, 0 failures/errors/skips.
- `pvg verify research/harness_adaptation.py scripts/run-harness-adaptation-cycle reports/adaptation-cycle-1.json reports/adaptation-cycle-1.md tests/unit_harness_adaptation.py --include-tests --format=text` — `VERIFY: PASSED (2 files scanned, 0 issues)`.
- `pvg gates research/harness_adaptation.py scripts/run-harness-adaptation-cycle reports/adaptation-cycle-1.json reports/adaptation-cycle-1.md tests/unit_harness_adaptation.py --format text` — `GATES: PASS (0 warn, 0 skipped)`.
- `git diff --check` — PASS (after intent-to-add registration for the five new paths).
- Sanitizer assertion script over both final outputs — PASS: no `expected_behavior`, raw provider response text, or `/Library/GRRR` path.

### AC Verification
| AC | Result | Evidence |
|---|---|---|
| 1. Exact immutable input binding and fail-closed schema/hash drift | PASS | `run_adaptation_cycle`; exact plan/result/truth/manifest/public hashes in report; real temp-copy tamper tests |
| 2. Exactly two fixed candidates, no search/holdout/model/credential input | PASS | reverse lexical plus fixed seeds 45/46/47; report provenance/controls; `tests/unit_harness_adaptation.py` |
| 3. Reverse lexical 8/8 but leakage rejection decisive | PASS | report proposal 1; reverse test |
| 4. Full random-block metrics vs benchmark 6.0 | PASS | report proposal 2; block test |
| 5. Pre-registered no-change compose and all authority false | PASS | report compose/authority/controls; no-compose test |
| 6. Deterministic exclusive JSON plus sanitized Markdown | PASS | real CLI integration test and final byte hashes |
| 7. Fail-closed tamper/malformed/leakage/unsafe/duplicate behavior | PASS | real-input tests; no skips or trusted-evaluator mocks |

LEARNINGS:
- The corpus canonical freeze digest alone would not reject semantically unchanged manifest whitespace drift; exact manifest/public byte hashes were also pinned and tested.
- Separating immutable binding from fixed candidate generation made leakage rejection auditable without exposing protected expected behavior.
- The honest no-change outcome is correctly representable as a complete cycle rather than a failed run.

### Budget disclosure
- Current diff: 5 files, 646 added lines versus the stated approximate 4 files / under-500 LOC budget. The overage is driven by mandatory fail-closed real-input cases and the separately required Markdown summary; no AC was waived.

## nd_contract
status: in_progress

### evidence
- Final source/report hashes and all required focused tests/gates recorded above; work remains uncommitted and not delivered pending independent PM review.

### proof
- [x] AC #1: Exact approved-plan/result/frozen-corpus/truth bytes are SHA-256-bound and drift fails closed.
- [x] AC #2: Exactly reverse-lexical and fixed random seeds 45/46/47 are generated without search or forbidden inputs.
- [x] AC #3: Reverse lexical records 8/8 and remains rejected for D/C local-ID-prefix leakage.
- [x] AC #4: Seeds 45/46/47 are evaluated as a full block with all required metrics against 6.0.
- [x] AC #5: No candidate composed a change; default retained and every authority flag is false.
- [x] AC #6: Exclusive deterministic JSON and sanitized Markdown outputs were generated and tested.
- [x] AC #7: Real-input drift, malformed selection, leakage, unsafe output, and duplicate-output cases fail closed without skips.

## History
- 2026-11-03T22:07:57Z status: open -> in_progress
- 2026-11-03T22:07:57Z auto-follows: linked to predecessor GRRR-fmvp
- 2026-11-03T22:07:57Z claimed by dev-GRRR-gge0
- 2026-11-03T23:07:31Z status: in_progress -> in_progress
- 2026-11-03T23:07:31Z auto-follows: linked to predecessor GRRR-34ve

## Links
- Parent: [[GRRR-2t3h]]
- Follows: [[GRRR-fmvp]], [[GRRR-34ve]]

## Comments

### 2026-11-03T22:07:59Z speed
## 2026-11-03 Adaptation Story Created and Stacked

Operator authorized starting the post-foundational adaptation phase. Story GRRR-gge0 creates one bounded offline Propose–Probe–Compose cycle using the completed three-arm result as immutable input.

Because the result artifacts are currently on unmerged story/GRRR-6sso at 5b50e29272819da205fc09e051f82c2639a7a197, the implementation branch is deliberately stacked from that commit. This is a repository-only dependency; no protected runtime authority, external call, promotion, replay, admission, production mutation, merge, or push is granted.

### 2026-11-03T22:08:38Z speed
## 2026-11-03 Adaptation Cycle Dispatch

Fresh GLM agent developer_grrr_gge0_adaptation_v1 claimed the stacked worktree at base 5b50e29. Scope is exactly one offline deterministic Propose–Probe–Compose cycle: reverse-lexical leakage rejection plus fixed random seeds 45/46/47 against benchmark 6.0. Denials: network/Jev, secret read, protected access, VM, replay, admission, promotion, production mutation, commit, merge, push.

### 2026-11-03T22:35:10Z speed
## 2026-11-03 Adaptation Security Rework — Parent Verified

Final WIP hashes after security rework:
- research/harness_adaptation.py 31829168251d51fcede72e795eda1522192cc5f6496ed578dc769b664cf9308a
- scripts/run-harness-adaptation-cycle 41f1fe749581ad902f554111cc343201588ee09c23d095ee28bc1fd7ab95fc5a
- reports/adaptation-cycle-1.json 550944a2b81b1e52cf4c9aaf410b5e43bcb5758aa0eb1bfa9ba4a63094d352ba
- reports/adaptation-cycle-1.md 8e3c2ec84f2e424b1918dca21754f40a4b5ca6ea2c471cea9caf1017ca09678d
- tests/unit_harness_adaptation.py 50f5eba4bfaf6a95a2b0b7217037ff6f7567938a5bc4b8f6df9c8d811bd38c61

Rework fixes: lexical/double-slash/protected path rejection before path syscalls; O_NOFOLLOW dirfd ancestor traversal with inode checks; held-parent exclusive writes; deterministic undeclared reverse-lexical leakage detection; all-defect composition control; non-immediate symlink/traversal/syscall-guard regressions.

Parent reran focused adaptation tests 13/13 on both interpreters, pvg verify PASS, gates PASS, diff checks PASS. Current diff is 5 files/855 added lines, 355 over approximate story budget because mandatory safe traversal and adversarial tests expanded scope; this remains explicitly disclosed for PM review. No network/Jev/secret/protected access/replay/admission/promotion/production mutation/commit/merge/push.

### 2026-11-03T22:45:32Z speed
## 2026-11-03 Concurrent-Deletion Rework — Parent Verified

Independent review correctly rejected unconditional failure cleanup because it could delete concurrent output entries this invocation never created. Rework removed all unlink/remove cleanup, preserves partial exclusive-created artifacts, closes descriptors in one finally path, and detects short writes. Deterministic race tests now prove concurrent Markdown and concurrent JSON+Markdown entries remain byte-unchanged when reservation races occur.

Final hashes:
- research/harness_adaptation.py 31829168251d51fcede72e795eda1522192cc5f6496ed578dc769b664cf9308a
- scripts/run-harness-adaptation-cycle 840cd2157ff5a094ea9f6cc1b6c3d92c8b82d195a9b81fde77f8d030fa3bbf20
- reports/adaptation-cycle-1.json 550944a2b81b1e52cf4c9aaf410b5e43bcb5758aa0eb1bfa9ba4a63094d352ba
- reports/adaptation-cycle-1.md 8e3c2ec84f2e424b1918dca21754f40a4b5ca6ea2c471cea9caf1017ca09678d
- tests/unit_harness_adaptation.py f643c75f6799435e0919a5c3d865d30610625b095280b31cab518356cb095c23

Parent reran focused adaptation suite 15/15 on both interpreters; pvg verify/gates and diff checks passed. Worker full no-guest inventory passed 807/807 on both interpreters. No network/Jev/secret/protected access/replay/admission/promotion/production mutation/commit/merge/push.

### 2026-11-03T22:47:09Z speed
## 2026-11-03 Adaptation Narrow Security Re-review — APPROVED

Fresh Astra reviewer verdict: GRRR_ADAPTATION_REREVIEW: APPROVED. Reviewer matched all five final hashes, reran the focused suite (15/15), and independently probed partial writes, zero/negative writes, reservation races, descriptor closure, and close failures. It confirmed no implementation cleanup deletes concurrent entries and all prior adaptation semantics remain intact: reverse lexical 8/8 rejected for leakage; fixed block mean 14/3 below benchmark 6.0; no composed strategy change; all authority flags false.

Approval is scoped to the bounded adaptation implementation, not broader security certification or runtime promotion. Work remains uncommitted pending explicit operator commit authorization.

### 2026-11-03T23:06:11Z speed
## Implementation Evidence (DELIVERED)

Summary: The first post-foundational, repository-only Karpathy/Harness²-style Propose–Probe–Compose cycle completed with an honest no-change outcome. Reverse lexical scored 8/8 but was rejected for decisive D/C local-ID-prefix leakage. The fixed random block seeds 45/46/47 scored [4,6,4], mean 14/3, below the immutable random benchmark 6.0. No strategy was composed; the approved default remains retain-deterministic-lexical-baseline and every authority flag is false.

Commit: cf3eb55422ba18898541318c138cd82543419d12 on story/GRRR-gge0 (base 5b50e29272819da205fc09e051f82c2639a7a197). Worktree clean after commit.

Files and SHA-256:
- research/harness_adaptation.py 31829168251d51fcede72e795eda1522192cc5f6496ed578dc769b664cf9308a
- scripts/run-harness-adaptation-cycle 840cd2157ff5a094ea9f6cc1b6c3d92c8b82d195a9b81fde77f8d030fa3bbf20
- reports/adaptation-cycle-1.json 550944a2b81b1e52cf4c9aaf410b5e43bcb5758aa0eb1bfa9ba4a63094d352ba
- reports/adaptation-cycle-1.md 8e3c2ec84f2e424b1918dca21754f40a4b5ca6ea2c471cea9caf1017ca09678d
- tests/unit_harness_adaptation.py f643c75f6799435e0919a5c3d865d30610625b095280b31cab518356cb095c23

Immutable inputs:
- Approved plan SHA 97ec4b8ccc34b3fc4da4fcfbef33b49bbb3f4f1c445cfecdb752715ddf034be1
- Completed result SHA b7bb2ec8717e8921e16f9a3e312f6ad46839a125634dc6e3d144499cc841fefb
- Corpus freeze digest dfa75ef2bf3d43fd4f750094fe643afe4f204812c0ae2426276bedb471fa8529
- Protected truth SHA 7cf9f99f5836c4e3e147df2866d54480a706f2665a732fbf61bd1a0d0b4c52ea

## CI/Test Results

Commands run:
- PYTHONDONTWRITEBYTECODE=1 GRRR_JEV_DISABLE=1 /usr/bin/python3 -I -B -m unittest discover -s tests -p unit_harness_adaptation.py -v — 15/15 OK
- PYTHONDONTWRITEBYTECODE=1 GRRR_JEV_DISABLE=1 /opt/homebrew/bin/python3 -I -B -m unittest discover -s tests -p unit_harness_adaptation.py -v — 15/15 OK
- Worker full no-guest inventory under Python 3.14 and 3.12 — 807/807 OK each
- pvg verify selected five files — PASS
- pvg gates selected five files — PASS
- git diff --check and git diff --cached --check — PASS

Independent review:
- GRRR_ADAPTATION_REVIEW: REJECTED initially because failure cleanup could delete concurrent files.
- Rework removed deletion, preserved partial exclusive artifacts, and added race tests.
- GRRR_ADAPTATION_REREVIEW: APPROVED after 15/15 focused tests and independent race probes.

Diff-budget disclosure: 5 files / 920 inserted lines, exceeding the approximate 4-file under-500-LOC budget. Overage is driven by mandatory safe openat traversal, no-deletion concurrency behavior, leakage detection, syscall guards, and adversarial tests. Independent review considered the five-file structure justified; no mandatory tests were dropped.

## AC Verification

| AC | Result |
|---|---|
| 1 | PASS: exact plan/result/corpus/truth hashes bind before proposal. |
| 2 | PASS: exactly reverse-lexical and fixed random block 45/46/47; no seed search or model call. |
| 3 | PASS: reverse lexical measured 8/8 and decisively rejected for D/C prefix leakage. |
| 4 | PASS: fixed block repetitions [4,6,4], mean 14/3, critical 10/3, clean 10/3, unique 12; below 6.0. |
| 5 | PASS: no-change compose; approved default retained; all authority flags false. |
| 6 | PASS: deterministic exclusive JSON/Markdown outputs with sanitized input hashes and metrics. |
| 7 | PASS: real-input tamper, malformed selection, leakage, protected/double-slash/traversal, symlink, duplicate-output, and concurrent reservation tests fail closed. |

## nd_contract
status: delivered

### evidence
- Implementation commit cf3eb55422ba18898541318c138cd82543419d12; focused 15/15 tests on both interpreters; worker full no-guest 807/807 on both; independent narrow security rereview approved.

### proof
- [x] AC #1: immutable input binding and fail-closed drift handling proven.
- [x] AC #2: exactly two fixed offline candidates generated without forbidden inputs.
- [x] AC #3: reverse lexical 8/8 measured and rejected as leakage.
- [x] AC #4: full fixed random block evaluated honestly and did not beat benchmark.
- [x] AC #5: no strategy composed; approved default and false authority flags preserved.
- [x] AC #6: deterministic sanitized outputs and exclusive-output behavior proven.
- [x] AC #7: adversarial path, tamper, race, and malformed-input coverage passed.
