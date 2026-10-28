# Stage K per-record evidence — operator handoff

## Purpose

Stage K searches repository-retained and original operator-session evidence for
the remaining reservation-specific fields after Stage J’s common authorization
binding. It does not access protected paths, reconcile accounting, replay,
admit, promote, merge, or push.

## New evidence validated

### Numeric process identities

Reviewed repository evidence establishes:

- `_grrr_evaluator` = UID/GID 320.
- `_grrr_runner` = UID/GID 321.

The pinned source also defines:

- evaluator principal UID 320;
- runner principal UID 321.

### Common ledger issuer identity

The pinned ledger implementation requires evaluator UID 320 and rejects every
other journal principal. The Stage A database owner is also UID/GID 320.
Therefore the common ledger issuer identity is validated as UID 320.

This does **not** create a per-request authenticated-principal receipt.

### Original session readback boundary

The original operator root-session archive contains one complete readback record
at line 11533 with all 16 reservation/run identifiers.

- Read started: `2026-10-21T20:00:39.190Z`
- Read completed: `2026-10-21T20:00:54.106Z`
- Line SHA-256:
  `9ab13249897f4508a2410ba4eabbf29becaab434e7fba8cc3ab551f25650ae60`

This is a common retrieval/readback boundary, not a per-reservation measurement
interval.

## Per-record matrix result

For all eight candidates, Stage K preserves:

- reservation ID;
- run ID;
- request key;
- request event sequence/hash;
- trusted observation object hash;
- meter receipt hash;
- measured duration;
- source/export/Stage I/Stage J custody chain.

Validated common fields:

- numeric evaluator/runner identity mapping;
- evaluator ledger issuer UID 320;
- common authorization binding;
- common readback boundary.

Still missing per reservation:

- authenticated principal receipt;
- explicit dispatch operation ID;
- reservation-specific request start/end boundary;
- reservation-specific UTC measurement start/end;
- measurement clock identity and window digest;
- artifact creation timestamp;
- independent reservation-specific custody classification;
- final independent classifier decision.

No record is classified `supplied`, and all eight remain response-not-ready.

## Tests

- Homebrew Python 3.14.3: 14/14 focused Stage K tests passed.
- Miniconda Python 3.12.7: 14/14 focused Stage K tests passed.
- Deterministic generation: byte-identical.
- `pvg verify --include-tests`: PASS.
- `git diff --check`: PASS.

## Next gate

Independent review of this Stage K matrix, followed by a search for original
dispatcher/evaluator records containing per-request authenticated principals,
operation IDs, and UTC timing boundaries.
