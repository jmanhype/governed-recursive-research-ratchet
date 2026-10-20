# Operator local-use authorization — GRRR-90te, 2026-10-20

This records the subsequent explicit operator decision in GRRR-90te nd notes,
confirmed in the dispatcher handoff. The earlier review draft and provenance
addendum remain unchanged historical evidence, including their then-open blockers.

## Exact authorization

The operator approved the reviewed **159-component** inventory with SHA-256
`dc11522600eae2424bf3fce4d124d401db85a3566fa63968d2a6a2ec32f98fcb`
for the already approved bounded local offline preflight only.

- No source/binary redistribution, appliance/media publication, or new project
  linking/incorporation is authorized. Preserve notices and source references.
- GPL/LGPL and other boundary-controlled components remain confined to approved
  local runtime/toolchain execution. No license classification or mixed
  AND/OR/WITH expression is narrowed. Existing host QEMU linking is not new
  project integration; Go's intended isolated compilation remains within scope.
- The operator confirmed that the installed **macOS build 26A428** terms permit
  local execution of the installed system frameworks and QEMU for this
  non-redistributable preflight. This grants no extraction, transfer, copying
  into guest media, redistribution, relicensing, or additional Apple rights.
- The operator authorized the parent-mediated root identity run after the disk
  floor passes and the exact final review artifact is bound. This document does
  not claim that the root run has occurred.
- Runtime dependency closure, clean baseline, reproducibility, isolation,
  cancellation, budget and license gates remain mandatory. Missing or uncatalogued
  dependencies, changed inputs, ambiguity or scope expansion still block execution.

## Review evidence binding

- Reviewed draft SHA-256:
  `4d3e93ebb6ac205225e7521c951a93baa64335a899710619ae3f593f7b3cf0c6`.
- Review-summary SHA-256:
  `fc64602277e89fbd4548dc6742e6a0649c73eeaa433deb59d96083d1a48dde9f`.
- Provenance-addendum SHA-256:
  `3be01e90783d6cfeb928585691c86d7413a37c02c8d5e0bc93135cb4cc36bc67`.
- `license-authorization-reference.json` binds this operator decision, the
  existing build-profile approval, inventory and exact license evidence. Its
  SHA-256 is the final private review's `authorization_reference`.
- The final launcher review remains outside Git at
  `.tmp-sr_pm/offline-preflight/assets-20261020-1/license-review.json`, owned by
  operator UID 501 with mode 0600. Its final hash and schema/key validation are
  recorded separately in `authorization-checks/review-verification.json`.

The 54 permissive-local-use, 80 boundary-controlled, and 25 Apple/system
classifications are preserved from the reviewed draft. Public-domain provenance
dispositions retain current ppp chat MIT attribution and the IANA named-file
BSD-3-Clause exceptions. The deferred Go dependency check is still unexecuted;
it is not relabeled as resolved merely because the operator approved measurement.

## Authorized disk cleanup evidence

The parent removed only `/Users/speed/.gradle/caches`, a regenerable build cache
(reported 1.7 GiB, 19,865 files). The parent manifest and console are copied
byte-for-byte as `parent-gradle-cache-cleanup-manifest.txt` and
`parent-gradle-cache-cleanup-console.txt`. Both original files have SHA-256
`de0617ffa519fa284b03e03f13e0eec0ab8620c12887d14df43cd44ee1577851`.
No new cleanup is performed by this authorization-finalization step. The launcher
must still recheck the 15,000,000,000-byte floor immediately before execution.
