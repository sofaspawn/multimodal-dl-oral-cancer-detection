import torch
import torch.nn.functional as F
from torchvision import transforms
from PIL import Image
from dataclasses import dataclass
from typing import Tuple, List
import numpy as np

from app.ml.model import load_model

# Initialize model (lazy loading or at startup)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = None

import os

def get_inference_model():
    global model
    if model is None:
        enhanced_path = os.path.join(os.path.dirname(__file__), 'weights/resnet50_oral_cancer_enhanced.pth')
        default_path = os.path.join(os.path.dirname(__file__), 'weights/resnet50_oral_cancer.pth')
        model_path = enhanced_path if os.path.exists(enhanced_path) else default_path
        model = load_model(model_path=model_path if os.path.exists(model_path) else None, device=device)
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
    confidence: float  # Mean confidence score (0-1)
    severity: str | None  # "mild", "moderate", "severe" (only for Cancer)
    potentially_malignant: bool  # True if lesion shows suspicious characteristics
    # Uncertainty metrics
    cancer_probability: float  # Probability of cancer class
    confidence_std: float  # Standard deviation across TTA runs
    entropy: float  # Prediction entropy (higher = more uncertain)


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


def _calculate_entropy(probabilities: np.ndarray) -> float:
    """Calculate Shannon entropy of probability distribution."""
    # Add small epsilon to avoid log(0)
    probs = np.clip(probabilities, 1e-10, 1.0)
    entropy = -np.sum(probs * np.log(probs))
    return entropy


def _assess_potentially_malignant(
    predicted_idx: int,
    mean_confidence: float,
    cancer_probability: float,
    confidence_std: float,
    entropy: float
) -> bool:
    """
    Assess if the lesion is potentially malignant.

    This uses a more sophisticated assessment that considers:
    1. Direct cancer prediction
    2. Prediction confidence
    3. Uncertainty (high std or entropy = less confident)
    4. The balance of probabilities

    A lesion is considered potentially malignant if:
    - The model predicts Cancer with confidence, OR
    - There's significant uncertainty (could go either way), OR
    - The model slightly favors cancer but isn't certain

    This conservative approach is appropriate for a screening tool.
    """
    # Direct cancer prediction with reasonable confidence
    if predicted_idx == 1 and mean_confidence > 0.6:
        return True

    # Uncertain predictions - could indicate subtle early-stage cancer
    # that the model can't confidently classify either way
    if confidence_std > 0.1 or entropy > 0.5:
        # If the model is uncertain, lean toward flagging for review
        if cancer_probability > 0.35:  # Even slight lean toward cancer
            return True

    # Close to decision boundary - needs expert review
    if 0.45 < cancer_probability < 0.55:
        return True

    # Low confidence cancer prediction
    if predicted_idx == 1 and mean_confidence < 0.65:
        return True

    return False


def _get_tta_transforms():
    """
    Get test-time augmentation transforms for more robust predictions.
    Returns a list of transform functions.
    """
    return [
        # Original
        transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
        ]),
        # Horizontal flip
        transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.RandomHorizontalFlip(p=1.0),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
        ]),
        # Slight rotation
        transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.RandomRotation(5),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
        ]),
        # Slight brightness/contrast adjustment
        transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ColorJitter(brightness=0.1, contrast=0.1),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
        ]),
        # Center crop variant
        transforms.Compose([
            transforms.Resize((256, 256)),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
        ]),
    ]


def predict_image(image_path: str) -> PredictionResult:
    """
    Runs inference on an image using Test-Time Augmentation (TTA).

    TTA helps reduce false positives by:
    1. Running multiple augmented versions of the image
    2. Averaging predictions to get a more robust result
    3. Measuring uncertainty via standard deviation

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
            potentially_malignant=False,
            cancer_probability=0.0,
            confidence_std=0.0,
            entropy=0.0
        )

    # Get TTA transforms
    tta_transforms = _get_tta_transforms()
    all_probs = []

    # Run inference on each augmented version
    for transform in tta_transforms:
        input_tensor = transform(image)
        input_batch = input_tensor.unsqueeze(0).to(device)

        with torch.no_grad():
            output = model(input_batch)
            probs = F.softmax(output[0], dim=0)
            all_probs.append(probs.cpu().numpy())

    # Stack all probabilities
    all_probs = np.array(all_probs)  # Shape: (num_augmentations, num_classes)

    # Calculate statistics
    mean_probs = np.mean(all_probs, axis=0)
    std_probs = np.std(all_probs, axis=0)

    # Get mean confidence and prediction
    mean_confidence = float(np.max(mean_probs))
    predicted_idx = int(np.argmax(mean_probs))

    # Get cancer probability (index 1)
    cancer_probability = float(mean_probs[1])

    # Calculate uncertainty metrics
    confidence_std = float(np.max(std_probs))
    entropy = _calculate_entropy(mean_probs)

    labels = ["Non-Cancer", "Cancer"]  # Index 0 is Non-Cancer, 1 is Cancer
    predicted_label = labels[predicted_idx]

    # Determine severity only for Cancer predictions
    severity = None
    if predicted_idx == 1:
        severity = _determine_severity(cancer_probability)

    # Assess potentially malignant status using more sophisticated criteria
    potentially_malignant = _assess_potentially_malignant(
        predicted_idx,
        mean_confidence,
        cancer_probability,
        confidence_std,
        entropy
    )

    return PredictionResult(
        label=predicted_label,
        confidence=mean_confidence,
        severity=severity,
        potentially_malignant=potentially_malignant,
        cancer_probability=cancer_probability,
        confidence_std=confidence_std,
        entropy=entropy
    )


# Backward compatibility: keep the old function signature for existing code
def predict_image_legacy(image_path: str):
    """
    Legacy function for backward compatibility.
    Returns: (prediction_label, confidence_score)
    """
    result = predict_image(image_path)
    return result.label, result.confidence
