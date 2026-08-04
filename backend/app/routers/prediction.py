#from pathlib import Path
from fastapi import APIRouter, UploadFile, File
from app.services.prediction_service import PredictionService

router = APIRouter()

@router.post("/predict")
async def predict(file: UploadFile = File(...)):
    filename = PredictionService().save_image(file)

    return {
        "filename": filename,
        "status": "uploaded successfully",
    }
