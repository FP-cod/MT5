import os
import numpy as np
import pandas as pd
from xgboost import XGBClassifier


class TradingModelIA:

    def __init__(self, model_path: str = "models/xgboost_forex.json"):
        self.model_path = model_path
        self.model = XGBClassifier()
        self.features_cols = ["dist_ema50_pips", "atr_14_pips", "rsi_14", "macd_diff"]

        if os.path.exists(self.model_path):
            self.model.load_model(self.model_path)
            self.is_trained = True
        else:
            self.is_trained = False

    def predire_signal(self, derniere_bougie: pd.Series) -> tuple[int, float]:
        """
        Prédit la direction du marché.
        Retourne : (signal, probabilite)
        signal : 1 (Achat), -1 (Vente), 0 (Neutre)
        """
        if not self.is_trained:
            # Règle heuristique de repli si aucun modèle entraîné n'est présent
            ema_trend = 1 if derniere_bougie["close"] > derniere_bougie["ema_200"] else -1
            rsi = derniere_bougie["rsi_14"]

            if ema_trend == 1 and rsi < 45:
                return 1, 0.70  # Achat sur pullback
            elif ema_trend == -1 and rsi > 55:
                return -1, 0.70  # Vente sur pullback
            return 0, 0.50

        # Préparation des features pour XGBoost
        X = pd.DataFrame([derniere_bougie[self.features_cols]])
        probas = self.model.predict_proba(X)[0]
        prediction = int(np.argmax(probas))
        prob_max = float(probas[prediction])

        # Mapping : 0 = Vente, 1 = Neutre, 2 = Achat
        signal_map = {0: -1, 1: 0, 2: 1}
        return signal_map.get(prediction, 0), prob_max
