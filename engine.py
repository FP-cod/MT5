"""
Engine orchestrator: loads allocations, instantiates strategies, polls market data,
computes targets, runs risk checks and routes orders to execution.

This is a lightweight skeleton focusing on wiring the new modules.
"""
import time
from config import ALLOCATIONS_PATH, DRY_RUN
from portfolio.allocator import AllocationManager
from portfolio.risk_manager import RiskManager
from execution.mt5_client import MT5Client
from execution.order_router import OrderRouter
import yaml


class Engine:
    def __init__(self, account_capital: float = 100000.0, dry_run: bool = True):
        self.account_capital = account_capital
        self.alloc = AllocationManager(ALLOCATIONS_PATH)
        self.risk = RiskManager()
        self.mt5 = MT5Client(dry_run=dry_run)
        self.router = OrderRouter(self.mt5)
        # strategies would be instantiated here (skeleton)

    def get_market_prices(self) -> dict:
        # placeholder: in real life we query market_data or broker
        return {}

    def get_current_positions_cash(self) -> dict:
        # placeholder: convert positions to cash exposure per symbol
        return {}

    def run_once(self):
        # expand targets -> per-symbol cash targets
        prices = self.get_market_prices()
        targets = self.alloc.expand_to_symbols(self.account_capital, prices)
        # enforce risk
        targets = self.risk.enforce_limits(targets, self.account_capital)
        current_positions = self.get_current_positions_cash()
        orders = self.router.build_orders(current_positions, targets, prices)
        # send orders
        for o in orders:
            self.mt5.send_order(o)

    def run(self, interval_sec: int = 60):
        self.mt5.connect()
        try:
            while True:
                self.run_once()
                time.sleep(interval_sec)
        except KeyboardInterrupt:
            print("Engine stopped by user")
        finally:
            self.mt5.disconnect()


if __name__ == '__main__':
    Engine(dry_run=True).run(interval_sec=300)
