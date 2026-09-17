import os
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
import sys

# Add backend to path to import app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.ml.model import get_resnet50_model

def train_model(data_dir, num_epochs=10, batch_size=32, learning_rate=0.001):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    # Data transformations
    data_transforms = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(10),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])
    
    # Load dataset
    image_dataset = datasets.ImageFolder(data_dir, data_transforms)
    dataloader = DataLoader(image_dataset, batch_size=batch_size, shuffle=True, num_workers=4)
    
    dataset_size = len(image_dataset)
    class_names = image_dataset.classes
    print(f"Classes: {class_names}")
    print(f"Total images: {dataset_size}")
    
    model = get_resnet50_model(num_classes=len(class_names), pretrained=True)
    model = model.to(device)
    
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)
    
    # Training Loop
    for epoch in range(num_epochs):
        print(f'Epoch {epoch}/{num_epochs - 1}')
        print('-' * 10)
        
        model.train()
        running_loss = 0.0
        running_corrects = 0
        
        for inputs, labels in dataloader:
            inputs = inputs.to(device)
            labels = labels.to(device)
            
            optimizer.zero_grad()
            
            outputs = model(inputs)
            _, preds = torch.max(outputs, 1)
            loss = criterion(outputs, labels)
            
            loss.backward()
            optimizer.step()
            
            running_loss += loss.item() * inputs.size(0)
            running_corrects += torch.sum(preds == labels.data)
            
        epoch_loss = running_loss / dataset_size
        epoch_acc = running_corrects.double() / dataset_size
        
        print(f'Loss: {epoch_loss:.4f} Acc: {epoch_acc:.4f}')
        
    print("Training complete.")
    
    # Save the model
    save_dir = os.path.join(os.path.dirname(__file__), '../app/ml/weights')
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, 'resnet50_oral_cancer.pth')
    torch.save(model.state_dict(), save_path)
    print(f"Model saved to {save_path}")

if __name__ == '__main__':
    # Default dataset path
    default_data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../oral-cancer/Oral Cancer Dataset'))
    data_dir = os.environ.get("DATA_DIR", default_data_dir)
    
    if os.path.exists(data_dir):
        train_model(data_dir, num_epochs=1)
    else:
        print(f"Dataset directory not found at {data_dir}. Please set DATA_DIR.")
