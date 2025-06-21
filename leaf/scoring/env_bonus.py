"""
Environment scoring and care recommendation module.

Includes:
- Unified environment condition analysis
- Bonus/penalty score logic
- Consistent care recommendations

Used by:
- health_score.py
- leaf_api.py
"""

from typing import List, Tuple, Dict

def evaluate_env_condition(light_level: float, soil_moisture: float) -> Dict[str, str]:
    """
    Categorize current environment readings into qualitative states.

    Parameters:
        light_level (float): Light level (normalized 0–100)
        soil_moisture (float): Soil moisture level (0–100)

    Returns:
        dict: {
            "light": "low" | "optimal" | "high",
            "moisture": "low" | "optimal" | "high"
        }
    """
    status = {"light": "optimal", "moisture": "optimal"}

    if light_level < 30:
        status["light"] = "low"
    elif light_level > 85:
        status["light"] = "high"

    if soil_moisture < 25:
        status["moisture"] = "low"
    elif soil_moisture > 80:
        status["moisture"] = "high"

    return status


def calculate_environment_bonus(soil_moisture: float, light_level: float) -> Tuple[int, List[str]]:
    """
    Computes bonus/penalty score based on environment conditions.

    Bonus range: -10 to +10
    Each optimal range contributes +5; warning zones deduct -5.

    Returns:
        (bonus: int, comments: List[str])
    """
    status = evaluate_env_condition(light_level, soil_moisture)
    bonus = 0
    comments = []

    # Light interpretation
    if status["light"] == "optimal":
        bonus += 5
        comments.append("Light level is optimal.")
    elif status["light"] == "low":
        bonus -= 5
        comments.append("Low light detected. Consider moving to a brighter location.")
    elif status["light"] == "high":
        bonus -= 5
        comments.append("Excessive light detected. Shade may be needed.")

    # Moisture interpretation
    if status["moisture"] == "optimal":
        bonus += 5
        comments.append("Soil moisture is ideal.")
    elif status["moisture"] == "low":
        bonus -= 5
        comments.append("Soil is too dry. Watering is recommended.")
    elif status["moisture"] == "high":
        bonus -= 5
        comments.append("Soil is too wet. Ensure good drainage.")

    return bonus, comments


def generate_recommendations(light_level: float, soil_moisture: float) -> List[str]:
    """
    Generate care suggestions based on environment condition labels.

    Returns:
        List of actionable care recommendations.
    """
    status = evaluate_env_condition(light_level, soil_moisture)
    recs = []

    if status["light"] == "low":
        recs.append("Light is too low. Consider relocating to a brighter area.")
    elif status["light"] == "high":
        recs.append("Too much light. Consider moving to a shaded area.")

    if status["moisture"] == "low":
        recs.append("Soil is too dry. Watering is recommended.")
    elif status["moisture"] == "high":
        recs.append("Soil is too wet. Reduce watering frequency.")

    return recs
