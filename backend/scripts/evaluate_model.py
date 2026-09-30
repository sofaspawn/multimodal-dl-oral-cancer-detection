"""
Model evaluation and calibration script.

This script helps diagnose false positive issues by:
1. Testing the model on a validation set
2. Analyzing per-class performance
3. Checking calibration (confidence vs accuracy)
4. Testing on out-of-distribution images
"""

import os
import sys
import torch
import torch.nn.functional as F
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
import numpy as np
from sklearn.metrics import confusion_matrix, classification_report, roc_auc_score
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.ml.model import load_model
from app.ml.inference import predict_image, get_inference_model


def evaluate_on_dataset(model, data_loader, device):
    """Evaluate model on a dataset and return metrics."""
    model.eval()

    all_preds = []
    all_labels = []
    all_probs = []
    all_confidences = []

    with torch.no_grad():
        for inputs, labels in data_loader:
            inputs, labels = inputs.to(device), labels.to(device)
            outputs = model(inputs)
            probs = F.softmax(outputs, dim=1)
            confidences, preds = torch.max(probs, 1)

            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
            all_probs.extend(probs.cpu().numpy())
            all_confidences.extend(confidences.cpu().numpy())

    return np.array(all_preds), np.array(all_labels), np.array(all_probs), np.array(all_confidences)


def analyze_calibration(confidences, correct, num_bins=10):
    """Analyze model calibration - how well confidence matches accuracy."""
    bins = np.linspace(0, 1, num_bins + 1)
    bin_accs = []
    bin_confs = []
    bin_counts = []

    for i in range(num_bins):
        mask = (confidences >= bins[i]) & (confidences < bins[i + 1])
        if mask.sum() > 0:
            bin_accs.append(correct[mask].mean())
            bin_confs.append(confidences[mask].mean())
            bin_counts.append(mask.sum())
        else:
            bin_accs.append(0)
            bin_confs.append(0)
            bin_counts.append(0)

    # Expected Calibration Error (ECE)
    ece = sum(abs(acc - conf) * count for acc, conf, count in zip(bin_accs, bin_confs, bin_counts))
    ece /= sum(bin_counts) if sum(bin_counts) > 0 else 1

    return ece, bin_accs, bin_confs, bins


def plot_calibration_curve(bin_accs, bin_confs, bins, save_path):
    """Plot calibration curve."""
    plt.figure(figsize=(8, 6))
    plt.plot([0, 1], [0, 1], 'k--', label='Perfectly calibrated')
    plt.bar(bins[:-1], bin_accs, width=0.1, align='edge', alpha=0.5, label='Accuracy')
    plt.bar(bins[:-1], bin_confs, width=0.1, align='edge', alpha=0.3, label='Confidence')
    plt.xlabel('Confidence')
    plt.ylabel('Accuracy')
    plt.title('Calibration Curve')
    plt.legend()
    plt.savefig(save_path)
    plt.close()
    print(f"Calibration curve saved to {save_path}")


def test_random_images(model_path, random_image_dir, device):
    """Test model on random images from the internet to detect false positive rate."""
    print(f"\n{'='*60}")
    print("Testing on random images (out-of-distribution test)")
    print(f"{'='*60}")

    model = load_model(model_path=model_path, device=device)

    if not os.path.exists(random_image_dir):
        print(f"Directory not found: {random_image_dir}")
        print("Create a folder with random non-cancer images to test false positive rate.")
        return

    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ])

    cancer_count = 0
    non_cancer_count = 0
    total = 0
    confidences = []

    for filename in os.listdir(random_image_dir):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            image_path = os.path.join(random_image_dir, filename)
            try:
                result = predict_image(image_path)
                total += 1
                confidences.append(result.confidence)

                if result.label == "Cancer":
                    cancer_count += 1
                    print(f"  {filename}: Cancer ({result.confidence:.2%}) - FALSE POSITIVE")
                else:
                    non_cancer_count += 1
                    print(f"  {filename}: Non-Cancer ({result.confidence:.2%})")
            except Exception as e:
                print(f"  {filename}: Error - {e}")

    if total > 0:
        print(f"\nResults on {total} random images:")
        print(f"  False positives (Cancer predictions): {cancer_count}/{total} ({cancer_count/total*100:.1f}%)")
        print(f"  Non-Cancer predictions: {non_cancer_count}/{total} ({non_cancer_count/total*100:.1f}%)")
        print(f"  Average confidence: {np.mean(confidences):.2%}")


def main():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    # Paths
    model_path = os.path.join(os.path.dirname(__file__), '../app/ml/weights/resnet50_oral_cancer.pth')
    data_dir = os.environ.get("DATA_DIR", os.path.abspath(
        os.path.join(os.path.dirname(__file__), '../../oral-cancer/Oral Cancer Dataset')
    ))
    random_image_dir = os.path.join(os.path.dirname(__file__), 'random_test_images')

    # Load model
    model = load_model(model_path=model_path, device=device)

    # Validation transforms
    val_transforms = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ])

    if os.path.exists(data_dir):
        print(f"\n{'='*60}")
        print(f"Evaluating on validation set: {data_dir}")
        print(f"{'='*60}")

        # Load dataset
        dataset = datasets.ImageFolder(data_dir, transform=val_transforms)
        class_names = dataset.classes
        print(f"Classes: {class_names}")

        # Split
        total = len(dataset)
        val_size = int(total * 0.2)
        train_size = total - val_size
        _, val_dataset = torch.utils.data.random_split(dataset, [train_size, val_size])

        val_loader = DataLoader(val_dataset, batch_size=32, shuffle=False)

        # Evaluate
        preds, labels, probs, confidences = evaluate_on_dataset(model, val_loader, device)

        # Metrics
        print("\nClassification Report:")
        print(classification_report(labels, preds, target_names=class_names))

        print("\nConfusion Matrix:")
        cm = confusion_matrix(labels, preds)
        print(cm)

        # Per-class analysis
        for i, class_name in enumerate(class_names):
            mask = labels == i
            class_acc = (preds[mask] == i).mean() if mask.sum() > 0 else 0
            class_conf = confidences[mask].mean() if mask.sum() > 0 else 0
            print(f"\n{class_name}:")
            print(f"  Accuracy: {class_acc:.2%}")
            print(f"  Avg Confidence: {class_conf:.2%}")

        # Calibration analysis
        correct = (preds == labels)
        ece, bin_accs, bin_confs, bins = analyze_calibration(confidences, correct)
        print(f"\nExpected Calibration Error: {ece:.4f}")

        # Plot calibration
        plot_path = os.path.join(os.path.dirname(__file__), 'calibration_curve.png')
        plot_calibration_curve(bin_accs, bin_confs, bins, plot_path)

        # AUC-ROC (using cancer probability)
        if len(class_names) == 2:
            cancer_probs = probs[:, 1]  # Probability of cancer class
            auc = roc_auc_score(labels, cancer_probs)
            print(f"\nAUC-ROC: {auc:.4f}")

    # Test on random images
    test_random_images(model_path, random_image_dir, device)


if __name__ == '__main__':
    main()
