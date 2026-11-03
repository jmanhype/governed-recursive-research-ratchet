# Stage I provenance enrichment — operator handoff

## Purpose

Stage I searches non-protected operator archives for issuer, authorization,
timing, and custody evidence matching the eight Stage H candidate record sets.
It does not access `/Library/GRRR`, classify evidence, reconcile accounting, or
grant execution authority.

## New evidence found

### 1. Exact toolchain and source custody

The trusted plan binds:

- source commit `9d3df8770f82a860f128a71d76528ff922911199`;
- 26 exact implementation/test code hashes;
- runtime, helper, supervisor, image, Python, and QEMU identities;
- offline/no-paid-dispatch controls.

The evidence export commit is:

- `141823fe7e19e43fd3d2bfcc0fe4be8303e42642`;
- parent is exactly the pinned source commit;
- key export bytes match the current repository evidence.

### 2. Corrected approval references and validation

A bounded operator-session archive contains the corrected approval generation
and validation outputs:

- execution approval SHA-256:
  `fdb11c2c30b2c385f132f4607ba2a198b42b9e0840e3c0bcee3035fb4191ca7b`;
- license-review SHA-256:
  `ad9570ca20676363eb4b3dff23715b058322a0ecffe10e7e3b404db5863d896d`;
- execution profile SHA-256:
  `b5400cdf040725cbe3b661d1d69f26a276123775bb63074b49fd7420befe61a7`;
- `approval_validation=pass`.

These are **references found in an operator session archive**, not exact copies
of the protected approval/review artifacts. Exact protected bytes and
independent custody review remain required.

### 3. Observed process identities and batch operation boundary

The same archive records the real launcher processes:

- `_grrr_evaluator`;
- `_grrr_runner`.

The archive record identifies those process names but does not by itself bind
them to numeric UIDs. Numeric UID mapping remains unresolved in this Stage I
record.

Exact root-launcher boundary:

- started: `2026-10-21T19:55:53.853Z`;
- completed: `2026-10-21T19:59:54.106Z`;
- duration: `240253` milliseconds;
- private runtime: `/private/tmp/grrr-trusted-rk5jwjmv`.

This supplies a batch operation boundary only. It does not supply each
reservation’s operation ID or measurement window.

### 4. Preservation custody

The archive also records preservation of 17 files with trusted readback SHA-256:

`2bbdb46aced148263505a775cee3e5033c20c337d1da6a73e875c87f62a821a8`

That result is independently bound to the export commit and current repository
bytes.

## Credential and privacy boundary

The session extract is redacted. It copies only selected authorization,
validation, launcher, process, readback, and preservation records. The three
password-bearing stdin records are intentionally absent. No credential value,
API key, bearer token, unrelated private record, or full session archive is
published. The generator independently hashes the full non-protected source
archive and compares every selected extracted record against that source; the
redacted stdin records are type-checked at their source lines but never copied.

## Still blocking final `supplied` classification

For each of the eight reservations:

- per-request authenticated principal and issuer binding;
- numeric process UID mapping;
- exact protected approval/review artifact bytes and custody;
- reservation-specific dispatch operation identity and boundary;
- reservation-specific UTC measurement start/end, clock, and window digest;
- reservation-specific custody classification;
- independent final classifier decision.

Therefore all eight record sets remain candidates; none is response-ready.

## Verification

- Homebrew Python 3.14.3: 13/13 focused Stage I tests passed.
- Miniconda Python 3.12.7: 13/13 focused Stage I tests passed.
- Deterministic generation across both interpreters: byte-identical.
- `pvg verify --include-tests`: PASS.
- `git diff --check`: PASS.
- Full suite remains not run under the existing host-pressure/process-table gate.

## Required next gates

1. Independent review of this provenance-enrichment package.
2. Separately authorized exact read-only protected approval/review search, or a
   custodian-provided exact copy of those records.
3. Reservation-specific operation and timing records.
4. Independent classification review before any partial external response is
   considered `supplied`.
