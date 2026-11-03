# Stage Q containment rework — lexical-first sandbox enforcement

## Operator scope

This rework responds to the explicitly authorized revised brief:

- canonicalize and validate paths lexically before any filesystem metadata call;
- reject `..`, absolute escapes, symlinked sandbox roots, symlinked ancestors,
  and every `/Library/GRRR` path without stat/lstat access;
- add syscall-guard tests proving zero protected metadata access.

No `/Library/GRRR` access or mutation, protected staging/installation, budget
amendment, reconciliation, replay, promotion, admission, production mutation,
merge, or push occurred.

## Implementation

`_safe_sandbox_path` now has two strictly ordered phases.

### Phase 1 — pure lexical validation

Before any stat/lstat/open call, it:

1. requires actual absolute `Path` values;
2. enumerates raw path components;
3. rejects any explicit `..` component;
4. lexically normalizes duplicate separators and single-dot components;
5. rejects the filesystem root as a sandbox;
6. rejects normalized paths outside the explicit sandbox root;
7. rejects any protected overlap, including:
   - `/Library/GRRR` itself;
   - every descendant of `/Library/GRRR`;
   - every ancestor such as `/Library` that contains the protected root.

This phase uses only string/path-component operations.

### Phase 2 — real filesystem containment

Only after lexical safety, it:

1. `lstat`s every component from the filesystem root down through the supplied
   sandbox root, rejecting symlinks and non-directories;
2. `lstat`s every component below the sandbox root;
3. requires real directories for ancestors;
4. requires the expected real directory/file type for final components.

Thus a sandbox root beneath a symlinked ancestor is rejected, as are symlinked
source/target ancestors and final components.

## Tests

The protected-path guard wraps `os.stat` and `os.lstat` and fails before
calling either real syscall for `/Library` or `/Library/GRRR`. Therefore a
regression cannot silently turn the test itself into protected metadata
access.

Added or strengthened regressions prove:

- protected root, protected descendant, and protected-ancestor sandbox roots
  reject with zero stat/lstat calls;
- explicit `..` and absolute escapes reject before metadata;
- preflight rejects a protected target before reading source files;
- a sandbox root beneath a symlinked ancestor rejects;
- existing source symlinks still reject;
- successful installation remains inside the explicit real sandbox.

## Verification

- Focused Stage Q installer tests:
  - Homebrew Python 3.14.3: **37/37 passed**.
  - Miniconda Python 3.12.7: **37/37 passed**.
- Full no-guest unit suites:
  - Homebrew Python 3.14.3: **598/598 passed**.
  - Miniconda Python 3.12.7: **598/598 passed**.
- `ResourceWarning` promoted to an error.
- `pvg verify`: PASS.
- `git diff --check`: PASS.

## Boundary statement

The rework constructs protected path strings for lexical rejection only. It
does not stat, lstat, open, read, or mutate `/Library/GRRR`.
