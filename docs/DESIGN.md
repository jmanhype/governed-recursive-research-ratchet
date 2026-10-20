# Governed Recursive Research Ratchet — Experience Design

## Status and discovery basis

This is a proposed experience contract, not an implementation or architecture.
No commands described here are claimed to exist. Implementation must wait for
operator approval of architecture and testable acceptance criteria.

Source basis: BUSINESS.md and the operator's authoritative Round 1 design answers.
Round 2 is intentionally skipped: those answers exhaustively resolve users and
workflow, surface priorities, decision trade-offs, evidence disclosure, dangerous
actions, failure/recovery cases, accessibility, and review-attention constraints.
The remaining technical feasibility decisions belong to architecture, not design.

## Personas and primary journeys

| Persona | Need | Successful journey |
|---|---|---|
| Operator/product owner | Control policy, attention and authorization | Start, monitor, inspect report and evidence, decide, receive recorded outcome |
| Maintainer/reviewer | Assess claims without trusting proposer narration | Trace claim to specification and independent replay, record finding and review |
| Coding-agent user | Benefit without constant supervision | Inspect bounded progress and explicit blockers, receive only qualified outcomes |
| Independent auditor | Inspect reproducible historical evidence | Follow report snapshot to revisions, evaluator, provenance and replay artifacts |

The POC prioritizes operator and maintainer journeys. Full external audit
certification is not a first-milestone requirement.

### Critical journeys

1. **Start and monitor:** inspect the intended scope, baseline, limits and
   authorization before starting; receive a run ID and concise status. Monitoring
   shows phase, blockers and consumed/remaining budgets without requiring a UI.
2. **Review:** open a generated report, distinguish allegation from verified
   evidence, inspect only the details needed, then approve, reject, request
   evidence or request change. Receive the recorded decision and actual outcome.
3. **Reproduce:** follow an evidence reference to its recorded revision,
   evaluator and replay instructions. An unsuccessful replay remains visible and
   cannot be represented as confirmation.
4. **Stop and recover:** stop is readily discoverable during work and review.
   Receive a truthful stop/recovery report, inspect preserved evidence and choose
   an explicitly safe next action. Promotion remains blocked until verification.

## Surface hierarchy and interface contract

Use existing PAIVOT workflow, tracker and knowledge conventions where applicable;
do not introduce a separate platform for the first milestone.

1. **Generated Markdown report:** primary human decision surface.
2. **CLI with plain-text summaries:** primary execution and control surface.
3. **JSON evidence:** structured inspection and automation, never a prerequisite
   for an ordinary human decision.
4. **Local dashboard:** deferred unless CLI and reports demonstrably fail needs.

### Proposed CLI family

The following names express user-facing intentions only. Exact flags and grammar
must be documented and approved before implementation; examples are not runnable
instructions or evidence of existing functionality.

| Proposed command | User-facing contract |
|---|---|
| `pvg research start` | Show bounded experiment scope and return run ID, limits and next inspection action |
| `pvg research status` | Show run/phase, blockers, budget usage and report availability |
| `pvg research review <run-id>` | Locate the current human report and identify its evidence snapshot |
| `pvg research evidence <run-id>` | Locate replay, technical details and full audit evidence |
| `pvg research decide <run-id>` | Identify exact action/target, collect decision and record outcome |
| `pvg research stop <run-id>` | Stop new work, report cancellation/recovery state and preserve evidence |
| `pvg research recover <run-id>` | Show unresolved state and authorized safe recovery choices |

Help must make inspection, stopping and recovery discoverable. Commands and
machine-readable output must be stable and documented. Errors identify the run,
what did or did not happen, and the next safe action; failures must not look like
successful commands with a warning buried below them.

### Output parity

- Plain text: concise status, blocker/warning/info distinction, next action and
  report/evidence location. Ordinary decision information fits one terminal
  screen or a short report; long audit material is available on demand.
- Markdown: decision summary first, technical evidence second, full audit third.
  Include readable labels and links rather than requiring source-code reading.
- JSON: expose the same run and snapshot identities, distinct state dimensions,
  findings, decisions, gate outcomes, evidence references, budget quantities and
  recovery status. Missing information is explicit, not silently represented as
  success or zero. This is a content contract, not a storage schema.
- All surfaces agree on identities and outcomes. Reports link immutable or
  integrity-verified evidence snapshots. Historical/stale snapshots are labeled;
  stale evidence cannot authorize promotion.

## State, findings and decisions are separate

| Dimension | Allowed user-facing vocabulary |
|---|---|
| Execution | Queued; Running; Awaiting verification; Ready for review; Stopped; Failed; Completed |
| Finding | Verified defect; Not reproduced; Specification ambiguity; Inconclusive; Invalid claim |
| Operator decision | Approve; Reject; Needs more evidence; Request change; Stop |

Execution completion does not mean verification passed or approval was granted.
Ready for review means a review packet is available, not that promotion is safe.
Stopped does not itself establish rollback. A decision must show its target and
type, actor, reason, timestamp and recorded outcome separately from execution.
Needs more evidence and Request change are never implicit approvals.

Use **proposed / observed / verified / approved / deployed** as distinct labels.
Deployment is outside this milestone; never infer it from approval. Challenger
claims remain unverified until independently reproduced and specification-backed.
Jev recommendations are labeled probabilistic, not established facts. Future
Harness²-style research-strategy changes do not confer authority to change
protected governance or evaluation requirements.

## Authorization and approval experience

Keep these three authorization targets visibly separate:

1. Acceptance of defect evidence.
2. Admission of a permanent verification contract.
3. Promotion of a software optimization.

Acceptance of one never implies another. Every approval preview must identify:

- Exact authorization action, target and intended effect.
- Candidate revision and evaluator identity/version.
- Applicable specification and acceptance criteria.
- Independent reproduction and mandatory gate status.
- Evidence integrity and snapshot currency.
- Budget consumption and remaining limits.
- Reversibility, unresolved warnings and blockers.

Permanent contract admission and implementation promotion require explicit
confirmation naming the action and target. Approval is never the default choice.
Missing, failed or not-run mandatory gates, stale evidence, unresolved integrity
failures or failed reproduction must visibly block promotion, not merely warn.
Specification ambiguity is unresolved evidence, not permission to relax criteria.
No approval surface implies production deployment or automatic merge to main.

Reject and Stop remain directly accessible while recording actor and reason.
An urgent stop must not wait for a lengthy review form. Record the stop request
and allow any missing explanation to be supplied without delaying safety work.
After a decision, show both what was authorized and what actually occurred;
recording an approval is not proof that its intended effect completed.

## Progressive evidence disclosure

### Level 1 — decision summary

Show claimed defect, relevant specification requirement, actual behavior,
independent reproduction status, mandatory gate pass/fail/not-run status, and
recommended action with reason. Separate verified defects from plausible claims.
Add authorization target, critical blockers, snapshot identity/currency and budget
summary so the operator need not navigate away to recognize an unsafe decision.

Example layout (illustrative, not measured evidence):

```text
Run: <run-id>                  Execution: Ready for review
Finding: Not reproduced       Decision: Not recorded
Action under review: Accept defect evidence
Claim / requirement / behavior: <short plain-language account>
Reproduction: Not reproduced
Mandatory gates: <passed>/<required>; <failed>; <not run>
Evidence: <snapshot>; <integrity and currency>
Budget: <spent>/<limit>; runtime <used>/<limit>
BLOCKER: Independent reproduction is missing. Promotion blocked.
Next: Inspect evidence | Needs more evidence | Reject | Stop
```

### Level 2 — technical verification

Replay command and recorded output; minimal input; expected versus actual
behavior; evaluator identity/version; candidate and baseline hashes;
specification/oracle reference; diagnostics. Label recorded output separately
from a fresh replay result, including unsuccessful or interrupted attempts.

### Level 3 — full audit

Environment/toolchain manifest; all gate results with checked counts; event
history; artifact digests and provenance; model/provider information;
token/API/compute costs and remaining budget; related experiments; evaluator and
specification changes. Preserve uncertainty, incomplete evidence and failures.
Comparisons report false positives/negatives, variance, confidence intervals and
costs without claiming statistical superiority from insufficient samples.

## Hard-stop, rollback and recovery experience

On a hard-stop trigger: stop new work, safely cancel active processes, block
promotion and further modifications, preserve the ledger/candidates/logs and
verification artifacts, and determine whether the accepted baseline is intact.
While cancellation or checks are incomplete, say so; do not show a safe outcome
prematurely. Triggers remain those in BUSINESS.md, including exhausted budgets,
unauthorized/protected-asset modifications, isolation or evidence failures,
missing dependencies, repeated unreproducibility and unrecoverable state.

Use explicit, non-interchangeable outcomes:

- **Stopped safely:** cessation and the stated safety checks are verified;
  this does not itself mean any changes were rolled back.
- **Rollback completed and verified:** restoration and the relevant verification
  evidence are linked. A zero exit code alone is insufficient.
- **Recovery required:** unresolved changes or unknown state remain; list them
  and keep promotion blocked.

The recovery report shows stop reason/time, baseline and candidate IDs, completed
and interrupted operations, changed resources, evidence integrity, restored versus
unresolved state, and exact safe next actions. Forensic evidence must survive.
Disposable candidate-only worktrees may be discarded only after evidence
preservation and cleanup verification. Persistent or external-state recovery
requires separate authorization; do not present it as routine automatic cleanup.

## Accessibility, attention and copy

- Keyboard-only operation and screen-reader-compatible ordered headings/tables.
- No color-only meaning; always print textual status and severity.
- Plain-language summary before technical terms; approximately 80-column prose
  and terminal summaries where practical, without truncating critical identities.
- No dashboard dependency and no raw JSON requirement for ordinary decisions.
- Explicit BLOCKER, WARNING and INFO labels, each with a concrete implication.
- Keep progress concise; unchanged progress must not demand repeated review.
  Surface hard stops and required decisions clearly. A notification channel or
  cadence is not otherwise committed by this design.
- Show review burden and stay within the BUSINESS.md POC 60-minute and milestone
  3-hour operator-review ceilings; never silently extend them.

Copy examples:

| Situation | Preferred wording |
|---|---|
| Missing gate | `BLOCKER: Mandatory gate not run. Promotion is blocked.` |
| Failed replay | `Not reproduced. The claim has not been verified.` |
| Stale packet | `Historical evidence: candidate or evaluator changed. Reverification required.` |
| Uncertain recovery | `Recovery required. Baseline integrity is not yet verified.` |
| Recommendation | `Probabilistic recommendation from Jev; not a verified finding.` |
| Recorded approval | `Decision recorded for <action/target>. Outcome: <pending/verified result/failure>.` |

Avoid “all clear,” “fixed,” “safe,” or “done” when only a command completed or an
agent made a claim. Errors explain the impact, preserved evidence and next safe
step without blaming the operator or suggesting weaker verification.

## User-perspective Definition of Done

The following are proposed testable UX requirements, pending formal AC approval:

- An operator unfamiliar with internals can inspect a completed experiment,
  explain its finding and evidence limits, and make the appropriate decision
  without reading source code.
- A reviewer can reach specification, independent replay and full audit evidence
  from the report and identify the exact candidate/evaluator/snapshot.
- Demonstrations distinguish execution completion, verification, all three
  approval types and actual outcomes; accepting evidence grants no other action.
- Missing/not-run gates, failed reproduction, stale evidence and integrity
  failures visibly block promotion across human and structured surfaces.
- Keyboard-only and screen-reader walkthroughs cover inspection, decision, stop
  and recovery, with no color-only information or dashboard dependency.
- A stopped-run walkthrough identifies preserved evidence, verifies or explicitly
  leaves unresolved baseline/rollback status, and requires separate authorization
  for persistent/external-state recovery.
- Ordinary review uses concise summaries plus optional detail, within the
  aggregate business review budget; actual review time is reported, not assumed.
- No demonstration claims implementation, deployment, passing tests or successful
  recovery without corresponding evidence.

## Design-to-Stories inputs

These are atomic UX requirement candidates, not created stories or final ACs.

| Candidate scope | Demonstration/proof expected |
|---|---|
| CLI discoverability and bounded start/status | Help and terminal transcript identifying scope, run, limits and next actions |
| Report with progressive disclosure | Markdown packet and navigation walkthrough from summary to replay and audit |
| Distinct state dimensions | Matching plain-text/Markdown/JSON examples for complete-but-unapproved and unreproduced cases |
| Separate authorization targets | Decision transcripts proving evidence acceptance cannot authorize contract admission or promotion |
| Explicit high-impact confirmation | Transcript naming exact action/target and showing no default approval |
| Fail-closed review experience | Negative-case demonstrations for missing gates, stale snapshots, failed replay and integrity failures |
| Recorded decision versus outcome | Packet showing actor/reason/time and pending or failed effect without false success |
| Safe-stop and recovery communication | Interrupted-run report, preserved evidence references and verified/unresolved restoration distinction |
| Separate recovery authorization | Demonstration that persistent/external recovery is not silently performed |
| Accessible low-attention operation | Keyboard/screen-reader walkthrough and measured ordinary-review time |
| Qualified comparative reporting | Report retaining uncertainty, costs and probabilistic/verified distinctions |

Integration handoffs: connect the report and CLI experience to existing PAIVOT
state/tracker conventions, evaluator evidence, budget accounting and recovery
outcomes. Architecture determines implementation boundaries; sr_pm converts
approved requirements into self-contained stories and testable ACs. This document
neither changes governance nor authorizes development.
