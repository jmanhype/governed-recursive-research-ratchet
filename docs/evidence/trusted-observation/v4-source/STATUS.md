# Trusted-observation v4 source revision — no-guest checkpoint

This checkpoint implements the operator-approved source-binding revision only.
It performs no root/sudo operation, protected mutation, accounting migration or
release, QEMU execution, guest execution, delivery, acceptance, or push.

## Bound identities

- v4 prepared profile:
  `a37c2ecff8094f1b52a97d214926b5040dd3afb480c63c617ccc78365b4fc205`
- v4 input ISO:
  `57c48a6845d65b6b3674c80367af42c062cf079d7bbdc4491331a4945375d2b6`
- v4 preparation receipt:
  `3d280af9e69ff05300cb0058194db14995a2d4baf927ef84d24e1199c7e70fa7`
- Retained supervisor:
  `a9a0fd9a8471bc1859e5ab91c3746a139942562f719784fec51b8254eb8307d6`
- Explicit helper:
  `14603a520a8a7d6f460aaa6057097da78e0cdba97a3e620ee8d4fcd3c5b62d2e`
- Installed immutable QEMU manifest:
  `e40888d8d14bc9c2b8db38d8468bc53fdbf77421b284d9eacbbce1d37818b625`

Configuration, approval, and result schemas bind the helper and installed QEMU
manifest. Launch preparation verifies the exact six-member preserved v4
namespace, safe ancestor/file metadata, bytes, and immutable QEMU closure. The
preserved ISO is the detached input path. Legacy v3 profile/image/receipt/QEMU
values and Homebrew paths remain rejected.

## No-guest verification

- `python3 -m unittest discover -s tests -p 'unit*.py' -v`:
  **116 passed, 0 failed, 0 skipped** (`UNIT.txt`).
- Focused `tests/unit_trusted_v4_source.py`: **8 passed, 0 failed, 0 skipped**,
  covering exact v4 shape, v3/Homebrew rejection, helper/QEMU mismatch, absent
  approval, stopped conservative accounting, and temp-fixture metadata,
  membership, symlink, hard-link, mutation, ACL, mode, owner, and size failures.
- Python compilation and `git diff --check`: pass. Explicit-path
  `pvg verify --include-tests`: pass, **4 recognized files, 0 issues**
  (`STATIC.txt`).
- Read-only installed-state check (`READBACK.txt`): all six preserved v4 hashes
  match; immutable QEMU manifest and executable hashes match; SQLite integrity
  is `ok`; conservative accounting remains stopped with zero reservations. QEMU
  and guests were not executed.

Dispatch remains blocked by exact-root-record approval absence and the stopped
conservative accounting state. The ten mandatory guest controls remain not-run;
this is not a runtime, isolation, race, correctness, or admission claim.
