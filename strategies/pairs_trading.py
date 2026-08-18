from .base import Strategy
import numpy as np

class PairsTradingStrategy(Strategy):
    """Pairs trading skeleton: compute zscore of spread and open mean-reversion trades.
    This module expects pairs_candidates to be provided in the config.
    """

    def generate_signals(self, market_data: dict, portfolio_state: dict) -> list:
        signals = []
        pairs = self.config.get("pairs_candidates", [])
        for a, b in pairs:
            a_df = market_data.get(a)
            b_df = market_data.get(b)
            if a_df is None or b_df is None or a_df.empty or b_df.empty:
                continue
            try:
                a_close = a_df["close"].astype(float)
                b_close = b_df["close"].astype(float)
                # simple hedge ratio via last price
                ratio = a_close.iloc[-1] / b_close.iloc[-1]
                spread = a_close - ratio * b_close
                z = (spread - spread.mean()) / (spread.std() + 1e-9)
                z_last = z.iloc[-1]
            except Exception:
                continue
            # open positions when |z| > 2, close when |z| < 0.5
            if z_last > 2.0:
                # a is rich: short a, long b
                signals.append({"symbol": a, "side": "sell", "score": float(z_last), "size_hint": 0.0})
                signals.append({"symbol": b, "side": "buy", "score": float(z_last), "size_hint": 0.0})
            elif z_last < -2.0:
                signals.append({"symbol": a, "side": "buy", "score": float(-z_last), "size_hint": 0.0})
                signals.append({"symbol": b, "side": "sell", "score": float(-z_last), "size_hint": 0.0})
        return signals
