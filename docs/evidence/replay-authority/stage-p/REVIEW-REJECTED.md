# GRRR-z3w9 Stage P initial review — rejected

Verdict:

```text
STAGE_P_INSTALLER_CONTRACT_REVIEW: REJECTED
```

Blocking finding:

- `schema_version` checks used equality without requiring an integer.
- Independently reproduced `True` and `1.0` passed issued-authorization shape
  validation.
- Neither value granted authority, but both violated fail-closed shape
  validation.

Reviewer independently confirmed at the initial identity:

- focused tests passed 25/25 on both interpreters;
- emitter output was byte-identical;
- all eight listed artifact hashes matched;
- Stage N/O package and predecessor bases matched;
- retained full-suite logs each reported 559 passing tests;
- all other reviewed boundary and authority properties passed;
- no protected access, installer execution, source edit, production mutation,
  merge, or push occurred.

Correction:

- require `type(schema_version) is int` in both contract validation and
  issued-authorization shape validation;
- add boolean and float regressions for both validators;
- regenerate focused/full logs and evidence identities.
