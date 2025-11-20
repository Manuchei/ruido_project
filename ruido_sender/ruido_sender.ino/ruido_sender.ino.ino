#include <WiFiNINA.h>
#include <ArduinoHttpClient.h>
#include <math.h>

// 🔹 CONFIGURA TU RED WiFi
const char* ssid = "PORTATIL-DELL 1211";
const char* password = "12345678";

// 🔹 IP y puerto del servidor Django
char serverAddress[] = "nonastronomically-unplotted-marlo.ngrok-free.dev";
int port = 80;

// 🔹 API Key
const char* API_KEY = "GB73_PISO1_KEY";

// 🔹 Cliente WiFi + HTTP
WiFiClient wifi;
HttpClient client(wifi, serverAddress, port);

// 🔹 Pines
int pinSensor = A0;
int pinPIR = 2;

// ⚙ Parámetros sonido
#define MUESTRAS 200

void setup() {
  Serial.begin(9600);
  delay(1000);

  pinMode(pinPIR, INPUT);

  Serial.println("Conectando a WiFi...");
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }

  Serial.println("\n✅ Conectado a WiFi!");
}

// 🔊 Cálculo RMS del sonido
float medirRMS() {
  long sumaCuadrados = 0;

  for (int i = 0; i < MUESTRAS; i++) {
    int valor = analogRead(pinSensor);
    int señal = valor - 512;  // centramos en 0
    sumaCuadrados += señal * señal;
    delayMicroseconds(200);
  }

  float rms = sqrt((float)sumaCuadrados / MUESTRAS);
  return rms;
}

// 🔊 Convertir RMS a dB
float rmsToDb(float rms) {
  float referencia = 10.0;  // Ajustable
  if (rms < 1) rms = 1;
  float dB = 20.0 * log10(rms / referencia);

  return dB + 40;   // desplazamiento para rango realista
}

void loop() {

  float rms = medirRMS();
  float nivelDB = rmsToDb(rms);

  int presencia = digitalRead(pinPIR);

  Serial.print("RMS: ");
  Serial.println(rms);

  Serial.print("Nivel estimado dB: ");
  Serial.println(nivelDB);

  Serial.print("Presencia: ");
  Serial.println(presencia);

  // JSON
  String json = "{";
  json += "\"api_key\":\"" + String(API_KEY) + "\",";
  json += "\"nivel_db\":" + String(nivelDB, 2) + ",";
  json += "\"presencia\":" + String(presencia);
  json += "}";

  client.beginRequest();
  client.post("/api/ruido/");
  client.sendHeader("Content-Type", "application/json");
  client.sendHeader("Content-Length", json.length());
  client.beginBody();
  client.print(json);
  client.endRequest();

  int statusCode = client.responseStatusCode();
  String response = client.responseBody();

  Serial.print("Servidor: ");
  Serial.println(statusCode);
  Serial.println(response);

  delay(5000);
}
