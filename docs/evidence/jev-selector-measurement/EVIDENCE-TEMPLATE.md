# TypeSafe Jev selector measurement evidence template

**This template and the repository implementation/tests do not start a
measurement.** They do not read or use a real credential, call the network,
access protected state, replay, admit, promote, mutate production, merge, or
push. A real run requires separate operator action.

## Required authorization record

Create an operator-owned authorization JSON file with exactly these fields and
values (only the approval quote/time are operator-supplied). Any missing,
extra, duplicate, or wrong field must refuse before adapter availability is
probed. `schema_version`, `max_calls`, and `selected_budget` must be JSON
integers exactly equal to `1`, `32`, and `8`; floating-point numbers and JSON
booleans are unauthorized:

```json
{
  "schema_version": 1,
  "authorized_by": "operator-speed",
  "action": "typesafe-jev-selector-measurement",
  "corpus_freeze_digest": "dfa75ef2bf3d43fd4f750094fe643afe4f204812c0ae2426276bedb471fa8529",
  "max_calls": 32,
  "selected_budget": 8,
  "retries_allowed": false,
  "measured_usage": "token-only",
  "credential_echo_fail_closed": true,
  "approval_quote": "<operator approval quote>",
  "approval_time": "<UTC approval time ending in Z>"
}
```

Do not place a credential, endpoint credential, protected truth, or raw
conversation in this file.

## Future operator invocation

```text
GRRR_JEV_REAL_SELECTOR_MEASUREMENT=1 \
  ./scripts/run-jev-selector-measurement \
  --authorization /operator/owned/selector-authorization.json \
  --output-dir /operator/owned/new-measurement-output
```

The output directory must not already exist. Supply a path whose existing
ancestors are real directories: lexical `..` traversal, every path under
`/Library/GRRR`, double- and triple-leading-slash authorization/output paths
such as `//Library/GRRR/...` and `///Library/GRRR/...`, symlinked
authorization/output ancestors, and symlinked
leaves are refused before an adapter probe. Evidence files are opened
exclusively relative to the held safe directory descriptor. Default invocation,
malformed authorization, or unsafe output refuses before availability probing
or network use. A real invocation uses the adapter HTTP boundary by default
while retaining sanitized before/after event records.

## Evidence to retain after an authorized run

- Unedited command line, environment presence (not value), exit code, UTC
  start/end, and operator authorization SHA-256.
- `events.jsonl` SHA-256. Events must retain fixed-shape sanitized before/after
  records for every attempted call; they must not contain credentials,
  Authorization headers, endpoint credentials, raw responses, full requests,
  protected truth, conversations, or semantic local challenge IDs/labels.
- `report.json` SHA-256. A complete report has at most 32 calls, zero retries,
  exactly summed input/output token usage, and a selector recommendation only.
  Monetary USD remains `null` unless an independently supplied provider receipt
  proves it.
- Any adapter failure is incomplete/unknown: preserve partial JSONL, emit no
  selector result, and require operator review. Do **not** automatically rerun.
- If final report writing fails after any attempted call, retain the partial
  event log, treat the adapter outcome as unknown/incomplete, and require
  operator review; never describe that run as having made no adapter call.
- The safe local challenge mapping appears only in the final report context.

## Explicit result boundary

Implementation, unit tests, and injected-transport tests are not measurement
proof and cannot complete the three-arm comparison. A complete report is only
a probabilistic selector recommendation, not a defect verdict, replay result,
admission, promotion, or production change.
