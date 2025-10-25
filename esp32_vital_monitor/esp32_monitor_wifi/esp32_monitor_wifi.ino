/*
 * ESP32 Vital Monitoring — WiFi edition
 * Reads the sensors and ships JSON to your API over WiFi. Clean and quick.
 *
 * You’ll want these libs:
 * - ArduinoJson (by Benoit Blanchon)
 * - WiFi (built-in)
 * - HTTPClient (built-in)
 * - Adafruit MLX90614
 * - MAX30100lib (by oxullo)
 * - Wire (built-in)
 *
 * Wiring cheat sheet:
 * - MAX30100 (HR/SpO2): SDA=21, SCL=22
 * - MLX90614 (Temp): SDA=21, SCL=22
 * - Blood Pressure: A34
 * - Respiration: A35
 * - AD8232 ECG: OUT=36, LO+=39, LO-=32
 */

#include <ArduinoJson.h>
#include <Wire.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <Adafruit_MLX90614.h>
#include <MAX30100_PulseOximeter.h>

// ============= WiFi setup (yes, change these) =============
const char* WIFI_SSID = "YOUR_WIFI_NAME";
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";

// API endpoint: point this at your PC’s IP
// Windows tip: run `ipconfig`, grab the "IPv4 Address"
const char* API_ENDPOINT = "http://192.168.1.100:5000/api/vitals";  // <- update this

// ============= Sensor setup =============
Adafruit_MLX90614 mlx = Adafruit_MLX90614();
PulseOximeter pox;

// Pins (standard ESP32 layout)
const int BP_SENSOR_PIN = 34;
const int RESP_SENSOR_PIN = 35;
const int ECG_OUTPUT_PIN = 36;     // AD8232 ECG output pin
const int ECG_LO_PLUS_PIN = 39;    // AD8232 leads-off detection LO+
const int ECG_LO_MINUS_PIN = 32;   // AD8232 leads-off detection LO-
const int LED_PIN = 2;

// Bundle all vitals in one struct
struct VitalData {
  int heartRate;
  int bpSystolic;
  int bpDiastolic;
  float temperature;
  int oxygenSaturation;
  int respiratoryRate;
  int ecgValue;              // Current ECG reading
  bool ecgLeadsConnected;    // ECG leads connection status
  unsigned long timestamp;
};

VitalData vitals;

// Timing (don’t spam your API)
unsigned long lastReadTime = 0;
unsigned long lastSendTime = 0;
const unsigned long READ_INTERVAL = 1000;  // Read sensors every 1 second
const unsigned long SEND_INTERVAL = 2000;  // Send to API every 2 seconds

// Who’s connected (flags)
bool mlxConnected = false;
bool poxConnected = false;
bool wifiConnected = false;

void setup() {
  Serial.begin(115200);
  delay(1000);
  
  Serial.println("====================================");
  Serial.println("ESP32 Vital Monitor - WiFi Edition"); // wireless mode
  Serial.println("====================================");
  
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);
  
  connectToWiFi(); // no WiFi, no party
  Wire.begin();
  if (mlx.begin()) {
    mlxConnected = true;
    Serial.println("✅ MLX90614 Temperature Sensor Connected");
  } else { // we’re not
    Serial.println("❌ MLX90614 Temperature Sensor Not Found");
  }
  
  if (pox.begin()) {
    poxConnected = true;
    Serial.println("✅ MAX30100 Pulse Oximeter Connected");
  } else {
    Serial.println("❌ MAX30100 Pulse Oximeter Not Found");
  }
  
  pinMode(BP_SENSOR_PIN, INPUT);
  pinMode(RESP_SENSOR_PIN, INPUT);
  pinMode(ECG_OUTPUT_PIN, INPUT);
  pinMode(ECG_LO_PLUS_PIN, INPUT);
  pinMode(ECG_LO_MINUS_PIN, INPUT);
  
  Serial.println("🏥 ESP32 Vital Monitor Ready");      // alive
  Serial.println("📡 Sending data wirelessly to API..."); // and chatty
  Serial.println("---");
}

void loop() {
  unsigned long currentTime = millis();
  
  if (WiFi.status() != WL_CONNECTED) { // fell off the WiFi?
    wifiConnected = false;
    Serial.println("⚠️ WiFi disconnected. Reconnecting...");
    connectToWiFi();
  }
  
  if (currentTime - lastReadTime >= READ_INTERVAL) {
    readAllSensors();
    lastReadTime = currentTime;
  }
  
  if (wifiConnected && currentTime - lastSendTime >= SEND_INTERVAL) {
    sendVitalDataToAPI();
    lastSendTime = currentTime;
  }
  
  if (poxConnected) { // heart + oxygen
    pox.update();
  }
  
  delay(10);
}

void connectToWiFi() { // quick connect loop with a little patience
  Serial.print("📶 Connecting to WiFi: ");
  Serial.println(WIFI_SSID);
  
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) { // try a bit, don’t panic
    delay(500);
    Serial.print(".");
    digitalWrite(LED_PIN, !digitalRead(LED_PIN));
    attempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) { // we’re on
    wifiConnected = true;
    digitalWrite(LED_PIN, HIGH);
    Serial.println("\n✅ WiFi Connected!");
    Serial.print("📍 IP Address: ");
    Serial.println(WiFi.localIP());
    Serial.print("📡 Sending data to: ");
    Serial.println(API_ENDPOINT);
  } else {
    wifiConnected = false;
    digitalWrite(LED_PIN, LOW);
    Serial.println("\n❌ WiFi Connection Failed!");
    Serial.println("⚠️ Check your WiFi credentials and try again");
  }
}

void readAllSensors() { // grab all the numbers we care about
  if (mlxConnected) { // temp gun online
    vitals.temperature = mlx.readObjectTempC();
  } else {
    vitals.temperature = 0;
  }
  
  if (poxConnected) {
    vitals.heartRate = pox.getHeartRate();
    vitals.oxygenSaturation = pox.getSpO2();
    if (vitals.heartRate < 30 || vitals.heartRate > 200) { // junk filter
      vitals.heartRate = 0;
    }
    if (vitals.oxygenSaturation < 70 || vitals.oxygenSaturation > 100) { // also junk
      vitals.oxygenSaturation = 0;
    }
  } else {
    vitals.heartRate = 0;
    vitals.oxygenSaturation = 0;
  }
  
  vitals.bpSystolic = readBloodPressure(); // simple map, tune it for your sensor
  vitals.bpDiastolic = vitals.bpSystolic - 40;
  vitals.respiratoryRate = readRespiratoryRate();
  readECGData();
  vitals.timestamp = millis();
}

void sendVitalDataToAPI() { // POST JSON to your server like it’s nothing
  if (!wifiConnected) return;
  
  HTTPClient http;
  StaticJsonDocument<300> doc;
  doc["hr"] = vitals.heartRate;
  doc["bp_sys"] = vitals.bpSystolic;
  doc["bp_dia"] = vitals.bpDiastolic;
  doc["temp"] = round(vitals.temperature * 10) / 10.0;
  doc["spo2"] = vitals.oxygenSaturation;
  doc["rr"] = vitals.respiratoryRate;
  doc["ecg"] = vitals.ecgValue;
  doc["ecg_leads"] = vitals.ecgLeadsConnected;
  doc["timestamp"] = vitals.timestamp;
  doc["device_id"] = "ESP32_001";
  doc["sensors"]["mlx90614"] = mlxConnected;
  doc["sensors"]["max30100"] = poxConnected;
  
  String jsonString;
  serializeJson(doc, jsonString);
  http.begin(API_ENDPOINT);
  http.addHeader("Content-Type", "application/json");
  
  int httpResponseCode = http.POST(jsonString);
  
  if (httpResponseCode > 0) { // it landed
    Serial.print("✅ Data sent successfully! Response: ");
    Serial.println(httpResponseCode);
    digitalWrite(LED_PIN, LOW);
    delay(50);
    digitalWrite(LED_PIN, HIGH);
  } else {
    Serial.print("❌ Error sending data: ");
    Serial.println(http.errorToString(httpResponseCode));
  }
  
  http.end();
  Serial.print("📊 Vitals: HR="); // quick log so you can see life signs
  Serial.print(vitals.heartRate);
  Serial.print(" BP=");
  Serial.print(vitals.bpSystolic);
  Serial.print("/");
  Serial.print(vitals.bpDiastolic);
  Serial.print(" Temp=");
  Serial.print(vitals.temperature);
  Serial.print(" SpO2=");
  Serial.print(vitals.oxygenSaturation);
  Serial.print(" RR=");
  Serial.println(vitals.respiratoryRate);
}

int readBloodPressure() { // ADC → mmHg, very approximate
  int rawValue = analogRead(BP_SENSOR_PIN);
  int systolic = map(rawValue, 0, 4095, 80, 180);
  return systolic;
}

int readRespiratoryRate() { // ADC → breaths/min, also approximate
  int rawValue = analogRead(RESP_SENSOR_PIN);
  int rate = map(rawValue, 0, 4095, 8, 25);
  return rate;
}

void readECGData() { // check leads before trusting ECG values
  bool loPlus = digitalRead(ECG_LO_PLUS_PIN);
  bool loMinus = digitalRead(ECG_LO_MINUS_PIN);
  
  if (loPlus == HIGH || loMinus == HIGH) { // leads off = zero it
    vitals.ecgLeadsConnected = false;
    vitals.ecgValue = 0;
  } else {
    vitals.ecgLeadsConnected = true;
    vitals.ecgValue = analogRead(ECG_OUTPUT_PIN);
  }
}

/*
 * SETUP (no drama):
 * 1) WiFi: SSID/PASSWORD go at the top. Built-in libs handle the rest.
 * 2) API IP: run `ipconfig`, copy your IPv4, drop it in API_ENDPOINT.
 * 3) Upload: plug ESP32, upload, open Serial Monitor.
 * 4) Server: run api_server.py, watch the logs.
 *
 * TROUBLESHOOTING:
 * - Won’t connect: SSID/PASS wrong or WiFi out of reach.
 * - Won’t POST: API endpoint IP wrong or server not running.
 * - Still confused: read the Serial output, it tells you.
 */
