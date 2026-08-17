"""Fonctions utilitaires pour calculer les métriques de performance d'un backtest."""
import math
import numpy as np


def compute_metrics(trades, equity_curve, start_balance):
    pnls = [t["pnl"] for t in trades]
    wins = [p for p in pnls if p > 0]
    losses = [p for p in pnls if p <= 0]
    total_pnl = sum(pnls)
    total_trades = len(pnls)
    win_rate = len(wins) / total_trades if total_trades > 0 else 0.0
    gross_profit = sum(wins) if wins else 0.0
    gross_loss = -sum(losses) if losses else 0.0
    profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else float("inf")
    avg_win = (sum(wins) / len(wins)) if wins else 0.0
    avg_loss = (sum(losses) / len(losses)) if losses else 0.0
    expectancy = (avg_win * win_rate) - (abs(avg_loss) * (1 - win_rate))

    eq = np.array(equity_curve)
    peak = np.maximum.accumulate(eq)
    dd = (eq - peak) / peak
    max_dd = float(dd.min()) if len(dd) > 0 else 0.0

    final_balance = equity_curve[-1] if len(equity_curve) > 0 else start_balance
    total_return = (final_balance / start_balance) - 1

    # Sharpe approximé sur la série d'incréments quotidiens/trades
    returns = np.diff(eq) / eq[:-1] if len(eq) > 1 else np.array([0.0])
    mean_r = float(np.mean(returns)) if returns.size > 0 else 0.0
    std_r = float(np.std(returns)) if returns.size > 0 else 0.0
    sharpe = (mean_r / std_r * math.sqrt(252)) if std_r > 0 else float("inf")

    return {
        "trades": total_trades,
        "total_pnl": total_pnl,
        "total_return": total_return,
        "win_rate": win_rate,
        "profit_factor": profit_factor,
        "expectancy": expectancy,
        "max_drawdown": max_dd,
        "sharpe": sharpe,
    }
