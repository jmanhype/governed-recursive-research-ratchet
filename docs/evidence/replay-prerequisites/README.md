# GRRR-w1lt no-guest prerequisite evidence

Status: in_progress; independent review, root installation and replay not-run.
No sudo/root, QEMU, VM, paid dispatch, /Library/GRRR mutation, commit push,
contract admission, production change or promotion occurred in this work.

## Commands and measured results

From the story worktree, under both /usr/bin/python3 (3.9.6) and
/opt/homebrew/bin/python3 (3.14.3):

- `PYTHON -B -m unittest discover -s tests -p unit_replay_prerequisites.py -v`:
  14 tests passed, zero failures/errors/skips on each interpreter.
- `PYTHON -B -m unittest discover -s tests -p 'unit_*.py'`:
  180 tests passed, zero failures/errors/skips on each interpreter.
- `pvg verify research/replay_prerequisites.py scripts/replay-prerequisites scripts/replay-root-prepare tests/unit_replay_prerequisites.py docs/replay-policy-v1.json docs/REPLAY-PREREQUISITES.md --format=text`:
  passed, 2 files scanned, 0 issues. The scanner does not count extensionless
  scripts; real subprocess tests load both scripts, and the launcher import
  test validates its exact import-closure hashes.
- `git diff --check`: passed.
- `/usr/bin/python3 -B -m trace --count --missing --summary --coverdir /tmp/GRRR-w1lt-coverage --module unittest discover -s tests -p unit_replay_prerequisites.py`:
  14 passed; replay_prerequisites.py line coverage 52% (117 executable lines).
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

None in delivered code known from these no-guest checks. Missing coverage.py and
worktree-local vault routing are tooling observations resolved by stdlib trace
and root-context vault search respectively. Root-positive behavior remains an
unverified gate, not a passing result.

See ../../REPLAY-PREREQUISITES.md for the exact future parent command and trusted
installation/review schema. Do not execute checkout code as root.
