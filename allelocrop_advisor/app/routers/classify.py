from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List

from ..ml.weed_classifier import WeedClassifier

weed_clf = WeedClassifier()

class WeedInput(BaseModel):
    weeds: List[str]
    region: str
    season: str
    main_crop: str

class WeedOutput(BaseModel):
    labels: List[str]
    probabilities: List[float]

router = APIRouter(prefix="/classify", tags=["classify"])

@router.post("/weed", response_model=WeedOutput)
def classify_weed(inp: WeedInput):
    try:
        labels, probs = weed_clf.classify(inp)
        return WeedOutput(labels=labels, probabilities=probs)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
