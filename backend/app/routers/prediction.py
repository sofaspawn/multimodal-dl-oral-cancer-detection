from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.dependencies.auth import get_current_user
from app.models import Prediction, User
from app.schemas.prediction import PredictionDetail, PredictionHistoryItem, PredictionUploadResponse
from app.services.prediction_service import PredictionService

router = APIRouter(tags=["predictions"])


def _record_to_detail(record: Prediction) -> PredictionDetail:
    return PredictionDetail(
        prediction_id=record.prediction_id,
        prediction=record.prediction or "Pending",
        confidence=record.confidence or 0.0,
        heatmap_url=f"/uploads/heatmaps/{record.heatmap_path}" if record.heatmap_path else None,
        pdf_url=f"/reports/{record.prediction_id}" if record.report else None,
        filename=record.filename,
        created_at=record.created_at.isoformat(),
        image_url=f"/uploads/{record.filename}" if record.filename else None,
        is_pending_inference=record.is_pending,
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
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PredictionUploadResponse:
    service = PredictionService(db)
    try:
        prediction = service.create_prediction(user=user, file=file)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return PredictionUploadResponse(
        prediction_id=prediction.prediction_id,
        filename=prediction.filename,
        status="uploaded",
        message="Image uploaded successfully. Prediction pending ML integration.",
        created_at=prediction.created_at.isoformat(),
        image_url=f"/uploads/{prediction.filename}" if prediction.filename else None,
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
        raise HTTPException(status_code=501, detail="PDF generation not implemented yet")
    raise HTTPException(status_code=501, detail="PDF generation not implemented yet")
