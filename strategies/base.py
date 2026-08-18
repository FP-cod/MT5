class Strategy:
    """Base strategy interface.
    Strategies must implement generate_signals(market_data, portfolio_state) -> list[signal]
    Signal format: {"symbol": str, "side": "buy"|"sell", "score": float, "size_hint": float}
    """
    def __init__(self, config: dict | None = None):
        self.config = config or {}

    def required_indicators(self) -> list:
        return []

    def on_start(self, context: dict):
        pass

    def generate_signals(self, market_data: dict, portfolio_state: dict) -> list:
        raise NotImplementedError

    def on_fill(self, fill: dict):
        pass
