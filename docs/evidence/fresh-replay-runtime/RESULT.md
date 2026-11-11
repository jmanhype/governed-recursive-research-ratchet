# GRRR-734u reviewed source-WIP checkpoint

Date: 2026-11-09. Base: `5f6ce4e83e2426e859127af568aa730c19dc6a9b`.
Branch: `story/GRRR-734u`. This is source approval, not PM acceptance or runtime qualification.

## Scope and authorization

The operator authorized independent review, fixing findings, then a local commit
of approved source WIP. No provisioning, reconciliation, replay, promotion,
admission, production mutation, merge or push. The initial story's no-commit
restriction is superseded only for this reviewed local source checkpoint.

The four functional files are the proposal/preflight module, its focused tests,
required backend suite registration, and source-only WIP documentation. The three
new functional files total 539 lines; registration is +2/-1. Review reports and
raw verification logs are separate retained evidence, not extra runtime modules.

## Independent review and rework

- R1: `REVIEW_RESULT: REJECTED`, `r1-review.md`, SHA256
  `575a0889134228046d091c4d654cefa9c28cad710a119155a719bf19c226ced5`.
- F1: external digest string subclasses could override equality and bypass
  expected-request/fixture-content binding. Reproduced with synthetic inputs
  and changed real temporary fixture bytes; no live authority escalation claimed.
- Fix: exact external expected-hash type; recursive exact-JSON validation of
  the whole evidence mapping before comparisons/I/O; frozen Proposal field
  type checks. No change to prepared-not-issued authority or path semantics.
- A GLM worker produced the bounded patch but was interrupted at its timebox.
  Parent integration caught a test setup KeyError, repaired that fixture and
  separated expected-hash from evidence attacks. No failed intermediate test
  was represented as proof of secure rejection. CoS dispatch was unavailable.
- R2: fresh independent security context, `REVIEW_RESULT: APPROVED`,
  `r2-review.md`, SHA256
  `d73e795e4753f02a47ecad4bdd2faf3135544e14baa9984a5031d33e58ced868`.
  Reviewer measured 15 focused tests plus 14 isolated boundary checks. Parent
  read the report, verified all hashes, reran the retained 14-check probe, and
  measured all required cross-version backend suites below.

## Exact independently approved functional bytes

| File | SHA256 |
|---|---|
| research/fresh_replay_runtime.py | 06607ef64574329ba0e989a9d4fbcfeef859b6a5458035a22127b78618874958 |
| tests/unit_capstone_fresh_replay_runtime.py | 47cd16ca28286444cd7fd1abba1187e99420d48ae2fffbc5df496522ec21a48f |
| tests/unit_capstone_backend_suite.py | 07e3d0521cdd631c9111da63a054fac579cb90f05da3e6f24c6af6d07bb1f6f4 |
| docs/FRESH-REPLAY-RUNTIME-WIP.md | e48e38d3d01d11b0eb62d0df1815313fc87b4ab6cba23f496a2d8cbb65dd28ee |

## Parent-measured verification

Working directory: `.claude/worktrees/dev-GRRR-734u`. Per interpreter:

```sh
/usr/bin/sandbox-exec -p '(version 1)(allow default)(deny file-read* file-write* (subpath "/Library/GRRR"))' <python> -B tests/unit_capstone_backend_suite.py
```

| Interpreter | Baseline | Final | failures/errors/skips |
|---|---:|---:|---|
| /opt/homebrew/bin/python3.14 (3.14.3) | 319 | 322 | 0/0/0 |
| /opt/homebrew/bin/python3.12 (3.12.9) | 319 | 322 | 0/0/0 |
| /usr/bin/python3 (3.9.6) | 319 | 322 | 0/0/0 |

All final suites exited zero and explicitly print `SOURCE_ONLY BACKEND_WIP`
and installed/live-capstone `NOT-QUALIFIED`. Fifteen focused tests passed on
3.14.3, including real files/SQLite preservation and syscall-negative guards.
Parent retained-probe replay: 14 checks passed; accounting bytes/inode unchanged
(`r2-parent-probe.log`). No protected path was probed even under the denial policy.

| Retained log | SHA256 |
|---|---|
| baseline-python314.log | 2f9d13e866ed7fb0468957b487e59d6e27a44922b0c5b932c5500f1f6183ec76 |
| baseline-python312.log | d8c54ded661ccb5958f0efc8e574949cf8f41c7cfc87005c45a56cbb5185aa13 |
| baseline-python39.log | 1dd80b1ef8faaf5942b15d9f63c2606ae03278c6b8ef663a93d155e987ff7c9e |
| final-python314.log | f63ed4cdf4c4852e757bbe8d9f89b1f4ddfe2442fb7a82f74ccee49b33112c95 |
| final-python312.log | 5198280ddb98efad7fe8b948260f0dbefcc0cd7c8152ef13cf94c8ab5cb2e27a |
| final-python39.log | ce3770a4e1a8fe7e0696f0ec5503b18f2bce204a150faa6afd7a4cd10fad5c59 |
| r2-parent-probe.log | 7830f2e648d76dcd7fa80126e4445077170e7a65b8a22013aa8a97a6a113b85a |

## R3 static-repair verification

`pvg verify` flagged three bare `pass` statements in the otherwise approved R2
bytes. The only functional delta replaces the expected-`FileNotFoundError`
`pass` with an explicit `target_absent` flag and gives the two exact-type marker
subclasses docstrings. Independent bounded security review R3 approved those
exact bytes: `r3-static-repair-review.md`, SHA256
`7e64a340bf18e9baa3df99f6b9b6c629e821de73f5a23df50eb17e7c62954bd0`.

Changed source hashes:

| File | SHA256 |
|---|---|
| research/fresh_replay_runtime.py | 4f0db5fb8b5deba7ffc21dff1f7dab864911e847754dbae5e5de85d1d52a42cf |
| tests/unit_capstone_fresh_replay_runtime.py | 8eea717b399c34bfd486a6b15b45545edb9fc3e3ddf6f76ce0e85071367e5f40 |

The same three-interpreter denial-profile command produced 322 tests on each
of Python 3.14.3, 3.12.9, and 3.9.6 with zero failures, errors, or skips. The
fifteen focused tests also passed on each interpreter. `pvg verify` now reports
zero issues. Raw retained logs and the R3 report are bound by
`static-repair-artifacts.sha256`. This remains source-only verification and
does not qualify installed topology or a live capstone.

## Remaining boundaries

Hash bindings are not authentication or live currency. Namespace absence and
inventory remain archival claims. Fixture preflight assumes caller-owned
quiescent temporary directories, not hostile concurrent renames. It neither
interprets SQLite authority nor opens the protected store. All five action
authorizations remain false and all eleven live gates remain not-run.

No protected installation, VM, replay, accounting change, spendability assertion,
production change, merge or push occurred. PM acceptance and canonical delivery
are not asserted. Separate app-wide state-machine audit output is outside this
commit and grants no runtime authority. No new dependency or state-machine
framework was installed. Beads sync found no database; the existing shared nd
vault remains the sole live tracker, with no second tracker initialized.
