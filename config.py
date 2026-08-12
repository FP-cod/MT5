import os
import MetaTrader5 as mt5
from dotenv import load_dotenv

load_dotenv()

# Paramètres de connexion MT5
MT5_ACCOUNT = int(os.getenv("MT5_ACCOUNT", 0))
MT5_PASSWORD = os.getenv("MT5_PASSWORD", "")
MT5_SERVER = os.getenv("MT5_SERVER", "OANDA-Demo")

# Paramètres de stratégie et gestion du risque
SYMBOL = os.getenv("SYMBOL", "EURUSD")
CAPITAL = float(os.getenv("CAPITAL", 250.0))
RISK_PCT = float(os.getenv("RISK_PCT", 4.0))  # 4% = 10€
SL_PIPS = float(os.getenv("SL_PIPS", 35.0))
TP_PIPS = float(os.getenv("TP_PIPS", 52.0))
MAX_ATR_PIPS = float(os.getenv("MAX_ATR_PIPS", 28.0))
PROBA_THRESHOLD = float(os.getenv("PROBA_THRESHOLD", 0.65))

# Unité de temps (H1 par défaut)
TIMEFRAME = mt5.TIMEFRAME_H1
