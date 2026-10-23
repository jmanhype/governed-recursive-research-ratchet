## Implementation Evidence (DELIVERED)

PROOF:

### CI/Test Results

Commands run:

- `./scripts/generate-validated-corpus` — PASS; emitted corpus freeze digest `ea62c30a72a1359455b94c235493d6959ce27757c38d1ba1c4fa21574d4a2c7d`.
- `./scripts/test-story validated-corpus` — PASS; **9 executed, 0 failed, 0 skipped** (repeated post-commit with the same result).
- `/usr/bin/python3 -I -B -m unittest discover -s tests -p 'unit*.py' -v` — PASS after authorized cache cleanup; **166 passed, 0 failed, 0 skipped**.
- `/opt/homebrew/bin/python3 -B -m unittest discover -s tests -p 'unit*.py' -v` — PASS after authorized cache cleanup; **166 passed, 0 failed, 0 skipped**.
- `pvg verify --include-tests <all explicit changed code/corpus/evidence paths>` — `VERIFY: PASSED (2 files scanned, 0 issues)`.
- `/usr/bin/python3 -I -B -m py_compile scripts/test-story scripts/generate-validated-corpus research/validated_corpus.py tests/integration/validated_corpus.py` — PASS.
- `git diff --check` — PASS.
- `shasum -a 256 -c docs/evidence/validated-corpus/SHA256SUMS` — PASS for all 26 recorded files.

Coverage: 166/166 required no-guest tests passed under both Python interpreters; the mandatory corpus integration gate passed 9/9. Line coverage was not measured and is not claimed.

The first full-suite attempt was preserved at 157 run / 1 setup error because free space was below 15.35 GB; after the parent's authorized regenerable-cache cleanup, both final full runs passed 166/166. That first attempt also caught a temporary import-path violation in new code, which was fixed before either final full-suite run.

### Commit

- Branch: `story/GRRR-bnkf`
- Corpus implementation SHA: `4f24b31d5f276996e1885cbad3bee0a256e661c0`
- Final evidence SHA: `aaecdb20c7a477a6c9073d776f130cef6ea552eb`

### Wiring

- `research/validated_corpus.py` generates and validates the frozen corpus.
- `scripts/generate-validated-corpus` is the reproducible operator entrypoint.
- `scripts/test-story validated-corpus` invokes `tests/integration/validated_corpus.py`.
- `corpus/public/*` is the only selector-visible projection.
- `corpus/protected/*` and `corpus/spec-map.json` hold seeds, truth, holdouts, and expected behavior.

### pvg verify

`VERIFY: PASSED (2 files scanned, 0 issues)`

### AC Verification

| AC # | Requirement | Code Location | Test Location | Status |
|------|-------------|---------------|---------------|--------|
| 1 | At least 20 independent seeded defects plus clean negatives, pinned source identities, hashed variants, critical labels, and preliminary validation | `research/validated_corpus.py`, `corpus/manifest.json`, `corpus/protected/*` | `tests/integration/validated_corpus.py` | PASS: 24 defects + 8 clean, 32 unique reconstructed variants; arbitrary seeded guest execution remains explicitly not-run because the fixed v4 input/profile admits only its original variants |
| 2 | Cover every required defect category | `research/validated_corpus.py::CATEGORIES`, `corpus/public/challenges.json` | `test_counts_categories_and_independence` | PASS: 10/10 categories |
| 3 | Freeze variants, hidden truth, critical classes, specs, and plan with public/protected separation and contamination checks | `corpus/*` | `test_public_projection_omits_protected_truth`, `test_seed_recipes_reproduce_against_exact_pinned_source` | PASS |
| 4 | Pre-register arms, seeds, repetitions, exceptions, stopping, feedback, deduplication, cost, denominator, and uncertainty | `corpus/evaluation-plan.json` | `test_plan_is_pre_registered_and_measurement_is_blocked` | PASS; operator approval is correctly still not-approved and measurement is false |
| 5 | Run preliminary trusted fixture checks while preserving downstream gates | `research/validated_corpus.py::validate`, accepted v4 snapshot evidence | `test_accepted_v4_observation_is_internally_verified`, `test_downstream_gates_remain_not_run` | PASS for static seed validation plus accepted v4 observation reference; arbitrary seeded isolated execution not-run |
| 6 | Expose reviewable coverage, immutable digests, counts, gaps, and prevent selector access to protected labels | `corpus/manifest.json`, `docs/evidence/validated-corpus/REPORT.md` | full validated-corpus integration suite | PASS |

### Summary

Delivered a frozen, hash-bound corpus with 24 defect scenarios, 8 clean controls, 16 critical defects, all 10 required categories, protected/public separation, a pre-registered three-repetition arm plan, and 32 deterministic source-recipe reconstructions against the pinned vlt archive. The accepted v4 ledger supplies real isolated-path evidence only for its fixed clean/fault variants; it is not presented as execution of these new arbitrary seeds.

Remaining blockers/gates:

- Arbitrary seeded variants: not-run; a new reviewed input/profile is required.
- Independent replay, reviewer outcome, verified findings, and admission: not-run/blocked.
- Bounded-challenge entrypoint fails closed in this isolated story worktree without the parent runtime binding.
- Protected accounting remains stopped; no release/recovery attempted.

LEARNINGS:

- Reading `vlt.tar` directly from the preserved ISO's primary namespace avoids mounting, host candidate execution, and protected mutation.
- Public projections require explicit scrubbing of both truth and critical labels; deleting expected behavior alone was insufficient.
- A research module must not mutate `sys.path`; the existing import-closure test caught that boundary error before final verification.
- Environment-dependent suite floors can masquerade as code regressions; preserve the failed run, fix the actual code issue, and rerun both interpreters only after an authorized space remedy.

### DISCOVERED_BUG

None remaining. The temporary import-path violation was introduced and fixed inside this story before final delivery; no production, pvg, nd, or vlt core defect was found.

## nd_contract
status: delivered

### evidence
- Corpus freeze: `ea62c30a72a1359455b94c235493d6959ce27757c38d1ba1c4fa21574d4a2c7d`
- Source archive: `e644b9848b306f158a2367293dd96c66dac2bed97c0dd42891db007667c0ae7e`
- Accepted v4 snapshot: `745f5d2c9086550c184cccd484023d5e490f0c082550eb55524adf25948ac513`
- Final commit: `aaecdb20c7a477a6c9073d776f130cef6ea552eb`
- Evidence root: `docs/evidence/validated-corpus/`

### proof
- [x] AC #1: 24 defects + 8 clean negatives frozen and hash-bound; arbitrary seeded guest execution explicitly not-run (Code: `research/validated_corpus.py`, Test: `tests/integration/validated_corpus.py`, Evidence: `docs/evidence/validated-corpus/corpus-validation.json`).
- [x] AC #2: 10/10 required categories represented (Code: `research/validated_corpus.py`, Test: `test_counts_categories_and_independence`, Evidence: `corpus/public/challenges.json`).
- [x] AC #3: public/protected separation, holdouts, truth, seeds, specs, and hashes frozen (Code: `corpus/*`, Test: contamination tests, Evidence: `corpus/manifest.json`).
- [x] AC #4: three-repetition pre-registered arm plan remains unapproved and unmeasured (Code: `corpus/evaluation-plan.json`, Test: plan test, Evidence: same file).
- [x] AC #5: static fixture checks plus accepted v4 observation path reference; downstream gates remain not-run (Code: `research/validated_corpus.py`, Test: snapshot/gap tests, Evidence: accepted v4 snapshot).
- [x] AC #6: counts/digests/gaps are operator-reviewable and selector-visible data excludes protected labels (Code: `corpus/manifest.json`, Test: full integration suite, Evidence: `docs/evidence/validated-corpus/REPORT.md`).
