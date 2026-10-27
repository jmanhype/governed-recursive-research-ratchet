# Independent Stage C implementation review 1 — rejected

Verdict:

```text
STAGE_C_IMPLEMENTATION_REVIEW: REJECTED
```

The reviewer found no protected-access or operational-authority path, but
rejected these intermediate validation defects:

1. Schema semantics did not pin exact column declarations, per-index xinfo
   semantics, or application metadata values; auxiliary negative CIDs were not
   modeled.
2. The raw schema fingerprint hashed only `sqlite_master`, omitting columns,
   indexes, foreign keys, metadata, and database identity.
3. Quiescence observations could be mutually stable but unrelated to the pinned
   database; lock protocol/ACL/coverage and chronology were insufficient, and
   writer exclusion was claimed before independent approval.
4. A top-level completeness record could say `complete` while child domains
   remained unresolved; empty operation/side-store domains lacked affirmative
   absence evidence; unknown lists were not always meaningful strings.
5. Provenance unresolved groups could carry contradictory statuses,
   authenticated pending rows required meters, and identifiers were not bound to
   retained Stage A evidence.
6. Pending dispositions accepted arbitrary equal baseline hashes and lacked
   dispatch/non-dispatch and evaluator stop/halt causal evidence.

The initial 21 focused tests and both 338-test full suites passed but did not
cover these defects. The reviewer performed no edit or protected operation.
