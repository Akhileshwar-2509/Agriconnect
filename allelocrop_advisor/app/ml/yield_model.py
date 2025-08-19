from typing import Dict, List, Tuple
import numpy as np
from pydantic import BaseModel
from sklearn.ensemble import GradientBoostingRegressor

try:
    import shap  # type: ignore
except Exception:  # pragma: no cover
    shap = None  # fallback

class YieldModel:
    def __init__(self) -> None:
        # Train very small toy models to enable runtime predictions
        self.feature_names = [
            "soil_N","soil_P","soil_K","pH","OM","EC","N_rate","P_rate","K_rate",
            "weather_30d_rain","weather_30d_gdd","weather_60d_rain","weather_60d_gdd"
        ]
        rng = np.random.RandomState(42)
        X = rng.uniform(low=0.0, high=1.0, size=(256, len(self.feature_names)))
        # synthetic yield: base + nutrient response + moisture term
        y = 80 + 60*X[:,6] + 25*X[:,7] + 20*X[:,8] + 10*X[:,1] - 5*(X[:,3]-0.6)**2 + 8*X[:,10] + rng.normal(0, 5, size=256)
        self.model_mean = GradientBoostingRegressor(random_state=42)
        self.model_p10 = GradientBoostingRegressor(loss='quantile', alpha=0.10, random_state=42)
        self.model_p90 = GradientBoostingRegressor(loss='quantile', alpha=0.90, random_state=42)
        self.model_mean.fit(X, y)
        self.model_p10.fit(X, y)
        self.model_p90.fit(X, y)

    def _vectorize(self, payload: Dict) -> np.ndarray:
        w30 = payload.get("weather_30d", {})
        w60 = payload.get("weather_60d", {})
        feats = [
            payload.get("soil_N", 0.0), payload.get("soil_P", 0.0), payload.get("soil_K", 0.0),
            payload.get("pH", 6.5), payload.get("OM", 2.0), payload.get("EC", 0.2),
            payload.get("N_rate", 0.0), payload.get("P_rate", 0.0), payload.get("K_rate", 0.0),
            w30.get("rain", 0.0), w30.get("gdd", 0.0), w60.get("rain", 0.0), w60.get("gdd", 0.0)
        ]
        return np.array(feats, dtype=float).reshape(1, -1)

    def predict_with_interval(self, payload_or_model: BaseModel) -> Tuple[float, float, float]:
        payload = payload_or_model.model_dump() if hasattr(payload_or_model, 'model_dump') else payload_or_model
        X = self._vectorize(payload)
        y_mean = float(self.model_mean.predict(X)[0])
        y_low = float(self.model_p10.predict(X)[0])
        y_high = float(self.model_p90.predict(X)[0])
        return y_mean, y_low, y_high

    def explain(self, payload: Dict) -> List[Dict]:
        X = self._vectorize(payload)
        if shap is not None:
            try:
                explainer = shap.TreeExplainer(self.model_mean)
                vals = explainer.shap_values(X)
                contribs = vals[0]
            except Exception:
                contribs = (X[0] - X.mean())  # fallback heuristic
        else:
            contribs = (X[0] - X.mean())
        items = []
        for i, name in enumerate(self.feature_names):
            items.append({
                "feature": name,
                "value": float(X[0, i]),
                "contribution": float(contribs[i])
            })
        # return top-8 by absolute contribution
        items.sort(key=lambda d: abs(d["contribution"]), reverse=True)
        return items[:8]

    def generate_why_text(self, payload: Dict, shap_top: List[Dict], akg_rules: List[Dict]) -> str:
        parts = []
        if shap_top:
            topf = shap_top[0]
            parts.append(f"Yield is driven mostly by {topf['feature']} (contribution {topf['contribution']:.2f}).")
        if akg_rules:
            r = akg_rules[0]
            parts.append(f"Allelopathic interaction: {r['source']} {r['relation']} {r['target']} (weight {r['weight']}).")
        parts.append("N-P-K rates are adjusted to balance nutrient response and cost under recent weather.")
        return " ".join(parts)
