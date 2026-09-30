import torch
import torch.nn.functional as F
from torchvision import transforms
from PIL import Image
from dataclasses import dataclass

from app.ml.model import load_model

# Initialize model (lazy loading or at startup)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = None

import os

def get_inference_model():
    global model
    if model is None:
        model_path = os.path.join(os.path.dirname(__file__), 'weights/resnet50_oral_cancer.pth')
        if not os.path.exists(model_path):
            model_path = None
        model = load_model(model_path=model_path, device=device)
    return model

# Preprocessing transforms (standard ImageNet normalization)
preprocess = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225]),
])


@dataclass
class PredictionResult:
    """Structured prediction result with severity and malignancy assessment."""
    label: str  # "Cancer" or "Non-Cancer"
    confidence: float  # Raw confidence score (0-1)
    severity: str | None  # "mild", "moderate", "severe" (only for Cancer)
    potentially_malignant: bool  # True if lesion shows suspicious characteristics


def _determine_severity(confidence: float) -> str:
    """
    Determine severity based on confidence score.

    The model shows high confidence even for non-cancerous images, so we use
    the confidence threshold to assess severity of cancerous predictions:
    - Low confidence (0.5-0.7): mild - early stage, less aggressive features
    - Medium confidence (0.7-0.85): moderate - established lesion
    - High confidence (>0.85): severe - advanced or highly aggressive features
    """
    if confidence < 0.7:
        return "mild"
    elif confidence < 0.85:
        return "moderate"
    else:
        return "severe"


def _assess_potentially_malignant(predicted_idx: int, confidence: float) -> bool:
    """
    Assess if the lesion is potentially malignant.

    A lesion is considered potentially malignant if:
    1. The model predicts Cancer with any confidence, OR
    2. The model is uncertain (confidence near 0.5) - could indicate early-stage
       cancer not visually distinct from benign lesions

    This is a conservative approach for a screening tool where false positives
    are preferable to false negatives.
    """
    # If Cancer prediction
    if predicted_idx == 1:
        return True

    # If uncertain (confidence close to random), flag as potentially malignant
    # as a safety measure for screening purposes
    if 0.45 < confidence < 0.55:
        return True

    return False


def predict_image(image_path: str) -> PredictionResult:
    """
    Runs inference on an image.
    Returns: PredictionResult with label, confidence, severity, and malignancy assessment.
    """
    model = get_inference_model()

    # Load and preprocess image
    try:
        image = Image.open(image_path).convert('RGB')
    except Exception as e:
        print(f"Error loading image {image_path}: {e}")
        return PredictionResult(
            label="Error",
            confidence=0.0,
            severity=None,
            potentially_malignant=False
        )

    input_tensor = preprocess(image)
    input_batch = input_tensor.unsqueeze(0).to(device)

    with torch.no_grad():
        output = model(input_batch)
        probabilities = F.softmax(output[0], dim=0)
        confidence, predicted_idx = torch.max(probabilities, 0)

    labels = ["Non-Cancer", "Cancer"]  # Index 0 is Non-Cancer, 1 is Cancer
    predicted_label = labels[predicted_idx.item()]
    confidence_score = confidence.item()

    # Determine severity only for Cancer predictions
    severity = None
    if predicted_idx == 1:
        severity = _determine_severity(confidence_score)

    # Assess potentially malignant status
    potentially_malignant = _assess_potentially_malignant(predicted_idx.item(), confidence_score)

    return PredictionResult(
        label=predicted_label,
        confidence=confidence_score,
        severity=severity,
        potentially_malignant=potentially_malignant
    )


# Backward compatibility: keep the old function signature for existing code
def predict_image_legacy(image_path: str):
    """
    Legacy function for backward compatibility.
    Returns: (prediction_label, confidence_score)
    """
    result = predict_image(image_path)
    return result.label, result.confidence
