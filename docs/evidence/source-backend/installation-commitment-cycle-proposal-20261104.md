# Installation commitment cycle: proposed repair

**PROPOSAL ONLY.** This does not change the accepted schema, authorize an
installation, approve a contract, or enable an evaluator. Independent design
acceptance and compatibility review are required before implementation.

**REVIEW RESULT: GAPS_FOUND.** Independent review of the previous proposal
bytes (SHA-256 `35ec8a1da117af5cb4f9905faec5995bb72db2eafcea287cc3f66837e645baef`)
found the projection is not ready for implementation. It needs exact versioned
schemas and hashing, no mixed v1/v2 interpretation, exact final-pair provenance,
cross-installation replay protection, and a separately authorized migration
contract. The review did not approve the following candidate.

The accepted base design makes a descriptor contain the hash of a registry;
the registry embeds authorization bytes; and those authorization bytes
contain the hash of the descriptor. Full-byte hashes therefore have no practical
deterministic construction order. This is a dependency cycle, not evidence of
an existing valid installation or a reason to ignore any check.

## Candidate acyclic construction

1. Define an exact canonical installation core containing every InstallationV2
   field except `authorization_registry_sha256`.
2. Introduce a versioned authorization whose `installation_core_sha256` is the
   SHA-256 of that exact core. Preserve legacy v1 interpretation; do not silently
   reinterpret any prior authorization bytes.
3. Construct the canonical registry embedding those exact authorization bytes.
4. Construct the final InstallationV2 descriptor with the registry hash.

The runtime must verify exact canonical formats, the final descriptor-to-registry
hash, the selected entry-to-authorization raw hash and bytes, and the core hash
computed by omitting **only** the registry field. It must reject duplicates,
noncanonical inputs, missing required fields and all missing review gates.
The complete final descriptor and registry pair must have independently verified
root-import provenance. Sharing a core hash alone never authorizes a different
registry or installation. Source/static review and provenance obligations remain
independent of candidate assertions.

## Required design and test decisions

- Verify historical v1 compatibility and exact normative schema/versioning.
- Specify independent import provenance and reviewer identity, not just hashes.
- Test deterministic construction; any changed core field; any changed registry;
  missing/duplicate authorization; noncanonical data; and a different final
  descriptor/registry pair without approved import provenance.
- Reject missing or skipped mandatory verification. Do not use fixture records,
  caller booleans or the existence of a file as approval.

This proposal is source-only. It does not access `/Library/GRRR`, enable real
protected authority, reconcile costs, execute replay, or merge or push code.
