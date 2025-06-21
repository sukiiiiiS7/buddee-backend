import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib

# Load cleaned dataset
data_path = "C:/Users/wusiq/Desktop/Grow-AI/leaf/predictor/external_data_cleaned.csv"
df = pd.read_csv(data_path)

# Prepare features (X) and label (y)
X = df[["light_level", "avgMoisture"]]
y = df["watering_days"]

# Split into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Train a Random Forest model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Evaluate performance (optional)
y_pred = model.predict(X_test)
report = classification_report(y_test, y_pred)
print("Classification Report:")
print(report)

#Save the trained model to .pkl
model_output_path = "C:/Users/wusiq/Desktop/Grow-AI/leaf/predictor/watering_model.pkl"
joblib.dump(model, model_output_path)
print(f"Model saved to: {model_output_path}")
