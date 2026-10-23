# GRRR-z3w9 — partial implementation, NOT delivered or live-approved

Do not install or execute this revision as root. No VM was started, no protected
installation was changed, and no independent ReplayReceipt was produced by this
worker. The historical C001 smoke remains consumed and is never replay evidence.

## Implemented draft

- `research/replay.py` reconstructs D011 candidate source identity from the pinned
  source archive plus exact frozen seed, resolves a direct upstream specification,
  defines explicit finding/gate semantics, and drafts evaluator-owned replay
  reservation, fresh baseline/seed dispatch, raw objects, receipts, failure count,
  settlement and immutable evidence export.
- The shared parent lifecycle can select a separately reviewed fixed replay
  protocol, under the same lock, bounded parent watchdog, actual UID/GID/group
  checks, immutable closure, and process-group cessation checks. Smoke defaults
  are preserved; replay uses the distinct `d011-independent-v1` namespace.
- The new root mode is `--independent-replay`. Its review decision is exactly
  `approved-D011-independent-replay`; its `replay` field must exactly equal
  `research/replay.py:SCOPE`. Existing smoke approval cannot authorize it.
- `./scripts/test-story independent-replay` is wired to a real UID-320 integration
  suite. It fails rather than skipping when the actual identity/runtime is absent.
  Three mandatory live fault cases remain red: failed rebuild, interruption,
  and two consecutive failures retained alongside a separate successful receipt.
  Altered dictionaries are not claimed as live fault-injection proof.

## Specification evidence, not a new operator attestation

Pinned archive `/Library/GRRR/replay-inputs/source.tar` is 716800 bytes, SHA-256
`e644b9848b306f158a2367293dd96c66dac2bed97c0dd42891db007667c0ae7e`, from
source commit `129e0b3f15a3bd6af949ee47d76f6855c582ab73`.
Its `wikilinks_test.go` member SHA-256 is
`218eebc6314ce14c555c579db24b85ccc4ccb425e3cd51f93d1c52a9049da570`.
`TestParseWikilinks/link with display text` supplies `[[Sr PM Agent|PM]]`, expects
`Display: "PM"`, and the assertion loop compares `g.Display != want.Display`.
This directly covers the D011 requirement that display text is captured.
The frozen D011 probe similarly checks `[[Target|Display]]`; its seed changes
`if len(m) > 4 {` to `if false {` in `wikilinks.go`.

The corpus `specification_digest` is SHA-256 of a commit/filename label, not a
hash of specification bytes. It is not sufficient by itself. No frozen corpus
artifact was edited. Other claims without a direct reviewed mapping remain
Specification ambiguity. A failed rebuild is Inconclusive, never a defect.

## Blocking correctness issue: cumulative accounting

`research/persistent_budget.py` explicitly requires one pre-provisioned campaign
store, not a fresh runtime allowance. Its exact registered profiles are
`synthetic`, `offline`, and `trusted-observation`. It does not register
`independent-replay`. Reusing the smoke's fresh Budget database would silently
reset allowance and is forbidden. The replay preflight now fails **before
namespace creation** on this missing profile. There is no fresh-budget fallback.

Required resolution: independently review how the existing cumulative campaign
history, including corpus/replay holds and settlements, is carried into the
registered replay profile and protected binding. Any store/profile migration
must preserve existing usage and uncertain reservations, not recast corpus or
smoke events as independent replay. This draft does not authorize that mutation.
The parent also reported the active successor store stopped (`state` row `1|1`)
at `/Library/GRRR/accounting-poc2/901acaff42b5a42f667b1c435beba9a9ae8312539cc36eb023c45584fd2e06d6`.
Profile registration alone cannot release that stop; any approved recovery must
preserve its usage/history. This worker did not access or modify that store.

## Remaining implementation/proof work

1. Integrate reviewed cumulative accounting without allowance reset; existing
   protected binding/schema cannot simply be relabeled or edited by this worker.
2. Complete actual failed-rebuild, interrupted-replay and consecutive-failure
   scenarios. The current fixed-D011 path only exercises clean baseline and
   seeded assertion failure; required integration expectations are intentionally
   not satisfiable by those observations alone. Parent mode currently runs the
   evaluator path, not the complete integration suite.
   The accepted corpus request requires `variant == challenge` and `probe=None`;
   the guest supervisor always applies the D011 seed for D011. It has no clean
   D011 or deliberate failed-rebuild fixture selector. Those modes require a
   separately prepared, reviewed and hash-pinned replay guest fixture profile,
   not edits to frozen corpus assets or relabeling C001 as D011. No functioning
   failed-rebuild/interruption/two-failure parent commands are claimed here.
3. Independently review the new root protocol and service code, including crash
   recovery, connection loss, pending reservations, source/build identity,
   environment evidence and every mandatory gate. No runtime-ready claim is made.
4. Recheck approved disk headroom. An initial full no-guest run had 205 tests and
   one `conservative-genesis` preparation-space-floor error (15350000000-byte
   threshold). After parent-reported safe staging cleanup, reruns passed 215/215
   under both interpreters. Replay still requires the higher approved
   16106127360-byte floor. This worker performed no cleanup.
5. Parent installation and real integration must happen only after the above,
   with fresh namespace, reviewed closure hashes and preserved prior evidence.

## Future parent command candidate — NOT reviewed or authorized to execute

After all correctness work, independent security review, fresh prelaunch runtime
audit and trusted parent installation of the exact hash-pinned closure:

```sh
/usr/bin/env -i PATH=/usr/bin:/bin LC_ALL=C /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/bin/python3.9 -I -S -B /Library/GRRR/bootstrap/replay-root-prepare --independent-replay
```

There are no caller-selected paths, guest commands or payloads. Keep the existing
runtime/preexec approval fields and exact code inventory checks. Add the new
review decision and fixed replay scope only after review. Never run checkout code
as root; never reuse the consumed smoke namespace or its approval. This command
is presently expected to refuse the absent cumulative accounting profile.

No-guest logs are retained under `evidence/independent-replay/no-guest/`.
Positive live replay, live negative paths, reviewer outcome, contract admission,
comparison and promotion remain unproven/blocked.

## Exact continuation map (not implementation or permission)

The parent requested a new replay-specific versioned input/profile, preserving
corpus v2.2. Continue in a fresh bounded implementation pass:

- Reuse `scripts/prepare-validated-corpus-input`'s pinned source/toolchain and
  readback design, but produce a separate replay artifact, never overwrite its
  output or protected corpus installation. `validated_corpus._iso_records`
  supplies the accepted bounded ISO namespace reader. No host vlt execution.
- The existing `corpus_supervisor_linux.go` accepts a generic strict seed/probe
  catalog and `GRRR-VC-[DC][0-9]{3}` identifiers; it need not be weakened. Create
  replay-only identifiers for clean D011 probe, seeded D011 probe, syntax-error
  rebuild fixture and bounded interruption fixture. Use the exact D011 semantic
  assertion for clean/seeded variants; do not use unrelated C001 as its baseline.
- The existing helper reports failed builds with three matching build-error
  repetitions, so the existing parser can observe a real build failure without
  substituting fabricated transport. `observation_outcome` already classifies
  such a result Inconclusive.
- Add explicit, default-preserving extension points to `CorpusExecutor` for
  immutable input/profile validation and input-image path; currently constructor,
  dispatch, QEMU args and output all pin corpus constants. New replay subclass
  must validate the new root-reviewed artifact/profile exactly. Do not monkeypatch
  module constants or make caller-supplied hashes authoritative.
- Extend root-reviewed fixed scope and plan with independently reviewed mode and
  profile digest. Each parent mode needs a distinct one-shot namespace and its
  own immutable review binding, but the same cumulative accounting store.
- Implement normal, actual failed-rebuild, bounded interruption, and consecutive
  non-reproduction scenarios. Preserve each attempt and conservative holds;
  success resets the counter but does not erase prior failures. Never resume a
  stopped run silently. Parent cleanup remains the accepted 473+5+2s bound.
- Replace the three unmet integration evidence expectations with execution of
  those real modes. Keep actual UID/VM absence as a hard failure. Review source,
  hashes and no-guest tests before proposing any privileged installation/run.
