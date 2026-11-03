# Stage R absent-leaf rework — revised preflight behavior

## Operator scope

This rework responds to the operator-authorized revised brief:

- accept a genuinely absent final leaf when `exists=False`;
- reject every existing final symlink, including dangling symlinks;
- retain sandbox-root-as-file rejection;
- add true absent-leaf regressions;
- refresh exact source/package hashes;
- preserve all already reviewed Stage R semantics.

No `/Library/GRRR` access or mutation, protected staging/installation, budget
amendment, reconciliation, replay, promotion, admission, production mutation,
merge, or push occurred.

## Correction

The final path component is now inspected with `lstat`:

- `FileNotFoundError` is accepted only for the final component and only when
  `exists=False`;
- every existing final component is still inspected;
- an existing symlink is rejected before type checking, including dangling
  symlinks;
- intermediate absence remains an error;
- the sandbox root cannot be misclassified as a file target;
- the sandbox root cannot be declared absent.

This restores controlled absence without reopening the leaf-symlink bypass.

## Regressions

The suite now covers:

- a genuinely absent directory target with `exists=False`;
- a genuinely absent file target with `exists=False`;
- an existing directory symlink with `exists=False`;
- a dangling final symlink with `exists=False`;
- sandbox-root-as-file rejection;
- sandbox-root-as-absent rejection;
- all prior protected lexical cases.

## Verification

- Stage R focused tests:
  - Homebrew Python 3.14.3: **16/16 passed**.
  - Miniconda Python 3.12.7: **16/16 passed**.
- Full no-guest unit suites:
  - Homebrew Python 3.14.3: **614/614 passed**.
  - Miniconda Python 3.12.7: **614/614 passed**.
- Deterministic `SOURCE-BUNDLE.json` regeneration: byte-identical.
- `pvg verify`: PASS.
- `git diff --check`: PASS.

## Refreshed identities

- Builder:
  `8a71e1d5020bafb75236d81abdf0bc79a2c236422a6c3c11ed43900fe7d755b4`
- Tests:
  `e9aac58ccf0d0ad0f2e483cb0335d4eadaa1ffebefc929df17a1adb19f08b759`
- Protected-preflight source:
  `0e09ccc6f995e24ab983489755df6a14028c154a99b84811b95d6ea95bf0946f`
- Generated `SOURCE-BUNDLE.json`:
  `31cb9b8ee538ac22553927fe5f8006c47461073578f9d025f3ddb892ed3ca84c`
- Canonical role identity:
  `b6354127a7552b628506c25dc7eee27c8ecb371f56bf565a63dd247b31445084`

## Boundary

Fresh differently scoped review returned:

```text
STAGE_R_ABSENT_LEAF_REVIEW: APPROVED
```

The reviewer independently reproduced both 16/16 focused suites, deterministic
bundle bytes, all requested hashes, and temporary-only absent/symlink/root
probes. The source package remains `prepared-not-issued`. Operator issuance,
protected staging, installation, budget amendment, reconciliation, replay,
admission, promotion, merge, and push remain unauthorized and not-run.
