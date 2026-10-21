# Accounting evidence request — metadata only

This request authorizes no migration, settlement, stop release, hold release, reservation, dispatch, or execution.

## Pinned basis

- Manifest SHA-256: `8c64d70cc0f3b903620ed45094133ceffaf5e48107427fcfc2204b73daa06270`
- Manifest decision: `blocked-ambiguous-history`
- Parsed inventory: **259 artifacts / 110 events**.
- Canonical `REQUEST.json` SHA-256: `e597a4ce884d04080682d884f1ae121bad981aa01917bfd2544a88373e6a2b71`

## Global requests

1. **Original reservation mappings:** provide authoritative mappings for **94 events**.
2. **Paid-service proof:** provide authenticated service-account proof for **62 events**.
3. **All-event accounting proof:** for all **110 events**, provide principal, request key, stage, currency, UTC start/end/overlap intervals, trusted meter receipt, and trusted settlement receipt.
4. **Historical campaign stop:** provide the authoritative campaign stop-state history, scope, and resolution provenance.

The 110 event-specific records, including exact missing-field lists and preserved source references, are in `REQUEST.json`.

## Evidence standard

Acceptable evidence is an original authenticated record with identities, UTC intervals, overlap computation, and provenance. Inferred, reconstructed, substitute, or zero-filled values are not acceptable. A retained source pointer is only an available reference and is never a meter, settlement, reservation, or stop receipt.
