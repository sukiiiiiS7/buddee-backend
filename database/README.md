# Grow AI – Backend Setup (`database/` Folder)

This folder contains the full backend implementation for avatar management, achievement unlocking, dream generation, and plant-based messaging in the Grow AI system.

---

## Implemented Features

- **User Avatar System**
  - Upload avatars and retrieve user profile images
  - Tracks unread dream notifications for users

- **Achievement System**
  - Unlock milestones based on user behavior
  - Visual progress bar & lottery reward draw (≥100 points)
  - Animated achievements supported

- **Dream Dialogue & Messaging**
  - Plants generate poetic dream logs based on mood, light, and water
  - Dream chat between neighboring plants
  - In-app notification system for dream messages
  
- **Sensor Status Summary**
  - `/get_latest_status/{plant_id}` Return the latest light and humidity data of the plant (for display on the home page).

- **MongoDB Cloud Integration**
  - Stores all logs, profiles, avatars, messages on MongoDB Atlas
  - Built-in support for light sensor readings

- **Deployed via Render**
  - Backend hosted at: [https://growai-backend.onrender.com](https://growai-backend.onrender.com)


---

## Folder Contents

| File | Description |
|------|-------------|
| `main.py` | FastAPI root entrypoint – combines all API routes |
| `avatar_uploader.py` | Handles image upload and unread counter |
| `achievement_api.py` | API routes for achievements & lottery |
| `check_achievements.py` | Core logic for automatic achievement detection |
| `achievement_config.py` | Achievement metadata (ID, icon, name, animation, points) |
| `dream_chat_api.py` | Routes for plant-to-plant dream chatting |
| `community_db_manager.py` | Logs dream chats and user notifications |
| `user_db_manager.py` | Manages user profiles and preferences |
| `dream_db_logger.py` | [Optional] Logs generated dream data to MongoDB |
| `dialogue_utils.py` | Dream generation logic (mood detection + templates) |
| `dialogue_templates.json` | Poetic dream sentence templates |
| `static/avatars/` | Stores uploaded images |
| `.env_user` | MongoDB secrets (excluded from Git) |
| `requirements.txt` | Python dependencies |
| `README.md` | This file |

---

## Notes

- `/chat/send_dream_chat` auto-triggers dream notifications
- Lottery draws cost **100 points**, managed internally
- `generate_dream_dialogue` supports mood-tagging for dream aesthetics
- FastAPI routes follow REST principles for modular frontend integration

---

## Acknowledgements

- All backend structure, achievement logic, database routing, and API design by **S7**
- Dream dialogue generation and template logic (`dialogue_utils.py`, `dialogue_templates.json`) contributed by **Le**

---

If you need help extending or deploying, see the [MongoDB Setup Wiki](https://git.arts.ac.uk/24043715/Grow-AI/wiki/MongoDB-Setup#mongodb-setup-for-grow-ai).
