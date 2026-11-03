# Stage L per-request evidence search — operator handoff

## Purpose

Stage L searches the pinned original execution session archive and exact retained
trusted records for the remaining per-request dispatcher/evaluator evidence:

- authenticated principal;
- issuer;
- dispatch operation ID;
- operation/request boundary;
- UTC start/end;
- measurement clock;
- measurement window digest;
- artifact creation timestamp.

It does not access protected paths, reconcile accounting, replay, admit, promote,
mutate production, merge, or push.

## Search boundary

Stage L scanned:

- every line of the pinned original operator root-session archive;
- all exact target-field representations in each candidate-ID-bearing archive
  record, including fields serialized inside string-valued tool output;
- all 11 exact trusted request-event bodies, including the three pending requests;
- eight exact trusted observation objects;
- eight exact Stage A meter bodies.

The original root-session archive contains exactly two candidate-ID-bearing
lines:

- line 11533, containing all 22 reservation/run identifiers;
- line 11534, containing 12 identifiers in the persisted tool output copy.

Across the complete pinned archive, all 22 reservation/run identifiers are
covered. The serialized-output scan found three generic `operation` fields, all
with value `unknown`; they are pending gate-error fields, not settled dispatch
operation IDs or request boundaries.

Line 11533 has an operator tool/readback boundary, but that boundary is not a
reservation-specific measurement interval.

Later session files contain many copies and analysis references. They are not
treated as original evidence.

## Result

Inside the declared exact-record boundary, Stage L found:

- zero authenticated principal fields;
- zero issuer fields;
- zero operation IDs;
- zero operation/request boundary fields;
- zero `started_at` fields;
- zero `ended_at` fields;
- zero clock fields;
- zero window digests.
- zero creation timestamps.

All eight duration values remain present. No duration was converted into a
reservation-specific UTC interval.

This is not a claim that such records are unavailable, lost, or never created:
the whole operator archive and all external custodians have not been exhausted.
The result is only `not-present-in-retained-original-records`.

## Per-record result

Each of the eight candidates retains:

- reservation ID;
- run ID;
- request key;
- request event sequence/hash;
- observation object hash;
- meter receipt hash;
- measured duration.

Each remains:

- unclassified;
- response-not-ready;
- not `supplied`.

## Tests

- Homebrew Python 3.14.3: 15/15 focused Stage L tests passed.
- Miniconda Python 3.12.7: 15/15 focused Stage L tests passed.
- Deterministic generation was byte-identical.
- `pvg verify --include-tests`: PASS.
- `git diff --check`: PASS.

## Next gate

Independent review of this declared-boundary search package. A final negative
classification still requires a separately reviewed exhaustive search-evidence
package with commands, inventories, timestamps, custodians, and complete source
boundaries.
