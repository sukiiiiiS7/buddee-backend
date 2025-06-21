"""
Dream Record Logger to MongoDB (Upsert Mode)
Author: S7
Last Updated: 2025-05-25

Reads 'dream_record_log_labeled.json' and writes to dream_logs collection.
Updates existing records if dream_stamp_id matches, otherwise inserts new ones.
"""

import json
from pymongo import MongoClient
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import os

# Load MongoDB credentials from local .env_user file
env_path = Path(__file__).parent / ".env_user"
load_dotenv(dotenv_path=env_path)

# connect to MongoDB
MONGO_URI = os.getenv("MONGODB_URI")
client = MongoClient(MONGO_URI)
db = client["GrowAI"]
collection = db["dream_logs"]

# load json from ../dream_record_log_labeled.json
json_path = Path(__file__).parent.parent / "dream_record_log_labeled.json"
with open(json_path, "r", encoding="utf-8") as file:
    dream_data = json.load(file)

# write each record (update if exists)
for record in dream_data:
    if isinstance(record.get("timestamp"), str):
        try:
            record["timestamp"] = datetime.fromisoformat(record["timestamp"])
        except Exception:
            pass

    result = collection.update_one(
        {"dream_stamp_id": record["dream_stamp_id"]},
        {"$set": record},
        upsert=True
    )

    if result.matched_count:
        print(f"Updated: {record['dream_stamp_id']}")
    else:
        print(f"Inserted: {record['dream_stamp_id']}")

print("Done writing dream logs to MongoDB.")
