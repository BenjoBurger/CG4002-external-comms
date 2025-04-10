import sys
import json
import paho.mqtt.client as paho
import ssl
from utilities.Colour import Colour

MQTT_BROKER = "broker.emqx.io"
# MQTT_BROKER = "localhost"
MQTT_TOPIC = "cg4002_b15"
MQTT_PORT = 8883

class MQTTServer:
    def __init__(self, action_queue):
        self.queue = action_queue
        self.client = paho.Client()
        sslSettings = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        sslSettings.check_hostname = False
        sslSettings.verify_mode = ssl.CERT_NONE
        self.client.tls_set_context(sslSettings)
        self.client.on_message = self.message_handling

        if self.client.connect(MQTT_BROKER, MQTT_PORT, 300) != 0:
            print(f"{Colour.RED}Could not connect to MQTT broker!{Colour.RESET}", end="\n\n")
            sys.exit(1)
        print(f"{Colour.PINK}Server Connected to MQTT broker{Colour.RESET}", end="\n\n")
        self.client.subscribe(MQTT_TOPIC, 0)
        
    def message_handling(self, client, userdata, message):
        msg = json.loads(message.payload.decode())
        topic = message.topic
        try:
            # only handle messages from visualiser
            if msg["topic"] == "visualiser/mqtt_server":
                # print(f"{Colour.PINK}MQTT Server Received message from Visualiser: {msg}{Colour.RESET}", end="\n\n")
                data = {
                    "player_id": msg["playerId"],
                    "action": msg["action"],
                    "is_active": msg["isActive"],
                    "is_visible": msg["isVisible"]
                    # "is_visible": 1
                }
                self.queue.put(data)
                # print(f"{Colour.PINK}MQTT Server Received message '{topic}: {msg}'{Colour.RESET}", end="\n\n")
        except Exception as e:
            print(f"{Colour.RED}Error in MQTTServer message_handling: {e}{Colour.RESET}", end="\n\n")
            return