# GRRR-z3w9 Stage E independent review request

## Exact scope

Review only the version-2 fail-closed evidence-bundle assembler, its retained
input bindings, generated bundle, tests, and validation evidence. Do not access
or mutate any protected accounting path. Do not write spendability, reconcile,
replay, admit, promote, mutate production, merge, or push.

## Exact identities

- Stage D evidence commit: `d431807ce24e6c7decf57d22ffe478309da98743`
- Approved Stage D package:
  SHA-256 `c2627683bd1be9f63032d5c9f332aa3ee0c8327420afeda9a59562c5b3f4cb0e`
- Assembler module:
  `research/spendability_bundle.py`
  SHA-256 `ddecfa5b70aeb395abee479f09fd5e5cf29f01c99877fe11425db223a294c215`
- Assembler script:
  `scripts/assemble-spendability-bundle`
  SHA-256 `e13743b909433cf2106d9935d3e2fd74ef78d73e63c19d2be80ebaeefe44aae5`
- Tests:
  `tests/unit_spendability_bundle.py`
  SHA-256 `00218d596a0f2f857b272d03609599a80cbe0bad770625a759d6b9eecc19b650`
- Generated bundle:
  `docs/evidence/spendability/stage-e/BUNDLE.json`
  SHA-256 `52f08fc740feee1e48de7fb79b83ccb684324339dab386c383805ec136956467`
- Validation:
  `docs/evidence/spendability/stage-e/VALIDATION.json`
  SHA-256 `28e322cb6e651962a6eb1e76974c8d99775181a4863c0db01c01f2e0b555cb05`

## Review questions

1. Does the assembler bind exact Stage A baseline bytes, Stage D capture bytes,
   Stage D postcapture bytes, database identity, and the approved Stage D review
   without using mutable parsed input as authority?
2. Does the script verify the approved Stage D package and all 18 listed
   artifacts before assembly?
3. Does the bundle preserve all five raw Stage A table inventories, including
   11 reservations, 8 meter rows, empty overhead, state, and store identity?
4. Does it embed the mapped Stage D schema and locked quiescence record without
   turning `writer_exclusion_proven` into authority?
5. Are exactly 11 unresolved provenance sidecars and 3 unresolved pending
   dispositions generated with full 300,000,000 execution-us holds?
6. Does historical completeness retain all 8 lineage artifacts, all 11
   reservation mappings, all 5 overhead domains, explicit missing history, and
   unbounded unknowns?
7. Does exact-regeneration validation reject forged Stage A bytes, unbound
   Stage D or postcapture bytes, tampered bundles, and injected non-null
   spendability?
8. Does the bundle remain structurally valid but evidence-invalid with
   `first_failed_gate=quiescence`, `spendable=null`, no allowed mutations, and
   no execution authority?
9. Does any code path access a protected path or grant spendability,
   reconciliation, replay, admission, promotion, merge, or push authority?

## Recorded validation

- Focused bundle tests: **14/14 passed** on Python 3.9.6 and 3.14.3.
- Full no-guest suites: **377/377 passed** on both interpreters.
- `pvg verify` selected assembler/script/tests: PASS.
- `git diff --check`: PASS.

## Boundary disclosure

An initial tracker-note shell command used Markdown backticks inside a
double-quoted shell string. zsh attempted command substitution for the protected
path and returned `permission denied`. No protected file was opened, read,
modified, or exported. The note was corrected, and Stage E implementation uses
only retained repository evidence.

## Required verdict

Return exactly one:

- `STAGE_E_BUNDLE_REVIEW: APPROVED`
- `STAGE_E_BUNDLE_REVIEW: REJECTED`

Approval covers only the fail-closed bundle assembler and artifact. It is not
historical completeness, spendability, reconciliation, replay, admission,
promotion, merge, or push authority.
