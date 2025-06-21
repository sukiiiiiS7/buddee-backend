"""
Avatar Upload API with MongoDB Integration for Grow AI
-------------------------------------------------------
Author: S7
Last Updated: 2025-05-23

This API allows users to upload profile pictures and automatically updates
the avatar_url field in the MongoDB 'users' collection.
"""

from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pymongo import MongoClient
from pathlib import Path
import shutil
import uuid
import os
from pymongo import MongoClient
from database.community_db_manager import count_unread_dreams
from database.check_achievements import check_achievements

MONGO_URI = os.getenv("MONGODB_URI")  


app = FastAPI()
client = MongoClient(MONGO_URI)
db = client["user_data"]
collection = db["users"]

# Serve static avatars
AVATAR_DIR = Path("static/avatars")
AVATAR_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.post("/upload_avatar")
async def upload_avatar(user_id: str = Form(...), file: UploadFile = File(...)):
    """
    Upload avatar and update MongoDB record for the given user_id.
    Also increment avatar count and trigger achievement check.
    """

    # Validate file format
    if not file.filename.endswith((".jpg", ".jpeg", ".png")):
        return JSONResponse(status_code=400, content={"error": "Only .jpg/.png/.jpeg allowed."})

    # Save file with unique filename
    ext = file.filename.split(".")[-1]
    unique_name = f"{uuid.uuid4()}.{ext}"
    save_path = AVATAR_DIR / unique_name

    with save_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Construct public URL
    avatar_url = f"http://localhost:8000/static/avatars/{unique_name}"
    
    result = collection.update_one(
        {"user_id": user_id},
        {
            "$set": {"avatar_url": avatar_url},
            "$inc": {"avatar_count": 1}
        }
    )

    if result.matched_count == 0:
        return JSONResponse(status_code=404, content={"error": f"User '{user_id}' not found."})

   
    check_achievements(user_id)

    return {
        "user_id": user_id,
        "avatar_url": avatar_url,
        "message": "Avatar uploaded & achievement checked"
    }
@app.get("/get_avatar/{user_id}")
def get_avatar(user_id: str):
    """
    Retrieve avatar URL for a given user ID.
    Returns 404 if user not found,
    Returns 204 if avatar_url not available.
    """
    user = collection.find_one({"user_id": user_id})
    if not user:
        return JSONResponse(status_code=404, content={"error": "User not found"})

    avatar_url = user.get("avatar_url", None)
    if not avatar_url:
        return JSONResponse(status_code=204, content={"message": "No avatar found"})

    return {"user_id": user_id, "avatar_url": avatar_url}
@app.get("/count_unread_dreams/{user_id}")
def count_unread_dreams_api(user_id: str):
    """
    Return how many unread 'dream' notifications the user has.
    Used by frontend to decide whether to show a red dot.
    """
    count = count_unread_dreams(user_id)
    return {"user_id": user_id, "unread_dreams": count}
