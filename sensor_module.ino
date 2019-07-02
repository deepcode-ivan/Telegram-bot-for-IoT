#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <DHT.h>

const char *ssid = "ZTE"; // Имя роутера
const char *pass = "c159be5df564"; // Пароль роутера

//const char *mqtt_server = "m23.cloudmqtt.com"; // Имя сервера MQTT
//const int mqtt_port = 13358; // Порт для подключения к серверу MQTT
//const char *mqtt_user = "fbsjiouu"; // Логи для подключения к серверу MQTT
//const char *mqtt_pass = "e-YNN4z-DI4-"; // Пароль для подключения к серверу MQTT
const char *mqtt_server = "194.87.236.51"; // Имя сервера MQTT
const int mqtt_port = 1883; // Порт для подключения к серверу MQTT
const char *mqtt_user = "smart_home"; // Логи для подключения к серверу MQTT
const char *mqtt_pass = "fbsjiouu"; // Пароль для подключения к серверу MQTT

WiFiClient espClient;
PubSubClient client(espClient);

void setup_wifi() {
  delay(10);
  // We start by connecting to a WiFi network
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);
  WiFi.begin(ssid, pass);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  randomSeed(micros());
  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

class Sensor
{
  public:
  void read_climat(int pin)
  {
    DHT dht(pin, DHT11);                     // объект датчика температуры и влажности
    char msg[5];
    float t = dht.readTemperature();         // температура
    Serial.print("Publish [id_1/tem]: "); Serial.println(t);
    dtostrf(t, 2, 1, msg);
    client.publish("id_1/tem", msg);
    
    float h = dht.readHumidity();            // влажность
    Serial.print("Publish [id_1/hum]: "); Serial.println(h);
    dtostrf(h, 2, 1, msg);
    client.publish("id_1/hum", msg);
    
    float hif = dht.computeHeatIndex(t, h, false);  // ощущаемая т-тура
    Serial.print("Publish [id_1/hix]: "); Serial.println(hif);
    dtostrf(hif, 2, 2, msg);
    client.publish("id_1/hix", msg);
  }
  void read_motion(int pin)
  {
    int motion = digitalRead(pin);
    if (motion == LOW) {
      Serial.println("Publish [id_1/motion]: No motion");
      client.publish("id_1/motion", "No motion");
      }
    else if (motion == HIGH) {
      Serial.println("Publish [id_1/motion]: Motion detected");
      client.publish("id_1/motion", "Motion detected");
      }
  } 
  void read_door(int pin)
  {
    int door = digitalRead(pin);
    if (door == LOW) {
      Serial.println("Publish [id_1/door]: Closed");
      client.publish("id_1/door", "Closed");
      } 
    if (door == HIGH) {
      Serial.println("Publish [id_1/door]: Opened");
      client.publish("id_1/door", "Opened");
      }
    }
};

Sensor situation;    // сенсоры

void reconnect() {
  // Loop until we're reconnected
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    // Create a random client ID
    String clientId = "ESP8266Client-";
    clientId += String(random(0xffff), HEX);
    // Attempt to connect
    if (client.connect(clientId.c_str(), mqtt_user, mqtt_pass)) {
      Serial.println("connected");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      // Wait 5 seconds before retrying
      delay(5000);
    }
  }
}

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  setup_wifi();
  client.setServer(mqtt_server, mqtt_port);
  //client.setCallback(callback);
  pinMode(D1, INPUT);
  pinMode(D2, INPUT);
  pinMode(D3, INPUT);
}

long lastMsg = 0;
void loop() {
  // put your main code here, to run repeatedly:
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  long now = millis();
  if (now - lastMsg > 2000) { 
    lastMsg = now;
    situation.read_climat(D1);
    situation.read_motion(D2);
    situation.read_door(D3);
  }
}
