# Preflight failure diagnosis (not a passing experiment)

Attempt `attempt-20261020T152048Z-d6f75d1f`, implementation
`3c93078d3e9e2c73d1196a24e5414af6b7f9864b`, executed 8 tests with 3 failures
and 1 error; none skipped. Identity permission controls passed. Existing files
are preserved unchanged. Parent exported the protected SQLite journal read-only
using `scripts/inspect-attempt`; the new `protected-diagnostic.json` is an
additional diagnostic, not a rewrite of the original manifest.

## Proven cause

Journal event 4 finished the preflight with execution `error` after
1.298718459 seconds. Object
`e82268e0401824fc601401300e955f6082938adcb3c85a888fb51c9b80a25f1d`
records `GateBlocked: Guest isolation/reset check failed`, unchanged assets and
verified process cessation. Its captured interface output contains
`ESC[1;36mloESC[m`, not plain `lo`. Alpine's interactive `ls` alias emitted
terminal colors, so the strict expected interface assertion rejected it.

The operator stop fence appears later at event 5. This was **not** a successful
direct-stop experiment accidentally reported as error: the guest had already
been terminated for a real bootstrap assertion failure. The transport-loss log
does not establish a lost stop response; the test's later method-valued `run`
request raised JSON serialization before sending its payload.

## Repair awaiting real integration proof

- Bootstrap prints exact interface names with shell parameter expansion rather
  than `ls`; strict inventory comparison still rejects colors, extra interfaces,
  missing reset evidence and host-share filesystem names.
- Executor exposes authenticated readiness only after bootstrap checks; the
  direct-stop test waits for readiness rather than sleeping ten seconds.
- Concurrent EOF/process-exit checks recheck the stop fence before classifying
  transport failure. Preflight authorization requires a stopped observation,
  verified isolation, unchanged assets and cessation; it cannot be obtained by
  stopping an already failed run.
- Validated idempotency bindings survive denied preflight requests, so a changed
  request cannot reuse their key. Authentication remains first.
- Saved test run IDs no longer overwrite `unittest.TestCase.run`.

Pure tests verify this diagnosis against the captured object hash. They do not
replace the next real service/VM integration run, and no historical failure is
relabeled as success.
