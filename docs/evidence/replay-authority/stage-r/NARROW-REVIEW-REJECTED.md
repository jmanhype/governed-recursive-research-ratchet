# GRRR-z3w9 Stage R narrow rework review — rejected

Verdict:

```text
STAGE_R_NARROW_REWORK_REVIEW: REJECTED
```

Blocking finding:

- `_safe_sandbox_path` now unconditionally `lstat`s the final component.
- A genuinely absent final leaf with `exists=False` raises `FileNotFoundError`.
- The `exists` argument is unused.
- Existing and dangling leaf symlinks are correctly rejected, but controlled
  absence must be accepted.

Reviewer independently verified:

- both focused suites passed 15/15;
- deterministic regeneration matched;
- all nine requested artifact hashes matched;
- all eight role hashes and canonical identity matched;
- existing/dangling leaf symlinks reject;
- root-as-file rejects and root-as-directory passes;
- Stage N/O restrictions, exact stopped/empty SQLite behavior, uncertainty,
  entrypoint refusal, and false authority remain intact;
- no protected access or repository edit occurred.

Required revised correction:

- inspect the final leaf only when it exists;
- accept a genuinely absent final leaf when `exists=False`;
- reject any existing final symlink regardless of `exists`;
- keep root-type validation;
- add a genuine-absence regression;
- regenerate hashes and use a newly scoped review brief.
