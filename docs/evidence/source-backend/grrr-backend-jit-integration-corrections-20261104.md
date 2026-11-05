# JIT source integration corrections - 2026-11-04

CORRECTIONS: READY_FOR_INDEPENDENT_REVIEW
This delta applies to v3 SHA256
3ab960191613b2e10018f5c9444532080e9757693c49393f888c6beff0793e09
and its two pinned base inputs. No source implementation or execution grant.
Originals remain unchanged. Resolves source compatibility and freezes the small
local reviewer boundary required by v3, not a new external integration.

## 1. Existing Ledger envelope compatibility
Campaign event format remains `capstone-campaign-event-v2`, but envelope version
is INTEGER **1**, injected by existing Ledger._append. Version2 in v3 section1
is superseded. No Ledger or journal-v1 schema/API/replay changes are permitted.
The record's format discriminates the v2 reducer. Evidence sets specified as
exactly two/three hashes always mean lexically sorted unique sets, not listed
tuple order; named object schemas disambiguate their types before use.

## 2. Exact installed reviewer boundary
An independently reviewed deterministic local verifier is UID322, distinct from
operator, evaluator320 and broker321. It is not the optimizer or an LLM. New
installation validation denies operator_uid322 without changing legacy U schema.
Production factory validates actual kernel/process identities; callers cannot
choose a reviewer UID or endpoint. No provisioning is authorized by this design.

Replace ONLY the uninstalled descriptor type with InstallationV2: exact base
InstallationV1 fields, schema literal `capstone-installation-v2`, plus
reviewer_manifest_sha256:H. The base fixed descriptor pathname stays unchanged;
new code refuses an old descriptor, never upgrades it. Reviewer inventory covers
its complete interpreter/import/verifier closure and approved JIT procedure.
Root-owned immutable registry/policy/static/source-review objects are readable
by322, not writable; their exact hashes are inventory/approval-bound. Verifier
has no accounting writer, ledger writer, runner socket, launch authority or key.

Fixed sockets under base fixed ipc root: reviewer.sock owned322, accepts ONLY
kernel UID320; review-context.sock owned320, accepts ONLY kernel UID322. They
are separate from operator data/control and broker channels, exact restrictive
root-approved ACLs/modes; no0666 default. Reviewer durable root is fixed
/Library/GRRR/capstone-v1/reviewer, owner322 mode0700. Evaluator/operator cannot
write/read its files directly; they retrieve records only through peer-checked
RPC. No caller root/path/URL/role/UID override. Actual OS provisioning and ACL
qualification are separate live gates, never inferred from unprivileged fixtures.

Strict reviewer requests (version2 is wire version, not Ledger version):
- {action:"review-plan",version:2,campaign_operation_id:H,leaf_id:H,
   campaign_plan_raw:raw,actual_plan_raw:raw,request_sha256:H}.
  request_sha256=D("jit-review-request-v2", request omitting only that field).
- {action:"get-review",version:2,request_sha256:H}.
Response is existing single ok/error envelope; ok={request_sha256:H,
review_sha256:H,review_raw:raw}. Normal bytes/checks use MAX_WIRE, strict duplicate
and enum rejection, bounded absolute timing from installed timing_policy, peer
authentication BEFORE payload/allocation. Oversized input is refused, not split.
ReviewV2 schema/content is exactly v3. No additional grant or pass boolean.

Read-only context RPC320 accepts ONLY
{action:"review-context",version:2,campaign_operation_id:H,leaf_id:H,
actual_plan_bytes_sha256:H,nonce:H,service_epoch:H}.
Reply is {schema:"capstone-jit-context-v2",campaign_operation_id:H,leaf_id:H,
actual_plan_bytes_sha256:H,observation_raw:raw,anchor:Anchor,service_epoch:H}.
Evaluator resolves the live owner and selected finite leaf, original retained
observation, exact prospective Plan bytes/hash and current static joins. Unknown,
wrong leaf, stale epoch/nonce, terminal/stopped campaign or changed anchor refuses.
Context registration is in-memory during run only, does not consume authority,
append events or mutate accounting; it cannot survive/revive worker loss. It is
never available to operator/candidate. Dedicated handler/thread capacity prevents
a synchronous review request from deadlocking its own context lookup. No ledger
or launch gate is held while waiting for reviewer RPC. Final prebind remains the
unchanged strict freshness check, so intervening stop/writes still refuse.

Verifier independently resolves approved root registry/policy/source/static
reviews, validates request/root/leaf/Plan hashes, and queries the authenticated
context. It compares exact original receipt and anchor, not caller assertions.
Only then it performs v3 deterministic checks and stores a ReviewV2. It cannot
substitute that Review for source/static/human approval or runtime result review.
Missing approved review procedure/verifier/records refuses, never creates them.

Reviewer stores immutable original request/result objects and a crash-recoverable
hash-linked request-to-review index in its OWN storage, objects fsynced before
index reference and directory fsync. Same exact request returns original bytes
without extending timestamps, including an expired/failing review. Changed bytes
under same key refuse; intent-only/corrupt/uncertain index refuses and never
remints. Retrieval authenticates322 before any request is sent and verifies both
hashes/bindings/phase/expiry; possessing copied review JSON is not provenance.
Review writes do not change ledger/accounting/grant anchor. Meter elapsed trusted
review cost inside preapproved review maxima; unknown duration preserves bound.

Source fixtures use distinct private-temp stores and real peer-authenticated
sockets with actual unprivileged UID, explicit NONPRODUCTION labels. They never
patch production identity checks or claim322/ACL proof. Add source tests for both
RPC phases, no deadlock, changed/stale contexts, expired repeated review, reviewer
index crash/corruption, and zero protected metadata access. Include the reviewer
implementation/tests in the ONE integrated backend task; no extra report stage.
