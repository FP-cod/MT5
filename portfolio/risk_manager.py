
class RiskManager:
    def __init__(self, max_exposure_per_symbol_pct: float = 0.25):
        self.max_exposure_per_symbol_pct = max_exposure_per_symbol_pct

    def enforce_limits(self, proposed_targets: dict, account_capital: float) -> dict:
        """Cap each symbol target to max_exposure_per_symbol_pct * account_capital
        proposed_targets: symbol -> target_cash
        returns adjusted dict
        """
        adjusted = {}
        cap = account_capital * self.max_exposure_per_symbol_pct
        for sym, cash in proposed_targets.items():
            adjusted[sym] = min(cash, cap)
        return adjusted
