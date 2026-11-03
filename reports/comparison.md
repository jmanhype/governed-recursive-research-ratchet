# Equal-Budget Selector Comparison

Corpus freeze digest: `dfa75ef2bf3d43fd4f750094fe643afe4f204812c0ae2426276bedb471fa8529`

Budget per arm: 8 challenges

## Results

| Arm | Available | Selected | Provenance |
|---|---|---|---|
| Deterministic | Yes | 8 | lexical-order-under-budget |
| Random | Yes | 8 | seeded-shuffle-under-budget |
| Jev | **No** | 0 | unavailable |

## Outcome

**incomplete-jev-unavailable** — Jev-guided arm is unavailable because no operator-provisioned adapter exists.

The three-arm comparative POC is incomplete per AC #4. No heuristic has been relabeled as Jev.

Deterministic and random baselines are established and reproducible.
