# Independent Stage A review 1 — rejected

Verdict:

```text
STAGE_A_REVIEW: REJECTED_BASELINE_CAPTURE
```

Positive observations:

- `CAPTURE.py` used read-only file descriptors, SQLite `mode=ro&immutable=1`,
  and query-only mode; no protected write operation was present.
- Raw inventory contained 11 reservations, 8 meters, empty overhead, state, and
  matching store identity.
- Raw reservation arithmetic reproduced `1,108,265,788` execution-us; three
  paired-null pending rows retained `900,000,000` execution-us.
- Both validation results remained `valid=false`, `spendable=null`, and all
  explicit authority flags were false.

Required corrections:

1. Remove the circular/inconsistent request-to-manifest hash binding.
2. Represent unresolved unknown upper bounds as unresolved; do not encode them
   as proven zero vectors.
3. Do not overstate schema, row-multiset, ancestry, symlink, or quiescence
   gates. Bind exact raw evidence or mark the affected gates unresolved.
4. Compare pre-open path identity, opened descriptor identity, and post-read
   descriptor identity for every protected source.

The reviewer performed no edit or protected operation and granted no authority.
