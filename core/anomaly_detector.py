import numpy as np
from sklearn.ensemble import IsolationForest
from config.logging_config import get_logger

logger = get_logger("AnomalyDetector")

class AnomalyDetector:
    def __init__(self, contamination: float = 0.1):
        self.model = IsolationForest(
            contamination=contamination,
            random_state=42,
            n_estimators=100
        )
        self.fitted = False

    def fit(self, metrics: list):
        vectors = self._vectorize(metrics)
        if len(vectors) < 5:
            logger.warning("Not enough data to train")
            return
        self.model.fit(vectors)
        self.fitted = True
        logger.info(f"Trained on {len(vectors)} samples")

    def detect(self, metrics: list) -> list:
        if not self.fitted:
            self.fit(metrics)
        vectors   = self._vectorize(metrics)
        preds     = self.model.predict(vectors)
        scores    = self.model.score_samples(vectors)
        anomalies = []
        for i, pred in enumerate(preds):
            if pred == -1:
                anomalies.append({
                    **metrics[i],
                    "anomaly_score": round(float(scores[i]), 4),
                    "is_anomaly": True
                })
        logger.info(f"Detected {len(anomalies)} anomalies out of {len(metrics)} samples")
        return anomalies

    def _vectorize(self, metrics: list) -> np.ndarray:
        keys = ["cpu", "memory", "error_rate", "latency", "request_count"]
        return np.array([[float(m.get(k, 0)) for k in keys] for m in metrics])
