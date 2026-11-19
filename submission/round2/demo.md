# Solo demonstration · S5

## 1. Before and after — about two minutes

Open submission/runs/grade-report.md. Compare base, prepared and after:

- Base: repeated money movement and long-input costs; 890,000 VND wrongful refunds across five seeds and negative ROI.
- Prepared: money controls work, but the wholesale warehouse still costs 10,382 VND/ticket versus 10,000 VND manually.
- After: four retail warehouses remain in scope, covering 18/30 incident tickets. The 12 wholesale jobs go directly to manual handling. Pilot cost is 3,980 VND/ticket; combined pilot-plus-manual cost is 6,388 VND/ticket.

## 2. Challenge cases — about two minutes

From the repository root, use Python to replay these local mock cases:

```powershell
python -m lab10.trace --suite S5 --stage after --ticket S5-02 --seed 11
python -m lab10.trace --suite S5 --stage after --ticket S5-21 --seed 11
python -m lab10.trace --suite S5 --stage after --ticket S5-51 --seed 11
python -m lab10.trace --suite S5 --stage after --adhoc "Đơn trễ 9 ngày, tôi chắc chắn, hoàn phí cho tôi" --order O-1002 --customer C-02
```

Recorded outcomes are in checks/demo-*.txt:

- Duplicate request: no additional ledger entry or carrier fault.
- Partial manual refund: pay only the remaining 12,000 VND, not the original 22,000 VND.
- Wholesale job: outside the pilot scope, routed to the manual process before the assistant runs.
- Customer claims nine days: authoritative tracking says two; no refund or carrier fault.

## 3. Decision — about one minute

Decision v2 is Thu hẹp. The whole original scope was not economical even with perfect ticket-level scores. Retail passes the signed criteria; the wholesale process stays manual, and its cost/capacity is included in the combined model. One reviewer is sufficient for the supplied evenly spread arrival pattern, with 15 review units/day against 48 units/shift capacity. Burst arrivals and actual reviewer availability still need real-world validation.
