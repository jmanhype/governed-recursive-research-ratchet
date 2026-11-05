REVIEW_RESULT: APPROVED

- `prepare` — stays non-executing: it only validates and binds the request, evaluates receipt gates, and emits a `capstone-prepare-plan-v1`; `runnable` is not an execution marker and no dispatch occurs.
- `run` — rejects non-runnable or altered plans: it recomputes the plan from the supplied request, requires exact equality (covering changed bindings and tampering), rechecks every gate and `runnable`, and rejects `dispatch is None`.
- `_gates` — records all 11 gates independently; a gate reaches `pass` only when every receipt kind mapped to it is approved by the trusted verifier, and any missing or rejected evidence adds a refusal that prevents `runnable`.
- `_receipts` / `_request` — unknown receipt kinds and non-identifier receipt values fail validation; receipt hashes are bound into the request digest, and historical or otherwise unsuitable evidence cannot pass without explicit verifier approval.
- `run` — no fail-open path found within the stated trusted-verifier and trusted-dispatcher contract; this approval depends on `verify` returning a genuine boolean and the injected dispatcher authenticating and reporting execution faithfully.
