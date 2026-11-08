# GRRR-hbc6 r9 recovery result

## Observed outcome

- F1 fixed with `table_xinfo` plus a qualified, zero-row SQLite rowid probe.
- Source fix commit: `09ef310`; independent-review evidence commit: `302d083`.
- Independent GLM reviewer: `REVIEW_RESULT: APPROVED`.
- Verdict SHA256: `fc4cd5f9df2ada6cfe2784e940759ee0dae066b96e30c258a57feec873c60457`.
- Required backend source suite: **307 tests, zero failures/errors/skips** on Python 3.14.3, 3.12.9, and 3.9.6. Supplemental discovery: 300 tests on each interpreter. These are source-only results, not capstone results.
- Supplemental fresh-fixture already-unhalted refusal: **1 test passed**, exit
  status 0; parent independently reran it successfully. The fixture never
  accesses protected storage and cannot leave a durable completion marker.
- Executed the exact reviewed root invocation after approval, using `/usr/bin/python3 -I -S -B`.
- Live installer returned **`published-durable`**.
- A separate, fresh interpreter process ran standalone `--verify` and returned **`published-durable`**.
- Wrong flags and wrong interpreter invocations refused at driver guards, before driver protected-path access.

## Exact authorized effect

The accounting `state.stopped` bit changed from **1 to 0**. This was the reviewed
`release-v4-stop-retain-unknowns` action. It is not reconciliation and does not
establish spendability or authorize campaign execution.

Both installer and fresh-process verification rechecked the full inventory and
metadata. Active binding bytes, database device/inode, schema, all historical
rows, holds, and unknowns were preserved. Only the stop cell and SQLite bytes
necessary for that transaction differ. Stable SQLite header fields match.

- Active SHA256: `ed40ee14278426d7af0b11a7b3a1e3ce4719f0cbad2bf7e566fd73224a6cd283`.
- Database before: `5cade36d1c437635d5881448961753b2b5306c595a893caba70b5fd8e0bac1d3`.
- Database after: `1d50a85279ff8e04e81fb7cf3f5c829812aac2cb8e73e41a864cdc70cb09fac7`.
- `historical_unknowns`: `unresolved`; `spendable`: `unknown`.

## Retained protected records

Root-owned directory `/Library/GRRR/accounting-poc2/recovery-v4` has mode `0555`;
its four records are root-owned `0444`. Copies here have matching SHA256:

| Record | SHA256 |
| --- | --- |
| `complete.json` | `ea5dae2b353a1e7c0747f92b5bdb0b907a92f3b0939588ea63046a70403407af` |
| `intent.json` | `ed709a21d7f6f8d76c3b2cfed53f54b7f69a41a6d1a5f94cbedcc86aeb7a69d9` |
| `prior-active.json` | `ed40ee14278426d7af0b11a7b3a1e3ce4719f0cbad2bf7e566fd73224a6cd283` |
| `receipt.json` | `8b7958e5be76f6b35c4bfafc1f17a2926badfdd813addbefd5d683e376e8eeeb` |

Raw operation evidence: `install-and-fresh-verify.log`. Exact target bindings:
`EXACT-STAGED-PACKET.md`, `plan.json`, `review.json`, `authorization.json`.
The independent verdict is `docs/RECOVERY-V4-REVIEW.md`.

The previous rejected r8 closure remains archived at
`/Library/GRRR/bootstrap/recovery-v4-history/rev8-4db1623-f01aa240`.
The first r9 staging attempt was denied by macOS Documents privacy before any
bootstrap staging changes. The successful retry used hash-verified temporary
copies; no protected permissions or privacy settings were weakened.

## Explicit limits

No reconciliation, replay/runtime reset, campaign execution, contract admission,
promotion, production mutation, merge, or push occurred. This result establishes
the requested accounting recovery and verification, **not full GRRR capstone
completion**. PM acceptance is a separate tracker transition; this report is not
self-acceptance.
