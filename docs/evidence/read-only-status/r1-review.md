REVIEW_RESULT: REJECTED

# Independent source-only security/semantics review

Base: `5f6ce4e83e2426e859127af568aa730c19dc6a9b` (HEAD verified).
Scope: seven supplied files read completely; admission/common constants read only.
No delegation, source/test changes, tracker transitions, live registry calls, protected-path access, provisioning, replay, admission, accounting mutation, commit, merge, or push.
`docs/findings` is absent in this checkout. Existing concurrent changes preserved.

## Reviewed SHA-256 inventory

```text
f4b16f35d0d5e62831f86ba262c1b0bc026b18a8bb2ffe9d71e1a9c4b395e764  research/status_view.py
b6fddc0c44f369e2bfc1a7d2fa045ecee95c521d5ca490a759e1599f853218dc  research/review_report.py
5ea82158c1557b295aafb4999c47a0243349634df610c5d6f7b98c779e8a40fd  scripts/grrr-review
603b016c264bf5223918cf7a9c6d1cb3e3dc734f7389675afcaebba091fe268e  tests/unit_status_view.py
98cfd27dc095cefdc14579b1e3d72f3661496fe2e64c9f7f057b5249e1784d67  tests/unit_review_report.py
27f896e197ef394135cd3259c8cdb0aeb968f1b9cf9d907721b5e8863e1aab15  tests/unit_capstone_backend_suite.py
439d464f28d9921d0002d0201a23169982cb185fbe67698a40f6bac8374a6138  docs/READ-ONLY-STATUS-VIEW.md
```

## Measured tests and commands

Working directory: this story worktree. All Python invocations used the following exact prefix; no protected probe was attempted:

```sh
PYTHONPATH=research:tests /usr/bin/sandbox-exec -p '(version 1)(allow default)(deny file-read* file-write* (subpath "/Library/GRRR"))' /opt/homebrew/bin/python3.14 -B
```

Prefix plus `-m unittest -v unit_status_view unit_review_report`:
`Ran 34 tests in 0.464s`, `OK`, zero failures/errors/skips.
The tests include real-code temporary CLI fixtures exercising both views and all three formats.
The required-suite diff only adds the two modules: no prior module removed, skip introduced, or zero-test guard removed.
I did not run or claim the parent's full/cross-version suite.

Two additional Python stdin probes used that prefix plus `-`, with the source below. Temporary fixture used only a normal-user disposable directory and the real loader, no mocks. These probes are not counted as unittest cases.

## Blocking findings

### R1-1 — P2: duplicate JSON costs erase ambiguity before projection

Location: `research/review_report.py:load_replay_data`, all three default `json.loads` calls.
An archived receipt containing `"cost_usd": null, "cost_usd": 0` is ambiguous/malformed evidence, but last-key-wins parsing silently removes the unknown value. The real loader and report render it as `$0.00 reported, unverified; not spendability` instead of Unknown/null. Unverified labeling does not cure the explicit ambiguous-cost requirement. Duplicate verification/gate keys are subject to the same silent overwrite mechanism.

Reproduction executed:

```python
import json
import tempfile
from pathlib import Path
from review_report import load_replay_data, build_report, to_plain_text
from unit_status_view import passing_receipt
with tempfile.TemporaryDirectory(prefix='grrr-review-r1-') as directory:
    export = Path(directory) / 'export'
    (export / 'objects').mkdir(parents=True)
    (export / 'snapshot.json').write_text('{}')
    receipt = json.dumps(passing_receipt())[:-1] + ', "cost_usd": null, "cost_usd": 0}'
    (export / 'objects/78fde524d9562f6cb28df336512b3ca84bc8d72c72b47cd71f1a47516613ab4e').write_text(receipt)
    report = build_report(load_replay_data(export))
    print('duplicate ambiguous cost:', report['budget'])
    print([line for line in to_plain_text(report).splitlines() if 'Cost:' in line])
```

Observed: `state='Reported', cost_usd=0.0, sources=['receipt'], reason_code='COST_REPORTED_UNVERIFIED'`; human cost line `$0.00 reported, unverified; not spendability`.
Required correction: preserve/reject duplicate-key ambiguity at the loader boundary without manufacturing a reportable zero or positive gate profile; add real-loader/CLI regression coverage.

### R1-2 — P2: float conversion collapses conflicting exact cost inputs

Location: `research/status_view.py:_number` and `_cost` distinct-value comparison.
Two supported, finite, nonnegative integer values are compared only after lossy float conversion. `9007199254740992` and `9007199254740993` differ but collapse to one value. The projection incorrectly calls the conflicting reports unambiguous.

Reproduction executed:

```python
from status_view import project_status
from review_report import to_plain_text
from unit_status_view import complete_data
x = complete_data()
x['cost_usd'] = 9007199254740992
x['receipt']['cost_usd'] = 9007199254740993
r = project_status(x)
print('conflicting integer costs:', r['budget'])
print('rounded nonzero:', [line for line in to_plain_text(project_status({'cost_usd': 0.001})).splitlines() if 'Cost:' in line])
```

Observed conflicting-cost result: `state='Reported', cost_usd=9007199254740992.0, sources=['input', 'receipt'], reason_code='COST_REPORTED_UNVERIFIED'`.
Expected: Unknown/null for distinct source values. Preserve exact numeric distinction or fail closed on unsupported precision before comparison. The separate sub-cent formatting observation (`$0.00` for explicit `0.001`) is not counted as a blocking finding: it is a known explicit numeric observation formatted to cents, not missing evidence.

## Positive source observations and limits

All eleven required gates are enumerated; the nine-gate admission subset is separately labeled and cannot substitute for missing gates. Empty gates do not recommend approval. Exact boolean verification, known finding, and all eleven passes are required for historical inspection eligibility only. All action authorities remain false; source review, currency, identity, runtime, accounting, installation, and current verification remain unestablished. Type-first recursive plain-value screening prevents the tested equality/lookup subclasses and terminal control characters from becoming trusted output. Shared projection and schema version 2 are consistent across renderers and CLI views.

This is source/test evidence only, not installed/runtime/campaign validation, source-code promotion approval, accounting proof, or permission to act. Authority-module byte parity is separately owned by the parent baseline audit and is not claimed here. Approval is rejected because the two reproduced cost ambiguities violate the stated fail-closed contract despite the focused suite passing.
