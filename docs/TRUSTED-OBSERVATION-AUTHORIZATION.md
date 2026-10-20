# GRRR-gu87: staged boundary, not an approved execution profile

The companion JSON is a **proposal only**. No dispatcher recognizes it, no
supervisor/image artifact is represented as built, and null artifact hashes
block approval and execution. The synthetic 512 MiB and offline
1024 MiB / 512 MiB workspace profile definitions remain byte-for-byte unchanged.
QEMU's proposal hash was measured locally without executing a new command profile.

## Operator approval requested

Approve development/review of the distinct `trusted-observation-v1` guest
supervisor under the exact proposed resource and identity limits. Once its
supervisor source and detached input image have final hashes, separately approve
those hashes and parent-mediated identity execution of the enumerated guest
negative controls. Approval of this draft does **not** authorize running a
not-yet-built image, expanding limits, treating UID 0 candidate logs as trusted,
or enabling paid dispatch. A parent identity run alone is not profile approval.

The supervisor will remain guest root, candidate UID/GID 1000 with no
supplementary groups/capabilities. Root-only files/control are inaccessible to
candidate. Candidate descriptors must exclude serial/TTY/control handles.
Supervisor alone runs the pinned schedule, owns locks, captures bounded child
stdout, and emits versioned results to executor. Candidate stdout cannot contain
authoritative frames. No host process runs candidate code or a supplied harness.
Mutation, read, replacement, signal and impersonation attempts must be observed
inside a real guest; permissions written in this proposal are not evidence.

## Current WIP boundaries

- `budget.py` adds evaluator-only transactional POC/milestone accounting, integer
  USD/time vectors, POC carry-forward, request-bound duplicates, conservative
  pending holds, stored meter receipts, additive replay/review, and separately
  disclosed overhead. A reservation explicitly is not a dispatch lease.
- Legacy synthetic evaluator uses this accounting and validates executor data.
  Only host-measured elapsed time after an authenticated complete executor
  response may settle it; absent/invalid receipts retain maxima.
- Legacy synthetic root-guest serial output can still establish only the
  pre-existing exact `CLEAN` synthetic assertion. Trusted-observation is now
  explicitly `not-run`, or `fail` for incomplete observations. Verified/admitted
  states remain blocked.
- The offline accepted build path is unchanged and is **not yet migrated** to
  the shared accounting service. Its previous bounded build proof is not
  GRRR-gu87 end-to-end proof.
- Structured invalid metadata/raw data tests and SQLite concurrency/page-cap
  tests are supplementary. Unit identity substitution is explicitly not
  permission proof. The integration entrypoint fails on missing actual UID or
  missing approved supervisor capability; it cannot substitute unit green.

## Remaining mandatory proof

AC1–3 require approved supervisor implementation, protected expectations, real
guest isolation and hostile-output/locking controls. AC4–5 still require actual
UID-320 store tests plus shared accounting integration with offline/review
sessions. AC6 still requires actual evaluator-service store exhaustion, lost
executor response, watchdog and no-repeat dispatch evidence. The current
SQLite page-cap test alone does not establish those service-level cases.

No delivery, acceptance, corpus result or production readiness is claimed.
