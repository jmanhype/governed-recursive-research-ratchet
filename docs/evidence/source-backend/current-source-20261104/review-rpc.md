# Scoped backend review-RPC source review — GRRR-k3j7

REVIEW_RESULT: APPROVED

## Scope and state

- Worktree: `/Users/speed/Documents/Codex/2026-10-19/3e4m-b-4/outputs/governed-recursive-research-ratchet/.claude/worktrees/dev-GRRR-k3j7`
- Branch/HEAD at review: `story/GRRR-k3j7` / `2b601462ba0ffb5aee6239aa22b06c26801dfaf9`
- Requested base: `2b601462ba0ffb5aee6239aa22b06c26801dfaf9` (equal to HEAD)
- `docs/findings/` is absent in this worktree.
- Graph lookup was not used because the current root was reported absent; this is an exact source/test fallback review.
- This is approval only of the implemented source mechanics reviewed below. It is **not** approval of the full story, installed production topology, campaign authority, static-review resolver, or a live campaign backend.

## Exact reviewed hashes

```text
1e5e2b01224cc6acc9d5944dfac9ab738ae690e7311194ba7145490227d504c4  research/capstone_review.py
2e7a7ee7d69f75f5e4e503bb2468254cae7ec9176141f87d9cbe16e214f398da  research/capstone_review_service.py
3c4e163a437577056dd4744926980f8219916296105c1332b088f4c84c947977  tests/unit_capstone_backend_review.py
a5baf99ba3b5a478ae1e58aee5f3e180c7e91af1103e2502e410a840de211e52  tests/unit_capstone_backend_composition.py

32f63af61f8a26f667569d0ffe8adea2f618b10366254b8fc8dbcacc43e41831  research/capstone_backend_contract.py
762b6586e41584c30e4011a495c18dda3384691d590265087552d13efcae6429  tests/unit_capstone_backend_contract.py
33edaf942a89f5eb0b1481e3ca5f430d7229e2b87758894cf29f95217e479a21  research/common.py
c60766be57d2d5e4c2b4aed8c3b8cb71f17cad21f282e2ae4c4117d6c822a349  research/capstone_contract.py
```

## Findings

No concrete defect was found in the bounded implemented review-store, ReviewV2 codec, reviewer/context RPC, freshness checks, or Queue-test repair.

### Durable reviewer intent, commit, and idempotency

- The SQLite schema is fixed and mutation-hostile: immutable event/request triggers and the invariant that result hash/raw are null together are declared at `research/capstone_review.py:22-29`.
- `_replay()` enforces exact schema/index inventory, DELETE journal mode, FULL synchronous mode, event chain order/hash, original request-object bytes, request hash, ReviewV2 result-object bytes, and exact equality with the materialized request rows at `research/capstone_review.py:169-213`.
- `_append()` writes objects before `BEGIN IMMEDIATE`, replays the existing index, refuses an existing intent or changed/duplicate result, re-replays the proposed state, and commits/rolls back atomically at `research/capstone_review.py:224-249`.
- `review()` freezes canonical caller bytes, returns only through the durable index, and does not hold the database transaction across the verifier callback at `research/capstone_review.py:251-265`. Committed retrieval returns original request/result hashes and bytes at `research/capstone_review.py:267-274`.
- The tests directly cover original-result idempotency and reopen, intent-only refusal, expired/failing original bytes, changed bytes under a request key, object/schema/row corruption, SQL guards, and real process death after FULL-synchronous intent at `tests/unit_capstone_backend_review.py:125-201`.

### Original bytes, hashes, ReviewV2, freshness, phase, and operation

- `request_hash()` accepts only the exact request fields/action/version, validates identifiers and canonical base64 raw fields, and domain-hashes every field except the supplied self-hash at `research/capstone_review.py:47-65`.
- ReviewV2 has the exact field set and pass/fail semantics at `research/capstone_backend_contract.py:18-29`; validation enforces canonical bounds, exact fields/types, sorted unique evidence, prerequisite evidence for pass, and an increasing review window at `research/capstone_backend_contract.py:70-92`. Decoding also requires exact canonical bytes at `research/capstone_backend_contract.py:99-109`.
- `ReviewClient.review_and_get()` performs review then a separate durable get, requires identical responses, validates the exact response shape, decodes original ReviewV2 and actual Plan bytes, checks request/result digests, compares every trusted expected binding including evidence, and checks phase/verdict/blockers/leaf/actual-byte hash/selfhash/operation/observation/anchor/epoch at `research/capstone_review_service.py:45-79`.
- Freshness is a current-clock check and expiry cannot outlive either grant expiry or the observation receipt-age bound at `research/capstone_review_service.py:80-83`.
- Negative tests cover expired retrieval, changed verifier inventory, and intervening anchor loss at `tests/unit_capstone_backend_review.py:281-335`.

### Peer-first RPC and retained context

- The installed client factory fixes the evaluator principal and reviewer path/peer UID at `research/capstone_review_service.py:36-43`.
- `_read()` is newline-terminated, absolute-deadline bounded, refuses oversize input, rejects duplicate/noncanonical JSON, and the response envelope must be exactly `ok` or a strict non-retryable recognized error at `research/capstone_review_service.py:87-130`.
- Context registration retains canonical prospective Plan and Receipt bytes plus a live in-process owner, validates current state, and refuses duplicate/inherited context at `research/capstone_review_service.py:133-159`. Lookup requires exact campaign/leaf, Plan-byte hash, nonce, epoch, and current-state validation before returning original receipt/anchor/epoch at `research/capstone_review_service.py:161-182`.
- The installed server roles fix expected principals and require an already-bound exact fixed listener; retained inode/ACL qualification is explicitly left to InstallationV2 at `research/capstone_review_service.py:222-234`.
- The accept loop obtains kernel peer credentials before request read or callback, bounds capacity, and tracks workers/connections at `research/capstone_review_service.py:250-271`. Responses are bounded, absolute-deadline enforced, and transport failures never rerun effects at `research/capstone_review_service.py:273-291`; close is explicit and bounded at `research/capstone_review_service.py:298-313`.
- The independent-process roundtrip exercises reviewer and context RPC without deadlock, while wrong nonce, lost owner, changed anchor, expiry, and wrong inventory all refuse at `tests/unit_capstone_backend_review.py:259-335`.

### Queue-test repair

- `collect_review_outcomes()` drains exactly `count` outcomes **before** joining producers. Its `finally` still bounds joins/termination and closes/joins the Queue, and only after that requires every producer exitcode to be zero at `tests/unit_capstone_backend_review.py:203-218`.
- The concurrency test requires exactly three outcomes, exactly one verifier execution, at least one committed result, one request row, and exactly two events at `tests/unit_capstone_backend_review.py:220-232`. The loser must fail closed rather than mint a second result.
- The cached-reply regression creates a result larger than 128 KiB, drains exactly two outcomes before joins, requires both outcomes to equal the original object exactly, requires both processes to exit zero, and confirms no second verifier/event/result at `tests/unit_capstone_backend_review.py:234-249`.
- No weakened assertion was found in this repair. A missing/hanging producer still fails through the exact queue count/timeout or nonzero exitcode path rather than reporting success.

### Composition boundary

- The composition test uses two dynamically fresh Plans/reviews and then performs the unchanged strict current-anchor prebind before Journal claim/reservation/permit/send at `tests/unit_capstone_backend_composition.py:69-164`.
- It requires two distinct Plan and review hashes, two one-use sends, two operations, and two consumed fixture grants at `tests/unit_capstone_backend_composition.py:165-201`.
- The fixture explicitly says its grants/reservations are synthetic and not issuance, v5 allowance, static approval, binding-only durability, campaign stop, baseline/candidate corpus results, or a root Manifest at `tests/unit_capstone_backend_composition.py:1-6` and `tests/unit_capstone_backend_composition.py:160-163`.

## Verification command and measured result

Command:

```sh
/opt/homebrew/bin/python3 -B /tmp/grrr-k3j7-guarded-source-suite-20261104.py unit_capstone_backend_contract unit_capstone_backend_review unit_capstone_backend_composition
```

Measured result:

```text
Ran 42 tests in 5.520s
OK
PARENT_SOURCE_ONLY tests=42 failures=0 errors=0 skipped=0 protected_attempts=0; guard=parent-interpreter-only; no VM/UID/OS-isolation proof
```

Actual module counts were independently counted as 22 + 19 + 1 = 42, matching the requested expectation.

Read-only state checks used: `git rev-parse`, `git merge-base`, `git log --oneline -3`, `git branch --show-current`, `git status --short --branch`, exact `rg`/`nl` source reads, and SHA-256 hashing. Final status still showed only the pre-existing untracked story files; this review made no source/tracker/Git changes.

## Limitations and explicit non-approval

- This does **not** verify `/Library/GRRR`, UID 322/320/321 separation, installed sockets, ACLs, retained inodes, verifier closure, credentials, VM behavior, or live APIs. The bounded source guard reported zero attempts and itself states that it is not OS isolation.
- The deterministic installed verifier and production authority/static-review resolver are absent. `expected` and `validate_current`/verifier callbacks are trusted source seams, not provenance. In particular, synthetic `H` values and opaque `campaign_plan_raw` fixtures must not be treated as real campaign/static authority.
- `ReviewServer.open_existing()` intentionally does not qualify installed topology; InstallationV2 retained inode/ACL/runtime-closure validation remains missing at `research/capstone_review_service.py:229-234`.
- The parent's reported combined 143-test, three-interpreter run was not rerun by this scoped reviewer. Only the required 42-test parent-guarded suite above was independently measured.
