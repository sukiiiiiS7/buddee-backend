# check_achievements.py
# Grow AI – Achievement Logic Checker
# Author: S7
# Last Updated: 2025-05-26
# This script checks unlocked achievements for a user,
# compares against config, and inserts new records into MongoDB.

from datetime import datetime, time
from pymongo import MongoClient
from database.achievement_config import ACHIEVEMENTS
from pathlib import Path
from dotenv import load_dotenv
import os

env_path = Path(__file__).parent / ".env_user"
load_dotenv(dotenv_path=env_path)

# Connect to MongoDB
MONGO_URI = os.getenv("MONGODB_URI")
client = MongoClient(MONGO_URI)

# Reference two databases
db_user = client["user_data"]
db_dream = client["GrowAI"]

# Access specific collections
achievement_collection = db_user["achievement_log"]
user_collection = db_user["users"]
dream_log_collection = db_dream["dream_logs"]

# Check if already unlocked
def has_achievement(user_id, achievement_id):
    return achievement_collection.count_documents({
        "user_id": user_id,
        "achievement_id": achievement_id
    }) > 0

# Unlock and write to MongoDB
def unlock(user_id, achievement_id):
    if has_achievement(user_id, achievement_id):
        return
    ach = next((a for a in ACHIEVEMENTS if a["id"] == achievement_id), None)
    if not ach:
        return
    achievement_collection.insert_one({
        "user_id": user_id,
        "achievement_id": achievement_id,
        "unlocked_at": datetime.utcnow(),
        "points": ach["points"]
    })
    user_collection.update_one(
        {"user_id": user_id},
        {"$inc": {"achievement_points": ach["points"]}},
        upsert=True
    )
    print(f"{user_id} unlocked: {ach['name']}")

# Core checker logic
def check_achievements(user_id):
    dreams = list(dream_log_collection.find({"user_id": user_id}))
    unread_count = sum(1 for d in dreams if d.get("read") is False)
    
    # DREAM_BEGINS
    if len(dreams) >= 1:
        unlock(user_id, "DREAM_BEGINS")

    # SILENT_READER
    if unread_count >= 3:
        unlock(user_id, "SILENT_READER")

    # STAYED_UP_LATE
    for d in dreams:
        ts = d.get("timestamp")
        if isinstance(ts, datetime):
            if time(1, 0) <= ts.time() <= time(4, 0):
                unlock(user_id, "STAYED_UP_LATE")
                break

    # GLITCH_GARDENER
    for d in dreams:
        if d.get("sensor_status") == "invalid_fixed":
            unlock(user_id, "GLITCH_GARDENER")
            break

    # MIST_DREAMER
    if any(d.get("dream_type") == "misty" for d in dreams):
        unlock(user_id, "MIST_DREAMER")

    # AVATAR_MASTER (from user collection)
    user = user_collection.find_one({"user_id": user_id})
    if user and user.get("avatar_count", 0) >= 5:
        unlock(user_id, "AVATAR_MASTER")

    # PIXEL_COLLECTOR (unlocked animated ones ≥ 3)
    unlocked = list(achievement_collection.find({"user_id": user_id}))
    animated_ids = [a["id"] for a in ACHIEVEMENTS if a["animate"]]
    unlocked_animated = [u for u in unlocked if u["achievement_id"] in animated_ids]
    if len(unlocked_animated) >= 3:
        unlock(user_id, "PIXEL_COLLECTOR")
