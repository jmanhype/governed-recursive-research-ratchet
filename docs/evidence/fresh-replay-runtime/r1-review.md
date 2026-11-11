REVIEW_RESULT: REJECTED

# Independent source-only security review R1

Base: `5f6ce4e83e2426e859127af568aa730c19dc6a9b` (HEAD verified).
Exact-source fallback; no current graph coverage claimed. `docs/findings/` absent.

## Reviewed SHA256s

- `research/fresh_replay_runtime.py`: `04e6dd9922de9e136dd0ad1b46ee114168c9fb509dd66df36a8711343f84eb55`
- `tests/unit_capstone_fresh_replay_runtime.py`: `de3616752ab0d19e4d4888ba73b9e00c758140c5dc18f6fb913640e115455da5`
- `tests/unit_capstone_backend_suite.py`: `07e3d0521cdd631c9111da63a054fac579cb90f05da3e6f24c6af6d07bb1f6f4`
- `docs/FRESH-REPLAY-RUNTIME-WIP.md`: `bfd60c10cf14376d0d918901deecc0dbc42b185bb5535cebcb9634448eb85cf7`

Read `research/common.py` for helper semantics only.

## Finding F1 — P2: external digest arguments bypass exact-type/hash validation

Rule: exact JSON types and exact content/hash bindings at public API boundaries.
`prepare` recursively validates `request`, but does not exact-type validate
`expected_request_hash`. `common.identifier` accepts string subclasses, and the
subclass can override equality. A 64-zero digest subclass whose `__eq__` always
returns true passes the stale-request check; the emitted canonical record then
contains 64 zeros rather than the actual request digest.

The same omission affects `fixture_preflight` evidence dictionaries: their
digests are not passed through `json_value`. A digest subclass bypasses both
archive binding and actual fixture-byte digest comparisons. Thus a changed real
source fixture can be accepted against the original request's archive hash.
This is an in-process API validation defect, not a claim of a JSON-wire exploit
or live authorization escalation. Pure preparation remains non-authoritative.

Fix boundary validation to reject subclasses for the external expected hash
and the complete evidence mapping before comparisons or I/O; add regressions.

## Executed tests

Working directory: story worktree `dev-GRRR-734u`.

```sh
/usr/bin/sandbox-exec -p '(version 1)(allow default)(deny file-read* file-write* (subpath "/Library/GRRR"))' /opt/homebrew/bin/python3.14 -B tests/unit_capstone_fresh_replay_runtime.py
```

Result: exit 0; 12 tests passed, 0 failures/errors/skips. Real temporary files and
SQLite preserved by the supplied positive test. The protected-link test opens
only a local fixture symlink with NOFOLLOW and gets ELOOP; no destination probe.
Lexical-path guard tests reject all supplied paths before patched open/stat/lstat.
These guards are negative-call assertions, not mocked filesystem success.

Full backend suite: not run (transitive suites outside this bounded review).
Python 3.9: not executed; inspected public annotations use 3.9-compatible syntax.

## Fixture-only reproduction

The following script uses existing real-fixture setup, not mocked filesystem or
SQLite success. Executed from the review artifact with this exact command:

```sh
sed -n '/^```python$/,/^```$/p' docs/evidence/fresh-replay-runtime/r1-review.md | sed '1d;$d' | /usr/bin/sandbox-exec -p '(version 1)(allow default)(deny file-read* file-write* (subpath "/Library/GRRR"))' /opt/homebrew/bin/python3.14 -B /dev/stdin
```

Exit 0; both independent assertions reproduced:

```text
F1 request digest bypass reproduced: stored zero hash differs from actual
F1 fixture digest bypass reproduced: changed real file accepted; SQLite unchanged
```

```python
import sys
sys.path[:0] = ['research', 'tests']
from common import canonical, digest
from fresh_replay_runtime import prepare
from unit_capstone_fresh_replay_runtime import FreshRuntimeTests

class SpoofDigest(str):
    def __eq__(self, other):
        return True

case = FreshRuntimeTests('test_canonical_immutable_hashes')
case.setUp()
try:
    spoof = SpoofDigest('0' * 64)
    actual = case.request_hash()
    assert actual != '0' * 64
    result = prepare(case.request, spoof).record()
    assert result['request_sha256'] == '0' * 64
    print('F1 request digest bypass reproduced: stored zero hash differs from actual')
    (case.root / 'source').write_bytes(b'fixture-only changed source')
    assert digest((case.root / 'source').read_bytes()) != case.evidence['source']['sha256']
    case.evidence['source']['sha256'] = spoof
    result = case.run_fixture().record()
    assert result['status'] == 'prepared_not_issued'
    assert case.snapshot()['accounting'] == case.before['accounting']
    print('F1 fixture digest bypass reproduced: changed real file accepted; SQLite unchanged')
finally:
    case.doCleanups()
```

## Boundary conclusions

No other concrete blocker found in the reviewed source. Six manifest identities,
pinned receipt, provenance-only predecessor, holds/unknowns preservation, absent
new target, five false authorizations and eleven not-run gates are explicit.
Descriptor traversal rejects symlink roots/ancestors/finals and checks all paths
lexically first. The documented caller-owned quiescent fixture assumption is
honest; hostile rename, live freshness, production authority and live deployment
were not evaluated. This review grants no live approval. No implementation/test
edit, protected metadata access, network, tracker transition, commit, provisioning,
replay, reconciliation, promotion, admission, merge or push was performed.
