# Trusted-observation v4 recovery candidate — execution not authorized

## Correction and classification

The exact retained v3 input-ISO hash is:

`799ec744f27e7329686e5acb8a3e1f663c82a321f7bc1d4bc940ea5c97068233`

Earlier recovery prose transcribed that retained hash incorrectly. This is a
reporting correction only: the committed v3 receipt and profile remain
authoritative and were never modified.

The first recovery attempt correctly stopped as an exact-v3 mismatch. Parent
verification then confirmed the recovered supervisor/helper, the recovered
receipt bound to its own anchor, and repeated `hdiutil` nondeterminism in ISO
container metadata/timestamps. Accordingly, the recovered output is classified
as a **new v4 recovery candidate**, not an exact v3 container recovery.

The historical output directory remains
`<main-repo>/.tmp-sr_pm/trusted-observation/prepared-v3-recovery` so the failed
exact-v3 attempt is not rewritten. Its durable location outside story worktrees
is intentional. No binary or ISO asset is committed to this branch.

## Candidate identities

| Artifact | SHA-256 |
|---|---|
| v4 supervisor | `a9a0fd9a8471bc1859e5ab91c3746a139942562f719784fec51b8254eb8307d6` |
| v4 helper | `14603a520a8a7d6f460aaa6057097da78e0cdba97a3e620ee8d4fcd3c5b62d2e` |
| v4 input ISO | `57c48a6845d65b6b3674c80367af42c062cf079d7bbdc4491331a4945375d2b6` |
| v4 prepared profile | `a37c2ecff8094f1b52a97d214926b5040dd3afb480c63c617ccc78365b4fc205` |
| v4 preparation receipt | `3d280af9e69ff05300cb0058194db14995a2d4baf927ef84d24e1199c7e70fa7` |
| Development binding, unchanged from v3 | `9fd432900036552fcdeb95ed1433937e01fbc45b73250aba91f6ed87a0efc209` |

## Direct v3/v4 comparison

A direct read-only comparison of the committed v3 receipt/profile against the
recovered v4 receipt/profile proved these mappings exactly equal:

- all seven primary ISO9660 payload records, including bytes and SHA-256;
- the complete 52-file vlt source inventory, per-file hashes, blob IDs, modes,
  and canonical inventory digest
  `3c43f236b2f3bc86e1fcd8c634c88ecd119a759458fc3f7b3580dda46271a487`;
- supervisor and helper executable identity records and byte hashes;
- Go archive SHA-256
  `3f4227ce7b206a513e794f1393adb473a07b46e94d18bd15d1c684bbb7319797`;
- guest script SHA-256
  `8738b78aed326c02ce95640765b103618565b5e8f90f97442b54ebc79c73b6eb`;
- shared Alpine/kernel/initramfs/QEMU hashes;
- compiler version/binary/license provenance;
- development binding;
- every profile field except `input_image_sha256`, including all resource,
  timeout, UID/GID, networking, sharing, paid-dispatch, output, IPC, workspace,
  and dispatch-disable limits.

Both ISOs are exactly 71,483,392 bytes. The container hash nevertheless differs
despite identical inventoried payload bytes. A same-media `hdiutil` diagnostic
reproduced different container hashes and timestamp-bearing metadata bytes, but
the original v3 container is unavailable, so that diagnostic does not prove that
every v3/v4 container difference is metadata. Such causation remains inferred;
payload equality does not make the v4 container byte-identical to v3.

The only top-level receipt/context differences are:

1. `commands`: v3 used the former story-worktree output path; v4 writes to the
   main checkout's durable ignored recovery path. Compiler, source paths, and
   build flags are otherwise identical.
2. `initial_free_bytes`: v3 `15213449216`; v4 `34560266240`.
3. `final_free_bytes`: v3 `15132168192`; v4 `34422800384`.
4. `image_sha256`: retained v3
   `799ec744f27e7329686e5acb8a3e1f663c82a321f7bc1d4bc940ea5c97068233`;
   v4 `57c48a6845d65b6b3674c80367af42c062cf079d7bbdc4491331a4945375d2b6`.
5. `profile_sha256`: retained v3
   `3edebcd4b85ae7ce666d953bd3c5527606a7043c42294a0f60000875f8d2eec0`;
   v4 `a37c2ecff8094f1b52a97d214926b5040dd3afb480c63c617ccc78365b4fc205`.

The recovered receipt necessarily has a new hash because it embeds those image,
profile, command-path, and free-space values. Binding verification therefore
uses the recovered anchor
`3d280af9e69ff05300cb0058194db14995a2d4baf927ef84d24e1199c7e70fa7`.

## Boundary

This is preparation and static/unit evidence only. No QEMU, guest, supervisor,
helper, candidate, or vlt code was executed. No root/sudo, protected accounting
mutation, paid call, resource increase, push, execution-approval request, or
story AC success claim is made. `dispatch_enabled` remains false.
