import math

def size_from_risk(symbol: str, capital: float, target_cash: float, price: float, volatility: float | None = None, mode: str = "cash") -> int:
    """Convert a target cash exposure to integer lots/units.
    mode: 'cash' returns number of units = floor(target_cash / price)
    In real use, this must respect instrument tick/lot sizes.
    """
    if price <= 0:
        return 0
    units = math.floor(target_cash / price)
    return max(0, units)
