from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict

from ..ml.recommender import CoverCropRecommender

recommender = CoverCropRecommender()

class RecommendInput(BaseModel):
    main_crop: str
    observed_weeds: List[str]
    region: str
    season: str

class CoverRec(BaseModel):
    cover_crop: str
    score: float
    akg_score: float
    features: Dict[str, float]

class RecommendOutput(BaseModel):
    recommendations: List[CoverRec]

router = APIRouter(prefix="/recommend", tags=["recommend"])

@router.post("/cover", response_model=RecommendOutput)
def recommend_cover(inp: RecommendInput):
    try:
        recs = recommender.recommend(inp)
        return RecommendOutput(recommendations=recs)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
