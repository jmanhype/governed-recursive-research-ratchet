# Integrated JIT amendment contract review — 2026-11-04

INTEGRATED_JIT_REVIEW: APPROVED

## Scope and inputs
- Repository HEAD verified: `2b601462ba0ffb5aee6239aa22b06c26801dfaf9`.
- Integrated base SHA256 `954a8578ca9354c0af2d1d19a25bff3dcd2f41b2ef98e62e5667254230239c56`.
- Original JIT SHA256 `3f2c661bf93b8513440f3a31daed2f3d2f37cd312137c3181304195402ebb488`.
- Prior rejection SHA256 `ae447e94efdbfcbf7480f0e7756734d1f202eeab9425adeb48a8bc8e603b76c5`.
- Repaired v3 SHA256 `3ab960191613b2e10018f5c9444532080e9757693c49393f888c6beff0793e09`.
- Integration corrections SHA256 `97c918328606cd69c62c6eaf52528ee4b024a76a8c5983a9e46f59c6a0bb7cee`.
- Applied precedence: corrections > v3 > original JIT > base. This review covers the
  three rejected findings and the named Ledger/reviewer integration only. It does not
  reopen resolved base findings F1-F3 and does not infer production qualification.
- Bounded source fallback used `research/ledger.py`,
  `research/capstone_contract.py`, and `research/capstone_journal.py` at the verified
  HEAD. The codebase graph was unavailable, so no exhaustive source claim is made.

## Original finding resolution
1. Campaign replay, transitions, and stop-pending are concretely contractable. The
   corrected event discriminator remains `capstone-campaign-event-v2` while Ledger
   envelope compatibility is restored to integer version `1`. The v3 reducer supplies
   exact rows, immutable identities, revision preconditions, action allowlist, receipt-
   derived anchors, replay comparison, SQL transition guards, non-resumable owner
   fencing, and a distinct `stop-pending` authority state. The stop hook commits the
   base campaign stop and run transition together; verified cessation and failed
   cancellation remain separable.
2. Persisted preclaim provenance is now truthful. An immutable leaf-plan row stores
   canonical Plan bytes, both the Plan selfhash and raw-byte hash, deterministic
   operation identity, and review hash atomically with the base binding. Status and
   manifests distinguish `not-planned`, `binding-only`, and `claimed`; a valid full
   Operation exists only after the unchanged journal claim. Missing joins fail closed
   rather than becoming fake authority, success, or a downgrade to unplanned.
3. Independent actual-Plan review is concretely separated from immutable finite
   approval. Static authorization continues to bind the finite CampaignSpec, grants,
   maxima, installation, window, and review anchor; it additionally approves the
   deterministic JIT procedure and verifier inventory without authorizing unknown
   future Plan bytes. The separately authenticated UID322 store retains canonical,
   phase-tagged `ReviewV2` bytes binding leaf, observation, anchor, operation, Plan
   hashes, policy, source/static reviews, expiry, evidence, and blockers. Review
   storage is not a substitute grant and cannot fabricate runtime-result approval.

## Exact source integration
- `research/ledger.py:72-77` confirms `Ledger._append` injects `version: 1` and the
  idempotency key. The corrections correctly supersede only v3's envelope-version `2`
  wording; reviewer request version `2` remains a wire/record version, not a Ledger
  event version.
- `research/capstone_contract.py:197-216` confirms `bind_observation` requires exact
  nonce, epoch, operator, full-anchor, clock-window, and receipt-age equality. It does
  not accept a freshness delta or derive liveness itself; the integrated ordering must
  pass the unchanged check against the current prebind anchor.
- `research/capstone_journal.py:265-291` confirms claim is the first source operation
  construction/consumption boundary and consumes the exact Start/Plan binding. It does
  not mint an Operation for persisted preclaim Plan bytes.
- The corrected reviewer/context sockets use separate kernel-UID principals and
  dedicated capacity. Review/context traffic performs no ledger, accounting, grant,
  registry, or launch mutation and holds no ledger or launch gate, so the review path
  cannot deadlock on its own context lookup. Final strict bind remains the freshness
  gate.
- Source fixtures remain private-temp, peer-authenticated, unprivileged, explicitly
  nonproduction, and barred from protected metadata and identity-check patching.
  Production UID322 provisioning, factory/kernel identity validation, ACLs, and live
  qualification remain future live-only gates.

## Verdict
No material contract gap remains in the requested review scope. The three original
rejection findings are resolved with executable contracts, and the named Ledger and
reviewer integrations preserve the unchanged freshness, claim, finite-approval, and
source-versus-production boundaries. No tests, builds, protected-path access, network
operations, repo/tracker mutations, installation, accounting, recovery, admission,
promotion, production, or push operations were performed.
