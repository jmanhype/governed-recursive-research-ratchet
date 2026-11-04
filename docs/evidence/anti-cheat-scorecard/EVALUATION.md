# Sean Chatman Anti-Cheat Scorecard evaluation

## Decision

**Recommendation: advisory only.**

Do **not** make the scorecard a trusted GRRR evaluator or mandatory verification
gate. It can be useful as a bounded textual-cheat scanner after a future wrapper
enforces clean input, output validity, coverage accounting, stable redaction, and
reviewed triage rules.

## Pinned source

- Repository: `seanchatmangpt/anti-cheat-scorecard`
- Tag: `v26.8.29`
- Commit: `5271351d079f79634de2f8b91970b80daf9bcb86`
- Release date: 2026-08-29
- License: Apache-2.0
- Module: `github.com/ossf/scorecard/v5`
- Source Go directive: 1.25.6
- Local builder: Go 1.26.7
- Built binary SHA-256:
  `d6df6a07b5d818bf11bed026455acf531307afb39c92bf7b58cae0c93883ee4e`

The release advertises 52 detectors. Source inspection and the blank-import
registry found 52 detector packages across seven categories. The README still
says 50, so the release metadata is the better count.

All 53 pattern-related Go packages (52 detector packages plus the aggregator)
passed their tests. Test log SHA-256:
`bbfe64ec1c98b9f55da6243b896415d2c621815481d0cf7cffeb1106dcd7ec0a`.

## Real GRRR-gge0 scan

Target was the clean accepted adaptation worktree at commit
`cf3eb55422ba18898541318c138cd82543419d12`.

- Exit code: 0
- Elapsed: 79.67 seconds
- Output size: 1,894,849 bytes
- Output SHA-256:
  `f56ee077318bea77d1678e5666b5a06904ff5651477f9a8a9f630d923e1f418f`
- Check score: **1/10**
- Detail rows: **5,487**
- Warning rows: **5,486**
- Informational rows: **1** (“no semantic-web-integrity patterns detected”)

Pattern distribution:

| Pattern | Count |
|---|---:|
| lockfile-checksum-mismatch | 4,599 |
| claim-verified-without-run | 230 |
| error-message-wrong-context | 172 |
| unverified-benchmark-numbers | 147 |
| claim-alive-without-receipt | 131 |
| self-contradicting-status | 88 |
| overclaiming-superlative | 51 |
| non-chicago-evidence | 36 |
| interaction-only-assertion | 11 |
| misleading-function-name-vs-body | 10 |
| placeholder-lorem-ipsum-in-code | 8 |
| six other one-count patterns | 6 |

The dominant `lockfile-checksum-mismatch` result is a false-positive class: the
scanner treats repeated `digest` keys in multi-object accounting manifests as
one lockfile subject. That single pattern creates 83.8% of all findings.

## Five-file adaptation subset

Scanning only the five files added by GRRR-gge0 took 0.15 seconds and produced:

- Score: **7/10**
- Seven detail rows
- Two warnings
- Output SHA-256:
  `9b6e5e04fdc52208670d74ba53c63ad20146badcf7c36ac68cb57e5ea0c284a2`

Warnings:

1. The Markdown summary says “completed” without a receipt on the immediately
   adjacent lines.
2. A deliberately synthetic test fixture is identified as non-Chicago evidence.

This is much more usable than the whole-history scan, but still illustrates the
local-context limitation: both findings require operator triage and are not
verified defects.

## Controls

### Seeded textual cheat

A small fixture containing an unimplemented function, a pass-only function, and
unsupported “verified/complete/100%” claims was detected:

- Score: 7/10
- Five warnings
- Output SHA-256:
  `af70a5118096b3d792e381c07bb5711521d81e53b9d3b34ab3506902ef3fcdd3`

Detected:

- claim-alive-without-receipt
- claim-verified-without-run
- overclaiming-superlative
- python-hollow-function
- python-notimplemented-shipped

This proves real advisory signal.

### Absent input

The scanner printed an error for a nonexistent local path but still exited **0**
and created no output. A GRRR wrapper must classify this as failure.

### Empty input

An empty eligible root exited **0** and returned a perfect **10/10**, claiming
“no LLM-cheat patterns detected across any category.” This exposes the missing
coverage ledger. Empty input must never be allowed to look like a passed gate.

### Rerun stability

Two subset scans were semantically identical after removing the output timestamp,
but raw hashes differed because the date changed. Durable evidence must use a
normalized semantic hash or redact/fix the timestamp.

## Reproduction command appendix

The exact command sequence, including checkout, tests, build, target identity
check, live-target scan, subset construction, seeded fixture, absent control,
empty control, and rerun control, is retained in
`evaluation.json` under `reproduction_commands`. Each control’s exit code and
output disposition is recorded beside its result above.
The pattern-test command and binary-build command likewise exited 0; their exact
commands, byte counts, and hashes are recorded under `reproduction_evidence`.

## Why it must not be a trusted gate

1. Findings do not produce a nonzero exit.
2. Missing input can exit zero without output.
3. Empty input can score perfectly.
4. No scanned-file, unreadable-file, or coverage count is emitted.
5. Local mode scans the live filesystem, including ignored/untracked files.
6. It has major false-positive classes against multi-object evidence manifests.
7. Its evidence rule only looks nearby, missing immutable receipts referenced
   elsewhere.
8. Its score is category-based, not severity- or confidence-calibrated.
9. Output contains timestamps and local paths.
10. Clean means “no known textual pattern matched,” not “correct.”

## Future advisory wrapper requirements

A later integration story may proceed only if it:

1. builds the pinned tag once and records the binary hash;
2. exports a clean Git tree at an exact commit rather than scanning a live worktree;
3. verifies the input path and commit;
4. requires valid JSON output;
5. independently computes eligible/scanned file counts;
6. records elapsed time, output bytes, output hash, and normalized semantic hash;
7. redacts local paths and normalizes timestamps;
8. applies reviewed suppressions for GRRR evidence formats;
9. treats scanner absence/errors as wrapper failure;
10. keeps every finding advisory.

No Anti-Cheat Scorecard output may replace independent replay, trusted
evaluation, accounting, human approval, contract admission, promotion, merge, or
production authorization.
