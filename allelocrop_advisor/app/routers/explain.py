from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List

from ..ml.yield_model import YieldModel
from ..services.akg import AllelopathyKG

yield_model = YieldModel()
akg = AllelopathyKG()

class ExplainInput(BaseModel):
    payload: Dict

class SHAPItem(BaseModel):
    feature: str
    value: float
    contribution: float

class RuleCard(BaseModel):
    source: str
    relation: str
    target: str
    weight: float
    evidence: str
    persistence_days: int

class ExplainOutput(BaseModel):
    shap_top: List[SHAPItem]
    akg_rules: List[RuleCard]
    why_text: str

router = APIRouter(prefix="/explain", tags=["explain"])

@router.post("/", response_model=ExplainOutput)
def explain(inp: ExplainInput):
    try:
        shap_top = yield_model.explain(inp.payload)
        akg_rules = akg.rule_cards_for_context(inp.payload.get("main_crop", ""), inp.payload.get("observed_weeds", []))
        why = yield_model.generate_why_text(inp.payload, shap_top, akg_rules)
        return ExplainOutput(shap_top=shap_top, akg_rules=akg_rules, why_text=why)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
