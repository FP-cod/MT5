from __future__ import annotations

from datetime import datetime, timedelta
from types import SimpleNamespace


TIMEFRAME_M1 = 1
TIMEFRAME_M5 = 5
TIMEFRAME_M15 = 15
TIMEFRAME_M30 = 30
TIMEFRAME_H1 = 60
TIMEFRAME_D1 = 1440
TIMEFRAME_W1 = 10080
TIMEFRAME_MN1 = 43200

ORDER_TYPE_BUY = 0
ORDER_TYPE_SELL = 1
TRADE_ACTION_DEAL = 1
ORDER_TIME_GTC = 0
ORDER_FILLING_IOC = 3
TRADE_RETCODE_DONE = 10009


class SimulatedMT5:
    """Minimal MT5-compatible stub used for dry runs and local development."""

    TIMEFRAME_M1 = TIMEFRAME_M1
    TIMEFRAME_M5 = TIMEFRAME_M5
    TIMEFRAME_M15 = TIMEFRAME_M15
    TIMEFRAME_M30 = TIMEFRAME_M30
    TIMEFRAME_H1 = TIMEFRAME_H1
    TIMEFRAME_D1 = TIMEFRAME_D1
    TIMEFRAME_W1 = TIMEFRAME_W1
    TIMEFRAME_MN1 = TIMEFRAME_MN1

    ORDER_TYPE_BUY = ORDER_TYPE_BUY
    ORDER_TYPE_SELL = ORDER_TYPE_SELL
    TRADE_ACTION_DEAL = TRADE_ACTION_DEAL
    ORDER_TIME_GTC = ORDER_TIME_GTC
    ORDER_FILLING_IOC = ORDER_FILLING_IOC
    TRADE_RETCODE_DONE = TRADE_RETCODE_DONE

    @staticmethod
    def initialize() -> bool:
        return True

    @staticmethod
    def login(*args, **kwargs) -> bool:
        return True

    @staticmethod
    def shutdown() -> None:
        return None

    @staticmethod
    def last_error() -> str:
        return "MetaTrader5 is not installed; dry-run simulator is active."

    @staticmethod
    def symbol_info_tick(symbol: str) -> SimpleNamespace:
        return SimpleNamespace(ask=1.0, bid=0.9999)

    @staticmethod
    def symbol_info(symbol: str) -> SimpleNamespace:
        return SimpleNamespace(
            point=0.00001,
            digits=5,
            volume_step=0.01,
            volume_min=0.01,
            volume_max=100.0,
        )

    @staticmethod
    def positions_get(symbol: str | None = None):
        return []

    @staticmethod
    def order_send(request: dict):
        return SimpleNamespace(retcode=TRADE_RETCODE_DONE, comment="dry_run", order=1)

    @staticmethod
    def copy_rates_from_pos(symbol: str, timeframe: int, start_pos: int, count: int):
        now = datetime.utcnow()
        candles = []
        base = 1.1000
        for idx in range(count):
            ts = int((now - timedelta(minutes=timeframe * (count - idx))).timestamp())
            open_price = base + idx * 0.0001
            close_price = open_price + 0.0002
            high_price = close_price + 0.0003
            low_price = open_price - 0.0002
            candles.append(
                {
                    "time": ts,
                    "open": open_price,
                    "high": high_price,
                    "low": low_price,
                    "close": close_price,
                    "tick_volume": 100,
                    "spread": 0,
                    "real_volume": 0,
                }
            )
        return candles


initialize = SimulatedMT5.initialize
login = SimulatedMT5.login
shutdown = SimulatedMT5.shutdown
last_error = SimulatedMT5.last_error
symbol_info_tick = SimulatedMT5.symbol_info_tick
symbol_info = SimulatedMT5.symbol_info
positions_get = SimulatedMT5.positions_get
order_send = SimulatedMT5.order_send
copy_rates_from_pos = SimulatedMT5.copy_rates_from_pos

mt5 = SimulatedMT5()

__all__ = [
    "mt5",
    "SimulatedMT5",
    "TIMEFRAME_M1",
    "TIMEFRAME_M5",
    "TIMEFRAME_M15",
    "TIMEFRAME_M30",
    "TIMEFRAME_H1",
    "TIMEFRAME_D1",
    "TIMEFRAME_W1",
    "TIMEFRAME_MN1",
    "ORDER_TYPE_BUY",
    "ORDER_TYPE_SELL",
    "TRADE_ACTION_DEAL",
    "ORDER_TIME_GTC",
    "ORDER_FILLING_IOC",
    "TRADE_RETCODE_DONE",
    "initialize",
    "login",
    "shutdown",
    "last_error",
    "symbol_info_tick",
    "symbol_info",
    "positions_get",
    "order_send",
    "copy_rates_from_pos",
]
