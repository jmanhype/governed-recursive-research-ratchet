# Read-only replay status view

## API and compatibility

`research/status_view.py` exposes one pure function:

```python
project_status(data: dict) -> dict
```

The result is schema version 2, is newly allocated/detached, and performs no
filesystem, network, clock, random, provider, registry, accounting, admission,
promotion, or other mutation. `research/review_report.py` retains its public
loader/render signatures and exports; `build_report(dict) -> dict` now returns
this same projection, while `to_plain_text`, `to_markdown`, and `to_json`
render only version-2 reports. The status-oriented renderers are
`to_status_plain_text`, `to_status_markdown`, and `to_status_json`.
Archived JSON loading rejects duplicate keys at any depth, non-finite constants,
numeric underflow and decimal tokens that lose precision on conversion. Ambiguous
archives produce an explicit nonzero CLI refusal, not a fabricated report.

The CLI remains read-only:

```text
scripts/grrr-review [--view review|status] [--format text|markdown|json]
```

The CLI reads the existing fixed archived replay export. It is historical
input, not proof of current state. No new arbitrary-path CLI reader is added.
Both review and status views call the identical projection before rendering.

## Evidence scope and gate semantics

This projection retains all eleven `research/common.py:GATES` present in the
archived replay receipt, including reviewer outcome and action-specific human
approval. It separately labels the nine-gate admission subset from
`research/admission.py:GATE_INVENTORY`; it does not call or alter authority code.
The real archived receipt is nine passed and two not-run, NOT a fully passed
nine-of-nine profile. Every required gate is enumerated. A missing record is
`not-run`; failure, error, unknown, and
malformed records remain blocking. Extra gates are named but cannot replace a
missing required gate or change the required count.

`evidence_review_eligible` is true only when all of the following are exact:

- `verified` is boolean `True`;
- `finding` is `Verified defect`;
- each of the eleven required records has status `pass`.

That eligibility means only that a person may inspect the named historical
evidence. It is not approval, admission, readiness, promotion, production
authority, or settled accounting. Missing or ambiguous evidence produces
`Needs more evidence`; it does not automatically reject or approve.
Source-code review is a distinct axis and remains not established here.

## Status, cost, identity, and authority limits

The report separates execution, verification/gates, source review, human
decision, action authorization, installation, budget/cost/spendability,
cessation, admission, and promotion. Unsupported values remain `Unknown`,
`Not established`, or `Disabled`. Missing lifecycle is `Unknown`, never
`Failed`. Arbitrary authority, ready, promotion, admission, or approval fields
in input are not trusted.

Missing, invalid, boolean, negative, non-finite, or ambiguous costs are JSON
`null` and human `Unknown`; they are never displayed as a zero amount.
Explicit finite nonnegative numeric zero/nonzero values can be shown as
reported observations only, with unverified scope and no spendability or
settled-accounting claim. Elapsed time is likewise shown only when explicitly
reported. Supported integer/float observations retain their native values for
comparison and JSON output; distinct exact integers cannot collapse via float
coercion. Single large integer costs render exactly, and sub-cent observations
are not displayed as zero. Out-of-representation inputs remain Unknown.
No snapshot digest is fabricated: the projection records that
artifact identity, provenance, and currency are not established unless
independently verified elsewhere. A future digest must declare the exact byte
or data basis; loading a file alone does not establish provenance or currency.

Every projected action authority is false. `read_only` is true, `scope.live`
is false, and `scope.current_verification` is false. Stable `reason_codes`,
`next_action`, and `next_owner` explain the fail-closed state. No text,
Markdown, JSON, or CLI output from this module authorizes an action.
