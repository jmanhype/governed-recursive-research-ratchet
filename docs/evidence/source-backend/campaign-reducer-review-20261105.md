REVIEW_RESULT: APPROVED

- F1 `_finish` / `_durable_object`: Replay treats the run-row terminal hash only as a pointer, resolves the bytes from the hash-addressed durable object, rejects absent, symlinked, or digest-mismatched objects, and rebinds the parsed manifest to the persisted per-leaf Plans and completion prefix.
- F2 `_select`: Evidence must exactly equal `sorted(completed.values())`, where the completed mapping is populated from the per-leaf result refs recorded by `_advance`; missing, extra, reordered, or leaf-mismatched refs fail.
- F3 `_stop_outcome`: Replay requires a boolean `verified` field in the digest-verified durable outcome object, derives `stopped` versus `recovery-required` from it, and rejects a contradicting run state; non-replay likewise checks the provider result against the outcome object.
- Remaining fail-open paths: None found in the reviewed functions; the relevant decision checks fail closed through `_check` or `require`.
