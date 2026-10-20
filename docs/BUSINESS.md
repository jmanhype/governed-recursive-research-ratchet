# Governed Recursive Research Ratchet — Business Brief

## Status

- **Decision stage:** business discovery complete; architecture and testable acceptance criteria remain pending operator approval.
- **Product owner:** the operator.
- **Development authorization gate:** no implementation, repository development, component commitment, or story execution begins until the operator explicitly approves both the architecture and testable acceptance criteria.
- **Authority model:** the operator owns policy; agents propose changes; independent verification establishes evidence; promotion remains governed.
- **Source basis:** operator problem statement and operator answers to the business clarification round.

## Problem Statement

Autonomous coding agents need a governed way to improve software, improve their own research strategies, and strengthen verification through independently validated counterexamples. The central business problem is not simply generating candidate improvements. It is ensuring that those candidates can be trusted after adversarial scrutiny without allowing the optimizing agent to grade itself, weaken verification, manipulate benchmarks, mutate protected assets, or promote unreproducible work.

The first proof of concept will target PAIVOT's `vlt` indexing subsystem. It must establish an independently verified baseline, compare Jev-guided adversarial research with deterministic and random baselines, and detect deliberately seeded regressions under a fixed budget. Recursive adaptation of the agent harness is not authorized until that foundation is proven.

## Stakeholders and Personas

Priority decreases from first to last:

1. **Operator / product owner**
   - Must trust that autonomous experiments cannot corrupt repositories, weaken verification requirements, manipulate benchmarks, or promote unverified changes.
   - Must be able to inspect, stop, reproduce, and roll back every experiment.
   - Owns policy and approval decisions.

2. **PAIVOT maintainers and reviewers**
   - Must trust evidence, test results, specification traceability, experiment history, and promotion decisions.
   - Must not depend on an agent's self-reported success.

3. **Autonomous coding-agent users**
   - Need demonstrably better implementations and research strategies.
   - Those gains must not sacrifice correctness or require constant supervision.

4. **Independent auditors**
   - Must eventually be able to independently replay experiments and verify signed or hashed evidence.
   - Full external audit certification is explicitly not required for the first milestone.

## Business Outcomes

Ranked outcomes:

1. **Stronger promotion confidence.** Autonomous software improvements can be accepted based on independently reproducible evidence without agents modifying the criteria used to judge themselves.
2. **Lower verification cost per genuine defect discovered.** Jev-guided adversarial research should find more real defects for the same computational and financial budget than deterministic or random challenge selection.

Faster convergence, software performance gains, and recursively improving agent harnesses are secondary outcomes until the verification system is reliable. The long-term goal is software engineering that compounds both implementation quality and verification capability.

## Goals

- Prove a trusted evaluation path for autonomous improvement candidates.
- Establish and protect an independently verified baseline for PAIVOT `vlt` indexing.
- Compare Jev-guided challenge selection with deterministic risk-based selection and random selection under equal budgets.
- Detect deliberately seeded regressions without loosening verification gates.
- Convert independently reproduced failures into reviewed verification obligations that prevent recurrence.
- Preserve complete evidence for inspection, reproduction, review, stop, and rollback.
- Demonstrate measurable benefit under explicit cost and runtime limits.
- Lay a governed foundation for later implementation, verification, and harness improvements.

## Non-Goals

The first release must not include:

- Production deployment or production-data mutation.
- Automatic merging into `main`.
- Unrestricted autonomous self-modification.
- Modification of PAIVOT core governance without separate authorization.
- Automatic changes to authoritative specifications.
- Automatic acceptance of agent-generated verification contracts.
- Training or fine-tuning foundation models.
- Claims of mathematically guaranteed system-wide correctness.
- Public benchmark or research superiority claims.
- Multi-project orchestration at production scale.
- Mandatory integration of every Sean Chatman repository.
- Mandatory Bend, ggen, wasm4pm, or dteam integration.
- Unrestricted execution of external Harness² implementations.

## First POC Success Metrics

Target subsystem: **PAIVOT `vlt` indexing**.

Compare these challenge-selection strategies under equal budgets:

- Jev-guided selection.
- Deterministic risk-based selection.
- Random selection.

Evidence population:

- At least 20 independently validated defect scenarios.
- Multiple defect categories.
- Clean negative examples.
- At least three randomized evaluation runs where feasible.

Acceptance targets:

- **≥20% more independently validated defects per dollar** for Jev-guided selection than the strongest alternative baseline.
- **100% detection of designated critical seeded faults** by the complete mandatory verification system.
- **≥90% detection of remaining seeded defects**, subject to a sufficiently representative test set.
- **Zero false-positive defect claims admitted as verified** without independent reproduction and specification confirmation.
- **Zero failed reproductions promoted** into permanent verification contracts.
- **Zero missing mandatory gates treated as passing.**
- Every admitted counterexample must replay against the recorded candidate revision and evaluator version.
- At least one demonstrated Counterexample-to-Contract cycle must prevent recurrence of a previously discovered defect.

Required reporting:

- False-positive rate.
- False-negative rate.
- Variance.
- Confidence intervals.
- Evaluation costs.

Do not claim statistically established superiority when the sample is too small. If Jev does not outperform the deterministic baseline, retain the simpler deterministic baseline rather than forcing Jev into the architecture.

## Requirements and Constraints

### Governance and Evidence

- Keep the optimization agent separate from the trusted evaluator and promotion authority.
- Protect benchmarks, holdouts, acceptance criteria, and authoritative specifications with execution-permission boundaries.
- Do not allow missing or skipped mandatory verification gates to count as passing.
- Maintain an append-only, replayable experiment ledger.
- Require independent reproduction and review before promotion.
- Record candidate revisions, evaluator versions, commands, results, costs, review outcomes, and rollback evidence.
- Ensure experiments cannot mutate production or automatically merge `main`.
- Define measurable success criteria, cost limits, failure conditions, and rollback before execution.

### Improvement Mechanism Boundaries

The business scope recognizes three separate improvement mechanisms:

1. **Implementation ratchet:** Karpathy Autoresearch improves code and measurable software performance.
2. **Verification ratchet:** Independently reproduced failures become reviewed, permanent verification obligations.
3. **Harness ratchet:** Harness²-style Propose–Probe–Compose experimentation improves agent strategies, prompts, tools, and research procedures across tasks.

These mechanisms must remain distinct and must not all be implemented simultaneously.

### Investigation Context, Not Settled Decisions

The exact investigation inputs are PAIVOT/pvg, Karpathy Autoresearch, Harness²-style Propose–Probe–Compose, TypeSafe Jev, Counterexample-to-Contract Ratchet, Sean Chatman Anti-Cheat Scorecard first, Machinery, and optional Bend 2. They are investigation contexts, not final architecture or component decisions.

- PAIVOT/pvg is the governance investigation context for all three improvement mechanisms.
- TypeSafe Jev is an optional probabilistic research director, not the final judge of correctness.
- Counterexample-to-Contract Ratchet is the investigation context for converting independently reproduced failures into reviewed obligations.
- Sean Chatman Anti-Cheat Scorecard is investigated first among his candidate tooling.
- Machinery supplies applicable formal design obligations.
- Bend 2, ggen, wasm4pm, and dteam are not mandatory; any integration must be selective and measurably justified.

## Cost, Time, and Hard-Stop Boundaries

### Proof of Concept

- Maximum **$50 incremental** model/API/compute spend.
- Maximum **6 cumulative hours** of experiment runtime.
- Maximum **60 minutes** of operator review.

### First Milestone

- Maximum **$150 cumulative** model/API/compute spend, including POC spend.
- Maximum **24 cumulative hours** of experiment runtime.
- Maximum **3 cumulative hours** of operator review.
- Target completion within **14 calendar days** of authorized kickoff. This is a target, not a delivery guarantee.

### Execution Constraints

- Use existing local tools and compute wherever practical.
- Paid external services require explicit budget authorization before use.
- Do not automatically increase budgets or loosen success criteria.

### Hard-Stop Conditions

Stop immediately if any of these occurs:

- Budget or runtime exhaustion.
- Unauthorized modification attempts.
- Compromised evaluation isolation.
- Missing required verification dependencies.
- Evidence integrity failures.
- Repeated unreproducible results.
- Unrecoverable experiment state.
- Any attempt to modify protected benchmarks or acceptance criteria.

On stopping, preserve:

- The original baseline.
- Candidate revisions.
- Experiment logs.
- Failure reports.
- Rollback evidence.

## Phased First-Milestone Priority

1. **Prove the independent evaluator and verification ratchet.**
   - Establish the protected baseline, evaluator authority, mandatory gates, replay evidence, and rollback capability.
2. **Compare Jev-guided research with simpler baselines.**
   - Run the equal-budget comparison against deterministic and random selection.
   - Retain the simpler baseline unless Jev meets the business threshold.
3. **Defer recursive harness adaptation.**
   - Do not advance until foundational evaluation, anti-manipulation controls, reproduction, and rollback are proven.

## Business-Level Kill Criterion

If the system cannot independently reproduce discovered defects, prevent benchmark manipulation, and preserve verifiable rollback evidence, it must not advance to recursive harness adaptation or autonomous promotion.

## Risks and Open Questions

- The evidence population may be too small to support a statistical superiority claim. In that case, report observed results and uncertainty without claiming established superiority.
- The meaning of a “sufficiently representative test set” must be resolved during evaluation design before results are interpreted.
- Equal-budget comparison and cost-per-defect accounting must be defined precisely enough to prevent optimistic scoring.
- Evaluation isolation must remain resistant to accidental or agent-directed manipulation.
- The eventual signed or hashed audit format remains open because full external audit certification is outside the first milestone.
- Optional integrations must not expand scope unless they measurably improve the governed outcome.
- A Jev loss to the deterministic baseline is an acceptable result; preserving a simpler, reliable baseline is preferable to forcing integration.

## Backlog Inputs for `sr_pm`

### Candidate Epic Themes

1. **Trusted evaluator and protected baseline**
    - Establish PAIVOT `vlt` indexing baseline.
    - Separate proposing agents from evaluation and promotion authority.
    - Protect benchmarks, holdouts, criteria, and authoritative specifications.

2. **Validated challenge corpus and seeded-regression detection**
    - Provide at least 20 independently validated defect scenarios across multiple categories.
    - Include clean negative examples.
    - Designate critical faults.
    - Run at least three randomized evaluation runs where feasible.

3. **Equal-budget strategy comparison**
    - Compare Jev-guided, deterministic risk-based, and random challenge selection.
    - Report defects per dollar, false positives, false negatives, variance, confidence intervals, and evaluation cost.
    - Fail closed rather than claiming unsupported statistical superiority.

4. **Mandatory verification and promotion gate**
    - Detect 100% of designated critical seeded faults.
    - Detect at least 90% of remaining seeded defects when the test set is representative.
    - Reject missing gates, unreproduced claims, and failed reproductions.
    - Require independent review before permanent obligations or promotion.

5. **Replayable ledger and rollback**
    - Record append-only experiment history, candidate revisions, evaluator versions, costs, and outcomes.
    - Replay every admitted counterexample.
    - Preserve rollback evidence and stop-state artifacts.

6. **Counterexample-to-Contract POC**
    - Demonstrate at least one independently reproduced defect becoming a reviewed verification obligation that prevents recurrence.

7. **Budget enforcement and hard-stop workflow**
    - Enforce POC and milestone spend/runtime/review limits.
    - Stop on every defined hard-stop condition.
    - Preserve the required evidence and rollback artifacts.

### Testable Business Acceptance Themes

- No experiment mutates production or automatically merges `main`.
- No protected evaluation asset or authoritative criterion is modified by the optimizer.
- No mandatory verification gate is missing or skipped.
- Every admitted defect has independent reproduction and specification confirmation.
- Every promoted obligation is independently reviewed and replayable.
- Budget, runtime, and review limits are measured and enforced.
- The first milestone report discloses actual uncertainty and costs without unsupported claims.
