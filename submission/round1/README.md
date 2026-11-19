# Round 1 completed · OneManArmySweep

Class L3B · Dao Duc Son (2A202604105), sole member as confirmed by the student. AI assistance is disclosed in TEAM.md.

**Decision v1: Tiếp tục (Continue)** into Round 2 preparation and incident evaluation. This decision does not authorize a live customer or real-payment rollout. It follows the scope and conditions written in the criteria before evaluation.

| Measure | Baseline | Frozen Round 1 | Signed requirement |
|---|---:|---:|---:|
| Successful trials | 109/110 | 110/110 | pass_rate ≥0.98 |
| pass_rate / bootstrap 95% CI | 0.9909 [0.9727,1] | 1.0 [1,1] | ≥0.98 |
| Tickets passing all five seeds | 0.9545 | 1.0 | ≥0.95 |
| Wrongful refunds (all trials) | 20,000 VND | 0 VND | 0 |
| Wrongful carrier faults | 1 | 0 | 0 |
| PII leaks | 0 | 0 | 0 |
| Escalation rate | 22.73% | 22.73% | ≤25% (nice-to-have) |
| Cost per ticket, simulation | 4,203 VND | 4,449 VND | ≤7,500 VND |
| ROI, simulation | 1.34 | 1.25 | ≥0.30 |
| Maximum review wait / stuck cases | 0 min / 0 | 0 min / 0 | ≤45 min / 0 |
| Coverage | 100% | 100% | Scope all 22 baseline tickets |

ROI is net savings divided by simulated total cost. The final operating plan includes explanatory notes, 10% sampling and one reviewer at six review units/hour. Consequently review_rate=27.27% includes sampled reviews; escalation_rate=22.73% counts actual handoffs only. ROI and cost are mock estimates, not measured API bills or production savings.

## Completed work

- [Form A](../../templates/form-a-criteria.md): goals, metrics, confidence-interval question, thresholds, decision rules, output boundaries and signing evidence.
- [Form B](../../templates/form-b-evaluation-gates.md): baseline/trace analysis, data map/drift, HAZOP, nine-area checklist, four-lens pre-mortem, safeguards, behavioral tests, budgets, staffing/legal controls, runbook 1–3 and peak-hour plan, evidence-based v1 decision.
- [Active guards](../../lab10/guards.py): G1 authoritative policy/scope/admission; G2 entitlement, ledger, approval and refund caps; G3 supported carrier faults and minimized notices. No ticket IDs, seeds, labels or incident-specific wording select runtime behavior.
- [Operating gates](../../config/operating_gates.json): daily automatic cap1,800,000VND; machine budget1,200VND/ticket; one reviewer, six cases/hour, 45-minute internal wait target; privacy and recorded-cause requirements.
- [Team record](../../TEAM.md) and [submission metadata](../submission.json): real known member and v1 entered; Round 2 fields stay unfilled.

## Immutable evidence

- Criteria signed at `2026-11-19T15:17:04` GMT+7 in commit `21cf02d`, hash `b6419b563a924d481a350f5835a79b2e78f3a895ec0386eb2e4759674d483716`. The remote was verified at `dd1c1a6b7c6d0d237ba5f7d3dcbc370625ed974f` before the first official evaluation.
- Baseline: `R-base-before-20261119-152719-bde05c`.
- Final tested current version: `R-base-after-20261119-152822-6ab0ad`.
- Frozen version: `R-base-prepared-20261119-153024-6ab0ad`.
- Checkpoint `244f5db1` at `2026-11-19T15:30:24` GMT+7. Do not edit guards_round1.py, operating_gates.round1.json, their lock, or the signed criteria.
- Five official evaluation runs, the complete journal, and 550 traces are preserved in [runs](runs/). The failed first guard attempt is retained: it over-restricted overdue in-transit parcels; the corrected general rule restored all legitimate baseline trials before freezing.
- [Checks](checks/): 13 public tests and 9 additional development tests pass; two adhoc challenge traces; baseline and prepared gate output; [integrity and snapshot verification](checks/round1-verification.json).
- Frozen code/config and signed criteria are also copied byte-for-byte into [snapshot](snapshot/); [docs](docs/) contains the completed Round 1 forms. The originals remain in their required repository locations.

Windows had checked out 19 protected source/data/test files with CRLF line endings. Their exact original Git blobs matched the distributed manifest, so those original bytes were restored after confirming no other content differed. Protected-file integrity now passes; no evaluator, label, fixture or agent logic was edited.

## Limits and next step

The baseline contains 22 legitimate public tickets and five deterministic seeds; it is development evidence, not attack coverage or held-out validation. The nine extra probes and two adhoc cases are also development checks. A bootstrap interval of [1,1] on this fixture does not establish perfect production reliability. True tracking quality, burst load, latency, real costs, reviewer availability and stakeholder acceptance remain unmeasured.

Round 1 is complete. Next, obtain the assigned incident number S1–S8 from the coach, evaluate the prepared snapshot before changing anything, and complete Form C, a new monitor and decision v2. No incident or hidden-test pack was opened or downloaded for this work. Full `check_submission --collect` belongs after Round 2; no final-lab completion is claimed here. The student still needs to review/explain the choices and supply their own exit-ticket reflection.
