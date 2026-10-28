# Stage M replay-authority audit — blocking inconsistency found

## Scope

This audit used only repository source and the committed Stage A baseline. It did
not access or mutate `/Library/GRRR`, reconcile accounting, dispatch replay,
promote, admit, merge, or push.

## Finding

The replay authority state machine currently has **no legal binding** that can
both:

1. pass independent-replay preflight; and
2. open a writable `PersistentBudget('independent-replay')`.

### Why

Replay preflight requires:

- profile: `independent-replay`;
- binding version: `1`;
- versions 2 and 3 are explicitly rejected.

The persistent store contract says:

- version 1 is writable but permits only the legacy profiles:
  `synthetic`, `offline`, `trusted-observation`;
- versions 2 and 3 include `independent-replay`, but are read-only/frozen.

Therefore:

- a hypothetical version-1 four-profile binding passes replay preflight but
  fails persistent-store schema validation;
- a legal version-1 three-profile binding passes writable store validation but
  fails replay preflight because `independent-replay` is absent;
- versions 2 and 3 have the replay profile but fail preflight and deny every
  mutation.

## Variant matrix

- **Audited active v3**: preflight FAIL; store schema PASS; read-only; replay no.
- **Legal legacy v1, three profiles**: preflight FAIL; store schema PASS; writable; replay no.
- **Hypothetical v1, four profiles**: preflight PASS; store schema FAIL; not openable; replay no.
- **Registered frozen v2, four profiles**: preflight FAIL; store schema PASS; read-only; replay no.
- **Recovered read-only v3, four profiles**: preflight FAIL; store schema PASS; read-only; replay no.

The audited active Stage A binding is version 3 with all four profiles. It is
therefore schema-valid but deliberately read-only and cannot authorize replay.

## Required next step

Do **not** relax replay preflight, alter profile checks, or mutate the existing
v3 store.

The next bounded stage must design and independently review a new binding
authority contract that explicitly represents:

- complete historical evidence status;
- spendability disposition;
- unresolved holds;
- mutation scope;
- replay-only ceilings or an approved cumulative-budget amendment;
- independent review and operator authorization;
- rollback and refusal behavior.

Only after that contract is approved should implementation or protected
installation be considered.

## Tests

- Homebrew Python 3.14.3: 12/12 focused Stage M tests passed.
- Miniconda Python 3.12.7: 12/12 focused Stage M tests passed.
- Deterministic audit regeneration was byte-identical.
- `pvg verify --include-tests`: PASS.
- `git diff --check`: PASS.
