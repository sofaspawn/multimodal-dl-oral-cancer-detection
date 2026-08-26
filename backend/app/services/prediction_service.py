import shutil
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models import Prediction, Report, User


class PredictionService:
    """Handles prediction-related business logic.

    Currently persists uploaded images and creates pending prediction rows.
    The inference path remains replaceable for later ML integration.
    """

    def __init__(self, db: Session) -> None:
        self.db = db
        self.upload_dir = settings.UPLOAD_DIR
        self._ensure_upload_dir()

    def _ensure_upload_dir(self) -> None:
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    def _validate_file(self, file: UploadFile) -> None:
        if file.filename is None:
            raise ValueError("No filename provided.")

        extension = Path(file.filename).suffix.lower()
        if extension not in settings.ALLOWED_EXTENSIONS:
            raise ValueError(
                f"Unsupported file type '{extension}'. "
                f"Allowed types: {', '.join(sorted(settings.ALLOWED_EXTENSIONS))}"
            )

    def save_image(self, file: UploadFile) -> str:
        self._validate_file(file)

        extension = Path(file.filename).suffix.lower()  # type: ignore[arg-type]
        filename = f"{uuid4()}{extension}"
        destination = self.upload_dir / filename

        with destination.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        return filename

    def create_prediction(self, user: User, file: UploadFile) -> Prediction:
        filename = self.save_image(file)
        prediction = Prediction(
            user_id=user.id,
            filename=filename,
            image_path=str(self.upload_dir / filename),
        )
        self.db.add(prediction)
        self.db.commit()
        self.db.refresh(prediction)
        return prediction

    def list_predictions(self, user: User) -> list[Prediction]:
        stmt = (
            select(Prediction)
            .where(Prediction.user_id == user.id)
            .order_by(desc(Prediction.created_at), desc(Prediction.prediction_id))
        )
        return list(self.db.scalars(stmt).all())

    def get_prediction(self, prediction_id: int, user: User) -> Prediction | None:
        stmt = select(Prediction).where(
            Prediction.prediction_id == prediction_id,
            Prediction.user_id == user.id,
        )
        return self.db.scalar(stmt)

    def get_report(self, prediction_id: int, user: User) -> Report | None:
        prediction = self.get_prediction(prediction_id, user)
        if prediction is None:
            return None
        return prediction.report
