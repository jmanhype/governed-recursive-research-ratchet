REVIEW_RESULT: APPROVED

# Independent source-only security re-review R2

Base HEAD verified: `5f6ce4e83e2426e859127af568aa730c19dc6a9b`.
Exact-source fallback; no graph coverage claimed. `docs/findings/` absent.
Read retained R1 review SHA256
`575a0889134228046d091c4d654cefa9c28cad710a119155a719bf19c226ced5`.

## Reviewed SHA256s

- `research/fresh_replay_runtime.py`: `06607ef64574329ba0e989a9d4fbcfeef859b6a5458035a22127b78618874958`
- `tests/unit_capstone_fresh_replay_runtime.py`: `47cd16ca28286444cd7fd1abba1187e99420d48ae2fffbc5df496522ec21a48f`
- `tests/unit_capstone_backend_suite.py`: `07e3d0521cdd631c9111da63a054fac579cb90f05da3e6f24c6af6d07bb1f6f4`
- `docs/FRESH-REPLAY-RUNTIME-WIP.md`: `e48e38d3d01d11b0eb62d0df1815313fc87b4ab6cba23f496a2d8cbb65dd28ee`

Read `common.py` for helper semantics only. No concrete blocking finding remains
in this bounded source review. R1 F1 is closed: external expected hash is exact
`str`; request and complete fixture evidence undergo recursive exact-JSON-type
validation before comparisons or I/O. Frozen Proposal construction rejects
mutable bytes and subclassed bytes/hash fields; validation compares against a
fresh canonical proposal, not caller equality hooks.

The supplied tests independently exercise external expected-hash rejection and
changed real source fixture evidence rejection. Their setup now succeeds and
15 tests run, rather than treating setup errors as rejection proof. The supplied
list-subclass case also includes a spoof digest; the independent probe below
isolates the list subclass with otherwise valid evidence to avoid that ambiguity.

## Execution

Working directory: story worktree `dev-GRRR-734u`.

```sh
/usr/bin/sandbox-exec -p '(version 1)(allow default)(deny file-read* file-write* (subpath "/Library/GRRR"))' /opt/homebrew/bin/python3.14 -B tests/unit_capstone_fresh_replay_runtime.py
```

Measured: exit 0; 15 tests passed, no failures/errors/skips. Real fixture files
and SQLite bytes/inodes are checked, with a separate read-only ledger query.
The protected-link test opens only the local symlink NOFOLLOW, observes ELOOP,
and never probes the protected destination. Invalid-path tests guard syscalls.

Independent probe command (script retained below, no separate script artifact):

```sh
sed -n '/^```python$/,/^```$/p' docs/evidence/fresh-replay-runtime/r2-review.md | sed '1d;$d' | /usr/bin/sandbox-exec -p '(version 1)(allow default)(deny file-read* file-write* (subpath "/Library/GRRR"))' /opt/homebrew/bin/python3.14 -B /dev/stdin
```

Measured: exit 0; 14 independent boundary checks passed. Output:

```text
R2 independent boundary checks passed: 14
Changed real fixture rejected; accounting bytes and inode unchanged
```

```python
import copy
import sys
from contextlib import ExitStack
from unittest.mock import patch
sys.path[:0] = ['research', 'tests']
from common import Failure, digest
from fresh_replay_runtime import Proposal, prepare, validate_proposal, fixture_preflight
from unit_capstone_fresh_replay_runtime import FreshRuntimeTests, SpoofDigest, SubclassDict, SubclassList

class SubclassBytes(bytes):
    pass

case = FreshRuntimeTests('test_canonical_immutable_hashes')
case.setUp()
count = 0
def reject(label, action, expected_message):
    global count
    with ExitStack() as stack:
        for name in ('os.open', 'builtins.open', 'os.stat', 'os.lstat'):
            stack.enter_context(patch(name, side_effect=AssertionError('unexpected I/O: ' + name)))
        try:
            action()
        except Failure as exc:
            assert exc.record['code'] == 'InvalidInput', exc.record
            assert str(exc) == expected_message, (label, str(exc))
        else:
            raise AssertionError('accepted: ' + label)
    count += 1

try:
    actual = case.request_hash()
    assert actual != '0' * 64
    good = prepare(case.request, actual)
    for value in (SpoofDigest('0' * 64), SpoofDigest(actual)):
        reject('prepare expected hash', lambda: prepare(case.request, value), 'Expected request digest')
        reject('validate expected hash', lambda: validate_proposal(good, case.request, value), 'Expected request digest')
        reject('fixture expected hash', lambda: fixture_preflight(case.request, value,
            sandbox=str(case.root), target=str(case.root / ('replay-' + 'a' * 32)),
            evidence=case.evidence), 'Expected request digest')
    (case.root / 'source').write_bytes(b'R2 changed real fixture')
    assert digest((case.root / 'source').read_bytes()) != case.evidence['source']['sha256']
    attacks = [SubclassDict(copy.deepcopy(case.evidence))]
    entry_subclass = copy.deepcopy(case.evidence)
    entry_subclass['source'] = SubclassDict(entry_subclass['source'])
    attacks.append(entry_subclass)
    for field, value in (('sha256', SpoofDigest('0' * 64)),
                         ('path', SubclassList([case.evidence['source']['path']]))):
        evidence = copy.deepcopy(case.evidence)
        evidence['source'][field] = value
        attacks.append(evidence)
    for evidence in attacks:
        reject('independent evidence subclass', lambda: case.run_fixture(evidence=evidence), 'Noncanonical value')
    evidence = copy.deepcopy(case.evidence)
    evidence['source'][1] = 'nonstring key'
    reject('nested nonstring key', lambda: case.run_fixture(evidence=evidence), 'Non-string key')
    for value in (bytearray(good.canonical_bytes), SubclassBytes(good.canonical_bytes)):
        reject('Proposal bytes', lambda: Proposal(value, good.sha256), 'Canonical bytes')
    reject('Proposal digest', lambda: Proposal(good.canonical_bytes, SpoofDigest(good.sha256)), 'Proposal digest')
    assert case.snapshot()['accounting'] == case.before['accounting']
    print('R2 independent boundary checks passed:', count)
    print('Changed real fixture rejected; accounting bytes and inode unchanged')
finally:
    case.doCleanups()
```

## Invariants and limits

Canonical digest/identity bindings, pinned v4 receipt, verbatim unknowns/holds,
and consumed predecessor as provenance only are unchanged. Namespace inventory
and absence remain archival claims. Five authorizations are false and all eleven
common gates are not-run; status is prepared_not_issued, with no accounting or
spendability action. Pure preparation contains no I/O. All fixture paths are
lexically validated before metadata; descriptor-relative NOFOLLOW traversal,
regular-file/link-count/size checks, and target absence checks remain intact.

This approval is ONLY for reviewed source under caller-owned quiescent
`/private/tmp` fixtures. It does not establish hostile-rename safety, live
freshness, trusted evidence origin, runtime installation or production authority.
Lifecycle docs correctly defer to Git and retained reviews: commit is not
runtime qualification or PM acceptance. Full backend/cross-version execution
is not claimed by this reviewer. No protected metadata access, network,
credentials, implementation/test changes, tracker transition, provisioning,
reconciliation, replay, promotion/admission, commit, merge or push performed.
