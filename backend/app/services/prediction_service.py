from pathlib import Path
import shutil
from uuid import uuid4

from fastapi import UploadFile

from app.core.config import settings


class PredictionService:
    """Handles prediction-related business logic.

    Currently only handles image upload and storage.
    Will later include preprocessing, inference, GradCAM, and report generation.
    """

    def __init__(self) -> None:
        self.upload_dir = settings.UPLOAD_DIR
        self._ensure_upload_dir()

    def _ensure_upload_dir(self) -> None:
        """Create the uploads directory if it does not exist."""
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    def _validate_file(self, file: UploadFile) -> None:
        """Validate file extension."""
        if file.filename is None:
            raise ValueError("No filename provided.")

        extension = Path(file.filename).suffix.lower()
        if extension not in settings.ALLOWED_EXTENSIONS:
            raise ValueError(
                f"Unsupported file type '{extension}'. "
                f"Allowed types: {', '.join(sorted(settings.ALLOWED_EXTENSIONS))}"
            )

    def save_image(self, file: UploadFile) -> str:
        """Save an uploaded image to disk.

        Args:
            file: The uploaded image file.

        Returns:
            The generated filename (UUID-based) under which the file was saved.

        Raises:
            ValueError: If the file is invalid (bad extension, no filename).
        """
        self._validate_file(file)

        extension = Path(file.filename).suffix.lower()  # type: ignore[arg-type]
        filename = f"{uuid4()}{extension}"
        destination = self.upload_dir / filename

        with destination.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        return filename
