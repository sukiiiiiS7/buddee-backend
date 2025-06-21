"""
Leaf Classifier Final Trainer (All Data)
Author: S7
Last Updated: 2025-05-30

Trains final ResNet18 model using all available labeled data.
Uses data augmentation and tuned hyperparameters for highest accuracy.

Output: Saves final model to 'leaf_classifier_final.pth'
"""

import os
import torch
from torch import nn, optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms, models

# Data augmentation pipeline
transform = transforms.Compose([
    transforms.Resize((128, 128)),
    transforms.RandomHorizontalFlip(),
    transforms.RandomRotation(25),
    transforms.ColorJitter(brightness=0.3, contrast=0.3, saturation=0.3),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225])
])

# Load entire dataset
train_dir = "leaf_dataset"
dataset = datasets.ImageFolder(train_dir, transform=transform)
dataloader = DataLoader(dataset, batch_size=16, shuffle=True)

# Load ResNet18
model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
model.fc = nn.Linear(model.fc.in_features, 2)

# Training setup
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.0003, weight_decay=1e-4)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = model.to(device)

# Train full model
num_epochs = 15
for epoch in range(num_epochs):
    model.train()
    running_loss = 0.0
    correct = 0
    total = 0

    for images, labels in dataloader:
        images, labels = images.to(device), labels.to(device)
        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        running_loss += loss.item()
        _, predicted = torch.max(outputs.data, 1)
        total += labels.size(0)
        correct += (predicted == labels).sum().item()

    epoch_loss = running_loss / len(dataloader)
    epoch_acc = 100 * correct / total
    print(f"Epoch {epoch+1}/{num_epochs} - Loss: {epoch_loss:.4f} - Train Accuracy: {epoch_acc:.2f}%")

# Save final model
torch.save(model.state_dict(), "leaf_classifier_final.pth")
print("Final model saved as 'leaf_classifier_final.pth'")