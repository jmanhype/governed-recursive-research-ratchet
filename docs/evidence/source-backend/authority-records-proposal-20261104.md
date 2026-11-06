# Source authority records: bounded clarification proposal — 2026-11-04

PROPOSAL_ONLY: not an approved authority import, implementation, or story acceptance.
Scope: source/static review resolution for issuance, campaign-start and JIT review.
Inspected worktree HEAD419c312 (base2b60146); docs/findings absent. Exact-source
fallback, graph absent. No protected-path access, execution, provisioning or tracker work.

## 1. Existing normative definitions (do not replace)
All references below are relative to this directory unless prefixed `research/`.
Precedence: corrections > v3 > original JIT > base; independently accepted within
the archived integrated review's stated scope, not full implementation acceptance.
- Base=`grrr-executable-backend-design-v2-20261104.md`, §§2–3, lines49–133:
  InstallationV1, canonical inventory, H/I/N/U/raw/C/D, exact CampaignSpecV1,
  AuthorizationV1, ApprovalV1 and approval-registry-v1 already exist. ApprovalV1
  pins original authorization bytes, spec, campaign, issuance_id, age, floors,
  import_review; registry is descriptor-pinned immutable inventory, not consumption.
- `grrr-backend-jit-plan-amendment-20261104.md`, “Keep static approval separate”:
  CampaignPlanV2 readiness is not future executable Plan approval.
- `grrr-backend-jit-plan-amendment-v3-20261104.md`, §§1,3 (lines51–55,151–196):
  start evidence is exactly source/static review hashes; policy/review_anchor must
  approve verifier and JIT procedure; ReviewV2 exact schema and raw SHA256 exist.
  ReviewV2 is neither human approval nor source/static review nor postrun proof.
- `grrr-backend-jit-integration-corrections-20261104.md`, §2 (lines19–83):
  InstallationV2 adds reviewer_manifest_sha256; root immutable reviews/policy are
  UID322-readable, not writable; peer-authenticated reviewer/context RPC and
  irreversible request/result storage exist. Missing approved records must refuse.
- `research/capstone_contract.py:12–50,55–96,164–216` already defines Bindings,
  Gates, Anchor, Plan and strict input/grant/observation bindings. `review_anchor:H`
  is NOT an Anchor. `research/capstone_backend_contract.py:17–29` implements only
  ReviewV2 among backend types. Index `_spec` checks hashes/shapes, not approval;
  `_validate` explicitly refuses campaign events. Reviewer callback/expected/current
  seams in `capstone_review.py` / `capstone_review_service.py` are not resolvers.
Bounded gap: these five modules and archived top-level Markdown supply no exact
source-review/static-review/approved-policy schema or review_anchor resolution rule.
The following definitions are NEW proposals, not recovered normative schemas.

## 2. Proposed exact records and acyclic review references
Reuse C=common.canonical; H=lowercase64hex, Commit=lowercase40hex, N=int>=0 excluding
bool, U=existing U with installed operator additionally !=322, Codes=existing Codes.
All objects have EXACT listed fields; reject extras, duplicates, floats, unknown
schemas, invalid Unicode, noncanonical bytes, >MAX_WIRE, depth>=40 or >65536 nodes.
Every hash below is SHA256(exact C(object)), with NO omitted/selfhash field. Raw
documents/inventories referenced by H must resolve to original bytes and verify;
a hash, an assertion of approval, or caller-supplied JSON is never provenance.
Sets `[H]` are sorted unique; leaves remain ordered by spec, never sorted as sets.

`ApprovedPolicyV1` exact fields:
{schema:"capstone-approved-policy-v1",reviewer_identity:H,verifier_inventory:H,
jit_procedure_sha256:H,gate_contract_sha256:H,not_before_ns:N,expires_ns:N}.
reviewer_identity=SHA256(C({schema:"capstone-reviewer-identity-v1",uid:322,
verifier_inventory:H})); verifier_inventory equals InstallationV2 reviewer manifest.
jit_procedure_sha256 resolves the approved deterministic procedure's original bytes;
gate_contract_sha256 resolves the approved phase/check specification's original bytes.
Both must be independently approved imports, bound to the installed verifier closure;
arbitrary prose, known hashes, or fixture constants cannot authorize a verifier.
The approved gate contract retains exactly common.GATES and base §8 semantics;
it is not an executable plugin or a caller-editable list of waived checks.

`SourceReviewV1` exact fields:
{schema:"capstone-source-review-v1",phase:"source",verdict:"pass"|"fail",
driver_commit:Commit,runtime_base:Commit,source_manifest_sha256:H,
shared_bindings:<Bindings WITHOUT invocation_bytes_sha256>,policy_sha256:H,
reviewed_ns:N,expires_ns:N,evidence:[H],blockers:Codes}.
Shared bindings include exact decision bytes/package revision, all inventories,
assets/corpus/catalog/image/profile/accounting pins, not merely a Git revision.
Require driver_commit/runtime_base equal their shared_bindings members, policy equal
shared_bindings.policy, source manifest equal installed exhaustive source inventory.

`StaticReviewV1` exact fields:
{schema:"capstone-static-review-v1",phase:"finite-intent",verdict:"pass"|"fail",
operator_uid:U,campaign_spec_sha256:H,source_review_sha256:H,policy_sha256:H,
baseline_endorsement_sha256:H,reviewed_ns:N,expires_ns:N,evidence:[H],blockers:Codes}.
It approves exactly the referenced finite spec, including inputs/coverage/leaf order,
maxima and expiry, and the policy's JIT procedure, NOT unknown actual Plan bytes.
No authorization hash or installation hash here: adding them creates backward hash
cycles. Source review precedes static review; static review precedes authorization.
PROPOSE review_anchor=SHA256(C(StaticReviewV1)); no separate anchor record is needed.
Source/static pass requires blockers=[] and evidence resolving independent original
review artifacts; static evidence includes source_review_sha256. Empty/unresolved
approval evidence refuses even if the record itself is well-shaped and says pass.

## 3. Proposed resolver and trust/currentness contract
Stable installed root-owned immutable object store: propose fixed
`/Library/GRRR/capstone-v1/authority/objects/<H>` (name only; not accessed here).
Base root:wheel0755 directories/0444 single-link files, no writable ACL/symlink
ancestor; retain no-follow descriptors, check ownership/mode/inode/hash, recheck
identity before effect. UID320/322 read only; broker321 acquires no approval role.
Only existing independently approved root installation/import can populate it;
no service import endpoint, self-signing scheme or new human ceremony is proposed.
Root storage origin is necessary but NOT sufficient: authority must be reachable
from the accepted installed descriptor/approval registry and exact operator entry.
Immutable object presence alone never grants authority. Candidate artifacts remain
allegations; source/static acceptance originates in independently reviewed imports.

Resolution algorithm (return typed resolved records, never a bool):
1. Open validated InstallationV2 and original registry bytes; verify descriptor pin.
   Select unique ApprovalV1 by original authorization hash; check campaign/spec/raw
   equality, original operator/installation/baseline/window/maxima/leaves and issuance
   identity. Resolve import_review to independently accepted original import evidence;
   no aliasing it to a fixture H, ReviewV2, or generic pass flag.
2. Resolve Authorization.review_anchor as StaticReviewV1; policy via descriptor
   policy_sha256; source via static.source_review_sha256. Rehash original bytes and
   check schema/phase/pass/blockers. Match static operator/spec/baseline/policy;
   source policy/shared_bindings against complete spec and installed closure, including
   revision, decision input bytes, authoritative coverage/spec and every inventory.
   Policy hash equals spec.policy, shared_bindings.policy and descriptor.policy_sha256.
3. Verify independent import provenance for source/static/policy/procedure/gate
   evidence. Import evidence schema is not specified in the inspected contract;
   missing installed approved importer/evidence validation MUST remain a refusal,
   not an injectable `accepted=True`. Gate evidence uses approved phase-specific
   validators: these static records cannot make runtime/postrun gates pass.
4. Use trusted current clock: every interval has lower<upper; policy not_before and
   review reviewed_ns <= now < each expiry; static expiry<=source/policy/spec expiry,
   authorization expiry<=static expiry. Join current installed hashes and baseline.
   Verifier independently repeats static resolution, then authenticated retained
   context/Plan checks. Evaluator derives ReviewClient.expected from this resolver
   plus genuine current context; never derive it from request gates or returned review.
5. Preserve exact v3 start evidence=sorted(source_hash,static_hash). Issuance and
   campaign effects require fresh resolution under existing writer/gate exclusions;
   current context and final strict bind retain unchanged nonce/epoch/anchor/window
   checks. ReviewV2 expiry additionally obeys auth/grant/observation bounds.

No mutable revocation service is added. Revocation means current root-approved
registry/installation no longer accepts that original entry/policy/review; controlled
replacement is separately authorized installation, fences current work, and cannot
reset grants/holds/issuance/ledger lineage. Expiry, changed pins, uncertain provenance
or inability to establish currentness denies NEW effects. Cached request retrieval
returns original bytes/timestamps, never renews them; retries yield status, not owners.
Historical replay uses retained event-prefix original approvals/objects and event-time
evidence, not today's expiry as retroactive corruption or future approval as repair.
Replay proves recorded consistency, not present authority; live use rechecks current
installation/revocation/expiry. No replay path mints owner, grant, permit or send.

## 4. Implementation consumers and bounded acceptance tests (not run)
- `capstone_backend_contract.validate_record/decode_record`: exact new codecs and
  relational checks; retain v1 untouched. Add resolver dependency with installed
  factory distinct from explicitly NONPRODUCTION private-temp fixture factory.
- `capstone_backend_index._spec/_base/append_transition/_validate`: separate raw
  structural replay from authoritative issuance checks and future campaign reducer;
  bind original authority evidence to event prefix, including cached retry checks.
- `capstone_review.ReviewStore.review`: verifier must be installed deterministic
  verifier using resolver, not supplied caller verdict; get remains original retrieval.
- `capstone_review_service.ReviewHandler`, `ReviewClient.review_and_get`,
  `ReviewContext.validate_current` wiring: independent approved joins/currentness.
  Keep `capstone_contract.bind_inputs/bind_grant/bind_observation` unchanged.
Positive source test: construct real canonical policy/source/static/procedure/gate
artifacts in private-temp stores, resolve exact finite spec and anchor, then independently
validate JIT bytes through existing peer-authenticated fixture sockets and stored
original ReviewV2. Assert independently derived expected bindings, stable repeated
bytes/expiry, all source gates truthful, NONPRODUCTION identity, zero protected access.
This tests source mechanics only, not actual root import/UID322/live approval.
Adversarial tests: wrong spec/leaf/order/input/revision/closure/policy/procedure/gate,
wrong raw hash versus selfhash, wrong phase, extra fields/duplicate keys, missing
import provenance, copied reviewer JSON, substituted expected map, source/static
fail, expired/revoked approvals, changed installation or context/anchor, cached pass
after expiry, future evidence used for past event, and replay trying to restore owner.
Every refusal precedes claim/reserve/send, preserves holds and does not remint bytes.

## 5. Actual remaining decisions; no fabricated approval
Operator/design acceptance of these NEW record schemas and fixed object-store path
is required; concrete approved imports/verifier procedure remain absent, not presumed.
Base §3's import_review bytes have no typed format here: select an existing accepted
import evidence contract or explicitly approve one before positive authority tests.
Also resolve the existing full-byte construction cycle: Installation pins registry;
registry embeds Authorization raw; Authorization pins installation_sha256. No supplied
text defines an exclusion hash. A reviewed acyclic installation commitment definition
is needed; do not silently omit fields, use placeholders, or claim positive full issuance.
Positive standalone resolver fixtures can precede that decision; full integrated
issuance/start acceptance cannot. This proposal changes no existing accepted hash rule.
All original12AC,11gates,7journeys remain; no whole-story/live acceptance is claimed.
