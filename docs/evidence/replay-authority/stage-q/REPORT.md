# Stage Q v4 installer core — sandbox-only implementation

## Scope

Stage Q implements the repository-retained v4 installer core and checkout CLI.
It does not access or mutate `/Library/GRRR`, stage protected records, execute a
protected installer, amend a budget, reconcile, dispatch replay, promote, admit,
merge, or push.

## Implementation

Added:

- `research/replay_successor_installer.py`
- `scripts/install-replay-successor-v4`
- `tests/unit_replay_successor_installer.py`

The installer core:

- validates the exact eight-role source inventory;
- requires distinct source hashes;
- binds the approved Stage N/O package and predecessor basis;
- validates exact plan, review, and external operator-authorization hashes;
- models the canonical root/interpreter/entrypoint identity without acquiring
  privilege;
- verifies source bytes before target creation;
- refuses an existing or partial target without reset;
- creates only a caller-supplied sandbox store;
- creates an empty SQLite store with `stopped=1`;
- writes a v4 binding and receipt with all operational authority false;
- verifies database integrity, exact identity, stopped state, and empty tables;
- preserves `uncertain.json` on failure without retry or authority.

The created store remains stopped because budget amendment is a separate gate.
The checkout CLI refuses both malformed grammar and even the exact live-install
grammar. No protected source issuance or live path is enabled.

## Initial review and correction

Initial review rejected three real blockers:

1. a postflight failure could leave success-looking receipt/binding artifacts
   plus uncertainty, and the verifier still accepted the store;
2. postflight did not enumerate exact SQLite objects/schema;
3. sandbox containment was only caller convention and did not reject protected
   paths or symlinked ancestors before filesystem access.

Correction now:

- requires an explicit non-root sandbox root containing source and target;
- lexically rejects `/Library/GRRR` before path access;
- rejects symlinked ancestors and final components;
- verifies exact SQLite object inventory and table DDL;
- makes `uncertain.json` dominate every verification;
- injects failures at receipt write, active write, directory sync, and
   postflight, proving each becomes an unverifiable uncertain store.

## Durability repair discovered by the full suite

Three earlier spendability validators depended on a mutable Codex session file
that host session retention has now removed. The suite correctly failed rather
than treating absence as zero.

The repair:

- keeps live original-archive reproduction whenever that file exists;
- otherwise validates the already retained, hash-pinned Stage I/K publications;
- adds a retained, hash-pinned Stage L original-session-search projection;
- preserves the original source hash and explicit unknowns;
- does not claim the missing mutable source is still present;
- does not fabricate raw source bytes or turn absent evidence into zero.

This preserves evidence durability without weakening prior uncertainty.

## Verification

- Focused Stage Q tests after correction:
  - Homebrew Python 3.14.3: 34/34 passed.
  - Miniconda Python 3.12.7: 34/34 passed.
- Durability-focused suites:
  - Stage I provenance: 13/13 passed.
  - Stage K per-record: 14/14 passed.
  - Stage L request search: 15/15 passed.
- Full no-guest unit suites after correction:
  - Homebrew Python 3.14.3: 595/595 passed.
  - Miniconda Python 3.12.7: 595/595 passed.
- The focused and full runs promoted `ResourceWarning` to an error.
- `pvg verify`: PASS.
- `git diff --check`: PASS.

## Remaining gates

The initial independent review is rejected and preserved. Fresh narrow re-review
also rejected the containment correction:

```text
STAGE_Q_NARROW_REWORK_REVIEW: REJECTED
```

The narrow reviewer found that protected-root rejection still performed
metadata calls before lexical rejection, `sandbox/../outside` could escape the
explicit root, and a sandbox root beneath a symlinked ancestor could evade the
ancestor check. The reviewer’s corrected syscall guards produced 33 passed and
1 failed on both interpreters.

Important disclosure: the repository’s own protected-root regression therefore
performed metadata access under `/Library/GRRR`, contrary to the declared
boundary. No protected content was read and no protected state was mutated, but
this is still a boundary violation. Stage Q must not proceed to another review
round without explicit operator direction.

The operator subsequently authorized the revised containment-only brief. The
first revised review rejected repeated-leading-slash and unrelated `/Library`
ancestor aliases. The one permitted retry corrected both and returned:

```text
STAGE_Q_CONTAINMENT_ALIAS_REVIEW: APPROVED
```

The approved lexical phase now rejects repeated leading roots, explicit `..`,
absolute escapes, the entire `/Library` tree, and all `/Library/GRRR`
descendants before any stat/lstat call. Real-ancestor checks then reject
symlinked sandbox roots and ancestors. The reviewer executed 40 fully mocked
lexical probes per interpreter with zero stat/lstat/fstat calls and confirmed
the existing SQLite, uncertainty, publication-failure, and checkout protections.

SQLite exact-inventory, uncertainty-dominance, injected publication failures,
and checkout refusal remain corrected. Exact eight-file protected source
issuance, protected staging, operator authorization, protected installation,
postflight, budget amendment, reconciliation decision, replay authorization,
live four-mode replay, PM acceptance, merge, and push remain separate and
unauthorized.
