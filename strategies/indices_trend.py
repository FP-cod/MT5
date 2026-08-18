from .base import Strategy

class IndicesTrendStrategy(Strategy):
    """Simple trend-following skeleton for indices/futures.
    Uses moving averages / breakout style signals (skeleton).
    """
    def __init__(self, config=None):
        super().__init__(config)

    def generate_signals(self, market_data: dict, portfolio_state: dict) -> list:
        signals = []
        # market_data is expected dict[symbol] -> DataFrame
        for symbol, df in market_data.items():
            # stub: if we have no data, continue
            if df is None or df.empty:
                continue
            # naive rule: if close > sma(50) -> buy, if close < sma(200) -> sell
            try:
                close = df["close"].astype(float)
                sma50 = close.rolling(50).mean().iloc[-1]
                sma200 = close.rolling(200).mean().iloc[-1]
                last = close.iloc[-1]
            except Exception:
                continue

            if sma50 and sma200 and last:
                if last > sma50 and sma50 > sma200:
                    signals.append({"symbol": symbol, "side": "buy", "score": 0.8, "size_hint": 0.0})
                elif last < sma50 and sma50 < sma200:
                    signals.append({"symbol": symbol, "side": "sell", "score": 0.6, "size_hint": 0.0})
        return signals
