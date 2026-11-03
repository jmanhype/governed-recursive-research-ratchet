# GRRR-z3w9 Stage Q containment rework review — rejected

Verdict:

```text
STAGE_Q_CONTAINMENT_REWORK_REVIEW: REJECTED
```

Findings:

1. `os.path.normpath` preserves `//`; `Path("//Library/GRRR/x")` with sandbox
   `Path("//Library")` bypassed protected-overlap comparison and reached a
   mocked `lstat("//Library")`.
2. A sandbox under `/Library/unrelated` passed the prior `/Library/GRRR`
   subtree-only lexical check, then root-chain validation attempted
   `lstat("/Library")`.

The reviewer replaced all stat/lstat calls; no real protected metadata access
occurred. All other focused suites and temporary containment probes passed.

The correction rejects repeated leading-root spellings before normalization and
rejects the entire `/Library` tree before any metadata call.
