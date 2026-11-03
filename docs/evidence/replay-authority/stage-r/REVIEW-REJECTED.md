# GRRR-z3w9 Stage R initial review — rejected

Verdict:

```text
STAGE_R_SOURCE_ISSUANCE_REVIEW: REJECTED
```

Findings:

1. Protected preflight skipped an existing leaf symlink when `exists=False`.
2. The sandbox root could be accepted as a file target when `directory=False`.
3. The initial review request contained a typo in the installer-entrypoint hash.

Reviewer independently confirmed:

- focused suites passed 14/14 on both interpreters;
- source-bundle regeneration was byte-identical;
- all other implementation, role, bundle, and log hashes matched;
- eight distinct roles and exact destinations were correct;
- package remained prepared-not-issued with no operational authority;
- no protected access or repository edit occurred.

Correction:

- validate the final component even when the expected target is absent;
- reject an existing final symlink;
- reject the sandbox root as a file target;
- add both regressions;
- regenerate source identity, bundle, logs, and review hashes.
