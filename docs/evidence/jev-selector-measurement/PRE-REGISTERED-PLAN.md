# Pre-registered three-arm evaluation design — proposed, not approved

This document and `corpus/evaluation-plan-v2-proposed.json` define a future
confirmatory selector-quality comparison. They do **not** approve or start
measurement. The existing `corpus/evaluation-plan.json` remains unchanged with
`approval.state=not-approved` and `measurement_started=false`.

## Evidence classification

The completed Jev run `6cf35082f34a4149b67293c7b53d9740` is classified as
exploratory capability evidence. Its immutable event hash is
`44cefd57b7ac65c811e2860a2bf37dfc54c41bb0ba9bed6ef93d475dca316d98`. It cannot
be reused as one of the three confirmatory Jev repetitions.

## Arms and budget

Each arm selects exactly eight challenges per repetition:

1. **Deterministic lexical:** sort local IDs and choose the first eight.
2. **Random:** Python stdlib `random.Random(seed).shuffle` over the canonical
   manifest order D001–D024 followed by C001–C008, using seeds 42, 43, and 44.
3. **Jev-guided:** three fresh scoring runs. Each run scores all 32 public
   challenges and returns a probabilistic top eight. Ranking is descending
   `expected_defect_weight`, then descending raw score, then ascending opaque
   challenge reference. The request asks for `jev-latest`; every response must
   identify `jev-1.14.0`, or the run is plan drift rather than a substitution.

The deterministic and random arms are local. Jev is the only external arm.
Outbound Jev state is limited to deterministic opaque references and allowlisted
public categories.

## Call and token limits

- Confirmatory Jev calls: `3 × 32 = 96`
- Retries: `0`
- Already observed exploratory calls: `32`
- Cumulative call ceiling: `128`
- Observed exploratory usage: 12,548 input and 736 output tokens
- Pilot-projected confirmatory usage: 37,644 input and 2,208 output tokens
- Pilot-projected cumulative usage: 50,192 input and 2,944 output tokens
- Hard cumulative ceilings: 60,000 input and 4,000 output tokens
- Per-Jev-repetition ceilings: 18,000 input and 1,000 output tokens

USD remains unknown until an independently supplied provider receipt proves it.
Any predicted or observed ceiling breach stops the comparison as incomplete.

## Measurements

The trusted evaluator computes selection quality locally against the frozen
protected truth after runs:

- Primary: mean selected true defect labels per repetition, from 0 through 8.
- Secondary: mean selected critical defects, mean selected clean negatives, and
  unique true defects across all three repetitions.

This is selector-quality evidence only. It is not software optimization,
verified-defect proof, independent replay, contract admission, or promotion.

Uncertainty uses a fixed descriptive percentile bootstrap:

- 95% interval,
- 10,000 resamples,
- seed `20261103`,
- unit: the three arm repetitions,
- RNG: Python stdlib `random.Random`,
- procedure: initialize exactly one `random.Random(20261103)` instance before
  iteration 0; for each bootstrap iteration from 0 through 9999 inclusive, visit
  arms in order deterministic lexical, random, Jev-guided; for each arm, call
  `rng.choice(primary_values)` exactly three times,
- input ordering: repetition 1, repetition 2, repetition 3,
- statistic: each resampled vector’s arithmetic mean,
- percentile convention: nearest-rank.

With only three repetitions, the interval is descriptive small-sample
uncertainty—not calibrated evidence of general superiority.

The default outcome is to retain the deterministic lexical baseline. Jev wins
only if its mean true-defect selection exceeds both baseline means by at least
1.0 and its bootstrap lower bound exceeds the higher baseline arithmetic mean.
Otherwise the comparison is inconclusive. No causal, general, or broader
superiority claim is permitted.

## Fail-closed conditions

The comparison is incomplete if any Jev repetition is incomplete; a call,
retry, selection, or token ceiling is breached; usage does not match reports;
credential or semantic leakage occurs; event/report hashes differ; plan bytes
drift; or mandatory evidence is missing. There is no automatic rerun.

## Required gates before execution

1. Independent design review must approve the exact proposed JSON and this
   document.
2. The operator must separately approve execution and confirm the token/call
   ceilings.
3. The runner must perform three fresh Jev repetitions with no retry.
4. The trusted evaluator must generate the comparison report locally from
   frozen protected truth.

Until all four occur, this design makes no result claim.
