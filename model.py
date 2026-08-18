import os
import numpy as np
import pandas as pd

try:
    from xgboost import XGBClassifier
except ModuleNotFoundError:  # pragma: no cover - local dry-run fallback
    class XGBClassifier:
        def __init__(self, *args, **kwargs):
            self.classes_ = np.array([-1, 0, 1])

        def load_model(self, *args, **kwargs):
            return None

        def predict(self, X):
            n = len(X)
            return np.zeros(n, dtype=int)

        def predict_proba(self, X):
            n = len(X)
            return np.tile([0.34, 0.33, 0.33], (n, 1))


class TradingModelIA:

    def __init__(self, model_path: str = "models/xgboost_forex.json"):
        self.model_path = model_path
        self.model = XGBClassifier(use_label_encoder=False, eval_metric="logloss")
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
            ema_trend = 1 if derniere_bougie["close"] > derniere_bougie["ema_200"] else -1
            rsi = derniere_bougie["rsi_14"]

            if ema_trend == 1 and rsi < 45:
                return 1, 0.70
            elif ema_trend == -1 and rsi > 55:
                return -1, 0.70
            return 0, 0.50

        X = pd.DataFrame([derniere_bougie[self.features_cols]]).astype(float)
        probas = self.model.predict_proba(X)[0]
        pred = self.model.predict(X)[0]
        classes = list(self.model.classes_)
        try:
            prob_max = float(probas[classes.index(pred)])
        except ValueError:
            prob_max = float(np.max(probas))

        if set(classes) >= {-1, 0, 1}:
            signal = int(pred)
        else:
            map_by_index = {0: -1, 1: 0, 2: 1}
            idx = int(np.argmax(probas))
            signal = map_by_index.get(idx, 0)

        return signal, prob_max
