# Stage G evidence search — operator handoff

## Scope completed

This was a read-only search and validation slice over non-protected operator
archives and repository-retained evidence. It made no final evidence
classification and granted no operational authority.

## Useful records found

The committed trusted-observation export at
`docs/evidence/trusted-observation/v4-run-9d3df87/` validates end-to-end:

- 30-event hash chain;
- 11 reservation request events;
- eight observation objects;
- exact Stage A meter receipt/usage joins for eight settled reservations;
- three pending reservations remain observation- and meter-less.

For eight settled reservations, Stage G therefore has a complete candidate set:

1. original request event from the evaluator ledger;
2. content-addressed trusted observation object;
3. exact meter-body copy and receipt join from Stage A.

These are **candidates only**. They still require independent review before any
Stage F response record may classify them as `supplied`.

## Still missing

- The three pending reservations have only partial request/gate evidence; they
  still lack definitive disposition, cessation, stale-handle, and pre/post state
  proof.
- None of the eight requested lineage artifacts' exact original bytes is
  established by this record. Manual discovery did not find them, but the
  generator does not consume exhaustive search receipts, so this is not a final
  absence classification.
- One evaluator export is not complete operation history.
- No side-store history, overhead-domain record, or complete global-history
  record is established by this record.
- Current agent/session logs contain the IDs but are not trusted evaluator
  receipts and cannot settle accounting.

## Discovery observations, not exhaustive search proof

Manual discovery looked at repository files, git blobs, the October 2026
operator session archive, memory/attachment archives, project output archives,
and top-level GRRR temporary artifacts. Those observations are recorded in
`CANDIDATE-INDEX.json`, but the generator does not consume search receipts or
inventories proving those scans exhaustive.

This slice did **not** search:

- `/Library/GRRR`;
- remote or network archives;
- credentials;
- unrelated private logs.

Negative observations therefore remain `search-completeness-not-established`;
they are not final `unavailable`, `lost`, or `never-created` classifications.
Before a final negative classification, a separately reviewed search-evidence
package must pin commands, inventories, timestamps, custodians, and complete
boundaries.

## Test environment note

The previous system Python path now reports that the Xcode 27.1 license has not
been accepted. No license was accepted and no privileged action was taken.
Stage G tests passed on Homebrew Python 3.14.3 and Miniconda Python 3.12.7, and
generation was byte-identical between those interpreters.

The latest full no-guest suite encountered the existing process-table polling
test `test_real_term_resistant_group_is_killed_within_deadline` under heavy host
load (about 80–1000 concurrent processes during the runs). It timed out once on
each interpreter. The isolated replay-smoke module then passed 12/12 on both.
The full-suite gate is therefore not claimed as accepted; this Stage G slice is
still search/validation only.

## Required next gates

1. Independent review of the Stage G search/index implementation and artifacts.
2. Operator decision on whether to authorize an explicitly read-only protected
   ancestry search under `/Library/GRRR` for the eight exact lineage byte sets.
3. Separate classification/review of any supplied records.
4. Separate authorization for reconciliation, replay, admission, promotion,
   merge, production mutation, or push—none of which is granted here.
