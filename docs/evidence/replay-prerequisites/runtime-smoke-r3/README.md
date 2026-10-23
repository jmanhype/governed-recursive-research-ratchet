# GRRR-w1lt macOS identity-vector correction

Base: d89cec7f57367fe512fe11b71f63be3098312c6e. Parent-provided live report:
the sanitized root smoke failed before runner readiness/VM dispatch; lifecycle
evaluator_succeeded=false, exit_codes=[1], children_ceased=true, elapsed 0.128s.
Runner output was generic RuntimeError. Parent diagnostic observed UID/GID321
with groups [321,12,61,701,100] after the documented drop sequence. The failed
runtime-smoke partial namespace remains preserved; this worker did not read,
modify, clean or retry it. This paragraph records parent evidence, not worker
verification of root-positive execution.

## Correction and real read-only diagnostic

Live pwd/getgrouplist and independent `/usr/bin/id -G` agree:
- _grrr_evaluator UID/GID320: {12,61,100,320,701}.
- _grrr_runner UID/GID321: {12,61,100,321,701}.

Exact vectors are pinned in reviewed code, recomputed at protected preflight,
before initgroups/drop and at every role entry. Account names, UID/GID, empty
home and nonlogin shell remain strict. Parent uses initgroups(account, gid),
setgid and setuid; children require exact resulting membership, not an impossible
empty vector. Any added/missing membership is denied. Root/wheel, staff/admin,
operator501 and opposite-service-group tampering is covered by real tests against
live account data. Existing _lpoperator100 and sharepoint701 memberships are
explicitly disclosed in the installation contract and require review; they are
not claimed absent. No account or group is changed by this revision.

## PROOF

Both `/usr/bin/python3` (3.9.6) and `/opt/homebrew/bin/python3` (3.14.3), from worktree:
- `-B -m unittest discover -s tests -p 'unit_replay*.py'`: 32 passed each.
- `-B -m unittest discover -s tests -p 'unit_*.py'`: 198 passed each.
- No mocks, identity substitution, skips or environment gates. Diagnostic and
  rejection tests are unprivileged and do not prove the actual root drop.
- pvg verify explicit changed implementation/test/contract/evidence paths:
  passed, 3 Python files scanned, zero issues. Real tests verify all12 code pins.
- git diff --check and staged check passed; SHA256SUMS binds final logs/report
  and revised source/contract bytes. Exact sanitized future commands unchanged.

## AC boundary / not-run

| AC | Evidence | Status |
|---|---|---|
| 1 | Original policy and C001 scope unchanged | New group vector requires review |
| 2 | Exact identity vector computed and enforced; initgroups drop specified | Revised root installation/drop/access probes not-run |
| 3 | Runtime/asset/preflight protections retained; account group checks added | Updated positive parent preflight not-run |
| 4 | Live failed attempt preserved; no-guest regressions pass | Actual successful VM/service/accounting/stop lifecycle NOT-RUN |
| 5 | No verdict/ReplayReceipt/admission/counter change | GRRR-z3w9 separate |

Renewed independent review, parent archive/update of installation/review, runtime
audit, explicit preserved-failure recovery/fresh namespace authorization, actual
UID drop/access/unchanged-asset probes and offline service/VM/accounting/stop
lifecycle remain required. No root/QEMU/VM, /Library/GRRR mutation, push, delivery
or acceptance by this worker. Story stays in_progress; AC4 unresolved.

LEARNINGS: macOS setuid can repopulate membership despite a prior setgroups([]).
Exact approved directory-service membership is the enforceable contract, not an
empty supplementary vector. DISCOVERED_BUG: observed identity mismatch fixed;
no other findings deferred.
