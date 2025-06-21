# Grow AI – Hardware Integration (ESP32 + Sensors + OLED)

This folder contains the Arduino (.ino) code files used in the **Grow AI** project. These ESP32 scripts read data from **light**, **soil moisture** sensors and display them on an **OLED screen**, while sending the data to a cloud backend via HTTP POST.

---

## Hardware Components

| Component               | Description / Note                                |
|-------------------------|---------------------------------------------------|
| ESP32 Dev Module        | Main microcontroller board                        |
| VM7700 Light Sensor     | Analog light sensor connected to GPIO 34          |
| Soil Moisture Sensor    | Analog, connected to GPIO 35                      |
| OLED Display (0.96" I2C)| 128x64 OLED, displays lux and WiFi status         |
| DC Buck Module          | Provides stable 5V to ESP32                       |
| USB-C or DC Adapter     | For power supply (via buck or direct USB)         |
| Jumper Wires + Breadboard | Used for sensor and OLED wiring                |

---

## Pin Mapping

| ESP32 Pin | Connected Component                 |
|-----------|-------------------------------------|
| GPIO 34   | VM7700 Light Sensor (Analog OUT)    |
| GPIO 35   | Soil Moisture Sensor (Analog OUT)   |
| GPIO 21   | SDA (OLED I2C data)                 |
| GPIO 22   | SCL (OLED I2C clock)                |
| 3V3       | VCC for sensors and OLED            |
| GND       | Ground for all components           |

> Note: The OLED I2C address is usually `0x3C`.

---

## OLED Display Usage

- Displays current lux value
- Shows WiFi connection status (e.g. `Connecting...`, `Connected`)
- Optional: Can flash status/error info like POST failed

### Example Display Layout:
```
Light: 124.3 lux  
WiFi: Connected
```

---

## Upload & Deployment Steps

1. Connect the ESP32 via USB and select the correct port in Arduino IDE.
2. Install these libraries using the Library Manager:
   - `Adafruit_SSD1306`
   - `Adafruit_GFX`
3. Ensure I2C is enabled on GPIO 21/22 (enabled by default on ESP32).
4. Upload the `.ino` file and watch Serial Monitor (115200 baud) & OLED feedback.

---

## Troubleshooting Tips

- If OLED doesn't show content, check:
  - OLED I2C address is set to `0x3C`
  - You are using **3.3V** for VCC (not 5V)
  - All components share a common **GND**

---

## Backend Endpoint (FastAPI)

The ESP32 sends lux sensor data to a FastAPI backend hosted on Render.

### Endpoint:
```http
POST https://light-api-ccw0.onrender.com/lux
```

### Payload Example:
```json
{
  "lux": 98.5,
  "timestamp": "2025-05-28T17:12:43"
}
```

### Behavior:
- The backend is deployed on [Render](https://render.com/) and maintained by **S7**.
- The API validates the incoming JSON payload and stores it in **MongoDB Atlas**, specifically under the `lux_records` collection in the `light_data` database.
- This setup supports real-time environmental monitoring and powers the dream-generation logic in Grow AI.

For full backend architecture, API routes, and database structure, see:  
[GitHub Wiki – Backend & MongoDB Integration](https://git.arts.ac.uk/24043715/Grow-AI/wiki/MongoDB-Setup#light-sensor-database-light_data)

