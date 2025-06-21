"""
Augment Leaf Dataset with Reddit Pseudo-Labeled Images
Author: S7
Last Updated: 2025-05-30

Reads 'reddit_pseudo_labeled.json' and copies images into
leaf_dataset/healthy/ or leaf_dataset/wilted/ based on predicted labels.
"""

import os
import shutil
import json

# JSON path and folders
json_path = "reddit_pseudo_labeled.json"
source_folder = "leaf_cleaned_ai"
target_base = "leaf_dataset"

# Ensure target subfolders exist
os.makedirs(os.path.join(target_base, "healthy"), exist_ok=True)
os.makedirs(os.path.join(target_base, "wilted"), exist_ok=True)

# Load JSON
with open(json_path, "r") as f:
    records = json.load(f)

# Copy images based on prediction
for record in records:
    filename = record["filename"]
    label = record["prediction"]  # "healthy" or "wilted"

    src = os.path.join(source_folder, filename)
    dst = os.path.join(target_base, label, filename)

    if os.path.exists(src):
        shutil.copy2(src, dst)
        print(f"Copied: {filename} → {label}/")
    else:
        print(f"[WARN] Missing file: {filename}")
