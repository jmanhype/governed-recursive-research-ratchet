# GRRR-n49g: review-approved read-only status source WIP

## Result and boundary

The zero-gate approval recommendation and fabricated zero-cost display are
repaired in the seven-file source inventory in `source.sha256`. The CLI now
offers `--view status` using the same projection as the existing review view,
in text, Markdown and JSON. This is **uncommitted source WIP**, not delivery,
PM acceptance, installation, or an end-to-end GRRR completion claim.

Base and unchanged HEAD: `5f6ce4e83e2426e859127af568aa730c19dc6a9b`.
Branch: `story/GRRR-n49g`. The accepted epic and preserved GRRR-734u source
checkpoint are not modified by this slice.

## Observable behavior

- All eleven common replay gates remain required and individually visible;
  missing, malformed, failed or unexecuted gates block inspection eligibility.
  Extra gates do not substitute for required gates. A nine-gate admission
  subset is separately labeled and grants no approval.
- The actual historical archive displays **9/11 pass**, reviewer outcome and
  action-specific human approval `not-run`, review eligibility `false`,
  **Cost: Unknown**, and recommendation **Needs more evidence**.
- Unknown, invalid, boolean, negative, non-finite or conflicting costs become
  JSON `null` / human `Unknown`. Explicit valid zero remains a reported,
  unverified observation, never settled or spendable accounting.
- Duplicate JSON keys are rejected at every depth. Distinct exact integer
  costs do not collapse through float conversion. Lossy/underflowing decimal
  JSON tokens are refused. Nonzero sub-cent observations do not render as zero.
- The pure detached schema-2 projection separates execution, finding/gates,
  source review, human decision, action authorization, installation, budget,
  stop/cessation, admission and promotion. Every action authority remains false.
- All formats label the archive historical, with current verification absent.
  Text needs no color or raw JSON. The existing fixed CLI evidence input is
  retained; no arbitrary-path reader or new mutation command was added.

Examples: `status-example.text`, `status-example.markdown`, `status-example.json`.
Public API/compatibility: `../../READ-ONLY-STATUS-VIEW.md`.

## Parent verification: fresh durable logs

Each required backend suite returned exit 0, with zero failures, errors and
skips. The suite retains every original required module and its zero-test and
skip-refusal guards, adding only the two report/status modules.

| Python | Tests | Retained log |
| --- | ---: | --- |
| 3.14.3 | 348 | `verified-python314.log` |
| 3.12.9 | 348 | `verified-python312.log` |
| 3.9.6 | 348 | `verified-python39.log` |

For each interpreter, the executed command was:

```sh
/usr/bin/sandbox-exec -p '(version 1)(allow default)(deny file-read* file-write* (subpath "/Library/GRRR"))' PYTHON -B tests/unit_capstone_backend_suite.py
```

These are source-only suites, not protected evaluation or replay. Each log
explicitly reports installed topology, live campaign execution and capstone
**NOT-QUALIFIED**. Fresh logs were written directly into this retained evidence
directory because earlier temporary R2 parent logs were unavailable after
context recovery; their historical hashes are not substituted for fresh proof.

The retained `parent-regression-probe.py` separately passed 15 synthetic
presentation checks (`parent-regression.json`) under the same OS denial.
Real temporary archive/CLI journeys, duplicate and numeric regressions,
detachment and negative syscall-purity guards are included in the source suites.
No successful filesystem behavior is mocked by those real fixture journeys.

`authority-source.sha256` is derived from the unchanged HEAD's admission,
common gate inventory, accounting-v5, ledger and two installation-authority
modules. `authority-parity.log` records all six exact byte matches. The seven
functional hashes matched before and after verification. `git diff --check`
passed. This is bounded source parity, not inspection of protected runtime state.

## Independent review

R1 rejected two reproduced cost bugs despite green tests: duplicate null/zero
JSON fields silently last-won, and distinct exact integers collapsed by float
coercion. `r1-review.md`, its original source manifest and original parent logs
remain retained; they are not evidence for the corrected final bytes.

Fresh R2 result: **REVIEW_RESULT: APPROVED**, in `r2-review.md`, SHA-256:
`ec4fabd6c2785e8e3de19a5a86163b9fa9ba0a24f5e5cfabeceb1c5c0448af6c`.
The independent security reviewer verified all seven final source hashes,
confirmed both findings closed and measured 41 focused tests with zero failures,
errors or skips under protected-path OS denial. That reviewer did not claim the
parent's full-suite counts as their own. No reviewed functional bytes were
changed after R2 approval. This is source review, not PM or runtime acceptance.

## Governance and handoff

No protected-path access or probe, credentials, research-provider calls,
provisioning, protected install, accounting mutation, reconciliation, actual
replay, admission, promotion, production mutation, merge or push was performed.
No source staging or commit was authorized or performed. Standard delegated
coding/review model use is separate from research-provider execution.

GRRR-n49g remains `in_progress`; no developer self-acceptance, delivery or PM
acceptance is claimed. A future authorized source commit and independent PM
disposition are separate from every runtime gate. The project uses its live
Paivot nd vault; `bd sync --from-main` refused because no Beads database exists.
No second tracker was initialized.
