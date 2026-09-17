import os
from pathlib import Path
from uuid import uuid4
from fpdf import FPDF

from sqlalchemy.orm import Session
from app.models import Prediction, Report
from app.core.config import settings

class ReportService:
    def __init__(self, db: Session):
        self.db = db
        self.report_dir = settings.UPLOAD_DIR / "reports"
        self.report_dir.mkdir(parents=True, exist_ok=True)

    def generate_pdf_report(self, prediction: Prediction) -> Report:
        if prediction.report:
            return prediction.report
            
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=15)
        
        pdf.cell(200, 10, txt="Oral Cancer Detection Report", ln=True, align="C")
        pdf.cell(200, 10, txt=f"Prediction ID: {prediction.prediction_id}", ln=True, align="C")
        
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt=f"Result: {prediction.prediction}", ln=True)
        pdf.cell(200, 10, txt=f"Confidence: {prediction.confidence:.2f}" if prediction.confidence else "Confidence: N/A", ln=True)
        
        if prediction.metadata_json:
            pdf.cell(200, 10, txt=f"Metadata: {prediction.metadata_json}", ln=True)
            
        # Add Original Image
        if prediction.image_path and os.path.exists(prediction.image_path):
            pdf.cell(200, 10, txt="Original Image:", ln=True)
            try:
                pdf.image(prediction.image_path, w=100)
            except Exception as e:
                pdf.cell(200, 10, txt=f"(Image omitted due to format issue: {e})", ln=True)
                
        # Add Heatmap
        if prediction.heatmap_path and os.path.exists(prediction.heatmap_path):
            pdf.cell(200, 10, txt="Grad-CAM Heatmap:", ln=True)
            try:
                pdf.image(prediction.heatmap_path, w=100)
            except Exception as e:
                pdf.cell(200, 10, txt=f"(Heatmap omitted due to format issue: {e})", ln=True)
                
        pdf_filename = f"report_{prediction.prediction_id}_{uuid4().hex[:8]}.pdf"
        pdf_path = self.report_dir / pdf_filename
        
        pdf.output(str(pdf_path))
        
        report = Report(
            prediction_id=prediction.prediction_id,
            pdf_path=str(pdf_path)
        )
        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)
        
        return report
