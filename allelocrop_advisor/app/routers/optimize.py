from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional

from ..services.optimizer import PlanOptimizer

optimizer = PlanOptimizer()

class OptimizeInput(BaseModel):
    soil_N: float
    soil_P: float
    soil_K: float
    pH: float
    OM: float
    EC: float
    texture: str
    region: str
    season: str
    main_crop: str
    observed_weeds: List[str]
    weather_30d: Dict[str, float]
    weather_60d: Dict[str, float]
    candidate_covers: Optional[List[str]] = None

class Plan(BaseModel):
    cover_crop: str
    N_rate: float
    P_rate: float
    K_rate: float
    expected_yield: float
    expected_yield_p10: float
    expected_yield_p90: float
    cost: float
    weed_risk: float
    score: float
    timeline: List[Dict[str, str]]

class OptimizeOutput(BaseModel):
    pareto: List[Plan]

router = APIRouter(prefix="/optimize", tags=["optimize"])

@router.post("/", response_model=OptimizeOutput)
def optimize_plan(inp: OptimizeInput):
    try:
        plans = optimizer.optimize(inp)
        return OptimizeOutput(pareto=plans)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
