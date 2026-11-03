# GRRR-z3w9 Stage Q narrow rework review — rejected

Verdict:

```text
STAGE_Q_NARROW_REWORK_REVIEW: REJECTED
```

Blocking findings:

1. `_safe_sandbox_path` performs filesystem metadata checks before lexically
   rejecting the protected GRRR root. With `os.stat`/`os.lstat` guarded, the
   protected-root regression fails on both interpreters.
2. A caller can supply `sandbox_root/path/../outside`; lexical containment
   accepts the `..` escape.
3. A sandbox root beneath a symlinked ancestor is accepted because checking
   stops at the supplied root.

Reviewer verification:

- With protected metadata syscalls blocked:
  - Homebrew Python 3.14.3: 33 passed, 1 failed.
  - Miniconda Python 3.12.7: 33 passed, 1 failed.
- Exact SQLite object/DDL inventory, extra-table rejection, uncertainty
  dominance, all publication-failure injections, and checkout refusal passed.
- All 14 checked artifact hashes matched.
- Durability files and checkout CLI remained byte-identical to the initial
  review manifest.

Disclosure:

- The first reviewer guard patched `Path.stat` but Python 3.14 `is_symlink`
  uses `os.lstat` directly, so the first run accidentally allowed metadata
  probes from the repository regression.
- Corrected syscall guards caught the failure.
- No protected content was read and no protected state was mutated.

Per the two-failure Astra escalation rule, no third review of this same brief
is permitted without operator direction.
