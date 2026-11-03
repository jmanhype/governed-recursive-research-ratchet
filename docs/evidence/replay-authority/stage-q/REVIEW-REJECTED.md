# GRRR-z3w9 Stage Q initial review — rejected

Verdict:

```text
STAGE_Q_INSTALLER_CORE_REVIEW: REJECTED
```

Blocking findings:

1. A late postflight failure retained success-looking `receipt.json` and
   `active.json` plus `uncertain.json`; the real verifier then accepted the
   uncertain store.
2. Postflight did not enumerate exact SQLite objects/schema, so an extra table
   could be installed and later accepted.
3. Sandbox containment did not reject protected paths or symlinked ancestors
   before filesystem access.

Reviewer independently reproduced all three blockers in temporary sandboxes and
confirmed:

- all 14 requested file hashes matched;
- installer focused tests passed 30/30 on both interpreters;
- provenance/per-record/request-search suites passed 13/13, 14/14, and 15/15;
- retained Stage L projection matched the prior publication;
- no protected access, repository edit, merge, or push occurred.

Correction:

- explicit sandbox root with lexical protected-path rejection;
- real-ancestor/no-symlink enforcement;
- exact SQLite object inventory and table DDL verification;
- uncertainty-dominant verification;
- publication-step failure regressions.
