#include <WiFiNINA.h>
#include <ArduinoHttpClient.h>

// 🔹 CONFIGURA TU RED WiFi
const char* ssid = "PORTATIL-DELL 1211";
const char* password = "12345678";

// 🔹 IP y puerto del servidor Django
char serverAddress[] = "nonastronomically-unplotted-marlo.ngrok-free.dev";   // ⚠️ Cámbiala si tu IP local cambia
int port = 80;  // el puerto del servidor Django (no 8080, por defecto Django usa 8000)

// 🔹 API Key única de este dispositivo (por ejemplo, GB73 Piso 1)
const char* API_KEY = "GB73_PISO1_KEY";

// 🔹 Cliente WiFi + HTTP
WiFiClient wifi;
HttpClient client(wifi, serverAddress, port);

// 🔹 Pin del sensor (A0 si usas un micrófono analógico)
int pinSensor = A0;

void setup() {
  Serial.begin(9600);
  delay(1000);
  //while (!Serial);

  Serial.println("Conectando a WiFi...");
  WiFi.begin(ssid, password);

  // Espera hasta conexión
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }

  Serial.println("\n✅ Conectado a WiFi!");
  Serial.print("IP asignada: ");
  Serial.println(WiFi.localIP());
}

void loop() {
  // 🔹 Leer el sensor o simular valor
  int valorAnalogico = analogRead(pinSensor);
  //float nivelRuido = map(valorAnalogico, 0, 1023, 30, 100);  // de 30 a 100 dB simulados

    // Por ahora enviamos valor RAW tal cual
  float nivelRuido = valorAnalogico;

    Serial.print("\nNivel RAW leído: ");
  Serial.println(nivelRuido);

  // Mostrar valor en el monitor serie
  //Serial.print("Nivel de ruido: ");
  //Serial.print(nivelRuido);
  //Serial.println(" dB");

  // 🔹 Construir el JSON con api_key + nivel_db
  String json = "{\"api_key\": \"" + String(API_KEY) + "\", \"nivel_db\": " + String(nivelRuido, 2) + "}";

  // 🔹 Enviar la petición POST al servidor Django
  Serial.println("Enviando POST al servidor...");
  client.beginRequest();
  client.post("/api/ruido/");
  //client.sendHeader("Host", serverAddress);
  client.sendHeader("Content-Type", "application/json");
  client.sendHeader("Content-Length", json.length());
  client.beginBody();
  client.print(json);
  client.endRequest();

  // 🔹 Recoger respuesta
  int statusCode = client.responseStatusCode();
  String response = client.responseBody();

  Serial.print("Respuesta del servidor (");
  Serial.print(statusCode);
  Serial.println("): ");
  Serial.println(response);

  // 🔹 Esperar antes del siguiente envío
  delay(5000);
}
