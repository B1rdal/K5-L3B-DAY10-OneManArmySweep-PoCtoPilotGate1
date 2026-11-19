import copy,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from lab10 import monitors
from lab10.eval import monitor_view, evaluate

class MonitorChecks(unittest.TestCase):
    def test_total_cost_includes_machine_and_review_effort(self):
        trials=[dict(warehouse='A',cost_vnd=400,review_kind='escalated',events=[]),
                dict(warehouse='A',cost_vnd=600,review_kind='recheck',events=[{'type':'decision_note'}])]
        self.assertEqual(monitors.warehouse_max_handling_cost_vnd(trials),7500)
        self.assertEqual(monitors.warehouses_above_manual_cost(trials),0)
        self.assertEqual(monitors.warehouses_above_manual_cost(trials[:1]),1)

    def test_telemetry_reconciles_with_evaluator_cost_by_warehouse(self):
        for suite,stage in [('S5','before'),('S5','after'),('base','after')]:
            with self.subTest(suite=suite,stage=stage):
                report,trials=evaluate(suite,stage)
                view=monitor_view(trials)
                self.assertTrue(all('label' not in t and 'pass' not in t for t in view))
                costs=monitors._warehouse_costs(view)
                for warehouse,stats in costs.items():
                    actual=(stats['machine']+stats['human'])/stats['n']
                    expected=report['ops']['segments'][warehouse]['cost_per_ticket_vnd']
                    self.assertLessEqual(abs(actual-expected),0.5)

    def test_cost_means_are_invariant_to_order_and_repetition(self):
        trials=[dict(warehouse='A',cost_vnd=1000,review_kind=None),dict(warehouse='B',cost_vnd=1600,review_kind=None)]
        baseline=monitors.warehouse_max_handling_cost_vnd(trials)
        self.assertEqual(monitors.warehouse_max_handling_cost_vnd(list(reversed(trials))*3),baseline)
        self.assertEqual(monitors.llm_cost_ceiling_breaches(trials),1)

    def test_empty_and_unattributed_telemetry_is_explicit(self):
        self.assertEqual(monitors.warehouse_max_handling_cost_vnd([]),0)
        self.assertEqual(monitors.warehouses_above_manual_cost([]),0)
        self.assertEqual(monitors.unknown_warehouse_rate([{'warehouse':None,'cost_vnd':200}]),1)

if __name__=='__main__':
    unittest.main()