/*
 * ESP32 Vital Monitoring System
 * We read a bunch of body sensors and spit out JSON over Serial. Simple.
 *
 * You’ll need these libs:
 * - ArduinoJson (by Benoit Blanchon)
 * - Adafruit MLX90614
 * - MAX30100lib (by oxullo)
 * - Wire (built-in)
 *
 * Wiring cheat sheet:
 * - MAX30100 (HR & SpO2): SDA=21, SCL=22
 * - MLX90614 (Temp): SDA=21, SCL=22
 * - Blood Pressure: A34
 * - Respiration: A35
 * - AD8232 ECG: OUT=36, LO+=39, LO-=32
 */

#include <ArduinoJson.h>
#include <Wire.h>
#include <Adafruit_MLX90614.h>                  
#include <MAX30100_PulseOximeter.h>

// Sensor objects (the squad)
Adafruit_MLX90614 mlx = Adafruit_MLX90614();
PulseOximeter pox;

// Pin setup (don’t overthink it)
const int BP_SENSOR_PIN = 34;      // Blood pressure analog
const int RESP_SENSOR_PIN = 35;    // Breathing rate analog
const int ECG_OUTPUT_PIN = 36;     // ECG signal out
const int ECG_LO_PLUS_PIN = 39;    // ECG leads-off LO+
const int ECG_LO_MINUS_PIN = 32;   // ECG leads-off LO-
const int LED_PIN = 2;             // Built-in LED = we’re alive

// All the vitals we care about (one bundle)
struct VitalData {
  int heartRate;
  int bpSystolic;
  int bpDiastolic;
  float temperature;
  int oxygenSaturation;
  int respiratoryRate;
  int ecgValue;              // ECG raw sample
  bool ecgLeadsConnected;    // Electrodes actually on?
  unsigned long timestamp;
};

VitalData vitals;

// Timing so we don’t hammer the sensors
unsigned long lastReadTime = 0;
const unsigned long READ_INTERVAL = 1000; // One read per second is chill

// Sensor status flags (we check who showed up)
bool mlxConnected = false;
bool poxConnected = false;

void setup() {
  Serial.begin(115200);
  while (!Serial) {
    delay(10);
  }
  
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);
  Wire.begin();                  // I2C on
  if (mlx.begin()) {
    mlxConnected = true;
    Serial.println(" MLX90614 Temperature Sensor Connected");
  } else {
    Serial.println(" MLX90614 Temperature Sensor Not Found");
  }
  
  if (pox.begin()) {
    poxConnected = true;
    Serial.println(" MAX30100 Pulse Oximeter Connected");
  } else {
    Serial.println(" MAX30100 Pulse Oximeter Not Found");
  }
  
  pinMode(BP_SENSOR_PIN, INPUT);
  pinMode(RESP_SENSOR_PIN, INPUT);
  pinMode(ECG_OUTPUT_PIN, INPUT);
  pinMode(ECG_LO_PLUS_PIN, INPUT);
  pinMode(ECG_LO_MINUS_PIN, INPUT);
  
  Serial.println(" ESP32 Vital Monitor Ready");   // We’re on
  Serial.println(" Sending data in JSON format..."); // And talk JSON
  Serial.println("---");
}

void loop() {
  unsigned long currentTime = millis();
  
  if (currentTime - lastReadTime >= READ_INTERVAL) { // time to sample
    readAllSensors();
    sendVitalData();
    lastReadTime = currentTime;
    digitalWrite(LED_PIN, HIGH);
    delay(50);
    digitalWrite(LED_PIN, LOW);
  }
  if (poxConnected) { // pulse ox needs constant updates
    pox.update();
  }
}

void readAllSensors() {
  if (mlxConnected) { // temp gun online
    vitals.temperature = mlx.readObjectTempC();
  } else {
    vitals.temperature = 0;
  }
  
  if (poxConnected) {
    vitals.heartRate = pox.getHeartRate();
    vitals.oxygenSaturation = pox.getSpO2();
    
    if (vitals.heartRate < 30 || vitals.heartRate > 200) { // garbage filter
      vitals.heartRate = 0;
    }
    if (vitals.oxygenSaturation < 70 || vitals.oxygenSaturation > 100) { // also garbage
      vitals.oxygenSaturation = 0;
    }
  } else {
    vitals.heartRate = 0;
    vitals.oxygenSaturation = 0;
  }
  
  vitals.bpSystolic = readBloodPressure(); // fake-ish map, calibrate IRL
  vitals.bpDiastolic = vitals.bpSystolic - 40;
  vitals.respiratoryRate = readRespiratoryRate();
  readECGData();
  vitals.timestamp = millis();
}

void sendVitalData() {
  StaticJsonDocument<200> doc; // tiny doc, we keep it light
  doc["hr"] = vitals.heartRate;
  doc["bp_sys"] = vitals.bpSystolic;
  doc["bp_dia"] = vitals.bpDiastolic;
  doc["temp"] = round(vitals.temperature * 10) / 10.0;
  doc["spo2"] = vitals.oxygenSaturation;
  doc["rr"] = vitals.respiratoryRate;
  doc["ecg"] = vitals.ecgValue;
  doc["ecg_leads"] = vitals.ecgLeadsConnected;
  doc["timestamp"] = vitals.timestamp;
  
  doc["sensors"]["mlx90614"] = mlxConnected;
  doc["sensors"]["max30100"] = poxConnected;
  
  serializeJson(doc, Serial); // send it
  Serial.println();
}

int readBloodPressure() { // dumb map from ADC → mmHg (tune this)
  int rawValue = analogRead(BP_SENSOR_PIN);
  int systolic = map(rawValue, 0, 4095, 80, 180);
  return systolic;
}

int readRespiratoryRate() { // same deal for breaths per minute
  int rawValue = analogRead(RESP_SENSOR_PIN);
  int rate = map(rawValue, 0, 4095, 8, 25);
  return rate;
}

void readECGData() { // check if electrodes are on before reading
  bool loPlus = digitalRead(ECG_LO_PLUS_PIN);
  bool loMinus = digitalRead(ECG_LO_MINUS_PIN);
  
  if (loPlus == HIGH || loMinus == HIGH) { // leads off = no signal
    vitals.ecgLeadsConnected = false;
    vitals.ecgValue = 0;
  } else {
    vitals.ecgLeadsConnected = true;
    vitals.ecgValue = analogRead(ECG_OUTPUT_PIN);
  }
}

void handleSensorError(const char* sensorName) { // blink + log, then move on
  Serial.print(" Error reading ");
  Serial.println(sensorName);
  digitalWrite(LED_PIN, HIGH);
  delay(1000);
  digitalWrite(LED_PIN, LOW);
}

/*
 * CALIBRATION (quick and honest):
 * 1) MLX90614 (temp): point at known temp, tweak offset if it’s off.
 * 2) MAX30100 (HR/SpO2): finger steady, wait ~10–15s, no flailing.
 * 3) BP sensor: A34 input; use a real cuff to map ADC → mmHg.
 * 4) Resp rate: A35 input; count breaths, match the map.
 * 5) AD8232 ECG: OUT=36, LO+=39, LO-=32, 3V3+GND; electrodes on RA/LA/RL.
 *
 * JSON looks like this:
 * { "hr":75, "bp_sys":120, "bp_dia":80, "temp":36.8, "spo2":98,
 *   "rr":16, "ecg":2048, "ecg_leads":true, "timestamp":1234567890,
 *   "sensors": { "mlx90614":true, "max30100":true } }
 */