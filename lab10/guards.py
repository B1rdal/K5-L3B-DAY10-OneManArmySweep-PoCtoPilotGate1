"""Round-one source-of-truth, money authority, and third-party safeguards.

No case IDs, seed checks, labels, or incident-specific text are used.
"""
from . import helpers as H
from .tools import Verdict


def _facts(ctx):
    order = ctx.tools.lookup_order(ctx.ticket.get("order_id"))
    policy = H.effective_policy(ctx.tools.lookup_policies(), ctx.as_of)
    if order is None or policy is None:
        raise ValueError("missing order or effective policy")
    if order["customer_id"] != ctx.ticket["customer_id"]:
        raise ValueError("ticket principal does not own order")
    parcels = order.get("parcels") or []
    if not parcels:
        raise ValueError("missing parcel tracking")
    parcel_id = ctx.ticket.get("parcel_id")
    if parcel_id and not any(p["parcel_id"] == parcel_id for p in parcels):
        raise ValueError("ticket parcel does not belong to order")
    parcel = H.ticket_parcel(order, ctx.ticket, ctx.as_of)
    # An overdue in-transit parcel is eligible under the late policy too.
    # Reject inconsistent/missing status facts, rather than requiring delivery.
    status = parcel.get("status")
    if status not in ("DELIVERED", "IN_TRANSIT"):
        raise ValueError("unsupported parcel tracking status")
    if (status == "DELIVERED") != bool(parcel.get("delivered_date")):
        raise ValueError("tracking status and delivery date disagree")
    delay = H.db_delay_days(parcel, ctx.as_of)
    return order, policy, parcel, delay


def pre_guard(ctx):
    # G1: admission uses dated policy and authenticated DB scope, before the LLM.
    try:
        policy = H.effective_policy(ctx.tools.lookup_policies(), ctx.as_of)
        if policy is None:
            return Verdict.escalate("G1: no policy effective on the processing date")
        order = ctx.tools.lookup_order(ctx.ticket.get("order_id"))
        if order is not None:
            _facts(ctx)
        facts = ctx.tools.ops_facts()
        price = facts.get("llm_cost", {})
        texts = [ctx.ticket.get("text", "")]
        if order and order.get("checkout_note"):
            texts.append(order["checkout_note"])
        estimate = price.get("platform_per_ticket_vnd", 0)
        estimate += sum(price.get("extract_base_vnd", 0) + len(s) // 4 *
                        price.get("extract_per_4_chars_vnd", 0) for s in texts)
        estimate += 2 * price.get("policy_check_vnd", 0) + price.get("confirm_vnd", 0)
        if ctx.gates.get("operations", {}).get("decision_note"):
            estimate += price.get("decision_note_vnd", 0)
        budget = ctx.gates.get("business", {}).get("cost_budget_per_ticket_vnd")
        limits = [v for v in (budget, ctx.tools.ops_limits().get("max_llm_cost_per_ticket_vnd")) if v is not None]
        if limits and estimate > min(limits):
            return Verdict.escalate("G1: estimated bounded LLM path exceeds ticket budget")
        ctx.log("policy_pinned", policy_id=policy["policy_id"], estimated_cost_vnd=estimate)
        return Verdict.allow(policy_id=policy["policy_id"])
    except (KeyError, ValueError, TypeError) as exc:
        return Verdict.escalate("G1: incomplete or inconsistent authoritative facts: " + str(exc))


def write_gate(ctx, action):
    tool = action.get("tool")
    if action.get("ticket_id") != ctx.ticket.get("ticket_id"):
        return Verdict.escalate("write is outside the current ticket")
    if tool == "send_reply":
        if action.get("customer_id") != ctx.ticket.get("customer_id"):
            return Verdict.deny("G3: reply recipient is outside authenticated ticket")
        paid = sum(r["amount_vnd"] for r in ctx.tools.ledger_rows(ticket_id=ctx.ticket["ticket_id"]))
        if action.get("amount_vnd", 0) != paid:
            text = (f"LogiX đã ghi nhận khoản hoàn {paid:,}đ theo sổ cái." if paid else
                    "LogiX chưa ghi nhận khoản hoàn nào cho yêu cầu này; CSKH sẽ kiểm tra.")
            return Verdict.modify("G2: reply must match committed ledger", text=text, amount_vnd=paid)
        return Verdict.allow()
    if tool not in ("issue_refund", "file_carrier_fault", "notify_carrier"):
        return Verdict.deny("unsupported write tool")
    try:
        order, policy, parcel, delay = _facts(ctx)
    except (KeyError, ValueError, TypeError) as exc:
        return Verdict.escalate("write needs verified facts: " + str(exc))
    if tool in ("issue_refund", "file_carrier_fault") and action.get("order_id") != order["order_id"]:
        return Verdict.escalate("write is outside the current order")

    if tool == "issue_refund":
        # G2: compute entitlement, residual, approval authority and caps outside the model.
        if delay > 0 and not parcel.get("delay_cause"):
            return Verdict.escalate("G2: delivery/cause must be verified before automatic money movement")
        entitled = H.entitlement_vnd(policy, order, delay, parcel.get("delay_cause"))
        already = sum(r["amount_vnd"] for r in ctx.tools.ledger_rows(order_id=order["order_id"]))
        remaining = max(0, entitled - already)
        if remaining <= 0:
            return Verdict.deny("G2: no unpaid policy entitlement; duplicate writes are not permitted")
        approval_id = action.get("approval_id")
        if approval_id:
            candidates = ctx.tools.lookup_approvals(approval_id=approval_id)
            approver = ctx.gates.get("operations", {}).get("approver_id")
            valid = any(a.get("status") == "valid" and a.get("expires_at", "") >= ctx.as_of
                        and all(a.get(k) == v for k, v in {
                            "ticket_id": ctx.ticket["ticket_id"], "order_id": order["order_id"],
                            "customer_id": order["customer_id"]}.items())
                        and a.get("max_vnd", 0) >= remaining
                        and bool(a.get("approver_id"))
                        and (not approver or a.get("approver_id") == approver)
                        for a in candidates)
            if not valid:
                return Verdict.escalate("G2: approval is stale, insufficient or outside this claim/approver")
            if any(r.get("approval_id") == approval_id for r in ctx.tools.ledger_rows()):
                return Verdict.escalate("G2: approval already consumed in ledger")
        elif remaining > policy["auto_limit_vnd"]:
            return Verdict.escalate("G2: policy amount requires scoped human approval")
        if not approval_id:
            limits = ctx.tools.ops_limits()
            customer_cap = limits.get("max_auto_refund_per_customer_per_day_vnd")
            # ReadTools exposes no row date: include all available rows conservatively.
            customer_spent = sum(r["amount_vnd"] for r in ctx.tools.ledger_rows(customer_id=order["customer_id"])
                                 if not r.get("approval_id"))
            if customer_cap is not None and customer_spent + remaining > customer_cap:
                return Verdict.escalate("G2: cumulative customer refunds require human review")
            caps = [v for v in (limits.get("daily_auto_refund_budget_vnd"),
                                ctx.gates.get("business", {}).get("daily_refund_cap_vnd")) if v is not None]
            if caps and ctx.tools.auto_refund_today_vnd() + remaining > min(caps):
                return Verdict.escalate("G2: daily automatic refund cap requires human review")
        if (action.get("amount_vnd") != remaining or action.get("payer") != "LOGIX"
                or action.get("basis") != "policy"):
            return Verdict.modify("G2: use authoritative unpaid policy amount and payer",
                                  amount_vnd=remaining, payer="LOGIX", basis="policy")
        return Verdict.allow()

    if tool == "file_carrier_fault":
        # G3: penalties identify the real parcel/carrier and require recorded evidence.
        if not H.carrier_at_fault(policy, parcel, delay):
            return Verdict.deny("G3: no recorded policy-supported carrier fault")
        if ctx.tools.fault_rows(ticket_id=ctx.ticket["ticket_id"], parcel_id=parcel["parcel_id"]):
            return Verdict.deny("G3: duplicate carrier fault for this claim")
        cap = ctx.tools.ops_limits().get("max_auto_strikes_per_carrier_per_day")
        if cap is not None and len(ctx.tools.fault_rows(carrier_id=parcel["carrier_id"])) >= cap:
            return Verdict.escalate("G3: daily carrier strike cap; reconcile any refund already committed")
        correct = {"parcel_id": parcel["parcel_id"], "carrier_id": parcel["carrier_id"],
                   "driver_id": parcel.get("driver_id"), "delay_days": delay}
        if any(action.get(k) != v for k, v in correct.items()):
            return Verdict.modify("G3: carrier fault must match the ticket parcel in tracking", **correct)
        return Verdict.allow()

    # G3: reconstruct notices from allowed DB fields, never customer-controlled text.
    fault = ctx.tools.fault_rows(ticket_id=ctx.ticket["ticket_id"], order_id=order["order_id"],
                                parcel_id=parcel["parcel_id"], carrier_id=parcel["carrier_id"])
    if not fault:
        return Verdict.deny("G3: no matching recorded fault authorizes a carrier notice")
    safe = {"order_id": order["order_id"], "parcel_id": parcel["parcel_id"],
            "district": order.get("recipient", {}).get("district"), "delay_days": delay}
    blocked = set(ctx.gates.get("legal", {}).get("pii_fields_blocked_to_third_party") or [])
    allowed = set(policy.get("carrier_notice_fields") or []) - blocked
    payload = {k: v for k, v in safe.items() if k in allowed}
    if action.get("payload") != payload or action.get("carrier_id") != parcel["carrier_id"]:
        return Verdict.modify("G3: minimum policy-schema payload from authoritative fields",
                              payload=payload, carrier_id=parcel["carrier_id"])
    return Verdict.allow()
