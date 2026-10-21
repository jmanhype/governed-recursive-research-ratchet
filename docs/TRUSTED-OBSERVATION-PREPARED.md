# Trusted-observation development checkpoint — execution not authorized

Implementation basis: `98c8af1` on `story/GRRR-gu87`. This supersedes the
preliminary v2 binary/image pins, **not** the original approved development
proposal. The v2 evidence and assets remain preserved.

## Prepared pins

| Artifact | SHA-256 |
|---|---|
| Original development proposal | `1830a92ad2cbd91788051304ec8f6acaebf256b85065b2db2c07271b6906e3f6` |
| Supervisor executable, static Linux/arm64 ELF, 3,991,473 bytes | `a9a0fd9a8471bc1859e5ab91c3746a139942562f719784fec51b8254eb8307d6` |
| Supervisor Linux source | `b5382ea1a87a76401b7ec68961991405578603e68dcd204f8ad1930ee17ed259` |
| Separate candidate helper executable | `14603a520a8a7d6f460aaa6057097da78e0cdba97a3e620ee8d4fcd3c5b62d2e` |
| Guest bootstrap | `8738b78aed326c02ce95640765b103618565b5e8f90f97442b54ebc79c73b6eb` |
| Detached input ISO | `799ec744f27e7329686e5acb8a3e1f663c82a321f7bc1d4bc940ea5c97068233` |
| Prepared profile, still dispatch-disabled | `3edebcd4b85ae7ce666d953bd3c5527606a7043c42294a0f60000875f8d2eec0` |
| Development-only binding | `9fd432900036552fcdeb95ed1433937e01fbc45b73250aba91f6ed87a0efc209` |
| Independently retained preparation receipt | `775a767ca74f9c18678fc998111b0c9870df1a68db68e453b6af0c50ae9d6c0c` |

Bulk assets remain **ignored and local**, in
`.tmp-sr_pm/trusted-observation/prepared-v3/`. Do not remove this worktree before
the dispatcher preserves them. Committed JSON evidence is in
`docs/evidence/trusted-observation/prepared-v3/`; it is not a substitute for the
actual ISO/binaries.

## Resource and identity boundaries

The original profile remains byte-identical. Limits: 1024 MiB RAM, 1 vCPU,
512 MiB `/work`, 30s boot, 240s command, 300s invocation, 2s stop-ack target,
5s TERM grace, 2s force-kill/cessation wait, 1 MiB guest output, 3 MiB IPC,
15 GB host free-space floor. Network, host shares and paid calls remain disabled.
The existing synthetic 512 MiB and offline 1024/512 MiB profiles are unchanged.

Host evaluator/executor remain UID 320/321. Guest supervisor is UID 0;
candidate UID/GID is 1000/1000, empty supplementary groups. The locked launching
thread sets no-new-privileges and drops the capability bounding set; credential
drop removes effective/permitted capabilities. Supervisor checks the candidate's
actual `/proc/PID/status`, not candidate-provided role metadata.

The original read-only input mount moves under root-only `/root` before candidate
launch. Supervisor/expectations live in root-only `/work/control`; candidate
receives `/dev/null` stdin, captured data pipes, a detached session, and no extra
control descriptors. Console and input block devices are root-only. The separate
helper attempts read/write/replacement/signal and control impersonation; its
bytes are data and do not become verdicts.

Supervisor owns the flock, sticky root-owned vault lock inode, hold/release
schedule, `/proc/locks` observation and no-follow artifact read. This is a bounded
schedule observation, **not exhaustive race freedom**. No permission, capability,
race, stop or isolation assertion is considered demonstrated until real guest
execution and independent evaluation.

## Restored inputs and compiler provenance

- vlt commit: `129e0b3f15a3bd6af949ee47d76f6855c582ab73`; 52 source files verified
  against Git and tar read-back. License blob:
  `c004659349c7a1f6c55e5107b53a0766085e8d2e`.
- Pinned guest Go archive:
  `3f4227ce7b206a513e794f1393adb473a07b46e94d18bd15d1c684bbb7319797`.
  Archive transport uses APFS clonefile, with no fallback full copy.
- Existing Alpine/kernel/initramfs/QEMU inputs were rehashed; exact values are
  in the preparation receipt and match the proposal.
- **Trusted supervisor/helper only** were cross-compiled using host Go 1.26.7,
  compiler SHA `e670dfa79b080bad7f7d6b1d7131145c8c49068096650ebf0ac6292f098db60d`.
  Compiler license text/hash is retained. This new compiler provenance needs
  independent local-use compliance/security review before execution approval.
- Target vlt was **not** built or executed on host. Its build remains guest-only
  with pinned Go 1.26.10. Generated Linux binaries were never executed here.
- Free space after v3 preparation: **15,132,168,192 bytes**. Subsequent shared-host
  changes can reduce this; launch must measure again.

## Verification performed

Commands were synchronous; full logs are committed in the v3 evidence directory.

1. `python3 scripts/prepare-trusted-observation
   .tmp-sr_pm/trusted-observation/source
   .tmp-sr_pm/trusted-observation/go1.26.10.linux-arm64.tar.gz
   ../../../.tmp-sr_pm/vm .tmp-sr_pm/trusted-observation/prepared-v3`
   — exit 0. Actual ELF headers verified static AArch64; all **7 ISO files**
   read back through the primary ISO9660 namespace and byte-hashed.
2. `python3 scripts/verify-trusted-preparation
   .tmp-sr_pm/trusted-observation/prepared-v3
   775a767ca74f9c18678fc998111b0c9870df1a68db68e453b6af0c50ae9d6c0c`
   — exit 0. Reverified binaries/image/profile/source against retained receipt.
3. `go test -count=1 -v -coverprofile=... protocol.go protocol_test.go` —
   **2 passed, 0 failed**, protocol statement coverage **90.6%**. This runs only
   the pure protocol parser on host, not supervisor/helper/candidate code.
4. Linux/arm64 `go vet` on supervisor+protocol and separately helper — both exit 0.
5. `python3 -m unittest discover -s tests -p 'unit*.py' -v` —
   **50 passed, 0 failed, 0 skipped**.
6. Python `coverage --source=research`: **37% overall**, budget 99%,
   observation 98%, evaluator 0%. Linux supervisor guest execution coverage is
   **0%**; parser coverage must not be presented as supervisor coverage.
7. Explicit-path `pvg verify --include-tests --format=text` —
   **12 recognized files, 0 issues**. `sh -n`, gofmt and `git diff --check` pass.
8. `./scripts/test-story trusted-observation` — **exit 1**:
   10 required, 1 executed, 2 prerequisite errors, 0 skips. No integrated pass.

Earlier preparation failures are preserved: insufficient reserved disk headroom,
then v1's incorrect Homebrew license location. v2 completed; v3 superseded it to
honor TERM grace rather than immediate timeout kill. No failed attempt was
rewritten as success.

## Remaining mandatory work and approval

**Historical checkpoint statement (91a7ad5), not current availability:**
No dedicated trusted-profile host dispatch adapter/root identity launcher exists
yet. Existing synthetic/offline launchers **must not** be repurposed to run this
image. They are not a valid `AWAITING_PARENT_IDENTITY_RUN` command for this profile.
Finish and independently review that adapter, strict evaluator schema/expected
results, root-controlled execution-approval binding, and real integration cases.
All six story ACs remain incomplete end to end; claim remains in progress.

**Current status:** a dedicated adapter/launcher was subsequently staged at
`87a8766`/`d53deaf`, then independent security review required changes to persistent
accounting, IPC control availability, executable binding and bootstrap trust.
The later security-fix checkpoint supersedes the execution instructions below.
Do not execute a checkout launcher as root or request guest execution before
that review and missing root-controlled prerequisites are resolved.

Recommended operator authorization, **after** adapter/security/license review:

> I approve parent-mediated restricted-identity execution, for evidence review
> only, of prepared profile
> `3edebcd4b85ae7ce666d953bd3c5527606a7043c42294a0f60000875f8d2eec0`,
> supervisor
> `a9a0fd9a8471bc1859e5ab91c3746a139942562f719784fec51b8254eb8307d6`,
> helper
> `14603a520a8a7d6f460aaa6057097da78e0cdba97a3e620ee8d4fcd3c5b62d2e`,
> and input image
> `799ec744f27e7329686e5acb8a3e1f663c82a321f7bc1d4bc940ea5c97068233`,
> with the exact original proposal limits and reviewed compiler provenance.
> Run only fixed registered controls through the reviewed trusted-profile
> adapter. Stop on missing prerequisites, unknown outcomes or exceeded limits.
> No resource increase, paid call, host fallback, production mutation or
> automatic admission is authorized. This approval does not certify candidate
> correctness, isolation, race freedom or any resulting finding.

The diff now exceeds the story's approximate 7-file/1,400-line guideline because
the separate supervisor, preparation/verifier and evidence were added. This is
explicitly referred to PM investigation; it is not hidden as a completed story.
