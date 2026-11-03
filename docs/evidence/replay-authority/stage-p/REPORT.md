# Stage P future v4 installer/authorization contract — design-only

## Scope

Stage P defines a repository-retained, fail-closed contract for a future v4
installer and operator authorization. It does not build installer bytes, read or
write `/Library/GRRR`, stage protected records, execute SQLite, launch a process,
amend a budget, reconcile, dispatch replay, promote, admit, merge, or push.

## Exact basis

The contract binds:

- story HEAD `2051e7dd5378db6ed4c2057dd50aa3287bfe3525`;
- Stage N package
  `e349cc8349f62072af94f8b82ee1aafa1648db22270a77b9dba278469d305a48`;
- Stage O package
  `283918e2c1df4b9b25b79a26be90de9e5d20ea8c195b058a5b827c474872553b`;
- predecessor active, database, and recovery identities.

## Future installer closure

The contract names eight required future source roles and their exact protected
bootstrap artifact paths:

- installer entrypoint;
- v4 store schema;
- Stage N contract;
- Stage O runtime adapter;
- protected preflight;
- atomic publisher;
- postflight verifier;
- failure preservation.

Every source hash remains explicitly `null`. The plan, review, and authorization
hashes also remain `null`. The only issued toolchain identity is the already
reviewed canonical Python 3.9 interpreter hash; it is not an installer approval.

The target is the Stage N sibling store
`/Library/GRRR/accounting-poc2/unissued-independent-replay-v4`, never a
replacement for the predecessor.

## Required installer behavior

A future installer must:

- run only from the exact protected entrypoint and canonical interpreter;
- bind every named source role by exact hash;
- hold an exclusive parent window;
- install once;
- preserve the predecessor read-only with zero predecessor mutations;
- create only the new sibling namespace;
- refuse without retry while preserving partial evidence;
- roll back only the new successor namespace after a verified baseline;
- produce a complete postflight receipt.

The contract itself performs none of those actions.

## Authorization separation

The future action is exactly:

```text
install-fresh-v4-replay-successor-poc
```

The principal is `operator-via-exclusive-root-parent`. Installer, plan, review,
and authorization receipts must be distinct, and the operator authorization hash
is external to the record. A structurally valid future authorization shape still
does not authenticate the operator, reviewer, bytes, or live state.

The authorization explicitly requires a separate budget amendment before any
charge, while denying this installer authorization the power to:

- amend the budget;
- reconcile history;
- dispatch replay;
- execute work;
- admit;
- promote;
- merge;
- push.

## Verification

- Initial independent review rejected malformed schema-version typing:
  equality accepted `True` and `1.0` even though neither is an integer.
- Both contract and issued-authorization validators now require
  `type(schema_version) is int`; regressions reject boolean and float versions.
- Focused Stage P tests after correction:
  - Homebrew Python 3.14.3: 27/27 passed.
  - Miniconda Python 3.12.7: 27/27 passed.
- Full no-guest unit suites after correction:
  - Homebrew Python 3.14.3: 561/561 passed.
  - Miniconda Python 3.12.7: 561/561 passed.
- Deterministic contract emission: byte-identical.
- `pvg verify`: PASS.
- `git diff --check`: PASS.

## Remaining gates

The initial independent review is rejected and preserved. Fresh narrow re-review
of the corrected WIP returned:

```text
STAGE_P_NARROW_REWORK_REVIEW: APPROVED
```

Approval covers only this design-only contract. The future installer
implementation, exact source/plan/review/operator bytes, protected staging,
protected installation, postflight, budget amendment, dedicated identities,
replay authorization, live four-mode replay, PM acceptance, merge, and push
remain separate gates.
