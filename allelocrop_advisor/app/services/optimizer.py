from typing import List, Dict
import numpy as np
import optuna
from pydantic import BaseModel

from ..ml.yield_model import YieldModel
from ..ml.weed_classifier import WeedClassifier
from ..services.akg import AllelopathyKG

class PlanOptimizer:
    def __init__(self) -> None:
        self.yield_model = YieldModel()
        self.weed_clf = WeedClassifier()
        self.akg = AllelopathyKG()

    def _objective(self, trial: optuna.trial.Trial, payload: Dict, cover: str):
        N = trial.suggest_float("N_rate", 0, 200)
        P = trial.suggest_float("P_rate", 0, 120)
        K = trial.suggest_float("K_rate", 0, 160)
        plan_payload = {**payload, "N_rate": N, "P_rate": P, "K_rate": K}
        y_mean, y_low, y_high = self.yield_model.predict_with_interval(plan_payload)
        # costs (toy): N=0.8, P=1.2, K=0.6 per kg
        cost = 0.8*N + 1.2*P + 0.6*K
        # weed risk: negative of inhibition from cover against observed weeds
        weeds = payload.get("observed_weeds", [])
        inhibition = sum(self.akg.inhibition_score(cover, w) for w in weeds)
        weed_risk = max(0.0, 1.0 - 0.1*inhibition)
        utility = y_mean - 0.05*cost - 5.0*weed_risk
        return -utility, {
            "N_rate": N, "P_rate": P, "K_rate": K,
            "expected_yield": y_mean, "expected_yield_p10": y_low, "expected_yield_p90": y_high,
            "cost": cost, "weed_risk": weed_risk
        }

    def optimize(self, inp: BaseModel) -> List[Dict]:
        payload = inp.model_dump() if hasattr(inp, 'model_dump') else inp
        covers = payload.get("candidate_covers") or self.akg.all_covers()
        all_plans: List[Dict] = []
        for cover in covers:
            def obj(trial):
                loss, metrics = self._objective(trial, payload, cover)
                return loss
            study = optuna.create_study(direction="minimize")
            study.optimize(obj, n_trials=25, show_progress_bar=False)
            best_trial = study.best_trial
            # recompute metrics for best params
            _, metrics = self._objective(best_trial, payload, cover)
            plan = {
                "cover_crop": cover,
                **{k: float(best_trial.params.get(k, metrics[k])) for k in ["N_rate","P_rate","K_rate"]},
                **{k: float(metrics[k]) for k in ["expected_yield","expected_yield_p10","expected_yield_p90","cost","weed_risk"]},
                "score": float(-best_trial.value),
                "timeline": [
                    {"day": "planting", "action": f"Apply {metrics['N_rate']:.0f}-{metrics['P_rate']:.0f}-{metrics['K_rate']:.0f} kg/acre"}
                ]
            }
            all_plans.append(plan)
        # select top-5 by score; treat as Pareto set proxy
        all_plans.sort(key=lambda p: p["score"], reverse=True)
        return all_plans[:5]
