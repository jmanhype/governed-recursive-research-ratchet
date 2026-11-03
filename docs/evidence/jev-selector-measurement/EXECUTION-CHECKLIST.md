# Three-arm execution checklist — prepare only

This checklist does **not** authorize execution. The approved design remains an
immutable proposal until the operator separately authorizes the confirmatory
runs.

## Required immutable identities

- Design commit: `9e107609db76022ed6d8e138cbbece2e41d634ee`
- Proposed plan SHA-256:
  `97ec4b8ccc34b3fc4da4fcfbef33b49bbb3f4f1c445cfecdb752715ddf034be1`
- Design approval record SHA-256:
  `926e1c04b49f0cb1dbfac9c5eb2775daa3182bda77939413b36297061146a8e6`
- Narrow review:
  `HASH_BOOTSTRAP_NARROW_REVIEW: APPROVED`
- Protected truth SHA-256:
  `7cf9f99f5836c4e3e147df2866d54480a706f2665a732fbf61bd1a0d0b4c52ea`

## Excluded pilot

Run `6cf35082f34a4149b67293c7b53d9740` is evidence that the external boundary
works. It is not one of the three confirmatory repetitions.

- Events SHA-256:
  `44cefd57b7ac65c811e2860a2bf37dfc54c41bb0ba9bed6ef93d475dca316d98`
- Report SHA-256:
  `59a9a21282ae2f4b8fa213f43d0fa1d652bee07d0aad2bf6bfc45535fb436c0f`
- Calls: 32 attempted / 32 returned / 0 retries
- Usage: 12,548 input / 736 output tokens

## Future execution request

Any future execution must separately authorize:

- exactly three fresh Jev repetitions;
- 32 calls per repetition, 96 total confirmatory calls;
- zero retries;
- at most 128 cumulative calls including the pilot;
- per-repetition token ceilings of 18,000 input / 1,000 output;
- cumulative token ceilings of 60,000 input / 4,000 output;
- deterministic lexical and random baselines with no external calls;
- local trusted-evaluator scoring against frozen protected truth;
- fail-closed handling of every condition in the approved plan;
- no automatic rerun.

## Prepare-only command

```text
./scripts/prepare-jev-three-arm-execution \
  --prepare-only \
  --output /operator/owned/new-authorization-request.json
```

The command validates immutable inputs and writes a sanitized request. It does
not probe or read the credential, call Jev, execute selectors, access protected
paths, or authorize execution.

The output path must be absolute and must traverse only real, non-symlinked
existing directories. Lexical `..`, double-leading slash, protected
`/Library/GRRR` paths, existing outputs, and symlinked ancestors are refused.
