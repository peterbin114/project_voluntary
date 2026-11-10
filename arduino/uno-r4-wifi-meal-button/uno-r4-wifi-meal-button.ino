/*
  Arduino Uno R4 WiFi -> meal display server

  Configure WIFI_SSID, WIFI_PASSWORD, API_SERVER, and BUTTON_PIN before upload.
  The button is wired between BUTTON_PIN and GND; INPUT_PULLUP is used.
*/
#include <WiFiS3.h>

const char WIFI_SSID[] = "YOUR_WIFI_SSID";
const char WIFI_PASSWORD[] = "YOUR_WIFI_PASSWORD";

// Set this to the laptop/server's LAN IPv4 address, not 127.0.0.1.
const IPAddress API_SERVER(192, 168, 0, 10);
const uint16_t API_PORT = 8000;
const char API_PATH[] = "/api/next";
const uint8_t BUTTON_PIN = 2;
const unsigned long DEBOUNCE_MS = 40;

int lastRawState = HIGH;
int stableState = HIGH;
unsigned long lastStateChangeMs = 0;

void connectToWifi() {
  if (WiFi.status() == WL_CONNECTED) {
    return;
  }

  Serial.print("Connecting to Wi-Fi");
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println();
  Serial.print("Connected. Board IP: ");
  Serial.println(WiFi.localIP());
}

bool sendNextEvent() {
  connectToWifi();

  WiFiClient client;
  client.setTimeout(3000);
  if (!client.connect(API_SERVER, API_PORT)) {
    Serial.println("Could not connect to meal server.");
    return false;
  }

  const char body[] = "{\"event\":\"next\",\"device_id\":\"uno-r4-wifi\"}";
  client.print("POST ");
  client.print(API_PATH);
  client.println(" HTTP/1.1");
  client.print("Host: ");
  client.print(API_SERVER);
  client.print(":");
  client.println(API_PORT);
  client.println("Content-Type: application/json");
  client.print("Content-Length: ");
  client.println(sizeof(body) - 1);
  client.println("Connection: close");
  client.println();
  client.print(body);

  String statusLine = client.readStringUntil('\n');
  statusLine.trim();
  Serial.print("Server response: ");
  Serial.println(statusLine);
  const bool succeeded = statusLine.startsWith("HTTP/1.1 200") ||
                         statusLine.startsWith("HTTP/1.0 200");
  client.stop();
  return succeeded;
}

void setup() {
  pinMode(BUTTON_PIN, INPUT_PULLUP);
  Serial.begin(115200);
  unsigned long serialWaitStarted = millis();
  while (!Serial && millis() - serialWaitStarted < 3000) {
    delay(10);
  }
  connectToWifi();
}

void loop() {
  const int rawState = digitalRead(BUTTON_PIN);
  if (rawState != lastRawState) {
    lastRawState = rawState;
    lastStateChangeMs = millis();
  }

  if (millis() - lastStateChangeMs >= DEBOUNCE_MS &&
      rawState != stableState) {
    stableState = rawState;
    if (stableState == LOW) {
      Serial.println("NEXT button pressed.");
      if (!sendNextEvent()) {
        Serial.println("NEXT event was not confirmed; press again to retry.");
      }
    }
  }

  delay(5);
}
