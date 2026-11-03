# GRRR-z3w9 Stage D narrow rework review request

## Exact scope

Review only whether the second capture corrects the three Stage D review-1
findings. Do not access or mutate `/Library/GRRR`. Do not write spendability,
reconcile, replay, admit, promote, mutate production, merge, or push.

## Exact identities

- Base story branch commit: `37a550cc4998ed71f8b6b7c29cccf332d85c65b8`
- Capture program:
  `docs/evidence/spendability/stage-d/CAPTURE.py`
  SHA-256 `2312a453e9e3c807d023456606da36303a97fab27c9fc9da243ff14774f1d4ee`
- Capture artifact:
  `docs/evidence/spendability/stage-d/CAPTURE.json`
  SHA-256 `d22bec465786840fc85a139ebe3781f68bd1663bde51649ac96d34e03e340de8`
- Approved-schema validation:
  SHA-256 `cf2d77eb7b19dd2ce917a8a1557b7e62472abe81cc93f149fba825ac3fcc9e56`
- Postcapture verifier:
  SHA-256 `a48d4233235699d680200dedd894943135ca3e2c264a5e8512fbcca5093132e2`
- Postcapture result:
  SHA-256 `78eb1f69a30d161f3c2d8c67fbbf40e579cc3de5f53b6bb0f8e8fc395888574a`
- Review-1 rejection:
  SHA-256 `edbccf1239aa854f2e294e722aa8eb2020244b271fec5e687112a1884975a40f`

## Required corrections

1. Verify the second capture is descriptor-bound and lock-bound:
   active bytes are read once through a no-follow descriptor after lock
   acquisition; active/database/lock path identities are bound to descriptors;
   sidecars and final locked identities are collected before unlock; completion
   is timestamped after all release observations.
2. Verify toolchain identities are independently measured:
   parent expected bytes are the reviewed source and observed bytes are the
   root-owned executed copy; interpreter and policy observed bytes are measured
   against independent expected hashes.
3. Verify the postcapture result is bound to the retained capture hash and
   records a timestamp after capture completion plus expected and observed
   active/lock/database hashes and device/inode identities.

## Recorded second-capture facts

- Capture: `2026-10-27T04:30:49.201645Z` through `2026-10-27T04:30:49.260082Z`
- Lock acquired: `2026-10-27T04:30:49.201887Z`
- Lock released: `2026-10-27T04:30:49.260069Z`
- Active SHA-256: `9c5194dd12ff7601917fcccc293c459db09a41da8bad9fa9983cbef618d453f8`
- Database SHA-256: `9c6ff2561a364ed982cd5477dd4b200c995da6910c9a17aa3d3c411a962d64f3`
- Lock SHA-256: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- Postcapture observation: `2026-10-27T04:32:57.578197Z`
- Postcapture active/lock/database checks: all true
- Sensitive processes: UID 320 = 0, UID 321 = 0, QEMU = 0
- Sidecars: none
- Focused Stage C tests: 46/46 on both interpreters

## Required verdict

Return exactly one:

- `STAGE_D_NARROW_REWORK_REVIEW: APPROVED`
- `STAGE_D_NARROW_REWORK_REVIEW: REJECTED`

Approval covers only the locked read-only capture artifact and schema evidence;
it is not spendability, reconciliation authority, replay authority, admission,
promotion, merge, or push authority.
