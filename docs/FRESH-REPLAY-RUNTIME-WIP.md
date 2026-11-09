# Fresh execution namespace: source-only WIP

GRRR-734u, based on exact parent `5f6ce4e83e2426e859127af568aa730c19dc6a9b`.
The initial checkpoint was uncommitted, not independently approved, and not
provisioned. Retained R1 review evidence rejected its first source. Current
source verdicts are retained in `docs/evidence/fresh-replay-runtime/`; Git records
any subsequent authorized WIP commit. That commit is not runtime, deployment,
production or story acceptance authority. This is a proposal
builder and offline fixture preflight, not a runtime engine or installer.

## API and schema v1

`prepare(request, expected_request_hash)` returns a frozen `Proposal` containing
canonical bytes and their SHA-256. `record()` returns a detached JSON copy;
`validate_proposal` recomputes both bindings. Hashes are identities, not signatures
or evidence of trusted origin. Callers must obtain expected hashes/identities
from independently retained evidence; self-consistency is not authentication.

Request keys are exactly: integer `version=1`, 32 lowercase hex `namespace`,
`target_state="absent"`, list of 32-hex `used_namespaces`, `predecessor`,
`bindings`, and `identities`. Predecessor keys are exactly 64-hex `identity`,
fixed `target=/Library/GRRR/independent-replay`, `replay_state` (consumed, unused,
unknown, stopped, pending), and nonnegative integer or null `replay_count`.
These are immutable provenance, not replay permission. Consumed predecessor
evidence does not make a consumed target reusable.

Bindings contain exactly source, inputs, vm, policy, prior_evidence, accounting.
Each has exactly 64-hex identity, sha256 of canonical payload, and nonempty
JSON-object payload. Identities contain exactly those six expected identities
and predecessor. All payloads must bind an `archive_sha256`. Other source/input/
VM/policy/prior-evidence payload fields are opaque canonical JSON evidence,
not interpreted policies. No floats, tuples, object subclasses or coerced keys.
Accounting payload has exactly integer version 4, archive_sha256,
recovery_receipt `8b7958e5be76f6b35c4bfafc1f17a2926badfdd813addbefd5d683e376e8eeeb`,
unknowns object, and holds list. Their contents are retained verbatim; no
allowance, spendability, budget adjustment, or hold release is inferred.

The future protected target is generated opaque data under
`/Library/GRRR/replay-proposals/<namespace>` and is NEVER probed. Supplied absence
and inventory facts are archival claims, not live checks of non-reuse.
Every result is `prepared_not_issued`, with review/installation/replay/promotion/
admission authority false, all common mandatory live gates not-run, and runtime
readiness not asserted. It cannot be used as an authorization receipt.

## Offline fixture boundary

`fixture_preflight(..., sandbox=..., target=..., evidence=...)` requires explicit
canonical absolute paths strictly below `/private/tmp/`. Target must be exactly
`<sandbox>/replay-<namespace>`. Evidence maps each of the six bindings to exactly
path and sha256; that digest must match its payload's archive_sha256. All paths
are validated before any filesystem metadata. Double slashes, dot components,
traversal, escapes and all protected paths fail lexically. Descriptor-relative
opens reject symlink roots, ancestors and final entries; existing or dangling
target entries fail. Evidence must be bounded, unique regular files.

This requires caller-owned quiescent fixtures, not hostile concurrent renames.
No files are created, no SQL is executed, and no replay state is reset. Real
SQLite fixture bytes are hashed read-only, not treated as semantic accounting
authority. Tests query the fixture separately and compare old evidence and
ledger bytes plus inodes. Fixtures do not prove live integrity or readiness.

## Remaining gates

1. Independent review of this exact source diff and exact parent, including
   containment and all story ACs; no delivery or acceptance asserted here.
2. Separate explicit operator authorization for any protected inspection or
   provisioning, followed by an independently approved installation design.
3. Authorized fresh live source/input/VM/policy/evidence/accounting identity and
   namespace checks; preserve recovery unknowns/holds and consumed-sequence
   guards. Any pending, stopped, unknown or reused target fails closed.
4. Independent installation/replay isolation and budget gates, followed by
   action-specific human approvals; promotion and admission remain separate.

The implementation and offline preflight must not perform root, protected-asset
access, VM, replay, reconciliation, promotion, admission, production mutation,
merge, push, or runtime commit actions. A repository commit is a separate,
explicitly authorized parent action and is not runtime authority.
Source tests are not live execution proof. No lifecycle marker was invented and
no worktree cleanup was forced.
