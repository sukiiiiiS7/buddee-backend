from fastapi import FastAPI, Body
from database.community_db_manager import add_dream_chat, chat_col, add_notification, get_plant_owner
from database.community_db_manager import count_unread_dreams, get_notifications, mark_notifications_read
import random
from database.dialogue_utils import make_dialogue
from datetime import datetime

app = FastAPI()

@app.post("/send_dream_chat")
def send_dream_chat(
    from_plant_id: str = Body(...),
    to_plant_id: str = Body(...),
    dream_text: str = Body(default=None) #Allow users not to pass.
):
    used_auto_generated = False


    if not dream_text or dream_text.strip() == "":
        dream_input = {
            "timestamp": datetime.utcnow().isoformat(),
            "dream_type": "sunny",  # TODO: replace with actual predicted dream_type
            "since_water_days": 2,
            "likes_bright_light": True,
            "light_level": 60,
            "user_id": from_plant_id
        }
    generated = make_dialogue(dream_input)
    dream_text = generated["text"]
    mood_tag = generated["mood_tag"]
    used_auto_generated = True

    chat_id = add_dream_chat(from_plant_id, to_plant_id, dream_text, mood_tag)
    #Notify the owners of the plants.
    to_user_id = get_plant_owner(to_plant_id)
    if to_user_id:
        add_notification(
            user_id=to_user_id,
            message=f"Your plant '{to_plant_id}' received a new dream.",
            notif_type="dream"
        )

    return {
    "status": "success",
    "chat_id": str(chat_id),
    "used_auto_generated": used_auto_generated,
    "mood_tag": mood_tag  
}
                                          
@app.post("/generate_dream_dialogue")
def generate_dream_dialogue(row: dict = Body(...)):
    """
    Generate a dream dialogue string and mood_tag from dream input.
    Required fields: timestamp, dream_type, since_water_days, likes_bright_light, light_level, user_id
    """
    try:
        result = make_dialogue(row)
        return result
    except Exception as e:
        return {"error": str(e)}

@app.get("/get_dream_chats/{plant_id}")
def get_dream_chats(plant_id: str):
    chats = list(chat_col.find({"to_plant_id": plant_id}, {"_id": 0}))
    return {
        "to_plant_id": plant_id,
        "received_chats": chats
    }

@app.get("/count_unread_dreams/{user_id}")
def count_unread_dreams_route(user_id: str):
    return count_unread_dreams(user_id)

@app.get("/get_dream_notifications/{user_id}")
def get_dream_notifications(user_id: str):
    return get_notifications(user_id)

@app.post("/clear_dream_notifications/{user_id}")
def clear_dream_notifications(user_id: str):
    return {"cleared": mark_notifications_read(user_id)}