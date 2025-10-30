#include <WiFiNINA.h>
#include <ArduinoHttpClient.h>

// 🔹 CONFIGURA TUS DATOS AQUÍ:
const char* ssid = "iPhone de Manuel";
const char* password = "12345678";

// 🔹 IP del PC donde corre tu servidor Django:
char serverAddress[] = "172.20.10.4";  // ⚠️ cámbiala por tu IP local
int port = 8080;  // puerto del servidor Django

// 🔹 Cliente WiFi + HTTP
WiFiClient wifi;
HttpClient client(wifi, serverAddress, port);

// 🔹 Pin del sensor (A0 si tienes micrófono analógico)
int pinSensor = A0;

void setup() {
  Serial.begin(9600);
  while (!Serial);

  Serial.println("Conectando a WiFi...");
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }

  Serial.println("\n✅ Conectado a WiFi!");
  Serial.print("IP asignada: ");
  Serial.println(WiFi.localIP());
}

void loop() {
  // 🔹 Simulamos o leemos un valor analógico de ruido
  int valorAnalogico = analogRead(pinSensor);
  float nivelRuido = map(valorAnalogico, 0, 1023, 30, 100); // de 30 a 100 dB simulados

  // Mostramos el valor en el monitor serie
  Serial.print("Nivel de ruido: ");
  Serial.print(nivelRuido);
  Serial.println(" dB");

  // 🔹 Creamos el JSON que enviará al servidor
  String json = "{\"nivel_db\": " + String(nivelRuido, 2) + "}";

  // 🔹 Enviamos la petición POST al backend Django
  Serial.println("Enviando POST al servidor...");
  client.beginRequest();
  client.post("/api/ruido/");
  client.sendHeader("Content-Type", "application/json");
  client.sendHeader("Content-Length", json.length());
  client.beginBody();
  client.print(json);
  client.endRequest();

  // 🔹 Recogemos respuesta
  int statusCode = client.responseStatusCode();
  String response = client.responseBody();

  Serial.print("Respuesta del servidor (");
  Serial.print(statusCode);
  Serial.println("): ");
  Serial.println(response);

  // Espera 5 segundos antes de la siguiente lectura
  delay(5000);
}
