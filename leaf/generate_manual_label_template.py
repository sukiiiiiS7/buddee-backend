import os
import json
import random

image_folder = "leaf_cleaned_ai"
# Get all image files (JPG or PNG)
all_images = [f for f in os.listdir(image_folder) if f.lower().endswith(('.jpg', '.png'))]
# Randomly select 30 images for manual labeling
selected_images = random.sample(all_images, 30)
# Create a list of dictionaries with empty label fields
manual_labels = [{"filename": fname, "manual_label": ""} for fname in selected_images]

# Save the template to a JSON file
output_path = "reddit_manual_labels_template.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(manual_labels, f, indent=2)

print(f"Manual labeling template saved to: {output_path}")
