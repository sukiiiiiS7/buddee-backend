"""
Reddit Batch Prediction Script
Author: S7
Last Updated: 2025-05-30

Runs inference on all images in 'leaf_cleaned_ai/' using trained model.
Outputs results to 'reddit_predictions.json'.
"""

import torch
from torchvision import transforms, models
from PIL import Image
import os
import json

# Folder to analyze
image_folder = "leaf_cleaned_ai"
output_file = "reddit_predictions.json"

# Model setup
model = models.resnet18()
model.fc = torch.nn.Linear(model.fc.in_features, 2)
model.load_state_dict(torch.load("leaf_classifier_final.pth", map_location=torch.device("cpu")))
model.eval()

class_labels = ["healthy", "wilted"]

# Preprocessing transform
transform = transforms.Compose([
    transforms.Resize((128, 128)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225])
])

def predict_image(image_path):
    image = Image.open(image_path).convert("RGB")
    image_tensor = transform(image).unsqueeze(0)
    with torch.no_grad():
        outputs = model(image_tensor)
        probs = torch.nn.functional.softmax(outputs, dim=1)[0]
        confidence, predicted = torch.max(probs, 0)
    return {
        "filename": os.path.basename(image_path),
        "prediction": class_labels[predicted.item()],
        "confidence": round(confidence.item(), 3)
    }

# Run predictions
results = []
for filename in os.listdir(image_folder):
    if filename.lower().endswith(('.jpg', '.png')):
        path = os.path.join(image_folder, filename)
        try:
            result = predict_image(path)
            results.append(result)
        except Exception as e:
            print(f"Failed on {filename}: {e}")

# Save results
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2)

print(f"Batch prediction complete. Results saved to '{output_file}'")
