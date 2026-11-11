REVIEW_RESULT: APPROVED

# Independent R2 source-only security re-review

Base HEAD verified: `5f6ce4e83e2426e859127af568aa730c19dc6a9b`.
All seven assigned functional files and retained R1 were read. Exact-source
inspection was used; no graph-index completeness is claimed. `docs/findings`
does not exist in this worktree. Concurrent source and evidence were preserved.

## Reviewed SHA-256 inventory

```text
d39158c4b0c3a5ba0398ac93d114353b267a004b0db8ebf22cf04b4afb5ffdfd  research/status_view.py
46728e0df57c23d1502e64bd32b45909a8b8a0194f6e7822b111480860e21bbc  research/review_report.py
d90f11f7b9f14fcd8b827cdf906ad677ef583ed78e8f1460609ff7d19f821ec4  scripts/grrr-review
03956006d8dc7f1650149c66658d0fadeafcd19fd98567c0a4f59d9be3cc7034  tests/unit_status_view.py
198b478b438df90ba720914aad2a988fee69f93ff4acce725aa0669b169a1887  tests/unit_review_report.py
27f896e197ef394135cd3259c8cdb0aeb968f1b9cf9d907721b5e8863e1aab15  tests/unit_capstone_backend_suite.py
9436883933d5befcf0895a740b60b06f9c6130667cab701220edadcacb419163  docs/READ-ONLY-STATUS-VIEW.md
9b8fc34458946427fe3c4d91462d7286ca28e6ea973556bf472ee04b5543e4c4  docs/evidence/read-only-status/r1-review.md
```

## Independently measured verification

Executed from this story worktree:

```sh
PYTHONPATH=research:tests /usr/bin/sandbox-exec -p '(version 1)(allow default)(deny file-read* file-write* (subpath "/Library/GRRR"))' /opt/homebrew/bin/python3.14 -B -m unittest -v unit_status_view unit_review_report
```

Observed exit 0, `Ran 41 tests in 0.864s`, `OK`; zero failures, errors, or
skips. These are my own focused results, not the parent's full-suite counts.
The suite exercises real temporary archive files and copied real CLI code;
successful loader/CLI I/O is not mocked. It covers both views and all three
successful output formats; duplicate-cost CLI refusal is exercised in text
and JSON. Markdown refusal follows the same non-JSON branch by source review.
No protected-path probe was attempted.

Additional read-only commands: `git log --oneline -3`, `git status --short`,
`shasum -a 256` on the inventory, complete source reads, and
`git diff -- tests/unit_capstone_backend_suite.py`. The suite diff adds only
the two status/review modules; all preexisting required modules and the
nonzero/skipped-test failure guards remain intact.

## R1 findings closed

### R1-1: duplicate archived JSON fields

Closed. All three artifacts (snapshot, receipt, lifecycle) now pass through
the same `_read_json` decoder. Recursive `object_pairs_hook=_unique_fields`
rejects duplicate decoded keys before projection, including escaped spelling
aliases and nested gate fields. This is a general field rule, not a special
case for cost. The real-loader regression rejects null-then-zero cost,
false-then-true verification, nested fail-then-pass gate status, duplicate
snapshot version, and duplicate lifecycle elapsed fields. The real CLI
regression returns code 2 without a zero-cost report or raw traceback;
JSON returns an explicit refusal with `actions_authorized: false`.

The shared decoder also rejects non-finite constants, overflowing decimal
tokens, nonzero underflow, and decimal tokens whose decimal value changes
on float/string round-trip. Exceptions are normalized to generic ReportError
and the CLI does not expose archived content through its refusal message.

### R1-2: distinct exact numeric costs collapsed by float coercion

Closed. `_number` checks finiteness but returns the original exact int/float;
it no longer substitutes a float. `_cost` compares these retained native
numbers before storing the selected observation. Python numeric set equality
does not collapse the distinct integer pair 9007199254740992 and
9007199254740993; tests now assert Unknown/null for that conflict and for
2 versus 2.5. A single large integer retains its integer type and exact JSON
value, and human rendering avoids a float conversion. Huge values rejected
by the finite representation check remain Unknown. Explicit sub-cent positive
observations no longer render as a false zero. Missing, boolean, negative,
non-finite, and otherwise malformed costs remain Unknown/null, never spendable.

## Regression review

All eleven common gates remain the required profile, with nine admission
gates separately labeled. Missing, failed, malformed, zero, and unknown gate
evidence cannot produce approval/readiness. Historical inspection eligibility
requires exact True, Verified defect, and all eleven passes; it confers no
action authority. Every action authority remains false, recommendation remains
Needs more evidence, and identity/current-verification/source-review/human
approval/installation/budget spendability/stop/admission/promotion limits are
preserved in the shared projection and renderers.

The projection remains detached, deterministic and free of I/O, network and
clock calls. Recursive plain-type screening rejects equality/lookup subclasses
before use. Reflected labels exclude terminal control characters. Only gate
constants are consumed from admission/common; no registry function or writer
is called by the reviewed projection/report/CLI path. Public function names,
vocabulary and signatures remain; schema version 2 is documented. The CLI
adds only `--view` alongside existing `--format`, not an arbitrary-path reader.

## Scope limits

No blocking finding remains in this bounded source re-review. This approval
is review of the supplied WIP source hashes only, not PM/story acceptance,
source promotion, installation, runtime/campaign qualification, current archive
provenance, settled accounting, or permission to act. I did not rerun the full
backend suite or cross-version matrix and do not adopt their counts as mine.
Authority-module byte-parity verification remains separately parent-owned.
No source/test edits, tracker changes, staging, commit, provider/network use,
credentials, protected-path access, provisioning, replay, admission, promotion,
production mutation, merge or push were performed. The only retained artifact
created by this review is this report.
