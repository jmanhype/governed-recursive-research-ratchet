# Independent replay v4 continuation — blocked, not delivered

This supersedes the v3 review's accounting-recovery prerequisite description,
not its historical measurements. Epic GRRR-2t3h at 38f33c9 includes accepted
GRRR-d8ji stop-only recovery. The recovery action is complete; **spendability
reconciliation and replay are not authorized**. No installation or execution
command in earlier replay documents is permission to act.

## Exact boundary

The parent reports active v3 SHA256
`9c5194dd12ff7601917fcccc293c459db09a41da8bad9fa9983cbef618d453f8`,
receipt `6d3d5b092c0ee8273a657c83823d8465b215f2b1b66ec627dfde2d96b21fe587`,
original database inode 682589447 and stopped=0. These are parent-provided live
references, not a new protected verification by this developer. The reviewed
contract retains historical_unknowns=unresolved, spendable=null,
allowed_mutations=[], execution_authorized=false. All v3 runtime mutations are
denied, including reserve, meter, settle, halt and SQL/BLOB writes. Clearing stop
does not grant any replay allowance or authority.

`replay.preflight()` now explicitly refuses v3 before reading replay inputs or
opening a budget. Version 2 and unknown versions remain denied. The launcher
hash map includes the accepted accounting_recovery.py transitive dependency,
accepted registration/budget bytes, merged cessation implementation, and updated
replay bytes. The sole merge conflict was the launcher's code hash map; both
replay-specific additions and accepted cessation/security changes were retained.
No accepted accounting source or tests were modified relative to the epic.

## Remaining parent gates

1. Separately reviewed and explicitly authorized reconciliation successor if
   replay requires spendability or runtime accounting writes. Do not manufacture
   allowance, reset history, release holds or reinterpret unknowns.
2. Fixed capacity floor, dedicated evaluator/runner identities, immutable exact
   package installation and independent review of final replay bytes.
3. Separate exact operator replay authorization and parent-mediated fresh VM
   execution for all four modes, then actual retained receipts and complete gates.
4. Independent PM acceptance. Admission, promotion and production mutation remain
   disabled; passing unit tests cannot satisfy live replay ACs.

This dispatch did not run root/sudo, QEMU/VM, identity setup, reconciliation,
protected mutation, replay, admission, promotion or push. The read-only live test
entrypoint only failed its actual UID/GID prerequisite; it did not launch guests.
Full no-guest verification and unresolved setup errors are recorded in
`evidence/independent-replay/v4-no-guest/REPORT.md`. All five ACs remain incomplete.
