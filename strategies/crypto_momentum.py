from .base import Strategy

class CryptoMomentumStrategy(Strategy):
    """Momentum/volatility-based signals for BTC/ETH.
    Skeleton implementation: uses returns and volatility to size ideas.
    """

    def generate_signals(self, market_data: dict, portfolio_state: dict) -> list:
        signals = []
        for symbol, df in market_data.items():
            if df is None or df.empty:
                continue
            try:
                close = df["close"].astype(float)
                returns = close.pct_change().dropna()
                vol = returns.rolling(24).std().iloc[-1]
                mom = (close.iloc[-1] / close.iloc[-21] - 1) if len(close) > 21 else 0
            except Exception:
                continue
            if mom and mom > 0.02:
                signals.append({"symbol": symbol, "side": "buy", "score": float(mom), "size_hint": float(min(0.4, 1.0/(vol*100+1)))})
            elif mom and mom < -0.02:
                signals.append({"symbol": symbol, "side": "sell", "score": float(-mom), "size_hint": float(min(0.4, 1.0/(vol*100+1)))})
        return signals
