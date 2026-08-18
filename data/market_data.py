"""
Simple market data adapter (skeleton).
Provides fetch_history(symbol, timeframe, start, end) and a stub stream_live generator.

In production you would plug exchange/broker APIs, a database cache, and websocket/tick feeders.
"""
from typing import Dict, Generator
import pandas as pd


def fetch_history(symbol: str, timeframe: str, start=None, end=None) -> pd.DataFrame:
    """Return a pandas DataFrame with DatetimeIndex and columns [open,high,low,close,volume].
    This is a stub: tests/backtests should monkeypatch or replace this with real data.
    """
    # Minimal empty DataFrame
    df = pd.DataFrame(columns=["open", "high", "low", "close", "volume"])
    return df


def stream_live(symbols) -> Generator[Dict, None, None]:
    """Yield market ticks or OHLC updates as dicts: {"symbol":..., "timestamp":..., "price":...}
    Stub implementation that yields nothing.
    """
    while False:
        yield {}
