# GRRR k3j7 launch rework independent review

LAUNCH_REWORK_REVIEW: APPROVED

## Scope and integrity

- Worktree HEAD: `2b601462ba0ffb5aee6239aa22b06c26801dfaf9` (requested base `2b60146`).
- The worktree has no `docs/findings/` files to reconcile.
- Reviewed only the four prior launch corrections and their direct interaction/error-cleanup paths, not the whole backend.
- Source SHA-256 before and after review: `c94b036daebdd03fffa8d5a33c075049b8a0d235e2bef6d2c11114c3d174ebaf` (`research/capstone_launch.py`).
- Test SHA-256 before and after review: `c8682ac69944a0eeee02c6515dcc0edb5634025306c5aaaa683a3d17a2052fe0` (`tests/unit_capstone_backend_launch.py`).
- Prior rejected review SHA-256: `b33986bd70abad76a38c890d732b6ff1ef7b9f46197803beafca920cad61f12c`.
- Neither reviewed file was edited. This review creates only this report.

## Prior findings

### F1 receive-failure socket leak — RESOLVED

`LaunchBroker.launch` now wraps `receive_ticket` in a `BaseException` handler that closes the connected socket before re-raising. `receive_ticket` retains every installed SCM_RIGHTS descriptor in `owned` and closes all of them on every receive error; successful receipt transfers the sole remaining descriptor into `GateLease`.

The new regression sends a real AF_UNIX wrong-marker frame directly to `LaunchBroker.launch` and observes `right.fileno() == -1`. This is specific to broker receive failure rather than relying only on the helper process's `finally`.

### F2 cancel/close during COMMITTED — RESOLVED

Before releasing the broker lock for `commit_owned`, launch inserts both the real child and the `(lease, conn)` handoff. `cancel` and `close` remove that handoff under the broker lock, mark the session unusable and the record `unknown`, close the gate lease, and close the connection before signaling/reaping the child. A returning launch then fails `_live()` and the exact-handoff identity check, so even an exact late COMMITTED cannot revive the session or convert cleanup to success.

Both regressions use a real spawned child plus a blocked commit callback and a second thread. Source inspection confirms gate release precedes signal/wait. The runtime gate reacquiry assertion occurs after cancellation returns, so it is not itself a pre-reap linearization probe; this is a test-coverage limitation, not a material source defect.

### F3 unbounded ticket deadline — RESOLVED WITHIN SOURCE BOUNDARY

Launch computes a local monotonic deadline with `_deadline(timeout)`, which rejects zero/negative and values above 15 seconds. It takes the minimum of that local deadline and the untrusted ticket deadline, checks remaining budget before spawn and before callback, passes only that remaining local budget to `commit_owned`, and checks it again before accepting COMMITTED.

The regression sends a ticket deadline roughly 31.7 years in the future while using `timeout=2`; it observes a positive callback budget no greater than 2 seconds. Installation-specific timing-policy injection remains outside this accepted source boundary and is not qualified here.

### F4 close-pipes/IO lock race — RESOLVED

`read` and `write` resolve stream state, `fileno()`, selector registration, and raw I/O while holding `_Child.io_lock`. `_Child.close_pipes` closes all three streams under that same lock. Consequently shutdown cannot replace a fileno between resolution and use, and post-close IO consistently observes the closed stream.

The regression verifies closed stdout/stderr/stdin IO fails after broker close. It is not a repeated adversarial scheduler stress, but the shared-lock ownership makes the stale/reused-FD interleaving structurally impossible in the reviewed paths.

## Independent test evidence

Command, executed three times from the specified worktree:

`timeout 90 /opt/homebrew/bin/python3 -B /tmp/grrr-k3j7-guarded-source-suite-20261104.py unit_capstone_backend_launch`

- Run 1: `Ran 21 tests in 1.498s`, `OK`; 0 failures, 0 errors, 0 skipped, 0 protected attempts.
- Run 2: `Ran 21 tests in 1.358s`, `OK`; 0 failures, 0 errors, 0 skipped, 0 protected attempts.
- Run 3: `Ran 21 tests in 1.389s`, `OK`; 0 failures, 0 errors, 0 skipped, 0 protected attempts.

The suite used the supplied parent-interpreter guard and the actual `/opt/homebrew/bin/python3`. Its children were harmless local Python processes using AF_UNIX/socketpair/FD transfer and private SQLite under a private `/private/tmp/grrr-backend-fixture-*` directory. No mock was used for gate exclusion, real process ownership, cancel/close linearization, or callback-deadline interaction.

## Remaining issues and boundary

- No material issue remains in the four reworked correction paths or their direct error cleanup within this bounded source review.
- The runtime tests do not force every theoretically useful F2/F4 interleaving; those are coverage notes above, not findings against the corrected source.
- The guard itself states it is not an OS sandbox or VM/UID-isolation proof. This review makes no installed backend, ACL, launchd crash-teardown, production, admission, replay, accounting, promotion, or full-story acceptance claim.
- `/Library/GRRR` was not accessed, including metadata. No network, secret, install, repo mutation, tracker mutation, or Git side effect was used.
