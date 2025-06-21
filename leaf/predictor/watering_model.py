import joblib
import numpy as np
import pandas as pd
import os

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(CURRENT_DIR, "watering_model.pkl")
model = joblib.load(model_path)

def predict_watering_days(light_level: float, avgMoisture: float) -> int:
    """
    Predict the recommended watering interval in days (1, 3, or 7) based on
    light level and average soil moisture.

    Parameters:
    - light_level (float): Light intensity level of the environment
    - avgMoisture (float): Average soil moisture level

    Returns:
    - int: Recommended watering interval in days (1, 3, or 7)
    """
    features = np.array([[light_level, avgMoisture]])
    prediction = model.predict(features)[0]
    return int(prediction)
def predict_watering_days(light_level, soil_moisture):
    X = [[light_level, soil_moisture]]
    prediction = model.predict(X)
    return int(prediction[0])
# Example usage (for testing only, remove before deployment):
if __name__ == "__main__":
    example_light = 2.5
    example_moisture = 1.8
    predicted_days = predict_watering_days(example_light, example_moisture)
    print(f"Recommended watering interval: every {predicted_days} day(s)")
