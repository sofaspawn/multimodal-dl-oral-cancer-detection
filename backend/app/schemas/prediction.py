from pydantic import BaseModel


class PredictionUploadResponse(BaseModel):
    """Response returned after successfully uploading an image."""
    filename: str
    status: str
    message: str


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
