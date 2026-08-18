try:
    import MetaTrader5 as mt5
except ModuleNotFoundError:  # pragma: no cover - local dry-run fallback
    import sim_mt5 as mt5

import numpy as np
import pandas as pd
import ta


def recuperer_donnees(symbol: str, timeframe: int, nb_bougies: int = 500) -> pd.DataFrame:
    """Récupère les bougies historiques depuis MT5 et retourne un DataFrame."""
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, nb_bougies)
    if rates is None or len(rates) == 0:
        raise ValueError(f"Impossible de récupérer les données pour {symbol}")

    df = pd.DataFrame(rates)
    df["time"] = pd.to_datetime(df["time"], unit="s")
    for col in ("open", "high", "low", "close", "tick_volume"):
        if col in df:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def calculer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Calcule les indicateurs techniques servant d'entrées (features) au modèle IA."""
    df = df.copy()

    # 1. Moyennes Mobiles Exponentielles
    df["ema_50"] = ta.trend.ema_indicator(df["close"], window=50)
    df["ema_200"] = ta.trend.ema_indicator(df["close"], window=200)
    df["dist_ema50_pips"] = (df["close"] - df["ema_50"]) * 10000

    # 2. Volatilité (ATR en pips)
    df["atr_14_pips"] = (
        ta.volatility.average_true_range(df["high"], df["low"], df["close"], window=14) * 10000
    )

    # 3. Momentum
    df["rsi_14"] = ta.momentum.rsi(df["close"], window=14)
    df["macd_diff"] = ta.trend.macd_diff(df["close"])

    # Nettoyage des valeurs manquantes causées par les indicateurs
    df.dropna(inplace=True)
    cols = [
        "time",
        "open",
        "high",
        "low",
        "close",
        "ema_50",
        "ema_200",
        "dist_ema50_pips",
        "atr_14_pips",
        "rsi_14",
        "macd_diff",
    ]
    return df[cols].reset_index(drop=True)
