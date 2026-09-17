import torch
import torch.nn.functional as F
from torchvision import transforms
from PIL import Image

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

def predict_image(image_path: str):
    """
    Runs inference on an image.
    Returns: (prediction_label, confidence_score)
    """
    model = get_inference_model()
    
    # Load and preprocess image
    try:
        image = Image.open(image_path).convert('RGB')
    except Exception as e:
        print(f"Error loading image {image_path}: {e}")
        return "Error", 0.0
        
    input_tensor = preprocess(image)
    input_batch = input_tensor.unsqueeze(0).to(device)
    
    with torch.no_grad():
        output = model(input_batch)
        probabilities = F.softmax(output[0], dim=0)
        confidence, predicted_idx = torch.max(probabilities, 0)
        
    labels = ["Non-Cancer", "Cancer"] # Index 0 is Non-Cancer, 1 is Cancer
    predicted_label = labels[predicted_idx.item()]
    confidence_score = confidence.item()
    
    return predicted_label, confidence_score
