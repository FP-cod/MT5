from .base import Strategy

class ForexAlgoStrategy(Strategy):
    """Dedicated forex algo for the 5% bucket.
    Placeholder: can implement mean-reversion on currency pairs or small trend signals.
    """
    def generate_signals(self, market_data: dict, portfolio_state: dict) -> list:
        signals = []
        for symbol, df in market_data.items():
            if df is None or df.empty:
                continue
            try:
                close = df["close"].astype(float)
                sma20 = close.rolling(20).mean().iloc[-1]
                last = close.iloc[-1]
            except Exception:
                continue
            if last > sma20:
                signals.append({"symbol": symbol, "side": "buy", "score": 0.5, "size_hint": 0.0})
            elif last < sma20:
                signals.append({"symbol": symbol, "side": "sell", "score": 0.5, "size_hint": 0.0})
        return signals
