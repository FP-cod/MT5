import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Target Python version: 3.11+

# MT5 / trading configuration
MT5_ACCOUNT = int(os.getenv("MT5_ACCOUNT") or 0)
MT5_PASSWORD = os.getenv("MT5_PASSWORD")
MT5_SERVER = os.getenv("MT5_SERVER")

# Allocation config path
ALLOCATIONS_PATH = Path(os.getenv("ALLOCATIONS_PATH") or "allocations.yaml")

# Execution / order defaults
DRY_RUN = os.getenv("DRY_RUN", "true").lower() in ("1", "true", "yes")
SLIPPAGE_PCT = float(os.getenv("SLIPPAGE_PCT", "0.001"))
MAX_LEVERAGE = float(os.getenv("MAX_LEVERAGE", "2.0"))

# Risk defaults
MAX_EXPOSURE_PER_SYMBOL_PCT = float(os.getenv("MAX_EXPOSURE_PER_SYMBOL_PCT", "0.25"))
MAX_PORTFOLIO_DRAWDOWN_PCT = float(os.getenv("MAX_PORTFOLIO_DRAWDOWN_PCT", "0.2"))

# Rebalance cadence
REBALANCE_CADENCE = os.getenv("REBALANCE_CADENCE", "daily")  # or 'hourly'
REBALANCE_THRESHOLD_PCT = float(os.getenv("REBALANCE_THRESHOLD_PCT", "0.025"))

# Symbols defaults (can be overridden by allocations file)
DEFAULT_SYMBOLS = {
    "indices": ["SPX500", "NAS100", "DAX30"],
    "crypto": ["BTCUSD", "ETHUSD"],
    "large_caps": ["AAPL", "MSFT", "GOOGL"],
    "forex": ["EURUSD"]
}
