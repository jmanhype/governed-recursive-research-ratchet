# GRRR-gu87 WIP checkpoint — not delivered

Implementation SHA: `7286815d88cc752bb58f5a9e692278027a61a79e`.
Branch: `story/GRRR-gu87`; base: `b13022c55f78a4a5b14ed0198b42d9476aae9610`.
No privileged launcher, new VM profile, paid call or remote push was executed.

PROOF:

- `python3 -m unittest discover -s tests -p 'unit*.py' -v`: exit 0,
  **45 passed / 0 failed / 0 skipped**. Unit budget identity substitution is not
  OS permission evidence; SQLite concurrency/page-exhaustion is actual SQLite.
- `./scripts/test-story trusted-observation`: exit 1. Required 10, executed 1,
  skipped 0, failures 0, errors 2. Actual UID-320 prerequisite failure prevents
  nine accounting tests; proposal-only supervisor blocks the guest test.
  This is an explicit failed mandatory suite, not integration success.
- `python3 -m coverage run
  --data-file=/private/tmp/grrr-gu87-wip-7286815.coverage --source=research
  -m unittest discover -s tests -p 'unit*.py'`, then `coverage report`:
  **37% total research statement coverage**; budget 99%, observation 98%,
  evaluator 0%. Identity/VM paths are unproven, not discounted from coverage.
- `pvg verify research/budget.py research/observation.py research/common.py
  research/evaluator.py research/execution.py scripts/identity-integration
  scripts/test-story tests/unit_trusted_observation.py
  tests/integration/trusted_observation.py
  docs/TRUSTED-OBSERVATION-AUTHORIZATION.md
  docs/TRUSTED-OBSERVATION-PROFILE-PROPOSAL.json --include-tests --format=text`:
  exit 0, 7 recognized files scanned, 0 issues. This is static scanning, not proof
  of runtime behavior.
- `git diff --check`: exit 0. `git diff b13022c -- research/policy.py
  research/offline.py research/offline_execution.py research/offline-guest.sh`:
  empty. Existing resource/command profiles were not changed.
- Proposal file SHA-256:
  `1830a92ad2cbd91788051304ec8f6acaebf256b85065b2db2c07271b6906e3f6`.
  Supervisor/image hashes are **null**, so this proposal is not launchable.
- Evidence byte hashes: `SHA256SUMS` alongside this document.

### AC Verification

| AC | Implemented/tested WIP | Remaining mandatory proof | Status |
|---|---|---|---|
| 1 | Strict executor envelope and evaluator-owned exact synthetic assertion | Distinct approved supervisor, real structured guest challenge | BLOCKED |
| 2 | Strict fields, types, wire duplicates, bounds, malformed data, digest artifacts; legacy logs cannot pass trusted-observation | Real adversarial guest/service cases, artifact validator production wiring | INCOMPLETE |
| 3 | Mandatory gate explicitly not-run; separate profile staged disabled | Implement/pin/review supervisor and execute guest mutation/impersonation/race controls after approval | BLOCKED |
| 4 | Atomic vector reservations, ceilings, carry-forward and concurrent SQLite tests | Actual evaluator UID tests; offline shared-accounting integration | INCOMPLETE |
| 5 | Stored trusted meter receipts, held unknowns, additive time/review, overhead separation, typed launch epoch | Real metering/overlap/review/launch proof across service boundaries | INCOMPLETE |
| 6 | Accounting store page-exhaustion test and evaluator fail-closed paths | Actual evaluator store exhaustion, lost response and watchdog no-repeat evidence | INCOMPLETE |

LEARNINGS:

- Existing guest-root serial markers cannot establish a candidate-inaccessible
  supervisor; resource approval does not imply command-profile approval.
- POC and milestone must share one transactional accounting store. Pending
  receipts remain worst-case charges; no absence-to-zero conversion is valid.
- Explicit integer units and request binding make concurrency/ceiling tests
  deterministic without claiming that unit tests prove OS identity.
- Mandatory missing capabilities remain suite failures and blocked authority.
  No mock, skip, relabeled proposal or control receipt can manufacture success.

DISCOVERED_BUG:
  title: Trusted-observation supervisor capability and authorization missing
  context: Accepted synthetic/offline guest profiles execute as root; neither provides a candidate-inaccessible race/locking supervisor. A distinct profile requires explicit approval, implementation and parent identity execution.
  affected_files: research/execution.py, research/offline-guest.sh, docs/TRUSTED-OBSERVATION-PROFILE-PROPOSAL.json
  discovered_during: GRRR-gu87

Operator approval requested: approve development/review of the distinct profile
under the draft's exact limits, then separately approve final supervisor/input
image hashes and parent-mediated guest negative-control execution. Null hashes
cannot be approved for execution. See `docs/TRUSTED-OBSERVATION-AUTHORIZATION.md`.

AWAITING_PARENT_IDENTITY_RUN
