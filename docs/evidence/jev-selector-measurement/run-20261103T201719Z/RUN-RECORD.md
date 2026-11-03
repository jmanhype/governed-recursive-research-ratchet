# Operator-authorized TypeSafe Jev selector run

## Authorization and identity

- Operator approval: “You have permission. Let’s get it working and use the
  already-saved Jev key for the one-shot selector run.”
- Authorization record:
  `/Users/speed/.codex/grrr-authorizations/typesafe-jev-selector-measurement-20261103.json`
- Authorization record raw SHA-256:
  `9791d532e2a2768131b28b2b1c7906945c116407b1ca5c907db597cad554056e`
- Report-bound canonical authorization SHA-256:
  `e27db52b1dcff18287a63fe89d23f4f0b054e6c69e2a4173f54660df28e100a4`
- Approval time: `2026-11-03T20:17:19Z`
- Runner commit: `4b4ae825fe4708d72ce14eb3bf80f03bc53e9910`
- Frozen corpus digest: `dfa75ef2bf3d43fd4f750094fe643afe4f204812c0ae2426276bedb471fa8529`

The credential remained in the operator-owned mode-0600 secret file. Its value
was not printed, transmitted to a worker, or written to this evidence.

## Exact command boundary

```text
env -u TYPESAFE_API_KEY -u TYPESAFE_BASE_URL -u TYPESAFE_DEFAULT_MODEL \
  -u GRRR_JEV_DISABLE \
  GRRR_JEV_REAL_SELECTOR_MEASUREMENT=1 \
  ./scripts/run-jev-selector-measurement \
  --authorization /Users/speed/.codex/grrr-authorizations/typesafe-jev-selector-measurement-20261103.json \
  --output-dir docs/evidence/jev-selector-measurement/run-20261103T201719Z
```

Exit code: `0`.

Standard output:

```json
{"next_action":"operator-review-required; do not automatically rerun","report":"/Users/speed/Documents/Codex/2026-10-19/3e4m-b-4/outputs/governed-recursive-research-ratchet/.claude/worktrees/dev-GRRR-6sso/docs/evidence/jev-selector-measurement/run-20261103T201719Z/report.json","run_id":"6cf35082f34a4149b67293c7b53d9740","status":"complete"}
```

Standard error: empty.

## Measured result

- Status: `complete`
- Adapter outcome: `complete`
- Attempted calls: `32`
- Returned responses: `32`
- Retries: `0`
- Event rows: `64` (32 starts and 32 finishes)
- Unique external challenge references: `32`
- Usage observation: complete
- Input tokens: `12,548`
- Output tokens: `736`
- Elapsed: approximately 4.499 seconds
  (`2026-11-03T20:17:19.531Z` through `2026-11-03T20:17:24.030Z`)
- Model reported by Jev: `jev-1.14.0`
- USD cost: `null`; status remains `unknown-until-independent-receipt`

Jev’s probabilistic top-eight recommendations were:

1. `GRRR-VC-C001`
2. `GRRR-VC-D015`
3. `GRRR-VC-D005`
4. `GRRR-VC-C004`
5. `GRRR-VC-D020`
6. `GRRR-VC-D012`
7. `GRRR-VC-D018`
8. `GRRR-VC-D008`

These are recommendations only. They are not defect verdicts and do not assert
selector superiority.

## Integrity

- `events.jsonl` SHA-256:
  `44cefd57b7ac65c811e2860a2bf37dfc54c41bb0ba9bed6ef93d475dca316d98`
- `report.json` SHA-256:
  `59a9a21282ae2f4b8fa213f43d0fa1d652bee07d0aad2bf6bfc45535fb436c0f`

Parent validation confirmed sequential event numbers 1–64, exactly 32 unique
opaque references, all 32 finish outcomes as `transport-returned`, and valid
usage on all 32 responses. The event log contains no credential, Authorization
header, endpoint credential, semantic local challenge ID, defect label, clean
label, or protected path. The final report contains the approved local mapping
but no credential or protected-path value.

## Result boundary

`corpus/evaluation-plan.json` remains unchanged with
`approval.state=not-approved` and `approval.measurement_started=false`. This
run was an explicit action-authorized, one-shot external-selector capability
measurement; it was not a silently started pre-registered three-arm evaluation
and must not be represented as completion of GRRR-6sso AC #3.

No automatic rerun, second Jev arm, replay, contract admission, promotion,
production mutation, merge, or push followed this run.
