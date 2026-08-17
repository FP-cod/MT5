"""Backtest simple bar-by-bar reproduisant la logique de l'agent.

Usage:
    python tools/backtest.py --symbol EURUSD --nb_bars 1000 --start_balance 1000

Ce backtest simule SL/TP sur les bougies suivantes et calcule des métriques.
"""
import argparse
import pandas as pd
import numpy as np
from features import recuperer_donnees, calculer_features
from model import TradingModelIA
from execution import calculer_taille_lot
import config
from tools.metrics import compute_metrics


def simulate(symbol, timeframe, nb_bars=1000, start_balance=None, max_holding_bars=50, spread_pips=0.0):
    if start_balance is None:
        start_balance = config.CAPITAL
    ia = TradingModelIA()
    df = recuperer_donnees(symbol, timeframe, nb_bougies=nb_bars)
    df = calculer_features(df)

    balance = start_balance
    equity_curve = [balance]
    trades = []

    pip = 0.0001 if "JPY" not in symbol else 0.01

    for i in range(len(df) - 1):
        row = df.iloc[i]
        signal, proba = ia.predire_signal(row)
        if signal == 0 or proba < config.PROBA_THRESHOLD:
            equity_curve.append(balance)
            continue

        entry_price = row["close"] + (spread_pips * pip if signal == 1 else -spread_pips * pip)
        sl_price = entry_price - signal * config.SL_PIPS * pip * 1
        tp_price = entry_price + signal * config.TP_PIPS * pip * 1

        exit_price = entry_price
        exit_idx = i
        pnl = 0.0
        hit = None

        for j in range(i + 1, min(i + 1 + max_holding_bars, len(df))):
            high = df.iloc[j]["high"]
            low = df.iloc[j]["low"]
            if signal == 1:
                if low <= sl_price:
                    exit_price = sl_price
                    exit_idx = j
                    hit = "SL"
                    break
                if high >= tp_price:
                    exit_price = tp_price
                    exit_idx = j
                    hit = "TP"
                    break
            else:
                if high >= sl_price:
                    exit_price = sl_price
                    exit_idx = j
                    hit = "SL"
                    break
                if low <= tp_price:
                    exit_price = tp_price
                    exit_idx = j
                    hit = "TP"
                    break

        # calculer lot basé sur balance
        lot = calculer_taille_lot(balance, config.RISK_PCT, config.SL_PIPS)
        pips = (exit_price - entry_price) / pip * (1 if signal == 1 else -1)
        pnl = pips * config.PIP_VALUE_PER_LOT * (lot / 1.0)
        balance += pnl

        trades.append({
            "entry_idx": i,
            "exit_idx": exit_idx,
            "entry": entry_price,
            "exit": exit_price,
            "pnl": pnl,
            "pips": pips,
            "signal": signal,
            "proba": proba,
            "hit": hit,
        })
        equity_curve.append(balance)

    metrics = compute_metrics(trades, equity_curve, start_balance)
    return trades, equity_curve, metrics


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbol", default=config.SYMBOL)
    parser.add_argument("--nb_bars", type=int, default=1000)
    parser.add_argument("--start_balance", type=float, default=config.CAPITAL)
    args = parser.parse_args()

    trades, equity, metrics = simulate(args.symbol, config.TIMEFRAME, nb_bars=args.nb_bars, start_balance=args.start_balance)
    print("Metrics:\n", metrics)
    # sauvegarder
    pd.DataFrame(trades).to_csv("backtest_trades.csv", index=False)
    pd.DataFrame({"equity": equity}).to_csv("backtest_equity.csv", index=False)


if __name__ == "__main__":
    main()
