# GRRR-z3w9 Stage I independent review request

## Exact scope

Review only the Stage I provenance-enrichment implementation, redacted session
extract, generated provenance record, validation, focused logs, and handoff. Do
not access or mutate protected accounting paths. Do not reconcile, write
spendability, replay, admit, promote, mutate production, merge, or push.

## Base state

- Stage H commit:
  `2c8fddf2a480a5eca8ac0dd577e3e7658c3c8e0f`
- Stage H package SHA-256:
  `12c4d2ff2a042588af5b9570d1eff68dd84475a87131bef83841cdca0a37d478`
- Source commit:
  `9d3df8770f82a860f128a71d76528ff922911199`
- Export commit:
  `141823fe7e19e43fd3d2bfcc0fe4be8303e42642`

## Files and identities

- `research/spendability_provenance.py`
  SHA-256 `cb899a2ced25b79caa73caecba5d76187aae89443083260f93e250709858df3c`
- `scripts/build-spendability-provenance`
  SHA-256 `f4f308de84c0202d27a5cc94bf74639b126ace67d07fb377cec3171c84e57cec`
- `tests/unit_spendability_provenance.py`
  SHA-256 `024bf54a876143de1fc67fe491b25fe7076f38fa27e090406c1dcd7d86a71ee9`
- `docs/evidence/spendability/stage-i/PROVENANCE.json`
  SHA-256 `b809e83b7da101b2a0aab4143d575d1e23f7b661608608e2a978e22aecd5b279`
- `docs/evidence/spendability/stage-i/SESSION-EXTRACT.json`
  SHA-256 `b7166485d0b92636dec39dc399d6e39b1fa0fd486962051ccb88a9b7570c480b`
- `docs/evidence/spendability/stage-i/VALIDATION.json`
  SHA-256 `bcf705998ece7e637b48caffd805c479b0f07b99d3329dd04c13170a4d1e2b03`
- `docs/evidence/spendability/stage-i/HANDOFF.md`
  SHA-256 `0beca4f75946a8c5bb563b6ef9a3602a1b63d29d23082a3b346d97799cff307e`
- `docs/evidence/spendability/stage-i/FOCUSED-HOMEBREW-3.14.log`
  SHA-256 `94631bc8ff268e0e8ac0e72948ebfb38aaae2ccd79ac37236f27e1c3c2706872`
- `docs/evidence/spendability/stage-i/FOCUSED-MINICONDA-3.12.log`
  SHA-256 `c08c7c0d8af3042d8112a4f1330047521490890bd33f327ede18e30135de76f7`

## Review questions

1. Does the generator bind the exact Stage H package/readiness bytes?
2. Does it validate the redacted session extract by hashing the full
   non-protected source archive, reproducing every selected record, type-checking
   redacted stdin records without copying them, and checking approval
   references, validation output, observed process names, launcher boundary,
   and preservation output?
3. Does it verify all 26 plan code hashes against the exact source commit?
4. Does it verify export-commit parentage and key export bytes at both the
   export commit and current worktree?
5. Does it keep exact approval artifact bytes, per-request principal bindings,
   numeric process UID mapping, per-reservation operation boundaries,
   per-reservation timing, and final classification unresolved?
6. Does it preserve all eight candidates as unclassified and non-ready?
7. Does it make zero final classifications and grant no spendability or
   operational authority?
8. Are credential-bearing session records excluded without removing the
   authorization, identity, boundary, or custody semantics?

## Required verdict

Return exactly one:

- `STAGE_I_PROVENANCE_NARROW_REWORK_REVIEW: APPROVED`
- `STAGE_I_PROVENANCE_NARROW_REWORK_REVIEW: REJECTED`

Approval covers only non-protected provenance enrichment. It does not provide
protected artifact bytes, classify records as supplied, establish spendability,
or authorize reconciliation/replay.
