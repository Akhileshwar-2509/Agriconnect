from typing import List, Dict
import numpy as np
from pydantic import BaseModel

from ..services.akg import AllelopathyKG

akg = AllelopathyKG()

class CoverCropRecommender:
    def __init__(self) -> None:
        self.akg = akg

    def _compute_features(self, main_crop: str, weeds: List[str], cover: str) -> Dict[str, float]:
        inhibition = 0.0
        for w in weeds:
            inhibition += self.akg.inhibition_score(cover, w)
        persistence = self.akg.persistence_days(cover)
        return {
            "akg_inhibition": inhibition,
            "akg_persistence": float(persistence),
        }

    def recommend(self, inp: BaseModel):
        payload = inp.model_dump() if hasattr(inp, 'model_dump') else inp
        main_crop = payload.get("main_crop")
        weeds = payload.get("observed_weeds", [])
        covers = self.akg.all_covers()
        recs = []
        for c in covers:
            feats = self._compute_features(main_crop, weeds, c)
            score = 0.7*feats["akg_inhibition"] + 0.3*np.tanh(feats["akg_persistence"]/60.0)
            recs.append({
                "cover_crop": c,
                "score": float(score),
                "akg_score": float(feats["akg_inhibition"]),
                "features": feats
            })
        recs.sort(key=lambda r: r["score"], reverse=True)
        return recs[:5]
