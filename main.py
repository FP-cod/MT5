import sys
import time
import MetaTrader5 as mt5
import config
from execution import executer_ordre
from features import calculer_features, recuperer_donnees
from model import TradingModelIA


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


def boucle_principale():
    initialiser_mt5()
    ia = TradingModelIA()

    print(f"Agent IA démarré sur {config.SYMBOL} (Risque: {config.RISK_PCT}%)")

    try:
        while True:
            # 1. Vérifier si une position est déjà ouverte (1 position à la fois max)
            nb_positions = verifier_positions_ouvertes(config.SYMBOL)
            if nb_positions > 0:
                time.sleep(60)
                continue

            # 2. Récupérer et préparer les données
            df_brut = recuperer_donnees(config.SYMBOL, config.TIMEFRAME, nb_bougies=300)
            df_features = calculer_features(df_brut)
            derniere_bougie = df_features.iloc[-1]

            # 3. Filtre de sécurité ATR (Volatilité extrême)
            atr_actuel = derniere_bougie["atr_14_pips"]
            if atr_actuel > config.MAX_ATR_PIPS:
                print(
                    f"Volatilité trop élevée (ATR: {atr_actuel:.1f} pips > {config.MAX_ATR_PIPS} pips). Attente..."
                )
                time.sleep(300)
                continue

            # 4. Inférence IA
            signal, probabilite = ia.predire_signal(derniere_bougie)

            # 5. Prise de décision et exécution
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

            # Attendre 5 minutes avant la prochaine vérification
            time.sleep(300)

    except KeyboardInterrupt:
        print("\nArrêt de l'agent IA par l'utilisateur.")
    finally:
        mt5.shutdown()


if __name__ == "__main__":
    boucle_principale()

