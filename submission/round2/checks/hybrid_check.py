"""Reconcile excluded manual work with the pilot cost/queue model."""
import copy,json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from lab10 import ops
from lab10.eval import arrivals
from lab10.world import load_suite

world,tickets=load_suite('S5')
gates=ops.load_gates('after')
reports=[p for p in (ROOT/'runs').glob('R-S5-after-*/report.json')]
report_path=max(reports,key=lambda p:p.stat().st_mtime)
report=json.loads(report_path.read_text(encoding='utf-8'))
trials=[json.loads(p.read_text(encoding='utf-8')) for p in sorted((report_path.parent/'traces').glob('*.json'))]
arrival=arrivals(world,tickets)
warehouses={o['order_id']:o['warehouse_id'] for o in world['orders']}
excluded=[t for t in tickets if not ops.in_scope(t,world,gates)]
seeds=sorted({t['seed'] for t in trials})
for seed in seeds:
    for ticket in excluded:
        # Synthetic manual jobs model effort/capacity only, not correctness of payouts.
        trials.append(dict(ticket_id=ticket['ticket_id'],scenario=ticket.get('scenario',ticket['ticket_id']),
            seed=seed,status='escalated',warehouse=warehouses[ticket['order_id']],
            arrive_min=arrival[ticket['ticket_id']],cost_vnd=0,events=[],ledger=[],
            wrongful_refund_vnd=0))
summary=ops.summarize_ops(trials,world,gates)
manual_cost=len(excluded)*world['ops_facts']['manual_cost_per_ticket_vnd']
result=dict(source_run_id=report['run_id'],pilot_tickets_per_day=report['ops']['tickets_in_scope_per_day'],
    direct_manual_tickets_per_day=len(excluded),direct_manual_cost_per_day_vnd=manual_cost,
    manual_routing_assumption='Wholesale tickets bypass the assistant and are modeled as one manual review unit at the reference 10000 VND rate.',
    manual_refund_accuracy_measured=False,
    combined_cost=summary['cost'],combined_queue=summary['queue'],combined_segments=summary['segments'],
    combined_violations=summary['violations'],
    original_all_scope_cost_per_day_vnd=196230,
    savings_vs_prepared_all_scope_vnd=196230-(summary['cost']['agent_cost_per_day_vnd']+summary['cost']['review_cost_per_day_vnd']+summary['cost']['standby_cost_per_day_vnd']))
assert len(excluded)==12 and report['ops']['coverage']>0
assert summary['queue']['stuck']==0 and summary['queue']['wait_max_min']<=45
assert summary['cost']['cost_per_ticket_vnd']<=7500 and summary['cost']['roi']>=0.3
assert not summary['violations']
(ROOT/'submission/round2/checks/hybrid-manual-cost-and-capacity.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps(result,ensure_ascii=False,indent=2))