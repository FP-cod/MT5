import sys
import time
import MetaTrader5 as mt5
import config
from execution import executer_ordre
from features import calculer_features, recuperer_donnees
from model import TradingModelIA
from datetime import datetime, timezone


def initialiser_mt5():
    """Initialise et connecte le terminal MT5."""
    if not mt5.initialize():
        print("Erreur : Connexion à MT5 impossible.")
        sys.exit(1)

    if config.MT5_ACCOUNT != 0:
        connecte = mt5.login(
            config.MT5_ACCOUNT, password=config.MT5_PASSWORD, server=config.MT5_SERVER
        )
        if not connecte:
            print(f"Erreur d'authentification MT5 : {mt5.last_error()}")
            sys.exit(1)

    print(f"Connecté à MT5 - Compte #{config.MT5_ACCOUNT}")


def verifier_positions_ouvertes(symbol: str) -> int:
    """Retourne le nombre de positions ouvertes sur le symbole spécifié."""
    positions = mt5.positions_get(symbol=symbol)
    return len(positions) if positions is not None else 0


def attendre_prochaine_bougie(df, timeframe_seconds: int, buffer: int = 2):
    """Calcule le temps restant jusqu'à la prochaine bougie et dort ce temps (+buffer)."""
    last_time = df["time"].iloc[-1]
    if isinstance(last_time, (int, float)):
        last_time = datetime.fromtimestamp(int(last_time), timezone.utc)
    now = datetime.now(timezone.utc)
    elapsed = (now - last_time).total_seconds()
    wait = max(0, timeframe_seconds - elapsed) + buffer
    wait = max(1, int(wait))
    time.sleep(wait)


# Map simple des timeframe MT5 vers secondes
TIMEFRAME_SECONDS = {
    mt5.TIMEFRAME_M1: 60,
    mt5.TIMEFRAME_M5: 5 * 60,
    mt5.TIMEFRAME_M15: 15 * 60,
    mt5.TIMEFRAME_M30: 30 * 60,
    mt5.TIMEFRAME_H1: 60 * 60,
    mt5.TIMEFRAME_D1: 24 * 60 * 60,
}


def boucle_principale():
    initialiser_mt5()
    ia = TradingModelIA()

    print(f"Agent IA démarré sur {config.SYMBOL} (Risque: {config.RISK_PCT}%)")

    try:
        while True:
            nb_positions = verifier_positions_ouvertes(config.SYMBOL)
            if nb_positions > 0:
                df_brut = recuperer_donnees(config.SYMBOL, config.TIMEFRAME, nb_bougies=2)
                tf_sec = TIMEFRAME_SECONDS.get(config.TIMEFRAME, 300)
                attendre_prochaine_bougie(df_brut, tf_sec)
                continue

            df_brut = recuperer_donnees(config.SYMBOL, config.TIMEFRAME, nb_bougies=300)
            df_features = calculer_features(df_brut)
            derniere_bougie = df_features.iloc[-1]

            atr_actuel = derniere_bougie["atr_14_pips"]
            if atr_actuel > config.MAX_ATR_PIPS:
                print(
                    f"Volatilité trop élevée (ATR: {atr_actuel:.1f} pips > {config.MAX_ATR_PIPS} pips). Attente..."
                )
                tf_sec = TIMEFRAME_SECONDS.get(config.TIMEFRAME, 300)
                time.sleep(tf_sec * 5)
                continue

            signal, probabilite = ia.predire_signal(derniere_bougie)

            if signal != 0 and probabilite >= config.PROBA_THRESHOLD:
                dir_str = "ACHAT" if signal == 1 else "VENTE"
                print(f"Signal détecté : {dir_str} (Confiance: {probabilite * 100:.1f}%)")

                account_info = mt5.account_info()
                capital = account_info.balance if account_info else config.CAPITAL

                executer_ordre(
                    symbol=config.SYMBOL,
                    signal=signal,
                    capital=capital,
                    pct_risque=config.RISK_PCT,
                    sl_pips=config.SL_PIPS,
                    tp_pips=config.TP_PIPS,
                )

            tf_sec = TIMEFRAME_SECONDS.get(config.TIMEFRAME, 300)
            attendre_prochaine_bougie(df_brut, tf_sec)

    except KeyboardInterrupt:
        print("\nArrêt de l'agent IA par l'utilisateur.")
    finally:
        mt5.shutdown()


if __name__ == "__main__":
    boucle_principale()
