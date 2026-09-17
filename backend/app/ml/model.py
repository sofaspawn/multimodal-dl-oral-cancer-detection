import torch
import torch.nn as nn
from torchvision import models

def get_resnet50_model(num_classes=2, pretrained=True):
    weights = models.ResNet50_Weights.DEFAULT if pretrained else None
    model = models.resnet50(weights=weights)
    
    # Replace the final fully connected layer
    num_ftrs = model.fc.in_features
    model.fc = nn.Linear(num_ftrs, num_classes)
    
    return model

def load_model(model_path=None, device="cpu"):
    model = get_resnet50_model(num_classes=2, pretrained=True)
    if model_path:
        try:
            model.load_state_dict(torch.load(model_path, map_location=device))
        except Exception as e:
            print(f"Failed to load model weights from {model_path}, using pre-trained ImageNet weights. Error: {e}")
    model.to(device)
    model.eval()
    return model
