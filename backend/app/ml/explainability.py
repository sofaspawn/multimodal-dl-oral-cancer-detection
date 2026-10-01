import os
import cv2
import numpy as np
import torch
from pytorch_grad_cam import GradCAM
from pytorch_grad_cam.utils.image import show_cam_on_image
from PIL import Image

from app.ml.inference import get_inference_model, preprocess

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def generate_gradcam_heatmap(image_path: str, output_path: str) -> str:
    """
    Generates a Grad-CAM heatmap for the given image and saves it to output_path.
    Returns the output_path.
    """
    model = get_inference_model()

    # Initialize CAM
    cam = GradCAM(model=model, target_layers=[model.layer4[-1]])
    
    # Load and preprocess image
    try:
        image = Image.open(image_path).convert('RGB')
    except Exception as e:
        print(f"Error loading image for Grad-CAM {image_path}: {e}")
        return None
        
    input_tensor = preprocess(image)
    input_batch = input_tensor.unsqueeze(0).to(device)
    
    # Generate CAM for the highest scoring class
    targets = None
    grayscale_cam = cam(input_tensor=input_batch, targets=targets)
    grayscale_cam = grayscale_cam[0, :]
    
    # Overlay CAM on original image
    rgb_img = np.float32(image.resize((224, 224))) / 255
    visualization = show_cam_on_image(rgb_img, grayscale_cam, use_rgb=True)
    
    # Save the visualization
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    cv2.imwrite(output_path, cv2.cvtColor(visualization, cv2.COLOR_RGB2BGR))
    
    return output_path
