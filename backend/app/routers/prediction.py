from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
import shutil

from uuid import uuid4

extension = Path(file.filename).suffix if file.filename else ".jpg"

router = APIRouter()

UPLOAD_DIR = Path("app/uploads")


@router.post("/predict")
async def predict(file: UploadFile = File(...)):
    if file.filename is None:
        raise HTTPException(status_code=400, detail="No filename provided.")

    destination = UPLOAD_DIR / file.filename

    with destination.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "filename": file.filename,
        "status": "uploaded successfully",
    }
