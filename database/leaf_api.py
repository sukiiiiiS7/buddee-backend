from fastapi import APIRouter, UploadFile, File, Form, Path
from fastapi.responses import JSONResponse
from typing import Dict
from io import BytesIO
from PIL import Image
import torch
import torchvision.transforms as transforms
from torchvision.models import resnet18
import sys
import os
import numpy as np
from datetime import datetime, timedelta


# Import score computation and environment bonus logic
from leaf.scoring.health_score import calculate_health_score
from leaf.scoring.env_bonus import calculate_environment_bonus
from leaf.predictor.watering_model import predict_watering_days
from database.user_db_manager import get_user
from leaf.weather_module import should_delay_watering


MODEL_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "leaf", "leaf_classifier_final_augmented.pth")
)
# Initialize FastAPI router
router = APIRouter(prefix="/leaf", tags=["Leaf Scan"])

from torchvision import models

# Initialize ResNet18 model (no pretrained weights)
model = resnet18(weights=None)
model.fc = torch.nn.Linear(model.fc.in_features, 2)


# Adjust the final layer for 2-class classification
model.fc = torch.nn.Linear(model.fc.in_features, 2)

# Load the state_dict (weights only)
state_dict = torch.load(MODEL_PATH, map_location=torch.device("cpu"))
model.load_state_dict(state_dict)

# Set to evaluation mode
model.eval()


# Define image preprocessing pipeline (must match training)
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225])
])

# Index-to-label mapping (based on training classes)
idx_to_label = {
    0: "healthy",
    1: "wilted"
}
def extract_leaf_features(img: Image.Image) -> dict:
    """
    Analyze leaf image and extract basic visual features.
    Returns features in the format required by calculate_leaf_score.
    """
    np_img = np.array(img)

    # Convert to HSV for better color segmentation
    hsv = np.array(img.convert("HSV"))

    # --- Color Features ---
    yellow_mask = ((hsv[:, :, 0] >= 20) & (hsv[:, :, 0] <= 40)) & (hsv[:, :, 1] > 50)
    brown_mask = ((hsv[:, :, 0] >= 10) & (hsv[:, :, 0] <= 20)) & (hsv[:, :, 1] > 30)

    yellow_ratio = yellow_mask.sum() / (np_img.shape[0] * np_img.shape[1])
    brown_pixels = brown_mask.sum()

    # --- Shape Features (dummy logic, improve later) ---
    irregularity = 0.3  # Fixed for now
    holes_detected = False  # Not implemented yet

    return {
        "color": {
            "yellow_ratio": round(float(yellow_ratio), 2),
            "brown": int(brown_pixels)
        },
        "shape": {
            "irregularity": irregularity,
            "holes_detected": holes_detected
        }
    }
@router.post("/scan", summary="Scan Leaf Health", description="Upload a leaf image and optional environment data to analyze plant health.")
async def scan_leaf(
    image: UploadFile = File(..., description="Leaf image (.jpg/.png)"),
    light_level: float = Form(50.0, description="Light level (0–100, optional)"),
    soil_moisture: float = Form(50.0, description="Soil moisture (0–100, optional)"),
    user_id: str = Form(..., description="User ID to fetch watering preference and location")
):

    
    """
Main API endpoint: Analyzes the uploaded leaf image and optional environment data,
then returns a comprehensive health report including visual and environmental insights.

Parameters:
- image (UploadFile): Leaf image file (.jpg/.png)
- light_level (float): Ambient light level (0–100), default = 50
- soil_moisture (float): Soil moisture level (0–100), default = 50

Returns (JSON):
- health_score (int): Overall plant health score (0–100)
- label (str): Leaf condition classified as "healthy" or "wilted"
- explanation (str): Summary of environmental analysis (e.g., "Light is sufficient.")
- recommendations (str): Care suggestions based on image + environment analysis,
  including watering interval prediction (e.g., "Water every 3 days.")
- components (dict):
    - image_score (int): Score from visual features (e.g., yellowing, damage)
    - env_bonus (int): Environmental adjustment (range: –10 to +10)
"""

    try:
        # 1. Read and open image
        contents = await image.read()
        img = Image.open(BytesIO(contents)).convert("RGB")

        # 2. Preprocess and predict with model
        input_tensor = transform(img).unsqueeze(0)
        with torch.no_grad():
            output = model(input_tensor)
            probs = torch.nn.functional.softmax(output[0], dim=0)
            confidence, pred_idx = torch.max(probs, dim=0)
            label = idx_to_label[int(pred_idx)]

        # 3. Score environment based on inputs
        env_bonus, env_comments = calculate_environment_bonus(soil_moisture, light_level)

        # 4. Compute final health score and suggestions
        leaf_features = extract_leaf_features(img)

        result = calculate_health_score(
            leaf_features=leaf_features,
            soil_moisture=soil_moisture,
            light_level=light_level
        )
        # 5. Predict watering interval using the trained model
        watering_days = predict_watering_days(light_level, soil_moisture)
        # Adjust watering_days based on plant-level needs
        def adjust_by_plant_needs(user_id: str, watering_days: int) -> tuple[int, str]:
            user = get_user(user_id)
            plants = user.get("plants", []) if user else []

            # Count how many plants prefer frequent watering
            frequent = sum(p.get("needs_frequent_water", False) for p in plants)
            total = len(plants)
            style_note = ""

            if total == 0:
                return watering_days, style_note  # No plants, no adjustment

            ratio = frequent / total
            if ratio >= 0.6:
                watering_days = max(1, watering_days - 1)
                style_note = "Most of your plants prefer frequent watering, so the interval was shortened."
            elif ratio <= 0.4:
                watering_days += 1
                style_note = "Most of your plants prefer sparse watering, so the interval was extended."

            return watering_days, style_note


        watering_days, style_note = adjust_by_plant_needs(user_id, watering_days)
        result["watering_days"] = watering_days
        result["suggestion"] = f"Suggested watering interval: every {watering_days} day(s)"
        # 5.5 Optional: Delay watering due to upcoming rain
        from leaf.weather_module import should_delay_watering

        user = get_user(user_id)
        weather_note = ""
        if user and "location" in user:
            coords = user["location"]
            lat = coords.get("lat")
            lon = coords.get("lon")
            if lat is not None and lon is not None:
                delay_due_to_weather = should_delay_watering(lat, lon)
                if delay_due_to_weather:
                    watering_days += 1
                    weather_note = "Rain is expected soon. Watering has been delayed by one day."


        # 6. Merge image-based recommendations with watering prediction
        image_recommendation = " ".join(result["recommendations"]).rstrip(".")
        final_notes = ". ".join(filter(None, [style_note, weather_note]))

        merged_reco = (
            f"{image_recommendation}. {final_notes} "
            f"Considering current environmental conditions (light: {light_level}, moisture: {soil_moisture}), "
            f"we recommend watering approximately every {watering_days} day(s)."
        )




        # 7. Replace old recommendation + remove separate field
        result["recommendations"] = merged_reco
        result.pop("suggestion", None)
        result.pop("watering_days", None)
        result["label"] = label

        return result

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@router.get("/next_watering/{user_id}", summary="Predict Next Watering Date")
async def get_next_watering(user_id: str):
    """
    Returns the estimated next watering date for a user, considering environment and plant preference.
    """

    try:
        user = get_user(user_id)
        if not user:
            return JSONResponse(status_code=404, content={"error": "User not found."})


        light_level = 50.0
        soil_moisture = 50.0


        watering_days = predict_watering_days(light_level, soil_moisture)

        def adjust_by_plant_needs(user_id: str, watering_days: int) -> tuple[int, str]:
            user = get_user(user_id)
            plants = user.get("plants", []) if user else []
            frequent = sum(p.get("needs_frequent_water", False) for p in plants)
            total = len(plants)
            style_note = ""

            if total == 0:
                return watering_days, style_note

            ratio = frequent / total
            if ratio >= 0.6:
                watering_days = max(1, watering_days - 1)
            elif ratio <= 0.4:
                watering_days += 1

            return watering_days, style_note

        watering_days, _ = adjust_by_plant_needs(user_id, watering_days)

        from leaf.weather_module import should_delay_watering
        if "location" in user:
            coords = user["location"]
            lat = coords.get("lat")
            lon = coords.get("lon")
            if lat is not None and lon is not None:
                delay_due_to_weather = should_delay_watering(lat, lon)
                if delay_due_to_weather:
                    watering_days += 1

        next_date = datetime.today() + timedelta(days=watering_days)

        return {
            "user_id": user_id,
            "predicted_next_watering_date": next_date.strftime("%Y-%m-%d"),
            "days_until_next_watering": watering_days
        }

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
