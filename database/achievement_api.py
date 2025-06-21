from fastapi import FastAPI
from pymongo import MongoClient
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime
import os
import random
from fastapi.responses import JSONResponse
from database.achievement_config import ACHIEVEMENTS
from database.check_achievements import check_achievements

app = FastAPI()
LOTTERY_COST = 100

env_path = Path(__file__).parent / ".env_user"
load_dotenv(dotenv_path=env_path)
MONGO_URI = os.getenv("MONGODB_URI")
client = MongoClient(MONGO_URI)
db = client["user_data"]
achievement_log = db["achievement_log"]
users = db["users"]
lottery_log = db["lottery_log"]

def get_achievement_progress(user_id: str):
    user = users.find_one({"user_id": user_id})
    if not user:
        return {"error": "user not found"}

    points = user.get("achievement_points", 0)
    percent = min(100, int((points / 100) * 100))
    can_draw = points >= 100

    return {
        "user_id": user_id,
        "points": points,
        "progress_percent": percent,
        "can_draw": can_draw
    }

def check_and_draw_lottery(user_id: str):
    user = users.find_one({"user_id": user_id})
    if not user:
        return JSONResponse(content={"error": "user not found"}, status_code=404)

    points = user.get("achievement_points", 0)
    if points < LOTTERY_COST:
        return JSONResponse(content={"status": "not enough points"}, status_code=200)

    prize_ids = [
        "digital_stamp_A",
        "digital_stamp_B",
        "full_physical_set",
        "full_physical_set_seed"
    ]
    weights = [0.5, 0.3, 0.15, 0.05]

    PRIZE_INFO = {
        "digital_stamp_A": "Hidden Digital Stamp A",
        "digital_stamp_B": "Hidden Digital Stamp B",
        "full_physical_set": "Full Physical Stamp Set",
        "full_physical_set_seed": "Full Set + Dream Seed Bottle"
    }

    chosen_id = random.choices(prize_ids, weights=weights, k=1)[0]
    reward_label = PRIZE_INFO[chosen_id]

    lottery_log.insert_one({
        "user_id": user_id,
        "reward_id": chosen_id,
        "reward_label": reward_label,
        "timestamp": datetime.utcnow()
    })

    users.update_one({"user_id": user_id}, {"$inc": {"achievement_points": -LOTTERY_COST}})

    return JSONResponse(content={
        "user_id": user_id,
        "reward": reward_label,
        "reward_id": chosen_id,
        "status": "lottery triggered"
    }, status_code=200)

@app.get("/draw_lottery/{user_id}")
def draw_lottery(user_id: str):
    return check_and_draw_lottery(user_id)

@app.get("/get_achievement_progress/{user_id}")
def get_progress(user_id: str):
    return get_achievement_progress(user_id)

@app.get("/latest_animated_achievement/{user_id}")
def latest_animated_achievement(user_id: str):
    recent = achievement_log.find({"user_id": user_id}).sort("unlocked_at", -1)
    for entry in recent:
        ach = next((a for a in ACHIEVEMENTS if a["id"] == entry["achievement_id"]), None)
        if ach and ach.get("animate", False):
            return {
                "achievement_id": ach["id"],
                "name": ach["name"],
                "icon": ach["icon"],
                "unlocked_at": entry["unlocked_at"]
            }
    return {"message": "No animated achievements found."}

@app.get("/get_achievements/{user_id}")
def get_achievements_api(user_id: str):
    unlocked = list(achievement_log.find({"user_id": user_id}))
    unlocked_ids = [u["achievement_id"] for u in unlocked]

    enriched = []
    for ach in ACHIEVEMENTS:
        enriched.append({
            "id": ach["id"],
            "name": ach["name"],
            "description": ach["description"],
            "icon": ach["icon"],
            "points": ach["points"],
            "animate": ach.get("animate", False),
            "unlocked": ach["id"] in unlocked_ids
        })

    user = users.find_one({"user_id": user_id}) or {}
    total_points = user.get("achievement_points", 0)

    return {
        "user_id": user_id,
        "total_points": total_points,
        "unlocked_achievements": enriched
    }

@app.get("/get_lottery_history/{user_id}")
def get_lottery_history(user_id: str):
    logs = list(lottery_log.find({"user_id": user_id}).sort("timestamp", -1))
    formatted = [{
        "reward_id": log["reward_id"],
        "reward_label": log["reward_label"],
        "timestamp": log["timestamp"]
    } for log in logs]

    return {
        "user_id": user_id,
        "history": formatted
    }

@app.get("/check_achievements/{user_id}")
def run_achievement_check(user_id: str):
    check_achievements(user_id)
    return {"message": f"Achievements checked for {user_id}"}

@app.delete("/reset_achievements/{user_id}")
def reset_achievements(user_id: str):
    achievement_log.delete_many({"user_id": user_id})
    lottery_log.delete_many({"user_id": user_id})
    users.update_one({"user_id": user_id}, {"$set": {"achievement_points": 0}})
    return {"message": f"All achievements and points reset for {user_id}"}
