"""User Profile Manager for Grow AI
--------------------------------------
Author: S7
Last Updated: 2025-05-23

This module connects to a MongoDB Atlas cluster and provides basic operations
to manage user profiles in the Grow AI project. Each user is uniquely identified
by a `user_id` and can store customized plant preferences and dream history metadata.
Update:
- Added support for `avatar_url` (user profile picture)
- Added `neighbors` list to simulate plant neighborhood relationships

"""

from pymongo import MongoClient
from dotenv import load_dotenv
from pathlib import Path
import os

# Load MongoDB credentials from local .env_user file
env_path = Path(__file__).parent / ".env_user"
load_dotenv(dotenv_path=env_path)

# Establish connection
MONGO_URI = os.getenv("MONGODB_URI")
client = MongoClient(MONGO_URI)
db = client["user_data"]
collection = db["users"]

def add_user(user_data: dict):
    """Insert a new user document into the collection."""
    result = collection.insert_one(user_data)
    return str(result.inserted_id)

def get_user(user_id: str):
    """Retrieve a user profile based on their user_id."""
    return collection.find_one({"user_id": user_id})

def update_user(user_id: str, updates: dict):
    """Update fields in a user profile using partial field updates."""
    result = collection.update_one({"user_id": user_id}, {"$set": updates})
    return result.modified_count

def delete_user(user_id: str):
    """Delete a user profile permanently from the database."""
    result = collection.delete_one({"user_id": user_id})
    return result.deleted_count

def list_users():
    """Return a list of all user profiles without MongoDB _id field."""
    return list(collection.find({}, {"_id": 0}))
def get_user_plants(user_id: str):
    """Return a list of all plant profiles owned by a user."""
    user = collection.find_one({"user_id": user_id}, {"_id": 0, "plants": 1})
    return user.get("plants", []) if user else []

if __name__ == "__main__":
    sample_user = {
        "user_id": "S7test",
        "name": "Siqi",
        "location": {
            "lat": 51.5074,
            "lon": -0.1278
        },

        "avatar_url": "https://example.com/avatar_s7.png",
        "neighbors": ["plant_001", "plant_002"],
        "plant_preference": {
            "likes_bright_light": True,
            "needs_frequent_water": False
        },
        "dream_log_count": 0,
        "plants": [
            {
                "plant_id": "plant_01",
                "plant_type": "fern",
                "water_days": 3,
                "health_score": 85,
                "likes_bright_light": True,
                "needs_frequent_water": False
            },
            {
                "plant_id": "plant_02",
                "plant_type": "cactus",
                "water_days": 6,
                "health_score": 91,
                "likes_bright_light": True,
                "needs_frequent_water": False
            }
        ]
    }

    deleted = collection.delete_many({"user_id": "S7test"}).deleted_count
    print(f"[CLEANUP] Deleted {deleted} copies of user 'S7test'")

    user_id = add_user(sample_user)
    print(f"[INSERT] Inserted cleaned user 'S7test' with _id: {user_id}")

    print("All current users in the database:")
    for user in list_users():
        print(user)
    update_count = update_user("S7test", {
    "location": {
        "lat": 51.5074,
        "lon": -0.1278
    }
})

    print(f"[UPDATE] Set location for 'S7test' → modified count: {update_count}")
