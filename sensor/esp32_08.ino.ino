#include <WiFi.h>
#include <HTTPClient.h>

#define PUMP_PIN 2
#define SOIL_SENSOR_PIN 34

const char* ssid = "UAL-IoT";
const char* password = "$taffDevice2023";
const char* serverURL = "https://esp-plant-dashboard.onrender.com/upload";

String deviceID = "ESP32-08";  // Change this for each device e.g. ESP32-04

void setup() {
    pinMode(PUMP_PIN, INPUT);
    delay(1000);
    Serial.begin(115200);

    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println("\nConnected to WiFi.");
}

void loop() {
    int totalMoisture = 0;
    for (int i = 0; i < 10; i++) {
        totalMoisture += analogRead(SOIL_SENSOR_PIN);
        delay(200);
    }

    int avgMoisture = totalMoisture / 10;
    Serial.print("Average Soil Moisture: ");
    Serial.println(avgMoisture);
    // avgMoisture=599;
    //  Send to Flask server
    if (WiFi.status() == WL_CONNECTED) {
        HTTPClient http;
        http.begin(serverURL);
        http.addHeader("Content-Type", "application/json");

        String payload = "{\"avgMoisture\":" + String(avgMoisture) + ",\"deviceID\":\"" + deviceID + "\"}";
        int httpResponseCode = http.POST(payload);

        Serial.print("HTTP Response code: ");
        Serial.println(httpResponseCode);

        http.end();
    }

    // delay(400); // wait 1 min << can be useful for testing
    delay(60000); // wait 1 min
}