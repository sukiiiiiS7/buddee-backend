# upload_dream_logs.py
"""
Upload Dream Logs to MongoDB Atlas
----------------------------------
Author: S7
Last Updated: 2025-05-28

This script reads a local dream_record_log_labeled.json file and
inserts the dream records into MongoDB under the `dream_logs` collection.

Assumes the file has been generated from export_dream_records.py.
"""

import json
from pymongo import MongoClient
from dotenv import load_dotenv
from pathlib import Path
import os

# Load environment variables from .env_user
env_path = Path(__file__).parent / ".env_user"
load_dotenv(dotenv_path=env_path)
MONGO_URI = os.getenv("MONGODB_URI")

client = MongoClient(MONGO_URI)
db = client["user_data"]
plant_log = db["plant_log"]

labeled_path = os.path.join(Path(__file__).parent.parent, "data", "dream_record_log_labeled.json")

if not os.path.exists(labeled_path):
    print(f"[ERROR] : {labeled_path}")
    exit()

with open(labeled_path, "r", encoding="utf-8") as f:
    dream_records = json.load(f)

inserted = 0
for record in dream_records:
    if record.get("dream_type"):  
        plant_log.insert_one(record)
        inserted += 1

print(f"[UPLOAD COMPLETE] Inserted {inserted} dream records to plant_log collection.")