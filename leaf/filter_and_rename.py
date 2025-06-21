import os
import json
from PIL import Image
import torch
import clip
from torchvision import transforms
from tqdm import tqdm

# Check device
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {device}")

# Load CLIP model and preprocessing function
model, preprocess = clip.load("ViT-B/32", device=device)

# Define semantic classes for classification
class_names = [
    "a close-up photo of a healthy green leaf on a plant",
    "a close-up photo of a diseased plant leaf",
    "a poster or infographic about gardening",
    "an avatar or cartoon headshot"
]

# Encode the text descriptions
text_inputs = torch.cat([clip.tokenize(desc) for desc in class_names]).to(device)

# Input and output folders
input_dir = "leaf_samples"
output_dir = "leaf_cleaned_ai"
review_dir = "leaf_review_needed"
os.makedirs(output_dir, exist_ok=True)
os.makedirs(review_dir, exist_ok=True)

# Prepare logging list
results = []
idx = 1

# Sort files for consistency
file_list = sorted(os.listdir(input_dir))

# Loop through all image files
for filename in tqdm(file_list, desc="Filtering"):
    filepath = os.path.join(input_dir, filename)

    try:
        # Load and preprocess image
        image = Image.open(filepath).convert("RGB")
        image_input = preprocess(image).unsqueeze(0).to(device)

        # Run CLIP model to compare with text
        with torch.no_grad():
            image_features = model.encode_image(image_input)
            image_features /= image_features.norm(dim=-1, keepdim=True)

            text_features = model.encode_text(text_inputs)
            text_features /= text_features.norm(dim=-1, keepdim=True)

            probs = (100.0 * image_features @ text_features.T).softmax(dim=-1).squeeze()

        # Get top prediction
        top_class = int(probs.argmax())
        top_prob = float(probs[top_class])

        result = {
            "original_filename": filename,
            "top_class_index": top_class,
            "top_class_name": class_names[top_class],
            "confidence": top_prob,
        }

        # Save only if the top prediction is leaf-related and high confidence
        if top_class in [0, 1] and top_prob >= 0.60:
            new_name = f"leaf_{idx:03}.jpg"
            save_path = os.path.join(output_dir, new_name)
            image.save(save_path, "JPEG")
            result["saved_as"] = new_name
            idx += 1
        else:
            # Send low-confidence or non-leaf images to review folder
            review_path = os.path.join(review_dir, filename)
            image.save(review_path, "JPEG")
            result["saved_as"] = None

        # Append result to log
        results.append(result)

    except Exception as e:
        print(f"Error processing {filename}: {e}")

# Save results to JSON
log_path = os.path.join(output_dir, "filter_log.json")
with open(log_path, "w") as f:
    json.dump(results, f, indent=2)

print(f"\nDone! {idx-1} leaf images saved to '{output_dir}'")
