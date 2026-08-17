from pathlib import Path

class Settings:
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    APP_DIR: Path = BASE_DIR / "app"

    UPLOAD_DIR: Path = APP_DIR / "uploads"
    ALLOWED_EXTENSIONS: set[str] = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp"}
    MAX_FILE_SIZE_MB: int = 10

    API_TITLE: str = "Oral Cancer Detection API"
    API_VERSION: str = "1.0.0"

    @property
    def max_file_size_bytes(self) -> int:
        return self.MAX_FILE_SIZE_MB * 1024 * 1024


settings = Settings()
