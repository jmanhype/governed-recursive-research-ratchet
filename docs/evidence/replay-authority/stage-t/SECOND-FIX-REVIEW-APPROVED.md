# Stage T second-rejection-fix review — approved

## Scope

Differently scoped review of only the three fixes from the second Stage T
rejection, following operator direction after the two-rejection escalation.

## Second rejection findings and corrections

1. **Destination traversal** — `posixpath.normpath` plus traversal,
   subdirectory, unnormalized, and empty-remainder rejection.
2. **Relative-path symlink bypass** — absolute paths required in both
   `check_no_symlink_ancestors` and the staging script.
3. **Write verification regression** — `os.write` return length checked;
   destination bytes read back and hash + size verified.

## Independent verification

```text
STAGE_T_SECOND_FIX_REVIEW: APPROVED
```

Reviewer independently:

- injected traversal, subdirectory, `//`, and empty-remainder destinations:
  all rejected;
- confirmed relative-path ancestor check raises and CLI exits 1;
- mocked short-write, hash-mismatch, and size-mismatch probes: all raised;
- ran 35/35 focused tests on both interpreters;
- verified all source hashes and the 10-member package:
  `2146c99d3e8af2d9821c69d00e3b0f381c72aabd6fc31e3b5f7713c83720e182`.

## Boundary

This approval covers only the three second-rejection fixes. It does not
approve protected staging execution, installation, budget amendment,
reconciliation, replay, admission, promotion, merge, or push.
