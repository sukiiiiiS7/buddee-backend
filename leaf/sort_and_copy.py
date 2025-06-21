"""
Batch Image Sorter and Copier for Leaf Classification
Author: S7
Last Updated: 2025-05-30

This script copies high-confidence Reddit leaf images from 'leaf_cleaned_ai/' into
'classified_output/[healthy|wilted]/' folders, based on predictions in 'reddit_pseudo_labeled.json'.

Useful for:
- Visual inspection of model predictions
- Preparing folders for presentation or frontend UI
- Creating quick training folders for further fine-tuning
"""

import os
import shutil
import json

# Config paths 
source_folder = "leaf_cleaned_ai"          # Original Reddit images
output_base = "classified_output"          # Output folder with healthy/wilted subfolders
json_path = "reddit_pseudo_labeled.json"   # High-confidence prediction result

# Load JSON predictions
with open(json_path, "r", encoding="utf-8") as f:
    data = json.load(f)

# Create output structure and copy files
for item in data:
    fname = item["filename"]
    pred = item["prediction"]  # "healthy" or "wilted"

    src_path = os.path.join(source_folder, fname)
    dest_dir = os.path.join(output_base, pred)
    os.makedirs(dest_dir, exist_ok=True)

    try:
        shutil.copy(src_path, os.path.join(dest_dir, fname))
    except Exception as e:
        print(f"Failed to copy {fname}: {e}")

print("Done: High-confidence images have been sorted into classified_output/[label]/ folders.")
