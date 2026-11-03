# Pre-registered three-arm selector result

## Decision

**Outcome:** `inconclusive-jev-did-not-win`

Jev did not satisfy the pre-registered win condition. The random arm had the
measured leading primary mean. This is a descriptive selector-quality result
only; it is not a defect verdict, software optimization, replay result,
contract admission, promotion, or production change.

The pre-registered default remains `retain-deterministic-lexical-baseline`
unless the operator separately changes baseline policy. No runtime selector was
promoted by this measurement.

## Immutable design and execution identity

- Approved design commit: `9e107609db76022ed6d8e138cbbece2e41d634ee`
- Approved design SHA-256:
  `97ec4b8ccc34b3fc4da4fcfbef33b49bbb3f4f1c445cfecdb752715ddf034be1`
- Execution preflight commit:
  `bdee48184d513f5cb0015f04b8f3882ae3375c85`
- Protected truth SHA-256:
  `7cf9f99f5836c4e3e147df2866d54480a706f2665a732fbf61bd1a0d0b4c52ea`
- Operator explicitly approved crossing the foundation gate and spending the
  bounded confirmatory Jev budget.

## Confirmatory Jev repetitions

### Repetition 1

- Run ID: `9f7ea255e61d4f2aa6596967ef698adf`
- Evidence: `../confirmatory-repetition-1-20261103T214533Z/`
- Events SHA-256:
  `9955289f633ccff58b3077a8d2c11263cdb063f3b18aa82e16b9b0e8a08f658a`
- Report SHA-256:
  `79aeba001d375b39806d9f73ff211a9573062fdb26792d9d489cf933c48dd628`
- Authorization raw SHA-256:
  `40f6a2183333cd698e84ac7a594a1f66c51217a16d8adb5d10c0a3d81ce7dcc2`
- Calls: 32 attempted / 32 returned / 0 retries
- Usage: 12,548 input / 736 output tokens
- Selected: D015, C001, D005, C006, C004, D018, D010, D012

### Repetition 2

- Run ID: `76aaf8542fce4465b082524432f6a1ca`
- Evidence: `../confirmatory-repetition-2-20261103T214623Z/`
- Events SHA-256:
  `0ed940ebd206be84aa99e65f03e2f11992a4468efeb070e294ccbe25efaac989`
- Report SHA-256:
  `f09f56cdddc0f183e7701eef7ec438ee0d30acc4bdc4beea1a0b3ea9ab7a2b84`
- Authorization raw SHA-256:
  `ed59e20ad807e9b1fe3dc385860a34f08bc863ef7e00ee721ffbec2cab5c5898`
- Calls: 32 attempted / 32 returned / 0 retries
- Usage: 12,548 input / 736 output tokens
- Selected: D015, C001, D005, D008, D010, D020, D018, C002

### Repetition 3

- Run ID: `e3938b63cf634cdda8e0f00fe416ab31`
- Evidence: `../confirmatory-repetition-3-20261103T214701Z/`
- Events SHA-256:
  `2cc3a88d131fd5a790cb1aed7e8bffc8cb6a8fcf90cf7f73fe13f9e1a42d8cf4`
- Report SHA-256:
  `0121a7caafecbe543e698e67ba729bf38726f43bdcfd7cc63d7245634c7dce1c`
- Authorization raw SHA-256:
  `eb4dd1f7a4f1ab82e47bc2a296a75df89d0bdb481e2092b6b94498ee646375a5`
- Calls: 32 attempted / 32 returned / 0 retries
- Usage: 12,548 input / 736 output tokens
- Selected: C001, D015, D005, D010, C006, C004, D008, C002

The selected-ID list above omits the `GRRR-VC-` prefix for readability.
Machine-readable exact IDs remain in each immutable report.

## Measurements

Primary metric: mean selected true defect labels per repetition, range 0–8.

| Arm | Repetitions | Mean | Mean critical | Mean clean | Unique defects | Bootstrap 95% |
|---|---:|---:|---:|---:|---:|---:|
| Deterministic lexical | 0, 0, 0 | 0.0 | 0.0 | 8.0 | 0 | 0.0–0.0 |
| Random | 6, 6, 6 | 6.0 | 4.333333 | 2.0 | 14 | 6.0–6.0 |
| Jev-guided | 5, 6, 4 | 5.0 | 3.0 | 3.0 | 7 | 4.0–6.0 |

The bootstrap used exactly one `random.Random(20261103)` instance, 10,000 outer
iterations, fixed arm order, three `rng.choice` calls per arm, arithmetic means,
and nearest-rank percentiles.

## Cost and usage

- Confirmatory Jev calls: **96**
- Confirmatory retries: **0**
- Confirmatory input tokens: **37,644**
- Confirmatory output tokens: **2,208**
- Cumulative calls including exploratory pilot: **128**
- Cumulative input tokens including pilot: **50,192**
- Cumulative output tokens including pilot: **2,944**
- USD: `null`, status `unknown-until-independent-receipt`

The exploratory pilot remains excluded from confirmatory selection values.

## Analysis artifacts

- Machine-readable report: `report.json`
- Report SHA-256:
  `b7bb2ec8717e8921e16f9a3e312f6ad46839a125634dc6e3d144499cc841fefb`
- Analyzer: `research/jev_three_arm_analysis.py`
- Analyzer SHA-256:
  `6c88f68d60a65ef13e397e8ab0c1d0bd692f4a75fac003134205fa2e87786805`
- Tests: `tests/unit_jev_three_arm_analysis.py`
- Tests SHA-256:
  `60803a5b4f76336fb581a1f0050fff42245fb1828ce1041a0832e8b2d978c7d5`

Focused analysis tests passed **6/6** under system Python and Homebrew Python.

## Disclosure

Post-run shell validators for repetitions 1 and 2 had local Python argument or
path-type bugs after the external runs had already returned exit 0. Neither bug
caused a retry or additional external call. The immutable reports were validated
afterward, and repetition 3 was validated directly. No Jev repetition was rerun.

No automatic rerun, additional external call, replay, contract admission,
promotion, production mutation, merge, or push followed this measurement.
