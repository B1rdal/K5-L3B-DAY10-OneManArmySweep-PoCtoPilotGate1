"""★ FILE ĐỘI SỬA (2/3): chỉ số theo dõi (monitor). Thêm ÍT NHẤT MỘT chỉ số bắt được sự cố của bàn.

Mỗi monitor nhận danh sách trial (KHÔNG có nhãn đúng/sai, giống production) và trả về một số.
Một trial = {"ticket_id", "seed", "day", "status", "amount_vnd", "ticket", "events", "ledger", "faults", "outbound",
             "arrive_min", "warehouse", "cost_vnd", "review_kind", "queue_wait_min", "queue_stuck"}
  "day"            một ngày vận hành giả lập: các ticket cùng "day" và cùng "seed" chạy nối nhau trên cùng một sổ cái
  "arrive_min"     phút ticket tới trong ca (0..480)          "warehouse"   kho của đơn
  "cost_vnd"       tiền LLM + nền tảng đã tốn cho ticket      "review_kind" None / "escalated" (trợ lý chuyển người) /
  "queue_wait_min" số phút chờ người duyệt (None nếu không vào hàng chờ)     "recheck" (nhân viên tự kiểm lại)
Chỉ số có thể là kỹ thuật (tỉ lệ model đè số trong ticket lên DB), vận hành (số ca cần người trong giờ đông nhất),
hay kinh doanh (tỉ lệ ticket trợ lý đọc xong vẫn phải chuyển người).

lab10.grade kiểm: monitor chạy không lỗi, và giá trị trên gói sự cố khác giá trị trên bộ nền,
tức là monitor "sáng đèn" khi sự cố xảy ra.
"""


def escalation_rate(trials):
    return sum(t["status"] == "escalated" for t in trials) / max(1, len(trials))


from collections import defaultdict

from .world import DATA, load_json


def _warehouse_costs(trials):
    """Operational unit costs from telemetry and the versioned reference prices."""
    facts = load_json(DATA / "world.json")["ops_facts"]
    review_price = facts["review_cost_per_ticket_vnd"]
    note_units = facts["recheck_with_note_units"]
    groups = defaultdict(lambda: {"n": 0, "machine": 0.0, "human": 0.0, "refund_cash": 0.0})
    for trial in trials:
        warehouse = trial.get("warehouse")
        if not warehouse:
            continue
        row = groups[warehouse]
        row["n"] += 1
        row["machine"] += float(trial.get("cost_vnd") or 0)
        review_kind = trial.get("review_kind")
        if review_kind == "escalated":
            row["human"] += review_price
        elif review_kind == "recheck":
            has_note = any(e.get("type") == "decision_note" for e in trial.get("events", []))
            row["human"] += review_price * (note_units if has_note else 1.0)
        row["refund_cash"] += sum(r["amount_vnd"] for r in trial.get("ledger", []))
    return groups


def warehouse_max_handling_cost_vnd(trials):
    groups = _warehouse_costs(trials)
    return max(((g["machine"] + g["human"]) / g["n"] for g in groups.values()), default=0.0)


def warehouses_above_manual_cost(trials):
    manual = load_json(DATA / "world.json")["ops_facts"]["manual_cost_per_ticket_vnd"]
    return sum((g["machine"] + g["human"]) / g["n"] > manual for g in _warehouse_costs(trials).values())


def llm_cost_ceiling_breaches(trials):
    cap = load_json(DATA / "world.json")["ops_limits"]["max_llm_cost_per_ticket_vnd"]
    return sum(float(t.get("cost_vnd") or 0) > cap for t in trials)


def unknown_warehouse_rate(trials):
    return sum(not t.get("warehouse") for t in trials) / max(1, len(trials))


MONITORS = {
    "escalation_rate": escalation_rate,
    "warehouse_max_handling_cost_vnd": warehouse_max_handling_cost_vnd,
    "warehouses_above_manual_cost": warehouses_above_manual_cost,
    "llm_cost_ceiling_breaches": llm_cost_ceiling_breaches,
    "unknown_warehouse_rate": unknown_warehouse_rate,
}
STARTER_MONITORS = ("escalation_rate",)
