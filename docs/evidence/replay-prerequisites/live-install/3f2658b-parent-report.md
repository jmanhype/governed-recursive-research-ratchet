# Parent-mediated replay prerequisite installation — 3f2658b

## Provenance and scope

This report preserves facts supplied by the coordinating parent after its live
installation/provisioning and readback. The developer worker did not repeat the
privileged commands, inspect protected contents, or run root, QEMU or a VM.
Raw privileged transcripts were not supplied with this handoff; the observations
below are explicitly parent-reported, not an independent worker verification.

Status: **GRRR-w1lt remains in_progress**. Namespace provisioning succeeded;
service/replay lifecycle (AC #4) remains **not-run**. No delivery or acceptance.

## Failed predecessor retained

The first installed 6e89e6 preflight rejected the legitimate
`-2 /usr/sbin/distnoted` UID before namespace creation. The parent preserved the
old package, launcher, review and failed-install record at:

`/Library/GRRR/replay-install-history/6e89e6b89aebb0d6a08ce61b1898a299158da43a/`

This failure is not overwritten or relabeled as successful provisioning.

## Renewed review and exact identities

| Item | SHA-256 or commit |
|---|---|
| Approved source commit | `3f2658ba29d6fa6a6177ea83b98f75245e4cb20d` |
| Independent review_reference | `1eac14967d28e1807cac87fdbeb3654aa4893de03e58fd8bb7776ec99213273b` |
| Installed launcher | `2ba4b712044470c7c378cf487b9a10a47ad9ec1c8361c1db7a7deb49dc6aca55` |
| replay_prerequisites.py | `85f7a14d271688d554f1af4e0e539a084fd66fd9bea7920cfdf712dd2d20a237` |
| Canonical policy | `355e6f7d9dd0a65817cdc1a6421fba6347f5075c40f4a456ed601e753f14a77a` |
| Runtime identity | `59073b8282cb4333c7719d4eac417c061c82f534bf11873d26bf2b26f7531526` |

The parent reported an exact nine-file code inventory and exact fourteen-file
input inventory matching the installed contract. No raw inventory listing is
reconstructed here.

## Successful sanitized parent command

```sh
/usr/bin/env -i PATH=/usr/bin:/bin LC_ALL=C /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/bin/python3.9 -I -S -B /Library/GRRR/bootstrap/replay-root-prepare --prepare
```

Exact supplied result:

```json
{"execution_authorized":false,"namespace":"/Library/GRRR/independent-replay","replay_dispatch":"not-run"}
```

Parent readback confirmed namespace/root-private/code ownership and modes,
evaluator UID 320 ownership of policy, expectations, budget, reservations and
ledger, and runner UID 321 ownership of only the executor directory.
Root code remained protected. The prepared record read back:

```json
{"root_installation":"prepared","replay_dispatch":"not-run","execution_authorized":false,"verdict_engine":"not-installed"}
```

This is prerequisite namespace preparation, not a ReplayReceipt or authorization
to start replay. Corpus fixture ledgers have not been relabeled.

## Parent-reported identity and integrity probes

| Probe | Observed outcome |
|---|---|
| Evaluator UID 320 reads policy | Exit 0; hash matched |
| Runner UID 321 reads evaluator subtree | Denied |
| Runner UID 321 reads private subtree | Denied |
| Evaluator UID 320 reads private subtree | Denied |
| Operator UID 501 reads evaluator subtree | Denied |
| Runner UID 321 stats executor directory | Exit 0 |
| Runner writes/truncates root code | Denied; code hash unchanged |
| Evaluator writes/truncates root code | Denied; code hash unchanged |

The write-probe shell emitted the expected `getcwd` warning because the root
parent shell's working directory was inaccessible to the reduced identity.
That warning alone is not denial proof: the reported file-write denial and
unchanged code hash are the evidence. No unreported numeric denial exit codes,
probe command strings or raw output have been fabricated.

## Acceptance-criteria boundary and remaining work

- AC #1: approved policy bindings retained; parent reports installed policy hash.
- AC #2: renewed independent review and live UID-separated namespace preparation
  now have parent-reported positive evidence.
- AC #3: parent command passed protected preflight and namespace readback/probes.
- **AC #4: services, authenticated replay lifecycle, VM isolation/cessation and
  independent replay/ReplayReceipt remain not-run. Verdict engine not installed;
  execution_authorized remains false.**
- AC #5: story remains in_progress; no delivery/acceptance or fixture-ledger
  relabeling. GRRR-z3w9's prerequisite dependency is not closed by this report.

The source tests remain those recorded at 3f2658b: 20 focused and 186 full
no-guest tests passed on each required Python. This documentation-only evidence
commit does not claim a new code test run.

## Integrity

This versioned report is frozen by its sibling SHA256SUMS and Git commit.
Verify with `shasum -a 256 -c SHA256SUMS` from this directory. Future observations
must be separate reports rather than edits to this record. No OS-level immutable
flag or independent cryptographic attestation by the worker is claimed.
