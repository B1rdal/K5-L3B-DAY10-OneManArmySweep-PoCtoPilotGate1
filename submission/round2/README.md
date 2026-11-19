# Final result · Solo Round 2 · S5

Team: K5-L3B-DAY10-OneManArmySweep-PoCtoPilotGate1. Member: Dao Duc Son, 2A202604105.

**Decision v2: Thu hẹp — Narrow the pilot.** Retain the HN, HCM, DN and CT retail warehouses; send HCM-B2B directly to the manual process. S5 was selected by a uniform random draw before any card was read for this solo run; see selection.json.

| Measure on S5 | Base | Frozen Round 1 | Final pilot |
|---|---:|---:|---:|
| Scope | 30/30 tickets | 30/30 | 18/30; 12 direct manual |
| Successful trials | 125/150 | 150/150 | 90/90 in scope |
| Wrongful refunds, all five seeds | 890,000 VND | 0 | 0 |
| Wrongful carrier faults | 20 | 0 | 0 |
| PII leaks | 0 | 0 | 0 |
| Maximum machine cost per ticket | 2,412 VND | 765 VND | 765 VND |
| Pilot cost per ticket | 6,083 VND | 6,541 VND | 3,980 VND |
| Pilot ROI | -0.33 | 0.53 | 1.51 |
| Wholesale warehouse cost per ticket | 11,326 VND | 10,382 VND | 10,000 VND via direct manual model |
| Warehouses in the pilot exceeding manual cost | 1 | 1 | 0 |

The final pilot ROI covers the 18 in-scope tickets. A separate reconciliation includes the 12 wholesale manual jobs: **6,388 VND per ticket overall, ROI 0.57, 15 human review units/day, maximum queue wait 0 minutes**, using one reviewer at six units/hour and the supplied 480-minute arrival pattern. Direct manual work costs 120,000 VND/day; it is included rather than treated as free or discarded. This is a cost/capacity model, not measured correctness of manual payouts or proof of burst-load performance.

## Deliverables

- [Completed Form C](../../templates/form-c-incident.md): C0–C12, including initial/final fault trees, S5 data map, risk register, runbooks 4–5 and decision v2.
- [Final metadata](../submission.json): incident S5, decision v1/v2 and the three required sentences copied exactly from C12.
- [Operating gates](../../config/operating_gates.json): retail warehouse allowlist; existing refund/budget/staffing/privacy limits retained.
- [Monitors](../../lab10/monitors.py): warehouse handling cost, warehouses above manual cost, machine-cost ceiling breaches and unknown warehouse rate. No labels are used.
- [Final grade](../runs/grade-report.md): `R-S5-grade-20261119-181231-ed310d`; PASS-VISIBLE. Integrity, criteria, visible, regression and monitor checks pass. Hidden tests are unavailable and no hidden-test score is claimed.
- [Combined manual and pilot cost/capacity](checks/hybrid-manual-cost-and-capacity.json), with [reproducible calculation](checks/hybrid_check.py).
- [Solo demonstration](demo.md), with actual trace outputs in checks/.

## Validation

The provided submission checker reports **ĐỦ THÀNH PHẦN**. The full result is in [the collection check](checks/submission-collection.txt).

- All 110 baseline trials still pass; baseline coverage remains 100%.
- All 90 in-scope S5 trials pass, including the 25 attack trials; five-seed reliability is 1.0.
- 13 public tests, 9 guard development tests and 4 monitor tests pass.
- Prepared snapshot `244f5db1` and criteria hash `b6419b56` remain unchanged.
- Initial S5 report: `R-S5-grade-20261119-180819-6ab0ad`; first fixes addressed warehouse scope and cost monitoring. The Round 1 money and budget guards already prevented duplicate/partial-refund and long-input failures.

The official package is under submission/code, submission/config, submission/docs and submission/runs, with the generated manifest. Source forms remain under templates/.
