from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict

from ..ml.yield_model import YieldModel

yield_model = YieldModel()

class YieldInput(BaseModel):
    soil_N: float = Field(..., description="kg/acre")
    soil_P: float
    soil_K: float
    pH: float
    OM: float
    EC: float
    texture: str
    region: str
    season: str
    main_crop: str
    weather_30d: Dict[str, float]
    weather_60d: Dict[str, float]
    N_rate: float
    P_rate: float
    K_rate: float

class YieldOutput(BaseModel):
    yield_mean: float
    yield_p10: float
    yield_p90: float

router = APIRouter(prefix="/predict", tags=["predict"])

@router.post("/yield", response_model=YieldOutput)
def predict_yield(inp: YieldInput):
    try:
        y_mean, y_low, y_high = yield_model.predict_with_interval(inp)
        return YieldOutput(yield_mean=y_mean, yield_p10=y_low, yield_p90=y_high)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
