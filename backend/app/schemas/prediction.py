from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


# --- Auth schemas ---

class RegisterRequest(BaseModel):
    email: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=2, max_length=255)

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        if "@" not in v or "." not in v.split("@")[-1]:
            raise ValueError("Invalid email format")
        return v.lower()


class LoginRequest(BaseModel):
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        if "@" not in v or "." not in v.split("@")[-1]:
            raise ValueError("Invalid email format")
        return v.lower()


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    full_name: str
    created_at: datetime


class AuthResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse


# --- Prediction schemas ---

class PredictionUploadResponse(BaseModel):
    """Response returned after successfully uploading an image."""

    prediction_id: int
    filename: str
    status: str
    message: str
    created_at: str
    image_url: str | None = None
    prediction: str = "Pending"
    confidence: float = 0.0
    heatmap_url: str | None = None
    pdf_url: str | None = None
    is_pending_inference: bool = True


class PredictionResult(BaseModel):
    """Full prediction result (used once ML inference is integrated)."""

    prediction_id: int
    prediction: str
    confidence: float
    heatmap_url: str | None = None
    pdf_url: str | None = None


class PredictionHistoryItem(BaseModel):
    """A single entry in prediction history."""

    prediction_id: int
    prediction: str
    confidence: float
    created_at: str
    image_url: str | None = None


class PredictionDetail(BaseModel):
    """Detailed prediction for GET /predictions/{id} - matches frontend PredictionOutcome."""

    prediction_id: int
    prediction: str
    confidence: float
    heatmap_url: str | None = None
    pdf_url: str | None = None
    filename: str
    created_at: str
    image_url: str | None = None
    is_pending_inference: bool
    metadata: dict | None = None
