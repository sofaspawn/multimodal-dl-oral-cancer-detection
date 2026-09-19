import os
import sys
import torch
import torch.nn as nn
import torch.optim as optim
from torch.optim.lr_scheduler import StepLR
from torchvision import datasets, transforms
from torch.utils.data import DataLoader, random_split

# Add backend to path to import app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.ml.model import get_resnet50_model


def train_model(data_dir, num_epochs=15, batch_size=32, learning_rate=0.0001):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Training on device: {device}")

    # ------------------------------------------------------------------
    # Transforms — heavier augmentation for training, clean resize for val
    # ------------------------------------------------------------------
    train_transforms = transforms.Compose([
        transforms.Resize((256, 256)),
        transforms.RandomResizedCrop(224, scale=(0.8, 1.0)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomVerticalFlip(),
        transforms.RandomRotation(15),
        transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.1),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ])

    val_transforms = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ])

    # ------------------------------------------------------------------
    # Dataset — 80/20 train/val split
    # ------------------------------------------------------------------
    full_dataset = datasets.ImageFolder(data_dir, transform=train_transforms)
    class_names = full_dataset.classes
    total = len(full_dataset)
    val_size = int(total * 0.2)
    train_size = total - val_size
    train_dataset, val_dataset = random_split(full_dataset, [train_size, val_size])

    # Override the val subset transform
    val_dataset.dataset = datasets.ImageFolder(data_dir, transform=val_transforms)

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=4)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=4)

    print(f"Classes: {class_names}")
    print(f"Total images: {total} (train: {train_size}, val: {val_size})")

    # ------------------------------------------------------------------
    # Model, Loss, Optimizer, Scheduler
    # ------------------------------------------------------------------
    model = get_resnet50_model(num_classes=len(class_names), pretrained=True)

    # Freeze early layers — only fine-tune layer3, layer4, and fc
    for name, param in model.named_parameters():
        if not any(k in name for k in ["layer3", "layer4", "fc"]):
            param.requires_grad = False

    model = model.to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(
        filter(lambda p: p.requires_grad, model.parameters()),
        lr=learning_rate,
        weight_decay=1e-4,
    )
    scheduler = StepLR(optimizer, step_size=5, gamma=0.5)

    # ------------------------------------------------------------------
    # Training loop — saves best model by validation accuracy
    # ------------------------------------------------------------------
    best_val_acc = 0.0
    save_dir = os.path.join(os.path.dirname(__file__), '../app/ml/weights')
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, 'resnet50_oral_cancer.pth')

    for epoch in range(num_epochs):
        # --- Training phase ---
        model.train()
        running_loss = 0.0
        running_corrects = 0

        for inputs, labels in train_loader:
            inputs, labels = inputs.to(device), labels.to(device)
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            _, preds = torch.max(outputs, 1)
            running_loss += loss.item() * inputs.size(0)
            running_corrects += torch.sum(preds == labels.data)

        train_loss = running_loss / train_size
        train_acc = running_corrects.double() / train_size

        # --- Validation phase ---
        model.eval()
        val_corrects = 0
        val_loss_sum = 0.0
        with torch.no_grad():
            for inputs, labels in val_loader:
                inputs, labels = inputs.to(device), labels.to(device)
                outputs = model(inputs)
                loss = criterion(outputs, labels)
                _, preds = torch.max(outputs, 1)
                val_loss_sum += loss.item() * inputs.size(0)
                val_corrects += torch.sum(preds == labels.data)

        val_loss = val_loss_sum / val_size
        val_acc = val_corrects.double() / val_size

        scheduler.step()
        current_lr = scheduler.get_last_lr()[0]

        print(
            f"Epoch {epoch + 1}/{num_epochs} | "
            f"Train Loss: {train_loss:.4f} Acc: {train_acc:.4f} | "
            f"Val Loss: {val_loss:.4f} Acc: {val_acc:.4f} | "
            f"LR: {current_lr:.6f}"
        )

        # Save best model
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            torch.save(model.state_dict(), save_path)
            print(f"  -> Best model saved (val_acc: {val_acc:.4f})")

    print(f"\nTraining complete. Best validation accuracy: {best_val_acc:.4f}")
    print(f"Model saved to {save_path}")


if __name__ == '__main__':
    default_data_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '../../oral-cancer/Oral Cancer Dataset')
    )
    data_dir = os.environ.get("DATA_DIR", default_data_dir)

    if os.path.exists(data_dir):
        train_model(data_dir, num_epochs=15)
    else:
        print(f"Dataset directory not found at {data_dir}. Please set DATA_DIR.")
