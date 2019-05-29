#include <ESP8266WiFi.h>
#include <PubSubClient.h>

/*
 * Config
 */
const char* ssid = "";
const char* password = "";
const char* mqtt_server = "";       // Address of your MQTT broker.
const char* _TOPIC = "";            // Topic to communicate with chatbot.

WiFiClient espClient;
PubSubClient client(espClient);
long lastMsg = 0;
char msg[50];
int value = 0;

void setup_wifi() {
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

void callback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("] ");
  for (int i = 0; i < length; i++) {
    Serial.print((char)payload[i]);
  }
  Serial.println();
  // Turn on the LED if payload is "on"
  if (strcmp((char*)payload, "on") == 0) {
    digitalWrite(D0, HIGH);   
    digitalWrite(D1, HIGH);
    client.publish(_TOPIC, "onEd");
  } 
  // Turn off the LED if payload is "off"
  else if(strcmp((char*)payload, "off") == 0) {
    digitalWrite(D0, LOW);
    digitalWrite(D1, LOW); 
    client.publish(_TOPIC, "offEd");
  }

}

void reconnect() {
  // Loop until we're reconnected
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    // Create a random client ID
    String clientId = "ESP8266Client-";
    clientId += String(random(0xffff), HEX);
    // Attempt to connect
    if (client.connect(clientId.c_str())) {
      Serial.println("connected");
      // Once connected, publish an announcement...
      client.publish(_TOPIC, "hello world");
      // ... and resubscribe
      client.subscribe(_TOPIC);
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
  pinMode(D0, OUTPUT);
  pinMode(D1, OUTPUT);
  Serial.begin(115200);
  setup_wifi();
  client.setServer(mqtt_server, 11203);
  client.setCallback(callback);
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();
}