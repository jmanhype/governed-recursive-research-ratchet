# Exact-source license provenance addendum — GRRR-90te

This resolves the public-domain provenance gap only. It does not approve the
inventory or authorize execution. macOS terms/entitlement confirmation and
unexecuted offline dependency closure remain visible in the blocked draft.

## Verification method

The parent retrieved the exact upstream archives and verified their SHA-512
values against the pinned Alpine APKBUILD files below. This reviewer separately
ran `shasum -a 512` on all three supplied local archives and read the decisive
archive members with `tar -xOf` (no extracted executable was run). All three
hashes matched the parent's pinned-build evidence. The APKBUILD retrieval/check
itself is parent evidence, not claimed as independently repeated here.

The inventory binding remains
`dc11522600eae2424bf3fce4d124d401db85a3566fa63968d2a6a2ec32f98fcb`.
Temporary archives are evidence inputs, not redistribution deliverables.

## PPP 2.5.2 / Alpine r0

- Aports commit: `6268112dcce642a1d44bc78a174907ac7dbb6d51`.
- [Pinned APKBUILD](https://git.alpinelinux.org/aports/plain/main/ppp/APKBUILD?h=6268112dcce642a1d44bc78a174907ac7dbb6d51).
- [Exact upstream archive](https://download.samba.org/pub/ppp/ppp-2.5.2.tar.gz).
- Local input: `/private/tmp/grrr-license-evidence/ppp-2.5.2.tar.gz`.
- SHA-512: `2c49d411818632a750f52b187c0ee421e9fcc1530c717abacce61e76aa8b296ce09fb142bc202696c0e0ac5570dd12ee649267921b756b6572ae514ce961d1e6`.

The exact APKBUILD labels the chat subpackage `license="Public-Domain"`.
However, `ppp-2.5.2/chat/chat.c` begins:

> SPDX-License-Identifier: MIT

It identifies copyright 1995–2024 Paul Mackerras and says:

> based on the original public-domain version by Karl Fox.

The full MIT permission, notice-retention condition and warranty disclaimer follow
in that source file. Top-level `ppp-2.5.2/COPYING` instead says:

> Pppd, pppstats and pppdump are under BSD-style notices. Some of the
> pppd plugins are GPL'd. Chat is public domain.

**Disposition:** classify `ppp-chat-2.5.2-r0.apk` as **MIT with historical
public-domain origin**, explicitly retaining the discrepancy with Alpine metadata
and top-level COPYING. Preserve the current source copyright/MIT notice; do not
erase it on the theory that the entire current program is public domain.

For `ppp-daemon`, `ppp-openrc` and `ppp-passwordfd`, retain each inventory entry's
full mixed SPDX expression and boundary-controlled local-use classification.
The source COPYING directs attention to individual source notices; it does not
relicense the entire package as public domain. No assertion of GPL compatibility
for an arbitrary new combined work or redistribution is made.

## IANA tzdata/tzcode 2026d / Alpine r0

- Aports commit: `94fecc1faddf3393d2a5ff65169994edaea6d518`.
- [Pinned APKBUILD](https://git.alpinelinux.org/aports/plain/main/tzdata/APKBUILD?h=94fecc1faddf3393d2a5ff65169994edaea6d518), declaring `license="Public-Domain"`.
- [Exact tzdata archive](https://www.iana.org/time-zones/repository/releases/tzdata2026d.tar.gz).
- Local input: `/private/tmp/grrr-license-evidence/tzdata2026d.tar.gz`.
- tzdata SHA-512: `1a27de5af50bbc28a2f64c506ab3678b09d9e5ab6c118f39eb38bb823aa8f57069bf5e465848e71df8274c6b8bcd0fc736a88107e5792d816a1db5d867cbc219`.
- [Exact tzcode archive](https://www.iana.org/time-zones/repository/releases/tzcode2026d.tar.gz).
- Local input: `/private/tmp/grrr-license-evidence/tzcode2026d.tar.gz`.
- tzcode SHA-512: `42d4b37549a35893187851187cae93c811928f808c24ac0003bf0b782837d0934f2f7da7e93a0417273c7e0a66f79e9d512290ae4811cb73a7d02b62b3f0fed1`.

Both exact archives contain the same `LICENSE` statement:

> Unless specified below, all files in the tz code and data (including
> this LICENSE file) are in the public domain.
>
> If the files date.c, newstrftime.3, and strftime.c are present, they
> contain material derived from BSD and use the BSD 3-clause license.

**Disposition:** `tzdata-2026d-r0.apk` is permissive local use based on the
exact-source public-domain dedication, retaining the named BSD-3-Clause
exceptions wherever present. Do not treat the metadata shorthand as a waiver
of those exceptions. Preserve licenses and upstream source references.

## Remaining decision boundary

The draft remains `blocked`, with null operator UID and no authorization claim.
Operator confirmation of applicable installed macOS terms/entitlement is still
needed before separate final license authorization. Dependency closure remains
unmeasured: any later authorized offline preflight must fail closed on missing
or uncatalogued dependencies, with no downloads or scope expansion. No VM was
run and no final launcher review was created.
