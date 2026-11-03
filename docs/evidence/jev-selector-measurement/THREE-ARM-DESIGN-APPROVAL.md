# Three-arm evaluation design approval — design only

## Independent review disposition

The broad design reviews established the plan structure but rejected two
successive drafts. The final rejected draft had already been inspected favorably
except for these blocking details:

1. a one-nibble protected-truth hash transcription error;
2. incompletely specified bootstrap RNG lifetime and sampling order.

Both were corrected. A fresh differently scoped reviewer then returned:

```text
HASH_BOOTSTRAP_NARROW_REVIEW: APPROVED
```

The reviewer independently matched all four design artifacts, hashed the live
protected truth file, compared it with the corpus manifest, and confirmed that
the focused test checks both sources. It also confirmed the exact bootstrap
procedure:

- one `random.Random(20261103)` initialized before iteration 0;
- outer iterations 0 through 9999 inclusive;
- fixed arm order deterministic-lexical, random, jev-guided;
- exactly three sequential `rng.choice(primary_values)` calls per arm per
  iteration;
- repetition input order 1, 2, 3;
- arithmetic mean statistic;
- nearest-rank percentile indices 249 and 9749.

Focused review tests passed 3/3.

## Operator decision

The operator then approved the corrected design:

> Approved

This is **design approval only**. It does not authorize execution.

## Approved exact design identity

- `corpus/evaluation-plan-v2-proposed.json`
  `97ec4b8ccc34b3fc4da4fcfbef33b49bbb3f4f1c445cfecdb752715ddf034be1`
- `research/evaluation_plan_v2.py`
  `ca31b3cf53e70d038da6ed7a835f0ad07dcc2b3de68bf9b1e18a0c825fea8809`
- `tests/unit_evaluation_plan_v2.py`
  `f2ae917ef806d8ccabf98adaf8c4634c425b812f11f3198934e7bbf69879893b`
- `docs/evidence/jev-selector-measurement/PRE-REGISTERED-PLAN.md`
  `de82208f2b4e55544dc25b43e91fe9156cee348b3fa82ba812078fc92ea3ad7b`

The JSON intentionally retains its reviewed `proposed`, `not-approved`,
`measurement_started=false`, and `execution_authorized=false` values. Those
fields describe execution state, not operator acceptance of the immutable
design bytes. Execution still requires a separate explicit authorization record
and preflight.

No selector, Jev network call, real secret use, protected `/Library/GRRR`
access, replay, contract admission, promotion, production mutation, merge, or
push is authorized by this design approval.
