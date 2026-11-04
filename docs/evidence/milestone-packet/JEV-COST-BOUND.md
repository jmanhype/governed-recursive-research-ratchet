# Conservative Jev cost-bound supplement

- Story: `GRRR-6sso`
- Basis package commit: `51ebc998e7c07018740ec53e389646a5b465cc75`
Status: **approved conservative cost bound; actual settlement unresolved**

This is repository-only accounting evidence. It does not execute the capstone,
authorize a runtime journey, or transform public list-price exposure into an
account invoice, balance debit, or final settlement.

## Authorization and independent review

- At `2026-11-04T03:57:37Z`, the operator authorized use of official
  public-rate exposure as the conservative Jev cost bound and retention of the
  full **$50** incremental reservation.
- At `2026-11-04T04:03:21Z`, independent review returned
  **`COST_BOUND_REVIEW: APPROVED`**.
- The approval covers conservative public-rate preflight arithmetic only. It
  does not prove account billing, a debit, credits, tax, statement linkage, or
  final settlement, and does not authorize the capstone.

## Official rate basis

- Model: `jev-1.14.0`.
- Official public model documentation snapshot SHA-256:
  `d0f55e74b7b97adf327842bba4da0d5f57cca60d6a5d41ba4d1c92edf388e6ff`.
- Official public input rate: **$42/Btok**, equivalently **$0.042/Mtok**.
- Official public output rate: **free**.
- These are list-price exposure inputs, not account-specific settlement.

## Retained runs

| Classification | Run ID | Report path | Report SHA-256 | Calls | Input | Output |
|---|---|---|---|---:|---:|---:|
| Exploratory pilot | `6cf35082f34a4149b67293c7b53d9740` | `docs/evidence/jev-selector-measurement/run-20261103T201719Z/report.json` | `59a9a21282ae2f4b8fa213f43d0fa1d652bee07d0aad2bf6bfc45535fb436c0f` | 32 | 12,548 | 736 |
| Confirmatory repetition 1 | `9f7ea255e61d4f2aa6596967ef698adf` | `docs/evidence/jev-selector-measurement/confirmatory-repetition-1-20261103T214533Z/report.json` | `79aeba001d375b39806d9f73ff211a9573062fdb26792d9d489cf933c48dd628` | 32 | 12,548 | 736 |
| Confirmatory repetition 2 | `76aaf8542fce4465b082524432f6a1ca` | `docs/evidence/jev-selector-measurement/confirmatory-repetition-2-20261103T214623Z/report.json` | `f09f56cdddc0f183e7701eef7ec438ee0d30acc4bdc4beea1a0b3ea9ab7a2b84` | 32 | 12,548 | 736 |
| Confirmatory repetition 3 | `e3938b63cf634cdda8e0f00fe416ab31` | `docs/evidence/jev-selector-measurement/confirmatory-repetition-3-20261103T214701Z/report.json` | `0121a7caafecbe543e698e67ba729bf38726f43bdcfd7cc63d7245634c7dce1c` | 32 | 12,548 | 736 |

Cumulative observed usage: **4 runs, 128 calls, 0 retries, 50,192 input
tokens, and 2,944 output tokens**.

## Conservative arithmetic

Only input tokens are priced; output is free.

| Scope | Input tokens | Formula | Conservative exposure |
|---|---:|---|---:|
| Pilot | 12,548 | `12,548 × $42 / 1,000,000,000` | **$0.000527016** |
| Three confirmatory runs | 37,644 | `37,644 × $42 / 1,000,000,000` | **$0.001581048** |
| Cumulative | 50,192 | `50,192 × $42 / 1,000,000,000` | **$0.002108064** |

The component amounts sum exactly to the cumulative amount:
`$0.000527016 + $0.001581048 = $0.002108064`.

## Reservation and unresolved settlement

- The full **$50** incremental reservation remains retained.
- No account invoice is present.
- Actual settlement remains unresolved because account-specific amount,
  currency, billing identity, credits, discounts, tax, billing period,
  statement linkage, exact run coverage, and final debit are not established.
- This bound is far below the ceiling, but it is not a receipt and must not be
  represented as cumulative milestone spend closure.

## Authority and unchanged request bytes

- `execution_authorized`: **false**
- `capstone_authorized`: **false**
- `docs/evidence/milestone-packet/E2E-DECISION-REQUEST.json` remains unchanged
  at SHA-256
  `79b471a6e99a83dac45cfd703c92ed11e511ac3f3b08e75a93626411a0470acb`.
- `docs/evidence/milestone-packet/E2E-DECISION-REQUEST.md` remains unchanged
  at SHA-256
  `284f1cf41e0662dec4d77611f662167019d8c07609269c86ab662b67680d12f4`.

This supplement grants no secret, authenticated API, network, protected path,
VM/QEMU, replay, admission, promotion, production mutation, stash pop, merge,
push, model/inference call, or capstone authority.
