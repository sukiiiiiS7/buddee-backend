"""
Dream Record Generator with User Integration & Schema Compliance  
--------------------------------------------------------------------
Author: S7  
Last Updated: 2025-05-28

This script processes soil moisture records and merges them with light sensor data.
It uses a trained ML model to classify each record into a dream_type, maps a mood_tag,
and dynamically injects user-specific settings from MongoDB Atlas based on the selected user_id.

Features:
- Loads user_id from .env_user file (supports multi-user switching)
- Predicts dream_type using pre-trained model
- Merges timestamps using merge_asof (1min tolerance)
- Injects user profile info: plant_type, water_days, health_score
- Adds user preferences: likes_bright_light, needs_frequent_water
- Auto-generates dream_stamp_id (e.g., #SUN-003)
- Outputs schema-compliant JSON for frontend rendering

To Do (Future):
- Add dream_dialogue generation (template or GPT)
- Link plant_type to visual theme customization
- Connect health_score to image-based diagnostics
"""


import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "database")))
from user_db_manager import get_user, get_user_plants
from dialogue_utils import make_dialogue

import pandas as pd
import joblib
from datetime import datetime
from dotenv import load_dotenv
import json
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "leaf", "scoring")))
from health_score import calculate_health_score


# Load MongoDB URI and USER_ID (supports cross-directory)
load_dotenv(dotenv_path=os.path.join("user", ".env_user"))

user_id = os.getenv("USER_ID", "S7test")  # Set the default fallback to S7test.

user_info = get_user(user_id) or {}
plant_ids = get_user_plants(user_id)
print(f"[INFO] Found plant_ids: {plant_ids}")

print(f"[INFO] Using user_id: {user_id}")
print(f"[INFO] Loaded user info: {user_info}")


# Load data
dream_df = pd.read_json("dream_record_log_real.json")
light_df = pd.read_json("light_data_backup.json")
model = joblib.load("dream_model.pkl")

# Prepare timestamps (no timezone, floor to minute)
dream_df["timestamp"] = pd.to_datetime(dream_df["timestamp"]).dt.tz_localize(None).dt.floor("min")
light_df["timestamp"] = pd.to_datetime(light_df["timestamp"]).dt.tz_localize(None).dt.floor("min")

# Sort before merge_asof
dream_df = dream_df.sort_values("timestamp")
light_df = light_df.sort_values("timestamp")

# Merge using merge_asof with tolerance
merged_df = pd.merge_asof(
    dream_df,
    light_df,
    on="timestamp",
    direction="nearest",
    tolerance=pd.Timedelta("1min")
)

# Rename and normalize light_level
merged_df.rename(columns={"lux": "light_level"}, inplace=True)
max_lux = 1000
merged_df["light_level"] = (merged_df["light_level"] / max_lux * 100).clip(0, 100).round(2)

# Sort and set timestamp as index
merged_df = merged_df.sort_values("timestamp").set_index("timestamp")

# Fill NaN with 3-minute rolling average (based on timestamp)
rolling_filled = merged_df["light_level"].rolling("3min", min_periods=1).mean()
merged_df["light_level"] = merged_df["light_level"].fillna(rolling_filled)

# Final fallback for edge cases (if any NaN remains)
merged_df["light_level"] = merged_df["light_level"].fillna(50.0)

# Reset index to restore timestamp as column
merged_df = merged_df.reset_index()

# Device ID to Plant ID mapping
device_to_plant = {
    "ESP32-06": "plant_01",
    "ESP32-08": "plant_02"
}

merged_df["plant_id"] = dream_df["device_id"].map(device_to_plant)

# Extract preferences early for reuse
pref = user_info.get("plant_preference", {})

# Inject per-plant parameters into merged_df
plant_profile_map = {p["plant_id"]: p for p in plant_ids}

merged_df["plant_type"] = merged_df["plant_id"].map(lambda pid: plant_profile_map.get(pid, {}).get("plant_type"))
merged_df["water_days"] = merged_df["plant_id"].map(lambda pid: plant_profile_map.get(pid, {}).get("water_days"))
merged_df["health_score"] = merged_df["plant_id"].map(lambda pid: plant_profile_map.get(pid, {}).get("health_score"))

# Optional: override preferences if defined per plant
merged_df["likes_bright_light"] = merged_df["plant_id"].map(
    lambda pid: plant_profile_map.get(pid, {}).get("likes_bright_light", pref.get("likes_bright_light", False))
)
merged_df["needs_frequent_water"] = merged_df["plant_id"].map(
    lambda pid: plant_profile_map.get(pid, {}).get("needs_frequent_water", pref.get("needs_frequent_water", False))
)

unmapped = merged_df[merged_df["plant_id"].isna()]
if not unmapped.empty:
    print("[WARNING] Unmapped device_id(s):", unmapped["device_id"].unique())

# -------- SENSOR VALIDATION --------
def classify_sensor_status(row):
    if pd.isna(row["avgMoisture"]):
        return "missing"
    elif row["avgMoisture"] == 0.146:
        return "invalid_fixed"
    elif row["avgMoisture"] >= 0.95:
        return "suspicious_high"
    else:
        return "valid"

merged_df["sensor_status"] = merged_df.apply(classify_sensor_status, axis=1)
merged_df["include_in_model"] = merged_df["sensor_status"] == "valid"

# Predict dream_type and ensure string mapping
valid_rows = merged_df[["avgMoisture", "light_level"]].dropna()
index_to_label = {0: "dry", 1: "sunny", 2: "misty", 3: "rainy"}
predicted_labels = model.predict(valid_rows).astype(int)
merged_df.loc[valid_rows.index, "dream_type"] = pd.Series(predicted_labels).map(index_to_label)

# Post-adjustment: shift dream_type based on user preference
def adjust_dream_type(row, preferences):
    light = row["light_level"]
    moisture = row["avgMoisture"]
    original = row["dream_type"]

    # Likes bright light but the light intensity is too low → Not suitable for sunny conditions.
    if preferences.get("likes_bright_light", False) and light < 30 and original == "sunny":
        return "misty"

    # Like to water frequently but the humidity is too low → directly dry
    if preferences.get("needs_frequent_water", False) and moisture < 0.4:
        return "dry"

    return original

# Apply preference-aware adjustment to dream_type
merged_df["dream_type"] = merged_df.apply(lambda row: adjust_dream_type(row, pref), axis=1)

# Map mood_tag
mood_map = {
    "dry": "sad",
    "sunny": "joyful",
    "misty": "dreamy",
    "rainy": "relieved"
}
merged_df["mood_tag"] = merged_df["dream_type"].map(mood_map)

# Add required fields with user profile injection
merged_df["user_id"] = user_id
# Apply health scoring per row
def score_row(row):
    image_score = 80  # Default image score, if image not processed
    env_bonus = 0

    try:
        # image_score is omitted here unless you want to expand to full vision model
        # just use env_bonus for now
        score_result = calculate_health_score(
            light_level=row["light_level"],
            moisture=row["avgMoisture"]
        )
        return score_result["health_score"]
    except:
        return None


merged_df["dream_dialogue"] = merged_df.apply(lambda row: make_dialogue(row)["text"], axis=1)


# Generate dream_stamp_id based on dream_type
prefix_map = {
    "sunny": "SUN",
    "dry": "DRY",
    "misty": "MIS",
    "rainy": "RAI"
}
merged_df = merged_df.reset_index(drop=True)
merged_df["dream_stamp_id"] = merged_df.apply(
    lambda row: f"#{prefix_map.get(row['dream_type'], 'UNK')}-{str(row.name + 1).zfill(3)}", axis=1
)

# Format timestamp
merged_df["timestamp"] = merged_df["timestamp"].dt.strftime("%Y-%m-%dT%H:%M:%S")

# Final output fields including avgMoisture
ordered_cols = [
    "user_id", "plant_id", "plant_type", "water_days", "light_level", "avgMoisture", "health_score",
    "dream_type", "mood_tag", "dream_stamp_id", "dream_dialogue", "timestamp", "source",
    "sensor_status", "include_in_model", "needs_frequent_water", "likes_bright_light"
]
output_records = []

# Export the final DataFrame with selected columns to JSON
merged_df = merged_df[merged_df["include_in_model"] == True]
final_df = merged_df[ordered_cols]

with open("dream_record_log_labeled.json", "w", encoding="utf-8") as f:
    json.dump(final_df.to_dict(orient="records"), f, indent=2, ensure_ascii=False)

print(f"[INFO] Successfully generated {len(final_df)} dream records with plant_id mapping.")

if len(valid_rows.index) != len(predicted_labels):
    print("[WARNING] Number of predictions doesn't match input rows!")
