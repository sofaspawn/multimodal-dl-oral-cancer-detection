from pathlib import Path
from fastapi import UploadFile, HTTPException
import shutil
from uuid import uuid4

UPLOAD_DIR = Path("app/uploads")

class PredictionService:
    def save_image(self, file: UploadFile):
        if file.filename is None:
            raise HTTPException(status_code=400, detail="No filename provided.")

        extension = Path(file.filename).suffix if file.filename else ".jpg"
        filename = f"{uuid4()}{extension}"

        destination = UPLOAD_DIR / filename

        with destination.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        return filename
