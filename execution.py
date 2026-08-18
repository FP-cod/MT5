import math

try:
    import MetaTrader5 as mt5
except ModuleNotFoundError:  # pragma: no cover - local dry-run fallback
    import sim_mt5 as mt5

import config


def calculer_taille_lot(
    capital: float,
    pct_risque: float,
    sl_pips: float,
    valeur_pip_par_microlot: float = 0.09,
) -> float:
    """Calcule la taille de position en lots (0.01 = 1 micro-lot).

    Retourne un volume en lots (float) brut — doit être arrondi au volume_step du broker.
    """
    if sl_pips <= 0:
        raise ValueError("SL pips doit être > 0")
    montant_risque = capital * (pct_risque / 100.0)
    perte_par_microlot = sl_pips * valeur_pip_par_microlot
    if perte_par_microlot <= 0:
        raise ValueError("Perte par microlot invalide (<=0)")
    # microlots = nombre de micro-lots (1 micro-lot = 0.01 lot)
    microlots = montant_risque / perte_par_microlot
    lots = microlots * 0.01
    return max(0.01, round(lots, 4))


def _round_volume_to_step(volume: float, step: float, min_vol: float, max_vol: float | None) -> float:
    # arrondir vers le bas au multiple de step pour ne pas dépasser le risque
    if step <= 0:
        return max(min_vol, volume)
    n_steps = int(volume / step)
    if n_steps <= 0:
        return min_vol
    v = max(min_vol, n_steps * step)
    if max_vol is not None and v > max_vol:
        return max_vol
    return v


def executer_ordre(
    symbol: str,
    signal: int,
    capital: float,
    pct_risque: float,
    sl_pips: float,
    tp_pips: float,
) -> bool:
    """Envoie un ordre au marché sur MT5 avec Stop-Loss et Take-Profit intégrés.

    Si config.DRY_RUN est True, l'ordre est simulé et rien n'est envoyé à MT5.
    """
    tick = mt5.symbol_info_tick(symbol)
    symbol_info = mt5.symbol_info(symbol)

    if tick is None or symbol_info is None:
        print(f"Erreur : Impossible d'obtenir les prix ou infos du symbole {symbol}")
        return False

    point = getattr(symbol_info, "point", 0.00001)
    digits = getattr(symbol_info, "digits", 5)
    pip = point * (10 if digits > 4 else 1)

    taille_lot_brute = calculer_taille_lot(capital, pct_risque, sl_pips)
    step = getattr(symbol_info, "volume_step", 0.01) or 0.01
    min_vol = getattr(symbol_info, "volume_min", 0.01) or 0.01
    max_vol = getattr(symbol_info, "volume_max", None)

    taille_lot = _round_volume_to_step(taille_lot_brute, step, min_vol, max_vol)

    if signal == 1:  # ACHAT
        price = tick.ask
        sl = price - (sl_pips * pip)
        tp = price + (tp_pips * pip)
        order_type = mt5.ORDER_TYPE_BUY
    elif signal == -1:  # VENTE
        price = tick.bid
        sl = price + (sl_pips * pip)
        tp = price - (tp_pips * pip)
        order_type = mt5.ORDER_TYPE_SELL
    else:
        return False

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": float(round(taille_lot, 2)),
        "type": order_type,
        "price": price,
        "sl": sl,
        "tp": tp,
        "deviation": 20,
        "magic": 202608,
        "comment": "Agent IA Forex",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    if config.DRY_RUN:
        # Simuler l'envoi : enregistrer dans un fichier local pour audit/backtest
        try:
            with open("trades_simulated.csv", "a", encoding="utf-8") as f:
                f.write(
                    ",".join(
                        [
                            symbol,
                            str("BUY" if signal == 1 else "SELL"),
                            str(round(taille_lot, 4)),
                            str(price),
                            str(sl),
                            str(tp),
                        ]
                    )
                    + "\n"
                )
        except Exception as e:
            print(f"Erreur en écrivant le log de simulation: {e}")
        print(f"[DRY_RUN] Ordre simulé : {request}")
        return True

    result = mt5.order_send(request)
    if result is None:
        print("order_send a retourné None")
        return False

    retcode = getattr(result, "retcode", None)
    if retcode != mt5.TRADE_RETCODE_DONE:
        comment = getattr(result, "comment", "No comment")
        print(f"Échec de l'ordre : {comment} (Code: {retcode})")
        return False

    order_id = getattr(result, "order", None)
    print(f"Ordre exécuté avec succès ! Ticket #{order_id} | Lots: {taille_lot}")
    return True
