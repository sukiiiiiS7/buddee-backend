import os
import json
import shutil

json_path = "high_conf_healthy_to_check.json"
reddit_image_folder = "leaf_cleaned_ai"  

target_folder = "leaf_dataset/healthy" 

with open(json_path, "r", encoding="utf-8") as f:
    data = json.load(f)

count = 0
for item in data:
    if item.get("manual_check") == "keep":
        src_path = os.path.join(reddit_image_folder, item["filename"])
        dst_path = os.path.join(target_folder, item["filename"])

        if os.path.exists(src_path):
            shutil.copy2(src_path, dst_path)
            count += 1
        else:
            print(f"File not found: {src_path}")

print(f"Copied {count} images to {target_folder}")
