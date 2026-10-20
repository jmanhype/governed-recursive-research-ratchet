# Exact source transport repair

Attempt `attempt-20261020T175506Z-fa0b9915` passed isolation and failed the full
source checksum gate on eight paths, including hidden paths and case-sensitive
names such as LICENSE and README.md. This is transport name loss/translation,
not evidence that all eight names were hidden. The complete failed receipt and
all preceding attempts are preserved unchanged.

Source is now transported as visible `source.tar`, containing exactly the 52
pinned Git inventory records, including dot paths, original case, byte hashes,
and Git executable modes. No .git or untracked files are included. Preparation
reads the archive back to verify all names/modes/hashes; the updated image was
also read back independently with libarchive and all 52 records verified.
The unchanged source.sha256 path set equals the archive member set. Guest
extracts to fresh /work/source and still runs the complete sha256sum gate.

The old loose source tree was moved outside media to source-loose-v3-preserved;
it is not shipped as authoritative transport. Previous image/receipt preserved
as input-v3.iso and asset-receipt-v3.json (v1/v2 also retained). No deletion,
privileged execution, source execution, or license-scope expansion occurred.

Image SHA-256: `797b99fad8534f2a49a7dc7954d0f008abd36941e361ef0e4167dd5698bd2220`.
Receipt SHA-256: `024d7d3a2f56e5942c17494392c49625eb638a3deaa6189d9711fe938c312c9f`.
Source tar SHA-256: `e644b9848b306f158a2367293dd96c66dac2bed97c0dd42891db007667c0ae7e`.
Inventory/license review/profile remain unchanged. Root launcher derives the
new image binding from the receipt. Free space after repack: 15,391,207,424 bytes;
parent must recheck the 15 GB gate immediately before running.

29 unit tests pass, Python compilation and shell syntax pass, pvg verify passes
on two changed Python files. Real offline builds remain unproven; not delivered.
