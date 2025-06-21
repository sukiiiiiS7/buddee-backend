"""
Leaf Classification Evaluation Script
Author: S7
Last Updated: 2025-05-30

This script compares model predictions (reddit_predictions.json)
with human-annotated labels (reddit_manual_labels_template.json),
calculates performance metrics, and generates a confusion matrix image.
"""

import json
from sklearn.metrics import classification_report, confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

with open("reddit_manual_labels_template.json", "r", encoding="utf-8") as f:
    manual_labels = json.load(f)

with open("reddit_predictions.json", "r", encoding="utf-8") as f:
    predictions = json.load(f)

# Convert predictions to dictionary for quick lookup
pred_dict = {item["filename"]: item["prediction"] for item in predictions}

# Extract matching data 
true_labels = []
pred_labels = []
unmatched = []

for item in manual_labels:
    fname = item["filename"]
    label = item["manual_label"].lower()
    if label not in ["healthy", "wilted"]:
        continue  # Skip uncertain or unfilled entries

    if fname in pred_dict:
        true_labels.append(label)
        pred_labels.append(pred_dict[fname])
    else:
        unmatched.append(fname)

# Classification report
report = classification_report(true_labels, pred_labels, output_dict=True)
report_df = pd.DataFrame(report).transpose()
print("\nClassification Report:")
print(report_df)

# Save report as CSV 
report_df.to_csv("leaf_model_metrics.csv", index=True)

# Confusion matrix 
cm = confusion_matrix(true_labels, pred_labels, labels=["healthy", "wilted"])
plt.figure(figsize=(6, 5))
sns.heatmap(cm, annot=True, fmt="d", cmap="Greens", xticklabels=["healthy", "wilted"], yticklabels=["healthy", "wilted"])
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.title("Confusion Matrix — Leaf Classifier")
plt.tight_layout()
plt.savefig("confusion_matrix_leaf.png")
plt.close()

# Optional: list unmatched files 
if unmatched:
    print("\nUnmatched filenames (in labels but not in predictions):")
    for u in unmatched:
        print("-", u)
