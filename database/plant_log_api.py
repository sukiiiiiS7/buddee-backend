from fastapi import APIRouter, HTTPException
from pymongo import MongoClient, ASCENDING
import os
from datetime import datetime

router = APIRouter()

client = MongoClient(os.getenv("MONGODB_URI"))
db = client["user_data"]
dream_logs = db["plant_log"]

@router.get("/get_plant_log/{plant_id}")
def get_plant_log(plant_id: str):
    cursor = dream_logs.find({"plant_id": plant_id}).sort("timestamp", -1)
    logs_by_date = {}

    for doc in cursor:
        ts = doc.get("timestamp")
        date_key = ts[:10] if isinstance(ts, str) else ts.strftime("%Y-%m-%d")

        entry = {
            "timestamp": ts,
            "dream_type": doc.get("dream_type"),
            "mood_tag": doc.get("mood_tag"),
            "dream_dialogue": doc.get("dream_dialogue"),
            "light_level": doc.get("light_level"),
            "avgMoisture": doc.get("avgMoisture"),
            "health_score": doc.get("health_score"),
            "water_days": doc.get("water_days")
        }

        logs_by_date.setdefault(date_key, []).append(entry)

    for date, logs in logs_by_date.items():
        seen = set()
        unique_logs = []
        for log in logs:
            key = (log["timestamp"], log["dream_type"], log["mood_tag"], log["dream_dialogue"])
            if key not in seen:
                seen.add(key)
                unique_logs.append(log)
        logs_by_date[date] = unique_logs

    return {
        "plant_id": plant_id,
        "log_by_date": logs_by_date
    }
@router.get("/get_latest_status/{plant_id}")
def get_latest_status(plant_id: str):
    """Return the latest sensor values (rounded) for display"""
    doc = dream_logs.find_one(
        {"plant_id": plant_id},
        sort=[("timestamp", -1)]
    )

    if not doc:
        raise HTTPException(status_code=404, detail="No data found for this plant.")

    return {
        "plant_id": plant_id,
        "light_level": round(doc.get("light_level", 0)),  # 四舍五入光照
        "avgMoisture": round(doc.get("avgMoisture", 0) * 100),  # 湿度百分制
        "timestamp": doc.get("timestamp")
    }
