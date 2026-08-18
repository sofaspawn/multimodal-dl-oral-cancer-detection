from datetime import datetime
from pathlib import Path
from fastapi import APIRouter, Depends, File, Header, HTTPException, UploadFile, status

from app.core.config import settings
from app.models.store import PredictionRecord, PredictionStore, UserStore
from app.schemas.prediction import (
    PredictionDetail,
    PredictionHistoryItem,
    PredictionUploadResponse,
)
from app.services.prediction_service import PredictionService

router = APIRouter(tags=["predictions"])

prediction_service = PredictionService()


async def get_current_user_id(authorization: str = Header(None)) -> int:
    """Extract user_id from Bearer token. Shared with auth router."""
    from app.core.security import decode_token

    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header",
        )
    token = authorization[7:]
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    user = UserStore.get_by_id(payload.sub)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return user.id


def _record_to_detail(record: PredictionRecord) -> PredictionDetail:
    """Convert store record to frontend-compatible PredictionDetail."""
    is_pending = record.prediction is None
    return PredictionDetail(
        prediction_id=record.prediction_id,
        prediction=record.prediction or "Pending",
        confidence=record.confidence or 0.0,
        heatmap_url=f"/uploads/heatmaps/{record.heatmap_path}" if record.heatmap_path else None,
        pdf_url=f"/reports/{record.prediction_id}.pdf" if not is_pending else None,
        filename=record.filename,
        created_at=record.created_at.isoformat(),
        image_url=f"/uploads/{record.filename}" if record.filename else None,
        is_pending_inference=is_pending,
    )


def _record_to_history_item(record: PredictionRecord) -> PredictionHistoryItem:
    """Convert store record to frontend-compatible history item."""
    return PredictionHistoryItem(
        prediction_id=record.prediction_id,
        prediction=record.prediction or "Pending",
        confidence=record.confidence or 0.0,
        created_at=record.created_at.isoformat(),
    )


@router.post("/predict", response_model=PredictionUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_prediction(
    file: UploadFile = File(...),
    user_id: int = Depends(get_current_user_id),
) -> PredictionUploadResponse:
    """Upload an image for prediction. Associates with authenticated user."""
    try:
        filename = prediction_service.save_image(file)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    image_path = str(settings.UPLOAD_DIR / filename)
    record = PredictionStore.create(user_id=user_id, filename=filename, image_path=image_path)

    return PredictionUploadResponse(
        filename=filename,
        status="uploaded",
        message="Image uploaded successfully. Prediction pending ML integration.",
    )


@router.get("/predictions", response_model=list[PredictionHistoryItem])
def list_predictions(user_id: int = Depends(get_current_user_id)):
    """Get prediction history for the authenticated user."""
    records = PredictionStore.get_by_user(user_id)
    return [_record_to_history_item(r) for r in records]


@router.get("/predictions/{prediction_id}", response_model=PredictionDetail)
def get_prediction(
    prediction_id: int,
    user_id: int = Depends(get_current_user_id),
):
    """Get detailed prediction by ID. Only returns user's own predictions."""
    record = PredictionStore.get(prediction_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Prediction not found")
    if record.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to view this prediction")

    return _record_to_detail(record)


@router.get("/reports/{prediction_id}")
def download_report(
    prediction_id: int,
    user_id: int = Depends(get_current_user_id),
):
    """Download PDF report for a prediction. Placeholder for Phase 3."""
    record = PredictionStore.get(prediction_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Prediction not found")
    if record.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    if record.prediction is None:
        raise HTTPException(status_code=400, detail="Report not available until inference completes")

    # In Phase 3, this would serve a generated PDF
    raise HTTPException(status_code=501, detail="PDF generation not implemented yet")