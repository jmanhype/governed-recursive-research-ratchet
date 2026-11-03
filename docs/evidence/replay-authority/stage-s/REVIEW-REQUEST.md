# Stage S Authorization Preparation — Independent Review Request

## Scope

Review the Stage S v4 operator-authorization preparation record for:

1. Exact binding to the independently approved Stage R source package.
2. Correct eight-role staging plan with exact hashes and destinations.
3. Correct installation target (sibling, not predecessor replacement).
4. Predecessor mutation is forbidden.
5. Operator authorization is null / prepared-not-authorized.
6. All authority flags are false.
7. All denied authorities are complete.
8. Validation rejects wrong hashes, modified plans, missing/extra fields,
   duplicate/missing roles, wrong destinations, wrong targets, non-null
   authorization, any true authority flag, and predecessor mutation.
9. Emission verifies Stage R SOURCE-BUNDLE.json, PACKAGE.json, and review
   approval file hashes before generating the record.
10. No `/Library/GRRR` access or mutation, no protected staging, no
    installation, no budget amendment, no reconciliation, no replay, no
    admission, no promotion, no merge, no push.

## Files to review

- `research/replay_successor_authorization.py`
- `scripts/prepare-replay-successor-v4-authorization`
- `tests/unit_replay_successor_authorization.py`
- `docs/evidence/replay-authority/stage-s/AUTHORIZATION-PREPARED.json`

## Commands to independently rerun

```bash
/opt/homebrew/bin/python3 -I -B -m unittest discover -s tests -p 'unit_replay_successor_authorization.py' -v
/Users/speed/miniconda3/bin/python -I -B -m unittest discover -s tests -p 'unit_replay_successor_authorization.py' -v
./scripts/prepare-replay-successor-v4-authorization | shasum -a 256
```

## Expected hashes

- Builder SHA-256:
  `64eaae965b20de911063d4d217ea44c6230a7a8b21193a8e47ddb0143130a44b`
- Script SHA-256:
  `e3ffbddbd6bb04b9b8a0fb4796d7973477688f2a38a8538f5e2385b19642becd`
- Tests SHA-256:
  `f06133ee6c179a56673380054d330dd1af6e1e15050d8a5a78e95e449b3fd6aa`
- Generated record SHA-256:
  `1d27da0d718ac7713f54bc73d4b87d5bcd1ea57f3eb55de1e74b0e2c933a75c9`

## Rework scope (narrow retry)

The initial review rejected six validator bypasses. This narrow rework adds:

- exact key-set enforcement for `basis`, staging items, `predecessor_binding`,
  `operator_authorization_requirement`, and `authority`;
- exact `base_commit` and `prepared_at` validation;
- 13 regression tests covering every reviewer mutation probe;
- 42 focused tests total (29 original + 13 rework regressions).

Verify independently that all initial reviewer probes now reject:

```python
mutations = [
    ("empty_authority", lambda r: r["authority"].clear()),
    ("missing_auth_hash", lambda r: r["operator_authorization_requirement"].pop("authorization_hash")),
    ("extra_predecessor", lambda r: r["predecessor_binding"].update({"extra": True})),
    ("wrong_base_commit", lambda r: r["basis"].update({"base_commit": "0"*40})),
    ("none_prepared_at", lambda r: r.update({"prepared_at": None})),
]
```

## Boundary

This review covers only the repository-retained Stage S authorization
preparation record. It does not approve protected staging, installation,
budget amendment, reconciliation, replay execution, admission, promotion,
merge, or push.
