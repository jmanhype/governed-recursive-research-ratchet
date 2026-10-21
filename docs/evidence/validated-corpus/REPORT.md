# GRRR-bnkf frozen vlt defect corpus

## Frozen identities

- Corpus: `GRRR-validated-corpus-v1`
- Freeze digest: `ea62c30a72a1359455b94c235493d6959ce27757c38d1ba1c4fa21574d4a2c7d`
- vlt commit: `129e0b3f15a3bd6af949ee47d76f6855c582ab73`
- Apache-2.0 license blob: `c004659349c7a1f6c55e5107b53a0766085e8d2e`
- v4 source archive: `e644b9848b306f158a2367293dd96c66dac2bed97c0dd42891db007667c0ae7e`
- v4 input image: `57c48a6845d65b6b3674c80367af42c062cf079d7bbdc4491331a4945375d2b6`
- Accepted v4 observation snapshot: `745f5d2c9086550c184cccd484023d5e490f0c082550eb55524adf25948ac513`
- Accepted v4 ledger receipt: `64869aa6d0c4d550dfaa794a71f14266ba0b7ef21a1b902efb44f38f391fd672`

## Coverage

| Population | Count |
|---|---:|
| Independent seeded defects | 24 |
| Clean negative controls | 8 |
| Total frozen variants | 32 |
| Critical defect seeds | 16 |
| Required categories | 10 |

The protected seeds bind every defect to one exact unique replacement in the pinned source. The validator reconstructs all 32 variants in memory and requires unique digests. Public challenge metadata and the public spec projection contain no anchors, truth, critical labels, expected behavior, or holdout membership.
The root manifest and full spec map are protected operator-review records; the selector-visible projection is limited to `corpus/public/`.

## Preliminary validation scope

The accepted v4 run remains the only guest/isolation evidence reused here. Its internally verified ledger records 2 clean passes and 6 fixed fault failures (8 completed baseline decisions). This proves that the accepted observation path was live for the pinned input; it does **not** execute GRRR-bnkf's arbitrary seeded variants.

Static source-recipe validation passed against the protected v4 archive:

```text
24 defect scenarios
 8 clean controls
32 unique variant digests
10 required categories
```

No host or guest candidate was built or executed, no vlt CLI was invoked, and no protected store was changed.

## Explicit blockers

1. `seeded_variant_execution: not-run` — arbitrary corpus variants require a new reviewed input/profile; the fixed v4 image cannot be weakened or replaced silently.
2. Full no-guest suite reached an environment floor error, not a code assertion: 13,499,834,368 bytes are free versus the 15,350,000,000-byte ConservativeGenesis floor. The first evidence run also caught a temporary import-path violation in this story; it was fixed before the final run.
3. `bounded-challenge` fails closed in this isolated story worktree because no parent runtime binding is present.
4. Protected accounting remains stopped and evaluator-private; no release or recovery was attempted.

Downstream independent replay, reviewer outcome, finding verification, and contract admission remain not-run/blocked. Preliminary fixture observations are not credited as selector discoveries or final-system detections.
