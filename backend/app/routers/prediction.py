from fastapi import APIRouter, File, HTTPException, UploadFile

from app.schemas.prediction import PredictionUploadResponse
from app.services.prediction_service import PredictionService

router = APIRouter()

prediction_service = PredictionService()


@router.post("/predict", response_model=PredictionUploadResponse)
async def predict(file: UploadFile = File(...)) -> PredictionUploadResponse:
    try:
        filename = prediction_service.save_image(file)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return PredictionUploadResponse(
        filename=filename,
        status="uploaded",
        message="Image uploaded successfully. Prediction pending ML integration.",
    )
