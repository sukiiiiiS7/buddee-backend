from health_score import calculate_health_score

# Sample test data
test_samples = [
    {
        "leaf_features": {
            "color": {"yellow_ratio": 0.1, "brown": 5},
            "shape": {"irregularity": 0.2, "holes_detected": False}
        },
        "soil_moisture": 60,
        "light_level": 35000
    },
    {
        "leaf_features": {
            "color": {"yellow_ratio": 0.4, "brown": 60},
            "shape": {"irregularity": 0.6, "holes_detected": True}
        },
        "soil_moisture": 20,
        "light_level": 40000
    },
    {
        "leaf_features": {
            "color": {"yellow_ratio": 0.0, "brown": 0},
            "shape": {"irregularity": 0.0, "holes_detected": False}
        },
        "soil_moisture": 65,
        "light_level": 25000
    },
    {
        "leaf_features": {
            "color": {"yellow_ratio": 0.2, "brown": 10},
            "shape": {"irregularity": 0.1, "holes_detected": False}
        },
        "soil_moisture": 55,
        "light_level": 42000
    },
    {
        "leaf_features": {
            "color": {"yellow_ratio": 0.5, "brown": 80},
            "shape": {"irregularity": 0.7, "holes_detected": True}
        },
        "soil_moisture": 30,
        "light_level": 47000
    }
]

# Run test
print("===== Leaf Health Score Test Results =====\n")

for i, sample in enumerate(test_samples):
    result = calculate_health_score(
        sample["leaf_features"],
        sample["soil_moisture"],
        sample["light_level"]
    )

    print(f"Sample {i + 1}:")
    print(f"Score: {result['health_score']} | Label: {result['label']}")
    print(f"Image Score: {result['components']['image_score']} + Env Bonus: {result['components']['env_bonus']}")
    for explanation in result['explanation']:
        print(f"- {explanation}")
    for tip in result['recommendations']:
        print(f"> Recommendation: {tip}")
    print()
