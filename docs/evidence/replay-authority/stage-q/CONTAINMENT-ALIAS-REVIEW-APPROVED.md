# GRRR-z3w9 Stage Q containment alias review — approved

Verdict:

```text
STAGE_Q_CONTAINMENT_ALIAS_REVIEW: APPROVED
```

Independent verification:

- Homebrew Python 3.14.3 focused tests: 37/37 passed.
- Miniconda Python 3.12.7 focused tests: 37/37 passed.
- `ResourceWarning` was treated as an error.
- Reviewer ran 40 fully mocked lexical probes per interpreter.
- Zero stat/lstat/fstat calls occurred in the lexical probes.
- Required alias and ancestor cases rejected before metadata:
  - `//Library/GRRR/x`;
  - `//Library/unrelated/x`;
  - `/Library/unrelated/x`;
  - `/Library/GRRR/x`.
- Repeated-leading-slash and entire `/Library`-tree rejection precede
  filesystem metadata calls.
- Symlink rejection, exact SQLite inventory/schema, uncertainty dominance,
  publication-failure preservation, and checkout refusal remain intact.
- Installer, CLI, and test hashes matched the narrow review request.
- Existing concurrent changes were preserved.

No repository files were edited and no protected filesystem access or mutation
occurred during review.

Approval covers only this containment correction—not protected issuance,
staging, installation, budget amendment, reconciliation, replay, admission,
promotion, merge, or push.
