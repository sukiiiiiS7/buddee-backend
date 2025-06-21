#include <Wire.h>
#include <Adafruit_VEML7700.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <time.h>

// WiFi Configuration 
const char* ssid = "\u5927\u58f0\u558a\u7239 \u81ea\u52a8\u8fde\u63a5";  
const char* password = "005470123";                   
const char* serverUrl = "https://light-api-ccw0.onrender.com/lux";  

// Light Sensor Setup 
Adafruit_VEML7700 veml = Adafruit_VEML7700();  // VEML7700 on Wire

// OLED Display Setup 
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET -1
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire1, OLED_RESET);  // OLED on Wire1

// Timing 
unsigned long lastUpdate = 0;
const unsigned long updateInterval = 60000;  // 60 seconds

// I2C Address Check Function 
void scanI2CAddress(TwoWire &bus, uint8_t targetAddress, const char* label) {
  Serial.print("Scanning ");
  Serial.print(label);
  Serial.print(" for I2C address 0x");
  Serial.println(targetAddress, HEX);

  bus.beginTransmission(targetAddress);
  if (bus.endTransmission() == 0) {
    Serial.print("Device found at 0x");
    Serial.println(targetAddress, HEX);
  } else {
    Serial.print("No device found at 0x");
    Serial.println(targetAddress, HEX);
  }
}

void setup() {
  Serial.begin(115200);
  delay(500);

 
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected");

  // I2C Setup 
  Wire.begin(21, 23);     // VEML7700 → SDA = GPIO21, SCL = GPIO23
  Wire1.begin(27, 4);     // OLED → SDA = GPIO27, SCL = GPIO4

  // I2C Scan 
  scanI2CAddress(Wire1, 0x3C, "OLED (Wire1)");
  scanI2CAddress(Wire, 0x10, "VEML7700 (Wire)");

  // Initialize VEML7700 
  if (!veml.begin()) {
    Serial.println("Failed to initialize VEML7700.");
    while (1);
  }
  veml.setGain(VEML7700_GAIN_1);
  veml.setIntegrationTime(VEML7700_IT_100MS);
  Serial.println("VEML7700 initialized.");

  //Initialize OLED Display 
  if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    Serial.println("SSD1306 initialization failed.");
    while (1);
  }
  display.clearDisplay();
  display.setTextColor(SSD1306_WHITE);
  display.setTextSize(1);
  display.setCursor(0, 0);
  display.println("OLED initialized.");
  display.display();
}

void loop() {
  unsigned long currentMillis = millis();

  if (currentMillis - lastUpdate >= updateInterval) {
    lastUpdate = currentMillis;

    //Read light level
    float lux = veml.readLux();
    Serial.print("Lux: ");
    Serial.println(lux);

    //Display data on OLED -
    display.clearDisplay();
    display.setTextSize(1);
    display.setCursor(0, 0);

    display.print("Lux: ");
    display.println(lux, 2);

    display.print("WiFi: ");
    display.println(WiFi.isConnected() ? "Connected" : "Disconnected");

    display.print("Uptime: ");
    display.print(millis() / 1000);
    display.println(" s");
    display.display();

    // Send Data to Server 
    if (WiFi.status() == WL_CONNECTED) {
      HTTPClient http;
      http.begin(serverUrl);
      http.addHeader("Content-Type", "application/json");

      String payload = "{\"lux\": " + String(lux, 2) + "}"; 
      int httpResponseCode = http.POST(payload);

      Serial.print("POST Response Code: ");
      Serial.println(httpResponseCode);
      if (httpResponseCode > 0) {
        String response = http.getString();
        Serial.println("Response: " + response);
      } else {
        Serial.println("Error sending POST request");
      }

      http.end();
    }
  }
}
