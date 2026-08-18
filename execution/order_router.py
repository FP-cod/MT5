from typing import Dict, List

class OrderRouter:
    """Map target positions -> list of orders.
    This is intentionally simple: in real life you'd want incremental orders, checks for existing positions, etc.
    """
    def __init__(self, mt5_client):
        self.mt5 = mt5_client

    def build_orders(self, current_positions: Dict[str, float], targets: Dict[str, float], prices: Dict[str, float]) -> List[Dict]:
        orders = []
        for sym, target_cash in targets.items():
            price = prices.get(sym, None)
            if price in (None, 0):
                continue
            current_cash = current_positions.get(sym, 0.0)
            diff = target_cash - current_cash
            if abs(diff) / max(1.0, target_cash) < 0.001:
                continue
            units = int(diff // price)
            if units == 0:
                continue
            side = "buy" if units > 0 else "sell"
            orders.append({"symbol": sym, "units": abs(units), "side": side, "price": price})
        return orders
