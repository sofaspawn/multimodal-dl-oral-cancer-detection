from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
import json
from pathlib import Path
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.db import get_db
from app.core.config import settings
from app.dependencies.auth import get_current_user
from app.models import Prediction, Report, User
from app.schemas.prediction import PredictionDetail, PredictionHistoryItem, PredictionUploadResponse
from app.services.prediction_service import PredictionService

router = APIRouter(tags=["predictions"])


def _record_to_detail(record: Prediction) -> PredictionDetail:
    return PredictionDetail(
        prediction_id=record.prediction_id,
        prediction=record.prediction or "Pending",
        confidence=record.confidence or 0.0,
        heatmap_url=f"/uploads/heatmaps/{Path(record.heatmap_path).name}" if record.heatmap_path else None,
        pdf_url=f"/reports/{record.prediction_id}" if record.report else None,
        filename=record.filename,
        created_at=record.created_at.isoformat(),
        image_url=f"/uploads/{record.filename}" if record.filename else None,
        is_pending_inference=record.is_pending,
        metadata=record.metadata_json,
    )


def _record_to_history_item(record: Prediction) -> PredictionHistoryItem:
    return PredictionHistoryItem(
        prediction_id=record.prediction_id,
        prediction=record.prediction or "Pending",
        confidence=record.confidence or 0.0,
        created_at=record.created_at.isoformat(),
        image_url=f"/uploads/{record.filename}" if record.filename else None,
    )


@router.post("/predict", response_model=PredictionUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_prediction(
    file: UploadFile = File(...),
    metadata_json: str | None = Form(None),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PredictionUploadResponse:
    service = PredictionService(db)
    try:
        metadata = None
        if metadata_json:
            try:
                metadata = json.loads(metadata_json)
            except json.JSONDecodeError as exc:
                raise ValueError("metadata_json must be valid JSON") from exc
            if not isinstance(metadata, dict):
                raise ValueError("metadata_json must contain a JSON object")
        prediction = service.create_prediction(user=user, file=file, metadata=metadata)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return PredictionUploadResponse(
        prediction_id=prediction.prediction_id,
        filename=prediction.filename,
        status="uploaded",
        message="Image uploaded and inference completed successfully.",
        created_at=prediction.created_at.isoformat(),
        image_url=f"/uploads/{prediction.filename}" if prediction.filename else None,
        prediction=prediction.prediction,
        confidence=prediction.confidence,
        heatmap_url=f"/uploads/heatmaps/{Path(prediction.heatmap_path).name}" if prediction.heatmap_path else None,
        pdf_url=f"/reports/{prediction.prediction_id}",
        is_pending_inference=False,
    )


@router.get("/predictions", response_model=list[PredictionHistoryItem])
def list_predictions(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = PredictionService(db)
    return [_record_to_history_item(record) for record in service.list_predictions(user)]


@router.get("/predictions/{prediction_id}", response_model=PredictionDetail)
def get_prediction(
    prediction_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = PredictionService(db)
    record = service.get_prediction(prediction_id, user)
    if record is None:
        raise HTTPException(status_code=404, detail="Prediction not found")
    return _record_to_detail(record)


@router.get("/reports/{prediction_id}")
def download_report(
    prediction_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = PredictionService(db)
    record = service.get_prediction(prediction_id, user)
    if record is None:
        raise HTTPException(status_code=404, detail="Prediction not found")
    if record.is_pending:
        raise HTTPException(status_code=400, detail="Report not available until inference completes")
    if record.report is None:
        from app.services.report_service import ReportService
        report_svc = ReportService(db)
        record.report = report_svc.generate_pdf_report(record)

    report_path = Path(record.report.pdf_path)
    if not report_path.is_file():
        raise HTTPException(status_code=404, detail="Report file not found")
    return FileResponse(str(report_path), media_type="application/pdf", filename=report_path.name)
