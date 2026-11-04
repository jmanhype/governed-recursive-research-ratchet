# Anti-Cheat evaluation artifact policy

## Retained in this repository

- `evaluation.json` — machine-readable summary, counts, control outcomes,
  limitations, and recommendation.
- `EVALUATION.md` — operator-readable evidence review.
- `ARTIFACTS.md` — this retention/redaction policy.

## Referenced temporary evidence

The following raw scans were generated outside the repository and are not
committed because they include local filesystem paths and timestamps:

| Artifact | SHA-256 | Disposition |
|---|---|---|
| Full GRRR-gge0 scan | `f56ee077318bea77d1678e5666b5a06904ff5651477f9a8a9f630d923e1f418f` | Counts and command identity retained; raw output not committed |
| Five-file subset scan | `9b6e5e04fdc52208670d74ba53c63ad20146badcf7c36ac68cb57e5ea0c284a2` | Counts retained; raw output not committed |
| Seeded control scan | `af70a5118096b3d792e381c07bb5711521d81e53b9d3b34ab3506902ef3fcdd3` | Findings summarized; raw output not committed |
| Empty control scan | `57ec647ca337d632ae1894c34f3e4d2fd2a8c1a575db585519f52fb02ea2a000` | Perfect-score failure mode summarized |
| All-pattern test log | `bbfe64ec1c98b9f55da6243b896415d2c621815481d0cf7cffeb1106dcd7ec0a` | Result counts retained |
| Built binary | `d6df6a07b5d818bf11bed026455acf531307afb39c92bf7b58cae0c93883ee4e` | Not committed |

Raw scan output is not authoritative state. It is reproducibility evidence only.
Exact commands and exit codes are retained in `evaluation.json`; local checkout
paths may appear in those commands when needed for reproduction, but credentials
and raw local-path-bearing scanner output are not retained.
Future durable retention must first remove local paths and normalize the date or
record both raw and semantic hashes.

No credential, API key, protected `/Library/GRRR` content, protected truth, or
remote scan result is present in these artifacts.
