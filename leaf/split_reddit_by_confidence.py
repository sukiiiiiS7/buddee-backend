"""
Reddit Predictions Confidence Splitter
Author: S7
Last Updated: 2025-05-30

Reads 'reddit_predictions.json' and creates:
- 'reddit_pseudo_labeled.json': confident predictions (confidence ≥ 0.95)
- 'reddit_low_confidence.json': uncertain predictions (confidence ≤ 0.7)
"""

import json

# Load the full prediction results
with open("reddit_predictions.json", "r") as f:
    data = json.load(f)

# Thresholds
HIGH_CONFIDENCE = 0.95
LOW_CONFIDENCE = 0.7

# Output lists
high_conf = []
low_conf = []

# Classify based on confidence
for item in data:
    confidence = item.get("confidence", 0)
    if confidence >= HIGH_CONFIDENCE:
        high_conf.append(item)
    elif confidence <= LOW_CONFIDENCE:
        low_conf.append(item)

# Save pseudo-labeled high confidence images
with open("reddit_pseudo_labeled.json", "w") as f:
    json.dump(high_conf, f, indent=2)

# Save low confidence uncertain predictions
with open("reddit_low_confidence.json", "w") as f:
    json.dump(low_conf, f, indent=2)

# Summary output
print(f"Saved {len(high_conf)} pseudo-labeled images to 'reddit_pseudo_labeled.json'")
print(f"Saved {len(low_conf)} low-confidence predictions to 'reddit_low_confidence.json'")
