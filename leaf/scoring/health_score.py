from leaf.scoring.feature_score import calculate_leaf_score
from leaf.scoring.env_bonus import calculate_environment_bonus, evaluate_env_condition

"""
This module calculates an overall plant health score by combining
(1) visual leaf analysis and (2) environmental sensor data.

The result includes:
- Final score (0~100)
- Health label
- Explanation list (from environmental data)
- Recommendations (A: environment, B: visual cues)
"""

def generate_env_recommendations(light_level, soil_moisture):
    """
    Generate care suggestions based on environmental data (A类建议).
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


def generate_image_recommendations(image_score):
    """
    Generate visual health suggestions based on image score (B类建议).
    """
    recs = []
    if image_score < 85:
        recs.append("Visual signs of mild stress detected. Monitor leaf color and shape.")
    if image_score < 60:
        recs.append("Significant leaf damage observed. Consider pruning or pest inspection.")
    return recs

def calculate_health_score(leaf_features, soil_moisture, light_level):
    """
    Calculate an overall health score by combining leaf image score and environment score.

    Parameters:
        leaf_features (dict): Extracted visual features of the leaf.
        soil_moisture (float): Current soil moisture level.
        light_level (float): Current light intensity.

    Returns:
        dict: Contains health score, label, component breakdown, explanations, and care suggestions.
    """
    # Get image-based health score (0.0 ~ 1.0 → scaled to 0 ~ 100)
    image_score = round(calculate_leaf_score(leaf_features) * 100)

    # Get environment bonus and explanation
    env_bonus, env_comments = calculate_environment_bonus(soil_moisture, light_level)

    # Final score with bounds
    final_score = max(0, min(100, image_score + env_bonus))

    # Label assignment
    if final_score >= 85:
        label = "Healthy"
    elif final_score >= 60:
        label = "Mild Wilt"
    else:
        label = "Health Warning"

    # Use unified logic to generate care suggestions
    env_recs = generate_env_recommendations(light_level, soil_moisture)
    image_recs = generate_image_recommendations(image_score)
    recommendations = env_recs + image_recs

    return {
        "health_score": final_score,
        "label": label,
        "components": {
            "image_score": image_score,
            "env_bonus": env_bonus
        },
        "explanation": env_comments,
        "recommendations": recommendations
    }
