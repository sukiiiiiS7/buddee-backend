<p align="center">
  <img src="buddee-logo.png" alt="Buddee Logo" width="200"/>
</p>

# Buddee Backend

**Buddee** is a modular backend system designed to support smart plant care, combining AI image recognition, environmental sensors, gamified interactions, and user-driven feedback.  
This repository consolidates the backend modules I personally developed during the Grow AI project at UAL.

> “Buddee doesn't just monitor your plant – it helps it dream back.”

---
### Watch Buddee in Action

[![Open Buddee Web Demo](https://raw.githubusercontent.com/sukiiiiiS7/buddee-backend/main/demo-cover.png)](https://sukiiiiis7.github.io/buddee-backend/)
👉 Click the image above to explore the GitHub Pages demo.

---
## Features

- **Leaf Classification** using ResNet18 and pseudo-labeled Reddit data
- **Light Sensor Module** with ESP32 and local OLED display
- **Smart Watering Predictor** using Random Forest regression
- **Dream Record System** with symbolic environmental feedback
- **Achievement & Lottery Engine** to gamify plant nurturing
- **MongoDB Atlas Integration** for real-time data logging
- **FastAPI Deployment** hosted on Render

---

## System Architecture

> _Three-layer logic: Sensor → Backend → Dream Feedback_

- **Hardware Layer:** ESP32 captures lux/moisture data and displays info on OLED.
- **Backend Layer (FastAPI):**
  - `/leaf_scan`: Image → health classification → care suggestion
  - `/lux`: Sensor POST → database → timestamped storage
  - `/leaf/next_watering`: Combines user location, forecast, plant data to return watering recommendation
  - `/get_achievements`: Returns unlocked achievements
- **Database Layer:** MongoDB Atlas with collections for users, dream logs, health scores, and achievements
- (Optional) **Frontend:** React-based UI display (built by teammates; not included here)

---

## Prediction Models

The Buddee backend uses a trained **Random Forest Regression model** to predict ideal next watering time for plants:

- **Inputs:**
  - Light intensity (lux)
  - Soil moisture
  - Local rainfall forecast (via Open-Meteo API)
  - Plant preference thresholds (pre-defined rules)
  - Historical environment data (stored in MongoDB)

- **Output:**
  - Number of days until next watering (returned by `/leaf/next_watering/{user_id}`)

- **Details:**
  - Implemented in `predict_watering.py`
  - Integrated into FastAPI with logic fallback
  - Chosen for interpretability and lightweight deployment

---

## Repository Structure

| Folder          | Description                                         |
|-----------------|-----------------------------------------------------|
| `app/`          | FastAPI routes and backend logic                    |
| `leaf/`         | Leaf classification model + scoring system          |
| `sensor/`       |  lux/moisture data                                  |
| `database/`     | MongoDB models, schemas, and connection logic       |
| `data/`         | Sample payloads and sample image records            |
| `README_S7.md`  | Personal backend development log (by Suki Wu)       |

---

## Tech Stack

- **Languages:** Python
- **Framework:** FastAPI
- **AI Model:** ResNet18 (PyTorch)
- **ML Model:** Random Forest (Scikit-learn)
- **Database:** MongoDB Atlas
- **Sensor:** ESP32 Dev + VM7700 Light Sensor	+OLED Display (0.96" I2C)	+DC Buck +USB-C or DC Adapter+Jumper Wires + Breadboard
- **Weather API:** Open-Meteo (hourly rain forecast)
- **Deployment:** Render (Cloud-hosted backend)

---

## Use Cases

- Detect plant health from a single photo  
- Suggest watering dates based on real light, soil, and rain forecast  
- Unlock achievements as users care for their plant  
- Generate dream-state responses from plant data

---

## Demo

> Demo video coming soon — will include:  
> `leaf_scan`, `lux`, `next_watering`, `get_achievements`, and dream feedback preview.

---

## Author

**Suki Wu (吴思琦)** – Backend developer and hardware integrator  
- Developed and deployed all backend APIs (except album)
- Built and trained the leaf health classifier
- Integrated hardware sensors and cloud storage
- Designed and implemented watering logic and random reward engine
- Created dream interaction and achievement unlocking system

GitHub: [@sukiiiiiS7](https://github.com/sukiiiiiS7)

---

## License

For educational and demonstrative use only.
