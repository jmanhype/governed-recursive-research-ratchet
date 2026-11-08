# Independent replay attempt — 2026-11-08

Status: **REFUSED BY THE HARNESS — not a pass, not a new execution.**

## What was wired

`launcher.sh` (SHA256 `8d1a04bab98eb9edbb3cb93c828b1de56eaf80b8efb89e9dd5351159318cd525`)
is the parent dispatcher for the existing protected replay package:

- clears only the stale runner-owned sockets in the sticky `ipc` dir;
- starts `replay.runner('normal')` as `_grrr_runner` (UID 321);
- waits for `executor.sock`;
- runs `replay.evaluator('normal')` as `_grrr_evaluator` (UID 320);
- stops the runner and records both exit paths.

The replay package itself (`/Library/GRRR/replay-package`) was not modified.

## Attempt result

`EVALUATOR_EXIT=1`

```
common.Failure: Fixed replay findings differ
  replay.py:536 in validate_mode_results
```

The receipt object `18ca11ba…fba94` records the actual cause:

```
error.code           = Stopped
error.message        = Fixed attempt sequence exhausted
execution_complete   = false
finding              = Inconclusive
consecutive_failures = 1
```

Gate states from that receipt: `budget_state = error`, `independent_replay = error`,
`source_environment_identity = pass`, `evidence_integrity_currency = pass`,
all others `not-run`.

The harness refused before launching guests: the fixed attempt sequence for this
replay runtime was already consumed by the 2026-11-03 run. No new guest ran.

## Side effect (fail-closed)

The evaluator's failure path called `budget.halt()`. Accounting state is now
`stopped = 1`; reservation `a549efbdca5743878052c0226c617c1f` was not settled.
This was not reset, reconciled or released.

## Prior real run (for contrast)

`export-ca47bda9f47645b1910cba1449bcddfe`:

- `decision = approved-D011-independent-replay-normal`
- receipt `c29e4deb…` finding **Verified defect**
- lifecycle: `evaluator_succeeded = true`, `children_ceased = true`,
  exit codes `[-15, 0]`, 47.7 s
- manifest trusted anchor `34dc2753bc0be33753a3312b48f9530ff3e00019757254529310e053fd0e905e`

This attempt produced export `export-6bbe1fc699954aebad2926f1d8c9c773`
(trusted anchor `792454bb2d2e352f1d61435f65d523ad7d0667107b2717c342b6029ac45d5c84`,
14 events) which records the refusal, not a reproduction.

## Consequence

GRRR-6sso is not closable from this attempt: the gates did not pass, execution was
not complete, and the accounting store is now halted. Unhalting requires a
separately reviewed recovery, which was not performed.

No merge, no push, no promotion, no admission, no production mutation.
