# GRRR-z3w9 Stage F independent review request

## Exact scope

Review only the Stage F external evidence request generator, generated request,
operator handoff, tests, and package. Do not access or mutate protected
accounting paths. Do not write spendability, reconcile, replay, admit, promote,
mutate production, merge, or push.

## Exact identities

- Base Stage E commit: `81e9785ccb20bea38a84aec70869b67f26d2d6cb`
- Request module:
  `research/spendability_request.py`
  SHA-256 `1860c7d8ea1ecba909b75ab98634bea1341a63f7a0064ebc51fbd8bf46253f90`
- Generator script:
  `scripts/generate-spendability-evidence-request`
  SHA-256 `7cb49ca0cebae14bc1bcfc0cedfc00a3634bcd90e9af372f9f0c28c09b0bee9c`
- Tests:
  `tests/unit_spendability_request.py`
  SHA-256 `8425d246514187bc2ccf282ffc2af7e985f4a7d4dc753926b809bc26f72e1d5f`
- Generated request:
  `docs/evidence/spendability/stage-f/REQUEST.json`
  SHA-256 `6c59851d15fa44afccc3907e0aa0bedd7eb629095898d50b51a53079183cf919`
- Operator handoff:
  `docs/evidence/spendability/stage-f/HANDOFF.md`
  SHA-256 `aa1f42efac5209df38fa761a6b42f406abfc99ad7bf87b45307ab5a16fa3c771`

## Bound Stage E inputs

- Stage E bundle SHA-256:
  `52f08fc740feee1e48de7fb79b83ccb684324339dab386c383805ec136956467`
- Stage E package SHA-256:
  `36b9bfb4ae2f3d2245c4d60624e0c06548caf528578ab2ce888dfef4b2d0cc09`
- Database SHA-256:
  `9c6ff2561a364ed982cd5477dd4b200c995da6910c9a17aa3d3c411a962d64f3`
- Required Stage E review:
  `STAGE_E_NARROW_REWORK_REVIEW: APPROVED`

## Review questions

1. Does the generator verify both the Stage D and Stage E approved packages and
   every listed artifact before producing a request?
2. Does the request bind exact approved Stage E bundle/package bytes rather than
   trusting request fields?
3. Does it enumerate exactly 30 evidence items:
   11 provenance, 3 pending, 8 lineage, 2 coverage, 5 overhead, and 1 global
   history?
4. Are reservation IDs, pending IDs, lineage artifacts, and overhead domains
   complete and non-duplicated?
5. Does every item state mandatory evidence, acceptable original-record sources,
   and explicit rejection conditions?
6. Does the response contract require raw bytes, hashes, provenance, custody,
   timestamps, and documented search boundaries while forbidding credentials,
   unrelated private data, fabricated records, and authority language?
7. Does validation reject modified Stage E inputs, tampered requests, injected
   authority, non-null spendability, and missing items?
8. Does the operator handoff accurately summarize the request without adding
   authority or unsafe instructions?
9. Does any code path access a protected accounting path or grant spendability,
   reconciliation, replay, admission, promotion, production-mutation, merge, or
   push authority?

## Recorded validation

- Focused Stage F tests: **15/15 passed** on Python 3.9.6 and 3.14.3.
- Deterministic request regeneration: byte-identical.
- `pvg verify` selected module/script/tests: PASS.
- `git diff --check`: PASS.
- Full suite was not run because stable available space was approximately
  9.69 GB, below the 15.35 GB preparation floor. This is recorded in
  `CAPACITY-PREFLIGHT.json`; no VM/corpus/replay operation was attempted.

## Required verdict

Return exactly one:

- `STAGE_F_REQUEST_REVIEW: APPROVED`
- `STAGE_F_REQUEST_REVIEW: REJECTED`

Approval covers only the evidence-request implementation and artifacts. It does
not establish historical completeness, spendability, reconciliation authority,
or replay authority.
