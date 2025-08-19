from typing import List, Dict
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

class PDFService:
    def build_pdf(self, inp) -> bytes:
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter
        y = height - 50
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y, f"AlleloCrop Advisor - {inp.scenario_name}")
        y -= 20
        c.setFont("Helvetica", 10)
        c.drawString(50, y, "Inputs:")
        y -= 15
        for k, v in (inp.inputs or {}).items():
            c.drawString(60, y, f"{k}: {v}")
            y -= 12
        y -= 5
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, "Plans (Top-5):")
        y -= 18
        for i, p in enumerate(inp.plans[:5]):
            if y < 120:
                c.showPage()
                y = height - 50
            c.setFont("Helvetica-Bold", 11)
            c.drawString(50, y, f"{i+1}. Cover: {p.cover_crop}, Yield: {p.expected_yield:.1f} (P10={p.expected_yield_p10:.1f}, P90={p.expected_yield_p90:.1f})")
            y -= 14
            c.setFont("Helvetica", 10)
            c.drawString(60, y, f"N-P-K: {p.N_rate:.0f}-{p.P_rate:.0f}-{p.K_rate:.0f} kg/acre | Cost: ${p.cost:.1f} | Weed risk: {p.weed_risk:.2f}")
            y -= 14
            for step in p.timeline:
                c.drawString(70, y, f"- {step.get('day')}: {step.get('action')}")
                y -= 12
            y -= 6
        c.showPage()
        c.save()
        pdf = buffer.getvalue()
        buffer.close()
        return pdf
