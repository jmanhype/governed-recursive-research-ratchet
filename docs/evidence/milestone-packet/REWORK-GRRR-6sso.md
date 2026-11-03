# GRRR-6sso repository-only rework evidence map

Verdict: **GRRR_6SSO_REWORK: BLOCKED**

This rework hardened the offline Jev boundary and produced an honest AC map. It
did not execute the capstone, read/provision/use a real credential, call the
network, start measurement, replay, admit a contract, mutate production,
commit, merge, or push. Credential regressions use only injected fake material.
The full capstone remains blocked because mandatory real E2E evidence is
absent; unit/injected-transport tests are not substitutes.

## Identity and immutable inputs

- Worktree branch: `story/GRRR-6sso`; unmodified base HEAD:
  `b08754ef4623a00b1f3839b343491c4b8a6c4f0c`.
- Frozen corpus digest: `dfa75ef2bf3d43fd4f750094fe643afe4f204812c0ae2426276bedb471fa8529`.
- Evaluation approval remains unchanged: `corpus/evaluation-plan.json` says
  `approval.state=not-approved` and `approval.measurement_started=false`;
  SHA-256 `b8510ff1af4873db58c3483e39f7076c6f959337c93888568a5f1c0bde690eae`.
- Ten direct predecessors are nd-closed/accepted (queried with `pvg nd show`):
  GRRR-0g4n, 90te, gu87, my5n, c875, bnkf, z3w9, dbbi, 34ve, and fmvp.

## Changed implementation evidence

| Path | SHA-256 after rework | Result |
|---|---|---|
| `research/jev_adapter.py` | `3294ab0acbd965bfd72e07d88b79510402da45b4e0f5bd81c23f0f7d0f772a84` | New offline-testable adapter: deterministic opaque refs, public-category allowlist, HTTPS-only URL, bounded JSON, strict score/probability/usage validation, successful-response credential-echo rejection, rejected redirects, sanitized transport errors |
| `research/selector_comparison.py` | `8514ff7015011a1bf81b0f10f92142c584bef3a572df81d7402c7455f27d2db8` | Binds Jev selection to the canonically self-verified frozen manifest/public projection, validates catalog/budget/seed, supports injected transport, preserves honest unavailable behavior |
| `tests/unit_selector_comparison.py` | `3c04376207b447ef0f3f5c18f50ff753f56f842f986a30e26fad36faceba1d36` | 29 focused tests: reproducibility, unavailable behavior, no semantic outbound IDs/labels, fail-closed malformed responses/usage, credential-echo sanitization/no persistence, same-origin/cross-origin redirect refusal with external observability, artifact-bound membership, manifest-free forgery rejection, secret-safe errors, no real network |

## Independent security review rework

The first delivered boundary was independently rejected for three findings.
Only those findings were reworked:

1. **Redirect forwarding:** default `urlopen` could preserve the authenticated
   request across a followed redirect. `_http_post_json` now constructs its
   opener with `_RejectRedirectHandler`; every redirect raises before a
   follow-up request is constructed, including same-origin and HTTPS-to-HTTPS
   redirects. Any received 3xx status is also rejected. The initial URL remains
   HTTPS-only with no credentials, query, or fragment.
2. **Declarative catalog binding:** the public bytes are now hashed exactly as
   stored and compared with `manifest.artifacts["public/challenges.json"]`.
   The manifest catalog and public projection must have exactly the same ID
   membership, and `jev_select` must use exactly that membership. The manifest
   itself is canonically self-verified: SHA-256 over every field except
   `freeze_digest` must equal both the manifest literal and the pinned corpus
   freeze. Invented or missing IDs, extra public entries, missing public
   entries, byte-only public tampering, rebound public-byte hashes under a
   forged manifest, and manifest membership/artifact-hash forgeries (whether
   the freeze literal is rebound or retained) are rejected before transport.
3. **Transport `JevError` leakage:** every exception raised by the injected or
   HTTP transport is now replaced by the fixed sanitized
   `Jev transport failed; outcome is unknown` / HTTP-boundary message,
   including exceptions already typed as `JevError`.

Focused regressions reproduce each reviewer probe:
`test_redirect_is_rejected_without_following_authorization`,
`test_catalog_binding_rejects_mismatch_before_transport`, and
`test_transport_jev_error_is_sanitized`. The redirect regression covers both
same-origin and cross-origin destinations. Accidental-network tests monkeypatch
the adapter's actual opener-construction boundary (`_build_opener`), not the
no-longer-used default `urlopen` entry point.

Outbound Jev state is only `challenge_ref` plus one allowlisted public category.
The reference is `SHA-256(grrr-jev-opaque-v1 || NUL || corpus-freeze-digest || NUL || local-ID)`.
Local D/C IDs, `kind`, variant, fixture text, protected truth, source, and raw
logs never enter the outbound body. The local ID is mapped back only after a
validated response. Tests reject a malicious semantic model identifier before
transport and monkeypatch opener construction to fail on any accidental real
call.

### Second independent security review rework

Only that reviewer's two new findings were changed:

1. **Successful-response credential echo:** before shape validation, return, or
   downstream persistence, `score_challenge` recursively compares every JSON
   string key and value against the actual credential supplied to the adapter.
   An otherwise valid response with `model` equal to the credential raises the
   fixed `Jev response failed credential safety validation` message, with no
   exception cause or credential-bearing provider detail. The regression proves
   the credential is absent from both the exception text and the serialized
   selector result; `jev_select` returns no selector object on that fail-closed
   path, so serialization is exactly `null`.
2. **Redirect regression observability:** the redirect test no longer relies on
   assertions inside callbacks that `_http_post_json` can swallow. It records
   opener-handler installation, initial request attempts, same-origin and
   cross-origin redirect-handler rejections, and would-be follow-up requests in
   external lists, then asserts all of them only after the expected sanitized
   `JevError`. This exposed and corrected that `_build_opener` receives the
   handler class rather than an instance.

### Differently scoped credential-echo review

A fresh Qwen Ambassador reviewer independently matched all four WIP hashes,
ran the offline focused suite with fake credentials, and returned:

`CREDENTIAL_ECHO_NARROW_REVIEW: APPROVED`

The review approved only the two latest findings. It confirmed that every
successful-response JSON string key/value is compared with the actual adapter
credential before shape validation, return, or persistence, and that the
credential-echo exception, repr, cause, selector output, and report path stay
free of the fake credential. It also confirmed that redirect-handler
installation, initial request attempts, redirect rejections, and absent
follow-up requests are asserted externally after the sanitized error. This is
not approval to start selector measurement or claim capstone completion.

Parent independently reran the focused suite on both interpreters (**29/29
each**) and the complete no-guest suite on both interpreters (**749/749
each**). Parent-generated full-suite log hashes were
`71a51d3a8778326043a1c7ee53d3edb4d4dac34af2d6df5c8f54f826277f5d8d` for system
Python and
`4192976628b4bf6a5cfeb2b22044f4d8792ff54c179f455a84af5edb5cb8ae9c` for
Homebrew Python.

## AC-by-AC evidence map

| AC | Existing evidence and result | Capstone status / exact missing artifact |
|---|---|---|
| 1. Clean authorized full operator journey | Real D011 replay lifecycle (`docs/evidence/replay-authority/replay-result/lifecycle.json`) records evaluator success, child cessation, and 47.7242865s; verified snapshot SHA-256 `ab8d72f25c3a4ce2f5d5d672c4d052ea2de442f9c9384bd381d8222d7a91b689`. Admission artifacts bind operator-speed to contract `ab4339807b8fae5b96713131ef524a409b475bb7c158a4318fce5de80b668aa4` under `docs/evidence/contract-admission/`. | **UNMET as full AC:** no single clean-environment, unedited command/output/receipt journey covering start, monitor, verified snapshot/report, replay, review, explicit approval, recurrence rejection, and clean baseline pass. |
| 2. >=20 seeds plus clean negatives through complete mandatory system | `docs/evidence/validated-corpus/v2.2-batched-run/REPORT.md` and `aggregate.json` (SHA-256 `93f2558864a7bdfa01dd0e8042ae8330834659ef71812f17a6ddc9efac3c5cc4`) record 32/32 isolated scenarios, 96/96 repetitions, 0 failures/errors/skips. The same aggregate explicitly marks downstream independent replay, reviewer outcome, selector comparison, contract admission not-run/blocked and `verified=false`. | **UNMET:** this is preliminary fixture validation, not the required full-system receipts for every mandatory gate and zero unverified/failed-replay admissions. |
| 3. Genuine equal-budget selector comparison | Accepted baseline artifact `reports/comparison.json` (revision `0bc3503`, SHA-256 `74580be7562c113a228f8ca066709d26cc47cf63da1c9c55b90d8498ab8d3688`) records deterministic/random selections and Jev unavailable/incomplete. This rework adds only offline/injected-transport hardening, not measurement. | **BLOCKED:** evaluation plan is not approved and measurement has not started; no real authorized Jev cost/uncertainty/repetition report exists. |
| 4. Hung-runner stop, races, crash/recover | Accepted sibling evidence includes `docs/evidence/safe-stop/final-verification/` (focused 7/7 and historical full no-guest 166/166 logs) and durable ledger evidence `docs/evidence/durable-evidence/attempt-20261021T204415Z-c360927f/summary.json` (4/4, 0 failures/errors/skips, verified=true). | **UNMET at capstone scope:** no retained full journey proving deliberately hung executor cessation/fence, repeated idempotent requests, durable transition crash/recovery, ordering races, committed-before-stop listing, and restoration-or-Recovery-required in one run. |
| 5. Full adversarial fail-closed matrix | `research/admission.py` and `tests/unit_admission.py` cover wrong operator/contract/auth/gates/receipt and duplicate consumption/recurrence; accepted GRRR-34ve close evidence records 23/23 tests. Durable export verification directions are in `docs/evidence/replay-authority/replay-result/export-ca47bda9f47645b1910cba1449bcddfe/VERIFY.md`. | **UNMET:** no complete unedited forged identity/evidence, stale approval, missing gate, budget unknown/exhausted, protected write, ambiguous-spec, and tamper/truncate/missing-export run set with matching CLI/Markdown/JSON safe next actions. |
| 6. Keyboard-only/screen-reader walkthrough | `docs/DESIGN.md` requires keyboard-only/screen-reader operation and measured review burden. `research/review_report.py`/`tests/unit_review_report.py` provide plain, color-free report projections, accepted as partial GRRR-fmvp. | **UNMET:** no keyboard-only or screen-reader walkthrough artifact for inspect, reject/request evidence/stop, execution/finding/decision/effect separation, and measured review time. |
| 7. Final immutable architecture/outcome packet | Original `docs/evidence/milestone-packet/FINAL-PACKET.md` at base revision `b08754e` maps architecture ACs and honestly lists Jev/full-capstone gaps. This map adds exact current hashes and blocked reasons. | **PARTIAL, not full AC:** original packet does not bind every architecture/business/design outcome to immutable receipts, exact revisions, costs, warnings, unresolved blocks, and rollback evidence. |

## Verification actually run

- `/usr/bin/python3 -m py_compile research/jev_adapter.py research/selector_comparison.py tests/unit_selector_comparison.py` — exit 0.
- `/opt/homebrew/bin/python3 -m py_compile research/jev_adapter.py research/selector_comparison.py tests/unit_selector_comparison.py` — exit 0.
- `GRRR_JEV_DISABLE=1 /usr/bin/python3 -m unittest -v tests.unit_selector_comparison` — **29/29 passed, 0 failures/errors/skips**.
- `GRRR_JEV_DISABLE=1 /opt/homebrew/bin/python3 -m unittest -v tests.unit_selector_comparison` — **29/29 passed, 0 failures/errors/skips**.
- Capacity preflight with `/bin/df -g .`: **24 GiB available (about 26 GB decimal)**, above the unchanged 15.35 GiB conservative floor.
- `GRRR_JEV_DISABLE=1 /usr/bin/python3 -B -m unittest discover -s tests -p 'unit_*.py' > /tmp/grrr-6sso-rework2-final-full-no-guest.log 2>&1` — exit 0, **749/749 passed in 39.003s**; log SHA-256 `74e06a25595ce17250c989d21788603faef55461bb93195f9eb53968933ac4bb`. This is only the full no-guest suite, not capstone or measurement evidence.
- `pvg verify research/jev_adapter.py research/selector_comparison.py tests/unit_selector_comparison.py --include-tests --format=text` — `VERIFY: PASSED (3 files scanned, 0 issues)`.
- `pvg gates research/jev_adapter.py research/selector_comparison.py tests/unit_selector_comparison.py --format text` — `GATES: PASS (2 warn, 0 skipped)`; warnings are `_load_frozen_projection` CCN 15>15 and the focused test file's 544 non-blank lines.
- `git diff --check` — exit 0.

The mandated codebase-memory MCP project-list call was unavailable (`list_projects is not available to the model`), so structural discovery used direct source and exact-path searches; no completeness claim is based on the graph.

## Remaining blockers

1. Operator-approved selector measurement and authorized Jev capability (or a
   deliberate blocked/unavailable outcome) plus real cost/uncertainty receipts.
2. Full mock-free capstone E2E execution across >=20 seeds and clean negatives,
   including every mandatory gate and independent replay/admission authority.
3. Full stop/crash/recovery/race journey evidence.
4. Full adversarial matrix and tamper/truncation/missing-export verifier proof.
5. Keyboard-only and screen-reader walkthrough plus measured review burden.
No full capstone success, selector measurement, credential use, replay,
admission, promotion, production mutation, commit, merge, or push is claimed.
