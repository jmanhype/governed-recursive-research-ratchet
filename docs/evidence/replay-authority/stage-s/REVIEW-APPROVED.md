# Stage S authorization-preparation review — approved after rework

## Initial review

```text
STAGE_S_AUTHORIZATION_REVIEW: REJECTED
```

Six validator bypasses were found:

1. `authority = {}` accepted (all required false flags removable).
2. Missing `authorization_hash` field accepted.
3. Extra predecessor-binding field accepted.
4. Missing or incorrect `basis.base_commit` accepted.
5. Extra staging-plan field with recomputed digest accepted.
6. `prepared_at = None` accepted.

## Correction

The validator now enforces exact nested key sets for `basis`, staging
items, `predecessor_binding`, `operator_authorization_requirement`, and
`authority`; validates `base_commit` and `prepared_at` exactly; and adds 13
regression tests covering every reviewer mutation probe.

## Narrow rework review

```text
STAGE_S_NARROW_REWORK_REVIEW: APPROVED
```

The reviewer independently verified:

- All six bypass categories reject.
- 13 regression tests cover every probe.
- 42/42 focused tests pass on both Python interpreters.
- Deterministic emission is byte-identical; record SHA-256:
  `1d27da0d718ac7713f54bc73d4b87d5bcd1ea57f3eb55de1e74b0e2c933a75c9`
- Package SHA-256:
  `4f81a932e0dc1ce58495d925a6c0a574653d897f6bea6c88b8ada1f3ce344ceb`
- 10/10 package members match sizes and hashes.
- Protected paths remain data strings; emission reads only repository files.
- No `/Library/GRRR` access or mutation.

## Boundary

This approval covers only the corrected repository-retained Stage S
authorization preparation record. It does not approve protected staging,
installation, budget amendment, reconciliation, replay execution, admission,
promotion, merge, or push.
