import pandas as pd
import numpy as np

# Load the dataset
file_path = "C:/Users/wusiq/Desktop/Grow-AI/leaf/predictor/Plants_indoor_dataset_iot_AI.xlsx"
df = pd.read_excel(file_path)

# Keep only useful columns and drop rows with missing values
df = df[["brightness", "solHumidity", "watering"]].dropna()

# Remove rows where watering is not a number (e.g., "undefined", text descriptions)
df = df[df["watering"].astype(str).str.match(r"^\d$")]  # Keep only "1", "2", "3"

# Convert brightness and humidity levels like "2_3" to 2.5
def parse_level(val):
    try:
        if isinstance(val, str) and "_" in val:
            return np.mean([int(v) for v in val.split("_")])
        return float(val)
    except:
        return np.nan

df["light_level"] = df["brightness"].apply(parse_level)
df["avgMoisture"] = df["solHumidity"].apply(parse_level)

# Convert watering level into binary: 1 = False (infrequent), 2 or 3 = True (frequent)
df["needs_frequent_water"] = df["watering"].astype(int).apply(lambda x: x >= 2)

# Map watering levels to approximate watering interval in days
def watering_to_days(w):
    w = int(w)
    if w == 1:
        return 7
    elif w == 2:
        return 3
    elif w == 3:
        return 1

df["watering_days"] = df["watering"].astype(int).apply(watering_to_days)

# Keep final columns only
cleaned_df = df[["light_level", "avgMoisture", "needs_frequent_water", "watering_days"]].dropna()

# Save to CSV
output_path = "C:/Users/wusiq/Desktop/Grow-AI/leaf/predictor/external_data_cleaned.csv"
cleaned_df.to_csv(output_path, index=False)

print("Dataset cleaned successfully and saved to external_data_cleaned.csv")
