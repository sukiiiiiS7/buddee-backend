"""
Final Training Script with Augmented Leaf Dataset
Author: S7
Last Updated: 2025-05-30

Trains a ResNet18 classifier on leaf_dataset/
Includes Reddit high-confidence pseudo-labeled images.
Saves the final model as 'leaf_classifier_final_augmented.pth'.
"""

import os
import torch
import torchvision
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms, models
from torch.utils.data import DataLoader
from sklearn.model_selection import train_test_split

# Config
data_dir = "leaf_dataset"
model_path = "leaf_classifier_final_augmented.pth"
batch_size = 32
epochs = 15
lr = 0.0005

# Transforms
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
])

# Load dataset
full_dataset = datasets.ImageFolder(data_dir, transform=transform)
class_names = full_dataset.classes

# Train/val split
indices = list(range(len(full_dataset)))
train_idx, val_idx = train_test_split(indices, test_size=0.2, random_state=42, shuffle=True)

train_sampler = torch.utils.data.SubsetRandomSampler(train_idx)
val_sampler = torch.utils.data.SubsetRandomSampler(val_idx)

train_loader = DataLoader(full_dataset, batch_size=batch_size, sampler=train_sampler)
val_loader = DataLoader(full_dataset, batch_size=batch_size, sampler=val_sampler)

# Model
model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
model.fc = nn.Linear(model.fc.in_features, 2)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = model.to(device)

# Optimizer & Loss
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=lr)

# Training
for epoch in range(epochs):
    model.train()
    correct = 0
    total = 0
    total_loss = 0.0

    for imgs, labels in train_loader:
        imgs, labels = imgs.to(device), labels.to(device)

        optimizer.zero_grad()
        outputs = model(imgs)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        total_loss += loss.item()
        _, predicted = torch.max(outputs.data, 1)
        total += labels.size(0)
        correct += (predicted == labels).sum().item()

    train_acc = 100 * correct / total

    # Validation
    model.eval()
    val_correct = 0
    val_total = 0
    with torch.no_grad():
        for imgs, labels in val_loader:
            imgs, labels = imgs.to(device), labels.to(device)
            outputs = model(imgs)
            _, predicted = torch.max(outputs.data, 1)
            val_total += labels.size(0)
            val_correct += (predicted == labels).sum().item()

    val_acc = 100 * val_correct / val_total
    print(f"Epoch {epoch+1}/{epochs} - Loss: {total_loss:.4f} - Train Accuracy: {train_acc:.2f}% - Val Accuracy: {val_acc:.2f}%")

# Save model
torch.save(model.state_dict(), model_path)
print(f"Final model saved as '{model_path}'")
