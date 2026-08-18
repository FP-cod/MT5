"""
Backtest harness skeleton that reuses strategy interfaces and allocation manager.
Returns simple PnL/time series and trades list.
"""
from portfolio.allocator import AllocationManager

class BacktestEngine:
    def __init__(self, allocations_path: str, initial_capital: float = 100000.0):
        self.alloc = AllocationManager(allocations_path)
        self.initial_capital = initial_capital

    def run(self, market_data: dict, start=None, end=None):
        # Very small skeleton: compute static targets and produce no trades.
        prices = {s: df["close"].iloc[-1] if (df is not None and not df.empty) else 0 for s, df in market_data.items()}
        targets = self.alloc.expand_to_symbols(self.initial_capital, prices)
        return {"targets": targets, "prices": prices}
