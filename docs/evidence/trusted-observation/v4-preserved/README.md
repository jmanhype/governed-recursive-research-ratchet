# Trusted-observation v4 preserved — execution still unauthorized

This records the operator-authorized root-controlled preservation performed at
independently reviewed plan commit `1957ab3478c67cd6082e92e3e67da35e4457e644`.
It is not source implementation, accounting migration, guest execution, or an
execution approval.

## Preserved namespace

`/Library/GRRR/trusted-observation/v4/` contains exactly six members:

- `input.iso`
- `preparation.json`
- `prepared-profile.json`
- `development-binding.json`
- `supervisor`
- `helper`

The preserved directories are `root:wheel` mode `0755`. Every preserved regular
file is `root:wheel` mode `0444`, a single-link regular file, ACL-free, and
byte-identical to its reviewed v4 source. Exact hashes, byte counts, device and
inode identities are machine-generated in `READBACK.json`.

The private staging root
`/Library/GRRR/.grrr-v4-preservation-stage-1957ab3` remains `root:wheel` mode
`0700` and is empty. It is retained as a forensic marker, not a second active
namespace.

## Installer boundary

The independently reviewed installer was first placed at:

`/Library/GRRR/bootstrap/install-v4-preservation-1957ab3`

Its installed bytes are `root:wheel` mode `0444`, single-link, ACL-free, and
SHA-256:

`0044e034e21921cb09032e27b33e4a013f71540dc83deed21180d766f961deba`

Only that protected copy was invoked as root, using the canonical CLT Python
with `-I -S -B` in an empty environment. The installer required its protected
path, verified safe ancestors, staged all six bytes privately, and published
the final namespace using Darwin `renamex_np` with `RENAME_EXCL` and
`RENAME_NOFOLLOW_ANY`.

## Verified boundaries

- Protected immutable QEMU bytes were read and hashed only; QEMU was not executed.
- Conservative accounting was read only; it remains integrity `ok`, stopped,
  with zero reservations and all 259 artifacts.
- `execution_authorized` is false.
- `dispatch_enabled` is false.
- No source revision or runtime claim is made.
- Current `research/trusted_execution.py` remains v3-only and cannot consume v4.
- Accounting history remains ambiguous and must not be released or converted to
  a fresh allowance.

The next mandatory gates are a reviewed v4 source revision, accounting-history
resolution or reviewed migration, and separate exact execution approval.
