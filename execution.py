import MetaTrader5 as mt5


def calculer_taille_lot(
    capital: float,
    pct_risque: float,
    sl_pips: float,
    valeur_pip_par_microlot: float = 0.09,
) -> float:
    """Calcule la taille de position en micro-lots (0.01 = 1000 unités)."""
    montant_risque = capital * (pct_risque / 100.0)
    perte_par_microlot = sl_pips * valeur_pip_par_microlot
    microlots = montant_risque / perte_par_microlot

    # Arrondi au micro-lot le plus proche (minimum 0.01 lot)
    taille_finale = max(0.01, round(microlots, 2))
    return taille_finale


def executer_ordre(
    symbol: str, signal: int, capital: float, pct_risque: float, sl_pips: float, tp_pips: float
) -> bool:
    """Envoie un ordre au marché sur MT5 avec Stop-Loss et Take-Profit intégrés."""
    tick = mt5.symbol_info_tick(symbol)
    symbol_info = mt5.symbol_info(symbol)

    if tick is None or symbol_info is None:
        print(f"Erreur : Impossible d'obtenir les prix du symbole {symbol}")
        return False

    point = symbol_info.point  # 0.00001 pour EURUSD
    taille_lot = calculer_taille_lot(capital, pct_risque, sl_pips)

    if signal == 1:  # ACHAT
        price = tick.ask
        sl = price - (sl_pips * 10 * point)
        tp = price + (tp_pips * 10 * point)
        order_type = mt5.ORDER_TYPE_BUY
    elif signal == -1:  # VENTE
        price = tick.bid
        sl = price + (sl_pips * 10 * point)
        tp = price - (tp_pips * 10 * point)
        order_type = mt5.ORDER_TYPE_SELL
    else:
        return False

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": taille_lot,
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

    result = mt5.order_send(request)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"Échec de l'ordre : {result.comment} (Code: {result.retcode})")
        return False

    print(f"Ordre exécuté avec succès ! Ticket #{result.order} | Lots: {taille_lot}")
    return True
