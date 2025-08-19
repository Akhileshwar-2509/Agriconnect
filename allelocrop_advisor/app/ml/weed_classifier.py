from typing import List, Tuple
import numpy as np
from pydantic import BaseModel

class WeedInputPyd(BaseModel):
    weeds: List[str]
    region: str
    season: str
    main_crop: str

class WeedClassifier:
    def __init__(self) -> None:
        self.labels_space = ["harmful", "neutral", "beneficial"]

    def classify(self, inp: BaseModel) -> Tuple[List[str], List[float]]:
        payload = inp.model_dump() if hasattr(inp, 'model_dump') else inp
        weeds = payload.get("weeds", [])
        rng = np.random.RandomState(len(weeds) + len(payload.get("region", "")))
        # Stub: random but deterministic probabilities
        probs = rng.dirichlet(alpha=[1.5, 1.0, 0.8]).tolist()
        # Same label for all weeds here; in real model, per-weed scores would be given
        labels = [self.labels_space[int(np.argmax(probs))] for _ in weeds]
        return labels, probs
