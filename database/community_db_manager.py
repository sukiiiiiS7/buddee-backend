"""
community_db_manager.py - Community features for Grow AI

Author: S7
Last Updated: 2025-05-23

Handles:
- plant activity logs (like watering, pruning)
- neighbor dream messages between plants
- system notifications for users
"""

from pymongo import MongoClient
from dotenv import load_dotenv
from pathlib import Path
import os
from datetime import datetime

# Load MongoDB connection info
env_path = Path(__file__).parent / ".env_user"
load_dotenv(dotenv_path=env_path)
MONGO_URI = os.getenv("MONGODB_URI")

# Connect to database
client = MongoClient(MONGO_URI)
db = client["user_data"]
plant_log_col = db["plant_log"]
chat_col = db["neighbor_chat_log"]
notif_col = db["notification_log"]

# Plant activity log 

def add_plant_log(user_id: str, plant_id: str, action: str, note: str = ""):
    """
    Record what the user did to a plant (e.g. watering, trimming).
    """
    log = {
        "user_id": user_id,
        "plant_id": plant_id,
        "action": action,
        "note": note,
        "timestamp": datetime.now().isoformat()
    }
    return plant_log_col.insert_one(log).inserted_id

# Dream messages between neighbor plants 

def add_dream_chat(from_plant_id: str, to_plant_id: str, dream_text: str, mood_tag: str = None):
    """
    Save a dream message from one plant to another.
    """
    chat = {
    "from_plant_id": from_plant_id,
    "to_plant_id": to_plant_id,
    "dream_text": dream_text,
    "mood_tag": mood_tag,
    "timestamp": datetime.now().isoformat()
}

    return chat_col.insert_one(chat).inserted_id

# User notifications 

def add_notification(user_id: str, message: str, notif_type: str = "info"):
    """
    Add a system notification for a user (e.g. new message, badge unlocked).
    """
    notif = {
        "user_id": user_id,
        "message": message,
        "type": notif_type,
        "read": False,
        "timestamp": datetime.now().isoformat()
    }
    return notif_col.insert_one(notif).inserted_id

def get_notifications(user_id: str):
    """
    Get all unread notifications for a user.
    """
    return list(notif_col.find({"user_id": user_id, "read": False}, {"_id": 0}))

def mark_notifications_read(user_id: str):
    """
    Mark all unread notifications as read.
    """
    result = notif_col.update_many(
        {"user_id": user_id, "read": False},
        {"$set": {"read": True}}
    )
    return result.modified_count
def count_unread_dreams(user_id: str):
    """
    Count how many unread dream-type notifications this user has.
    Used by frontend to decide whether to show a red dot.
    """
    return notif_col.count_documents({
        "user_id": user_id,
        "type": "dream",
        "read": False
    })

plant_profile_col = db["plant_profile"]

def get_plant_owner(plant_id: str):
    """
    Get the user_id who owns the given plant_id.
    """
    doc = plant_profile_col.find_one({"plant_id": plant_id})
    return doc["user_id"] if doc else None
