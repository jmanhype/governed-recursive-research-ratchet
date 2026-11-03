# GRRR-z3w9 Stage D capture review 1 — rejected

Verdict:

```text
STAGE_D_CAPTURE_REVIEW: REJECTED
```

Findings:

1. The capture was not exclusively no-follow or fully lock-bound. Active bytes
   were hashed and then separately reopened before lock acquisition; `stat_record`
   followed symlinks; sidecars were enumerated after unlock; and final active/lock
   observations occurred after `completed_at`.
2. Policy identity was asserted rather than measured, and parent-code expected
   identity was copied from its observed hash.
3. The postcapture verifier consumed an unpinned temporary JSON file and emitted
   booleans without binding the exact retained capture hash, observation time, or
   observed active/lock/database identities.

Positive findings:

- All six inspected manifest-listed artifact hashes matched.
- The retained PRAGMA inventory matched the Stage C-approved declarations.
- Recorded database/lock chronology and identities were internally consistent.
- Validation remained fail-closed with `spendable=null`, unresolved
   writer-exclusion proof, no allowed mutations, and no execution authority.

The reviewer did not access protected paths, execute the programs, or edit files.
