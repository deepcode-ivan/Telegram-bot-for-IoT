#include <ESP8266WiFi.h>
#include <PubSubClient.h>

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

class Switch
{
  public:
  void enable(int pin, char comm)
  {
    if (comm == '1') {
    digitalWrite(pin, HIGH);   
    } else {
    digitalWrite(pin, LOW);  // Turn the RELAY off by making the voltage HIGH
    }
  }
};

Switch socket;       // розетки

void callback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("] ");
  for (int i = 0; i < length; i++) {
    Serial.print((char)payload[i]);
  }
  Serial.println();
  if ((String)topic == "id_2/socket1")
    socket.enable(D5,(char)payload[0]);  
  else if ((String)topic == "id_2/socket2")
    socket.enable(D6,(char)payload[0]);
  else if ((String)topic == "id_2/socket3")
    socket.enable(D7,(char)payload[0]);
  else if ((String)topic == "id_2/socket4")
    socket.enable(D8,(char)payload[0]); 
}    

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
      client.subscribe("id_2/socket1");
      client.subscribe("id_2/socket2");
      client.subscribe("id_2/socket3");
      client.subscribe("id_2/socket4");
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
  client.setCallback(callback);
  pinMode(D5, OUTPUT);
  pinMode(D6, OUTPUT);
  pinMode(D7, OUTPUT);
  pinMode(D8, OUTPUT);
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
  }
}
