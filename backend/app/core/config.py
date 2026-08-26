import json
import os
from pathlib import Path


class Settings:
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    APP_DIR: Path = BASE_DIR / "app"

    UPLOAD_DIR: Path = Path(os.getenv("UPLOAD_DIR", str(APP_DIR / "uploads")))
    ALLOWED_EXTENSIONS: set[str] = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp"}
    MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", "10"))

    API_TITLE: str = os.getenv("API_TITLE", "Oral Cancer Detection API")
    API_VERSION: str = os.getenv("API_VERSION", "1.0.0")

    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-change-in-production")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))

    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'oral_cancer.db'}")
    AUTO_CREATE_TABLES: bool = os.getenv("AUTO_CREATE_TABLES", "true").lower() == "true"

    CORS_ORIGINS_RAW: str = os.getenv(
        "CORS_ORIGINS",
        '["http://localhost:5173", "http://localhost:3000"]',
    )

    @property
    def max_file_size_bytes(self) -> int:
        return self.MAX_FILE_SIZE_MB * 1024 * 1024

    @property
    def cors_origins(self) -> list[str]:
        raw = self.CORS_ORIGINS_RAW.strip()
        if raw.startswith("["):
            return json.loads(raw)
        return [origin.strip() for origin in raw.split(",") if origin.strip()]


settings = Settings()
