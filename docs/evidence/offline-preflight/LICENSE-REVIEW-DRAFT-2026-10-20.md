# GRRR-90te local-use license review — DRAFT, BLOCKED

This is a technical compliance triage, not legal advice or operator approval.
The draft does not authorize a VM invocation. No final `license-review.json`
was created; `operator_uid` is deliberately null and the decision is `blocked`.

## Exact binding and evidence

- Worktree HEAD inspected: `6c7b93e`; prior commits `b50f074`, `90f4da2`.
- Inventory: `.tmp-sr_pm/offline-preflight/assets-20261020-1/inventory.json`.
- Inventory SHA-256: `dc11522600eae2424bf3fce4d124d401db85a3566fa63968d2a6a2ec32f98fcb`;
  independently matched to `asset-receipt.json`.
- Draft: `.tmp-sr_pm/offline-preflight/assets-20261020-1/license-review-draft.json`.
- Draft SHA-256: `4d3e93ebb6ac205225e7521c951a93baa64335a899710619ae3f593f7b3cf0c6`.
- Scope: local offline preflight only; no redistribution.
- All 159 component keys match the launcher's expected set exactly: pinned vlt,
  Go toolchain, 101 Alpine APKs, 56 host images. All four known risks have explicit
  dispositions; every component/risk rationale exceeds 20 characters.
- Pinned vlt LICENSE hash verified against inventory; Apache-2.0 header and
  go.mod inspected. No external modules are declared; actual closure is untested.
- All 26 distinct installed Homebrew formula files match inventory text/hashes,
  covering 31 host images. Formula license expressions retain AND/OR structure;
  a formula-wide license is not silently narrowed to a particular dylib.
- Remaining 25 host images are Apple/system runtime, build `26A428`, used only
  in place. Per-image dyld-cache hashes are unavailable, as inventory declares.
- Go embeds 41 notice-name matches: 36 text records and five DER certificate
  test fixtures. No separate `toolchain-notices.json` is present. The draft uses
  embedded records and distinguishes incidental certificate names from licenses.

## Counts

Disjoint classifications: **54 permissive local-use; 80 boundary-controlled;
0 unknown-provenance; 25 Apple/system**. These are recommendations within the
draft, not approvals. Exact upstream evidence resolves the two earlier provenance
gaps: current ppp chat is MIT with historical public-domain origin; IANA tzdata
has a public-domain dedication with specified BSD-3-Clause exceptions. See
`LICENSE-PROVENANCE-ADDENDUM-2026-10-20.md` for hashes and decisive statements.

License-family occurrences below overlap for mixed expressions and are counted
per exact component (including formula-wide alternatives, not selected branches):

| Family | Components |
|---|---:|
| GPL | 54 |
| LGPL | 35 |
| BSD (including IANA named-file exception) | 33 |
| MIT (including current ppp chat source) | 24 |
| ISC | 10 |
| SSH-OpenSSH | 8 |
| Apache | 6 |
| Public-Domain metadata, including mixed and historical chat discrepancy | 5 |
| X11 variants | 3 |
| Python / Zlib | 2 each |
| MPL / AFL / IJG / Unicode / libpng | 1 each |
| Apple/system | 25 |

No AGPL, Business Source License, noncommercial or source-available restriction
was identified in the captured license expressions. This is not a negative
finding for every source file or a redistribution audit. Go also retains
OpenSSL/SSLeay and patent notices, with conditional boringcrypto terms.

## Boundary controls

Use packages only as the existing local host runtime or unmodified offline guest
tools. No source/binary redistribution, public appliance/media publication,
project linking/incorporation, new network service, dependency download or
new feature/license branch is covered. Existing Go standard-library compilation
for the isolated disposable preflight is the intended toolchain use; the
no-project-linking restriction forbids incorporating host/APK libraries into
the research project or shipping resulting artifacts.

Preserve licenses, notices, disclaimers, patent terms and upstream/aports
references. Existing host QEMU dynamic linking is not new project integration.
Private GPL use need not become public source publication, but distribution and
other scope changes require fresh review. See the [GNU GPL FAQ](https://www.gnu.org/licenses/gpl-faq.en.html#GPLRequireSourcePostedPublic).

Apple components remain governed by the applicable installed macOS terms; this
review grants no extra extraction, transfer, virtualization or redistribution
rights. Apple's [SLA guidance](https://www.apple.com/legal/sla/) warns that online
terms can differ from the agreement supplied with the installed product.

## Blockers and risk dispositions

1. **Public-domain provenance blocker resolved for this local-use triage.**
   Exact ppp and IANA source archives were checked against the SHA-512 values
   verified by the parent against pinned Alpine APKBUILD files. This reviewer
   independently rehashed all three archives and read their decisive source
   notices. Current chat.c MIT notice takes precedence over the broader historical
   Public-Domain description. Mixed ppp packages retain their full expressions;
   public-domain is never imputed to the whole mixed package. IANA exceptions
   remain visible. This is still not a file-level redistribution clearance.
2. **Installed macOS entitlement/terms need operator confirmation.** The reviewer
   cannot attest acceptance or entitlement for build 26A428 on the operator's
   behalf. No additional rights are inferred from successful installation.
3. **Dependency closure remains deferred, not proven.** After separate license
   approval and all existing gates, the authorized offline preflight may measure
   `go list/test`. Stop on missing/uncatalogued dependencies; never download or
   widen scope. This draft does not assert any execution result.
4. **Notice evidence is bounded.** APK classifications use exact captured metadata,
   not a file-by-file source audit. Some Homebrew inventories have no collected
   notices; that is not a waiver. Preserve installed notices and source references.
   Go certificate testdata is not a separate license text; retain as supplied,
   do not redistribute. Do not enable boringcrypto under this draft.

## Operator decision requested

**Do not approve the current blocked draft for execution.** Public-domain
provenance has now been resolved; confirm applicable installed macOS
terms/entitlement. Then request explicit operator authorization
for this exact inventory hash and only the already bounded local offline
preflight, accepting all no-redistribution/no-new-linking/notice-retention
conditions. Record a real operator UID and authorization reference in a separate
final artifact only after that decision. Approval must not be inferred from the
earlier build-profile approval or from this review.

No source, implementation, VM state, nd story, commit or push was changed by this
review. This document and draft are the only review deliverables.
