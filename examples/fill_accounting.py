"""Pure cumulative-fill accounting. No broker access and no price guesses."""
import math

VERSION = "cumulative-owned-fills-v1"
TERMINAL = {"FILLED", "CANCELLED", "FAILED", "EXPIRED"}


class ReconciliationError(RuntimeError):
    pass


def quantity(value):
    try:
        number = float(value)
    except (TypeError, ValueError):
        raise ReconciliationError("missing broker quantity") from None
    if not math.isfinite(number) or number < 0 or not number.is_integer():
        raise ReconciliationError("invalid whole-share quantity")
    return int(number)


def observe(active, details):
    """Replace each cumulative snapshot, never add it twice. Reject regressions."""
    ids = active["ids"]
    owned = ({ids['master'], *active.get('premarket_exit_ids', [])}
             if active.get('execution_cohort') == 'premarket_limit_paper_v1'
             else {ids[k] for k in ("master", "target", "stop")})
    owned.update(str(active[k]) for k in ("early_exit_id", "eod_exit_id") if active.get(k))
    ledger = dict(active.get("fill_ledger") or {})
    for order_id in owned:
        item = details.get(order_id)
        if item is None:
            raise ReconciliationError("owned order detail unavailable")
        filled = quantity(item.get("filled_quantity"))
        # The sandbox detail API returns total_quantity; placement uses quantity.
        total = quantity(item.get("total_quantity", item.get("quantity")))
        if item.get("total_quantity") is not None and item.get("quantity") is not None:
            if quantity(item["total_quantity"]) != quantity(item["quantity"]):
                raise ReconciliationError("broker total quantity fields disagree")
        status = str(item.get("status") or "").upper()
        if filled > total or not status or (status == "FILLED" and filled != total):
            raise ReconciliationError("inconsistent order fill status")
        old = ledger.get(order_id, {})
        if filled < old.get("filled_quantity", 0):
            raise ReconciliationError("cumulative filled quantity regressed")
        if old.get("status") in TERMINAL and status not in TERMINAL:
            raise ReconciliationError("terminal order status regressed")
        average = None
        if filled:
            try:
                average = float(item.get("filled_price"))
            except (TypeError, ValueError):
                raise ReconciliationError("filled order lacks actual average price") from None
            if not math.isfinite(average) or average <= 0:
                raise ReconciliationError("filled order lacks actual average price")
        ledger[order_id] = {"filled_quantity": filled, "quantity": total,
                            "average_price": average, "status": status}
    entry = ledger[ids["master"]]
    exited = sum(v["filled_quantity"] for k, v in ledger.items() if k != ids["master"])
    if exited > entry["filled_quantity"]:
        raise ReconciliationError("closing fills exceed owned entry fills")
    active["fill_ledger"] = ledger
    active.setdefault("requested_quantity", active.get("quantity"))
    active["entry_filled_quantity"] = entry["filled_quantity"]
    active["entry_filled_price"] = entry["average_price"]
    active["entry_remaining_quantity"] = (entry["quantity"] - entry["filled_quantity"]
                                           if entry["status"] not in TERMINAL else 0)
    active["exit_filled_quantity"] = exited
    active["quantity"] = entry["filled_quantity"] - exited
    return active["quantity"]


def result(active):
    ledger = active.get("fill_ledger") or {}
    master_id = active["ids"]["master"]
    entry = ledger.get(master_id, {})
    filled = entry.get("filled_quantity", 0)
    exits = [v for k, v in ledger.items() if k != master_id]
    exited = sum(v["filled_quantity"] for v in exits)
    if not filled or exited != filled or active.get("manual_quantity_change"):
        return {"pnl_before_fees": None, "exit_price": None, "quantity": filled,
                "pnl_verified": False}
    value = sum(v["filled_quantity"] * (v["average_price"] or 0) for v in exits)
    sign = 1 if active["direction"] == "long" else -1
    return {"pnl_before_fees": sign * (value - filled * entry["average_price"]),
            "exit_price": value / filled, "quantity": filled, "pnl_verified": True}


def held_quantity(rows, symbol, direction):
    matches = [r for r in rows if str(r.get("symbol") or "").upper() == symbol.upper()]
    if not matches:
        return 0
    if len(matches) != 1:
        raise ReconciliationError("ambiguous broker position")
    row = matches[0]
    try:
        raw = float(row["quantity"])
    except (KeyError, TypeError, ValueError):
        raise ReconciliationError("broker position quantity unavailable") from None
    qty = quantity(abs(raw))
    side = str(row.get("side") or "").upper()
    if qty and ((direction == "long" and (raw < 0 or side in {"SHORT", "SELL"}))
                or (direction == "short" and raw >= 0 and side not in {"SHORT", "SELL"})):
        raise ReconciliationError("broker position direction differs from owned trade")
    return qty
