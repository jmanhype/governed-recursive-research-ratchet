REVIEW_RESULT: REJECTED

1. **`_gates`** — Receipt-backed gates pass solely because the corresponding key exists; the `expected` argument is never inspected. A stale receipt, or a syntactically valid identifier for malformed content, therefore satisfies the gate. One receipt also drives multiple nominally separate gates (`observation` for both observation gates and `review` for both review gates), so the separate records do not represent independent verification.

2. **`_request`** — It validates identifier shape only and never authenticates receipt contents, recomputes `request_sha256` or `authorization_sha256`, checks freshness, or binds receipt hashes to the runtime, corpus, accounting, and VM assets. Historical or unrelated hashes can therefore populate `receipts` and produce a plan marked runnable.

3. **`run`** — `plan_id` is an unkeyed digest of selected plan fields. A caller can alter gates or the binding, recompute the digest, and submit a self-consistent forged plan. Extra top-level fields are excluded from the digest and then forwarded to the dispatcher. This detects accidental edits, not tampering or provenance.

4. **`run`** — Any non-`None` callable is treated as the trusted dispatcher, and its result is accepted when it is merely a `dict`. An empty or failure result yields `executed: True` and returns the pre-run `pass` gates; the dispatcher result and post-dispatch gate states are never validated. Absence is rejected, but an unauthenticated stand-in callable is not.

5. **`prepare`** — Floor values are caller-asserted, unauthenticated integers; `_floors` does not tie them to current capacity or the accounting receipt, and `run` does not recheck them. A falsified `free_bytes`/`required_bytes` pair avoids `floor-breach` and remains eligible for execution.

`prepare` itself has no dispatch, protected-access, or write path, and the 11 gate keys are structurally separate. Those properties do not cure the fail-open receipt, plan-integrity, floor, and dispatcher paths above.
