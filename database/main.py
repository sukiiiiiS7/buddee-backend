from fastapi import FastAPI, File, Form, UploadFile

from database.achievement_api import app as achievement_app, get_achievement_progress, check_and_draw_lottery
from database.avatar_uploader import app as avatar_app, upload_avatar, get_avatar
from database.community_db_manager import count_unread_dreams
from database.check_achievements import check_achievements
from database.dream_chat_api import app as chat_app
from database.plant_log_api import router as plant_log_router
from database.leaf_api import router as leaf_router

app = FastAPI()
app.include_router(plant_log_router)
app.include_router(leaf_router)

app.mount("/achievement", achievement_app)
app.mount("/avatar", avatar_app)
app.mount("/chat", chat_app)

@app.get("/")
def root():
    return {"message": "Grow AI backend is running + all routes included"}

@app.post("/upload_avatar")
async def upload_avatar_route(
    user_id: str = Form(...),
    file: UploadFile = File(...)
):
    return await upload_avatar(user_id, file)

@app.get("/get_avatar/{user_id}")
def get_avatar_route(user_id: str):
    return get_avatar(user_id)

@app.get("/count_unread_dreams/{user_id}")
def count_unread_dreams_route(user_id: str):
    return count_unread_dreams(user_id)

@app.get("/check_achievements/{user_id}")
def trigger_achievement_check(user_id: str):
    check_achievements(user_id)
    return {"status": "checked"}


@app.get("/achievement_progress/{user_id}")
def achievement_progress_api(user_id: str):
    return get_achievement_progress(user_id)

@app.post("/draw_lottery/{user_id}")
def draw_lottery_api(user_id: str):
    return check_and_draw_lottery(user_id)
