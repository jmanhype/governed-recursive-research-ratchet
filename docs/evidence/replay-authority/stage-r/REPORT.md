# Stage R exact v4 protected-source issuance package — prepared, not issued

## Operator scope

Stage R prepares an exact repository-retained source package for future v4
protected issuance. It does not access or mutate `/Library/GRRR`, stage or
install protected records, amend the budget, reconcile, execute replay, promote,
admit, mutate production, merge, or push.

## Exact role closure

The package contains the eight roles required by Stage P:

1. installer entrypoint;
2. v4 store schema;
3. Stage N contract;
4. Stage O runtime adapter;
5. protected preflight;
6. atomic publisher;
7. postflight verifier;
8. failure preservation.

The source identity map is:

| Role | SHA-256 |
|---|---|
| installer-entrypoint | `94b37112fc3b3146078b6edd0cf80d5e845f1cc83543344d79400d144d453dbc` |
| v4-store-schema | `629c6a70936fb94ea4b4a89b4dc3c94095aa2586194c077e4c06258b2c7ce644` |
| stage-n-contract | `d2105c6fbab6edd42ad9724e6ff2313d2531c11af14625bfb0cf8a81b9646fb5` |
| stage-o-runtime-adapter | `f54f051684dd9be4ccf635d3029cb1f099ddb227e8d763efad2c8bf24e3478c4` |
| protected-preflight | `8a288bf13c2ccfffb695fdc350b28b1d99e5a368e8ceb070fcd1c69b82983171` |
| atomic-publisher | `c448f4853e6bb9467c6994b64b3f04dfd9ee9c6d0718de69529eb24218e5a719` |
| postflight-verifier | `f276c0bd84a4fe43d5661672600734120af1332c45c372fc6881a2913491ca46` |
| failure-preservation | `8fb37a74e96c7fab7f96fed74ad1aea187fc306716ebb024a1cd0059ca9ded47` |

All eight hashes are distinct.

## Package identities

- Story basis: `23fdac5fcdc9bcef5147314a8f3c8bcb6d458d3f`
- Stage P package:
  `ba7e8a45486a21ff399027821d3b0bd1d21c6577730597f900f3c21fb192c0b1`
- Stage Q package:
  `d953651c0bd635a1e80295376665fd2331b86ac9b5f25f726b945bcf9e41fb3e`
- Canonical role identity digest:
  `2fc2821d0301718e94072f46094b959131598c7233b158dead64fb7a0b46cbff`
- Generated `SOURCE-BUNDLE.json` SHA-256:
  `38cc6f7904cf130e616772c98d1b526785763871dd6f498d1f02bb8af916e4e4`

The bundle decision remains `prepared-not-issued`. Operator issuance and
protected staging are explicitly `not-run`.

## Source role functionality

The retained source modules were exercised in temporary sandboxes:

- the entrypoint refuses exact live-install grammar;
- the Stage N contract preserves unresolved predecessor history, all encumbered
  ceilings, and three exact unresolved holds;
- the Stage O adapter remains uninstalled and blocks replay;
- protected preflight rejects `/Library`, `/Library/GRRR`, repeated leading
  roots, `..`, absolute escapes, and symlinks before protected metadata access;
- absent-target validation now checks the leaf too, so an existing symlink is
  rejected even when the expected target does not yet exist, and the sandbox
  root cannot be misclassified as a file target;
- store creation creates a stopped empty v4 database;
- atomic publication uses exclusive no-follow writes and fsync;
- postflight verifies exact SQLite objects, DDL, identity, stopped state, and
  empty accounting rows;
- failure preservation writes uncertainty-dominant evidence.

## Verification

- Initial independent review rejected an existing leaf symlink accepted with
  `exists=False` and a sandbox root accepted as a file target; both are corrected
  with regressions.
- Stage R focused tests after correction:
  - Homebrew Python 3.14.3: 15/15 passed.
  - Miniconda Python 3.12.7: 15/15 passed.
- Full no-guest unit suites after correction:
  - Homebrew Python 3.14.3: 613/613 passed.
  - Miniconda Python 3.12.7: 613/613 passed.
- Deterministic source-bundle emission: byte-identical.
- `pvg verify`: PASS.
- `git diff --check`: PASS.

## Remaining gates

The initial independent review is rejected and preserved. The one permitted
narrow retry was also rejected:

```text
STAGE_R_NARROW_REWORK_REVIEW: REJECTED
```

The correction now rejects existing leaf symlinks and root-as-file cases, but
it unconditionally calls `lstat` on a genuinely absent final leaf. With
`exists=False`, this raises `FileNotFoundError`; controlled absence should be
accepted while any existing leaf symlink remains rejected. The `exists` argument
is currently unused.

Per the two-rejection escalation rule, no third review of this same Stage R
brief is permitted without operator direction. Even approval would cover only
the prepared source
package. Operator issuance, protected staging, installation, postflight, budget
amendment, reconciliation, replay authorization, live four-mode replay, PM
acceptance, merge, and push remain separate gates.
