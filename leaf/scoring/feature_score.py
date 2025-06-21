def calculate_leaf_score(leaf_features):
    """
    Calculate a health score (0.0 to 1.0) based on visual features of a leaf.

    Parameters:
        leaf_features (dict): Extracted features from image processing.
        Example:
        {
            "color": {
                "yellow_ratio": 0.3,
                "brown": 28,
                "black_spot_ratio": 0.1
            },
            "shape": {
                "irregularity": 0.5,
                "holes_detected": True
            }
        }

    Returns:
        float: Health score between 0.0 (poor) and 1.0 (healthy).
    """
    score = 1.0

    # Extract individual features with default fallback values
    yellow_ratio = leaf_features.get("color", {}).get("yellow_ratio", 0)
    brown = leaf_features.get("color", {}).get("brown", 0)
    black_spot_ratio = leaf_features.get("color", {}).get("black_spot_ratio", 0)

    irregularity = leaf_features.get("shape", {}).get("irregularity", 0)
    holes = leaf_features.get("shape", {}).get("holes_detected", False)

    # Deduct points based on severity and updated weightings
    score -= yellow_ratio * 0.35                      # Slightly reduced weight
    score -= min(brown / 100, 0.25)                   # Max 0.25 deduction for brown
    score -= min(black_spot_ratio, 0.2)               # Max 0.2 deduction for black spots
    score -= irregularity * 0.15                      # Irregularity lowered to 0.15
    if holes:
        score -= 0.1                                  # Holes deduction kept

    return round(max(score, 0.0), 2)
