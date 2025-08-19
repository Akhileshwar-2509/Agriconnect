from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel
from typing import List, Dict
from ..services.pdf_export import PDFService
import csv
import io

pdf_service = PDFService()

class ExportPlan(BaseModel):
    cover_crop: str
    N_rate: float
    P_rate: float
    K_rate: float
    expected_yield: float
    expected_yield_p10: float
    expected_yield_p90: float
    cost: float
    weed_risk: float
    timeline: List[Dict[str, str]]

class ExportInput(BaseModel):
    scenario_name: str
    inputs: Dict
    plans: List[ExportPlan]

router = APIRouter(prefix="/export", tags=["export"])

@router.post("/pdf")
def export_pdf(inp: ExportInput):
    try:
        data = pdf_service.build_pdf(inp)
        headers = {"Content-Disposition": f"attachment; filename={inp.scenario_name}.pdf"}
        return Response(content=data, media_type="application/pdf", headers=headers)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/csv")
def export_csv(inp: ExportInput):
    try:
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(["cover_crop","N_rate","P_rate","K_rate","expected_yield","expected_yield_p10","expected_yield_p90","cost","weed_risk"])
        for p in inp.plans[:5]:
            writer.writerow([
                p.cover_crop, f"{p.N_rate:.2f}", f"{p.P_rate:.2f}", f"{p.K_rate:.2f}",
                f"{p.expected_yield:.2f}", f"{p.expected_yield_p10:.2f}", f"{p.expected_yield_p90:.2f}",
                f"{p.cost:.2f}", f"{p.weed_risk:.2f}"
            ])
        data = buf.getvalue().encode("utf-8")
        headers = {"Content-Disposition": f"attachment; filename={inp.scenario_name}.csv"}
        return Response(content=data, media_type="text/csv", headers=headers)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
