"""
Enhanced training script for oral cancer detection.

Addresses:
1. False positive rate (requirement 3)
2. Detection of subtle/early-stage lesions (requirement 4)

Key improvements:
- Focal Loss to handle class imbalance and focus on hard examples
- MixUp augmentation for better generalization
- Label smoothing to reduce overconfidence
- Higher dropout for regularization
- Learning rate warmup + cosine annealing
- Better model calibration
- Early stopping based on validation loss
"""

import os
import sys
import torch
import torch.nn as nn
import torch.optim as optim
from torch.optim.lr_scheduler import CosineAnnealingWarmRestarts
from torchvision import datasets, transforms
from torch.utils.data import DataLoader, random_split, WeightedRandomSampler
import numpy as np
from PIL import Image
import random

# Add backend to path to import app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class FocalLoss(nn.Module):
    """
    Focal Loss for handling class imbalance and focusing on hard examples.

    FL(p_t) = -alpha_t * (1 - p_t)^gamma * log(p_t)

    This reduces loss for well-classified examples, focusing training on hard cases.
    """
    def __init__(self, alpha=0.5, gamma=2.0, reduction='mean'):
        super().__init__()
        self.alpha = alpha
        self.gamma = gamma
        self.reduction = reduction

    def forward(self, inputs, targets):
        ce_loss = nn.functional.cross_entropy(inputs, targets, reduction='none')
        pt = torch.exp(-ce_loss)
        focal_loss = self.alpha * (1 - pt) ** self.gamma * ce_loss

        if self.reduction == 'mean':
            return focal_loss.mean()
        elif self.reduction == 'sum':
            return focal_loss.sum()
        return focal_loss


class LabelSmoothingCrossEntropy(nn.Module):
    """Label smoothing to reduce model overconfidence."""
    def __init__(self, smoothing=0.1):
        super().__init__()
        self.smoothing = smoothing

    def forward(self, pred, target):
        n_classes = pred.size(1)
        # Convert target to one-hot with smoothing
        target_one_hot = torch.zeros_like(pred)
        target_one_hot.scatter_(1, target.unsqueeze(1), 1 - self.smoothing)
        target_one_hot += self.smoothing / n_classes

        # Compute loss
        log_pred = nn.functional.log_softmax(pred, dim=1)
        loss = -(target_one_hot * log_pred).sum(dim=1).mean()
        return loss


def mixup_data(x, y, alpha=0.2):
    """
    MixUp augmentation: mix two images and their labels.
    Helps model generalize better and reduces overfitting.
    """
    if alpha > 0:
        lam = np.random.beta(alpha, alpha)
    else:
        lam = 1

    batch_size = x.size(0)
    index = torch.randperm(batch_size).to(x.device)

    mixed_x = lam * x + (1 - lam) * x[index]
    y_a, y_b = y, y[index]
    return mixed_x, y_a, y_b, lam


def mixup_criterion(criterion, pred, y_a, y_b, lam):
    """Compute MixUp loss."""
    return lam * criterion(pred, y_a) + (1 - lam) * criterion(pred, y_b)


def get_resnet50_with_dropout(num_classes=2, pretrained=True, dropout_rate=0.5):
    """
    Get ResNet50 with added dropout for better regularization.
    """
    from torchvision import models

    weights = models.ResNet50_Weights.DEFAULT if pretrained else None
    model = models.resnet50(weights=weights)

    # Replace the final fully connected layer with dropout
    num_ftrs = model.fc.in_features
    model.fc = nn.Sequential(
        nn.Dropout(dropout_rate),
        nn.Linear(num_ftrs, num_classes)
    )

    return model


class EarlyStopping:
    """Early stopping to prevent overfitting."""
    def __init__(self, patience=7, min_delta=0.001):
        self.patience = patience
        self.min_delta = min_delta
        self.counter = 0
        self.best_loss = None
        self.early_stop = False

    def __call__(self, val_loss):
        if self.best_loss is None:
            self.best_loss = val_loss
        elif val_loss > self.best_loss - self.min_delta:
            self.counter += 1
            if self.counter >= self.patience:
                self.early_stop = True
        else:
            self.best_loss = val_loss
            self.counter = 0


def train_model(
    data_dir,
    num_epochs=30,
    batch_size=16,
    learning_rate=0.0001,
    use_focal_loss=True,
    use_mixup=True,
    use_label_smoothing=True,
    dropout_rate=0.5,
    save_path=None
):
    """
    Enhanced training with better regularization and calibration.

    Args:
        data_dir: Path to dataset with CANCER/ and NON CANCER/ subdirectories
        num_epochs: Number of training epochs (default 30, with early stopping)
        batch_size: Batch size (smaller for better gradients)
        learning_rate: Initial learning rate
        use_focal_loss: Use Focal Loss to handle class imbalance
        use_mixup: Use MixUp augmentation
        use_label_smoothing: Use label smoothing to reduce overconfidence
        dropout_rate: Dropout rate for regularization
        save_path: Path to save the best model
    """
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Training on device: {device}")

    # ------------------------------------------------------------------
    # Enhanced Transforms - more augmentation for better generalization
    # ------------------------------------------------------------------
    train_transforms = transforms.Compose([
        transforms.Resize((256, 256)),
        transforms.RandomResizedCrop(224, scale=(0.7, 1.0)),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomVerticalFlip(p=0.5),
        transforms.RandomRotation(20),
        transforms.ColorJitter(brightness=0.3, contrast=0.3, saturation=0.3, hue=0.15),
        transforms.RandomAffine(degrees=0, translate=(0.1, 0.1), scale=(0.9, 1.1)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
        # Random erasing to simulate occlusion
        transforms.RandomErasing(p=0.3, scale=(0.02, 0.1)),
    ])

    val_transforms = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ])

    # ------------------------------------------------------------------
    # Dataset with weighted sampling for class imbalance
    # ------------------------------------------------------------------
    full_dataset = datasets.ImageFolder(data_dir, transform=train_transforms)
    class_names = full_dataset.classes
    class_to_idx = full_dataset.class_to_idx
    print(f"Classes: {class_names} -> {class_to_idx}")

    total = len(full_dataset)
    val_size = int(total * 0.2)
    train_size = total - val_size
    train_dataset, val_dataset = random_split(full_dataset, [train_size, val_size])

    # Create separate val dataset with val transforms
    val_dataset.dataset = datasets.ImageFolder(data_dir, transform=val_transforms)

    # Calculate class weights for balanced sampling
    targets = [full_dataset.targets[i] for i in train_dataset.indices]
    class_counts = np.bincount(targets)
    class_weights = 1.0 / class_counts
    sample_weights = [class_weights[t] for t in targets]

    sampler = WeightedRandomSampler(
        weights=sample_weights,
        num_samples=len(sample_weights),
        replacement=True
    )

    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        sampler=sampler,
        num_workers=4,
        pin_memory=True
    )
    val_loader = DataLoader(
        val_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=4,
        pin_memory=True
    )

    print(f"Total images: {total} (train: {train_size}, val: {val_size})")
    print(f"Class distribution: {class_counts}")

    # ------------------------------------------------------------------
    # Model with dropout
    # ------------------------------------------------------------------
    model = get_resnet50_with_dropout(num_classes=len(class_names), pretrained=True, dropout_rate=dropout_rate)

    # Freeze early layers initially
    for name, param in model.named_parameters():
        if not any(k in name for k in ["layer3", "layer4", "fc"]):
            param.requires_grad = False

    model = model.to(device)

    # Count trainable parameters
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"Trainable parameters: {trainable_params:,}")

    # ------------------------------------------------------------------
    # Loss function
    # ------------------------------------------------------------------
    if use_focal_loss:
        # Use focal loss with alpha weighted for minority class
        criterion = FocalLoss(alpha=0.6, gamma=2.0)
        print("Using Focal Loss")
    elif use_label_smoothing:
        criterion = LabelSmoothingCrossEntropy(smoothing=0.1)
        print("Using Label Smoothing Cross Entropy")
    else:
        criterion = nn.CrossEntropyLoss()
        print("Using Cross Entropy Loss")

    # ------------------------------------------------------------------
    # Optimizer with weight decay
    # ------------------------------------------------------------------
    optimizer = optim.AdamW(
        filter(lambda p: p.requires_grad, model.parameters()),
        lr=learning_rate,
        weight_decay=0.01
    )

    # Cosine annealing with warm restarts
    scheduler = CosineAnnealingWarmRestarts(optimizer, T_0=10, T_mult=2)

    # Early stopping
    early_stopping = EarlyStopping(patience=7, min_delta=0.001)

    # ------------------------------------------------------------------
    # Training loop
    # ------------------------------------------------------------------
    best_val_loss = float('inf')
    best_val_acc = 0.0

    if save_path is None:
        save_dir = os.path.join(os.path.dirname(__file__), '../app/ml/weights')
        os.makedirs(save_dir, exist_ok=True)
        save_path = os.path.join(save_dir, 'resnet50_oral_cancer_enhanced.pth')

    for epoch in range(num_epochs):
        # --- Training phase ---
        model.train()
        running_loss = 0.0
        running_corrects = 0
        all_preds = []
        all_labels = []

        for inputs, labels in train_loader:
            inputs, labels = inputs.to(device), labels.to(device)

            # Apply MixUp augmentation
            if use_mixup and random.random() > 0.5:
                inputs, labels_a, labels_b, lam = mixup_data(inputs, labels, alpha=0.2)

                optimizer.zero_grad()
                outputs = model(inputs)
                loss = mixup_criterion(criterion, outputs, labels_a, labels_b, lam)
            else:
                optimizer.zero_grad()
                outputs = model(inputs)
                loss = criterion(outputs, labels)

            loss.backward()
            optimizer.step()

            _, preds = torch.max(outputs, 1)
            running_loss += loss.item() * inputs.size(0)
            running_corrects += torch.sum(preds == labels.data)
            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())

        train_loss = running_loss / train_size
        train_acc = running_corrects.double() / train_size

        # --- Validation phase ---
        model.eval()
        val_loss_sum = 0.0
        val_corrects = 0
        val_preds = []
        val_labels = []
        val_probs = []

        with torch.no_grad():
            for inputs, labels in val_loader:
                inputs, labels = inputs.to(device), labels.to(device)
                outputs = model(inputs)
                loss = criterion(outputs, labels)
                probs = torch.nn.functional.softmax(outputs, dim=1)

                _, preds = torch.max(outputs, 1)
                val_loss_sum += loss.item() * inputs.size(0)
                val_corrects += torch.sum(preds == labels.data)
                val_preds.extend(preds.cpu().numpy())
                val_labels.extend(labels.cpu().numpy())
                val_probs.extend(probs.cpu().numpy())

        val_loss = val_loss_sum / val_size
        val_acc = val_corrects.double() / val_size

        scheduler.step(epoch)

        # Calculate additional metrics
        val_preds = np.array(val_preds)
        val_labels = np.array(val_labels)
        val_probs = np.array(val_probs)

        # Per-class accuracy
        for i, class_name in enumerate(class_names):
            mask = val_labels == i
            if mask.sum() > 0:
                class_acc = (val_preds[mask] == i).mean()
                print(f"  {class_name} accuracy: {class_acc:.4f}")

        # Average confidence
        avg_conf = np.max(val_probs, axis=1).mean()

        print(
            f"Epoch {epoch + 1}/{num_epochs} | "
            f"Train Loss: {train_loss:.4f} Acc: {train_acc:.4f} | "
            f"Val Loss: {val_loss:.4f} Acc: {val_acc:.4f} | "
            f"Avg Conf: {avg_conf:.4f}"
        )

        # Save best model (based on validation loss, not accuracy)
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            best_val_acc = val_acc
            torch.save({
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'val_loss': val_loss,
                'val_acc': val_acc,
                'epoch': epoch,
                'class_to_idx': class_to_idx,
            }, save_path)
            print(f"  -> Best model saved (val_loss: {val_loss:.4f}, val_acc: {val_acc:.4f})")

        # Early stopping check
        early_stopping(val_loss)
        if early_stopping.early_stop:
            print(f"Early stopping triggered at epoch {epoch + 1}")
            break

    print(f"\nTraining complete.")
    print(f"Best validation loss: {best_val_loss:.4f}")
    print(f"Best validation accuracy: {best_val_acc:.4f}")
    print(f"Model saved to {save_path}")

    return model


if __name__ == '__main__':
    default_data_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '../../oral-cancer/Oral Cancer Dataset')
    )
    data_dir = os.environ.get("DATA_DIR", default_data_dir)

    if os.path.exists(data_dir):
        train_model(
            data_dir,
            num_epochs=30,
            batch_size=16,
            learning_rate=0.0001,
            use_focal_loss=True,
            use_mixup=True,
            use_label_smoothing=False,  # Don't combine with focal loss
            dropout_rate=0.5,
        )
    else:
        print(f"Dataset directory not found at {data_dir}. Please set DATA_DIR.")
