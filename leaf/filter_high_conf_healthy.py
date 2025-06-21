import json
import random

# Path to the prediction results file
input_file = "reddit_predictions.json"

# Output path for human verification list
output_file = "high_conf_healthy_to_check.json"

# Load the prediction results
with open(input_file, "r", encoding="utf-8") as f:
    predictions = json.load(f)

# Fix field name: use "prediction" instead of "predicted_label"
high_conf_healthy = [
    {
        "filename": item["filename"],
        "prediction": item["prediction"],
        "confidence": item["confidence"]
    }
    for item in predictions
    if item["prediction"] == "healthy" and item["confidence"] >= 0.98
]

# Shuffle the list to reduce visual bias
random.shuffle(high_conf_healthy)

# Limit to 20 samples for easier review
high_conf_healthy = high_conf_healthy[:20]

# Add manual check field for review: "keep" or "drop"
for item in high_conf_healthy:
    item["manual_check"] = ""

# Save to file
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(high_conf_healthy, f, indent=2)

print(f"Filtered {len(high_conf_healthy)} high-confidence 'healthy' samples.")
print(f"Manual check file saved to: {output_file}")
