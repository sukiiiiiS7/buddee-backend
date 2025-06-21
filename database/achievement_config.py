# Grow AI – Achievement System Configuration
# Author: S7
# Last Updated: 2025-05-26
#
# This file contains all achievements definitions.
# Each entry defines:
# - id: unique key for internal logic
# - name: displayed title
# - description: tooltip or detail description
# - points: reward points added to progress bar
# - icon: emoji (or image name placeholder)
# - animate: whether the achievement triggers a pixel animation
#
# Used by: check_achievements.py, frontend renderer

ACHIEVEMENTS = [
    {
        "id": "DREAM_BEGINS",
        "name": "Dream Begins",
        "description": "Generated your first dream record.",
        "points": 15,
        "icon": "💭",
        "animate": True
    },
    {
        "id": "SILENT_READER",
        "name": "Silent Reader",
        "description": "You left 3 or more dreams unread.",
        "points": 15,
        "icon": "📪",
        "animate": True
    },
    {
        "id": "STAYED_UP_LATE",
        "name": "Stayed Up Late",
        "description": "Generated a dream between 1–4 a.m.",
        "points": 15,
        "icon": "🕯️",
        "animate": True
    },
    {
        "id": "GLITCH_GARDENER",
        "name": "Glitch Gardener",
        "description": "Logged a dream with corrupted moisture data.",
        "points": 15,
        "icon": "🌀",
        "animate": True
    },
    {
        "id": "AVATAR_MASTER",
        "name": "Avatar Master",
        "description": "Uploaded 5 avatars.",
        "points": 20,
        "icon": "🖼️",
        "animate": False
    },
    {
        "id": "PIXEL_COLLECTOR",
        "name": "Pixel Collector",
        "description": "Unlocked 3 animated achievements.",
        "points": 25,
        "icon": "📬",
        "animate": False
    },
    {
        "id": "MIST_DREAMER",
        "name": "Mist Dreamer",
        "description": "Experienced your first misty dream.",
        "points": 15,
        "icon": "🌫️",
        "animate": False
    }
]
