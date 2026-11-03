# GRRR adaptation cycle 1
- Outcome: **no composed strategy change**; retain the deterministic lexical baseline.
- Benchmark: random mean **6.0** from the immutable completed result.
- Reverse lexical: measured **8/8**, but **rejected for D/C local-ID prefix leakage**.
- Fixed random block 45/46/47: mean **14/3**, critical mean **10/3**, clean mean **10/3**, unique defects **12**.
- `reverse-lexical`: eligible=false; leakage reason: D/C local-ID prefix signal was declared or deterministically detected; the measured score cannot override leakage.
- `random-block-45-46-47`: eligible=true; exceeds_benchmark=false; full block retained.
- Plan / result SHA-256: `97ec4b8ccc34b3fc4da4fcfbef33b49bbb3f4f1c445cfecdb752715ddf034be1` / `b7bb2ec8717e8921e16f9a3e312f6ad46839a125634dc6e3d144499cc841fefb`
- Corpus freeze digest / protected truth SHA-256: `dfa75ef2bf3d43fd4f750094fe643afe4f204812c0ae2426276bedb471fa8529` / `7cf9f99f5836c4e3e147df2866d54480a706f2665a732fbf61bd1a0d0b4c52ea`
All promotion, admission, execution, production mutation, merge, and push flags are false. No automatic rerun is authorized; operator review is required.
