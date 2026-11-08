REVIEW_RESULT: REJECTED

- `binding`: does not compare active binding `device`/`inode` fields to the actual store directory/database. The plan snapshot records observed metadata, but the active binding's declared identity is not enforced.
- `verify`: checks only that current `state` is `[[1, 0]]`; it does not compare current database inventory/hash with `receipt.database_sha256_after`, or check that `prior-active.json` matches the active binding. Post-install drift or tampering can therefore pass verification.
- `metadata`: accepts `uid` and `mode` arguments but ignores them. Callers do some separate checks, but this helper itself does not enforce the metadata contract its signature implies.
- `apply_install`: commits the stop-bit update before publishing receipt/completion records. An exception or interruption in subsequent inventory/record writes leaves the store released without a durable verified completion; no recovery/rollback path handles this state.
