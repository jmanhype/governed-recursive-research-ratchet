# GRRR-w1lt no-guest prerequisite evidence

Status: in_progress; independent review, root installation and replay not-run.
No sudo/root, QEMU, VM, paid dispatch, /Library/GRRR mutation, commit push,
contract admission, production change or promotion occurred in this work.

## Commands and measured results

From the story worktree, under both /usr/bin/python3 (3.9.6) and
/opt/homebrew/bin/python3 (3.14.3):

- `PYTHON -B -m unittest discover -s tests -p unit_replay_prerequisites.py -v`:
  18 tests passed, zero failures/errors/skips on each interpreter (review revision).
- `PYTHON -B -m unittest discover -s tests -p 'unit_*.py'`:
  184 tests passed, zero failures/errors/skips on each interpreter (review revision).
- `pvg verify research/replay_prerequisites.py scripts/replay-prerequisites scripts/replay-root-prepare tests/unit_replay_prerequisites.py docs/replay-policy-v1.json docs/REPLAY-PREREQUISITES.md --format=text`:
  passed, 2 files scanned, 0 issues. The scanner does not count extensionless
  scripts; real subprocess tests load both scripts, and the launcher import
  test validates its exact import-closure hashes.
- `git diff --check`: passed.
- `/usr/bin/python3 -B -m trace --count --missing --summary --coverdir /tmp/GRRR-w1lt-coverage --module unittest discover -s tests -p unit_replay_prerequisites.py`:
  Original c1cd13c run: 14 passed; replay_prerequisites.py line coverage 52% (117 executable lines).
  Unexecuted protected-positive paths are intentionally not claimed as proof.
  Coverage.py is not installed on either required interpreter; stdlib trace
  with --missing supplies the reported measurement, not its misleading default
  executed-lines-only denominator.

Exact test outputs are sibling .log files. Test imports/subprocesses are
unprivileged; no mocks, skips or environment gates were added. Synthetic process
inventory parsing cases are unit tests, not live process absence evidence.

## AC verification boundary

| AC | Package evidence | Live status |
|---|---|---|
| 1 | Exact pinned canonical policy, all approved limits/denials/UIDs; leaf-mutation tests | Operator approval recorded in story; policy installation not-run |
| 2 | Root-only preparer, reviewed closure gate, locked preflight, exclusive namespace and UID ownership layout | Independent review and root provisioning not-run |
| 3 | Exact corpus/spec/source/QEMU/VM checks, disk/identity/process/lock and safe-path checks | Positive protected preflight not-run; real unsafe inputs denied |
| 4 | Root-only private records, no inherited environment/service/guest dispatch; downstream lifecycle design | Service/guest replay not-run; no ReplayReceipt |
| 5 | No story acceptance, no ledger relabeling, dispatch disabled and independent gate retained | GRRR-z3w9 remains blocked |

## Observations and learnings

- Literal approved 15 GiB is 16106127360 bytes, not older corpus 15000000000.
- Byte-validation success must never be interpreted as privileged authority.
- Parent retains the same lock descriptor across preflight and namespace effects.
- A partial namespace deliberately blocks retry; no automatic destructive cleanup.
- Worktree vault search returned missing-directory; retry from repository root
  returned no relevant result. No vault configuration was changed.
- The relevant worktree had no codebase-memory index; exact source reads were
  used. No graph completeness claim is made.
- Initial design-only launcher was expanded to executable namespace preparation
  on coordinator request. Service/guest lifecycle remains separate and not-run.

## DISCOVERED_BUG

Independent review blocked the original runtime entrypoint and missing destination
postconditions. This revision replaces the Xcode shim with the audited direct CLT
python3.9 executable and mandatory pre-elevation audit; it also reopens every
created object before publishing the prepared marker. Root-positive behavior
remains an unverified gate, not a passing result.

Real ACL testing then exposed that '+'-only ACL detection can miss macOS ACLs
when xattrs show '@'. Per coordinator direction this revision fixes all such
checks reachable here, including shared trusted_install.immutable and
trusted_execution.protected_bytes, with real file/directory ACL/xattr tests.
The original test failed correctly before this fix. An intermediate full-suite
failure identified that research modules must not access sys.path; runtime import
path validation was moved to the root launcher without changing that test.

Missing coverage.py and worktree-local vault routing remain tooling observations
resolved by stdlib trace and root-context vault search respectively.

See ../../REPLAY-PREREQUISITES.md for the exact future parent command and trusted
installation/review schema. Do not execute checkout code as root.

## Review revision runtime and postcondition evidence

- runtime-identity.json: complete canonical runtime inventory; its bytes minus
  the trailing newline hash to 59073b8282cb4333c7719d4eac417c061c82f534bf11873d26bf2b26f7531526.
- runtime-prelaunch.log: actual unprivileged direct-CLT prelaunch validation,
  explicitly root_launch_authorized=false.
- runtime-native-dependencies.log: /usr/bin/otool -L output for direct python3.9,
  its Python3 framework and all native stdlib modules. The executable's framework
  dependency is relative to its fixed executable path; remaining native loads
  are sealed-system libraries, bound to OS build in the runtime inventory.
- coverage-r2.log: stdlib trace --missing summary for 18 focused tests. This is
  no-guest code coverage only, not root-positive ownership/isolation proof:
  replay_runtime.py 96%, replay_prerequisites.py 52%, root preparer 38%.
- Revision scan command: `pvg verify research/replay_runtime.py research/trusted_install.py research/trusted_execution.py scripts/replay-root-prepare scripts/replay-runtime-preflight tests/unit_replay_prerequisites.py docs/REPLAY-PREREQUISITES.md docs/evidence/replay-prerequisites/README.md --format=text`:
  PASSED, 4 files scanned, zero issues. Extensionless scripts are also imported
  or executed by real no-guest checks; no privileged path was invoked.
- The root preparer requires review.runtime_identity and the trusted parent's
  runtime_prelaunch_verified=true attestation, then repeats the runtime hash
  checks before effects. No review record or approval was fabricated here.
- Destination tests use actual files, ACLs, xattrs, hardlinks and symlinks under
  the current non-root UID. Metadata mismatches and exact byte/inventory drift
  fail closed; no mocked UID or root-positive success claim is used.

Remaining not-run gates: independent re-review, trusted parent installation,
root-positive namespace preparation, UID 320/321 access/denial probes, actual
service/VM lifecycle and independent replay/ReplayReceipt. No root/QEMU/VM or
/Library/GRRR mutation occurred during this revision.
