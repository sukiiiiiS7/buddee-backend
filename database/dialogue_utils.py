"""
Dream Dialogue Generator with Mood Tag Classification
-----------------------------------------------------
Author: Leslie
Last Updated: 2025-05-28

Generates personalized dream_dialogue text for plant sensor data.
Each user gets consistent daily sentences based on deterministic randomization.
Mood tags are calculated for QQ emoji animation control in the frontend.

Core Logic:
- Daily refresh at 06:00 London time
- Deterministic RNG per (date|user_id) prevents text flickering
- Conditional suffixes for water/light needs
- Weighted mood calculation from all text components
- Full-length dialogue output for complete message display

"""

import json
import random
import hashlib
from pathlib import Path
from datetime import timedelta
from typing import Dict, Tuple

import pandas as pd
import pytz

# Config and initialization
TEMPLATE_PATH = Path(__file__).with_name("dialogue_templates.json")
TIMEZONE = pytz.timezone("Europe/London")
TEMPLATES = json.loads(TEMPLATE_PATH.read_text(encoding="utf-8"))

# Mood scoring weights for final mood calculation
MOOD_WEIGHTS = {
    "happy": 2,
    "neutral": 1, 
    "sad": -1
}


def _period_key(row: dict) -> str:
    """Calculate date string for dialogue consistency period.
    
    Records before 06:00 local time belong to previous day's period.
    """
    ts_local = (
        pd.to_datetime(row["timestamp"])
        .tz_localize("UTC")
        .astimezone(TIMEZONE)
    )
    
    six_am = ts_local.replace(hour=6, minute=0, second=0, microsecond=0)
    
    if ts_local < six_am:
        key_date = (ts_local - timedelta(days=1)).strftime("%Y-%m-%d")
    else:
        key_date = ts_local.strftime("%Y-%m-%d")
    
    return key_date


def _rng_for_row(row: dict) -> random.Random:
    """Build deterministic RNG seeded by period_key|user_id."""
    base_key = f"{_period_key(row)}|{row.get('user_id', '')}"
    seed_int = int(hashlib.md5(base_key.encode()).hexdigest(), 16)
    return random.Random(seed_int)


def _choose_sentence(rng: random.Random, template_key: str) -> Dict[str, str]:
    """Pick sentence and mood from template category."""
    sentences = TEMPLATES[template_key]["sentences"]
    return rng.choice(sentences)


def _calculate_final_mood(mood_tags: list) -> str:
    """Calculate weighted final mood from component moods.
    
    Returns:
        "happy" if total_weight >= 2
        "sad" if total_weight <= -1  
        "neutral" otherwise
    """
    if not mood_tags:
        return "neutral"
    
    total_weight = sum(MOOD_WEIGHTS.get(tag, 0) for tag in mood_tags)
    
    if total_weight >= 2:
        return "happy"
    elif total_weight <= -1:
        return "sad"
    else:
        return "neutral"


def make_dialogue(row: dict) -> Dict[str, str]:
    """Generate dream dialogue with mood classification.
    
    Args:
        row: Sensor data dict with keys:
            - timestamp: ISO 8601 UTC string  
            - dream_type: "sunny"|"dry"|"misty"|"rainy"
            - since_water_days: int
            - likes_bright_light: bool
            - light_level: float (0-100)
            - user_id: str (optional)
    
    Returns:
        Dict with keys:
            - text: Complete dialogue text (no length limit)
            - mood_tag: Overall mood ("happy"|"neutral"|"sad") 
            - components: Debug info with individual parts
    """
    rng = _rng_for_row(row)
    mood_tags = []
    text_parts = []
    
    # Main sentence based on dream_type
    main_sentence = _choose_sentence(rng, row["dream_type"])
    text_parts.append(main_sentence["text"])
    mood_tags.append(main_sentence["mood_tag"])
    
    # Water request suffix (if dry > 3 days)
    need_water_suffix = None
    if row.get("since_water_days", 0) > 3:
        need_water_suffix = _choose_sentence(rng, "need_water")
        text_parts.append(need_water_suffix["text"])
        mood_tags.append(need_water_suffix["mood_tag"])
    
    # Light request suffix (if bright-loving plant in low light)
    want_light_suffix = None
    if row.get("likes_bright_light") and row.get("light_level", 100) < 30:
        want_light_suffix = _choose_sentence(rng, "want_light")
        text_parts.append(want_light_suffix["text"])
        mood_tags.append(want_light_suffix["mood_tag"])
    
    # Kaomoji ending
    kaomoji = _choose_sentence(rng, "kaomojis")
    text_parts.append(" " + kaomoji["text"])
    mood_tags.append(kaomoji["mood_tag"])
    
    # Assembly without truncation
    final_text = "".join(text_parts)
    final_mood = _calculate_final_mood(mood_tags)
    
    return {
        "text": final_text,
        "mood_tag": final_mood,
        "components": {
            "main": {"text": main_sentence["text"], "mood": main_sentence["mood_tag"]},
            "need_water": {"text": need_water_suffix["text"], "mood": need_water_suffix["mood_tag"]} if need_water_suffix else None,
            "want_light": {"text": want_light_suffix["text"], "mood": want_light_suffix["mood_tag"]} if want_light_suffix else None,
            "kaomoji": {"text": kaomoji["text"], "mood": kaomoji["mood_tag"]},
            "mood_tags": mood_tags,
            "final_mood": final_mood
        }
    }
