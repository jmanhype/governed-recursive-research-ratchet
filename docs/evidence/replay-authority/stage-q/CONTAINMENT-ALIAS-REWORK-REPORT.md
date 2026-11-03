# Stage Q containment alias rework — correction after revised-brief rejection

## Scope

This correction addresses the two findings from
`STAGE_Q_CONTAINMENT_REWORK_REVIEW: REJECTED`:

1. repeated leading slashes such as `//Library` bypassed literal protected-root
   comparisons;
2. a sandbox under unrelated `/Library/...` could pass protected-subtree checks
   and then `lstat("/Library")` during root-ancestor traversal.

No `/Library` or `/Library/GRRR` stat, lstat, open, read, or mutation occurred.

## Corrections

The lexical phase now rejects repeated leading-root separators before
`os.path.normpath` is called. `//Library`, `//Library/GRRR`, and equivalent
noncanonical root spellings cannot reach metadata access.

The protected lexical boundary is now the entire `/Library` tree, not only the
`/Library/GRRR` descendant subtree. Therefore `/Library/unrelated`,
`/Library/unrelated/x`, `/Library`, and `/Library/GRRR/...` are all rejected
before any root-ancestor `lstat`.

The test syscall guard also fails before real stat/lstat for:

- repeated leading-root paths;
- `/Library`;
- every `/Library/...` descendant.

Thus even a future regression cannot turn the test into protected ancestor
metadata access.

## Verification

- Stage Q focused installer tests:
  - Homebrew Python 3.14.3: **37/37 passed**.
  - Miniconda Python 3.12.7: **37/37 passed**.
- Full no-guest unit suites:
  - Homebrew Python 3.14.3: **598/598 passed**.
  - Miniconda Python 3.12.7: **598/598 passed**.
- `ResourceWarning` promoted to an error.
- `pvg verify`: PASS.
- `git diff --check`: PASS.

## Remaining boundary

Fresh alias retry review returned:

```text
STAGE_Q_CONTAINMENT_ALIAS_REVIEW: APPROVED
```

The reviewer independently reran 37/37 focused tests on both interpreters and
40 fully mocked lexical probes per interpreter with zero stat/lstat/fstat calls.
The approval covers only this containment correction. It does not authorize
protected source issuance, staging, installation, budget amendment,
reconciliation, replay, admission, promotion, merge, or push.
