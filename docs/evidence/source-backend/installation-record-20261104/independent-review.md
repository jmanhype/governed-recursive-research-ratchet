# Scoped source review — GRRR-k3j7 InstallationV2 codec (2026-11-04)

REVIEW_RESULT: scoped APPROVED

## Boundary

- Worktree: `/Users/speed/Documents/Codex/2026-10-19/3e4m-b-4/outputs/governed-recursive-research-ratchet/.claude/worktrees/dev-GRRR-k3j7`
- Current HEAD: `419c312a116476ff22486737883d4b19b4a2ddb4` (`419c312 wip(GRRR-k3j7): preserve reviewed backend source mechanics`)
- Reviewed only:
  - `research/capstone_installation_record.py` SHA256 `5d6afe113a13882ac256d57cbf19dda4f73ea44cece98efe0c23b01bc7e5ef6e`
  - `tests/unit_capstone_installation_record.py` SHA256 `d7697d53e303233f13844dd7197c1a3eb6ed1ccb8dc7a9de91a02eea81a58997`
- Exact-source fallback was limited to the existing canonical/digest primitives, v1 `U`/`H` checker, approved InstallationV1 field list, and the InstallationV2 correction. No other implementation was reviewed.
- Both target files are untracked WIP at the reported hashes. No source/test edits, Git/tracker mutation, delegation, credentials, network, VM/replay, production effect, or `/Library/GRRR` metadata/content access occurred.

## Findings

No concrete defect was found in the data-only InstallationV2 codec scope.

1. **Exact field set and V2 delta**
   - The codec defines exactly the 18 base digest fields from InstallationV1, changes the schema literal to `capstone-installation-v2`, and adds `reviewer_manifest_sha256`; it accepts no extra or missing field (`research/capstone_installation_record.py:13-41`).
   - This matches the approved base field inventory (`docs/evidence/source-backend/grrr-executable-backend-design-v2-20261104.md:61-67`) and the correction's add-only V2 replacement (`docs/evidence/source-backend/grrr-backend-jit-integration-corrections-20261104.md:25-28`). InstallationV1 and every other schema value are unsupported.
   - Exact missing/extra fields and wrong schemas are tested at `tests/unit_capstone_installation_record.py:30-44`.

2. **UID semantics**
   - The codec reuses the unchanged v1 `U` primitive—exact `int`, positive, below `4294967295`, and distinct from evaluator320/broker321 (`research/capstone_contract.py:78-86`)—and separately rejects reviewer UID322 as required by the correction (`research/capstone_installation_record.py:31-40`; correction lines 18-23).
   - Bool, float/string/null, zero/negative, both reserved service UIDs, reviewer322, and upper-bound values are tested at `tests/unit_capstone_installation_record.py:46-51`.

3. **Strict digest/canonical bytes and duplicates**
   - Every non-schema, non-operator field is checked as exact lowercase 64-hex SHA-256 text using the unchanged `H` rule (`research/capstone_installation_record.py:38-40`; `research/capstone_contract.py:84-86`).
   - Decoding accepts only nonempty `bytes` up to `MAX_WIRE`, rejects duplicate JSON keys through `unique_fields`, rejects finite floats and NaN/Infinity while parsing, validates the exact flat shape, and finally requires byte-equal `common.canonical` output (`research/capstone_installation_record.py:44-59`; canonical/digest primitives at `research/common.py:24-30`).
   - Encoding validates first and returns only exact canonical bytes plus their SHA-256 (`research/capstone_installation_record.py:62-66`). It has no descriptor path, installation resolver, authority object, or effect.
   - Digest mutations, duplicate keys, whitespace/order/non-bytes/float/non-finite cases are tested at `tests/unit_capstone_installation_record.py:53-72`.

4. **Size, complexity, and fail-closed behavior**
   - Oversized or non-`bytes` input is refused before JSON parsing (`research/capstone_installation_record.py:48-56`; tests `tests/unit_capstone_installation_record.py:74-77`).
   - The accepted record is intentionally flat: every field must be the exact schema string, `U` integer, or `H` digest. Therefore nested or complex payloads cannot be accepted; parser recursion/malformed JSON is caught, and any parsed nested value fails the exact field/type checks (`research/capstone_installation_record.py:31-59`).
   - Valid data changes the exact bytes/hash and returns no authority surface (`research/capstone_installation_record.py:62-66`; test `tests/unit_capstone_installation_record.py:79-87`).

## Actual verification

Parent-interpreter source guard SHA256:
`182ade427971f13354ec32a94d2af295818b3a0d1dedb79249de32ec130a4673`

Command:

```sh
/usr/bin/time -p timeout 30 /opt/homebrew/bin/python3 -B /tmp/grrr-k3j7-guarded-source-suite-20261104.py unit_capstone_installation_record
```

Interpreter: Python `3.14.3`.

Measured result:

```text
Ran 7 tests in 0.009s
OK
PARENT_SOURCE_ONLY tests=7 failures=0 errors=0 skipped=0 protected_attempts=0; guard=parent-interpreter-only; no VM/UID/OS-isolation proof
real 0.31
user 0.08
sys 0.03
```

## Limitations

This is only approval of the strict canonical InstallationV2 **record codec**. It is not approval of the full backend story and establishes no descriptor-path integrity, installed file/inventory validation, UID322 provisioning or ACL proof, manifest resolution, operator authentication, runtime closure, installation authority, execution permission, or production readiness. The guard is parent-interpreter-only and is not an OS sandbox.
