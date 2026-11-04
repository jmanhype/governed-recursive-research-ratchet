# GRRR-6sso exact-target full E2E decision request

## Decision state

- Request ID: `GRRR-6sso-exact-target-e2e-v1`
- Created: `2026-11-04T01:51:58Z`
- State: **blocked awaiting independent review and human authorization**
- **`execution_authorized: false`**
- Effect now: **none**
- This Markdown and `E2E-DECISION-REQUEST.json` are request artifacts only. They do not launch a VM, read or write a protected path, replay, admit, promote, mutate production, call Jev/network, access credentials, pop the excluded stash, merge, or push.

## Exact revision bindings

| Role | Revision |
|---|---|
| Historical evidence base | `845b47d221773eb4157491d35f57dce47ce8afe6` |
| Accepted admission fail-closed fix (GRRR-ev2w) | `710e6fb1affa366da6ca4c855f49805d3bdb944d` |
| Current epic `epic/GRRR-2t3h` | `0b2365e30ab5858cb419f4f4ce9b2ce001850541` |
| Current story `story/GRRR-6sso` | `c928791cdaa72df91e61002c40317457b543b032` |
| Observed main (not a merge target) | `c2970356436531565711fb3c2df24eb91c3ed510` |

The exact story HEAD and epic HEAD must match these values. The admission fix must be an ancestor. Any changed request byte requires a new independent review and human decision; historical approvals are not reusable.

## Immutable historical evidence identities

The authoritative machine-readable inventory is `E2E-DECISION-REQUEST.json`; all 19 entries exactly mirror `evidence-index.json` at historical base `845b47d221773eb4157491d35f57dce47ce8afe6`. Matching an identity is not fresh runtime proof, approval, export verification, replay, admission, or E2E success.

| ID | Last-changing revision | SHA-256 |
|---|---|---|
| adaptation | `cf3eb55422ba18898541318c138cd82543419d12` | `550944a2b81b1e52cf4c9aaf410b5e43bcb5758aa0eb1bfa9ba4a63094d352ba` |
| admission | `0503286612075c06d0acda654b740f12ee9a873f` | `c875e5668ccbc3f79735045fc69899bddd675552207bb3d34e40fc27a7326686` |
| architecture | `0fa26e4cf6f0c35b19fb6f1f75259932b00a086e` | `c06101668429195596a4d2bf4e4731d02ae0a0b870da93a50bbe6c9f4382add0` |
| authorization | `0503286612075c06d0acda654b740f12ee9a873f` | `55dbedc3e03c31a61830e2e83969243cac7958f86ee5b86d0ba488b77fe4e911` |
| business | `67ea3709b0ad1d3d496d90e99af3feca8b25f745` | `7d56b562c4b3c194e2ee76ccdd4be68aa22ff0f8b749bdefacbd03e868a5dd82` |
| contract | `0503286612075c06d0acda654b740f12ee9a873f` | `d9ef76d4f99f8d354fdbeb7473a88423728cdc46ff15800f7b58109dad5a4910` |
| corpus | `3f6d8dcfb407438591ad13c9bc14d60886bb0d73` | `93f2558864a7bdfa01dd0e8042ae8330834659ef71812f17a6ddc9efac3c5cc4` |
| design | `67ea3709b0ad1d3d496d90e99af3feca8b25f745` | `97f0e36febd2ad4dce43cc2912db477735f82349d9d3f965d22216d6a566b252` |
| durable | `1c2a1c595703abf6a94e96792c5f1deb60841ca8` | `d7b8d4c14510a689f9742edba1f5a7d8019b58cfd191bce9b48ba4cb421556c6` |
| export_verification | `ff600fff656ef8570857291e6b0a79fb2862ce64` | `f73589682a553d48d6a6c452720d030e087f07a30e2bc598ca09232dc698cecb` |
| jev_design | `9e107609db76022ed6d8e138cbbece2e41d634ee` | `97ec4b8ccc34b3fc4da4fcfbef33b49bbb3f4f1c445cfecdb752715ddf034be1` |
| jev_manifest | `5b50e29272819da205fc09e051f82c2639a7a197` | `0632b43338155d0cf9802dc21079b2aa66dc6bb11a3710f312cf3dc546788d36` |
| jev_result | `5b50e29272819da205fc09e051f82c2639a7a197` | `b7bb2ec8717e8921e16f9a3e312f6ad46839a125634dc6e3d144499cc841fefb` |
| jev_review | `5b50e29272819da205fc09e051f82c2639a7a197` | `57d71f12f21f0f0a6407923fc8c1137e819b7ecf3d297670e0b58a5d96cc4db1` |
| lifecycle | `ff600fff656ef8570857291e6b0a79fb2862ce64` | `4f9c08584c72b4dc8cf0e878ae901007a97024ab8d60889987e5dba9c76ca795` |
| replay_receipt | `ff600fff656ef8570857291e6b0a79fb2862ce64` | `78fde524d9562f6cb28df336512b3ca84bc8d72c72b47cd71f1a47516613ab4e` |
| scorecard | `86ace00860f62f302f4f633eefa6c98b5cce8252` | `2bcaa7cdaacc6b8d642846c498fcf1e93655948afa2cd1a8463fcbc36359bd12` |
| snapshot | `ff600fff656ef8570857291e6b0a79fb2862ce64` | `ab8d72f25c3a4ce2f5d5d672c4d052ea2de442f9c9384bd381d8222d7a91b689` |
| stop | `3f4a9cf2c52ae5992f76ff5350e63518ba1fad83` | `88c4768aeee38a36c3dafb07480978515fceec365658b171278bce945da811cc` |

## Required preflight

Preflight is blocked and must complete before any VM launch:

1. Confirm the clean worktree and every revision binding above, including GRRR-ev2w ancestry.
2. Verify all 19 historical identities against the pinned index and current local Git objects without treating them as fresh gate passes.
3. Verify source, archive, input ISO, VM image, preparation/profile, interpreter/tool, capacity, evaluator/runner identity, corpus, ledger schema/tip/anchor, reservation, and output-name availability.
4. Obtain independent review plus cost/review-time reconciliation.
5. Fail closed on malformed, stale, missing, unknown, ambiguous, or exhausted inputs.

## VM, evaluator, and ledger

- VM: one dedicated disposable offline guest per candidate; no host/container fallback. Bind source commit `129e0b3f15a3bd6af949ee47d76f6855c582ab73`, archive `e644b9848b306f158a2367293dd96c66dac2bed97c0dd42891db007667c0ae7e`, input ISO `57c48a6845d65b6b3674c80367af42c062cf079d7bbdc4491331a4945375d2b6`, image `6c3cb672f367fd5164672e0a2d36f720dcc705414c6dcf96ab9e9d3adfa327f3`, preparation `755af0f8d9fc632287b5b099fc7ac913ad9a01970f0ad84145a2c15fce96815c`, and profile `b3b92a6382c1ed276862675540ab07ba399a4e0dc8bcdc7254138e5abc86db71`.
- Boundary probes, disabled networking, and UID separation are mandatory: evaluator UID 320 owns protected expectations, verdicts, reservations, and receipts; runner UID 321 remains separate. Principals are transport-authenticated, never trusted from payload roles.
- Ledger appends must bind fresh expected tips, idempotency keys, snapshots, and an independently retained anchor. Historical D011/durable anchors are identities only, not current verification.

## Seed inventory, replay, and admission

The frozen corpus is `GRRR-validated-corpus-v2.2-isolated`, digest `dfa75ef2bf3d43fd4f750094fe643afe4f204812c0ae2426276bedb471fa8529`, with 24 defects, 8 clean negatives, 17 critical cases, and all 32 IDs listed in JSON across training/measurement/holdout partitions. At least 20 representative seeds plus all clean negatives must traverse all gates; required detection is 100% critical and ≥90% remaining. Historical fixture validation cannot substitute.

Fresh replay must retain per-seed commands/output hashes, operation IDs, expected ledger tips, and every gate outcome. D011 alone is insufficient. The proposed two-consecutive-independent-replay-failure threshold itself requires review and human approval before launch.

Admission requires a new exact-target grant bound to contract digest, verified snapshot, current run epoch, idempotency key, and authenticated admission principal. The clean baseline must pass and recurrence must be rejected. Zero invalid or failed-replay admissions are allowed. The accepted GRRR-ev2w registry fix is current: malformed, unreadable, invalid-shape, directory, and dangling-link registry states must fail closed while preserving bytes.

## Negative cases, stop, and recovery

The full matrix must cover forged identity/evidence, stale approval, missing gate, unknown/exhausted budget, protected write, ambiguous spec, tampered/truncated/missing exports, duplicate authorization/contract, and unusable admission registry. Every case must fail closed with matching CLI/Markdown/JSON safe action and no unintended mutation.

The journey must stop a deliberately hung executor, prove cessation/fence and idempotent repeated stop, preserve durable dispatch/admission ordering, cover every durable crash transition, list committed-before-stop admissions, and either verify restoration from preserved hashes or return `RecoveryRequired`. Hard-stop triggers include budget/runtime/review exhaustion, authorization or protected-write violation, isolation failure, missing dependency, integrity failure, unrecoverable state, and repeated unreproducibility.

## Independent cost and accessibility closure

- An actor independent of the execution team must close incremental USD, cumulative USD, execution time summed across concurrent arms/replays, preparation time, review time, and open reservations. Current cumulative values are unknown, not zero. Historical Jev confirmatory usage was 96 calls, zero retries, 37,644 input / 2,208 output tokens, and USD null.
- Proposed incremental maxima: **$50, 6 execution hours, 60 review minutes**. Cumulative ceilings including POC: **$150, 24 execution hours, 180 review minutes**. No automatic increase; unknown maximum cost blocks paid dispatch and uncertain usage retains reservation.
- Keyboard-only and screen-reader walkthroughs must inspect the layered report, distinguish execution/finding/decision/effect, reject, request evidence, stop, and review recovery, with aggregate review timing recorded separately from execution.

## Immutable output destinations

All outputs are reserved, not created, under `docs/evidence/milestone-e2e/GRRR-6sso-exact-target-v1` and become write-once immutable evidence:

- `PREFLIGHT.json`, `VM-IDENTITY.json`, `EVALUATOR-IDENTITY.json`, `LEDGER-ANCHOR.json`, `SEED-INVENTORY.json`
- `ADMISSION-GRANT.json`, `ADMISSION-RECEIPT.json`, `NEGATIVE-MATRIX.json`, `STOP-RECOVERY.json`
- `COST-RECONCILIATION.json`, `ACCESSIBILITY-WALKTHROUGH.md`, `OPERATOR-TRANSCRIPT.md`, `FINAL-REPORT.md`, `REVIEW-APPROVAL.md`, `SHA256SUMS`
- One `replay/{seed_id}.json` destination for each listed seed
- One `negative/{case_id}.json` destination for each listed negative case

`SHA256SUMS` must cover every emitted file. Overwrite, missing checksum, post-review mutation, traversal, absolute path, or protected-path reference invalidates the journey.

## Review, denials, and rollback

Independent review must reconcile the seven ACs, 11 gates, 19 identities, seed partitions, negative matrix, budgets, accessibility obligations, outputs, and stop/rollback semantics. A separate human decision must bind exact JSON and Markdown bytes, request ID, revisions, budget maxima, and the output root. Delivery and PM acceptance remain distinct.

Denied until separately authorized: `/Library/GRRR` access; protected read/write; VM/QEMU launch; replay; admission; promotion; production mutation; external Jev/network; secret access; stash pop; merge; push; automatic budget increase; and harness adaptation/autonomous patch generation.

On error or ambiguity: stop, preserve inputs/evidence/ledger, list committed-before-stop admissions when relevant, and require recovery review. Ambiguous committed state remains `RecoveryRequired`. Runtime disposal is allowed only after durable export/hashing. Repository rollback is review/revert of this story's request commit only; no destructive cleanup or excluded-stash access.

## Final request

Review these two exact request artifacts and decide whether to authorize the full seven-AC journey. Approval must be action-specific and consume a fresh grant. Until then, `execution_authorized` remains **false**, all gates/journeys remain blocked/not-run, and no capstone success is claimed.
